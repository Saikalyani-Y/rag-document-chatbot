import hashlib
import logging
import re
import uuid
from pathlib import Path

from config.settings import settings
from services import chunking, embedding_service
from services.vector_store_service import vector_store
from utils.errors import DocumentProcessingError, DuplicateDocumentError, NotFoundError
from utils.validation import validate_upload
import db

logger = logging.getLogger("rag_chatbot")


def _extract_units(file_path: Path, file_type: str) -> tuple[list[str], str]:
    """Return (units, unit_label). Units are pages (pdf) or paragraphs (txt/docx)."""
    if file_type == "pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(file_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return pages, "page"

    if file_type == "docx":
        from docx import Document as DocxDocument

        doc = DocxDocument(str(file_path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return paragraphs, "section"

    if file_type == "txt":
        text = file_path.read_text(encoding="utf-8", errors="replace")
        paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
        return paragraphs or [text], "section"

    raise DocumentProcessingError(f"Unsupported file type '{file_type}'.")


def process_upload(filename: str, content: bytes) -> dict:
    ext = validate_upload(filename, len(content), settings.max_file_size_mb)

    file_hash = hashlib.sha256(content).hexdigest()
    existing = db.get_document_by_hash(file_hash)
    if existing is not None:
        raise DuplicateDocumentError(f"'{existing['filename']}' has already been uploaded.")

    document_id = str(uuid.uuid4())
    storage_path = settings.uploads_dir / f"{document_id}.{ext}"

    units, unit_label = [], "section"
    chunks = []
    try:
        storage_path.write_bytes(content)
        units, unit_label = _extract_units(storage_path, ext)
        combined_text = "\n\n".join(units).strip()
        if not combined_text:
            raise DocumentProcessingError(
                "No readable text could be extracted from this document. "
                "If it's a scanned/image-only PDF, text extraction isn't supported yet."
            )

        chunk_objs = chunking.chunk_units(units, settings.chunk_size, settings.chunk_overlap)
        if not chunk_objs:
            raise DocumentProcessingError("The document did not produce any usable chunks.")

        vectors = embedding_service.embed_texts([c.text for c in chunk_objs])
        chunks = [
            {
                "chunk_index": c.chunk_index,
                "unit_label": unit_label,
                "unit_number": c.unit_number,
                "text": c.text,
            }
            for c in chunk_objs
        ]
    except Exception:
        storage_path.unlink(missing_ok=True)
        raise

    db.insert_document(document_id, filename, ext, file_hash, str(storage_path))
    try:
        chunk_ids = db.insert_chunks(document_id, chunks)
        vector_store.add(chunk_ids, vectors)
        db.mark_document_ready(document_id, len(chunk_ids))
    except Exception as exc:
        logger.exception("Failed to index document %s", document_id)
        db.mark_document_failed(document_id, "Failed to build the search index for this document.")
        storage_path.unlink(missing_ok=True)
        raise DocumentProcessingError("Failed to build the search index for this document.") from exc

    return dict(db.get_document(document_id))


def delete_document(document_id: str) -> None:
    document = db.get_document(document_id)
    if document is None:
        raise NotFoundError("Document not found.")

    chunk_ids = db.get_chunk_ids_for_document(document_id)
    vector_store.remove(chunk_ids)
    db.delete_document_row(document_id)  # cascades to chunks

    storage_path = Path(document["storage_path"])
    storage_path.unlink(missing_ok=True)
