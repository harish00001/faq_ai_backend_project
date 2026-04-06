from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQResponse, FAQSearchItem, FAQSearchRequest, FAQSearchResponse
from app.services.index_service import index_service


class FAQService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: FAQCreate) -> FAQ:
        item = FAQ(
            question=payload.question,
            answer=payload.answer,
            category=payload.category,
            tags=",".join(payload.tags) if payload.tags else None,
        )
        self.db.add(item)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ValueError("Question already exists. Use a unique FAQ question.") from exc
        self.db.refresh(item)
        index_service.rebuild_from_db(self.db)
        return item

    def bulk_create(self, items: list[FAQCreate]) -> list[FAQ]:
        rows = [
            FAQ(
                question=item.question,
                answer=item.answer,
                category=item.category,
                tags=",".join(item.tags) if item.tags else None,
            )
            for item in items
        ]
        self.db.add_all(rows)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ValueError("Bulk insert failed. Make sure questions are unique.") from exc
        for row in rows:
            self.db.refresh(row)
        index_service.rebuild_from_db(self.db)
        return rows

    def list(self, skip: int, limit: int) -> tuple[list[FAQ], int]:
        total = self.db.query(func.count(FAQ.id)).scalar() or 0
        items = self.db.query(FAQ).order_by(FAQ.id.desc()).offset(skip).limit(limit).all()
        return items, total

    def get(self, faq_id: int) -> FAQ | None:
        return self.db.query(FAQ).filter(FAQ.id == faq_id).first()

    def delete(self, faq_id: int) -> bool:
        item = self.get(faq_id)
        if not item:
            return False
        self.db.delete(item)
        self.db.commit()
        index_service.rebuild_from_db(self.db)
        return True

    def search(self, payload: FAQSearchRequest) -> FAQSearchResponse:
        hits = index_service.search(query=payload.query, top_k=payload.top_k)
        items: list[FAQSearchItem] = []

        for hit in hits:
            faq = self.get(hit["faq_id"])
            if not faq:
                continue
            tags = faq.tags.split(",") if faq.tags else []
            items.append(
                FAQSearchItem(
                    id=faq.id,
                    question=faq.question,
                    answer=faq.answer,
                    category=faq.category,
                    tags=tags,
                    created_at=faq.created_at,
                    updated_at=faq.updated_at,
                    score=round(hit["score"], 4),
                    matched=hit["score"] >= settings.similarity_threshold,
                )
            )

        return FAQSearchResponse(query=payload.query, total_hits=len(items), items=items)
