"""SQLAlchemy ORM models."""

from datetime import UTC, datetime

from backend.src.infrastructure.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.types import JSON


class Source(Base):
    """Source model for database (catalog entry)."""

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    feed_url = Column(String(500), nullable=False)
    source_type = Column(String(50), default="RSS")
    category = Column(String(100), nullable=True)
    update_frequency_minutes = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)
    last_fetched = Column(DateTime, nullable=True)
    # Health monitoring
    health_status = Column(String(20), default="healthy", nullable=False)
    consecutive_failures = Column(Integer, default=0, nullable=False)
    last_health_check = Column(DateTime, nullable=True)
    last_healthy_at = Column(DateTime, nullable=True)
    # Catalog fields (ADR-005, ADR-007)
    geographic_level = Column(String(20), nullable=True)
    country_code = Column(String(2), nullable=True)
    region = Column(String(100), nullable=True)
    tags = Column(JSON, default=list)
    is_curated = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )


class Subscription(Base):
    """User subscription to a source (ADR-007)."""

    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("user_id", "source_id", name="uq_user_source"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=1, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    update_frequency_override = Column(Integer, nullable=True)
    added_at = Column(DateTime, default=lambda: datetime.now(UTC))


class NewsItem(Base):
    """NewsItem model for database."""

    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=False, index=True)
    external_id = Column(String(255), nullable=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=False, index=True)
    fetched_at = Column(DateTime, default=lambda: datetime.now(UTC))
    content_hash = Column(String(64), unique=True, index=True)
    relevance_score = Column(Float, nullable=True)
    verification_status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
