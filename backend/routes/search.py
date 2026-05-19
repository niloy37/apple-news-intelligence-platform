"""Semantic search endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend.services.repository import repository
from src.schemas import SemanticSearchRequest

router = APIRouter(tags=["search"])


@router.post("/search/semantic")
def semantic_search(request: SemanticSearchRequest) -> list[dict]:
    return repository.semantic_search(request)
