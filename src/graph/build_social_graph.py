"""Load social posts and hashtags into Neo4j."""

from __future__ import annotations

from src.graph.neo4j_client import Neo4jGraphClient
from src.processing.entity_extraction import extract_social_entities
from src.schemas import SocialPostRecord


SOCIAL_GRAPH_CYPHER = """
MERGE (s:SocialPost {post_id: $post_id})
SET s.platform = $platform,
    s.text = $text,
    s.author = $author,
    s.url = $url,
    s.created_at = datetime($created_at),
    s.engagement_score = $engagement_score
"""

HASHTAG_CYPHER = """
MATCH (s:SocialPost {post_id: $post_id})
MERGE (h:Hashtag {name: $hashtag})
MERGE (s)-[:USES]->(h)
"""

SOCIAL_ENTITY_CYPHER = """
MATCH (s:SocialPost {post_id: $source_id})
MERGE (e:Topic {name: $entity_text})
MERGE (s)-[:MENTIONS]->(e)
"""


def build_social_graph(client: Neo4jGraphClient, posts: list[SocialPostRecord]) -> None:
    client.ensure_constraints()
    for post in posts:
        client.run(
            SOCIAL_GRAPH_CYPHER,
            {
                "post_id": post.post_id,
                "platform": post.platform,
                "text": post.text,
                "author": post.author,
                "url": post.url,
                "created_at": post.created_at.isoformat(),
                "engagement_score": post.engagement_score,
            },
        )
        for hashtag in post.hashtags:
            client.run(HASHTAG_CYPHER, {"post_id": post.post_id, "hashtag": hashtag})
        for entity in extract_social_entities(post):
            client.run(
                SOCIAL_ENTITY_CYPHER,
                {"source_id": entity.source_id, "entity_text": entity.entity_text},
            )
