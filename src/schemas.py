"""Shared data contracts used across ingestion, processing, and serving."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid5, NAMESPACE_URL

from pydantic import BaseModel, Field, HttpUrl, field_validator


def stable_id(value: str) -> str:
    """Create a deterministic id from a URL or source-native identifier."""

    return str(uuid5(NAMESPACE_URL, value.strip().lower()))


class ArticleRecord(BaseModel):
    article_id: str | None = None
    url: HttpUrl
    headline: str = Field(min_length=1)
    summary: str = ""
    body: str = ""
    publisher: str = Field(min_length=1)
    author: str | None = None
    published_at: datetime
    source_type: str = "news"
    source_name: str = "unknown"
    country: str | None = None
    language: str = "en"
    image_url: str | None = None
    keywords: list[str] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)
    ingestion_ts: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("headline", "publisher")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field cannot be empty")
        return value

    def model_post_init(self, __context: Any) -> None:
        if self.article_id is None:
            self.article_id = stable_id(str(self.url))


class SocialPostRecord(BaseModel):
    post_id: str
    platform: Literal["reddit", "twitter", "bluesky", "sample"]
    text: str = Field(min_length=1)
    author: str | None = None
    url: str | None = None
    created_at: datetime
    engagement_score: float = 0.0
    sentiment_score: float | None = None
    hashtags: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)
    ingestion_ts: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("text")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("text cannot be empty")
        return value


class EntityRecord(BaseModel):
    entity_id: str
    entity_text: str
    entity_type: str
    source_id: str
    source_kind: Literal["article", "social_post"]


class TrendMetric(BaseModel):
    metric_date: datetime
    topic: str
    product: str | None = None
    article_volume: int = 0
    social_volume: int = 0
    engagement_score: float = 0.0
    average_sentiment: float = 0.0
    recency_score: float = 0.0
    trend_score: float = 0.0


class SemanticSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=50)
    collection: Literal["article_embeddings", "headline_embeddings", "social_post_embeddings"] = "article_embeddings"
