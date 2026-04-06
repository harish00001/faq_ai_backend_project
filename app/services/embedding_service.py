from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    def __init__(self, model_name: str, fallback_dimension: int = 384):
        self.model_name = model_name
        self.fallback_dimension = fallback_dimension
        self.model = None
        self._dimension = fallback_dimension
        self._load_model()

    def _load_model(self) -> None:
        try:
            self.model = SentenceTransformer(self.model_name)
            self._dimension = int(self.model.get_sentence_embedding_dimension())
            logger.info("embedding_model_loaded", extra={"model": self.model_name, "dimension": self._dimension})
        except Exception as exc:  # pragma: no cover - fallback path
            self.model = None
            logger.warning("embedding_model_fallback_enabled", extra={"model": self.model_name, "reason": str(exc)})

    def _fallback_embed(self, text: str) -> list[float]:
        vector = np.zeros(self.fallback_dimension, dtype=np.float32)
        tokens = text.lower().split()
        if not tokens:
            return vector.tolist()
        for token in tokens:
            vector[hash(token) % self.fallback_dimension] += 1.0
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector.tolist()

    def embed_text(self, text: str) -> list[float]:
        if self.model is not None:
            vector = self.model.encode(text, normalize_embeddings=True)
            return vector.tolist()
        return self._fallback_embed(text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if self.model is not None:
            vectors = self.model.encode(texts, normalize_embeddings=True)
            return vectors.tolist()
        return [self._fallback_embed(text) for text in texts]

    def dimension(self) -> int:
        return self._dimension


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(settings.embedding_model)
