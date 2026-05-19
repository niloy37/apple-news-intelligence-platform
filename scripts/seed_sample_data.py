"""Generate deterministic sample data for local demos and tests."""

from __future__ import annotations

import json
import random
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.config import get_settings
from src.schemas import ArticleRecord, SocialPostRecord

PUBLISHERS = [
    ("The Verge", "United States", "theverge.com"),
    ("Bloomberg Technology", "United States", "bloomberg.com"),
    ("Reuters Tech", "United Kingdom", "reuters.com"),
    ("CNBC Tech", "United States", "cnbc.com"),
    ("MacRumors", "United States", "macrumors.com"),
    ("9to5Mac", "United States", "9to5mac.com"),
    ("TechCrunch", "United States", "techcrunch.com"),
    ("Engadget", "United States", "engadget.com"),
    ("Financial Times Tech", "United Kingdom", "ft.com"),
    ("Nikkei Asia Tech", "Japan", "asia.nikkei.com"),
    ("The Information", "United States", "theinformation.com"),
    ("Wall Street Journal Tech", "United States", "wsj.com"),
    ("Wired", "United States", "wired.com"),
    ("Ars Technica", "United States", "arstechnica.com"),
    ("ZDNet", "United States", "zdnet.com"),
    ("CNET", "United States", "cnet.com"),
    ("The Guardian Tech", "United Kingdom", "theguardian.com"),
    ("India Today Tech", "India", "indiatoday.in"),
    ("South China Morning Post Tech", "China", "scmp.com"),
    ("Heise Online", "Germany", "heise.de"),
]

PRODUCTS_TOPICS = [
    "Apple",
    "iPhone",
    "iPhone 17",
    "MacBook",
    "iPad",
    "Apple Watch",
    "Vision Pro",
    "iOS",
    "macOS",
    "App Store",
    "Tim Cook",
    "Apple Intelligence",
    "Apple chip",
    "M-series chip",
    "Apple earnings",
    "Apple supply chain",
]

HEADLINE_TEMPLATES = [
    "{product} demand rises as analysts track Apple's next launch window",
    "Apple suppliers prepare for {product} production shift",
    "Developers react to Apple's latest {product} roadmap",
    "Tim Cook highlights {product} strategy during investor briefing",
    "Regulators examine Apple policy changes around {product}",
    "Apple Intelligence update sparks new debate about {product}",
    "{product} rumors accelerate ahead of Apple's fall event",
    "Apple earnings preview points to stronger {product} momentum",
    "New supply chain report links Apple chip plans to {product}",
    "Customers compare {product} upgrades after early reviews",
]

SOCIAL_TEMPLATES = [
    "People are talking about {product} again after today's Apple headlines #{tag}",
    "The {product} rumor cycle is wild, but the supply chain signal looks strong #{tag}",
    "Apple fans seem split on {product}; sentiment is not as simple as the headlines suggest #{tag}",
    "If {product} gets this upgrade, social buzz will explode #{tag}",
    "Developers are watching the {product} story closely after the latest Apple update #{tag}",
    "The market reaction to {product} news feels surprisingly optimistic #{tag}",
    "Some users still worry about bugs and delays around {product} #{tag}",
    "Apple's {product} strategy keeps showing up across tech communities #{tag}",
]

AUTHORS = [
    "Avery Stone",
    "Maya Chen",
    "Jordan Ellis",
    "Priya Raman",
    "Noah Park",
    "Elena Rossi",
    "Marcus Reed",
    "Sofia Patel",
]


def build_sample_dataset(seed: int = 42) -> tuple[list[ArticleRecord], list[SocialPostRecord]]:
    random.seed(seed)
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    articles: list[ArticleRecord] = []
    social_posts: list[SocialPostRecord] = []

    for index in range(100):
        publisher, country, domain = PUBLISHERS[index % len(PUBLISHERS)]
        product = PRODUCTS_TOPICS[index % len(PRODUCTS_TOPICS)]
        headline = HEADLINE_TEMPLATES[index % len(HEADLINE_TEMPLATES)].format(product=product)
        published_at = now - timedelta(hours=random.randint(0, 120), minutes=random.randint(0, 55))
        tone = "strong growth and optimistic demand" if index % 3 else "risk, delays, and regulatory concern"
        url = f"https://{domain}/apple-news-intelligence/sample-{index:03d}"
        article = ArticleRecord(
            url=url,
            headline=headline,
            summary=(
                f"{publisher} reports that {product} is shaping Apple coverage across markets. "
                f"The story mentions {tone}."
            ),
            body=(
                f"Apple, Tim Cook, and partners such as TSMC and Foxconn are connected to this {product} story. "
                f"Analysts are watching App Store, iOS, and Apple Intelligence signals."
            ),
            publisher=publisher,
            author=random.choice(AUTHORS),
            published_at=published_at,
            source_type="sample",
            source_name="sample-generator",
            country=country,
            language="en",
            keywords=[product, "Apple"],
            raw={"sample_index": index},
        )
        articles.append(article)

    for index in range(300):
        product = PRODUCTS_TOPICS[index % len(PRODUCTS_TOPICS)]
        tag = product.replace(" ", "")
        created_at = now - timedelta(hours=random.randint(0, 96), minutes=random.randint(0, 55))
        text = SOCIAL_TEMPLATES[index % len(SOCIAL_TEMPLATES)].format(product=product, tag=tag)
        social_posts.append(
            SocialPostRecord(
                post_id=f"sample-social-{index:03d}",
                platform="sample",
                text=text,
                author=f"apple_watcher_{index % 37}",
                url=f"https://social.example.com/posts/{index:03d}",
                created_at=created_at,
                engagement_score=float(random.randint(1, 1200)),
                hashtags=[tag],
                keywords=[product, "Apple"],
                raw={"sample_index": index},
            )
        )

    return articles, social_posts


def write_sample_data() -> None:
    settings = get_settings()
    settings.sample_dir.mkdir(parents=True, exist_ok=True)
    articles, posts = build_sample_dataset()
    files = {
        "articles_sample.json": [article.model_dump(mode="json") for article in articles],
        "social_posts_sample.json": [post.model_dump(mode="json") for post in posts],
        "publishers_sample.json": [
            {"name": name, "country": country, "domain": domain} for name, country, domain in PUBLISHERS
        ],
        "products_topics_sample.json": PRODUCTS_TOPICS,
    }
    for name, payload in files.items():
        (settings.sample_dir / name).write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"Wrote sample data to {settings.sample_dir}")


if __name__ == "__main__":
    write_sample_data()
