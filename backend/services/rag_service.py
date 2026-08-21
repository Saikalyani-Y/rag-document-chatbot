from config.settings import settings
from services import embedding_service, llm_service
from services.vector_store_service import vector_store
import db

NOT_FOUND_MESSAGE = "I couldn't find sufficient information in the uploaded documents to answer that."


def _label(unit_label: str, unit_number: int) -> str:
    return f"Page {unit_number}" if unit_label == "page" else f"Section {unit_number}"


def _build_history(conversation_id: str) -> list[dict]:
    messages = db.list_messages(conversation_id)
    recent = messages[-settings.history_turns :]
    return [{"role": m["role"], "content": m["content"]} for m in recent]


def answer_question(conversation_id: str, question: str, allow_general: bool = False) -> dict:
    history = _build_history(conversation_id)

    total_chunks = db.count_all_chunks()
    if total_chunks == 0:
        return _fallback(history, question, allow_general)

    query_vector = embedding_service.embed_query(question)
    hits = vector_store.search(query_vector, settings.top_k)

    # Cosine similarity scores from a small local embedding model aren't well-calibrated
    # for tiny document sets — an off-topic query can score higher than the one genuinely
    # relevant chunk in a 3-chunk document. Filtering by an absolute threshold there does
    # more harm (false negatives) than good, so below a small-corpus size, skip the filter
    # and let the LLM's own judgment (see the grounded system prompt) decide relevance.
    if total_chunks > settings.small_corpus_chunk_limit:
        hits = [(chunk_id, score) for chunk_id, score in hits if score >= settings.similarity_threshold]

    if not hits:
        return _fallback(history, question, allow_general)

    chunk_rows = db.get_chunks_by_ids([chunk_id for chunk_id, _ in hits])

    context_parts = []
    sources = []
    seen_source_keys = set()
    for i, (chunk_id, score) in enumerate(hits, start=1):
        row = chunk_rows.get(chunk_id)
        if row is None:
            continue
        label = _label(row["unit_label"], row["unit_number"])
        context_parts.append(f"[{i}] ({row['filename']}, {label})\n{row['text']}")

        source_key = (row["document_id"], row["unit_number"])
        if source_key not in seen_source_keys:
            seen_source_keys.add(source_key)
            sources.append(
                {
                    "document_id": row["document_id"],
                    "filename": row["filename"],
                    "label": label,
                    "chunk_id": chunk_id,
                    "score": round(score, 3),
                }
            )

    context = "\n\n".join(context_parts)
    answer = llm_service.generate_answer(context, history, question)

    # These chunks cleared the relevance threshold, so they're worth showing regardless
    # of how the model phrased its answer — small local models don't reliably echo the
    # exact refusal string, so string-matching the answer to decide this isn't reliable.
    return {"answer": answer, "sources": sources, "grounded": True}


def _fallback(history: list[dict], question: str, allow_general: bool) -> dict:
    """No document context cleared the relevance bar. Either refuse, or answer from the
    model's general knowledge if the caller opted into that — clearly marked as ungrounded."""
    if not allow_general:
        return {"answer": NOT_FOUND_MESSAGE, "sources": [], "grounded": False}

    answer = llm_service.generate_general_answer(history, question)
    return {"answer": answer, "sources": [], "grounded": False}
