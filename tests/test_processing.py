from scripts.seed_sample_data import build_sample_dataset
from src.processing.clean_articles import clean_articles, clean_text
from src.processing.clean_social_posts import clean_social_posts
from src.processing.data_quality import validate_articles, validate_social_posts
from src.processing.entity_extraction import extract_article_entities
from src.processing.sentiment import score_sentiment
from src.processing.topic_modeling import assign_topics


def test_clean_text_removes_html():
    assert clean_text("<p>Apple&nbsp;Watch</p>") == "Apple Watch"


def test_processing_pipeline_steps_on_samples():
    articles, posts = build_sample_dataset()
    cleaned_articles = clean_articles(articles[:5])
    cleaned_posts = clean_social_posts(posts[:5])
    validate_articles(cleaned_articles)
    validate_social_posts(cleaned_posts)
    entities = extract_article_entities(cleaned_articles[0])
    assert any(entity.entity_type == "Company" for entity in entities)
    assert -1 <= score_sentiment(cleaned_articles[0].summary) <= 1
    assert assign_topics(cleaned_articles[0].headline)
