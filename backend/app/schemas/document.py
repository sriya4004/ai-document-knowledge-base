from datetime import datetime

from pydantic import BaseModel, field_serializer

from app.core.datetime_json import datetime_to_utc_z


class DocumentCreate(BaseModel):
    title: str
    category: str = "general"
    source: str
    content: str | None = None


class DocumentUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    source: str | None = None
    content: str | None = None


class DocumentRead(BaseModel):
    id: int
    title: str
    category: str
    source: str
    file_name: str | None = None
    stored_file_path: str | None = None
    file_type: str | None = None
    has_original_file: bool = False
    content: str
    department: str
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at", when_used="json")
    def serialize_created_at(self, value: datetime) -> str:
        return datetime_to_utc_z(value) if value else ""
