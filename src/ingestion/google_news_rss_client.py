"""Optional Google News RSS connector for Apple keyword queries."""

from __future__ import annotations

from urllib.parse import quote_plus

from src.config import Settings, get_settings
from src.ingestion.rss_client import RssClient
from src.schemas import ArticleRecord


class GoogleNewsRssClient:
    """Fetch Google News RSS query feeds where usage is allowed."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def fetch_articles(self, max_per_query: int = 20) -> list[ArticleRecord]:
        feeds = {
            f"Google News {keyword}": (
                "https://news.google.com/rss/search?"
                f"q={quote_plus(keyword)}&hl=en-US&gl=US&ceid=US:en"
            )
            for keyword in self.settings.keywords[:8]
        }
        return RssClient(feeds=feeds, settings=self.settings).fetch_articles(max_per_feed=max_per_query)
