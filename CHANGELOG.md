# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Add German (DE) translation and cycle language toggle
- Add import-all button with streaming progress to Dashboard
- Add French (FR) translation and replace language toggle with dropdown menu
- Add stateful feed health monitoring with escalation ladder
- Add health status badges and bulk health check to Sources page
- Add geographic sidebar with server-side filtering to dashboard

### Fixed

- Cosmetic fixes for dashboard, feed page, and admin
- Read version dynamically from package.json, bump to 0.3.5-pre

### Documentation

- Add git root directory rule to workflow
- Split feed health spec into monitor and auto-recovery
- Rewrite starter packs spec with geographic sidebar design
- Add custom filters future evolution (M4b) to starter packs spec
- Auto-generated key-decisions, idea-capture rule, session discipline

### Miscellaneous

- Adopt ADR-012 automation layer and scaffold git hooks

## [0.3.0-pre] - 2026-03-12

### Added

- Implement Admin UI page (tab layout, stats, quality, actions, inspector)
- Redesign Admin UI with accordion-sidebar layout
- Add catalog-subscription model (ADR-007)
- Add Alembic migration for catalog fields and subscriptions table
- Add feed crawler script and import 86 validated sources
- Add repository methods and fix empty subscription filtering
- Subscription-based sources API semantics
- Unified Sources page with catalog search
- Sources page with tabs layout, renamed to Feed
- Validate feed URL before adding source
- Import-all feeds with streaming progress bar

### Fixed

- HTML cleanup now preserves semantic tags, only strips non-content residue
- Remove duplicate title from article content and downgrade headings
- Add browser User-Agent headers to content scraper
- Distinguish feed import errors from no-new-news
- Reinstate mandatory session startup checklist

### Documentation

- Add document indexing spec (planned, M4a)
- M4a planning — ADR-007 catalog-subscription model, new specs
- Remove resolved tech-debt documentation and update INDEX
- Add ADR-008 data locality split (proposed for M5)

### Refactored

- Replace accordion animation with static sidebar in Admin UI
- Align core entities with infrastructure models
- FeedParserService now uses UnitOfWork instead of raw Session

### Testing

- Update and add tests for subscription-based sources

### Miscellaneous

- Update frontend dependencies and local settings

## [0.2.0] - 2026-03-09

### Added

- Add dashboard with paginated API, filters, and Tailwind UI
- Add on-demand article content fetching
- Add news detail page with full article view
- Dark mode, Sources/Settings Tailwind migration, responsive layout
- Add recent and saved searches
- Add feed discovery with URL-based detection
- Add search result highlighting and contextual snippets
- Complete settings page with scheduler and retention controls
- Add pre-commit hook to auto-archive resolved tech-debt issues
- Preserve semantic HTML in article scraper for readable content
- Add i18n support with react-i18next (Italian + English)
- Add language toggle button in navbar (IT/EN)
- Add swappable visual templates (Financial Times, Hacker, Brutalist, Gazette, Minimal)
- Implement M3.1 admin API endpoints (9 endpoints, 18 tests)

### Fixed

- Replace deprecated APIs across codebase
- Strip HTML from feed summaries and improve content scraping
- Add settings validation and XXE protection
- Render news preview with proper formatting via ArticleContent
- Merge citation fragments in HTML scraper output
- Improve scraper with structural fragment detection and noise filtering
- Strip trailing boilerplate sections from scraped articles
- Improve summary prompt and timeout for thinking models
- Unify page widths, align breadcrumb, fix summary card palette
- Collapse advanced filters behind toggle button

### Documentation

- Update project status, add tech-debt tracking, update README
- Mark resolved tech-debt issues
- Consolidate and simplify docs/ folder
- Split M4 into M4a (Feed Infrastructure) and M4b (Intelligence)
- Add feed admin tools spec and M3.1 milestone
- Move search-discovery spec to implemented
- Update specs, status, and add ADR-005 geographic levels
- Add daily digest spec (M4a) with cross-referencing outline (M4b)

### Refactored

- Migrate .claude/ config to .claude/rules/ pattern
- Simplify NewsCard to preview-only, add ADR-004
- Split monolithic main.py into modular route files

### Styling

- Editorial typography, warm color palette, breadcrumb navigation

### Testing

- Add backend test coverage for scraper, discovery, and security
- Add Vitest setup and 73 frontend tests

### Miscellaneous

- Archive 4 resolved tech-debt issues
- Bump version to 0.2.0

## [0.1.0] - 2025-10-25

### Added

- Improve AI summarization with web scraping and content cleaning

<\!-- generated by git-cliff -->