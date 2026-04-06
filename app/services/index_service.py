from pathlib import Path

import faiss
import numpy as np
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.faq import FAQ
from app.services.embedding_service import get_embedding_service
from app.utils.serializer import read_json, write_json

logger = get_logger(__name__)


class IndexService:
    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.dimension = self.embedding_service.dimension()
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_map: list[int] = []

    def initialize(self) -> None:
        Path(settings.index_dir).mkdir(parents=True, exist_ok=True)
        index_path = Path(settings.index_file)
        metadata = read_json(settings.metadata_file, default={"faq_ids": []})

        if index_path.exists():
            self.index = faiss.read_index(str(index_path))
            self.id_map = metadata.get("faq_ids", [])
            logger.info("faiss_index_loaded", extra={"count": len(self.id_map)})
        else:
            self._persist()
            logger.info("faiss_index_created_empty")

    def rebuild_from_db(self, db: Session) -> None:
        faqs = db.query(FAQ).order_by(FAQ.id.asc()).all()
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_map = []

        if faqs:
            texts = [faq.question for faq in faqs]
            vectors = np.array(self.embedding_service.embed_texts(texts), dtype="float32")
            self.index.add(vectors)
            self.id_map = [faq.id for faq in faqs]

        self._persist()
        logger.info("faiss_index_rebuilt", extra={"count": len(self.id_map)})

    def search(self, query: str, top_k: int) -> list[dict]:
        if self.index.ntotal == 0:
            return []

        query_vector = np.array([self.embedding_service.embed_text(query)], dtype="float32")
        scores, positions = self.index.search(query_vector, top_k)

        results: list[dict] = []
        for score, position in zip(scores[0], positions[0]):
            if position == -1:
                continue
            faq_id = self.id_map[position]
            results.append({"faq_id": faq_id, "score": float(score)})

        return results

    def _persist(self) -> None:
        Path(settings.index_dir).mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, settings.index_file)
        write_json(settings.metadata_file, {"faq_ids": self.id_map})


index_service = IndexService()
