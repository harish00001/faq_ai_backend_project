from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, field_validator


class FAQBase(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000)
    answer: str = Field(..., min_length=2, max_length=5000)
    category: str | None = Field(default=None, max_length=120)
    tags: list[str] = Field(default_factory=list)

    @field_validator("question", "answer")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class FAQCreate(FAQBase):
    pass


class FAQResponse(FAQBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [tag for tag in value.split(",") if tag]
        return value


class FAQListResponse(BaseModel):
    total: int
    count: int
    items: list[FAQResponse]


class BulkFAQCreate(BaseModel):
    items: list[FAQCreate] = Field(..., min_length=1, max_length=500)


class BulkFAQCreateResponse(BaseModel):
    count: int
    items: list[FAQResponse]


class FAQSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=20)

    @field_validator("query")
    @classmethod
    def strip_query(cls, value: str) -> str:
        return value.strip()


class FAQSearchItem(FAQResponse):
    score: float
    matched: bool


class FAQSearchResponse(BaseModel):
    query: str
    total_hits: int
    items: list[FAQSearchItem]


class MessageResponse(BaseModel):
    message: str
