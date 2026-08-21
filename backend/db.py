"""Plain sqlite3 access layer — no ORM. Handles documents, chunks, conversations, messages."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator, Optional

from config.settings import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE,
    storage_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'processing',
    error_message TEXT,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    uploaded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    unit_label TEXT NOT NULL,
    unit_number INTEGER NOT NULL,
    text TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL DEFAULT 'New chat',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    sources TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(settings.db_path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)


# --- documents -------------------------------------------------------------

def insert_document(document_id: str, filename: str, file_type: str, file_hash: str, storage_path: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO documents (id, filename, file_type, file_hash, storage_path, status, uploaded_at)
               VALUES (?, ?, ?, ?, ?, 'processing', ?)""",
            (document_id, filename, file_type, file_hash, storage_path, now_iso()),
        )


def get_document_by_hash(file_hash: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM documents WHERE file_hash = ?", (file_hash,)).fetchone()


def get_document(document_id: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()


def list_documents() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM documents ORDER BY uploaded_at DESC").fetchall()


def mark_document_ready(document_id: str, chunk_count: int) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE documents SET status = 'ready', chunk_count = ?, error_message = NULL WHERE id = ?",
            (chunk_count, document_id),
        )


def mark_document_failed(document_id: str, error_message: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE documents SET status = 'failed', error_message = ? WHERE id = ?",
            (error_message, document_id),
        )


def delete_document_row(document_id: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))  # cascades to chunks


# --- chunks ------------------------------------------------------------------

def insert_chunks(document_id: str, chunks: list[dict]) -> list[int]:
    """Insert chunk rows and return their generated ids, in the same order."""
    with get_connection() as conn:
        ids = []
        for c in chunks:
            cur = conn.execute(
                """INSERT INTO chunks (document_id, chunk_index, unit_label, unit_number, text)
                   VALUES (?, ?, ?, ?, ?)""",
                (document_id, c["chunk_index"], c["unit_label"], c["unit_number"], c["text"]),
            )
            ids.append(cur.lastrowid)
        return ids


def get_chunk_ids_for_document(document_id: str) -> list[int]:
    with get_connection() as conn:
        rows = conn.execute("SELECT id FROM chunks WHERE document_id = ?", (document_id,)).fetchall()
        return [r["id"] for r in rows]


def get_chunks_by_ids(chunk_ids: list[int]) -> dict[int, sqlite3.Row]:
    if not chunk_ids:
        return {}
    with get_connection() as conn:
        placeholders = ",".join("?" for _ in chunk_ids)
        rows = conn.execute(
            f"""SELECT chunks.*, documents.filename, documents.file_type
                FROM chunks JOIN documents ON documents.id = chunks.document_id
                WHERE chunks.id IN ({placeholders})""",
            chunk_ids,
        ).fetchall()
        return {row["id"]: row for row in rows}


def count_all_chunks() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM chunks").fetchone()
        return row["n"]


# --- conversations -------------------------------------------------------------

def create_conversation(conversation_id: str, title: str = "New chat") -> None:
    with get_connection() as conn:
        ts = now_iso()
        conn.execute(
            "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (conversation_id, title, ts, ts),
        )


def get_conversation(conversation_id: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,)).fetchone()


def list_conversations() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM conversations ORDER BY updated_at DESC").fetchall()


def delete_conversation(conversation_id: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))


def touch_conversation(conversation_id: str) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now_iso(), conversation_id))


def maybe_set_conversation_title(conversation_id: str, title: str) -> None:
    with get_connection() as conn:
        row = conn.execute("SELECT title FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
        if row and row["title"] == "New chat":
            conn.execute("UPDATE conversations SET title = ? WHERE id = ?", (title[:80], conversation_id))


# --- messages -------------------------------------------------------------

def insert_message(message_id: str, conversation_id: str, role: str, content: str, sources: Optional[list] = None) -> str:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (id, conversation_id, role, content, sources, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (message_id, conversation_id, role, content, json.dumps(sources) if sources is not None else None, now_iso()),
        )
        return message_id


def list_messages(conversation_id: str) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC", (conversation_id,)
        ).fetchall()
