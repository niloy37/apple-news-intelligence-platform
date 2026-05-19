"""Sentiment scoring with dependency-free fallback."""

from __future__ import annotations

import math

POSITIVE_TERMS = {
    "growth",
    "record",
    "surge",
    "strong",
    "improve",
    "upgrade",
    "innovative",
    "beat",
    "popular",
    "excited",
    "optimistic",
    "breakthrough",
}

NEGATIVE_TERMS = {
    "decline",
    "weak",
    "delay",
    "lawsuit",
    "probe",
    "ban",
    "bug",
    "risk",
    "concern",
    "miss",
    "controversy",
    "complaint",
}


def score_sentiment(text: str) -> float:
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        return float(SentimentIntensityAnalyzer().polarity_scores(text)["compound"])
    except Exception:
        words = [word.strip(".,!?;:()[]{}\"'").lower() for word in text.split()]
        positive = sum(1 for word in words if word in POSITIVE_TERMS)
        negative = sum(1 for word in words if word in NEGATIVE_TERMS)
        if positive == negative == 0:
            return 0.0
        raw = (positive - negative) / max(positive + negative, 1)
        return round(math.tanh(raw), 4)


def score_records(records: list[tuple[str, str]]) -> dict[str, float]:
    return {record_id: score_sentiment(text) for record_id, text in records}
