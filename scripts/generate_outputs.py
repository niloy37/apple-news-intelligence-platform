"""Generate portfolio-ready PDF and graph/chart outputs."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import networkx as nx
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUTPUT_DIR = PROJECT_ROOT / "data" / "exports" / "reports"
GRAPH_DIR = OUTPUT_DIR / "graphs"
GOLD_PATH = PROJECT_ROOT / "data" / "exports" / "gold" / "gold_metrics.json"


def load_metrics() -> dict:
    if not GOLD_PATH.exists():
        raise FileNotFoundError(f"Gold metrics not found: {GOLD_PATH}")
    return json.loads(GOLD_PATH.read_text(encoding="utf-8"))


def save_bar_chart(rows: list[dict], label_key: str, value_key: str, title: str, path: Path, color: str) -> Path:
    rows = rows[:10]
    labels = [str(row[label_key]) for row in rows]
    values = [float(row[value_key]) for row in rows]
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(labels[::-1], values[::-1], color=color)
    ax.set_title(title, fontsize=16, weight="bold")
    ax.set_xlabel(value_key.replace("_", " ").title())
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def save_timeseries(metrics: dict, path: Path) -> Path:
    rows = sorted(metrics["timeseries"], key=lambda row: row["timestamp"])
    labels = [datetime.fromisoformat(row["timestamp"]).strftime("%m-%d %H:%M") for row in rows]
    article_values = [row["article_volume"] for row in rows]
    social_values = [row["social_volume"] for row in rows]
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(labels, article_values, color="#1d6f99", label="Article volume", linewidth=2)
    ax.plot(labels, social_values, color="#2f7d5c", label="Social volume", linewidth=2)
    ax.fill_between(labels, article_values, alpha=0.12, color="#1d6f99")
    ax.fill_between(labels, social_values, alpha=0.12, color="#2f7d5c")
    ax.set_title("News Volume vs Social Buzz", fontsize=16, weight="bold")
    ax.set_ylabel("Records per hour")
    ax.tick_params(axis="x", labelrotation=60)
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def save_sentiment(metrics: dict, path: Path) -> Path:
    rows = sorted(metrics["timeseries"], key=lambda row: row["timestamp"])
    labels = [datetime.fromisoformat(row["timestamp"]).strftime("%m-%d %H:%M") for row in rows]
    values = [row["average_sentiment"] for row in rows]
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(labels, values, color="#b0445a", linewidth=2)
    ax.axhline(0, color="#18202a", linewidth=1, alpha=0.5)
    ax.set_ylim(-1, 1)
    ax.set_title("Average Sentiment Timeline", fontsize=16, weight="bold")
    ax.set_ylabel("Sentiment score")
    ax.tick_params(axis="x", labelrotation=60)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def save_trend_chart(metrics: dict, path: Path) -> Path:
    rows = metrics["trends"][:10]
    labels = [row["topic"] for row in rows]
    values = [row["trend_score"] for row in rows]
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(labels, values, color="#2f7d5c")
    ax.set_title("Top Trending Apple Topics", fontsize=16, weight="bold")
    ax.set_ylabel("Trend score")
    ax.tick_params(axis="x", labelrotation=45)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def save_graph(metrics: dict, path: Path) -> Path:
    graph = nx.Graph()
    for article in metrics["latest_headlines"][:18]:
        article_id = article["article_id"]
        graph.add_node(article_id, label=article["headline"][:42], kind="Article")
        graph.add_node(article["publisher"], label=article["publisher"], kind="Publisher")
        graph.add_edge(article_id, article["publisher"], relation="PUBLISHED_BY")
        text = f"{article['headline']} {article.get('summary', '')}".lower()
        for product in [row["product"] for row in metrics["top_products"][:8]]:
            if product and product.lower() in text:
                graph.add_node(product, label=product, kind="Product")
                graph.add_edge(article_id, product, relation="MENTIONS")

    colors_by_kind = {"Article": "#1d6f99", "Publisher": "#b7791f", "Product": "#2f7d5c"}
    node_colors = [colors_by_kind.get(graph.nodes[node].get("kind"), "#9aa79b") for node in graph.nodes]
    sizes = [900 if graph.nodes[node].get("kind") != "Article" else 450 for node in graph.nodes]
    pos = nx.spring_layout(graph, seed=7, k=0.8)

    fig, ax = plt.subplots(figsize=(14, 10))
    nx.draw_networkx_edges(graph, pos, ax=ax, edge_color="#9aa79b", alpha=0.45)
    nx.draw_networkx_nodes(graph, pos, ax=ax, node_color=node_colors, node_size=sizes, linewidths=1, edgecolors="white")
    labels = {node: graph.nodes[node].get("label", str(node)) for node in graph.nodes}
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8, ax=ax)
    ax.set_title("Article, Publisher, and Product Knowledge Graph", fontsize=16, weight="bold")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def table_from_rows(rows: list[dict], columns: list[tuple[str, str]], max_rows: int = 8) -> Table:
    data = [[title for title, _ in columns]]
    for row in rows[:max_rows]:
        data.append([str(row.get(key, ""))[:70] for _, key in columns])
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#18202a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d8dfd8")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8faf7")]),
            ]
        )
    )
    return table


def build_pdf(metrics: dict, images: dict[str, Path], pdf_path: Path) -> Path:
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "PortfolioTitle",
        parent=styles["Title"],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#18202a"),
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#2f7d5c"),
        spaceBefore=12,
    )
    body_style = styles["BodyText"]

    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=0.55 * inch, leftMargin=0.55 * inch)
    story = [
        Paragraph("Apple News Intelligence Platform", title_style),
        Paragraph("Portfolio Data Engineering Report", styles["Heading2"]),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style),
        Spacer(1, 0.2 * inch),
        Paragraph(
            "This report summarizes the Docker-backed local run of the Apple news intelligence platform: "
            "sample-safe ingestion, lakehouse processing, graph-ready entities, vector-search indexing, "
            "and dashboard-ready gold analytics.",
            body_style,
        ),
        Spacer(1, 0.25 * inch),
    ]

    summary = metrics["summary"]
    summary_data = [
        ["Metric", "Value"],
        ["Articles", summary["article_count"]],
        ["Social Posts", summary["social_post_count"]],
        ["Publishers", summary["publisher_count"]],
        ["Topics", summary["topic_count"]],
        ["Average Sentiment", summary["average_sentiment"]],
    ]
    summary_table = Table(summary_data, hAlign="LEFT")
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#18202a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#d8dfd8")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8faf7")]),
            ]
        )
    )
    story.extend([Paragraph("Run Summary", section_style), summary_table, PageBreak()])

    for title, key in [
        ("News Volume vs Social Buzz", "timeseries"),
        ("Average Sentiment Timeline", "sentiment"),
        ("Top Publishers", "publishers"),
        ("Top Products", "products"),
        ("Top Trending Topics", "trends"),
        ("Knowledge Graph", "graph"),
    ]:
        story.append(Paragraph(title, section_style))
        story.append(Image(str(images[key]), width=7.1 * inch, height=3.85 * inch if key != "graph" else 5.0 * inch))
        story.append(Spacer(1, 0.18 * inch))
        if key in {"sentiment", "products", "graph"}:
            story.append(PageBreak())

    story.append(Paragraph("Top Headlines", section_style))
    story.append(
        table_from_rows(
            metrics["latest_headlines"],
            [("Headline", "headline"), ("Publisher", "publisher"), ("Sentiment", "sentiment_score")],
            max_rows=10,
        )
    )
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("Top Social Buzz", section_style))
    story.append(
        table_from_rows(
            metrics["social_buzz"],
            [("Text", "text"), ("Platform", "platform"), ("Engagement", "engagement_score")],
            max_rows=10,
        )
    )

    doc.build(story)
    return pdf_path


def build_graph_appendix_pdf(images: dict[str, Path], pdf_path: Path) -> Path:
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=0.45 * inch, leftMargin=0.45 * inch)
    titles = {
        "timeseries": "News Volume vs Social Buzz",
        "sentiment": "Average Sentiment Timeline",
        "publishers": "Top Publishers",
        "products": "Top Products",
        "trends": "Top Trending Topics",
        "graph": "Knowledge Graph",
    }
    story = [Paragraph("Apple News Intelligence Graph Appendix", styles["Title"]), Spacer(1, 0.2 * inch)]
    for index, key in enumerate(["timeseries", "sentiment", "publishers", "products", "trends", "graph"]):
        if index:
            story.append(PageBreak())
        story.append(Paragraph(titles[key], styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Image(str(images[key]), width=7.2 * inch, height=4.2 * inch if key != "graph" else 5.2 * inch))
    doc.build(story)
    return pdf_path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    metrics = load_metrics()
    images = {
        "publishers": save_bar_chart(metrics["top_publishers"], "publisher", "article_count", "Top Publishers by Article Count", GRAPH_DIR / "top_publishers.png", "#1d6f99"),
        "products": save_bar_chart(metrics["top_products"], "product", "mentions", "Top Apple Products by Mentions", GRAPH_DIR / "top_products.png", "#2f7d5c"),
        "timeseries": save_timeseries(metrics, GRAPH_DIR / "news_social_volume.png"),
        "sentiment": save_sentiment(metrics, GRAPH_DIR / "sentiment_timeline.png"),
        "trends": save_trend_chart(metrics, GRAPH_DIR / "trend_scores.png"),
        "graph": save_graph(metrics, GRAPH_DIR / "knowledge_graph.png"),
    }
    pdf_path = build_pdf(metrics, images, OUTPUT_DIR / "apple_news_intelligence_report.pdf")
    appendix_path = build_graph_appendix_pdf(images, OUTPUT_DIR / "apple_news_graph_appendix.pdf")
    index = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "pdfs": {
            "report": str(pdf_path),
            "graph_appendix": str(appendix_path),
        },
        "graphs": {name: str(path) for name, path in images.items()},
        "source": str(GOLD_PATH),
    }
    (OUTPUT_DIR / "outputs_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()
