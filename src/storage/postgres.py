"""PostgreSQL repository for analytical metadata and gold tables."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import UUID, uuid5, NAMESPACE_DNS

from src.config import Settings, get_settings
from src.schemas import ArticleRecord, SocialPostRecord, TrendMetric
from src.utils.logging import get_logger

logger = get_logger(__name__)


def _uuid_from_text(value: str) -> UUID:
    return uuid5(NAMESPACE_DNS, value.strip().lower())


@dataclass
class PostgresRepository:
    settings: Settings = field(default_factory=get_settings)
    _psycopg: Any | None = None

    def _connect(self) -> Any:
        try:
            import psycopg

            return psycopg.connect(self.settings.postgres_dsn)
        except Exception as exc:  # pragma: no cover - optional service
            logger.warning("PostgreSQL connection unavailable: %s", exc)
            return None

    def initialize_schema(self) -> None:
        conn = self._connect()
        if not conn:
            return
        schema_path = Path(__file__).with_name("schema.sql")
        with conn, conn.cursor() as cursor:
            cursor.execute(schema_path.read_text(encoding="utf-8"))

    def upsert_articles(self, articles: list[ArticleRecord], sentiment_by_id: dict[str, float] | None = None) -> None:
        conn = self._connect()
        if not conn:
            return
        sentiment_by_id = sentiment_by_id or {}
        with conn, conn.cursor() as cursor:
            for article in articles:
                cursor.execute(
                    """
                    INSERT INTO publishers (publisher_id, name, country, domain)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (name) DO NOTHING
                    """,
                    (_uuid_from_text(article.publisher), article.publisher, article.country, article.publisher),
                )
                if article.author:
                    cursor.execute(
                        """
                        INSERT INTO authors (author_id, name)
                        VALUES (%s, %s)
                        ON CONFLICT (name) DO NOTHING
                        """,
                        (_uuid_from_text(article.author), article.author),
                    )
                cursor.execute(
                    """
                    INSERT INTO articles (
                        article_id, url, headline, summary, body, publisher, author, published_at,
                        source_type, source_name, country, language, image_url, sentiment_score
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET
                        headline = EXCLUDED.headline,
                        summary = EXCLUDED.summary,
                        body = EXCLUDED.body,
                        publisher = EXCLUDED.publisher,
                        sentiment_score = EXCLUDED.sentiment_score
                    """,
                    (
                        UUID(article.article_id),
                        str(article.url),
                        article.headline,
                        article.summary,
                        article.body,
                        article.publisher,
                        article.author,
                        article.published_at,
                        article.source_type,
                        article.source_name,
                        article.country,
                        article.language,
                        article.image_url,
                        sentiment_by_id.get(article.article_id),
                    ),
                )

    def upsert_social_posts(
        self, posts: list[SocialPostRecord], sentiment_by_id: dict[str, float] | None = None
    ) -> None:
        conn = self._connect()
        if not conn:
            return
        sentiment_by_id = sentiment_by_id or {}
        with conn, conn.cursor() as cursor:
            for post in posts:
                cursor.execute(
                    """
                    INSERT INTO social_posts (
                        post_id, platform, text, author, url, created_at, engagement_score, sentiment_score
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (post_id) DO UPDATE SET
                        text = EXCLUDED.text,
                        engagement_score = EXCLUDED.engagement_score,
                        sentiment_score = EXCLUDED.sentiment_score
                    """,
                    (
                        post.post_id,
                        post.platform,
                        post.text,
                        post.author,
                        post.url,
                        post.created_at,
                        post.engagement_score,
                        sentiment_by_id.get(post.post_id, post.sentiment_score),
                    ),
                )

    def upsert_trends(self, trends: list[TrendMetric]) -> None:
        conn = self._connect()
        if not conn:
            return
        with conn, conn.cursor() as cursor:
            for trend in trends:
                cursor.execute(
                    """
                    INSERT INTO trend_metrics (
                        metric_date, topic, product, article_volume, social_volume,
                        engagement_score, average_sentiment, recency_score, trend_score
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (metric_date, topic, product) DO UPDATE SET
                        article_volume = EXCLUDED.article_volume,
                        social_volume = EXCLUDED.social_volume,
                        engagement_score = EXCLUDED.engagement_score,
                        average_sentiment = EXCLUDED.average_sentiment,
                        recency_score = EXCLUDED.recency_score,
                        trend_score = EXCLUDED.trend_score
                    """,
                    (
                        trend.metric_date,
                        trend.topic,
                        trend.product or "",
                        trend.article_volume,
                        trend.social_volume,
                        trend.engagement_score,
                        trend.average_sentiment,
                        trend.recency_score,
                        trend.trend_score,
                    ),
                )

    def fetch_latest_articles(self, limit: int = 25) -> list[dict[str, Any]]:
        conn = self._connect()
        if not conn:
            return []
        with conn, conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT article_id::text, url, headline, summary, publisher, author, published_at,
                       source_type, country, language, sentiment_score
                FROM articles
                ORDER BY published_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            cols = [desc[0] for desc in cursor.description]
            return [dict(zip(cols, row, strict=False)) for row in cursor.fetchall()]
