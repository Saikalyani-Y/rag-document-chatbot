"""
chatbot.py

Core Retrieval-Augmented Generation (RAG) logic for the document chatbot.

Responsibilities:
- Load and split documents into text chunks
- Generate embeddings for each chunk
- Build and query a FAISS vector index
- Retrieve relevant chunks for a user question
- Call the OpenAI API to generate a grounded answer
"""

import os
from dataclasses import dataclass
from typing import List

import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@dataclass
class Chunk:
    text: str
    source: str


def load_text(file_path: str) -> str:
    """Load raw text from a .txt or .pdf file."""
    if file_path.lower().endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def split_into_chunks(text: str, source: str) -> List[Chunk]:
    """Split text into overlapping chunks for embedding."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(Chunk(text=chunk_text, source=source))
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def embed_texts(texts: List[str]) -> np.ndarray:
    """Get embeddings for a list of texts from the OpenAI API."""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    vectors = [item.embedding for item in response.data]
    return np.array(vectors, dtype="float32")


class VectorStore:
    """A minimal in-memory FAISS-backed vector store."""

    def __init__(self):
        self.index = None
        self.chunks: List[Chunk] = []

    def add(self, chunks: List[Chunk]) -> None:
        vectors = embed_texts([c.text for c in chunks])
        if self.index is None:
            dimension = vectors.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
        self.index.add(vectors)
        self.chunks.extend(chunks)

    def search(self, query: str, top_k: int = 4) -> List[Chunk]:
        if self.index is None or len(self.chunks) == 0:
            return []
        query_vector = embed_texts([query])
        distances, indices = self.index.search(query_vector, top_k)
        return [self.chunks[i] for i in indices[0] if i < len(self.chunks)]


def build_vector_store(file_path: str) -> VectorStore:
    """Load a document, chunk it, and build a vector store from it."""
    text = load_text(file_path)
    chunks = split_into_chunks(text, source=os.path.basename(file_path))
    store = VectorStore()
    store.add(chunks)
    return store


def answer_question(store: VectorStore, question: str) -> str:
    """Retrieve relevant chunks and generate a grounded answer."""
    relevant_chunks = store.search(question)
    context = "\n\n".join(c.text for c in relevant_chunks)

    system_prompt = (
        "You are a helpful assistant that answers questions using only the "
        "provided context. If the answer is not in the context, say you "
        "don't know instead of making something up."
    )
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
