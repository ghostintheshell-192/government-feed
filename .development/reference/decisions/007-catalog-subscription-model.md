# ADR-007: Catalog-Subscription Model for Source Management

**Date**: 2026-03-11
**Status**: Accepted
**Impact**: significant

## Context

Government Feed currently treats every `Source` as both "a known feed" and "something the user actively follows". There is no separation between a catalog of available feeds and the user's personal selection. This creates several problems:

1. **No browsable catalog**: Users can only see sources they've already added. There's no way to discover and subscribe to feeds from within the app.
2. **Starter packs impossible**: Pre-populated feed bundles (ADR-005) need a catalog to draw from.
3. **Multi-user preparation**: When M5 adds multiple users, each needs their own subscriptions to a shared pool of sources.
4. **Bulk import ambiguity**: Crawling 1000+ feeds for the catalog shouldn't mean all are actively polled.

## Decision

Adopt a **single Source table + subscriptions pivot table** model:

```
Source (the global catalog — all known feeds)
  id, name, feed_url, description, source_type, category,
  geographic_level, country_code, region, tags,
  is_curated, verified_at,
  created_at, updated_at

Subscription (who follows what)
  id, user_id, source_id (FK → Source),
  is_active, update_frequency_override,
  added_at
```

### Key behaviors

- **Source = catalog entry**. Every known feed is a Source, whether curated or user-added.
- **Subscription = user's choice**. A user subscribing to a source creates a Subscription row. For now, `user_id` is always 1 (single-user). M5 adds real user IDs.
- **Polling scope**: The scheduler only polls sources that have at least one active subscription (JOIN on subscriptions).
- **Custom sources**: When a user adds a feed by URL that isn't in the catalog, a new Source is created with `is_curated=False`, and a Subscription is automatically added.
- **Catalog updates propagate**: If a catalog source's URL is corrected, all subscribers benefit immediately (no data duplication).

### Alternatives considered

- **Option A (two tables: CatalogSource + UserSource)**: Cleaner conceptual separation, but duplicates data (name, URL copied on subscribe), catalog URL updates don't propagate, complex migration splitting the current Source table, custom sources need dual paths. Rejected due to unnecessary complexity.
- **Option B (flag on Source: is_subscribed)**: Simplest, but doesn't scale to multi-user and conflates catalog metadata with user state. Rejected.

## Rationale

- **Zero data duplication**: Source data lives in one place, subscriptions are just links.
- **Minimal migration**: Current Source table stays, gains catalog fields. New Subscription table is small. `NewsItem.source_id` doesn't change.
- **M5-ready**: Adding multi-user means adding rows to Subscription with different `user_id` values.
- **Proven pattern**: Classic many-to-many pivot table — well-understood, well-supported by SQLAlchemy.

## Consequences

- **Positive**: Enables catalog browsing, starter packs, bulk import without auto-polling, natural multi-user path.
- **Negative**: Source table grows with catalog fields (geographic_level, tags) that user-added sources may not have. Scheduler queries become slightly more complex (join with subscriptions).
- **Migration**: Add new fields to Source, create Subscription table, create subscriptions for all existing active sources (data migration).
- **Supersedes**: Reshapes how starter packs, feed registry, and geographic navigation interact with the data layer.

## Related

- [ADR-005: Geographic Levels Navigation](005-geographic-levels-navigation.md) — defines the geographic fields on Source
- Spec: [source-catalog-subscriptions](../../specs/planned/source-catalog-subscriptions.md) — implementation spec
- Spec: [starter-packs](../../specs/backlog/starter-packs.md) — depends on this model
