select
    article_id,
    url,
    headline,
    summary,
    publisher,
    author,
    published_at,
    source_type,
    source_name,
    country,
    language,
    sentiment_score
from {{ source('app', 'articles') }}
