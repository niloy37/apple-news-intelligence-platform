# Architecture Notes

## Objective

The platform answers Apple-related intelligence questions across news volume, publisher behavior, product mentions, social buzz, sentiment, semantic similarity, near duplicates, and graph relationships.

## Source Layer

Connectors live in `src/ingestion/`:

- `gdelt_client.py`: public GDELT DOC API
- `rss_client.py`: technology and business publisher RSS feeds
- `reddit_client.py`: PRAW when credentials exist, public Reddit JSON fallback when allowed
- `twitter_client.py`: X API v2 only with bearer token
- `scraper_client.py`: robots-aware optional public page fetcher
- `producer.py`: Redpanda/Kafka publishing with local fallback

## Lakehouse Layers

Raw:

- Original source payloads and normalized messages
- Stored in MinIO raw buckets and local `data/exports/raw/`

Bronze:

- Schema-valid article and social records
- Cleaned text and normalized timestamps

Silver:

- Deduplicated articles and posts
- Entity extraction
- Sentiment scores
- Topic assignment

Gold:

- Publisher rankings
- Product mentions
- Trend metrics
- News/social/sentiment time series
- Dashboard-ready JSON and PostgreSQL tables

## Orchestration

Airflow DAGs wrap the same executable pipeline used locally:

- `scripts/run_pipeline_once.py`
- `scripts/init_neo4j.py`
- `scripts/init_qdrant.py`

This keeps local development and scheduled orchestration aligned.

## Data Quality

Implemented in `src/processing/data_quality.py` and dbt tests:

- Article URL cannot be null
- Headline cannot be empty
- Publication date must be valid
- Duplicate URL is rejected
- Source name must exist
- Sentiment score must be between `-1` and `1`

## Graph Design

Graph entities:

- `Article`
- `Publisher`
- `Author`
- `Topic`
- `Product`
- `Person`
- `Company`
- `Country`
- `SocialPost`
- `Hashtag`
- `Event`

Graph relationships:

- `Article PUBLISHED_BY Publisher`
- `Article WRITTEN_BY Author`
- `Article MENTIONS Product`
- `Article MENTIONS Person`
- `Article MENTIONS Company`
- `Article RELATED_TO Topic`
- `Publisher LOCATED_IN Country`
- `SocialPost DISCUSSES Article`
- `SocialPost MENTIONS Product`
- `SocialPost USES Hashtag`
- `Person ASSOCIATED_WITH Company`
- `Topic TRENDING_WITH Topic`

Constraints and sample queries are in `src/graph/`.

## Vector Search

Vector modules live in `src/vector/`.

Default local embedding model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Fallback:

- Deterministic hash embeddings for offline tests and demos

Optional:

- OpenAI embeddings when `EMBEDDING_PROVIDER=openai` and `OPENAI_API_KEY` is set

Qdrant collections:

- `article_embeddings`
- `headline_embeddings`
- `social_post_embeddings`

Capabilities:

- Similar article search
- Natural language article search
- Near-duplicate headline detection
- Social post semantic search

## Streaming Design

Redpanda topics:

- `news.raw`
- `social.raw`
- `news.bronze`
- `social.bronze`
- `news.silver`
- `social.silver`
- `trend.metrics`

The local `EventProducer` publishes to Kafka when Redpanda is available and stores an in-memory buffer otherwise.

## Monitoring

Monitoring includes:

- FastAPI `/health`
- FastAPI Prometheus `/metrics`
- Docker health checks
- Airflow task state
- Grafana dashboard provisioning
- Redpanda and Qdrant metric scrape targets

## Presentation Narrative

1. Show compliant source ingestion and sample fallback.
2. Explain raw, bronze, silver, gold lakehouse flow.
3. Show how Postgres, Neo4j, and Qdrant each serve a different access pattern.
4. Demonstrate FastAPI endpoints.
5. Open the dashboard and walk through trends, social buzz, semantic search, and graph explorer.
6. Discuss how the same architecture maps to AWS, GCP, or Azure.
