import logging
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# backend/ directory (this file is app/core/config.py)
_BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "AI Document Knowledge Base"
    app_env: str = "development"
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Database configuration
    use_postgresql: bool = False
    database_url: str = ""
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "knowledge_base"
    
    # Chroma configuration
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_use_http: bool = False
    chroma_persist_directory: str = "./.chroma"
    chroma_collection_name: str = "documents"
    chroma_hnsw_space: str = "cosine"
    chroma_hnsw_m: int = 48
    chroma_hnsw_ef_construction: int = 200
    chroma_query_ef: int = 64
    
    # Embedding configuration
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # JWT configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # Seed admin configuration
    seed_admin_email: str = "admin@company.com"
    seed_admin_password: str = "admin123"
    seed_admin_department: str = "general"

    # Demo documents (PostgreSQL + Chroma); idempotent via stable `seed://demo/...` sources
    seed_demo_documents_on_startup: bool = False

    # Original uploaded files (PDF/TXT bytes) for download
    upload_storage_directory: str = "./uploads"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def postgres_url(self) -> str:
        encoded_password = quote_plus(self.postgres_password)
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{encoded_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            f"?sslmode=require"
        )

    @staticmethod
    def _resolve_backend_path(relative_or_absolute: str) -> Path:
        p = Path(relative_or_absolute)
        if p.is_absolute():
            return p.resolve()
        return (_BACKEND_DIR / p).resolve()

    @property
    def sqlalchemy_database_url(self) -> str:
        """
        Get database URL with fallback to SQLite if PostgreSQL is not available.
        SQLite files are resolved under backend/ so cwd does not matter.
        """
        if self.use_postgresql:
            logger.info("Using PostgreSQL database: %s", self.postgres_url)
            return self.postgres_url

        if self.database_url.strip():
            raw = self.database_url.strip()
            if raw.startswith("sqlite:///./"):
                rel = raw.removeprefix("sqlite:///./")
                abs_path = (_BACKEND_DIR / rel).resolve()
                url = f"sqlite:///{abs_path.as_posix()}"
                logger.info("Using SQLite database (resolved): %s", url)
                return url
            return raw

        abs_path = (_BACKEND_DIR / "knowledge_base.db").resolve()
        url = f"sqlite:///{abs_path.as_posix()}"
        logger.info("Using SQLite database (resolved): %s", url)
        return url

    @property
    def chroma_persist_absolute(self) -> str:
        """Chroma persistence path anchored to backend/ when relative."""
        return str(self._resolve_backend_path(self.chroma_persist_directory))

    @property
    def upload_storage_absolute(self) -> str:
        """Upload directory anchored to backend/ when relative."""
        return str(self._resolve_backend_path(self.upload_storage_directory))

    @property
    def cors_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
        return origins if origins else ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()
