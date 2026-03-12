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

    def _build_filtered_query(
        self,
        source_ids: list[int] | None = None,
        search: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ):
        """Build a query with optional filters applied."""
        query = self._db.query(NewsItem)

        if source_ids is not None:
            if len(source_ids) == 0:
                query = query.filter(NewsItem.id == -1)  # no results
            else:
                query = query.filter(NewsItem.source_id.in_(source_ids))

        if search and search.strip():
            search_lower = search.lower()
            query = query.filter(
                (NewsItem.title.ilike(f"%{search_lower}%"))
                | (NewsItem.content.ilike(f"%{search_lower}%"))
            )

        if date_from is not None:
            query = query.filter(NewsItem.published_at >= date_from)

        if date_to is not None:
            query = query.filter(NewsItem.published_at <= date_to)

        return query

    def get_recent(
        self,
        limit: int = 20,
        offset: int = 0,
        source_ids: list[int] | None = None,
        search: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[NewsItem], int]:
        """Get recent news items with pagination and filters."""
        if limit <= 0:
            raise ValueError("Limit must be greater than zero")
        if offset < 0:
            raise ValueError("Offset must be non-negative")

        query = self._build_filtered_query(source_ids, search, date_from, date_to)

        total = query.count()

        items = (
            query
            .order_by(NewsItem.published_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return items, total

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

    def delete_by_source_id(self, source_id: int) -> int:
        """Delete all news items for a given source. Returns count of deleted items."""
        count = self._db.query(NewsItem).filter(NewsItem.source_id == source_id).delete()
        logger.debug("Deleted %d news items for source_id=%d", count, source_id)
        return count

    def update(self, news_item: NewsItem) -> None:
        """Update an existing news item."""
        if news_item is None:
            raise ValueError("News item cannot be None")

        self._db.merge(news_item)
        logger.debug(f"Updated news item: {news_item.title}")
