"""Concrete repository implementations."""

from backend.src.infrastructure.repositories.news_repository import NewsRepository
from backend.src.infrastructure.repositories.source_repository import SourceRepository

__all__ = ["NewsRepository", "SourceRepository"]
