select
    publisher,
    sum(article_count) as article_count,
    avg(average_sentiment) as average_sentiment,
    dense_rank() over (order by sum(article_count) desc) as publisher_rank
from {{ ref('silver_article_daily') }}
group by 1
