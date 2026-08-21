import numpy as np
import pytest

from services import document_service, embedding_service
from utils.errors import DuplicateDocumentError, EmptyFileError, UnsupportedFormatError


def _fake_embed(texts):
    rng = np.random.default_rng(42)
    vectors = rng.random((len(texts), 8)).astype("float32")
    return vectors


@pytest.fixture(autouse=True)
def stub_embeddings(monkeypatch):
    monkeypatch.setattr(embedding_service, "embed_texts", _fake_embed)


def test_process_upload_indexes_a_txt_document():
    content = b"Retrieval-Augmented Generation combines retrieval with text generation.\n\nIt reduces hallucination."
    doc = document_service.process_upload("notes.txt", content)
    assert doc["status"] == "ready"
    assert doc["chunk_count"] >= 1
    assert doc["file_type"] == "txt"


def test_duplicate_upload_is_rejected():
    content = b"Some unique document content for dedup testing."
    document_service.process_upload("dup.txt", content)
    with pytest.raises(DuplicateDocumentError):
        document_service.process_upload("dup-again.txt", content)


def test_unsupported_extension_is_rejected():
    with pytest.raises(UnsupportedFormatError):
        document_service.process_upload("archive.zip", b"binary-ish content")


def test_empty_file_is_rejected():
    with pytest.raises(EmptyFileError):
        document_service.process_upload("empty.txt", b"")


def test_delete_document_removes_row_and_file():
    content = b"Content that will be deleted after indexing to test cleanup."
    doc = document_service.process_upload("to_delete.txt", content)

    import db

    assert db.get_document(doc["id"]) is not None
    document_service.delete_document(doc["id"])
    assert db.get_document(doc["id"]) is None
    assert db.count_all_chunks() == 0
