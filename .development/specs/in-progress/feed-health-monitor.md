# Feed Health Monitor

**Status**: in-progress
**Milestone**: M4a-Feed-Infrastructure
**Priority**: must-have
**Depends on**: [background-workers](../implemented/background-workers.md), [error-resilience](../implemented/error-resilience.md)

## Summary

Stateful feed health tracking that detects broken feeds, escalates through severity levels, and exposes health status to the user — replacing the current fire-and-forget HEAD check with persistent tracking and clear visibility.

## User Stories

- As a user, I want to see the health status of each feed source at a glance
- As a user, I want broken feeds to be clearly flagged so I know which ones need attention
- As a user, I want feeds that are permanently dead to be deactivated so they don't waste resources

## Context

The current `FeedScheduler._health_check_sources` does a HEAD request every 6h and logs a warning on failure. It does not:

- Track failure history in the database
- Escalate through severity levels
- Deactivate permanently broken feeds
- Distinguish between transient failures and persistent problems
- Expose health status to the user

This spec replaces that behavior with a stateful health monitoring system.

## Requirements

### Functional

- [ ] Track consecutive failure count per source in the database
- [ ] Track health status per source: `healthy`, `degraded`, `unhealthy`, `dead`
- [ ] Validate feed content on health check (not just HTTP HEAD — parse a few entries)
- [ ] Escalation ladder based on consecutive failures:
  - 1-2 failures → `degraded` (transient, keep polling normally)
  - 3-5 failures → `unhealthy` (reduce polling frequency, log warning)
  - 6+ failures → `dead` (deactivate feed, `is_active = False`)
- [ ] On successful check: reset `consecutive_failures` to 0, set `healthy`
- [ ] Expose health status via existing REST API (`GET /api/sources` should include health info)
- [ ] Manual health check trigger via API endpoint (`POST /api/sources/{id}/health-check`)
- [ ] Bulk health check endpoint (`POST /api/sources/health-check`)
- [ ] Health status visible in frontend Sources/Feed page (icon or badge per source)

### Non-Functional

- Reliability: Health checks must not block feed polling or API responses
- Resilience: Health check failures themselves are handled gracefully (no cascading)
- Observability: All state transitions logged with structured context
- Efficiency: Health checks use connection pooling (single httpx client per batch)

## Technical Design

### Database Changes

Add columns to `Source` model:

```python
health_status = Column(String(20), default="healthy")  # healthy|degraded|unhealthy|dead
consecutive_failures = Column(Integer, default=0)
last_health_check = Column(DateTime, nullable=True)
last_healthy_at = Column(DateTime, nullable=True)
```

Create Alembic migration for these columns.

### Health Check Logic

```text
Every 6 hours (existing schedule):
  for each active source:
    1. GET feed_url (with timeout, follow redirects)
    2. If success → parse with feedparser, verify ≥1 entry
       → reset consecutive_failures to 0, set healthy, update last_healthy_at
    3. If failure (HTTP error, timeout, parse error, empty feed):
       → increment consecutive_failures
       → update health_status based on escalation ladder
       → if status becomes "dead": set is_active = False
```

### Health Status Lifecycle

```text
healthy ←→ degraded → unhealthy → dead (is_active = False)

Any non-dead state → healthy (on successful health check)
```

### Integration Points

- **FeedScheduler**: Replace `_health_check_sources` with new `HealthMonitorService`
- **REST API**: Extend `GET /api/sources` response to include health fields
- **Frontend**: Show health badge/icon per source in Sources page
- **Resilience**: Use existing retry decorators for HTTP calls

## Acceptance Criteria

- [ ] Consecutive failures are tracked in the database per source
- [ ] Health status transitions follow the escalation ladder
- [ ] Dead feeds are deactivated (`is_active = False`)
- [ ] Health status is visible in API responses
- [ ] Health status is visible in frontend (Sources page)
- [ ] Manual health check works (single source + bulk)
- [ ] All state transitions produce structured log entries
- [ ] Health checks do not degrade API performance

## Out of Scope (see feed-auto-recovery spec)

- Automatic URL recovery via redirect following or feed discovery
- Migration tracking (`previous_feed_url`, `migrated` status)
- Recovery history logging
