"""Article cleaning and normalization."""

from __future__ import annotations

import html
import re
from src.schemas import ArticleRecord
from src.utils.time import ensure_utc

TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    value = TAG_RE.sub(" ", value)
    value = WHITESPACE_RE.sub(" ", value)
    return value.strip()


def detect_language(text: str) -> str:
    try:
        from langdetect import detect

        return detect(text[:500]) if text.strip() else "unknown"
    except Exception:
        return "en"


def clean_article(article: ArticleRecord) -> ArticleRecord:
    headline = clean_text(article.headline)
    summary = clean_text(article.summary)
    body = clean_text(article.body)
    language = article.language or detect_language(f"{headline} {summary} {body}")
    return article.model_copy(
        update={
            "headline": headline,
            "summary": summary,
            "body": body,
            "publisher": clean_text(article.publisher),
            "published_at": ensure_utc(article.published_at),
            "language": language,
        }
    )


def clean_articles(articles: list[ArticleRecord]) -> list[ArticleRecord]:
    return [clean_article(article) for article in articles]
