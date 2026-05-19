"""Duplicate and near-duplicate detection."""

from __future__ import annotations

import hashlib
import re
from difflib import SequenceMatcher
from typing import Iterable

from src.schemas import ArticleRecord, SocialPostRecord

NORMALIZE_RE = re.compile(r"[^a-z0-9 ]+")


def normalize_title(value: str) -> str:
    lowered = value.lower()
    lowered = NORMALIZE_RE.sub(" ", lowered)
    return " ".join(lowered.split())


def fingerprint(value: str) -> str:
    return hashlib.sha1(normalize_title(value).encode("utf-8")).hexdigest()


def deduplicate_articles(articles: Iterable[ArticleRecord], near_duplicate_threshold: float = 0.92) -> list[ArticleRecord]:
    unique: list[ArticleRecord] = []
    seen_urls: set[str] = set()
    seen_fingerprints: set[str] = set()
    for article in articles:
        url = str(article.url).lower().rstrip("/")
        title_fp = fingerprint(article.headline)
        if url in seen_urls or title_fp in seen_fingerprints:
            continue
        if any(SequenceMatcher(None, normalize_title(article.headline), normalize_title(item.headline)).ratio() >= near_duplicate_threshold for item in unique):
            continue
        seen_urls.add(url)
        seen_fingerprints.add(title_fp)
        unique.append(article)
    return unique


def deduplicate_social_posts(posts: Iterable[SocialPostRecord]) -> list[SocialPostRecord]:
    unique: list[SocialPostRecord] = []
    seen_ids: set[str] = set()
    seen_texts: set[str] = set()
    for post in posts:
        text_fp = fingerprint(post.text)
        if post.post_id in seen_ids or text_fp in seen_texts:
            continue
        seen_ids.add(post.post_id)
        seen_texts.add(text_fp)
        unique.append(post)
    return unique
