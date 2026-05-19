"""Keyword and topic assignment for Apple-related stories."""

from __future__ import annotations

import re
from collections import Counter

from src.config import get_settings
from src.processing.entity_extraction import APPLE_PRODUCTS


def extract_keywords(text: str, max_keywords: int = 12) -> list[str]:
    configured = [term for term in get_settings().keywords if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE)]
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", text.lower())
    stopwords = {"the", "and", "for", "with", "from", "that", "this", "into", "about", "apple"}
    common = [word for word, _ in Counter(t for t in tokens if t not in stopwords).most_common(max_keywords)]
    return list(dict.fromkeys(configured + common))[:max_keywords]


def assign_topics(text: str) -> list[str]:
    lowered = text.lower()
    topics: list[str] = []
    topic_rules = {
        "Hardware": ["iphone", "macbook", "ipad", "watch", "vision pro", "chip"],
        "Software": ["ios", "macos", "app store", "apple intelligence", "developer"],
        "Financials": ["earnings", "revenue", "margin", "stock", "forecast"],
        "Supply Chain": ["supply chain", "foxconn", "tsmc", "factory", "production"],
        "Policy": ["lawsuit", "regulator", "antitrust", "privacy", "app store"],
        "AI": ["ai", "artificial intelligence", "apple intelligence", "openai"],
    }
    for topic, markers in topic_rules.items():
        if any(marker in lowered for marker in markers):
            topics.append(topic)
    for product in APPLE_PRODUCTS:
        if product.lower() in lowered:
            topics.append(product)
    return list(dict.fromkeys(topics or ["Apple"]))
