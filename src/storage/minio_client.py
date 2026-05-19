"""MinIO S3-compatible object storage adapter."""

from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from typing import Any

from src.config import Settings, get_settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class MinioObjectStore:
    settings: Settings = field(default_factory=get_settings)
    client: Any | None = None

    def __post_init__(self) -> None:
        try:
            from minio import Minio

            secure = self.settings.minio_endpoint.startswith("https://")
            endpoint = self.settings.minio_endpoint.replace("http://", "").replace("https://", "")
            self.client = Minio(
                endpoint,
                access_key=self.settings.minio_access_key,
                secret_key=self.settings.minio_secret_key,
                secure=secure,
            )
        except Exception as exc:  # pragma: no cover - optional service
            logger.info("MinIO client unavailable: %s", exc)
            self.client = None

    @property
    def buckets(self) -> list[str]:
        return [
            self.settings.minio_bucket_raw_news,
            self.settings.minio_bucket_raw_social,
            self.settings.minio_bucket_bronze,
            self.settings.minio_bucket_silver,
            self.settings.minio_bucket_gold,
            "model-artifacts",
        ]

    def ensure_buckets(self) -> None:
        if not self.client:
            return
        for bucket in self.buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info("Created MinIO bucket %s", bucket)
            except Exception as exc:  # pragma: no cover - optional service
                logger.warning("MinIO bucket initialization skipped for %s: %s", bucket, exc)
                return

    def put_json(self, bucket: str, object_name: str, payload: bytes) -> None:
        if not self.client:
            logger.info("MinIO not available; skipped upload for %s/%s", bucket, object_name)
            return
        try:
            self.client.put_object(
                bucket,
                object_name,
                BytesIO(payload),
                length=len(payload),
                content_type="application/json",
            )
        except Exception as exc:  # pragma: no cover - optional service
            logger.warning("MinIO upload skipped for %s/%s: %s", bucket, object_name, exc)
