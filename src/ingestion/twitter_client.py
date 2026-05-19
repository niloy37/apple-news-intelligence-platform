"""X/Twitter API v2 connector that runs only when a bearer token is provided."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.config import Settings, get_settings
from src.schemas import SocialPostRecord
from src.utils.logging import get_logger

logger = get_logger(__name__)

RECENT_SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"


class TwitterClient:
    """Fetch recent tweets from the official API when credentials are available."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def fetch_posts(self, limit: int = 100) -> list[SocialPostRecord]:
        if not self.settings.x_bearer_token:
            logger.info("X_BEARER_TOKEN is not set; Twitter ingestion skipped")
            return []
        try:
            import httpx

            query = "(" + " OR ".join(f'"{term}"' if " " in term else term for term in self.settings.keywords) + ") lang:en"
            params = {
                "query": query,
                "max_results": min(max(limit, 10), 100),
                "tweet.fields": "created_at,author_id,public_metrics,entities,lang",
            }
            headers = {"Authorization": f"Bearer {self.settings.x_bearer_token}"}
            response = httpx.get(RECENT_SEARCH_URL, params=params, headers=headers, timeout=20)
            response.raise_for_status()
            return [self._to_post(item) for item in response.json().get("data", [])]
        except Exception as exc:
            logger.warning("Twitter fetch failed; source skipped: %s", exc)
            return []

    def _to_post(self, item: dict[str, Any]) -> SocialPostRecord:
        metrics = item.get("public_metrics", {})
        text = item.get("text") or ""
        hashtags = [
            tag.get("tag", "")
            for tag in item.get("entities", {}).get("hashtags", [])
            if tag.get("tag")
        ]
        created_at = datetime.fromisoformat(item.get("created_at", "").replace("Z", "+00:00"))
        return SocialPostRecord(
            post_id=item["id"],
            platform="twitter",
            text=text,
            author=item.get("author_id"),
            url=f"https://x.com/i/web/status/{item['id']}",
            created_at=created_at.astimezone(UTC),
            engagement_score=float(
                metrics.get("like_count", 0)
                + metrics.get("reply_count", 0)
                + metrics.get("retweet_count", 0)
                + metrics.get("quote_count", 0)
            ),
            hashtags=hashtags,
            keywords=[term for term in self.settings.keywords if term.lower() in text.lower()],
            raw=item,
        )
