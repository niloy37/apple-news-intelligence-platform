// Top publishers covering Apple
MATCH (a:Article)-[:PUBLISHED_BY]->(p:Publisher)
RETURN p.name AS publisher, count(a) AS article_count
ORDER BY article_count DESC
LIMIT 10;

// Most mentioned Apple products
MATCH (a:Article)-[:MENTIONS]->(p:Product)
RETURN p.name AS product, count(a) AS mentions
ORDER BY mentions DESC
LIMIT 10;

// Articles connected to the same product
MATCH (p:Product {name: $product_name})<-[:MENTIONS]-(a:Article)
RETURN a.headline AS headline, a.url AS url, a.published_at AS published_at
ORDER BY published_at DESC
LIMIT 25;

// Social posts connected to topics
MATCH (s:SocialPost)-[:MENTIONS]->(t:Topic)
RETURN t.name AS topic, count(s) AS post_count, avg(s.engagement_score) AS average_engagement
ORDER BY post_count DESC
LIMIT 15;

// Countries where Apple news is being published
MATCH (a:Article)-[:PUBLISHED_BY]->(p:Publisher)-[:LOCATED_IN]->(c:Country)
RETURN c.name AS country, count(a) AS article_count
ORDER BY article_count DESC;

// Topic clusters around Apple
MATCH (a:Article)-[:RELATED_TO]->(t:Topic)
WITH a, collect(t.name) AS topics
UNWIND topics AS topic_a
UNWIND topics AS topic_b
WITH topic_a, topic_b, count(*) AS overlap
WHERE topic_a < topic_b AND overlap > 1
MERGE (ta:Topic {name: topic_a})
MERGE (tb:Topic {name: topic_b})
MERGE (ta)-[r:TRENDING_WITH]->(tb)
SET r.overlap = overlap
RETURN topic_a, topic_b, overlap
ORDER BY overlap DESC
LIMIT 25;
