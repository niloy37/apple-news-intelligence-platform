"""RSS connector for technology and business publishers."""

from __future__ import annotations

from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any

from src.config import Settings, get_settings
from src.schemas import ArticleRecord
from src.utils.logging import get_logger

logger = get_logger(__name__)

DEFAULT_RSS_FEEDS = {
    "The Verge Apple": "https://www.theverge.com/rss/apple/index.xml",
    "MacRumors": "https://www.macrumors.com/macrumors.xml",
    "9to5Mac": "https://9to5mac.com/feed/",
    "TechCrunch": "https://techcrunch.com/feed/",
    "Engadget": "https://www.engadget.com/rss.xml",
}


class RssClient:
    """Fetch articles from public RSS feeds exposed by publishers."""

    def __init__(self, feeds: dict[str, str] | None = None, settings: Settings | None = None) -> None:
        self.feeds = feeds or DEFAULT_RSS_FEEDS
        self.settings = settings or get_settings()

    def fetch_articles(self, max_per_feed: int = 25) -> list[ArticleRecord]:
        try:
            import feedparser
        except ImportError:
            logger.warning("feedparser is not installed; RSS ingestion skipped")
            return []

        records: list[ArticleRecord] = []
        for publisher, feed_url in self.feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:max_per_feed]:
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    text = f"{title} {summary}".lower()
                    if not any(keyword.lower() in text for keyword in self.settings.keywords):
                        continue
                    records.append(self._to_article(publisher, entry))
            except Exception as exc:
                logger.warning("RSS feed failed for %s: %s", publisher, exc)
        return records

    def _to_article(self, publisher: str, entry: dict[str, Any]) -> ArticleRecord:
        published = entry.get("published") or entry.get("updated")
        published_at = self._parse_rss_date(published)
        title = entry.get("title") or "Untitled Apple story"
        return ArticleRecord(
            url=entry.get("link"),
            headline=title,
            summary=entry.get("summary", ""),
            body=entry.get("summary", ""),
            publisher=publisher,
            author=entry.get("author"),
            published_at=published_at,
            source_type="rss",
            source_name=publisher,
            language="en",
            keywords=[term for term in self.settings.keywords if term.lower() in title.lower()],
            raw=dict(entry),
        )

    @staticmethod
    def _parse_rss_date(value: str | None) -> datetime:
        if not value:
            return datetime.now(UTC)
        try:
            parsed = parsedate_to_datetime(value)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=UTC)
            return parsed.astimezone(UTC)
        except Exception:
            return datetime.now(UTC)
