"""Trend and sentiment endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query

from backend.services.repository import repository

router = APIRouter(tags=["trends"])


@router.get("/products/trending")
def products_trending(limit: int = Query(15, ge=1, le=50)) -> list[dict]:
    return repository.trending_products(limit)


@router.get("/sentiment/timeline")
def sentiment_timeline() -> list[dict]:
    return repository.sentiment_timeline()


@router.get("/trends/timeseries")
def trends_timeseries() -> list[dict]:
    return repository.trend_timeseries()
