"""Load cleaned articles and extracted entities into Neo4j."""

from __future__ import annotations

from src.graph.neo4j_client import Neo4jGraphClient
from src.processing.entity_extraction import extract_article_entities
from src.processing.topic_modeling import assign_topics
from src.schemas import ArticleRecord


ARTICLE_GRAPH_CYPHER = """
MERGE (a:Article {article_id: $article_id})
SET a.url = $url,
    a.headline = $headline,
    a.summary = $summary,
    a.published_at = datetime($published_at),
    a.language = $language
MERGE (p:Publisher {name: $publisher})
MERGE (a)-[:PUBLISHED_BY]->(p)
FOREACH (authorName IN CASE WHEN $author IS NULL OR $author = '' THEN [] ELSE [$author] END |
    MERGE (au:Author {name: authorName})
    MERGE (a)-[:WRITTEN_BY]->(au)
)
FOREACH (countryName IN CASE WHEN $country IS NULL OR $country = '' THEN [] ELSE [$country] END |
    MERGE (c:Country {name: countryName})
    MERGE (p)-[:LOCATED_IN]->(c)
)
"""

TOPIC_CYPHER = """
MATCH (a:Article {article_id: $article_id})
MERGE (t:Topic {name: $topic})
MERGE (a)-[:RELATED_TO]->(t)
"""

ENTITY_LABELS = {
    "Product": "Product",
    "Person": "Person",
    "Company": "Company",
    "Country": "Country",
    "Event": "Event",
    "Topic": "Topic",
}


def build_article_graph(client: Neo4jGraphClient, articles: list[ArticleRecord]) -> None:
    client.ensure_constraints()
    for article in articles:
        client.run(
            ARTICLE_GRAPH_CYPHER,
            {
                "article_id": article.article_id,
                "url": str(article.url),
                "headline": article.headline,
                "summary": article.summary,
                "published_at": article.published_at.isoformat(),
                "language": article.language,
                "publisher": article.publisher,
                "author": article.author,
                "country": article.country,
            },
        )
        for entity in extract_article_entities(article):
            label = ENTITY_LABELS.get(entity.entity_type, "Topic")
            client.run(
                f"""
                MATCH (a:Article {{article_id: $source_id}})
                MERGE (e:{label} {{name: $entity_text}})
                MERGE (a)-[:MENTIONS]->(e)
                """,
                {
                    "source_id": entity.source_id,
                    "entity_text": entity.entity_text,
                },
            )
        for topic in assign_topics(f"{article.headline} {article.summary}"):
            client.run(TOPIC_CYPHER, {"article_id": article.article_id, "topic": topic})


def article_graph_payload(article: ArticleRecord) -> dict[str, object]:
    """Return a graph-shaped payload for API tests and offline demos."""

    entities = extract_article_entities(article)
    return {
        "nodes": [
            {"id": article.article_id, "label": "Article", "name": article.headline},
            {"id": article.publisher, "label": "Publisher", "name": article.publisher},
            *[
                {"id": entity.entity_id, "label": entity.entity_type, "name": entity.entity_text}
                for entity in entities
            ],
        ],
        "edges": [
            {"source": article.article_id, "target": article.publisher, "type": "PUBLISHED_BY"},
            *[
                {"source": article.article_id, "target": entity.entity_id, "type": "MENTIONS"}
                for entity in entities
            ],
        ],
    }
