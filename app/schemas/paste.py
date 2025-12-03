from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Request schemas
class PasteCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: str = Field(..., min_length=1)
    language: str = Field(default="text", max_length=50)
    is_public: bool = True
    password: Optional[str] = None
    expires_in_hours: Optional[int] = None  # null = never expires


class PasteUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    language: Optional[str] = None
    is_public: Optional[bool] = None


# Response schemas
class PasteResponse(BaseModel):
    id: int
    title: Optional[str]
    content: str
    language: str
    short_code: str
    is_public: bool
    expires_at: Optional[datetime]
    created_at: datetime
    view_count: int

    class Config:
        from_attributes = True  # Replaces orm_mode in Pydantic V2


class PasteListResponse(BaseModel):
    id: int
    title: Optional[str]
    short_code: str
    language: str
    created_at: datetime
    view_count: int

    class Config:
        from_attributes = True
