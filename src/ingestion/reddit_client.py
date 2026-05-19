"""Reddit connector for Apple-related social discussion."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.config import Settings, get_settings
from src.schemas import SocialPostRecord
from src.utils.logging import get_logger

logger = get_logger(__name__)


class RedditClient:
    """Fetch Reddit posts via PRAW when credentials exist, otherwise public JSON."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def fetch_posts(self, limit: int = 100) -> list[SocialPostRecord]:
        if self.settings.reddit_client_id and self.settings.reddit_client_secret:
            return self._fetch_with_praw(limit)
        return self._fetch_public_json(limit)

    def _fetch_with_praw(self, limit: int) -> list[SocialPostRecord]:
        try:
            import praw

            reddit = praw.Reddit(
                client_id=self.settings.reddit_client_id,
                client_secret=self.settings.reddit_client_secret,
                user_agent=self.settings.reddit_user_agent,
            )
            query = " OR ".join(self.settings.keywords)
            posts = reddit.subreddit("all").search(query, sort="new", limit=limit)
            return [self._from_reddit_like(post) for post in posts]
        except Exception as exc:
            logger.warning("PRAW fetch failed; trying public JSON fallback: %s", exc)
            return self._fetch_public_json(limit)

    def _fetch_public_json(self, limit: int) -> list[SocialPostRecord]:
        try:
            import httpx

            url = "https://www.reddit.com/search.json"
            query = " OR ".join(self.settings.keywords[:8])
            headers = {"User-Agent": self.settings.reddit_user_agent}
            response = httpx.get(url, params={"q": query, "sort": "new", "limit": limit}, headers=headers, timeout=20)
            response.raise_for_status()
            children = response.json().get("data", {}).get("children", [])
            return [self._from_public_json(child.get("data", {})) for child in children]
        except Exception as exc:
            logger.warning("Reddit public JSON fetch failed; use sample social fallback: %s", exc)
            return []

    def _from_reddit_like(self, post: Any) -> SocialPostRecord:
        text = f"{getattr(post, 'title', '')} {getattr(post, 'selftext', '')}".strip()
        return SocialPostRecord(
            post_id=str(getattr(post, "id")),
            platform="reddit",
            text=text,
            author=str(getattr(post, "author", "") or ""),
            url=f"https://reddit.com{getattr(post, 'permalink', '')}",
            created_at=datetime.fromtimestamp(float(getattr(post, "created_utc", 0)), tz=UTC),
            engagement_score=float(getattr(post, "score", 0)) + float(getattr(post, "num_comments", 0)),
            hashtags=[],
            keywords=[term for term in self.settings.keywords if term.lower() in text.lower()],
            raw={"id": getattr(post, "id", None), "subreddit": str(getattr(post, "subreddit", ""))},
        )

    def _from_public_json(self, data: dict[str, Any]) -> SocialPostRecord:
        text = f"{data.get('title', '')} {data.get('selftext', '')}".strip()
        return SocialPostRecord(
            post_id=str(data.get("id")),
            platform="reddit",
            text=text,
            author=data.get("author"),
            url=f"https://reddit.com{data.get('permalink', '')}",
            created_at=datetime.fromtimestamp(float(data.get("created_utc", 0)), tz=UTC),
            engagement_score=float(data.get("score", 0)) + float(data.get("num_comments", 0)),
            hashtags=[],
            keywords=[term for term in self.settings.keywords if term.lower() in text.lower()],
            raw=data,
        )
