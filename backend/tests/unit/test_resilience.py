"""Unit tests for resilience module (CircuitBreaker + retry decorators)."""

import time
from unittest.mock import patch

import pytest

from backend.src.infrastructure.resilience import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)


class TestCircuitBreakerStates:
    """Tests for circuit breaker state management."""

    def test_initial_state_is_closed(self):
        cb = CircuitBreaker("test")
        assert cb.state == CircuitState.CLOSED

    def test_stays_closed_below_threshold(self):
        cb = CircuitBreaker("test", failure_threshold=3)
        for _ in range(2):
            cb._record_failure()
        assert cb.state == CircuitState.CLOSED

    def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker("test", failure_threshold=3)
        for _ in range(3):
            cb._record_failure()
        assert cb.state == CircuitState.OPEN

    def test_success_resets_failure_count(self):
        cb = CircuitBreaker("test", failure_threshold=3)
        cb._record_failure()
        cb._record_failure()
        cb._record_success()
        # Now fail again — should need 3 more failures to open
        cb._record_failure()
        cb._record_failure()
        assert cb.state == CircuitState.CLOSED

    def test_reset_returns_to_closed(self):
        cb = CircuitBreaker("test", failure_threshold=2)
        cb._record_failure()
        cb._record_failure()
        assert cb.state == CircuitState.OPEN
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb._failure_count == 0


class TestCircuitBreakerTransitions:
    """Tests for state transitions."""

    def test_open_to_half_open_after_timeout(self):
        cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout=1.0)
        cb._record_failure()
        cb._record_failure()
        assert cb.state == CircuitState.OPEN

        # Simulate time passing by backdating the last failure
        cb._last_failure_time = time.monotonic() - 2.0
        assert cb.state == CircuitState.HALF_OPEN

    def test_half_open_to_closed_on_success(self):
        cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout=0.0)
        cb._record_failure()
        cb._record_failure()
        # recovery_timeout=0 → immediately goes to half_open
        assert cb.state == CircuitState.HALF_OPEN

        cb._record_success()
        assert cb.state == CircuitState.CLOSED

    def test_half_open_to_open_on_failure(self):
        cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout=60.0)
        cb._record_failure()
        cb._record_failure()
        # Backdate to trigger half_open
        cb._last_failure_time = time.monotonic() - 120.0
        assert cb.state == CircuitState.HALF_OPEN

        # A failure in half_open re-opens the circuit
        cb._record_failure()
        assert cb._state == CircuitState.OPEN


class TestCircuitBreakerCall:
    """Tests for synchronous call method."""

    def test_call_passes_through_when_closed(self):
        cb = CircuitBreaker("test")
        result = cb.call(lambda: 42)
        assert result == 42

    def test_call_rejects_when_open(self):
        cb = CircuitBreaker("test", failure_threshold=1)
        cb._record_failure()
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(lambda: 42)

    def test_call_records_failure_on_exception(self):
        cb = CircuitBreaker("test", failure_threshold=2)

        with pytest.raises(ValueError):
            cb.call(_raise_value_error)

        assert cb._failure_count == 1

    def test_call_records_success(self):
        cb = CircuitBreaker("test")
        cb._failure_count = 3  # simulate prior failures
        cb.call(lambda: "ok")
        assert cb._failure_count == 0


class TestCircuitBreakerCallAsync:
    """Tests for async call_async method."""

    @pytest.mark.asyncio
    async def test_async_call_passes_through_when_closed(self):
        cb = CircuitBreaker("test")
        result = await cb.call_async(_async_return, 42)
        assert result == 42

    @pytest.mark.asyncio
    async def test_async_call_rejects_when_open(self):
        cb = CircuitBreaker("test", failure_threshold=1)
        cb._record_failure()
        with pytest.raises(CircuitBreakerOpenError):
            await cb.call_async(_async_return, 1)

    @pytest.mark.asyncio
    async def test_async_call_records_failure(self):
        cb = CircuitBreaker("test", failure_threshold=5)

        with pytest.raises(RuntimeError):
            await cb.call_async(_async_raise)

        assert cb._failure_count == 1

    @pytest.mark.asyncio
    async def test_async_call_records_success(self):
        cb = CircuitBreaker("test")
        cb._failure_count = 2
        await cb.call_async(_async_return, "ok")
        assert cb._failure_count == 0


class TestCircuitBreakerOpenErrorAfterRepeatedCallFailures:
    """Integration: calling through CB until it opens."""

    def test_cb_opens_after_n_failed_calls(self):
        cb = CircuitBreaker("test", failure_threshold=3)

        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(_raise_value_error)

        assert cb.state == CircuitState.OPEN

        with pytest.raises(CircuitBreakerOpenError):
            cb.call(lambda: "should not run")

    @pytest.mark.asyncio
    async def test_cb_opens_after_n_failed_async_calls(self):
        cb = CircuitBreaker("test", failure_threshold=3)

        for _ in range(3):
            with pytest.raises(RuntimeError):
                await cb.call_async(_async_raise)

        assert cb.state == CircuitState.OPEN

        with pytest.raises(CircuitBreakerOpenError):
            await cb.call_async(_async_return, 1)


# ==================== HELPERS ====================


def _raise_value_error() -> None:
    raise ValueError("test error")


async def _async_return(value: object) -> object:
    return value


async def _async_raise() -> None:
    raise RuntimeError("async test error")
