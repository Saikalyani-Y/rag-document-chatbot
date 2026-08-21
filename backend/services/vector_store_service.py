"""FAISS-backed vector store: cosine similarity via IndexFlatIP over normalized vectors,
wrapped in IndexIDMap2 so vectors can be added/removed by an explicit integer id
(the sqlite chunk id). Persisted to disk after every mutation.
"""

import faiss
import numpy as np

from config.settings import settings


class VectorStoreService:
    def __init__(self):
        self.index: faiss.IndexIDMap2 | None = None
        self._load()

    def _load(self) -> None:
        if settings.index_path.exists():
            self.index = faiss.read_index(str(settings.index_path))
        else:
            self.index = None

    def _ensure_index(self, dimension: int) -> None:
        if self.index is None:
            base = faiss.IndexFlatIP(dimension)
            self.index = faiss.IndexIDMap2(base)

    def add(self, ids: list[int], vectors: np.ndarray) -> None:
        if len(ids) == 0:
            return
        self._ensure_index(vectors.shape[1])
        id_array = np.array(ids, dtype="int64")
        self.index.add_with_ids(vectors, id_array)
        self._persist()

    def remove(self, ids: list[int]) -> None:
        if self.index is None or len(ids) == 0:
            return
        id_array = np.array(ids, dtype="int64")
        self.index.remove_ids(id_array)
        self._persist()

    def search(self, query_vector: np.ndarray, top_k: int) -> list[tuple[int, float]]:
        if self.index is None or self.index.ntotal == 0:
            return []
        scores, ids = self.index.search(query_vector, min(top_k, self.index.ntotal))
        results = []
        for score, chunk_id in zip(scores[0], ids[0]):
            if chunk_id == -1:
                continue
            results.append((int(chunk_id), float(score)))
        return results

    def _persist(self) -> None:
        settings.storage_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(settings.index_path))


vector_store = VectorStoreService()
