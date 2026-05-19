"""Initialize Qdrant collections."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.vector.embedding_model import EmbeddingModel
from src.vector.qdrant_client import QdrantVectorStore


if __name__ == "__main__":
    model = EmbeddingModel()
    store = QdrantVectorStore()
    for collection in ["article_embeddings", "headline_embeddings", "social_post_embeddings"]:
        store.ensure_collection(collection, model.dimension)
    print("Qdrant collections initialized")
