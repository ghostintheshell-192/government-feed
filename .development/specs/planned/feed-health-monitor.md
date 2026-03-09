# Feed Health Monitor

**Status**: planned
**Milestone**: M4a-Feed-Infrastructure
**Priority**: must-have
**Depends on**: [background-workers](../implemented/background-workers.md), [error-resilience](../implemented/error-resilience.md), [feed-discovery-automated](feed-discovery-automated.md)

## Summary

Intelligent feed health tracking that detects dead/migrated feeds, escalates through severity levels, and triggers automatic URL recovery via the discovery service — replacing the current fire-and-forget health check with a stateful, self-healing system.

## User Stories

- As a user, I want broken feeds to be detected and recovered automatically without my intervention
- As a user, I want to see the health status of each feed source at a glance
- As a user, I want to be notified when a feed has been automatically migrated to a new URL
- As a user, I want feeds that are permanently dead to be deactivated so they don't waste resources

## Context

The current `FeedScheduler._health_check_sources` does a HEAD request every 6h and logs a warning on failure. It does not:

- Track failure history in the database
- Escalate through severity levels
- Attempt recovery
- Deactivate permanently broken feeds
- Distinguish between transient failures and permanent migration

This spec replaces that behavior with a stateful health monitoring system.

## Requirements

### Functional

- [ ] Track consecutive failure count per source in the database
- [ ] Track health status per source: `healthy`, `degraded`, `unhealthy`, `dead`, `migrated`
- [ ] Validate feed content on health check (not just HTTP HEAD — parse a few entries)
- [ ] Escalation ladder based on consecutive failures:
  - 1-2 failures → `degraded` (transient, keep polling normally)
  - 3-5 failures → `unhealthy` (reduce polling frequency, log warning)
  - 6+ failures → `dead` (trigger auto-recovery, then deactivate if recovery fails)
- [ ] Auto-recovery: when a feed reaches `dead`, trigger a discovery search for the new URL
- [ ] If recovery finds a valid new URL: update the source record, set status to `migrated`
- [ ] If recovery fails: set `is_active = False`, log clearly
- [ ] Record recovery history (old URL → new URL, when, how)
- [ ] Expose health status via existing REST API (`GET /api/sources` should include health info)
- [ ] Manual health check trigger via API endpoint

### Non-Functional

- Reliability: Health checks must not block feed polling or API responses
- Resilience: Health check failures themselves are handled gracefully (no cascading)
- Observability: All state transitions logged with structured context
- Efficiency: Health checks use connection pooling (single httpx client per batch)

## Technical Design

### Database Changes

Add columns to `Source` model:

```python
# New columns on Source
health_status = Column(String(20), default="healthy")  # healthy|degraded|unhealthy|dead|migrated
consecutive_failures = Column(Integer, default=0)
last_health_check = Column(DateTime, nullable=True)
last_healthy_at = Column(DateTime, nullable=True)
previous_feed_url = Column(String(500), nullable=True)  # set on migration
```

Create Alembic migration for these columns.

### Health Check Logic

```text
Every 6 hours (existing schedule):
  for each active source:
    1. GET feed_url (with timeout)
    2. If success → parse with feedparser, verify ≥1 entry
       → reset consecutive_failures to 0, set healthy
    3. If failure (HTTP error, timeout, empty feed):
       → increment consecutive_failures
       → update health_status based on escalation ladder
       → if status becomes "dead":
           trigger_auto_recovery(source)
```

### Auto-Recovery Flow

```text
trigger_auto_recovery(source):
  1. Extract institution name/domain from source.name and source.feed_url
  2. Call FeedDiscoveryService.search(query) with Exa
  3. If Exa fails or returns no results → try Brave Search as fallback
  4. Validate candidates with FeedDiscoveryService._validate_feed()
  5. If valid feed found:
     → source.previous_feed_url = source.feed_url
     → source.feed_url = new_url
     → source.health_status = "migrated"
     → source.consecutive_failures = 0
     → log migration event
  6. If no valid feed found:
     → source.is_active = False
     → log deactivation
```

### Integration Points

- **FeedScheduler**: Replace `_health_check_sources` with new `HealthMonitorService`
- **FeedDiscoveryService**: Used for auto-recovery (search + validate)
- **REST API**: Extend `GET /api/sources` response to include health fields
- **Resilience**: Use existing retry decorators for HTTP calls

### Health Status Lifecycle

```text
healthy ←→ degraded → unhealthy → dead → migrated (if recovery succeeds)
                                       → inactive  (if recovery fails)

Any state → healthy (on successful health check)
```

## Acceptance Criteria

- [ ] Consecutive failures are tracked in the database per source
- [ ] Health status transitions follow the escalation ladder
- [ ] Dead feeds trigger automatic recovery via discovery service
- [ ] Successfully recovered feeds are updated with new URL and marked as migrated
- [ ] Unrecoverable feeds are deactivated
- [ ] Health status is visible in API responses
- [ ] All state transitions produce structured log entries
- [ ] Health checks do not degrade API performance

## Open Questions

- Should we keep a separate `feed_health_log` table for audit history, or is structured logging sufficient?
- Should `degraded` feeds have reduced polling frequency, or keep normal frequency?
- Should there be a UI notification when a feed is migrated or deactivated?
