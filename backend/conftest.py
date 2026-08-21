import pytest

from config.settings import settings
import db as db_module
from services.vector_store_service import vector_store


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    """Point storage (sqlite db, faiss index, uploads) at a throwaway tmp dir per test."""
    monkeypatch.setattr(settings, "storage_dir", tmp_path)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    vector_store.index = None
    db_module.init_db()
    yield
