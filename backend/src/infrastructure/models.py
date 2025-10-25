"""SQLAlchemy ORM models."""

from datetime import datetime

from backend.src.infrastructure.database import Base
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text


class Source(Base):
    """Source model for database."""

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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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
    fetched_at = Column(DateTime, default=datetime.utcnow)
    content_hash = Column(String(64), unique=True, index=True)
    relevance_score = Column(Float, nullable=True)
    verification_status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
