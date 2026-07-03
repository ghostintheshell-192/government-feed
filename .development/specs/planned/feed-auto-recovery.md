# Feed Auto-Recovery

**Status**: planned
**Milestone**: M4a-Feed-Infrastructure
**Priority**: should-have
**Depends on**: [feed-health-monitor](../in-progress/feed-health-monitor.md), [feed-discovery-automated](feed-discovery-automated.md)

## Summary

Automatic feed URL recovery for dead or broken feeds. When the health monitor detects a dead feed, this system attempts to find the new URL through redirect following, same-domain discovery, and optionally external search — then offers the user the option to migrate.

## User Stories

- As a user, I want the system to suggest a new URL when a feed moves
- As a user, I want to approve or reject a proposed URL migration
- As a user, I want to see the recovery history (old URL → new URL)

## Context

The health monitor (separate spec) tracks feed health and deactivates dead feeds. This spec adds the recovery layer on top: when a feed is dead, try to find where it moved.

## Requirements

### Functional

- [ ] Recovery strategy ladder (tried in order):
  1. **HTTP redirect following**: GET the old URL, if 301 → use the new Location
  2. **Same-domain discovery**: fetch homepage of the domain, find `<link rel="alternate" type="application/rss+xml">` tags
  3. **Common path probing**: try `/feed`, `/rss`, `/atom.xml`, `/feed.xml`, `/rss.xml` on the domain
  4. **Search API fallback** (optional): use FeedDiscoveryService (Exa/Brave) to search by institution name
- [ ] Each candidate URL is validated (HTTP GET + feedparser parse)
- [ ] Add `previous_feed_url` column to Source for migration tracking
- [ ] Add `migrated` health status (extends health monitor's status set)
- [ ] Recovery results presented to user for approval (not auto-applied)
- [ ] API endpoint: `POST /api/sources/{id}/recover` → returns candidate URLs
- [ ] Frontend: "Recover" button on dead feeds, shows candidates, user picks one

### Non-Functional

- Privacy: local recovery strategies (redirect, domain scan, path probing) are preferred over external APIs
- Resilience: recovery attempts have timeouts and don't block other operations
- Observability: recovery attempts and outcomes are logged

## Technical Design

### Recovery Service

```python
class FeedRecoveryService:
    async def find_candidates(self, source: Source) -> list[RecoveryCandidate]:
        """Try recovery strategies in order, return validated candidates."""

    async def _try_redirect(self, url: str) -> str | None: ...
    async def _try_domain_discovery(self, url: str) -> list[str]: ...
    async def _try_common_paths(self, url: str) -> list[str]: ...
    async def _validate_candidate(self, url: str) -> bool: ...
```

### Database Changes

Add to `Source` model:

```python
previous_feed_url = Column(String(500), nullable=True)  # set on migration
```

Extend `health_status` to include `migrated`.

### API

- `POST /api/sources/{id}/recover` → `{ candidates: [{ url, strategy, entry_count }] }`
- `POST /api/sources/{id}/migrate` → `{ new_url }` (user confirms migration)

### Frontend

- Dead feeds show a "Recover" button
- Click triggers recovery, shows candidate list with strategy label
- User selects one → calls migrate endpoint
- Source card updates to show `migrated` badge with previous URL

## Acceptance Criteria

- [ ] Redirect following detects 301 moves
- [ ] Domain discovery finds `<link rel="alternate">` feeds
- [ ] Common path probing finds feeds at standard locations
- [ ] All candidates are validated before being presented
- [ ] User must approve migration (no auto-apply)
- [ ] Migration records old URL in `previous_feed_url`
- [ ] Recovery history is visible in UI

## Open Questions

- Should recovery run automatically when health monitor marks a feed as dead, or only on user request?
- Should we cache recovery results to avoid repeated scans?
- Should external search API recovery be opt-in in settings?
