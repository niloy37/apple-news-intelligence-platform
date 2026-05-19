import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.main import app


def test_api_health_and_latest_news():
    client = TestClient(app)
    assert client.get("/health").json()["status"] == "ok"
    response = client.get("/news/latest?limit=3")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_semantic_search_endpoint():
    client = TestClient(app)
    response = client.post("/search/semantic", json={"query": "iPhone supply chain", "limit": 3})
    assert response.status_code == 200
    assert len(response.json()) <= 3
