# Source Catalog & Subscriptions

**Status**: planned
**Milestone**: M4a-Feed-Infrastructure
**Priority**: must-have
**Depends on**: (none — this is the foundation for other M4a features)
**Related ADR**: [ADR-007 Catalog-Subscription Model](../../reference/decisions/007-catalog-subscription-model.md)

## Summary

Separate the concept of "known feed" (catalog) from "user follows this feed" (subscription) using a pivot table. This enables catalog browsing, starter packs, and prepares for multi-user support.

## Data Model Changes

### Source table — new fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `geographic_level` | Enum (LOCAL, NATIONAL, CONTINENTAL, GLOBAL) | NULL | From ADR-005 |
| `country_code` | String(2) | NULL | ISO 3166-1 alpha-2, optional for GLOBAL |
| `region` | String(100) | NULL | Optional, relevant for LOCAL |
| `tags` | JSON (list of strings) | [] | Freeform tags for filtering |
| `is_curated` | Boolean | False | True for catalog-imported sources |
| `verified_at` | DateTime | NULL | Last time feed URL was verified working |

### New table: Subscription

| Field | Type | Notes |
|-------|------|-------|
| `id` | Integer PK | Auto-increment |
| `user_id` | Integer | Default 1 (single-user), FK to users table in M5 |
| `source_id` | Integer FK → Source | Required |
| `is_active` | Boolean | Default True |
| `update_frequency_override` | Integer | NULL = use source default |
| `added_at` | DateTime | When user subscribed |

**Constraints**: UNIQUE(user_id, source_id)

### Core entity updates

Add corresponding fields to `core/entities.py`:
- `Source`: geographic_level, country_code, region, tags, is_curated, verified_at
- New `Subscription` dataclass

## Migration

1. Add new columns to Source (all nullable, non-breaking)
2. Create Subscription table
3. Data migration: for every existing Source where `is_active=True`, create a Subscription(user_id=1, source_id=id, is_active=True)
4. Scheduler: change polling query from `Source.is_active` to JOIN with active subscriptions

## API Changes

### Modified endpoints

- `GET /api/sources` — returns only subscribed sources (current behavior preserved)
- `POST /api/sources` — creates Source + Subscription in one step (current behavior preserved)
- `DELETE /api/sources/{id}` — deletes Subscription, not the Source itself (catalog entry persists)

### New endpoints

- `GET /api/catalog` — browse all sources (paginated, filterable by geographic_level, tags, search)
- `POST /api/catalog/{source_id}/subscribe` — subscribe to a catalog source
- `DELETE /api/catalog/{source_id}/subscribe` — unsubscribe (same as deleting subscription)
- `GET /api/catalog/stats` — counts by geographic level, tag cloud

## Frontend Changes

- New "Discover" / "Catalog" page: browse available sources by geographic level and tags
- Source management page: show subscribed sources with unsubscribe option
- "Add source" flow: if URL matches a catalog source, subscribe to it instead of creating duplicate

## Scheduler Impact

Current:
```python
sources = db.query(Source).filter(Source.is_active == True)
```

After:
```python
sources = (
    db.query(Source)
    .join(Subscription, Subscription.source_id == Source.id)
    .filter(Subscription.user_id == 1, Subscription.is_active == True)
)
```

## Implementation Order

1. Core entities + infrastructure model + Alembic migration
2. Repository + UoW updates (SubscriptionRepository)
3. API endpoints (catalog browse, subscribe/unsubscribe)
4. Scheduler query update
5. Frontend catalog page

## Acceptance Criteria

- [ ] Source model has geographic_level, country_code, region, tags, is_curated, verified_at
- [ ] Subscription table exists with user_id, source_id, is_active
- [ ] Existing sources migrated to have subscriptions
- [ ] `GET /api/sources` returns only subscribed sources
- [ ] `GET /api/catalog` returns all sources with pagination and filters
- [ ] Subscribe/unsubscribe endpoints work
- [ ] Scheduler only polls subscribed sources
- [ ] Deleting a subscription doesn't delete the Source
