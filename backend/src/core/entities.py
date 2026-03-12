"""Domain entities for Government Feed.

These dataclasses define the canonical domain fields. Infrastructure models
(SQLAlchemy) mirror these fields for persistence. Repository interfaces
reference these types; concrete repositories return SQLAlchemy model instances
that are structurally compatible (duck typing).
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from hashlib import sha256


class GeographicLevel(str, Enum):
    """Geographic scope of an institutional source."""

    LOCAL = "LOCAL"
    NATIONAL = "NATIONAL"
    CONTINENTAL = "CONTINENTAL"
    GLOBAL = "GLOBAL"


@dataclass
class Source:
    """An institutional source of news/communications (catalog entry)."""

    id: int | None = None
    name: str = ""
    description: str | None = None
    feed_url: str = ""
    source_type: str = "RSS"
    category: str | None = None
    update_frequency_minutes: int = 60
    is_active: bool = True
    last_fetched: datetime | None = None
    # Catalog fields
    geographic_level: str | None = None
    country_code: str | None = None
    region: str | None = None
    tags: list[str] = field(default_factory=list)
    is_curated: bool = False
    verified_at: datetime | None = None
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Subscription:
    """A user's subscription to a source."""

    id: int | None = None
    user_id: int = 1
    source_id: int = 0
    is_active: bool = True
    update_frequency_override: int | None = None
    added_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class NewsItem:
    """A news item from an institutional source."""

    id: int | None = None
    source_id: int = 0
    external_id: str | None = None
    title: str = ""
    content: str | None = None
    summary: str | None = None
    published_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    fetched_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    content_hash: str = ""
    relevance_score: float | None = None
    verification_status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def update_content_hash(self) -> None:
        """Calculate and update content hash for deduplication."""
        content_str = (
            f"{self.title}|{self.content}|{self.source_id}|{self.published_at.isoformat()}"
        )
        self.content_hash = sha256(content_str.encode()).hexdigest()
