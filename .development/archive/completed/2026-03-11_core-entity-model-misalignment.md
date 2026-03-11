---
type: refactor
priority: high
status: resolved
discovered: 2026-03-08
resolved: 2026-03-11
related: [feedparser-bypasses-uow.md]
related_decision: reference/decisions/001-clean-architecture.md
report: null
---

# Core Entity / Infrastructure Model Misalignment

## Problem

The domain entity `Source` in `core/entities.py` and the SQLAlchemy model `Source` in `infrastructure/models.py` have diverged significantly. The core entity is effectively unused — all code works directly with the infrastructure model, violating the Clean Architecture dependency rule (ADR-001).

## Analysis

### Field Comparison (before resolution)

| Core Entity (`core/entities.py`) | DB Model (`infrastructure/models.py`) | Match |
|---|---|---|
| `id` | `id` | same |
| `name` | `name` | same |
| `url` | `feed_url` | different name |
| `feed_type` ("rss", "atom", "web_scraping") | `source_type` (default "RSS") | different name + values |
| `is_active` | `is_active` | same |
| `country` ("IT") | — | missing from model |
| `category` | `category` | same |
| `created_at` | `created_at` | same |
| `updated_at` | `updated_at` | same |
| — | `description` | missing from entity |
| — | `update_frequency_minutes` | missing from entity |
| — | `last_fetched` | missing from entity |

The same issue exists for `NewsItem`: the entity has `blockchain_certificate` and `categories` that don't exist in the model, while the model's field set is the authoritative one.

### Impact

- Core layer is dead code — no service imports or uses core entities
- Repository interfaces (`ISourceRepository`, `INewsRepository`) reference the infrastructure model via `TYPE_CHECKING`, not the core entity
- Adding new domain concepts (health status, discovery) will deepen the misalignment
- New developers would be confused by two competing `Source` definitions

### Root Cause

The entities were likely written early as a design sketch, then the infrastructure models evolved independently as the actual implementation. No mapping layer was ever created between them.

## Possible Solutions

- **Option A: Align entity to model, add mapping layer** — Update `core/entities.py` to match reality, create mappers in infrastructure. Services use entities, repositories translate. *Pro*: Clean Architecture as intended. *Con*: Significant refactoring, mapping boilerplate.

- **Option B: Make entity the source of truth** — Derive the SQLAlchemy model from the entity fields. *Pro*: Domain-driven. *Con*: Same effort as A, plus SQLAlchemy model needs rework.

- **Option C: Remove core entities, use models directly** — Accept that for a single-user app, the indirection isn't worth it. Keep interfaces in core, but let them reference models. *Pro*: Pragmatic, minimal code. *Con*: Abandons Clean Architecture separation, harder to change DB later.

## Resolution (2026-03-11)

**Approach taken: Option A pragmatic (duck typing, no explicit mapping layer).**

### Changes Made

1. **`core/entities.py`** — Aligned Source and NewsItem dataclasses to match infrastructure model fields exactly:
   - Source: `url` → `feed_url`, `feed_type` → `source_type`, added `description`, `update_frequency_minutes`, `last_fetched`, removed `country`
   - NewsItem: removed `blockchain_certificate`, `categories`, `VerificationStatus` enum; `verification_status` is now a plain string
   - Removed `Category` entity (no corresponding model/table)
   - Kept `update_content_hash()` domain method

2. **`core/repositories/`** — Fixed dependency violation:
   - `ISourceRepository` and `INewsRepository` now import from `core.entities` directly (no `TYPE_CHECKING` from infrastructure)

3. **Tests** — Updated `test_entities.py` to match new field names and removed dead code tests

### Design Decision

No explicit mapping layer was added. SQLAlchemy models in `infrastructure/models.py` have the same fields as the core entities, so concrete repositories return model instances that satisfy the entity interface via duck typing. This avoids boilerplate while maintaining the Clean Architecture dependency rule: **core has no knowledge of infrastructure**.

### Remaining Related Issues

- `feedparser-bypasses-uow.md` — FeedParserService still uses `db.query()` directly instead of going through repository/UoW. Separate concern, not blocked by this refactoring.

## Related Documentation

- **Architecture Decision**: [ADR-001: Clean Architecture](../reference/decisions/001-clean-architecture.md)
- **Related Issues**: [FeedParser bypasses UoW](feedparser-bypasses-uow.md)
- **Code Locations**:
  - `backend/src/core/entities.py` — domain entities
  - `backend/src/infrastructure/models.py` — SQLAlchemy models
  - `backend/src/core/repositories/source_repository.py` — interface (now imports from core)
  - `backend/src/core/repositories/news_repository.py` — interface (now imports from core)
