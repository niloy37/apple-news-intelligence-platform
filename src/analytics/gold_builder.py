"""Build analytics-ready gold datasets for the API and dashboard."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any

from src.processing.entity_extraction import extract_article_entities, extract_social_entities
from src.processing.topic_modeling import assign_topics
from src.schemas import ArticleRecord, SocialPostRecord, TrendMetric


def _hour_bucket(value: datetime) -> str:
    return value.replace(minute=0, second=0, microsecond=0).isoformat()


def build_gold_metrics(
    articles: list[ArticleRecord],
    posts: list[SocialPostRecord],
    trends: list[TrendMetric],
    article_sentiment: dict[str, float],
    social_sentiment: dict[str, float],
) -> dict[str, Any]:
    publishers = Counter(article.publisher for article in articles)
    hashtags = Counter(tag for post in posts for tag in post.hashtags)

    product_counter: Counter[str] = Counter()
    topic_counter: Counter[str] = Counter()
    for article in articles:
        text = f"{article.headline} {article.summary}"
        topic_counter.update(assign_topics(text))
        for entity in extract_article_entities(article):
            if entity.entity_type == "Product":
                product_counter[entity.entity_text] += 1
    for post in posts:
        topic_counter.update(assign_topics(post.text))
        for entity in extract_social_entities(post):
            if entity.entity_type == "Product":
                product_counter[entity.entity_text] += 1

    article_volume = defaultdict(int)
    social_volume = defaultdict(int)
    sentiment_timeline = defaultdict(list)
    for article in articles:
        bucket = _hour_bucket(article.published_at)
        article_volume[bucket] += 1
        sentiment_timeline[bucket].append(article_sentiment.get(article.article_id or "", 0.0))
    for post in posts:
        bucket = _hour_bucket(post.created_at)
        social_volume[bucket] += 1
        sentiment_timeline[bucket].append(social_sentiment.get(post.post_id, post.sentiment_score or 0.0))

    all_buckets = sorted(set(article_volume) | set(social_volume) | set(sentiment_timeline))
    timeseries = [
        {
            "timestamp": bucket,
            "article_volume": article_volume[bucket],
            "social_volume": social_volume[bucket],
            "average_sentiment": round(
                sum(sentiment_timeline[bucket]) / max(len(sentiment_timeline[bucket]), 1),
                4,
            ),
        }
        for bucket in all_buckets
    ]

    countries = Counter(article.country or "Unknown" for article in articles)
    return {
        "summary": {
            "article_count": len(articles),
            "social_post_count": len(posts),
            "publisher_count": len(publishers),
            "topic_count": len(topic_counter),
            "average_sentiment": round(
                (
                    sum(article_sentiment.values()) + sum(social_sentiment.values())
                )
                / max(len(article_sentiment) + len(social_sentiment), 1),
                4,
            ),
        },
        "top_publishers": [{"publisher": name, "article_count": count} for name, count in publishers.most_common(15)],
        "top_products": [{"product": name, "mentions": count} for name, count in product_counter.most_common(15)],
        "top_topics": [{"topic": name, "mentions": count} for name, count in topic_counter.most_common(15)],
        "top_hashtags": [{"hashtag": tag, "mentions": count} for tag, count in hashtags.most_common(15)],
        "countries": [{"country": country, "article_count": count} for country, count in countries.most_common()],
        "trends": [trend.model_dump(mode="json") for trend in trends],
        "timeseries": timeseries,
        "latest_headlines": [
            {
                "article_id": article.article_id,
                "headline": article.headline,
                "summary": article.summary,
                "url": str(article.url),
                "publisher": article.publisher,
                "published_at": article.published_at.isoformat(),
                "sentiment_score": article_sentiment.get(article.article_id or "", 0.0),
            }
            for article in sorted(articles, key=lambda item: item.published_at, reverse=True)[:50]
        ],
        "social_buzz": [
            {
                "post_id": post.post_id,
                "platform": post.platform,
                "text": post.text,
                "author": post.author,
                "created_at": post.created_at.isoformat(),
                "engagement_score": post.engagement_score,
                "sentiment_score": social_sentiment.get(post.post_id, post.sentiment_score or 0.0),
            }
            for post in sorted(posts, key=lambda item: item.engagement_score, reverse=True)[:75]
        ],
    }
