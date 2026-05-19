"""Optional NewsAPI connector, enabled only when NEWS_API_KEY is set."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.config import Settings, get_settings
from src.schemas import ArticleRecord
from src.utils.logging import get_logger

logger = get_logger(__name__)

NEWS_API_URL = "https://newsapi.org/v2/everything"


class NewsApiClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def fetch_articles(self, max_records: int = 100) -> list[ArticleRecord]:
        if not self.settings.news_api_key:
            logger.info("NEWS_API_KEY is not set; NewsAPI ingestion skipped")
            return []
        try:
            import httpx

            response = httpx.get(
                NEWS_API_URL,
                params={
                    "q": " OR ".join(self.settings.keywords[:10]),
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": min(max_records, 100),
                    "apiKey": self.settings.news_api_key,
                },
                timeout=30,
            )
            response.raise_for_status()
            return [self._to_article(item) for item in response.json().get("articles", []) if item.get("url")]
        except Exception as exc:
            logger.warning("NewsAPI fetch failed; source skipped: %s", exc)
            return []

    def _to_article(self, item: dict[str, Any]) -> ArticleRecord:
        published_at = datetime.fromisoformat(item["publishedAt"].replace("Z", "+00:00")).astimezone(UTC)
        source = item.get("source") or {}
        title = item.get("title") or "Untitled Apple story"
        return ArticleRecord(
            url=item["url"],
            headline=title,
            summary=item.get("description") or "",
            body=item.get("content") or item.get("description") or "",
            publisher=source.get("name") or "NewsAPI",
            author=item.get("author"),
            published_at=published_at,
            source_type="newsapi",
            source_name="NewsAPI",
            language="en",
            image_url=item.get("urlToImage"),
            keywords=[term for term in self.settings.keywords if term.lower() in title.lower()],
            raw=item,
        )
