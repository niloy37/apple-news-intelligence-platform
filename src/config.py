"""Runtime configuration for the Apple News Intelligence Platform."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is optional at import time
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    """Centralized application settings loaded from environment variables."""

    project_root: Path = PROJECT_ROOT
    app_name: str = "Apple News Intelligence Platform"
    environment: str = field(default_factory=lambda: _env("ENVIRONMENT", "local"))

    postgres_user: str = field(default_factory=lambda: _env("POSTGRES_USER", "apple_news"))
    postgres_password: str = field(default_factory=lambda: _env("POSTGRES_PASSWORD", "apple_news_password"))
    postgres_db: str = field(default_factory=lambda: _env("POSTGRES_DB", "apple_news_db"))
    postgres_host: str = field(default_factory=lambda: _env("POSTGRES_HOST", "localhost"))
    postgres_port: str = field(default_factory=lambda: _env("POSTGRES_PORT", "5432"))

    neo4j_uri: str = field(default_factory=lambda: _env("NEO4J_URI", "bolt://localhost:7687"))
    neo4j_user: str = field(default_factory=lambda: _env("NEO4J_USER", "neo4j"))
    neo4j_password: str = field(default_factory=lambda: _env("NEO4J_PASSWORD", "apple_news_neo4j_password"))

    qdrant_url: str = field(default_factory=lambda: _env("QDRANT_URL", "http://localhost:6333"))

    minio_endpoint: str = field(default_factory=lambda: _env("MINIO_ENDPOINT", "localhost:9000"))
    minio_access_key: str = field(default_factory=lambda: _env("MINIO_ACCESS_KEY", "minioadmin"))
    minio_secret_key: str = field(default_factory=lambda: _env("MINIO_SECRET_KEY", "minioadmin"))
    minio_bucket_raw_news: str = field(default_factory=lambda: _env("MINIO_BUCKET_RAW_NEWS", "raw-news"))
    minio_bucket_raw_social: str = field(default_factory=lambda: _env("MINIO_BUCKET_RAW_SOCIAL", "raw-social"))
    minio_bucket_bronze: str = field(default_factory=lambda: _env("MINIO_BUCKET_BRONZE", "bronze"))
    minio_bucket_silver: str = field(default_factory=lambda: _env("MINIO_BUCKET_SILVER", "silver"))
    minio_bucket_gold: str = field(default_factory=lambda: _env("MINIO_BUCKET_GOLD", "gold"))

    redpanda_bootstrap_servers: str = field(
        default_factory=lambda: _env("REDPANDA_BOOTSTRAP_SERVERS", "localhost:19092")
    )

    reddit_client_id: str = field(default_factory=lambda: _env("REDDIT_CLIENT_ID", ""))
    reddit_client_secret: str = field(default_factory=lambda: _env("REDDIT_CLIENT_SECRET", ""))
    reddit_user_agent: str = field(
        default_factory=lambda: _env("REDDIT_USER_AGENT", "apple-news-intelligence-platform")
    )

    x_bearer_token: str = field(default_factory=lambda: _env("X_BEARER_TOKEN", ""))
    news_api_key: str = field(default_factory=lambda: _env("NEWS_API_KEY", ""))

    embedding_provider: str = field(default_factory=lambda: _env("EMBEDDING_PROVIDER", "local"))
    local_embedding_model: str = field(
        default_factory=lambda: _env("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    )
    openai_api_key: str = field(default_factory=lambda: _env("OPENAI_API_KEY", ""))

    keywords: tuple[str, ...] = (
        "Apple",
        "iPhone",
        "iPhone 17",
        "MacBook",
        "iPad",
        "Apple Watch",
        "Vision Pro",
        "iOS",
        "macOS",
        "App Store",
        "Tim Cook",
        "Apple Intelligence",
        "Apple chip",
        "M-series chip",
        "Apple earnings",
        "Apple supply chain",
    )

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sample_dir(self) -> Path:
        return self.project_root / "data" / "sample"

    @property
    def exports_dir(self) -> Path:
        return self.project_root / "data" / "exports"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load `.env` once and return immutable settings."""

    if load_dotenv:
        load_dotenv(PROJECT_ROOT / ".env", override=False)
    return Settings()
