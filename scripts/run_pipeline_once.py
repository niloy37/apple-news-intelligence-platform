"""Run the full local pipeline once from ingestion through gold outputs."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from scripts.seed_sample_data import build_sample_dataset, write_sample_data
from src.analytics.gold_builder import build_gold_metrics
from src.config import get_settings
from src.graph.build_article_graph import build_article_graph
from src.graph.build_social_graph import build_social_graph
from src.graph.neo4j_client import Neo4jGraphClient
from src.ingestion.gdelt_client import GdeltClient
from src.ingestion.google_news_rss_client import GoogleNewsRssClient
from src.ingestion.newsapi_client import NewsApiClient
from src.ingestion.producer import EventProducer
from src.ingestion.reddit_client import RedditClient
from src.ingestion.rss_client import RssClient
from src.ingestion.twitter_client import TwitterClient
from src.processing.clean_articles import clean_articles
from src.processing.clean_social_posts import clean_social_posts
from src.processing.data_quality import validate_articles, validate_social_posts
from src.processing.deduplicate import deduplicate_articles, deduplicate_social_posts
from src.processing.sentiment import score_records
from src.processing.trend_calculator import calculate_trends
from src.storage.file_lake import LocalLakehouse
from src.storage.minio_client import MinioObjectStore
from src.storage.postgres import PostgresRepository
from src.vector.embedding_model import EmbeddingModel
from src.vector.index_articles import index_articles
from src.vector.index_social_posts import index_social_posts
from src.vector.qdrant_client import QdrantVectorStore


def run_pipeline_once(use_live_sources: bool = True) -> dict[str, int]:
    settings = get_settings()
    lake = LocalLakehouse(settings=settings)
    producer = EventProducer(settings=settings)

    live_articles = []
    live_posts = []
    if use_live_sources:
        live_articles.extend(GdeltClient(settings).fetch_articles(max_records=100))
        live_articles.extend(RssClient(settings=settings).fetch_articles(max_per_feed=20))
        live_articles.extend(GoogleNewsRssClient(settings).fetch_articles(max_per_query=10))
        live_articles.extend(NewsApiClient(settings).fetch_articles(max_records=100))
        live_posts.extend(RedditClient(settings).fetch_posts(limit=100))
        live_posts.extend(TwitterClient(settings).fetch_posts(limit=100))

    sample_articles, sample_posts = build_sample_dataset()
    articles = live_articles if len(live_articles) >= 25 else sample_articles
    posts = live_posts if len(live_posts) >= 50 else sample_posts

    lake.write_jsonl("raw", "raw_articles.jsonl", [article.model_dump(mode="json") for article in articles])
    lake.write_jsonl("raw", "raw_social_posts.jsonl", [post.model_dump(mode="json") for post in posts])
    for article in articles:
        producer.publish("news.raw", article.article_id or str(article.url), article.model_dump(mode="json"))
    for post in posts:
        producer.publish("social.raw", post.post_id, post.model_dump(mode="json"))
    producer.flush()

    bronze_articles = clean_articles(articles)
    bronze_posts = clean_social_posts(posts)
    validate_articles(bronze_articles)
    validate_social_posts(bronze_posts)
    lake.write_jsonl("bronze", "articles_bronze.jsonl", [article.model_dump(mode="json") for article in bronze_articles])
    lake.write_jsonl("bronze", "social_posts_bronze.jsonl", [post.model_dump(mode="json") for post in bronze_posts])

    silver_articles = deduplicate_articles(bronze_articles)
    silver_posts = deduplicate_social_posts(bronze_posts)
    article_sentiment = score_records(
        [(article.article_id or str(article.url), f"{article.headline} {article.summary}") for article in silver_articles]
    )
    social_sentiment = score_records([(post.post_id, post.text) for post in silver_posts])
    lake.write_jsonl("silver", "articles_silver.jsonl", [article.model_dump(mode="json") for article in silver_articles])
    lake.write_jsonl("silver", "social_posts_silver.jsonl", [post.model_dump(mode="json") for post in silver_posts])
    lake.write_json("silver", "article_sentiment.json", article_sentiment)
    lake.write_json("silver", "social_sentiment.json", social_sentiment)

    trends = calculate_trends(silver_articles, silver_posts, article_sentiment, social_sentiment)
    gold = build_gold_metrics(silver_articles, silver_posts, trends, article_sentiment, social_sentiment)
    lake.write_json("gold", "gold_metrics.json", gold)
    lake.write_jsonl("gold", "trend_metrics.jsonl", [trend.model_dump(mode="json") for trend in trends])

    write_sample_data()

    if os.getenv("SKIP_OBJECT_STORE", "false").lower() != "true":
        object_store = MinioObjectStore(settings=settings)
        object_store.ensure_buckets()
        object_store.put_json(settings.minio_bucket_gold, "gold_metrics.json", json.dumps(gold, default=str).encode("utf-8"))

    if os.getenv("SKIP_DB_LOAD", "false").lower() != "true":
        repository = PostgresRepository(settings=settings)
        repository.initialize_schema()
        repository.upsert_articles(silver_articles, article_sentiment)
        repository.upsert_social_posts(silver_posts, social_sentiment)
        repository.upsert_trends(trends)

    if os.getenv("SKIP_GRAPH_LOAD", "false").lower() != "true":
        graph = Neo4jGraphClient(settings=settings)
        build_article_graph(graph, silver_articles[:100])
        build_social_graph(graph, silver_posts[:150])
        graph.close()

    if os.getenv("SKIP_VECTOR_INDEX", "false").lower() != "true":
        model = EmbeddingModel(settings=settings)
        store = QdrantVectorStore(settings=settings)
        index_articles(silver_articles, model=model, store=store)
        index_social_posts(silver_posts, model=model, store=store)

    return {
        "articles": len(silver_articles),
        "social_posts": len(silver_posts),
        "trends": len(trends),
        "published_messages": len(producer.published),
    }


if __name__ == "__main__":
    stats = run_pipeline_once(use_live_sources=os.getenv("USE_LIVE_SOURCES", "true").lower() == "true")
    print(json.dumps(stats, indent=2))
