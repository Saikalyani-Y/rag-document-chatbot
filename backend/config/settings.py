from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    ollama_host: str = "http://localhost:11434"
    chat_model: str = "llama3.2:3b"
    embedding_model: str = "nomic-embed-text"

    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k: int = 5
    similarity_threshold: float = 0.5
    small_corpus_chunk_limit: int = 12
    history_turns: int = 6

    max_file_size_mb: int = 20
    allowed_origins: str = "http://localhost:5173"

    storage_dir: Path = BACKEND_DIR / "storage"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def uploads_dir(self) -> Path:
        return self.storage_dir / "uploads"

    @property
    def index_path(self) -> Path:
        return self.storage_dir / "index.faiss"

    @property
    def db_path(self) -> Path:
        return self.storage_dir / "app.db"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
