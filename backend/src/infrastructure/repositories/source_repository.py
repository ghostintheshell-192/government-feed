"""Concrete implementation of Source repository."""

from typing import Optional

from shared.logging import get_logger
from sqlalchemy.orm import Session

from backend.src.core.repositories.source_repository import ISourceRepository
from backend.src.infrastructure.models import Source

logger = get_logger(__name__)


class SourceRepository(ISourceRepository):
    """SQLAlchemy implementation of Source repository."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self._db = db

    def get_by_id(self, id: int) -> Optional[Source]:
        """Get source by ID."""
        return self._db.query(Source).filter(Source.id == id).first()

    def get_all(self) -> list[Source]:
        """Get all sources ordered by name."""
        return self._db.query(Source).order_by(Source.name).all()

    def get_active_sources(self) -> list[Source]:
        """Get only active sources ordered by name."""
        return self._db.query(Source).filter(Source.is_active == True).order_by(Source.name).all()

    def add(self, source: Source) -> Source:
        """Add a new source."""
        if source is None:
            raise ValueError("Source cannot be None")

        self._db.add(source)
        logger.debug(f"Added source to session: {source.name}")
        return source

    def update(self, source: Source) -> None:
        """Update an existing source."""
        if source is None:
            raise ValueError("Source cannot be None")

        self._db.merge(source)
        logger.debug(f"Updated source: {source.name}")

    def delete(self, source: Source) -> None:
        """Delete a source."""
        if source is None:
            raise ValueError("Source cannot be None")

        self._db.delete(source)
        logger.debug(f"Deleted source: {source.name}")
