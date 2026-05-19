CREATE TABLE IF NOT EXISTS ingestion_runs (
    run_id UUID PRIMARY KEY,
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    status TEXT NOT NULL,
    records_ingested INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS publishers (
    publisher_id UUID PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    country TEXT,
    domain TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS authors (
    author_id UUID PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS articles (
    article_id UUID PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    headline TEXT NOT NULL,
    summary TEXT,
    body TEXT,
    publisher TEXT NOT NULL,
    author TEXT,
    published_at TIMESTAMPTZ NOT NULL,
    source_type TEXT NOT NULL,
    source_name TEXT NOT NULL,
    country TEXT,
    language TEXT DEFAULT 'en',
    image_url TEXT,
    sentiment_score NUMERIC,
    duplicate_group_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS article_entities (
    entity_id UUID PRIMARY KEY,
    article_id UUID REFERENCES articles(article_id) ON DELETE CASCADE,
    entity_text TEXT NOT NULL,
    entity_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS article_topics (
    article_id UUID REFERENCES articles(article_id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    score NUMERIC NOT NULL DEFAULT 1.0,
    PRIMARY KEY(article_id, topic)
);

CREATE TABLE IF NOT EXISTS social_posts (
    post_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    text TEXT NOT NULL,
    author TEXT,
    url TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    engagement_score NUMERIC NOT NULL DEFAULT 0,
    sentiment_score NUMERIC,
    created_record_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS social_engagement (
    post_id TEXT REFERENCES social_posts(post_id) ON DELETE CASCADE,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(post_id, metric_name, observed_at)
);

CREATE TABLE IF NOT EXISTS sentiment_scores (
    source_id TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    sentiment_score NUMERIC NOT NULL CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    model_name TEXT NOT NULL,
    scored_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(source_id, source_kind, model_name)
);

CREATE TABLE IF NOT EXISTS trend_metrics (
    metric_date TIMESTAMPTZ NOT NULL,
    topic TEXT NOT NULL,
    product TEXT NOT NULL DEFAULT '',
    article_volume INTEGER NOT NULL DEFAULT 0,
    social_volume INTEGER NOT NULL DEFAULT 0,
    engagement_score NUMERIC NOT NULL DEFAULT 0,
    average_sentiment NUMERIC NOT NULL DEFAULT 0,
    recency_score NUMERIC NOT NULL DEFAULT 0,
    trend_score NUMERIC NOT NULL DEFAULT 0,
    PRIMARY KEY(metric_date, topic, product)
);

CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_publisher ON articles(publisher);
CREATE INDEX IF NOT EXISTS idx_social_posts_created_at ON social_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_trend_metrics_score ON trend_metrics(trend_score DESC);
