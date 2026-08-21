import logging

import ollama

from config.settings import settings
from utils.errors import LLMServiceError

logger = logging.getLogger("rag_chatbot")

_client = ollama.Client(host=settings.ollama_host)

SYSTEM_PROMPT = (
    "You are a document-grounded assistant. Answer the user's question using ONLY the "
    "information in the provided context below. Do not use outside knowledge and do not "
    "guess or invent details that are not stated in the context.\n\n"
    "The context below was already retrieved because it's relevant to the question, so in "
    "most cases it contains something useful — use it. If it fully answers the question, "
    "answer directly. If it only partially answers the question (e.g. it doesn't state the "
    "exact fact asked for, but has closely related information), explain what the documents "
    "do say and be explicit about what they don't cover — do not simply refuse. "
    "Only respond with exactly: "
    "\"I couldn't find sufficient information in the uploaded documents to answer that.\" "
    "if the context is genuinely unrelated to the question. "
    "When you use information from the context, refer to it using the [n] markers already "
    "present in it."
)


GENERAL_SYSTEM_PROMPT = (
    "You are a helpful general-purpose assistant. The user's uploaded documents did not "
    "contain relevant information for this question, so answer from your own general "
    "knowledge instead. Be direct and helpful, and if you're not confident about a fact, "
    "say so rather than guessing with false confidence."
)

WEB_SYSTEM_PROMPT = (
    "You are a helpful assistant. The user's uploaded documents did not contain relevant "
    "information for this question, so you were given live web search results instead — "
    "prefer these over your own memorized knowledge, since they're more current and "
    "specific. Synthesize a clear, direct answer from the search results below. If the "
    "results don't actually answer the question, say so plainly instead of guessing. When "
    "you use a result, refer to it using the [n] markers already present in it."
)


def _chat(messages: list[dict]) -> str:
    try:
        response = _client.chat(model=settings.chat_model, messages=messages)
    except Exception as exc:
        logger.exception("Chat request to Ollama failed")
        raise LLMServiceError(
            f"Could not reach the local language model '{settings.chat_model}' on Ollama "
            f"({settings.ollama_host}). Make sure Ollama is running (`ollama serve`) and the "
            f"model is pulled (`ollama pull {settings.chat_model}`)."
        ) from exc

    return response["message"]["content"]


def generate_answer(context: str, history: list[dict], question: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Context:\n{context}"},
        *history,
        {"role": "user", "content": question},
    ]
    return _chat(messages)


def generate_general_answer(history: list[dict], question: str) -> str:
    messages = [
        {"role": "system", "content": GENERAL_SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": question},
    ]
    return _chat(messages)


def generate_web_grounded_answer(search_context: str, history: list[dict], question: str) -> str:
    messages = [
        {"role": "system", "content": WEB_SYSTEM_PROMPT},
        {"role": "system", "content": f"Search results:\n{search_context}"},
        *history,
        {"role": "user", "content": question},
    ]
    return _chat(messages)


def check_ollama_ready() -> tuple[bool, str]:
    try:
        models_response = _client.list()
        available = {m["model"] for m in models_response.get("models", [])}
    except Exception as exc:
        return False, f"Cannot reach Ollama at {settings.ollama_host}: {exc}"

    missing = [m for m in (settings.chat_model, settings.embedding_model) if not _model_available(m, available)]
    if missing:
        return False, f"Ollama is reachable but missing model(s): {', '.join(missing)}. Run `ollama pull <model>`."
    return True, "Ollama is reachable and required models are available."


def _model_available(model: str, available: set[str]) -> bool:
    # Ollama tags responses as "name:tag"; a bare name implies ":latest".
    if model in available:
        return True
    return any(a == model or a.startswith(f"{model}:") or model.startswith(a.split(":")[0]) for a in available)
