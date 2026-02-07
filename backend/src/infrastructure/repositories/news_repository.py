"""Concrete implementation of NewsItem repository."""

from datetime import datetime

from backend.src.core.repositories.news_repository import INewsRepository
from backend.src.infrastructure.models import NewsItem
from shared.logging import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)


class NewsRepository(INewsRepository):
    """SQLAlchemy implementation of NewsItem repository."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self._db = db

    def get_by_id(self, id: int) -> NewsItem | None:
        """Get news item by ID."""
        return self._db.query(NewsItem).filter(NewsItem.id == id).first()

    def get_by_content_hash(self, content_hash: str) -> NewsItem | None:
        """Get news item by content hash (for deduplication)."""
        if not content_hash:
            raise ValueError("Content hash cannot be empty")

        return self._db.query(NewsItem).filter(NewsItem.content_hash == content_hash).first()

    def get_recent(self, limit: int = 50) -> list[NewsItem]:
        """Get recent news items ordered by published date."""
        if limit <= 0:
            raise ValueError("Limit must be greater than zero")

        return (
            self._db.query(NewsItem)
            .order_by(NewsItem.published_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> list[NewsItem]:
        """Get news items within a date range."""
        if start_date > end_date:
            raise ValueError("Start date must be before end date")

        return (
            self._db.query(NewsItem)
            .filter(NewsItem.published_at >= start_date, NewsItem.published_at <= end_date)
            .order_by(NewsItem.published_at.desc())
            .all()
        )

    def search(self, search_term: str) -> list[NewsItem]:
        """Search news items by title or content."""
        if not search_term or not search_term.strip():
            return []

        search_lower = search_term.lower()

        return (
            self._db.query(NewsItem)
            .filter(
                (NewsItem.title.ilike(f"%{search_lower}%"))
                | (NewsItem.content.ilike(f"%{search_lower}%"))
            )
            .order_by(NewsItem.published_at.desc())
            .all()
        )

    def add(self, news_item: NewsItem) -> NewsItem:
        """Add a new news item."""
        if news_item is None:
            raise ValueError("News item cannot be None")

        self._db.add(news_item)
        logger.debug(f"Added news item to session: {news_item.title}")
        return news_item

    def update(self, news_item: NewsItem) -> None:
        """Update an existing news item."""
        if news_item is None:
            raise ValueError("News item cannot be None")

        self._db.merge(news_item)
        logger.debug(f"Updated news item: {news_item.title}")
