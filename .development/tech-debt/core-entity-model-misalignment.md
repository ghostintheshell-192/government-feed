---
type: refactor
priority: high
status: open
discovered: 2026-03-08
related: [feedparser-bypasses-uow.md]
related_decision: reference/decisions/001-clean-architecture.md
report: null
---

# Core Entity / Infrastructure Model Misalignment

## Problem

The domain entity `Source` in `core/entities.py` and the SQLAlchemy model `Source` in `infrastructure/models.py` have diverged significantly. The core entity is effectively unused — all code works directly with the infrastructure model, violating the Clean Architecture dependency rule (ADR-001).

## Analysis

### Field Comparison

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

## Recommended Approach

**Option A** — but pragmatically. The entity becomes the canonical definition of domain fields. The infrastructure model mirrors it for persistence. A thin mapping (factory methods or a simple `to_entity()`/`from_entity()`) bridges them. This sets us up cleanly for the new health monitoring fields.

Do this **before** implementing feed-health-monitor and feed-discovery-automated, as both specs add new fields to Source.

## Notes

- The `Category` entity in core exists but has no corresponding model or table — decide if it's needed
- `NewsItem.blockchain_certificate` in the core entity appears speculative — remove if not planned
- Repository interfaces already import from infrastructure via `TYPE_CHECKING` — this needs fixing as part of the refactoring
- Related: `feedparser-bypasses-uow.md` — fixing the entity/model alignment naturally helps resolve the UoW bypass issue

## Related Documentation

- **Architecture Decision**: [ADR-001: Clean Architecture](../reference/decisions/001-clean-architecture.md)
- **Related Issues**: [FeedParser bypasses UoW](feedparser-bypasses-uow.md)
- **Code Locations**:
  - `backend/src/core/entities.py` — domain entities (lines 18-76)
  - `backend/src/infrastructure/models.py` — SQLAlchemy models (lines 1-45)
  - `backend/src/core/repositories/source_repository.py` — interface imports model (line 7)
  - `backend/src/core/repositories/news_repository.py` — interface imports model (line 8)

---

Investigation Note: Read [ARCHITECTURE.md](../ARCHITECTURE.md) to locate relevant files and understand the architectural context before starting your analysis.
