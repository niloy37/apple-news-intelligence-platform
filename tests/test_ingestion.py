from scripts.seed_sample_data import build_sample_dataset
from src.ingestion.gdelt_client import GdeltClient
from src.schemas import ArticleRecord, SocialPostRecord


def test_gdelt_query_contains_apple_keywords():
    query = GdeltClient().build_query()
    assert "Apple" in query
    assert "iPhone" in query


def test_sample_records_validate_against_contracts():
    articles, posts = build_sample_dataset()
    assert len(articles) == 100
    assert len(posts) == 300
    assert isinstance(articles[0], ArticleRecord)
    assert isinstance(posts[0], SocialPostRecord)
    assert articles[0].article_id
