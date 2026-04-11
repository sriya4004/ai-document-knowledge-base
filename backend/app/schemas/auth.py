from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_serializer

from app.core.datetime_json import datetime_to_utc_z

Role = Literal["admin", "employee"]


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: Role = "employee"
    department: str = "general"


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: Role
    department: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at", when_used="json")
    def serialize_created_at(self, value: datetime) -> str:
        return datetime_to_utc_z(value) if value else ""


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
