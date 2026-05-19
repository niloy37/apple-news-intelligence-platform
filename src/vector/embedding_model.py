"""Embedding model abstraction for local and optional hosted embeddings."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field

from src.config import Settings, get_settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class EmbeddingModel:
    settings: Settings = field(default_factory=get_settings)
    dimension: int = 384
    _model: object | None = None

    def __post_init__(self) -> None:
        if self.settings.embedding_provider in {"hash", "test"}:
            self._model = None
            return
        if self.settings.embedding_provider == "openai" and self.settings.openai_api_key:
            self.dimension = 1536
            return
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.settings.local_embedding_model)
            self.dimension = int(self._model.get_sentence_embedding_dimension())
        except Exception as exc:  # pragma: no cover - model download/runtime dependent
            logger.warning("Local sentence-transformers unavailable; using hash embeddings: %s", exc)
            self._model = None

    def embed(self, text: str) -> list[float]:
        text = text or ""
        if self.settings.embedding_provider == "openai" and self.settings.openai_api_key:
            return self._embed_openai(text)
        if self._model:
            vector = self._model.encode(text, normalize_embeddings=True)
            return [float(value) for value in vector.tolist()]
        return self._hash_embedding(text)

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        if self._model:
            vectors = self._model.encode(texts, normalize_embeddings=True)
            return [[float(value) for value in vector.tolist()] for vector in vectors]
        return [self.embed(text) for text in texts]

    def _embed_openai(self, text: str) -> list[float]:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.settings.openai_api_key)
            response = client.embeddings.create(model="text-embedding-3-small", input=text)
            return [float(value) for value in response.data[0].embedding]
        except Exception as exc:
            logger.warning("OpenAI embedding failed; falling back to hash embedding: %s", exc)
            return self._hash_embedding(text, dimension=1536)

    def _hash_embedding(self, text: str, dimension: int | None = None) -> list[float]:
        dimension = dimension or self.dimension
        values = [0.0] * dimension
        tokens = text.lower().split()
        if not tokens:
            return values
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            values[index] += sign
        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        return [round(value / norm, 6) for value in values]
