"""Neo4j constraints and indexes for the Apple news graph."""

CONSTRAINTS = [
    "CREATE CONSTRAINT article_url_unique IF NOT EXISTS FOR (a:Article) REQUIRE a.url IS UNIQUE",
    "CREATE CONSTRAINT article_id_unique IF NOT EXISTS FOR (a:Article) REQUIRE a.article_id IS UNIQUE",
    "CREATE CONSTRAINT publisher_name_unique IF NOT EXISTS FOR (p:Publisher) REQUIRE p.name IS UNIQUE",
    "CREATE CONSTRAINT author_name_unique IF NOT EXISTS FOR (a:Author) REQUIRE a.name IS UNIQUE",
    "CREATE CONSTRAINT product_name_unique IF NOT EXISTS FOR (p:Product) REQUIRE p.name IS UNIQUE",
    "CREATE CONSTRAINT person_name_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",
    "CREATE CONSTRAINT company_name_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",
    "CREATE CONSTRAINT topic_name_unique IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE",
    "CREATE CONSTRAINT country_name_unique IF NOT EXISTS FOR (c:Country) REQUIRE c.name IS UNIQUE",
    "CREATE CONSTRAINT social_post_id_unique IF NOT EXISTS FOR (s:SocialPost) REQUIRE s.post_id IS UNIQUE",
    "CREATE CONSTRAINT hashtag_name_unique IF NOT EXISTS FOR (h:Hashtag) REQUIRE h.name IS UNIQUE",
    "CREATE INDEX article_published_at IF NOT EXISTS FOR (a:Article) ON (a.published_at)",
    "CREATE INDEX social_created_at IF NOT EXISTS FOR (s:SocialPost) ON (s.created_at)",
]


def constraints_as_text() -> str:
    return ";\n".join(CONSTRAINTS) + ";"
