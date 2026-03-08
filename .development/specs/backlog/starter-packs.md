# Starter Packs

**Status**: backlog
**Milestone**: M4a-Feed-Infrastructure
**Priority**: should-have
**Depends on**: [feed-registry](feed-registry.md), [import-export-config](import-export-config.md)

## Summary

Pre-configured feed bundles for quick onboarding, curated by topic and geography (e.g., "Italia Economia Base", "Europa Politica Monetaria"), downloadable and importable with one click.

## User Stories

- As a new user, I want to start with a curated set of feeds without manual configuration
- As a user, I want to browse starter packs by topic and geography
- As a user, I want to import a starter pack with one click

## Requirements

### Functional

- [ ] Curated starter pack definitions (name, description, tags, feed list)
- [ ] Browse starter packs by category and geography
- [ ] One-click import of entire starter pack into personal sources
- [ ] Preview pack contents before importing
- [ ] Community-contributed starter packs (future)

### Non-Functional

- UX: Onboarding with starter pack should take < 1 minute
- Quality: Starter packs are regularly verified for working feeds

## Technical Notes

- Initial starter packs (examples from vision.md):
  - "Italia - Economia Base": BCE, MEF, Banca d'Italia
  - "Europa - Politica Monetaria": ECB, Commissione EU
  - "Locale - Regione Lombardia": Regione, ARPA, ASL
- Pack format: JSON matching feed registry schema (see vision.md for example)
- Phase 1: Bundled JSON files in the application
- Phase 2: Hosted in feed registry with download API
- Reuses import functionality from [import-export-config](import-export-config.md)

## Acceptance Criteria

- [ ] At least 3 starter packs are available at launch
- [ ] Starter packs can be browsed and previewed
- [ ] One-click import adds all pack feeds to user's sources
- [ ] All feeds in starter packs are verified as working
