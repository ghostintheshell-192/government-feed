"""Abstract repository interface for NewsItem entities."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from backend.src.infrastructure.models import NewsItem


class INewsRepository(ABC):
    """Abstract base class for NewsItem repository."""

    @abstractmethod
    def get_by_id(self, id: int) -> Optional["NewsItem"]:
        """Get news item by ID."""
        pass

    @abstractmethod
    def get_by_content_hash(self, content_hash: str) -> Optional["NewsItem"]:
        """Get news item by content hash (for deduplication)."""
        pass

    @abstractmethod
    def get_recent(
        self,
        limit: int = 20,
        offset: int = 0,
        source_ids: list[int] | None = None,
        search: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list["NewsItem"], int]:
        """Get recent news items with pagination and filters.

        Returns a tuple of (items, total_count).
        """
        pass

    @abstractmethod
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> list["NewsItem"]:
        """Get news items within a date range."""
        pass

    @abstractmethod
    def search(self, search_term: str) -> list["NewsItem"]:
        """Search news items by title or content."""
        pass

    @abstractmethod
    def add(self, news_item: "NewsItem") -> "NewsItem":
        """Add a new news item."""
        pass

    @abstractmethod
    def update(self, news_item: "NewsItem") -> None:
        """Update an existing news item."""
        pass
