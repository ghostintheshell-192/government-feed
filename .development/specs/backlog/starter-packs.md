# Starter Packs

**Status**: backlog
**Milestone**: M4a-Feed-Infrastructure
**Priority**: should-have
**Depends on**: [feed-registry](feed-registry.md), [import-export-config](import-export-config.md)
**Related ADR**: [ADR-005 Geographic Levels Navigation](../../reference/decisions/005-geographic-levels-navigation.md)

## Summary

Pre-populated feed catalog organized by geographic level, presented through the app's concentric navigation structure (local → national → continental → global). Replaces the original "downloadable bundle" concept with an integrated discovery experience where geographic levels act as active containers that suggest available sources.

## User Stories

- As a new user, I want to see relevant institutional sources organized by geographic proximity to me
- As a user, I want each geographic level to show what I follow and what else is available
- As a user, I want to activate new sources with one click from within the level view
- As a user, I want to add my own sources and classify them by geographic level

## Design Change (ADR-005)

The original concept treated starter packs as **separate downloadable bundles** (e.g., "Italia Economia Base"). ADR-005 reframes them as **views into a catalog filtered by geographic level**. Instead of importing a pack, the user sees the National level populated with available Italian sources and picks the ones they want. The starter pack concept dissolves into the geographic navigation itself.

This unifies three previously separate UX flows:
1. **Onboarding** — user selects country/region, sees pre-populated levels
2. **Source management** — sources grouped by level, both catalog and user-added
3. **Feed discovery** — "Discover more" links within each level

## Requirements

### Functional

- [ ] Geographic level enum on Source model (`LOCAL`, `NATIONAL`, `CONTINENTAL`, `GLOBAL`)
- [ ] Country code (ISO 3166-1) and optional region on Source model
- [ ] Curated feed catalog with pre-classified sources (JSON, bundled in app)
- [ ] Onboarding flow: user selects country/region → sees catalog by level
- [ ] Level containers show active sources + available catalog sources
- [ ] One-click activation of catalog sources
- [ ] Manual source addition with level classification
- [ ] "Discover more" link per level → filtered catalog view
- [ ] Community-contributed catalog entries (future, via feed registry)

### Non-Functional

- UX: Onboarding with geographic selection should take < 1 minute
- Quality: Catalog sources are regularly verified for working feeds
- Data: Initial catalog focuses on Italy (leveraging italia/awesome-rss-feeds)

## Technical Notes

- Initial catalog sources by level (Italy focus):
  - **Local**: Regioni (Lombardia, Puglia, Campania, FVG, ...), ARPA, ASL
  - **National**: ISTAT, Banca d'Italia, MEF, MIMIT, Italia Domani (PNRR)
  - **Continental**: BCE, Commissione EU, EMA, Parlamento EU
  - **Global**: ONU, WHO, IMF
- Catalog format: JSON with geographic_level, country_code, region fields
- Phase 1: Bundled JSON catalog in the application
- Phase 2: Hosted in feed registry with API
- Reference: [italia/awesome-rss-feeds](https://github.com/italia/awesome-rss-feeds) for Italian PA sources

## Acceptance Criteria

- [ ] Source model includes geographic_level, country_code, region fields
- [ ] Onboarding asks for country/region and presents catalog by level
- [ ] At least 4 levels are populated for Italy at launch
- [ ] Sources are visually grouped by geographic level in source management
- [ ] Users can activate catalog sources and add custom sources to any level
- [ ] All catalog sources are verified as working feeds
