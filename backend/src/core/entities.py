"""Domain entities for Government Feed."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from hashlib import sha256


class VerificationStatus(str, Enum):
    """Status of content verification."""

    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


@dataclass
class Source:
    """An institutional source of news/communications."""

    id: int | None = None
    name: str = ""
    url: str = ""
    feed_type: str = "rss"  # rss, atom, web_scraping
    is_active: bool = True
    country: str = "IT"
    category: str = "government"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Category:
    """Content categorization."""

    id: int | None = None
    name: str = ""
    slug: str = ""
    parent_id: int | None = None


@dataclass
class NewsItem:
    """A news item from an institutional source."""

    id: int | None = None
    source_id: int = 0
    external_id: str | None = None
    title: str = ""
    content: str | None = None
    summary: str | None = None
    published_at: datetime = field(default_factory=datetime.utcnow)
    fetched_at: datetime = field(default_factory=datetime.utcnow)
    content_hash: str = ""
    relevance_score: float | None = None
    verification_status: VerificationStatus = VerificationStatus.PENDING
    blockchain_certificate: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Relations (loaded separately)
    source: Source | None = None
    categories: list[Category] = field(default_factory=list)

    def update_content_hash(self) -> None:
        """Calculate and update content hash for deduplication."""
        content_str = f"{self.title}|{self.content}|{self.source_id}|{self.published_at.isoformat()}"
        self.content_hash = sha256(content_str.encode()).hexdigest()

    def mark_as_verified(self, certificate: str) -> None:
        """Mark item as verified with blockchain certificate."""
        if not certificate:
            raise ValueError("Certificate cannot be empty")
        self.blockchain_certificate = certificate
        self.verification_status = VerificationStatus.VERIFIED
        self.updated_at = datetime.utcnow()
