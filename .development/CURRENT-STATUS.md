# Government Feed - Current Status

*Last updated: 2026-07-03*

## Project Phase

**Current milestone**: M4a-Feed-Infrastructure — **complete** (release pending)
**Next milestone**: M4b-Intelligence
**Previous milestones**: M1 (MVP), M2 (Production), M3 (Frontend), M3.1 (Admin API) — all complete

## M4a — Complete

| Item | Outcome |
|------|---------|
| Source Catalog & Subscriptions (ADR-007) | Implemented — pivot table, M5-ready `user_id` |
| Feed Crawler (admin script) | Implemented — 86+ feeds imported |
| Catalog Browse UI | Implemented — tabs in Feed page (I tuoi feed / Esplora catalogo) |
| Bulk Fetch All | Implemented — NDJSON streaming, UI in Sources + Dashboard |
| Feed Health Monitor | Implemented — escalation ladder, badges, bulk check |
| i18n DE + FR | Implemented — 4 languages, dropdown selector |
| Geographic Sidebar (starter-packs) | Implemented — server-side filtering, full-width layout |
| Country selection + freshness settings | Implemented — `user_country` (ISO 3166-1) + `news_freshness_hours` |
| Admin UI, HTML cleanup, core/model alignment | Implemented (early M4a) |

**Deliberately deferred**: geographic badge counters (UX rethink, → M4b custom
filters; idea in `.memory-bank/ideas/2026-07-03-geographic-badge-counters-ux.md`).

**Carried over (spec ready, not scheduled)**: feed-discovery-automated,
feed-auto-recovery, feed-admin-tools, document-indexing — in `specs/planned/`.

### Architecture Decisions (M4a)

- **ADR-005** (Accepted): Geographic levels as primary navigation (LOCAL → NATIONAL → CONTINENTAL → GLOBAL)
- **ADR-007** (Accepted): Catalog-Subscription model — single Source table + Subscription pivot table
- **ADR-008** (Proposed): Data locality — catalog vs user content split, deferred to M5

### Known follow-ups (small)

- Feed page buttons overflow with DE/FR labels (shorten translations or adjust layout)
- 55 articles with 0-char content (ECB, CFTC) — run "Scarica contenuti" bulk fetch in Admin
- Lint cleanup of `backend/tests` (20 pre-existing ruff findings, mostly autofixable)
- `ruff format` one-off pass on 13 legacy files, then enforce in format-check.sh

## M4b — Planning (specs ready)

Design foundation (read in this order before implementing):
[design brief](reference/technical/m4b-intelligence-design-brief.md) →
[relevance model notes](reference/technical/relevance-model-notes.md) →
[prior art](reference/technical/axes-classification-prior-art.md).

| Spec | Priority | Depends on | Status |
|------|----------|------------|--------|
| [Eval Harness](specs/planned/eval-harness.md) | must-have | — | Spec ready |
| [Categorization Baseline (M4b.1)](specs/planned/categorization-baseline.md) | must-have | eval-harness | Spec ready |
| [Categorization Model (M4b.2)](specs/planned/categorization-model.md) | should-have | baseline | Spec ready |
| [Axes & Cadence (M4b.3)](specs/planned/axes-and-cadence.md) | should-have | harness + baseline | Spec ready |
| [Feed Discovery / Track 0](specs/planned/feed-discovery-automated.md) | must-have | — (parallel) | Spec rewritten (enumeration-first) |

**Pre-implementation gate**: apply the UTCDateTime TypeDecorator fix
(`tech-debt/naive-aware-datetime-columns.md`) before the `enrichments`
migration lands.

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
