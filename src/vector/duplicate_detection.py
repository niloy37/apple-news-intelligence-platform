"""Near-duplicate detection using headline embeddings."""

from __future__ import annotations

from itertools import combinations

from src.schemas import ArticleRecord
from src.vector.embedding_model import EmbeddingModel
from src.vector.qdrant_client import cosine_similarity


def find_near_duplicate_headlines(
    articles: list[ArticleRecord],
    threshold: float = 0.88,
    model: EmbeddingModel | None = None,
) -> list[dict[str, object]]:
    model = model or EmbeddingModel()
    vectors = model.embed_many([article.headline for article in articles])
    duplicates: list[dict[str, object]] = []
    for (left_article, left_vector), (right_article, right_vector) in combinations(zip(articles, vectors, strict=False), 2):
        score = cosine_similarity(left_vector, right_vector)
        if score >= threshold:
            duplicates.append(
                {
                    "left_article_id": left_article.article_id,
                    "right_article_id": right_article.article_id,
                    "left_headline": left_article.headline,
                    "right_headline": right_article.headline,
                    "score": round(score, 4),
                }
            )
    return duplicates
