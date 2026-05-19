"""Gold-layer trend metric calculations."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta

from src.processing.topic_modeling import assign_topics
from src.schemas import ArticleRecord, SocialPostRecord, TrendMetric


def recency_weight(timestamp: datetime, now: datetime | None = None) -> float:
    now = now or datetime.now(UTC)
    age_hours = max((now - timestamp.astimezone(UTC)).total_seconds() / 3600, 0)
    return max(0.0, 1.0 - min(age_hours / 72, 1.0))


def calculate_trends(
    articles: list[ArticleRecord],
    posts: list[SocialPostRecord],
    article_sentiment: dict[str, float] | None = None,
    social_sentiment: dict[str, float] | None = None,
    now: datetime | None = None,
) -> list[TrendMetric]:
    now = now or datetime.now(UTC)
    article_sentiment = article_sentiment or {}
    social_sentiment = social_sentiment or {}
    buckets: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for article in articles:
        text = f"{article.headline} {article.summary}"
        for topic in assign_topics(text):
            bucket = buckets[topic]
            bucket["article_volume"] += 1
            bucket["sentiment_sum"] += article_sentiment.get(article.article_id or "", 0.0)
            bucket["sentiment_count"] += 1
            bucket["recency"] += recency_weight(article.published_at, now)

    for post in posts:
        for topic in assign_topics(post.text):
            bucket = buckets[topic]
            bucket["social_volume"] += 1
            bucket["engagement"] += float(post.engagement_score)
            bucket["sentiment_sum"] += social_sentiment.get(post.post_id, post.sentiment_score or 0.0)
            bucket["sentiment_count"] += 1
            bucket["recency"] += recency_weight(post.created_at, now)

    metrics: list[TrendMetric] = []
    metric_date = now.replace(minute=0, second=0, microsecond=0)
    for topic, values in buckets.items():
        article_volume = int(values["article_volume"])
        social_volume = int(values["social_volume"])
        engagement = float(values["engagement"])
        sentiment_count = max(values["sentiment_count"], 1)
        avg_sentiment = values["sentiment_sum"] / sentiment_count
        recency = float(values["recency"])
        trend_score = (
            article_volume * 2.0
            + social_volume * 1.2
            + min(engagement / 25.0, 40.0)
            + max(avg_sentiment, 0) * 5.0
            + recency * 3.0
        )
        metrics.append(
            TrendMetric(
                metric_date=metric_date,
                topic=topic,
                product=topic if topic.lower() in {p.lower() for p in ["iPhone", "MacBook", "iPad", "Vision Pro", "Apple Watch"]} else None,
                article_volume=article_volume,
                social_volume=social_volume,
                engagement_score=round(engagement, 2),
                average_sentiment=round(avg_sentiment, 4),
                recency_score=round(recency, 4),
                trend_score=round(trend_score, 4),
            )
        )
    return sorted(metrics, key=lambda metric: metric.trend_score, reverse=True)
