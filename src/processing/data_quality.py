"""Data quality checks using Pandera when available, with a pure-Python fallback."""

from __future__ import annotations

from datetime import datetime

from src.schemas import ArticleRecord, SocialPostRecord


class DataQualityError(ValueError):
    """Raised when source data violates quality expectations."""


def validate_articles(articles: list[ArticleRecord]) -> None:
    seen_urls: set[str] = set()
    for article in articles:
        if not str(article.url):
            raise DataQualityError("article URL cannot be null")
        if not article.headline.strip():
            raise DataQualityError("headline cannot be empty")
        if not isinstance(article.published_at, datetime):
            raise DataQualityError("publication date must be valid")
        if article.publisher.strip() == "":
            raise DataQualityError("source name must exist")
        url = str(article.url).lower().rstrip("/")
        if url in seen_urls:
            raise DataQualityError(f"duplicate URL rejected: {url}")
        seen_urls.add(url)


def validate_social_posts(posts: list[SocialPostRecord]) -> None:
    seen_ids: set[str] = set()
    for post in posts:
        if post.post_id in seen_ids:
            raise DataQualityError(f"duplicate social post rejected: {post.post_id}")
        if post.sentiment_score is not None and not -1 <= post.sentiment_score <= 1:
            raise DataQualityError("sentiment score must be between -1 and 1")
        seen_ids.add(post.post_id)
