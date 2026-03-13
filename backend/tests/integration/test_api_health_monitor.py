"""Integration tests for feed health monitoring API endpoints.

Tests the full flow: HTTP request → FastAPI routing → HealthMonitorService → DB update → response.
"""

from unittest.mock import MagicMock, patch

import httpx

from backend.src.infrastructure.models import Subscription
from backend.tests.conftest import sample_source, sample_subscription


# Minimal valid RSS for mocking successful fetches
VALID_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <item><title>Test Entry</title></item>
  </channel>
</rss>"""

EMPTY_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel><title>Empty</title></channel>
</rss>"""


def _mock_successful_get(mock_client_cls: MagicMock) -> None:
    """Configure httpx.Client mock to return a valid RSS response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = VALID_RSS
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
    mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)


def _mock_timeout_get(mock_client_cls: MagicMock) -> None:
    """Configure httpx.Client mock to raise a timeout."""
    mock_client = MagicMock()
    mock_client.get.side_effect = httpx.TimeoutException("timeout")
    mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
    mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)


class TestSingleSourceHealthCheck:
    """POST /api/sources/{id}/health-check"""

    def test_healthy_source_returns_status(self, test_client, db_session) -> None:
        """Healthy feed returns correct status and updates DB."""
        source = sample_source(name="Healthy Feed")
        db_session.add(source)
        db_session.flush()

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock:
            _mock_successful_get(mock)
            response = test_client.post(f"/api/sources/{source.id}/health-check")

        assert response.status_code == 200
        data = response.json()
        assert data["source_id"] == source.id
        assert data["source_name"] == "Healthy Feed"
        assert data["new_status"] == "healthy"
        assert data["consecutive_failures"] == 0
        assert data["error"] is None

    def test_failing_source_escalates(self, test_client, db_session) -> None:
        """Failing feed increments failures and escalates status."""
        source = sample_source(name="Failing Feed")
        db_session.add(source)
        db_session.flush()

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock:
            _mock_timeout_get(mock)
            response = test_client.post(f"/api/sources/{source.id}/health-check")

        assert response.status_code == 200
        data = response.json()
        assert data["new_status"] == "degraded"
        assert data["consecutive_failures"] == 1
        assert data["error"] is not None

    def test_not_found_source(self, test_client) -> None:
        """Returns 404 for nonexistent source."""
        response = test_client.post("/api/sources/99999/health-check")
        assert response.status_code == 404

    def test_dead_source_deactivated(self, test_client, db_session) -> None:
        """Source with 5 prior failures becomes dead and deactivated on 6th."""
        source = sample_source(
            name="Almost Dead",
            consecutive_failures=5,
            health_status="unhealthy",
        )
        db_session.add(source)
        db_session.flush()

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock:
            _mock_timeout_get(mock)
            response = test_client.post(f"/api/sources/{source.id}/health-check")

        data = response.json()
        assert data["new_status"] == "dead"
        assert data["consecutive_failures"] == 6

        # Verify DB was updated
        db_session.refresh(source)
        assert source.is_active is False
        assert source.health_status == "dead"

    def test_recovery_from_unhealthy(self, test_client, db_session) -> None:
        """A previously unhealthy source recovers to healthy on success."""
        source = sample_source(
            name="Recovering",
            consecutive_failures=4,
            health_status="unhealthy",
        )
        db_session.add(source)
        db_session.flush()

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock:
            _mock_successful_get(mock)
            response = test_client.post(f"/api/sources/{source.id}/health-check")

        data = response.json()
        assert data["previous_status"] == "unhealthy"
        assert data["new_status"] == "healthy"
        assert data["consecutive_failures"] == 0


class TestBulkHealthCheck:
    """POST /api/sources/health-check"""

    def test_checks_all_subscribed(self, test_client, db_session) -> None:
        """Bulk check runs on all subscribed active sources."""
        source_a = sample_source(name="Feed A")
        source_b = sample_source(
            name="Feed B", feed_url="https://example.com/b.xml",
        )
        db_session.add_all([source_a, source_b])
        db_session.flush()

        db_session.add(sample_subscription(source_id=source_a.id))
        db_session.add(sample_subscription(source_id=source_b.id))
        db_session.flush()

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock:
            _mock_successful_get(mock)
            response = test_client.post("/api/sources/health-check")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = {r["source_name"] for r in data}
        assert names == {"Feed A", "Feed B"}
        assert all(r["new_status"] == "healthy" for r in data)

    def test_empty_when_no_subscriptions(self, test_client) -> None:
        """Returns empty list when no subscribed sources."""
        response = test_client.post("/api/sources/health-check")
        assert response.status_code == 200
        assert response.json() == []

    def test_skips_inactive_sources(self, test_client, db_session) -> None:
        """Inactive sources are not checked even if subscribed."""
        active = sample_source(name="Active")
        inactive = sample_source(
            name="Inactive", is_active=False,
            feed_url="https://example.com/inactive.xml",
        )
        db_session.add_all([active, inactive])
        db_session.flush()

        db_session.add(sample_subscription(source_id=active.id))
        db_session.add(sample_subscription(source_id=inactive.id))
        db_session.flush()

        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock:
            _mock_successful_get(mock)
            response = test_client.post("/api/sources/health-check")

        data = response.json()
        assert len(data) == 1
        assert data[0]["source_name"] == "Active"


class TestHealthFieldsInSourceResponse:
    """GET /api/sources should include health fields."""

    def test_new_source_has_default_health_fields(self, test_client, db_session) -> None:
        """Newly created source has default health fields in API response."""
        source = sample_source(name="Fresh Source")
        db_session.add(source)
        db_session.flush()

        sub = sample_subscription(source_id=source.id)
        db_session.add(sub)
        db_session.flush()

        response = test_client.get("/api/sources")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        source_data = next(s for s in data if s["name"] == "Fresh Source")
        assert source_data["health_status"] == "healthy"
        assert source_data["consecutive_failures"] == 0
        assert source_data["last_health_check"] is None
        assert source_data["last_healthy_at"] is None

    def test_health_fields_updated_after_check(self, test_client, db_session) -> None:
        """Health fields are updated in GET response after a health check."""
        source = sample_source(name="Checked Source")
        db_session.add(source)
        db_session.flush()

        sub = sample_subscription(source_id=source.id)
        db_session.add(sub)
        db_session.flush()

        # Run a health check first
        with patch("backend.src.infrastructure.health_monitor.httpx.Client") as mock:
            _mock_successful_get(mock)
            test_client.post(f"/api/sources/{source.id}/health-check")

        # Now GET should reflect updated fields
        response = test_client.get("/api/sources")
        data = response.json()
        source_data = next(s for s in data if s["name"] == "Checked Source")

        assert source_data["health_status"] == "healthy"
        assert source_data["consecutive_failures"] == 0
        assert source_data["last_health_check"] is not None
        assert source_data["last_healthy_at"] is not None
