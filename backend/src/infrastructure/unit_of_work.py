"""Unit of Work pattern implementation for managing repositories and transactions."""

from backend.src.core.repositories.news_repository import INewsRepository
from backend.src.core.repositories.source_repository import ISourceRepository
from backend.src.infrastructure.repositories.news_repository import NewsRepository
from backend.src.infrastructure.repositories.source_repository import SourceRepository
from shared.logging import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)


class UnitOfWork:
    """
    Unit of Work pattern implementation.

    Manages repository instances and coordinates database transactions.
    Repositories are created lazily on first access.
    """

    def __init__(self, db: Session):
        """
        Initialize Unit of Work with database session.

        Args:
            db: SQLAlchemy database session
        """
        self._db = db
        self._news_repository: INewsRepository | None = None
        self._source_repository: ISourceRepository | None = None

    @property
    def news_repository(self) -> INewsRepository:
        """
        Get NewsRepository instance (lazy initialization).

        Returns:
            NewsRepository instance
        """
        if self._news_repository is None:
            self._news_repository = NewsRepository(self._db)
            logger.debug("NewsRepository initialized")
        return self._news_repository

    @property
    def source_repository(self) -> ISourceRepository:
        """
        Get SourceRepository instance (lazy initialization).

        Returns:
            SourceRepository instance
        """
        if self._source_repository is None:
            self._source_repository = SourceRepository(self._db)
            logger.debug("SourceRepository initialized")
        return self._source_repository

    def commit(self) -> None:
        """
        Commit the current transaction.

        Saves all pending changes to the database.
        """
        self._db.commit()
        logger.debug("Transaction committed")

    def rollback(self) -> None:
        """
        Rollback the current transaction.

        Discards all pending changes.
        """
        self._db.rollback()
        logger.debug("Transaction rolled back")

    def close(self) -> None:
        """Close the database session."""
        self._db.close()
        logger.debug("Database session closed")
