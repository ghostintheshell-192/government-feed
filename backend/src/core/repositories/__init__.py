"""Repository interfaces for the core domain."""

from backend.src.core.repositories.news_repository import INewsRepository
from backend.src.core.repositories.source_repository import ISourceRepository

__all__ = ["INewsRepository", "ISourceRepository"]
