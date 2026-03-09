# Error Resilience

**Status**: implemented
**Milestone**: M2-Production
**Priority**: should-have
**Depends on**: [feed-parsing](../implemented/feed-parsing.md), [ai-summarization](../implemented/ai-summarization.md)

## Summary

Retry policies, circuit breaker pattern, and graceful degradation for external service calls (feed fetching, Ollama AI), ensuring the system remains functional even when dependencies fail.

## User Stories

- As a user, I want feed imports to retry automatically on transient network failures
- As a user, I want the system to keep working even when AI is temporarily unavailable
- As a user, I want to see clear error status when something is wrong

## Requirements

### Functional

- [ ] Retry with exponential backoff for feed fetching (transient failures)
- [ ] Retry with backoff for Ollama API calls
- [ ] Circuit breaker for external services (stop calling after N consecutive failures)
- [ ] Graceful degradation: save news without summary when AI is down
- [ ] Graceful degradation: skip unreachable feeds without blocking others
- [ ] Structured error logging with context (URL, attempt number, error type)

### Non-Functional

- Resilience: System operates in degraded mode rather than failing entirely
- Performance: Retry delays don't block other operations (async)
- Observability: Failed operations clearly visible in logs

## Technical Notes

- Library: `tenacity` for retry policies (well-maintained, async-compatible)
- Circuit breaker: custom implementation or `pybreaker` library
- Retry configuration:
  - Feed fetch: 3 retries, exponential backoff (1s, 2s, 4s)
  - Ollama API: 2 retries, exponential backoff (2s, 4s)
  - Web scraping: 2 retries, exponential backoff (1s, 2s)
- Circuit breaker thresholds:
  - Open after 5 consecutive failures
  - Half-open after 60 seconds
  - Reset after 1 successful call

## Acceptance Criteria

- [ ] Transient feed failures are retried automatically
- [ ] AI unavailability doesn't prevent news import
- [ ] Circuit breaker prevents cascading failures
- [ ] All retry attempts are logged with context
- [ ] Error status is visible for each source
