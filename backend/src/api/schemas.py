"""Pydantic schemas for API."""

from datetime import datetime

from pydantic import BaseModel, Field


class SourceBase(BaseModel):
    """Base schema for Source."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    feed_url: str = Field(..., min_length=1, max_length=500)
    source_type: str = Field(default="RSS", max_length=50)
    category: str | None = Field(None, max_length=100)
    update_frequency_minutes: int = Field(default=60, ge=1)


class SourceCreate(SourceBase):
    """Schema for creating a Source."""

    pass


class SourceUpdate(SourceBase):
    """Schema for updating a Source."""

    is_active: bool = True


class SourceResponse(SourceBase):
    """Schema for Source response."""

    id: int
    is_active: bool
    last_fetched: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NewsItemResponse(BaseModel):
    """Schema for NewsItem response."""

    id: int
    source_id: int
    title: str
    content: str | None
    summary: str | None
    published_at: datetime
    fetched_at: datetime
    relevance_score: float | None
    verification_status: str

    class Config:
        from_attributes = True
