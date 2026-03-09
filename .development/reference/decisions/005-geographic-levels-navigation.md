# ADR-005: Geographic Levels as Primary Navigation Structure

**Date**: 2026-03-08
**Status**: Proposed
**Impact**: significant

## Context

Government Feed aggregates institutional sources spanning multiple geographic scopes — from regional authorities to international organizations. Currently, sources are presented as a flat list, filterable by various attributes. Starter packs (planned for M4a) are conceived as a separate onboarding mechanism with their own browsing interface.

Meanwhile, the concept of geographic proximity is central to the project's value: a citizen's relationship with institutional information is inherently geographic. National policies affect them directly, EU regulations shape their legal framework, and local government decisions impact their daily life. This structure already exists in how institutions organize themselves — it just isn't reflected in the UX.

## Decision

Adopt a concentric geographic level model as the primary organizational structure for sources, unifying onboarding, source management, and feed discovery into a single navigation paradigm.

### The Four Levels

| Level | Enum | Example Sources |
|-------|------|-----------------|
| Local | `LOCAL` | Regione Lombardia, ARPA, ASL |
| National | `NATIONAL` | ISTAT, Banca d'Italia, Ministeri |
| Continental | `CONTINENTAL` | BCE, Commissione EU, EMA |
| Global | `GLOBAL` | ONU, WHO, IMF |

### Data Model Changes

Add to the `Source` entity:

- `geographic_level`: enum (`LOCAL`, `NATIONAL`, `CONTINENTAL`, `GLOBAL`) — required
- `country_code`: ISO 3166-1 alpha-2 (e.g., `IT`, `FR`) — optional for `GLOBAL`
- `region`: free text (e.g., "Lombardia") — optional, relevant for `LOCAL`

### UX Behavior

The geographic levels serve as **active containers**, not passive categories:

1. **Onboarding**: User provides country and optionally region. The app presents available sources organized by level, pre-populated from the feed catalog. User selects which to activate.
2. **Daily navigation**: Sources are grouped by geographic level. Each level shows active sources and a discrete "Discover more" link to the catalog filtered for that level.
3. **Manual additions**: When a user adds a source via URL, they classify it by level. The same containers accommodate both catalog sources and user-added ones.

### Starter Packs Integration

Starter packs become **views into the catalog filtered by level and geography**, not separate bundles. Instead of "Import Italia Economia Base", the user sees the National level populated with Italian institutional sources and picks the ones they want. The starter pack concept dissolves into the geographic navigation itself.

## Rationale

- **Single mental model**: One structure for onboarding, browsing, and managing — reduces cognitive load
- **Reflects reality**: Mirrors how institutions actually organize (municipal → national → supranational)
- **Citizen-centric perspective**: Places the user at the center of concentric spheres of institutional influence
- **Discovery mechanism**: Empty or sparse levels invite exploration ("You have 3 national sources — 12 more available")
- **Minimal technical cost**: 2-3 fields on the Source model, an enum, no new tables or hierarchies
- **Compatible with existing plans**: Feed registry (M4a) provides the catalog; this ADR defines how to present it

## Concerns

- **Classification ambiguity**: Some organizations don't fit neatly (NATO — continental? global?). Mitigated by letting the user choose; defaults can be opinionated.
- **Geolocation dependency**: Requires knowing the user's country/region at minimum. A simple setup question suffices — no GPS needed.
- **Empty levels**: If the catalog is sparse for a given country, levels may look empty. Mitigated by launching with a well-curated Italian catalog first (leveraging italia/awesome-rss-feeds).
- **Over-structuring**: Users with eclectic interests might find levels constraining. Mitigated by keeping it as grouping, not restriction — all sources remain accessible in a flat view too.

## Consequences

- **Positive**: Unified UX for onboarding and daily use, intuitive geographic metaphor, natural integration with feed registry and starter packs
- **Negative**: Requires catalog data to be meaningful (chicken-and-egg with M4a), adds classification step when adding sources manually
- **Supersedes**: This decision reshapes how starter packs (spec `starter-packs.md`) and feed registry browsing (spec `feed-registry.md`) are presented, though not their underlying data infrastructure
