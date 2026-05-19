"""Graph exploration endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend.services.repository import repository

router = APIRouter(tags=["graph"])


@router.get("/graph/product/{product_name}")
def product_graph(product_name: str) -> dict:
    return repository.product_graph(product_name)


@router.get("/graph/article/{article_id}")
def article_graph(article_id: str) -> dict:
    return repository.article_graph(article_id)
