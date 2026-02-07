"""Redis caching layer with graceful fallback."""

import logging

import redis

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis caching layer with graceful fallback.

    All operations silently degrade when Redis is unavailable,
    ensuring the application continues to function without cache.
    """

    def __init__(self, url: str = "redis://localhost:6379") -> None:
        self._redis = redis.Redis.from_url(url, decode_responses=True)
        self._available = False
        try:
            self._redis.ping()
            self._available = True
            logger.info("Redis cache connected: %s", url)
        except redis.ConnectionError:
            logger.warning("Redis not available at %s, caching disabled", url)

    def get(self, key: str) -> str | None:
        """Get cached value by key. Returns None if unavailable."""
        if not self._available:
            return None
        try:
            result: str | None = self._redis.get(key)  # type: ignore[assignment]
            return result
        except redis.ConnectionError:
            self._available = False
            return None

    def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Set cached value with optional TTL in seconds."""
        if not self._available:
            return
        try:
            self._redis.set(key, value, ex=ttl)
        except redis.ConnectionError:
            self._available = False

    def delete(self, pattern: str) -> None:
        """Delete cache entries by exact key or wildcard pattern."""
        if not self._available:
            return
        try:
            if "*" in pattern:
                keys: list[str] = self._redis.keys(pattern)  # type: ignore[assignment]
                if keys:
                    self._redis.delete(*keys)
            else:
                self._redis.delete(pattern)
        except redis.ConnectionError:
            self._available = False

    def is_available(self) -> bool:
        """Check if Redis is currently available."""
        try:
            self._redis.ping()
            self._available = True
        except redis.ConnectionError:
            self._available = False
        return self._available
