---
type: refactor
priority: medium
status: open
discovered: 2026-03-07
related: []
related_decision: 001-clean-architecture.md
report: null
---

# FeedParserService bypasses Unit of Work pattern

## Problem

`FeedParserService` receives a raw SQLAlchemy `Session` and performs direct database queries and commits, bypassing the Repository and Unit of Work patterns established by ADR-001.

In `main.py:215`, the endpoint creates the service by accessing the internal `_db` attribute:

```python
parser = FeedParserService(uow._db)
```

The service then directly queries `NewsItemModel`, creates model instances, and calls `session.commit()` — all operations that should go through `INewsRepository` and `UnitOfWork`.

## Impact

- Breaks the Clean Architecture dependency rule (infrastructure service depends on ORM models directly)
- Makes FeedParserService untestable without a real database session
- Duplicates repository logic (e.g., duplicate checking by content_hash)
- Code comment acknowledges the issue: "FeedParserService still uses db directly"

## Recommended Approach

Refactor `FeedParserService` to accept `UnitOfWork` instead of `Session`. Use `uow.news_repository` for queries and `uow.source_repository` for source updates. Let the caller manage commit/rollback.

## Notes

- The `parse_and_import()` method is synchronous despite the rest of the API being async
- Consider making it async as part of this refactor
- Scheduler also creates its own sessions for polling — same pattern issue
