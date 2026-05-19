"""Semantic search service over Qdrant collections."""

from __future__ import annotations

from src.vector.embedding_model import EmbeddingModel
from src.vector.qdrant_client import QdrantVectorStore


class SemanticSearchService:
    def __init__(self, model: EmbeddingModel | None = None, store: QdrantVectorStore | None = None) -> None:
        self.model = model or EmbeddingModel()
        self.store = store or QdrantVectorStore()

    def search(self, query: str, collection: str = "article_embeddings", limit: int = 10) -> list[dict]:
        vector = self.model.embed(query)
        return self.store.search(collection, vector, limit=limit)
