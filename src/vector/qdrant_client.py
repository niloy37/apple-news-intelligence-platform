"""Qdrant vector database adapter with in-memory fallback."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from src.config import Settings, get_settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    length = min(len(left), len(right))
    dot = sum(left[i] * right[i] for i in range(length))
    left_norm = math.sqrt(sum(value * value for value in left[:length])) or 1.0
    right_norm = math.sqrt(sum(value * value for value in right[:length])) or 1.0
    return dot / (left_norm * right_norm)


@dataclass
class VectorPoint:
    point_id: str
    vector: list[float]
    payload: dict[str, Any]


@dataclass
class QdrantVectorStore:
    settings: Settings = field(default_factory=get_settings)
    client: Any | None = None
    memory: dict[str, list[VectorPoint]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.settings.qdrant_url.startswith("memory://"):
            self.client = None
            return
        try:
            from qdrant_client import QdrantClient

            self.client = QdrantClient(url=self.settings.qdrant_url, timeout=5)
            self.client.get_collections()
        except Exception as exc:  # pragma: no cover - optional service
            logger.warning("Qdrant unavailable; using in-memory vector store: %s", exc)
            self.client = None

    def ensure_collection(self, collection: str, dimension: int) -> None:
        if self.client:
            from qdrant_client.models import Distance, VectorParams

            collections = {item.name for item in self.client.get_collections().collections}
            if collection not in collections:
                self.client.create_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
                )
        self.memory.setdefault(collection, [])

    def upsert(self, collection: str, points: list[VectorPoint]) -> None:
        if self.client:
            from qdrant_client.models import PointStruct

            self.client.upsert(
                collection_name=collection,
                points=[
                    PointStruct(id=point.point_id, vector=point.vector, payload=point.payload)
                    for point in points
                ],
            )
        self.memory.setdefault(collection, [])
        existing = {point.point_id: point for point in self.memory[collection]}
        for point in points:
            existing[point.point_id] = point
        self.memory[collection] = list(existing.values())

    def search(self, collection: str, query_vector: list[float], limit: int = 10) -> list[dict[str, Any]]:
        if self.client:
            hits = self.client.search(collection_name=collection, query_vector=query_vector, limit=limit)
            return [
                {
                    "id": str(hit.id),
                    "score": float(hit.score),
                    "payload": hit.payload or {},
                }
                for hit in hits
            ]
        hits = [
            {
                "id": point.point_id,
                "score": cosine_similarity(query_vector, point.vector),
                "payload": point.payload,
            }
            for point in self.memory.get(collection, [])
        ]
        return sorted(hits, key=lambda hit: hit["score"], reverse=True)[:limit]
