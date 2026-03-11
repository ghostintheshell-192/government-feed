# Catalog Browse & Search UI

**Status**: planned
**Milestone**: M4a-Feed-Infrastructure
**Priority**: should-have
**Depends on**: [source-catalog-subscriptions](source-catalog-subscriptions.md)
**Related ADR**: [ADR-005 Geographic Levels](../../reference/decisions/005-geographic-levels-navigation.md), [ADR-007 Catalog-Subscription Model](../../reference/decisions/007-catalog-subscription-model.md)

## Summary

Frontend page for browsing, searching, and subscribing to sources from the global catalog. Organized by geographic level (ADR-005) with tag-based filtering.

## User Stories

- As a user, I want to browse available feeds organized by geographic proximity
- As a user, I want to search the catalog by name, tag, or category
- As a user, I want to subscribe to a catalog source with one click
- As a user, I want to see which catalog sources I already follow

## Design

### Page structure

- **Navigation**: Accessible from sidebar/nav as "Scopri" / "Discover"
- **Layout**: Geographic level tabs or accordion (Local → National → Continental → Global)
- **Each level shows**:
  - Count of available vs subscribed sources
  - Source cards with name, description, tags, subscribe button
  - "Already subscribed" indicator for sources the user follows
- **Search bar**: Filters across all levels by name, description, tags
- **Tag filter**: Clickable tag chips to filter within a level

### Source card

```
┌─────────────────────────────────────────┐
│  📰 Banca d'Italia                      │
│  Bollettini economici e statistiche     │
│  🏷 economia  banca-centrale            │
│  🌍 Nazionale · IT                      │
│                          [+ Sottoscrivi] │
└─────────────────────────────────────────┘
```

For already-subscribed sources, the button changes to a muted "Sottoscritto" with an unsubscribe option.

### Empty states

- Level with no sources: "Nessuna fonte disponibile per questo livello. Aggiungine una!"
- Search with no results: "Nessun risultato per [query]"
- Level with few sources: "N fonti disponibili — Scoprine altre" (links to feed discovery when available)

## Technical Notes

- Uses `GET /api/catalog` endpoint with query params: `geographic_level`, `tags`, `search`, `limit`, `offset`
- Subscription state from `GET /api/sources` (already subscribed IDs)
- Subscribe/unsubscribe via `POST/DELETE /api/catalog/{id}/subscribe`
- Client-side filtering for responsiveness, server-side for pagination

## Acceptance Criteria

- [ ] Catalog page accessible from main navigation
- [ ] Sources grouped by geographic level
- [ ] Search filters by name, description, tags
- [ ] Tag chips for filtering within a level
- [ ] One-click subscribe/unsubscribe
- [ ] Visual distinction between subscribed and available sources
- [ ] Responsive layout (mobile-friendly)
- [ ] Empty states for all scenarios
