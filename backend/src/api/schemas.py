"""Pydantic schemas for API."""

from datetime import datetime
from typing import Literal

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
    health_status: str = "healthy"
    consecutive_failures: int = 0
    last_health_check: datetime | None = None
    last_healthy_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


# ==================== CATALOG SCHEMAS ====================


class CatalogSourceResponse(BaseModel):
    """Schema for a source in the catalog browse view."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    feed_url: str
    source_type: str
    category: str | None
    geographic_level: str | None
    country_code: str | None
    region: str | None
    tags: list[str]
    is_curated: bool
    is_subscribed: bool = False


class PaginatedCatalogResponse(BaseModel):
    """Paginated response for catalog browsing."""

    items: list[CatalogSourceResponse]
    pagination: "PaginationMeta"


class CatalogStatsResponse(BaseModel):
    """Statistics about the catalog."""

    total_sources: int
    by_geographic_level: dict[str, int]
    top_tags: list[tuple[str, int]]


class SubscriptionResponse(BaseModel):
    """Schema for subscription response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    is_active: bool
    added_at: datetime


class HealthCheckResultResponse(BaseModel):
    """Result of a health check on a single source."""

    source_id: int
    source_name: str
    previous_status: str
    new_status: str
    consecutive_failures: int
    error: str | None = None


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


class FeedValidationRequest(BaseModel):
    """Request schema for feed URL validation."""

    feed_url: str = Field(..., min_length=1, max_length=500)


class FeedValidationResponse(BaseModel):
    """Response schema for feed URL validation."""

    valid: bool
    feed_title: str | None = None
    entry_count: int = 0
    error: str | None = None


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


# ==================== ADMIN SCHEMAS ====================


class NewsPreviewResponse(BaseModel):
    """Brief article preview for feed inspector."""

    id: int
    title: str
    published_at: datetime
    snippet: str | None


class SourceStatsResponse(BaseModel):
    """Statistics for a single source."""

    source_id: int
    source_name: str
    article_count: int
    earliest_article: datetime | None
    latest_article: datetime | None
    avg_content_length: int | None
    last_fetched: datetime | None
    is_active: bool


class CleanupResultResponse(BaseModel):
    """Result of a cleanup operation."""

    matched: int
    deleted: int
    dry_run: bool


class ReimportResultResponse(BaseModel):
    """Result of a purge + reimport operation."""

    purged: int
    imported: int


class BulkFetchResultResponse(BaseModel):
    """Result of bulk content fetching for a source."""

    total: int
    fetched: int
    skipped: int
    failed: int


class PatternCleanupRequest(BaseModel):
    """Request for pattern-based article cleanup."""

    field: Literal["title", "content"]
    pattern: str = Field(..., min_length=1, max_length=500)
    source_id: int | None = None
    dry_run: bool = True


class HtmlResidueFlagResponse(BaseModel):
    """A single HTML residue flag."""

    id: int
    title: str
    field: str


class HtmlResidueResultResponse(BaseModel):
    """Result of HTML residue cleanup."""

    flagged: list[HtmlResidueFlagResponse]
    fixed: int
    dry_run: bool


class PerSourceCountResponse(BaseModel):
    """Article count for a single source."""

    source_id: int
    source_name: str
    article_count: int


class GlobalStatsResponse(BaseModel):
    """Global database statistics."""

    total_articles: int
    total_sources: int
    per_source: list[PerSourceCountResponse]


class ContentLengthFlagResponse(BaseModel):
    """An article flagged for unusual content length."""

    id: int
    title: str
    length: int


class DuplicateTitleResponse(BaseModel):
    """A group of duplicate titles within a source."""

    title: str
    source_id: int
    count: int


class EmptySourceResponse(BaseModel):
    """A source with zero articles."""

    id: int
    name: str


class QualityReportResponse(BaseModel):
    """Quality report with all issue categories."""

    total_articles: int
    total_sources: int
    short_content: list[ContentLengthFlagResponse]
    long_content: list[ContentLengthFlagResponse]
    html_residue: list[HtmlResidueFlagResponse]
    duplicate_titles: list[DuplicateTitleResponse]
    empty_sources: list[EmptySourceResponse]
