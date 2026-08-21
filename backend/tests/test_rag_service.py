import uuid

import numpy as np
import pytest

import db
from services import document_service, embedding_service, llm_service, rag_service
from services.vector_store_service import vector_store


def _fake_embed(texts):
    rng = np.random.default_rng(7)
    return rng.random((len(texts), 8)).astype("float32")


@pytest.fixture(autouse=True)
def stub_embeddings(monkeypatch):
    monkeypatch.setattr(embedding_service, "embed_texts", _fake_embed)


@pytest.fixture
def conversation_id():
    cid = str(uuid.uuid4())
    db.create_conversation(cid)
    return cid


def test_no_documents_returns_not_found_without_calling_llm(monkeypatch, conversation_id):
    called = False

    def fail_if_called(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(llm_service, "generate_answer", fail_if_called)

    result = rag_service.answer_question(conversation_id, "What is RAG?")

    assert result["answer"] == rag_service.NOT_FOUND_MESSAGE
    assert result["sources"] == []
    assert called is False


def test_low_similarity_hits_are_filtered_out(monkeypatch, conversation_id):
    document_service.process_upload("notes.txt", b"Some unrelated content to index for this test.")

    monkeypatch.setattr(vector_store, "search", lambda query_vector, top_k: [(1, 0.01)])
    monkeypatch.setattr(llm_service, "generate_answer", lambda *a, **k: pytest.fail("LLM should not be called"))

    result = rag_service.answer_question(conversation_id, "unrelated question")

    assert result["answer"] == rag_service.NOT_FOUND_MESSAGE
    assert result["sources"] == []


def test_relevant_hits_call_llm_and_return_sources(monkeypatch, conversation_id):
    doc = document_service.process_upload("notes.txt", b"Relevant content that should be retrieved for citations.")
    chunk_ids = db.get_chunk_ids_for_document(doc["id"])

    monkeypatch.setattr(vector_store, "search", lambda query_vector, top_k: [(chunk_ids[0], 0.9)])
    monkeypatch.setattr(llm_service, "generate_answer", lambda context, history, question: f"Answer using: {context[:20]}")

    result = rag_service.answer_question(conversation_id, "What does the document say?")

    assert result["answer"].startswith("Answer using:")
    assert len(result["sources"]) == 1
    assert result["sources"][0]["filename"] == "notes.txt"
    assert result["sources"][0]["chunk_id"] == chunk_ids[0]
