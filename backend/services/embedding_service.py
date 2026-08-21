import logging

import faiss
import numpy as np
import ollama

from config.settings import settings
from utils.errors import LLMServiceError

logger = logging.getLogger("rag_chatbot")

_client = ollama.Client(host=settings.ollama_host)


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a batch of texts and L2-normalize the vectors (for cosine similarity via inner product)."""
    if not texts:
        return np.zeros((0, 0), dtype="float32")
    try:
        response = _client.embed(model=settings.embedding_model, input=texts)
    except Exception as exc:
        logger.exception("Embedding request to Ollama failed")
        raise LLMServiceError(
            f"Could not reach the local embedding model '{settings.embedding_model}' on Ollama "
            f"({settings.ollama_host}). Make sure Ollama is running and the model is pulled "
            f"(`ollama pull {settings.embedding_model}`)."
        ) from exc

    vectors = np.array(response["embeddings"], dtype="float32")
    faiss.normalize_L2(vectors)
    return vectors


def embed_query(text: str) -> np.ndarray:
    return embed_texts([text])
