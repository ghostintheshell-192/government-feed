"""Abstract repository interface for Source entities."""

from abc import ABC, abstractmethod

from backend.src.core.entities import Source


class ISourceRepository(ABC):
    """Abstract base class for Source repository."""

    @abstractmethod
    def get_by_id(self, id: int) -> Source | None:
        """Get source by ID."""
        pass

    @abstractmethod
    def get_all(self) -> list[Source]:
        """Get all sources."""
        pass

    @abstractmethod
    def get_active_sources(self) -> list[Source]:
        """Get only active sources."""
        pass

    @abstractmethod
    def add(self, source: Source) -> Source:
        """Add a new source."""
        pass

    @abstractmethod
    def update(self, source: Source) -> None:
        """Update an existing source."""
        pass

    @abstractmethod
    def get_by_ids(self, ids: list[int]) -> list[Source]:
        """Get sources by a list of IDs."""
        pass

    @abstractmethod
    def delete(self, source: Source) -> None:
        """Delete a source."""
        pass
