"""Read API data from Postgres exports with sample fallback."""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from scripts.seed_sample_data import build_sample_dataset
from src.analytics.gold_builder import build_gold_metrics
from src.graph.build_article_graph import article_graph_payload
from src.processing.sentiment import score_records
from src.processing.trend_calculator import calculate_trends
from src.schemas import SemanticSearchRequest


class DashboardRepository:
    def __init__(self) -> None:
        self.project_root = PROJECT_ROOT
        self.gold_path = self.project_root / "data" / "exports" / "gold" / "gold_metrics.json"

    @lru_cache(maxsize=1)
    def get_gold_metrics(self) -> dict[str, Any]:
        if self.gold_path.exists():
            return json.loads(self.gold_path.read_text(encoding="utf-8"))

        articles, posts = build_sample_dataset()
        article_sentiment = score_records(
            [(article.article_id or str(article.url), f"{article.headline} {article.summary}") for article in articles]
        )
        social_sentiment = score_records([(post.post_id, post.text) for post in posts])
        trends = calculate_trends(articles, posts, article_sentiment, social_sentiment)
        return build_gold_metrics(articles, posts, trends, article_sentiment, social_sentiment)

    def latest_news(self, limit: int = 25) -> list[dict[str, Any]]:
        return self.get_gold_metrics()["latest_headlines"][:limit]

    def trending_news(self, limit: int = 15) -> list[dict[str, Any]]:
        headlines = self.get_gold_metrics()["latest_headlines"]
        return sorted(headlines, key=lambda item: item.get("sentiment_score", 0), reverse=True)[:limit]

    def top_publishers(self, limit: int = 15) -> list[dict[str, Any]]:
        return self.get_gold_metrics()["top_publishers"][:limit]

    def trending_products(self, limit: int = 15) -> list[dict[str, Any]]:
        return self.get_gold_metrics()["top_products"][:limit]

    def social_buzz(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.get_gold_metrics()["social_buzz"][:limit]

    def sentiment_timeline(self) -> list[dict[str, Any]]:
        return [
            {"timestamp": row["timestamp"], "average_sentiment": row["average_sentiment"]}
            for row in self.get_gold_metrics()["timeseries"]
        ]

    def trend_timeseries(self) -> list[dict[str, Any]]:
        return self.get_gold_metrics()["timeseries"]

    def semantic_search(self, request: SemanticSearchRequest) -> list[dict[str, Any]]:
        query_terms = {term.lower() for term in request.query.split() if len(term) > 2}
        candidates = self.get_gold_metrics()["latest_headlines"]
        scored: list[dict[str, Any]] = []
        for candidate in candidates:
            text = f"{candidate['headline']} {candidate.get('summary', '')}".lower()
            overlap = sum(1 for term in query_terms if term in text)
            if overlap or request.query.lower() in text:
                scored.append({"score": overlap / max(len(query_terms), 1), "payload": candidate})
        if not scored:
            scored = [{"score": 0.0, "payload": item} for item in candidates[: request.limit]]
        return sorted(scored, key=lambda item: item["score"], reverse=True)[: request.limit]

    def product_graph(self, product_name: str) -> dict[str, Any]:
        metrics = self.get_gold_metrics()
        nodes = [{"id": product_name, "label": "Product", "name": product_name}]
        edges = []
        for article in metrics["latest_headlines"]:
            text = f"{article['headline']} {article.get('summary', '')}".lower()
            if product_name.lower() in text:
                nodes.append({"id": article["article_id"], "label": "Article", "name": article["headline"]})
                nodes.append({"id": article["publisher"], "label": "Publisher", "name": article["publisher"]})
                edges.append({"source": article["article_id"], "target": product_name, "type": "MENTIONS"})
                edges.append({"source": article["article_id"], "target": article["publisher"], "type": "PUBLISHED_BY"})
        return {"nodes": nodes, "edges": edges}

    def article_graph(self, article_id: str) -> dict[str, Any]:
        articles, _ = build_sample_dataset()
        for article in articles:
            if article.article_id == article_id:
                return article_graph_payload(article)
        metrics = self.get_gold_metrics()
        for article in metrics["latest_headlines"]:
            if article["article_id"] == article_id:
                return {
                    "nodes": [
                        {"id": article_id, "label": "Article", "name": article["headline"]},
                        {"id": article["publisher"], "label": "Publisher", "name": article["publisher"]},
                    ],
                    "edges": [{"source": article_id, "target": article["publisher"], "type": "PUBLISHED_BY"}],
                }
        return {"nodes": [], "edges": []}


repository = DashboardRepository()
