from scripts.seed_sample_data import build_sample_dataset
from src.processing.deduplicate import deduplicate_articles, deduplicate_social_posts


def test_article_deduplication_removes_duplicate_url():
    articles, _ = build_sample_dataset()
    duplicated = [articles[0], articles[0], articles[1]]
    assert len(deduplicate_articles(duplicated)) == 2


def test_social_deduplication_removes_duplicate_id():
    _, posts = build_sample_dataset()
    duplicated = [posts[0], posts[0], posts[1]]
    assert len(deduplicate_social_posts(duplicated)) == 2
