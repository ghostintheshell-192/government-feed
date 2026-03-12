---
type: refactor
priority: medium
status: resolved
discovered: 2026-03-07
resolved: 2026-03-11
related: []
related_decision: 001-clean-architecture.md
report: null
---

# FeedParserService bypasses Unit of Work pattern

## Problem

`FeedParserService` received a raw SQLAlchemy `Session` and performed direct database queries and commits, bypassing the Repository and Unit of Work patterns established by ADR-001.

Multiple callers created the service by accessing the internal `_db` attribute:

```python
# In routes/sources.py:151 and routes/admin.py:196
parser = FeedParserService(uow._db)

# In scheduler.py:83-84
db = SessionLocal()
parser = FeedParserService(db)
```

The service then directly queried `NewsItem` models, created model instances, and called `session.commit()` — all operations that should go through `INewsRepository` and `UnitOfWork`.

## Impact

- Broke the Clean Architecture dependency rule (infrastructure service depended on ORM models directly)
- Made FeedParserService untestable without a real database session
- Duplicated repository logic (e.g., duplicate checking by content_hash)
- Code comment acknowledged the issue: "FeedParserService still uses db directly"

## Recommended Approach

Refactor `FeedParserService` to accept `UnitOfWork` instead of `Session`. Use `uow.news_repository` for queries and `uow.source_repository` for source updates. Let the caller manage commit/rollback.

## Resolution (2026-03-11)

### Changes Made

1. **`FeedParserService`** — Constructor now accepts `UnitOfWork` instead of `Session`. Uses `uow.news_repository.get_by_content_hash()` for dedup checks, `uow.news_repository.add()` for inserts, `uow.source_repository.update()` for last_fetched updates, and `uow.commit()`/`uow.rollback()` for transactions.

2. **Route callers** (`sources.py`, `admin.py`) — Now pass `uow` directly instead of `uow._db`.

3. **Scheduler** — Creates `UnitOfWork(db)` from its `SessionLocal()` sessions. Uses `uow.source_repository.get_active_sources()` instead of direct `db.query(Source)`.

4. **Tests** — Updated `test_feed_parser.py` and `test_scheduler.py` to mock `UnitOfWork` instead of raw sessions.

### Remaining Notes

- `parse_and_import()` is still synchronous — async conversion deferred (low priority, works fine as-is)
- Scheduler's `_cleanup_old_news()` still uses `db.query(NewsItem)` directly for the delete query. This is acceptable: it's a bulk delete operation that doesn't map well to the repository pattern.
