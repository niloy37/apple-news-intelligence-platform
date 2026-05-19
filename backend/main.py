"""FastAPI application for the Apple News Intelligence Platform."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import graph, news, search, social, trends

app = FastAPI(
    title="Apple News Intelligence Platform API",
    version="0.1.0",
    description="News, social buzz, graph, and semantic search API for Apple-related intelligence.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router)
app.include_router(trends.router)
app.include_router(graph.router)
app.include_router(search.router)
app.include_router(social.router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "apple-news-intelligence-platform"}


try:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator().instrument(app).expose(app, include_in_schema=False)
except Exception:
    pass
