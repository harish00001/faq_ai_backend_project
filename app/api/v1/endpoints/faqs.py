from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.faq import (
    BulkFAQCreate,
    BulkFAQCreateResponse,
    FAQCreate,
    FAQListResponse,
    FAQResponse,
    FAQSearchRequest,
    FAQSearchResponse,
    MessageResponse,
)
from app.services.faq_service import FAQService

router = APIRouter()


@router.post("", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
def create_faq(payload: FAQCreate, db: Session = Depends(get_db)):
    service = FAQService(db)
    try:
        return service.create(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/bulk", response_model=BulkFAQCreateResponse, status_code=status.HTTP_201_CREATED)
def create_bulk_faqs(payload: BulkFAQCreate, db: Session = Depends(get_db)):
    service = FAQService(db)
    try:
        items = service.bulk_create(payload.items)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return BulkFAQCreateResponse(count=len(items), items=items)


@router.get("", response_model=FAQListResponse)
def list_faqs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = FAQService(db)
    items, total = service.list(skip=skip, limit=limit)
    return FAQListResponse(total=total, count=len(items), items=items)


@router.get("/{faq_id}", response_model=FAQResponse)
def get_faq(faq_id: int, db: Session = Depends(get_db)):
    service = FAQService(db)
    item = service.get(faq_id)
    if not item:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return item


@router.post("/search", response_model=FAQSearchResponse)
def search_faqs(payload: FAQSearchRequest, db: Session = Depends(get_db)):
    service = FAQService(db)
    return service.search(payload)


@router.delete("/{faq_id}", response_model=MessageResponse)
def delete_faq(faq_id: int, db: Session = Depends(get_db)):
    service = FAQService(db)
    deleted = service.delete(faq_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return MessageResponse(message="FAQ deleted successfully")
