"""Generate a concise, table-free architecture explanation PDF."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "data" / "exports" / "reports"
GRAPH_DIR = REPORT_DIR / "graphs"
GOLD_PATH = PROJECT_ROOT / "data" / "exports" / "gold" / "gold_metrics.json"
OUTPUT_PATH = REPORT_DIR / "apple_news_architecture_brief.pdf"


def load_metrics() -> dict:
    if GOLD_PATH.exists():
        return json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    return {
        "summary": {
            "article_count": "sample fallback",
            "social_post_count": "sample fallback",
            "publisher_count": "sample fallback",
            "topic_count": "sample fallback",
            "average_sentiment": "sample fallback",
        },
        "top_publishers": [],
        "top_products": [],
        "top_hashtags": [],
    }


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def bullet(title: str, text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(f"<b>{title}:</b> {text}", style, bulletText="-")


def section_block(title: str, paragraphs: list[str], styles: dict[str, ParagraphStyle]) -> list:
    story: list = [p(title, styles["section"])]
    for paragraph in paragraphs:
        story.append(p(paragraph, styles["body"]))
        story.append(Spacer(1, 0.07 * inch))
    return story


def top_items(rows: list[dict], label_key: str, value_key: str, limit: int = 5) -> str:
    if not rows:
        return "No current run rows available."
    return "; ".join(f"{row[label_key]} ({row[value_key]})" for row in rows[:limit])


def build_pdf() -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    metrics = load_metrics()
    summary = metrics["summary"]

    sample_styles = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "ReadableTitle",
            parent=sample_styles["Title"],
            alignment=TA_LEFT,
            fontSize=23,
            leading=28,
            textColor=colors.HexColor("#18202a"),
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "ReadableSubtitle",
            parent=sample_styles["BodyText"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#4a5561"),
            spaceAfter=6,
        ),
        "section": ParagraphStyle(
            "ReadableSection",
            parent=sample_styles["Heading2"],
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#2f7d5c"),
            spaceBefore=14,
            spaceAfter=7,
        ),
        "body": ParagraphStyle(
            "ReadableBody",
            parent=sample_styles["BodyText"],
            fontSize=10.2,
            leading=15.5,
            textColor=colors.HexColor("#18202a"),
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "ReadableBullet",
            parent=sample_styles["BodyText"],
            fontSize=10,
            leading=15,
            leftIndent=18,
            firstLineIndent=0,
            bulletIndent=7,
            textColor=colors.HexColor("#18202a"),
            spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "ReadableSmall",
            parent=sample_styles["BodyText"],
            fontSize=8.8,
            leading=12,
            textColor=colors.HexColor("#4a5561"),
            spaceAfter=4,
        ),
    }

    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title="Apple News Intelligence Architecture Brief",
    )

    story: list = [
        p("Apple News Intelligence Platform", styles["title"]),
        p("Short architecture brief: what was chosen, why it was chosen, and how each choice supports the project questions.", styles["subtitle"]),
        p(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["subtitle"]),
        Spacer(1, 0.12 * inch),
        p(
            "This project was built as an end-to-end data engineering platform for Apple-related news and social discussion. "
            "The design starts with compliant public sources, then moves through ingestion, streaming, lakehouse layers, cleaning, graph modeling, vector search, analytics, APIs, dashboards, and PDF outputs.",
            styles["body"],
        ),
        p(
            f"Current generated run: {summary.get('article_count')} articles, {summary.get('social_post_count')} social posts, "
            f"{summary.get('publisher_count')} publishers, {summary.get('topic_count')} topics/products, and average sentiment {summary.get('average_sentiment')}.",
            styles["body"],
        ),
        p("Core Decisions", styles["section"]),
        bullet(
            "News ingestion",
            "GDELT, RSS, Google News RSS, and optional NewsAPI were chosen because they provide legal/public Apple-related headlines, URLs, publishers, timestamps, and source metadata without scraping Apple News.",
            styles["bullet"],
        ),
        bullet(
            "Publisher and location metadata",
            "The article schema keeps publisher, source name, URL, country, language, and published time so the system can answer where a story was printed and which outlets are covering Apple most.",
            styles["bullet"],
        ),
        bullet(
            "Neo4j",
            "Neo4j was chosen for relationship questions: Article PUBLISHED_BY Publisher, Publisher LOCATED_IN Country, Article MENTIONS Product, and SocialPost USES Hashtag.",
            styles["bullet"],
        ),
        bullet(
            "Qdrant vector database",
            "Qdrant was chosen for semantic search and duplicate detection because embeddings can find similar Apple headlines even when the exact wording is different.",
            styles["bullet"],
        ),
        bullet(
            "Social buzz",
            "Reddit and optional X/Twitter API v2 records are modeled separately from news because they include author, platform, text, hashtags, engagement, created time, and sentiment.",
            styles["bullet"],
        ),
        bullet(
            "Dashboard and reports",
            "FastAPI, Next.js, charts, graph visualizations, PNG exports, and PDFs turn the data pipeline into something explainable in a portfolio or presentation.",
            styles["bullet"],
        ),
        PageBreak(),
    ]

    story.extend(
        section_block(
            "Why Neo4j Was Chosen",
            [
                "Neo4j is used because this project asks graph-shaped questions. A regular SQL table can count publishers, but it is less natural for questions like: which Apple products are connected to the same articles, which publishers are associated with which countries, and which social posts mention the same topics?",
                "The graph loader creates Article, Publisher, Author, Product, Person, Company, Country, Topic, SocialPost, Hashtag, and Event nodes. Relationships show how the data connects: Article PUBLISHED_BY Publisher, Article MENTIONS Product, Article RELATED_TO Topic, Publisher LOCATED_IN Country, and SocialPost USES Hashtag.",
                "Constraints are added so important graph entities remain unique. Article URLs, publisher names, product names, topic names, and social post IDs are protected from duplication. This makes repeated pipeline runs safer and easier to explain.",
            ],
            styles,
        )
    )

    graph_path = GRAPH_DIR / "knowledge_graph.png"
    if graph_path.exists():
        story.append(Spacer(1, 0.1 * inch))
        story.append(Image(str(graph_path), width=6.8 * inch, height=4.75 * inch))
        story.append(p("Generated knowledge graph showing article, publisher, and product relationships.", styles["small"]))

    story.extend(
        [
            PageBreak(),
            *section_block(
                "Why a Vector Database Was Chosen",
                [
                    "Qdrant is used because the platform needs semantic search, not only keyword search. For example, 'Apple AI features' and 'Apple Intelligence update' may describe the same topic even if the exact words are not identical.",
                    "The project creates three vector collections: article_embeddings for full article context, headline_embeddings for headline similarity and duplicate detection, and social_post_embeddings for finding related discussion.",
                    "The default embedding path uses local sentence-transformers/all-MiniLM-L6-v2 so the project can work without paid APIs. There is also a deterministic hash fallback for tests and an optional OpenAI embedding path when credentials exist.",
                ],
                styles,
            ),
            p("How this helps the project questions:", styles["body"]),
            bullet("Similar articles", "Find stories that discuss the same Apple product, launch, earnings story, or policy issue.", styles["bullet"]),
            bullet("Near-duplicate headlines", "Group headlines that are phrased differently but likely refer to the same story.", styles["bullet"]),
            bullet("Natural-language search", "Ask questions such as 'What is being said about iPhone supply chain?' and retrieve semantically relevant records.", styles["bullet"]),
        ]
    )

    story.extend(
        [
            PageBreak(),
            *section_block(
                "Apple News, Headlines, and Where It Was Printed",
                [
                    "The news layer keeps the fields needed to explain every headline: URL, headline, summary, publisher, author, source type, source name, country, language, image URL, keywords, and publication time.",
                    "GDELT contributes broad global coverage and source country metadata when available. RSS feeds provide direct publisher-controlled headlines. Google News RSS and optional NewsAPI extend coverage. The sample generator keeps the project runnable when no external API keys are available.",
                    "This design answers: what Apple headlines are trending, who printed them, when they were published, which publishers write the most, and which countries or regions appear in the coverage.",
                ],
                styles,
            ),
            p(f"Top publishers in the current generated data: {top_items(metrics.get('top_publishers', []), 'publisher', 'article_count')}", styles["body"]),
            p(f"Top Apple products/topics in the current generated data: {top_items(metrics.get('top_products', []), 'product', 'mentions')}", styles["body"]),
        ]
    )

    publishers_chart = GRAPH_DIR / "top_publishers.png"
    products_chart = GRAPH_DIR / "top_products.png"
    if publishers_chart.exists():
        story.append(Spacer(1, 0.1 * inch))
        story.append(Image(str(publishers_chart), width=6.75 * inch, height=3.55 * inch))
    if products_chart.exists():
        story.append(Spacer(1, 0.1 * inch))
        story.append(Image(str(products_chart), width=6.75 * inch, height=3.55 * inch))

    story.extend(
        [
            PageBreak(),
            *section_block(
                "Social Media Buzz and Who Is Posting",
                [
                    "Social posts are modeled separately because they behave differently from articles. A social record has a platform, author, post text, URL, creation time, engagement score, hashtags, keywords, and sentiment score.",
                    "Reddit is supported through PRAW when credentials are available, with a public JSON fallback where allowed. X/Twitter is supported only through the official v2 API when a bearer token exists. This keeps the project aligned with the compliance rule.",
                    "The author field is important because it lets the API and dashboard answer who is posting or tweeting about a topic. The engagement score helps compare social buzz against news volume.",
                ],
                styles,
            ),
            p("How social buzz is used:", styles["body"]),
            bullet("Buzz volume", "Counts how many social posts appear around Apple topics over time.", styles["bullet"]),
            bullet("Engagement", "Ranks discussion by likes, comments, replies, repost-like metrics, or sample engagement score.", styles["bullet"]),
            bullet("Hashtags", "Shows which tags are attached to Apple products or events.", styles["bullet"]),
            bullet("Sentiment", "Compares positive or negative social reaction with article volume.", styles["bullet"]),
        ]
    )

    buzz_chart = GRAPH_DIR / "news_social_volume.png"
    sentiment_chart = GRAPH_DIR / "sentiment_timeline.png"
    if buzz_chart.exists():
        story.append(Image(str(buzz_chart), width=6.75 * inch, height=3.45 * inch))
    if sentiment_chart.exists():
        story.append(Spacer(1, 0.1 * inch))
        story.append(Image(str(sentiment_chart), width=6.75 * inch, height=3.45 * inch))

    story.extend(
        [
            PageBreak(),
            *section_block(
                "How the Pipeline Steps Fit Together",
                [
                    "The ingestion layer fetches data from public/legal sources and publishes normalized records to Redpanda topics while also writing raw data to the lakehouse.",
                    "The bronze layer stores normalized records. The silver layer cleans text, validates required fields, removes duplicates, extracts entities, assigns topics, and scores sentiment. The gold layer creates dashboard-ready metrics for headlines, publishers, products, countries, hashtags, social buzz, and sentiment timelines.",
                    "PostgreSQL serves structured analytics. Neo4j serves relationship exploration. Qdrant serves semantic search. FastAPI exposes the results, and the Next.js dashboard plus PDF generators make the project presentation-ready.",
                ],
                styles,
            ),
            p("Main API and output questions covered:", styles["section"]),
            bullet("Latest headlines", "GET /news/latest", styles["bullet"]),
            bullet("Trending news and time series", "GET /news/trending and GET /trends/timeseries", styles["bullet"]),
            bullet("Where stories were printed", "GET /publishers/top plus publisher/country metadata and Publisher LOCATED_IN Country graph relationships.", styles["bullet"]),
            bullet("Product mentions", "GET /products/trending and Article MENTIONS Product graph relationships.", styles["bullet"]),
            bullet("Social buzz and posters", "GET /social/buzz preserves platform, author, text, engagement, and sentiment.", styles["bullet"]),
            bullet("Semantic search", "POST /search/semantic searches vectorized article/headline/social text.", styles["bullet"]),
            bullet("Graph explorer", "GET /graph/product/{product_name} and GET /graph/article/{article_id}.", styles["bullet"]),
            bullet("Presentation outputs", "Generated PDFs and PNG graphs live in data/exports/reports.", styles["bullet"]),
        ]
    )

    trend_chart = GRAPH_DIR / "trend_scores.png"
    if trend_chart.exists():
        story.append(Spacer(1, 0.1 * inch))
        story.append(Image(str(trend_chart), width=6.75 * inch, height=3.55 * inch))

    doc.build(story)
    return OUTPUT_PATH


if __name__ == "__main__":
    print(build_pdf())
