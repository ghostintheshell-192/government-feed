"""Unit tests for Redis cache layer."""

from unittest.mock import MagicMock, patch

import redis
from backend.src.infrastructure.cache import RedisCache


class TestRedisCacheAvailable:
    """Tests for RedisCache when Redis is available."""

    @patch("backend.src.infrastructure.cache.redis.Redis.from_url")
    def setup_method(self, method, mock_from_url):
        """Create a RedisCache with a mocked Redis connection."""
        self.mock_redis = MagicMock()
        self.mock_redis.ping.return_value = True
        mock_from_url.return_value = self.mock_redis
        self.cache = RedisCache(url="redis://localhost:6379")

    def test_init_sets_available(self):
        assert self.cache._available is True

    def test_get_returns_value(self):
        self.mock_redis.get.return_value = '{"key": "value"}'
        result = self.cache.get("test:key")
        assert result == '{"key": "value"}'
        self.mock_redis.get.assert_called_once_with("test:key")

    def test_get_returns_none_for_missing_key(self):
        self.mock_redis.get.return_value = None
        result = self.cache.get("missing:key")
        assert result is None

    def test_set_stores_value_with_ttl(self):
        self.cache.set("test:key", "value", ttl=300)
        self.mock_redis.set.assert_called_once_with("test:key", "value", ex=300)

    def test_set_stores_value_without_ttl(self):
        self.cache.set("test:key", "value")
        self.mock_redis.set.assert_called_once_with("test:key", "value", ex=None)

    def test_delete_exact_key(self):
        self.cache.delete("test:key")
        self.mock_redis.delete.assert_called_once_with("test:key")

    def test_delete_pattern_with_wildcard(self):
        self.mock_redis.keys.return_value = ["news:recent:10", "news:recent:50"]
        self.cache.delete("news:recent:*")
        self.mock_redis.keys.assert_called_once_with("news:recent:*")
        self.mock_redis.delete.assert_called_once_with("news:recent:10", "news:recent:50")

    def test_delete_pattern_no_matching_keys(self):
        self.mock_redis.keys.return_value = []
        self.cache.delete("news:recent:*")
        self.mock_redis.keys.assert_called_once_with("news:recent:*")
        self.mock_redis.delete.assert_not_called()

    def test_is_available_returns_true(self):
        self.mock_redis.ping.return_value = True
        assert self.cache.is_available() is True

    def test_is_available_returns_false_on_connection_error(self):
        self.mock_redis.ping.side_effect = redis.ConnectionError()
        assert self.cache.is_available() is False
        assert self.cache._available is False


class TestRedisCacheUnavailable:
    """Tests for RedisCache graceful fallback when Redis is down."""

    @patch("backend.src.infrastructure.cache.redis.Redis.from_url")
    def setup_method(self, method, mock_from_url):
        """Create a RedisCache with Redis unavailable."""
        self.mock_redis = MagicMock()
        self.mock_redis.ping.side_effect = redis.ConnectionError()
        mock_from_url.return_value = self.mock_redis
        self.cache = RedisCache(url="redis://localhost:6379")

    def test_init_sets_unavailable(self):
        assert self.cache._available is False

    def test_get_returns_none(self):
        result = self.cache.get("test:key")
        assert result is None
        self.mock_redis.get.assert_not_called()

    def test_set_is_noop(self):
        self.cache.set("test:key", "value", ttl=300)
        self.mock_redis.set.assert_not_called()

    def test_delete_is_noop(self):
        self.cache.delete("test:key")
        self.mock_redis.delete.assert_not_called()


class TestRedisCacheConnectionLoss:
    """Tests for RedisCache when connection is lost mid-operation."""

    @patch("backend.src.infrastructure.cache.redis.Redis.from_url")
    def setup_method(self, method, mock_from_url):
        """Create a RedisCache that loses connection after init."""
        self.mock_redis = MagicMock()
        self.mock_redis.ping.return_value = True
        mock_from_url.return_value = self.mock_redis
        self.cache = RedisCache(url="redis://localhost:6379")
        # Now simulate connection loss
        self.mock_redis.get.side_effect = redis.ConnectionError()
        self.mock_redis.set.side_effect = redis.ConnectionError()
        self.mock_redis.delete.side_effect = redis.ConnectionError()
        self.mock_redis.keys.side_effect = redis.ConnectionError()

    def test_get_returns_none_and_marks_unavailable(self):
        result = self.cache.get("test:key")
        assert result is None
        assert self.cache._available is False

    def test_set_marks_unavailable(self):
        self.cache.set("test:key", "value")
        assert self.cache._available is False

    def test_delete_marks_unavailable(self):
        self.cache.delete("test:key")
        assert self.cache._available is False

    def test_delete_pattern_marks_unavailable(self):
        self.cache.delete("news:*")
        assert self.cache._available is False
