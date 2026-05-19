"""News endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query

from backend.services.repository import repository

router = APIRouter(tags=["news"])


@router.get("/news/latest")
def latest_news(limit: int = Query(25, ge=1, le=100)) -> list[dict]:
    return repository.latest_news(limit)


@router.get("/news/trending")
def trending_news(limit: int = Query(15, ge=1, le=50)) -> list[dict]:
    return repository.trending_news(limit)


@router.get("/publishers/top")
def top_publishers(limit: int = Query(15, ge=1, le=50)) -> list[dict]:
    return repository.top_publishers(limit)
