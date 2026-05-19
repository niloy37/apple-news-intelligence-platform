"""Social post cleaning and normalization."""

from __future__ import annotations

import re

from src.processing.clean_articles import clean_text
from src.schemas import SocialPostRecord
from src.utils.time import ensure_utc

HASHTAG_RE = re.compile(r"#([A-Za-z0-9_]+)")


def extract_hashtags(text: str) -> list[str]:
    return sorted({match.group(1) for match in HASHTAG_RE.finditer(text)})


def clean_social_post(post: SocialPostRecord) -> SocialPostRecord:
    text = clean_text(post.text)
    hashtags = sorted(set(post.hashtags + extract_hashtags(text)))
    return post.model_copy(
        update={
            "text": text,
            "created_at": ensure_utc(post.created_at),
            "hashtags": hashtags,
        }
    )


def clean_social_posts(posts: list[SocialPostRecord]) -> list[SocialPostRecord]:
    return [clean_social_post(post) for post in posts]
