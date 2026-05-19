from src.vector.embedding_model import EmbeddingModel
from src.vector.qdrant_client import QdrantVectorStore, VectorPoint
from src.vector.semantic_search import SemanticSearchService


def test_hash_embedding_is_deterministic():
    model = EmbeddingModel()
    assert model.embed("Apple iPhone") == model.embed("Apple iPhone")


def test_in_memory_vector_search_returns_best_match():
    model = EmbeddingModel()
    store = QdrantVectorStore()
    store.ensure_collection("article_embeddings", model.dimension)
    store.upsert(
        "article_embeddings",
        [
            VectorPoint("1", model.embed("Apple iPhone supply chain"), {"headline": "iPhone supply chain"}),
            VectorPoint("2", model.embed("Vision Pro developer story"), {"headline": "Vision Pro"}),
        ],
    )
    service = SemanticSearchService(model=model, store=store)
    hits = service.search("iPhone supply", limit=1)
    assert hits[0]["payload"]["headline"] == "iPhone supply chain"
