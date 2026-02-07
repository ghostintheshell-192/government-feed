# Background Workers

**Status**: implemented
**Milestone**: M2-Production
**Priority**: must-have
**Depends on**: [feed-parsing](../implemented/feed-parsing.md)

## Summary

Job scheduling system for automatic feed polling, periodic cleanup, and health checks, eliminating the need for manual feed processing triggers.

## User Stories

- As a user, I want feeds to be updated automatically without manual intervention
- As a user, I want to configure polling frequency per source
- As a user, I want old data to be cleaned up automatically

## Requirements

### Functional

- [x] Automatic feed polling on configurable schedule per source
- [x] Periodic cleanup of old news items (configurable retention)
- [x] Automatic health checks for feed sources (detect broken feeds)
- [x] Job status visibility (last run, next run, success/failure)
- [x] Manual trigger override (run job immediately)
- [x] Graceful shutdown (complete current job before stopping)

### Non-Functional

- Reliability: Jobs survive transient failures without losing state
- Performance: Background jobs don't degrade API response times
- Observability: Job execution logged with timing and outcome

## Technical Notes

- Library candidates: APScheduler (simpler, in-process) or Celery (distributed, more complex)
- APScheduler recommended for single-user/small scale (simpler setup, no broker needed)
- Celery recommended only if distributed processing becomes necessary
- Jobs to implement:
  1. `poll_feeds` — fetch and process all active sources
  2. `cleanup_old_news` — remove items older than retention period
  3. `health_check_sources` — verify feed URLs are still responding
- Integration with existing `FeedParserService` for feed processing

## Open Questions

- APScheduler vs Celery: decide based on expected scale
- Default polling interval per source (15min? 30min? 1h?)
- Retention period for old news (30 days? 90 days? configurable?)

## Acceptance Criteria

- [x] Feeds are polled automatically at configured intervals
- [x] Old news items are cleaned up based on retention policy
- [x] Broken feed sources are detected and flagged
- [x] Background jobs don't block API endpoints
- [x] Job status is visible via API or logs
