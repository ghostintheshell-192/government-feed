---
type: bug
priority: medium
status: open
discovered: 2026-03-07
related: []
related_decision: null
report: null
---

# Missing foreign key constraint from news_items to sources

## Problem

The `news_items.source_id` column has no `ForeignKey` constraint to `sources.id` in the SQLAlchemy model (`models.py`). This means:

1. Deleting a source leaves orphaned news items in the database
2. No referential integrity — news items can reference non-existent sources
3. No cascade delete behavior

## Current State

```python
# models.py - NewsItemModel
source_id = Column(Integer, nullable=False, index=True)  # no ForeignKey!
```

## Recommended Approach

Add the foreign key with cascade delete:

```python
source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
```

This requires a database migration (Alembic), which is configured but not yet actively used. This could be the first real migration.

## Notes

- SQLite supports foreign keys but they must be explicitly enabled with `PRAGMA foreign_keys = ON`
- Existing data may have orphaned records that need cleanup before adding the constraint
- This should be coordinated with actually activating Alembic migrations
