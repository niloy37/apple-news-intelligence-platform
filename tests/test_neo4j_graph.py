from scripts.seed_sample_data import build_sample_dataset
from src.graph.build_article_graph import article_graph_payload
from src.graph.cypher_constraints import constraints_as_text


def test_constraints_include_required_unique_keys():
    constraints = constraints_as_text()
    assert "Article" in constraints
    assert "Publisher" in constraints
    assert "SocialPost" in constraints


def test_article_graph_payload_contains_nodes_and_edges():
    articles, _ = build_sample_dataset()
    payload = article_graph_payload(articles[0])
    assert payload["nodes"]
    assert payload["edges"]
    assert any(edge["type"] == "PUBLISHED_BY" for edge in payload["edges"])
