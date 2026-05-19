"""Social buzz endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query

from backend.services.repository import repository

router = APIRouter(tags=["social"])


@router.get("/social/buzz")
def social_buzz(limit: int = Query(50, ge=1, le=100)) -> list[dict]:
    return repository.social_buzz(limit)
