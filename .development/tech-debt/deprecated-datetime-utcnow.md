---
type: code-quality
priority: high
status: open
discovered: 2026-03-07
related: []
related_decision: null
report: null
---

# Deprecated datetime.utcnow() usage throughout codebase

## Problem

Python 3.12+ deprecates `datetime.datetime.utcnow()` in favor of timezone-aware `datetime.datetime.now(datetime.UTC)`. The test suite produces 77 deprecation warnings from this, spread across entities, infrastructure services, and tests.

## Affected Files

- `backend/src/core/entities.py` — NewsItem dataclass defaults and `mark_as_verified()`
- `backend/src/infrastructure/feed_parser.py` — `_parse_date()` fallback, `parse_and_import()` fetched_at/last_fetched
- `backend/src/infrastructure/scheduler.py` — `_poll_all_feeds()` elapsed check, `_cleanup_old_news()` cutoff
- `backend/src/infrastructure/models.py` — SQLAlchemy column defaults (`default=datetime.utcnow`)
- `backend/tests/conftest.py` — Test fixtures
- `backend/tests/unit/test_scheduler.py` — Test assertions
- `backend/tests/unit/test_feed_parser.py` — Test assertions

## Possible Solutions

- **Option A**: Global search-and-replace `datetime.utcnow()` with `datetime.now(UTC)`, import `UTC` from `datetime`. Simple, mechanical change.
- **Option B**: Create a `backend/src/core/clock.py` utility with `utc_now()` function for consistent usage and easier testing/mocking.

## Recommended Approach

Option A — direct replacement. The codebase is small enough that a utility abstraction isn't warranted. For SQLAlchemy model defaults, use `lambda: datetime.now(UTC)`.

## Notes

- This will be a breaking change in a future Python version (scheduled for removal)
- All 77 warnings are from this single deprecation
- The fix is mechanical and safe — no logic changes required
