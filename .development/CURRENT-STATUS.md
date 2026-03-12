# Government Feed - Current Status

*Last updated: 2026-03-11*

## Project Phase

**Current milestone**: M4a-Feed-Infrastructure
**Previous milestones**: M1 (MVP), M2 (Production), M3 (Frontend), M3.1 (Admin API) — all complete

## M4a Planning

### Completed (M4a)

- Admin UI: sidebar navigation, feed inspector, cleanup, diagnostics
- Bulk fetch content per source (streaming NDJSON)
- HTML cleanup: semantic whitelist, preserves structural markup
- **Core entity/model alignment** — entities match DB models, dependency violation fixed
- **FeedParserService uses UnitOfWork** — no more raw Session access

### Architecture Decisions (M4a)

- **ADR-005** (Accepted): Geographic levels as primary navigation (LOCAL → NATIONAL → CONTINENTAL → GLOBAL)
- **ADR-007** (Accepted): Catalog-Subscription model — single Source table + Subscription pivot table
- **ADR-008** (Proposed): Data locality — catalog vs user content split, deferred to M5

### Planned Specs (M4a)

| Spec | Priority | Depends on | Status |
|------|----------|------------|--------|
| [Source Catalog & Subscriptions](specs/planned/source-catalog-subscriptions.md) | must-have | — | Spec ready |
| [Catalog Browse UI](specs/planned/catalog-browse-ui.md) | should-have | catalog-subscriptions | Spec ready |
| [Bulk Fetch All Sources](specs/planned/bulk-fetch-all-sources.md) | should-have | catalog-subscriptions | Spec ready |
| [Feed Health Monitor](specs/planned/feed-health-monitor.md) | should-have | catalog-subscriptions | Spec ready |
| [Feed Discovery Automated](specs/planned/feed-discovery-automated.md) | should-have | — | Spec ready |
| [i18n: DE + FR](specs/planned/i18n-additional-languages.md) | nice-to-have | — | Spec ready |
| [Document Indexing](specs/planned/document-indexing.md) | nice-to-have | — | Spec ready (tentative M4a) |

### Implementation Order

1. **Source Catalog & Subscriptions** — foundation for everything else
2. **Feed Crawler** (admin script) — populate catalog with ~1000 sources
3. **Catalog Browse UI** — search and subscribe to catalog sources
4. **Bulk Fetch All** — download content for all subscribed sources at once
5. **Feed Health Monitor** — automated health tracking and recovery
6. **i18n DE + FR** — anytime, no dependencies
7. **Starter Packs** — once catalog has enough sources + geographic levels

### Backlog (deferred to later milestones)

See `specs/backlog/` — includes data export, daily digest, notifications, feed registry, config import/export.

## Previous Milestones (complete)

### M1 — MVP Backend
Core domain, repository pattern, feed parsing, AI summarization, REST API (18 endpoints), Pydantic schemas, structured logging.

### M2 — Production-Ready
Testing suite (278 tests), APScheduler (polling/cleanup/health), Redis caching, Alembic configured, retry + circuit breaker.

### M3 — Frontend
Dashboard with filters, news detail, dark mode, shadcn/ui + Tailwind, feed discovery (URL-based), sources CRUD, 75 Vitest tests.

### M3.1 — Admin API
9 admin endpoints: feed inspector, content cleanup, pattern delete, HTML residue fix, orphan cleanup, quality report, DB stats, bulk fetch.

## Tech Debt

See `tech-debt/` for tracked issues. Key items:

| Issue | Priority | File |
|-------|----------|------|
| Source tagging unreliable (39/103 untagged) | Medium | `source-tagging-unreliable.md` |
| Missing FK constraint news_items → sources | Medium | `missing-foreign-key-constraint.md` |
| NewsCard summary hidden on expand | Medium | `newscard-summary-hidden-on-expand.md` |
| Pre-commit grep regex | Low | `pre-commit-grep-regex.md` |
| Duplicated HTML stripping | Low | `duplicated-html-stripping.md` |
| Global mutable state in main.py | Low | `global-mutable-state-main.md` |

Recently resolved: core-entity-model-misalignment, feedparser-bypasses-uow (archived).

## Quick Links

| What | Where |
|------|-------|
| **Specs** | `specs/` |
| **Tech debt** | `tech-debt/` |
| **ADR** | `reference/decisions/` |
| **Architecture** | `ARCHITECTURE.md` |
| **Public docs** | `docs/` |
