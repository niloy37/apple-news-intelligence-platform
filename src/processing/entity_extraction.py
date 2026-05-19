"""Entity extraction for products, people, companies, countries, and topics."""

from __future__ import annotations

import re
from functools import lru_cache

from src.config import get_settings
from src.schemas import ArticleRecord, EntityRecord, SocialPostRecord, stable_id

APPLE_PRODUCTS = [
    "iPhone",
    "iPhone 17",
    "MacBook",
    "iPad",
    "Apple Watch",
    "Vision Pro",
    "iOS",
    "macOS",
    "App Store",
    "Apple Intelligence",
    "Apple chip",
    "M-series chip",
]

KNOWN_PEOPLE = ["Tim Cook", "Craig Federighi", "Jeff Williams", "Eddy Cue"]
KNOWN_COMPANIES = ["Apple", "OpenAI", "Google", "Samsung", "Foxconn", "TSMC", "Microsoft"]
COUNTRIES = ["United States", "China", "India", "Japan", "South Korea", "Germany", "United Kingdom"]


@lru_cache(maxsize=1)
def _load_spacy_model():
    try:
        import spacy

        return spacy.load("en_core_web_sm")
    except Exception:
        return None


def _keyword_entities(text: str, source_id: str, source_kind: str) -> list[EntityRecord]:
    entities: list[EntityRecord] = []
    catalog = [
        ("Product", APPLE_PRODUCTS),
        ("Person", KNOWN_PEOPLE),
        ("Company", KNOWN_COMPANIES),
        ("Country", COUNTRIES),
        ("Topic", list(get_settings().keywords)),
    ]
    for entity_type, values in catalog:
        for value in values:
            if re.search(rf"\b{re.escape(value)}\b", text, flags=re.IGNORECASE):
                entities.append(
                    EntityRecord(
                        entity_id=stable_id(f"{source_id}:{entity_type}:{value}"),
                        entity_text=value,
                        entity_type=entity_type,
                        source_id=source_id,
                        source_kind=source_kind,
                    )
                )
    return entities


def extract_entities_from_text(text: str, source_id: str, source_kind: str) -> list[EntityRecord]:
    entities = _keyword_entities(text, source_id, source_kind)
    nlp = _load_spacy_model()
    if not nlp:
        return _dedupe_entities(entities)
    doc = nlp(text[:2000])
    mapping = {"PERSON": "Person", "ORG": "Company", "GPE": "Country", "PRODUCT": "Product", "EVENT": "Event"}
    for ent in doc.ents:
        entity_type = mapping.get(ent.label_)
        if not entity_type:
            continue
        entities.append(
            EntityRecord(
                entity_id=stable_id(f"{source_id}:{entity_type}:{ent.text}"),
                entity_text=ent.text.strip(),
                entity_type=entity_type,
                source_id=source_id,
                source_kind=source_kind,
            )
        )
    return _dedupe_entities(entities)


def extract_article_entities(article: ArticleRecord) -> list[EntityRecord]:
    text = f"{article.headline}. {article.summary}. {article.body}"
    return extract_entities_from_text(text, article.article_id or str(article.url), "article")


def extract_social_entities(post: SocialPostRecord) -> list[EntityRecord]:
    return extract_entities_from_text(post.text, post.post_id, "social_post")


def _dedupe_entities(entities: list[EntityRecord]) -> list[EntityRecord]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[EntityRecord] = []
    for entity in entities:
        key = (entity.entity_text.lower(), entity.entity_type, entity.source_id)
        if key in seen:
            continue
        seen.add(key)
        unique.append(entity)
    return unique
