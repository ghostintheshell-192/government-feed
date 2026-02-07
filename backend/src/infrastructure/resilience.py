"""Resilience patterns: retry decorators and circuit breaker."""

import time
from enum import Enum
from typing import Any

import httpx
from shared.logging import get_logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = get_logger(__name__)


# ==================== RETRY CALLBACKS ====================


def log_retry_attempt(retry_state: Any) -> None:
    """Log retry attempts with structured information."""
    exception = retry_state.outcome.exception() if retry_state.outcome else None
    logger.warning(
        "Retry attempt %d/%d for %s: %s",
        retry_state.attempt_number,
        retry_state.retry_object.stop.max_attempt_number,  # type: ignore[union-attr]
        retry_state.fn.__name__ if retry_state.fn else "unknown",
        str(exception) if exception else "unknown error",
    )


# ==================== RETRY DECORATORS ====================

_TRANSIENT_EXCEPTIONS = (httpx.ConnectError, httpx.TimeoutException)

retry_feed_fetch = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type(_TRANSIENT_EXCEPTIONS),
    before_sleep=log_retry_attempt,
    reraise=True,
)

retry_ollama_api = retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=2, min=2, max=4),
    retry=retry_if_exception_type(_TRANSIENT_EXCEPTIONS),
    before_sleep=log_retry_attempt,
    reraise=True,
)

retry_web_scraping = retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=2),
    retry=retry_if_exception_type(_TRANSIENT_EXCEPTIONS),
    before_sleep=log_retry_attempt,
    reraise=True,
)


# ==================== CIRCUIT BREAKER ====================


class CircuitBreakerOpenError(Exception):
    """Raised when a call is attempted on an open circuit breaker."""


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker pattern implementation.

    - CLOSED: requests pass through normally
    - OPEN: requests are rejected immediately (after `failure_threshold` consecutive failures)
    - HALF_OPEN: one request is allowed through after `recovery_timeout` seconds
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0.0

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker '%s' transitioning to HALF_OPEN", self.name)
        return self._state

    def reset(self) -> None:
        """Reset circuit breaker to initial closed state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0

    def _record_success(self) -> None:
        self._failure_count = 0
        if self._state != CircuitState.CLOSED:
            logger.info("Circuit breaker '%s' transitioning to CLOSED", self.name)
            self._state = CircuitState.CLOSED

    def _record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.monotonic()
        if self._state == CircuitState.HALF_OPEN or self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(
                "Circuit breaker '%s' OPEN after %d consecutive failures",
                self.name,
                self._failure_count,
            )

    def call(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Execute a synchronous function through the circuit breaker."""
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerOpenError(
                f"Circuit breaker '{self.name}' is open — service temporarily unavailable"
            )

        try:
            result = func(*args, **kwargs)
        except Exception:
            self._record_failure()
            raise

        self._record_success()
        return result

    async def call_async(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Execute an async function through the circuit breaker."""
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerOpenError(
                f"Circuit breaker '{self.name}' is open — service temporarily unavailable"
            )

        try:
            result = await func(*args, **kwargs)
        except Exception:
            self._record_failure()
            raise

        self._record_success()
        return result
