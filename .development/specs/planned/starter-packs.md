# Starter Packs — Geographic Navigation

**Status**: planned
**Milestone**: M4a-Feed-Infrastructure
**Priority**: should-have
**Depends on**: catalog-subscriptions (complete), geographic levels on Source (complete)
**Related ADR**: [ADR-005 Geographic Levels Navigation](../../reference/decisions/005-geographic-levels-navigation.md)

## Summary

Reorganize the dashboard around geographic levels using a persistent sidebar with 4 level badges (LOCAL, NATIONAL, CONTINENTAL, GLOBAL). Each badge shows a count of new articles and acts as a pre-filter over the news feed. The original "starter packs as downloadable bundles" concept is replaced by geographic navigation into the existing catalog.

## User Stories

- As a user, I want to see my news organized by geographic proximity at a glance
- As a user, I want to quickly filter to only continental news, or only national, etc.
- As a user, I want to see how many new articles arrived per geographic level
- As a user, I want to configure what "new" means (last X hours/days)
- As a user, I want to select my country so the app knows what "national" means for me

## Design

### Dashboard Layout — Sidebar + Content

```
┌──────────┬─────────────────────────────────────┐
│ LOCAL    │                                     │
│    (2)   │  News cards (filtered by selected   │
│          │  geographic levels)                  │
│ NATIONAL │                                     │
│    (5)   │  Existing filters (search, source,  │
│          │  date) operate on top of geographic  │
│ CONTIN.  │  selection                           │
│   (12)   │                                     │
│          │                                     │
│ GLOBAL   │                                     │
│    (0)   │                                     │
└──────────┴─────────────────────────────────────┘
```

- **Sidebar**: fixed left column (~150px), always visible, 4 large badge-buttons stacked vertically
- **Content area**: full remaining width (replaces current `max-w-4xl` constraint on dashboard)
- **Existing filters**: search, source, date — remain in content area, operate on top of geographic selection

### Badge Behavior

- **Default state**: all levels active, dashboard shows all news (same as current behavior)
- **Click a badge**: toggle — acts as a pre-filter. Can select/deselect multiple levels
- **Visual state**: active badge = primary/filled, inactive = muted/outline
- **Count**: number of "new" articles per level, shown as a small counter on the badge
- **Empty levels**: show count of 0, still clickable (user might subscribe to sources later)

### "New" Articles Definition

Configurable in Settings:
- New setting: "Consider articles as new if published within the last X hours" (default: 24)
- Stored in `settings.json` alongside existing settings
- The badge counters use this threshold to calculate counts

### Country Selection

- New setting in Settings page: "Your country" dropdown (ISO 3166-1 countries)
- Stored in `settings.json`
- Used to determine what "NATIONAL" means — filter catalog suggestions by country_code
- Not required — if unset, national sources from all countries are shown together

### Catalog Integration

The "Esplora catalogo" tab already supports search. With country selected:
- Catalog results can highlight "your country" sources
- Geographic level filter in catalog becomes more meaningful

No onboarding flow for now — just the Settings dropdown. Onboarding deferred to M5 (multi-user).

## Requirements

### Functional

- [ ] Dashboard sidebar with 4 geographic level badges
- [ ] Badge counters showing "new" article count per level
- [ ] Toggle filtering: click badge to include/exclude that level
- [ ] Full-width dashboard layout (sidebar + content area)
- [ ] Settings: "new articles" threshold (hours, default 24)
- [ ] Settings: country selection dropdown
- [ ] Existing filters (search, source, date) work on top of geographic selection
- [ ] i18n for all 4 languages (badge labels, settings labels)

### Non-Functional

- Performance: badge counts must not cause extra API calls on every render (compute client-side from already-fetched data)
- Responsive: on mobile, sidebar collapses to horizontal badge row above content
- Accessibility: badges are keyboard-navigable, screen-reader friendly

## Technical Notes

### Badge Counts (Client-Side)

No new API endpoint needed. The dashboard already fetches all news items. Counts are computed by:
1. Fetch sources to get `geographic_level` per source
2. Fetch news (already done) — each news item has `source_id`
3. Join client-side: group news by source's geographic level, count those within the "new" threshold

### API Changes

None for core functionality. The geographic_level is already on Source and returned by GET /api/sources.

### Settings Changes

Two new settings keys in `settings.json`:
- `news_freshness_hours`: number (default 24)
- `user_country`: string | null (ISO 3166-1 alpha-2, default null)

### Component Changes

- **Dashboard (Feed.tsx)**: new sidebar layout, badge components, geographic filtering logic
- **Settings**: two new fields (country dropdown, freshness hours input)
- **i18n**: new keys for geographic level labels, settings labels, empty state messages

## Acceptance Criteria

- [ ] Dashboard shows 4 geographic badges in sidebar with article counts
- [ ] Clicking badges filters news by geographic level
- [ ] Multiple badges can be active simultaneously
- [ ] Default state shows all news (all badges active)
- [ ] "New" threshold configurable in settings
- [ ] Country selectable in settings
- [ ] Badge counts update when news is fetched/imported
- [ ] Layout is full-width with sidebar
- [ ] Works in all 4 languages
- [ ] Responsive: horizontal badges on mobile

## Out of Scope

- Onboarding flow (deferred to M5)
- Feed registry / community catalog (separate spec)
- Geolocation-based country detection (privacy concern)
- Custom user filters (see Future Evolution below)

## Future Evolution (M4b)

The geographic sidebar is the foundation for a **fully customizable navigation system**:

- **Custom filters**: user creates named filters (e.g., "Middle East Economics", "USA Economics") based on source tags, country, keywords
- **Groups/categories**: filters can be organized into collapsible groups (e.g., geographic levels under "Geography", custom filters under "Economics")
- **Drag & drop**: user reorders filters and groups freely
- **Multi-membership**: a news item can appear under multiple filters (a source can match both "Continental" and "Economics")
- **Default vs custom**: geographic levels are the default filter set; user adds their own alongside

This transforms the sidebar from 4 fixed badges into a personal navigation workspace. Implementation requires: filter persistence (DB or settings), tagging/categorization system, drag & drop UI, group CRUD.

## Open Questions

- Should badges show total article count or only "new" count?
- Should there be a visual distinction between "0 new but has sources" vs "0 new, no sources at this level"?
- On mobile, should the horizontal badges be scrollable or always all visible?
