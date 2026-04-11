from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_serializer

from app.core.datetime_json import datetime_to_utc_z


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class SourceChunk(BaseModel):
    document_id: int
    title: str = ""
    snippet: str = ""
    category: str = ""
    score: float
    content: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]


class SearchHistoryRead(BaseModel):
    id: int
    query_text: str
    response_text: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at", when_used="json")
    def serialize_created_at(self, value: datetime) -> str:
        """UTC instant with Z so browsers compute relative time correctly."""
        return datetime_to_utc_z(value) if value else ""


class AnalyticsItem(BaseModel):
    label: str
    count: int


class DashboardAnalytics(BaseModel):
    most_searched_queries: list[AnalyticsItem]
    top_documents: list[AnalyticsItem]
