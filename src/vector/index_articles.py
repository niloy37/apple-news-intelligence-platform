"""Index article records into Qdrant collections."""

from __future__ import annotations

from src.schemas import ArticleRecord, stable_id
from src.vector.embedding_model import EmbeddingModel
from src.vector.qdrant_client import QdrantVectorStore, VectorPoint


def index_articles(
    articles: list[ArticleRecord],
    model: EmbeddingModel | None = None,
    store: QdrantVectorStore | None = None,
) -> None:
    model = model or EmbeddingModel()
    store = store or QdrantVectorStore()
    store.ensure_collection("article_embeddings", model.dimension)
    store.ensure_collection("headline_embeddings", model.dimension)

    article_texts = [f"{article.headline}\n{article.summary}\n{article.body}" for article in articles]
    headline_texts = [article.headline for article in articles]
    article_vectors = model.embed_many(article_texts)
    headline_vectors = model.embed_many(headline_texts)

    store.upsert(
        "article_embeddings",
        [
            VectorPoint(
                point_id=article.article_id or str(article.url),
                vector=vector,
                payload={
                    "article_id": article.article_id,
                    "url": str(article.url),
                    "headline": article.headline,
                    "publisher": article.publisher,
                    "published_at": article.published_at.isoformat(),
                },
            )
            for article, vector in zip(articles, article_vectors, strict=False)
        ],
    )
    store.upsert(
        "headline_embeddings",
        [
            VectorPoint(
                point_id=stable_id(f"headline:{article.article_id}"),
                vector=vector,
                payload={
                    "article_id": article.article_id,
                    "headline": article.headline,
                    "url": str(article.url),
                },
            )
            for article, vector in zip(articles, headline_vectors, strict=False)
        ],
    )
