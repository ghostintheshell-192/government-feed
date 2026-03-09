"""Shared application state for cross-router access."""

from backend.src.infrastructure.cache import RedisCache
from backend.src.infrastructure.scheduler import FeedScheduler

scheduler: FeedScheduler | None = None
cache: RedisCache | None = None
