"""Tests for HealthMonitorService."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from backend.src.core.entities import HealthStatus
from backend.src.infrastructure.health_monitor import HealthCheckError, HealthMonitorService
from tests.conftest import sample_source, sample_subscription


class TestHealthStatusEscalation:
    """Tests for the HealthStatus.from_failure_count escalation ladder."""

    def test_zero_failures_is_healthy(self) -> None:
        assert HealthStatus.from_failure_count(0) == HealthStatus.HEALTHY

    def test_one_failure_is_degraded(self) -> None:
        assert HealthStatus.from_failure_count(1) == HealthStatus.DEGRADED

    def test_two_failures_is_degraded(self) -> None:
        assert HealthStatus.from_failure_count(2) == HealthStatus.DEGRADED

    def test_three_failures_is_unhealthy(self) -> None:
        assert HealthStatus.from_failure_count(3) == HealthStatus.UNHEALTHY

    def test_five_failures_is_unhealthy(self) -> None:
        assert HealthStatus.from_failure_count(5) == HealthStatus.UNHEALTHY

    def test_six_failures_is_dead(self) -> None:
        assert HealthStatus.from_failure_count(6) == HealthStatus.DEAD

    def test_many_failures_is_dead(self) -> None:
        assert HealthStatus.from_failure_count(100) == HealthStatus.DEAD


# Minimal valid RSS feed for mocking
VALID_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <item><title>Test Entry</title></item>
  </channel>
</rss>"""

EMPTY_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel><title>Empty Feed</title></channel>
</rss>"""


class TestCheckSource:
    """Tests for single-source health checks with real DB."""

    def test_healthy_feed_resets_failures(self, db_session, uow) -> None:
        """A successful check resets consecutive_failures and sets healthy."""
        source = sample_source(consecutive_failures=3, health_status="unhealthy")
        db_session.add(source)
        db_session.flush()

        sub = sample_subscription(source_id=source.id)
        db_session.add(sub)
        db_session.flush()

        monitor = HealthMonitorService(uow)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = VALID_RSS
        mock_response.raise_for_status = MagicMock()

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = monitor.check_source(source.id)

        assert result["new_status"] == "healthy"
        assert result["consecutive_failures"] == 0
        assert result["previous_status"] == "unhealthy"
        assert source.consecutive_failures == 0
        assert source.last_healthy_at is not None

    def test_failure_increments_count(self, db_session, uow) -> None:
        """A failed check increments consecutive_failures."""
        source = sample_source(consecutive_failures=0, health_status="healthy")
        db_session.add(source)
        db_session.flush()

        monitor = HealthMonitorService(uow)

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get.side_effect = httpx.TimeoutException("timeout")
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = monitor.check_source(source.id)

        assert result["new_status"] == "degraded"
        assert result["consecutive_failures"] == 1
        assert result["error"] is not None

    def test_escalation_to_unhealthy(self, db_session, uow) -> None:
        """Third failure escalates to unhealthy."""
        source = sample_source(consecutive_failures=2, health_status="degraded")
        db_session.add(source)
        db_session.flush()

        monitor = HealthMonitorService(uow)

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get.side_effect = httpx.TimeoutException("timeout")
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = monitor.check_source(source.id)

        assert result["new_status"] == "unhealthy"
        assert result["consecutive_failures"] == 3

    def test_dead_deactivates_source(self, db_session, uow) -> None:
        """Sixth failure marks source as dead and sets is_active=False."""
        source = sample_source(consecutive_failures=5, health_status="unhealthy")
        db_session.add(source)
        db_session.flush()

        monitor = HealthMonitorService(uow)

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get.side_effect = httpx.TimeoutException("timeout")
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = monitor.check_source(source.id)

        assert result["new_status"] == "dead"
        assert result["consecutive_failures"] == 6
        assert source.is_active is False

    def test_http_error_is_failure(self, db_session, uow) -> None:
        """HTTP 404 is treated as a health check failure."""
        source = sample_source()
        db_session.add(source)
        db_session.flush()

        monitor = HealthMonitorService(uow)

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=mock_response,
        )

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = monitor.check_source(source.id)

        assert result["new_status"] == "degraded"
        assert "404" in result["error"]

    def test_empty_feed_is_failure(self, db_session, uow) -> None:
        """A feed with no entries is treated as a failure."""
        source = sample_source()
        db_session.add(source)
        db_session.flush()

        monitor = HealthMonitorService(uow)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = EMPTY_RSS
        mock_response.raise_for_status = MagicMock()

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = monitor.check_source(source.id)

        assert result["new_status"] == "degraded"
        assert "no entries" in result["error"]

    def test_nonexistent_source_raises(self, db_session, uow) -> None:
        """Checking a nonexistent source raises ValueError."""
        monitor = HealthMonitorService(uow)
        with pytest.raises(ValueError, match="not found"):
            monitor.check_source(99999)

    def test_last_health_check_always_updated(self, db_session, uow) -> None:
        """last_health_check is set regardless of success or failure."""
        source = sample_source()
        db_session.add(source)
        db_session.flush()
        assert source.last_health_check is None

        monitor = HealthMonitorService(uow)

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get.side_effect = httpx.TimeoutException("timeout")
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            monitor.check_source(source.id)

        assert source.last_health_check is not None


class TestCheckAllSubscribed:
    """Tests for bulk health checks."""

    def test_checks_only_subscribed_active(self, db_session, uow) -> None:
        """Only checks sources that are subscribed and active."""
        active = sample_source(name="Active", is_active=True)
        inactive = sample_source(name="Inactive", is_active=False,
                                 feed_url="https://example.com/inactive.xml")
        unsubscribed = sample_source(name="Unsubscribed",
                                     feed_url="https://example.com/unsub.xml")
        db_session.add_all([active, inactive, unsubscribed])
        db_session.flush()

        # Only subscribe to active and inactive
        db_session.add(sample_subscription(source_id=active.id))
        db_session.add(sample_subscription(source_id=inactive.id))
        db_session.flush()

        monitor = HealthMonitorService(uow)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = VALID_RSS
        mock_response.raise_for_status = MagicMock()

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            results = monitor.check_all_subscribed()

        # Only the active+subscribed source should be checked
        assert len(results) == 1
        assert results[0]["source_name"] == "Active"

    def test_returns_empty_when_no_subscriptions(self, db_session, uow) -> None:
        """Returns empty list when there are no subscribed sources."""
        monitor = HealthMonitorService(uow)

        with patch("backend.src.infrastructure.health_monitor.httpx.Client"):
            results = monitor.check_all_subscribed()

        assert results == []
