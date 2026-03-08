"""Pydantic schemas for API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    last_fetched: datetime | None
    created_at: datetime
    updated_at: datetime


class NewsItemResponse(BaseModel):
    """Schema for NewsItem response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    external_id: str | None
    title: str
    content: str | None
    summary: str | None
    published_at: datetime
    fetched_at: datetime
    relevance_score: float | None
    verification_status: str


class PaginationMeta(BaseModel):
    """Pagination metadata for paginated responses."""

    total: int
    limit: int
    offset: int
    has_more: bool


class PaginatedNewsResponse(BaseModel):
    """Paginated response for news items."""

    items: list[NewsItemResponse]
    pagination: PaginationMeta


class SettingsUpdate(BaseModel):
    """Validated settings update schema. Only whitelisted keys are accepted."""

    ai_enabled: bool | None = None
    summary_max_words: int | None = Field(None, ge=10, le=1000)
    scheduler_enabled: bool | None = None
    news_retention_days: int | None = Field(None, ge=1, le=365)
    ollama_endpoint: str | None = Field(None, max_length=200)
    ollama_model: str | None = Field(None, max_length=100)
    redis_url: str | None = Field(None, max_length=200)


class FeedDiscoveryRequest(BaseModel):
    """Request schema for feed discovery."""

    query: str = Field(..., min_length=1, max_length=500)


class DiscoveredFeedResponse(BaseModel):
    """Schema for a discovered feed."""

    url: str
    title: str
    feed_type: str
    site_url: str
    entry_count: int


class FeedDiscoveryResponse(BaseModel):
    """Response schema for feed discovery."""

    feeds: list[DiscoveredFeedResponse]
    searched_sites: list[str]
