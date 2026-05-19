select
    date_trunc('day', published_at) as metric_date,
    publisher,
    country,
    count(*) as article_count,
    avg(sentiment_score) as average_sentiment
from {{ ref('bronze_articles') }}
group by 1, 2, 3
