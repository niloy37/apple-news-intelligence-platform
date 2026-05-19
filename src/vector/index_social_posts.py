"""Index social posts into Qdrant."""

from __future__ import annotations

from src.schemas import SocialPostRecord, stable_id
from src.vector.embedding_model import EmbeddingModel
from src.vector.qdrant_client import QdrantVectorStore, VectorPoint


def index_social_posts(
    posts: list[SocialPostRecord],
    model: EmbeddingModel | None = None,
    store: QdrantVectorStore | None = None,
) -> None:
    model = model or EmbeddingModel()
    store = store or QdrantVectorStore()
    store.ensure_collection("social_post_embeddings", model.dimension)
    vectors = model.embed_many([post.text for post in posts])
    store.upsert(
        "social_post_embeddings",
        [
            VectorPoint(
                point_id=stable_id(f"social:{post.post_id}"),
                vector=vector,
                payload={
                    "post_id": post.post_id,
                    "platform": post.platform,
                    "text": post.text,
                    "author": post.author,
                    "created_at": post.created_at.isoformat(),
                    "engagement_score": post.engagement_score,
                },
            )
            for post, vector in zip(posts, vectors, strict=False)
        ],
    )
