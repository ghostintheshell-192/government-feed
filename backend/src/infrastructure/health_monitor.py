"""Feed health monitoring service.

Performs stateful health checks on feed sources: GET + parse (not just HEAD),
tracks consecutive failures, escalates through health statuses, and deactivates
dead feeds.
"""

from datetime import UTC, datetime

import feedparser
import httpx
from backend.src.core.entities import HealthStatus
from backend.src.infrastructure.models import Source
from backend.src.infrastructure.unit_of_work import UnitOfWork
from shared.logging import get_logger

logger = get_logger(__name__)

_HEALTH_CHECK_TIMEOUT = 15.0


class HealthMonitorService:
    """Checks feed health and updates source status in the database."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow
        self._logger = get_logger(__name__)

    def check_source(self, source_id: int) -> dict[str, object]:
        """Run a health check on a single source. Returns check result."""
        source = self._uow.source_repository.get_by_id(source_id)
        if source is None:
            raise ValueError(f"Source {source_id} not found")
        return self._perform_check(source)

    def check_all_subscribed(self, user_id: int = 1) -> list[dict[str, object]]:
        """Run health checks on all subscribed sources."""
        subscribed_ids = set(
            self._uow.subscription_repository.get_subscribed_source_ids(user_id=user_id)
        )
        sources = [
            s for s in self._uow.source_repository.get_all()
            if s.id in subscribed_ids and s.is_active
        ]

        results: list[dict[str, object]] = []
        with httpx.Client(timeout=_HEALTH_CHECK_TIMEOUT, follow_redirects=True) as client:
            for source in sources:
                result = self._perform_check(source, client=client)
                results.append(result)

        return results

    def _perform_check(
        self,
        source: Source,
        client: httpx.Client | None = None,
    ) -> dict[str, object]:
        """Perform a single health check: GET feed, parse, update status."""
        previous_status = source.health_status
        error_msg: str | None = None

        try:
            if client is None:
                with httpx.Client(
                    timeout=_HEALTH_CHECK_TIMEOUT, follow_redirects=True
                ) as c:
                    self._fetch_and_validate(c, source.feed_url)
            else:
                self._fetch_and_validate(client, source.feed_url)

            # Success: reset failures
            source.consecutive_failures = 0
            source.health_status = HealthStatus.HEALTHY
            source.last_healthy_at = datetime.now(UTC)

        except HealthCheckError as e:
            error_msg = str(e)
            source.consecutive_failures += 1
            new_status = HealthStatus.from_failure_count(source.consecutive_failures)
            source.health_status = new_status

            if new_status == HealthStatus.DEAD:
                source.is_active = False
                self._logger.warning(
                    "Source deactivated (dead): %s (%s) after %d consecutive failures",
                    source.name,
                    source.feed_url,
                    source.consecutive_failures,
                )
            else:
                self._logger.info(
                    "Health check failed for %s: %s → %s (failures: %d)",
                    source.name,
                    previous_status,
                    new_status,
                    source.consecutive_failures,
                )

        source.last_health_check = datetime.now(UTC)
        self._uow.source_repository.update(source)
        self._uow.commit()

        return {
            "source_id": source.id,
            "source_name": source.name,
            "previous_status": previous_status,
            "new_status": source.health_status,
            "consecutive_failures": source.consecutive_failures,
            "error": error_msg,
        }

    def _fetch_and_validate(self, client: httpx.Client, feed_url: str) -> None:
        """Fetch feed URL and validate it contains parseable entries."""
        try:
            response = client.get(feed_url)
            response.raise_for_status()
        except httpx.TimeoutException as e:
            raise HealthCheckError(f"Timeout fetching {feed_url}") from e
        except httpx.HTTPStatusError as e:
            raise HealthCheckError(
                f"HTTP {e.response.status_code} from {feed_url}"
            ) from e
        except httpx.RequestError as e:
            raise HealthCheckError(f"Connection error: {e}") from e

        parsed = feedparser.parse(response.text)

        if parsed.bozo and not parsed.entries:
            raise HealthCheckError(
                f"Feed parse error: {parsed.bozo_exception}"
            )

        if not parsed.entries:
            raise HealthCheckError("Feed returned no entries")


class HealthCheckError(Exception):
    """Raised when a health check fails."""
