"""GDELT DOC API connector for Apple-related news."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.config import Settings, get_settings
from src.schemas import ArticleRecord
from src.utils.logging import get_logger

logger = get_logger(__name__)

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"


class GdeltClient:
    """Fetch articles from the public GDELT DOC API."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def build_query(self) -> str:
        terms = [f'"{term}"' if " " in term else term for term in self.settings.keywords]
        return "(" + " OR ".join(terms) + ")"

    def fetch_articles(self, max_records: int = 100) -> list[ArticleRecord]:
        try:
            import httpx

            params = {
                "query": self.build_query(),
                "mode": "ArtList",
                "format": "json",
                "maxrecords": max_records,
                "sort": "HybridRel",
            }
            response = httpx.get(GDELT_DOC_API, params=params, timeout=30.0)
            response.raise_for_status()
            payload = response.json()
            return [self._to_article(item) for item in payload.get("articles", []) if item.get("url")]
        except Exception as exc:
            logger.warning("GDELT fetch failed; use sample data fallback: %s", exc)
            return []

    def _to_article(self, item: dict[str, Any]) -> ArticleRecord:
        published_at = self._parse_gdelt_date(item.get("seendate"))
        domain = item.get("domain") or item.get("sourceCommonName") or "GDELT"
        return ArticleRecord(
            url=item["url"],
            headline=item.get("title") or "Untitled Apple story",
            summary=item.get("snippet") or "",
            body=item.get("snippet") or "",
            publisher=domain,
            author=None,
            published_at=published_at,
            source_type="gdelt",
            source_name="GDELT DOC API",
            country=item.get("sourceCountry"),
            language=item.get("language") or "en",
            image_url=item.get("socialimage"),
            keywords=[term for term in self.settings.keywords if term.lower() in (item.get("title") or "").lower()],
            raw=item,
        )

    @staticmethod
    def _parse_gdelt_date(value: str | None) -> datetime:
        if not value:
            return datetime.now(UTC)
        for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%d%H%M%S"):
            try:
                return datetime.strptime(value, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        return datetime.now(UTC)
