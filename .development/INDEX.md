# INDEX - Government Feed Development Documentation

*Auto-generated: 2026-07-04 00:04*

---

## Quick Links

- [Current Status](CURRENT-STATUS.md)
- [Tech Debt](tech-debt/README.md)
- [Specs](specs/README.md)
- [ADR](reference/decisions/README.md)

---

## Development Documentation (.development/)

*Specs, tech-debt, decisions*

### (root)/ (4 files)

- [ARCHITECTURE.md](ARCHITECTURE.md) (3KB, 2026-07-04) **RECENT**
- [INDEX.md](INDEX.md) (8KB, 2026-07-03) **RECENT**
- [CURRENT-STATUS.md](CURRENT-STATUS.md) (3KB, 2026-07-03) **RECENT**
- [README.md](README.md) (3KB, 2026-07-03) **RECENT**

### specs/ (1 files)

- [README.md](specs/README.md) (1KB, 2026-03-09)

### specs/backlog/ (10 files)

- [feed-registry.md](specs/backlog/feed-registry.md) (2KB, 2026-03-09)
- [import-export-config.md](specs/backlog/import-export-config.md) (1KB, 2026-03-09)
- [multi-user-auth.md](specs/backlog/multi-user-auth.md) (2KB, 2026-03-09)
- [notifications.md](specs/backlog/notifications.md) (2KB, 2026-03-09)
- [relevance-scoring.md](specs/backlog/relevance-scoring.md) (2KB, 2026-03-09)
- [trend-detection.md](specs/backlog/trend-detection.md) (1KB, 2026-03-09)
- [ui-preferences.md](specs/backlog/ui-preferences.md) (1KB, 2026-03-09)
- [ai-categorization.md](specs/backlog/ai-categorization.md) (1KB, 2026-03-09)
- [daily-digest.md](specs/backlog/daily-digest.md) (3KB, 2026-03-09)
- [data-export.md](specs/backlog/data-export.md) (1KB, 2026-03-09)

### specs/implemented/ (22 files)

- [bulk-fetch-all-sources.md](specs/implemented/bulk-fetch-all-sources.md) (1KB, 2026-07-03) **RECENT**
- [catalog-browse-ui.md](specs/implemented/catalog-browse-ui.md) (2KB, 2026-07-03) **RECENT**
- [feed-health-monitor.md](specs/implemented/feed-health-monitor.md) (4KB, 2026-07-03) **RECENT**
- [source-catalog-subscriptions.md](specs/implemented/source-catalog-subscriptions.md) (3KB, 2026-07-03) **RECENT**
- [starter-packs.md](specs/implemented/starter-packs.md) (8KB, 2026-07-03) **RECENT**
- [ai-summarization.md](specs/implemented/ai-summarization.md) (2KB, 2026-03-09)
- [background-workers.md](specs/implemented/background-workers.md) (2KB, 2026-03-09)
- [content-deduplication.md](specs/implemented/content-deduplication.md) (1KB, 2026-03-09)
- [dashboard-news-browsing.md](specs/implemented/dashboard-news-browsing.md) (1KB, 2026-03-09)
- [database-migrations.md](specs/implemented/database-migrations.md) (1KB, 2026-03-09)
- [error-resilience.md](specs/implemented/error-resilience.md) (2KB, 2026-03-09)
- [feed-parsing.md](specs/implemented/feed-parsing.md) (1KB, 2026-03-09)
- [frontend-base.md](specs/implemented/frontend-base.md) (1KB, 2026-03-09)
- [news-detail-view.md](specs/implemented/news-detail-view.md) (1KB, 2026-03-09)
- [redis-caching.md](specs/implemented/redis-caching.md) (2KB, 2026-03-09)
- [repository-pattern.md](specs/implemented/repository-pattern.md) (1KB, 2026-03-09)
- [rest-api.md](specs/implemented/rest-api.md) (2KB, 2026-03-09)
- [search-discovery.md](specs/implemented/search-discovery.md) (1KB, 2026-03-09)
- [settings-management.md](specs/implemented/settings-management.md) (1KB, 2026-03-09)
- [source-management.md](specs/implemented/source-management.md) (2KB, 2026-03-09)
- [structured-logging.md](specs/implemented/structured-logging.md) (1KB, 2026-03-09)
- [testing-suite.md](specs/implemented/testing-suite.md) (2KB, 2026-03-09)

### specs/planned/ (5 files)

- [feed-auto-recovery.md](specs/planned/feed-auto-recovery.md) (3KB, 2026-07-03) **RECENT**
- [document-indexing.md](specs/planned/document-indexing.md) (3KB, 2026-03-12)
- [i18n-additional-languages.md](specs/planned/i18n-additional-languages.md) (<1KB, 2026-03-12)
- [feed-admin-tools.md](specs/planned/feed-admin-tools.md) (5KB, 2026-03-09)
- [feed-discovery-automated.md](specs/planned/feed-discovery-automated.md) (8KB, 2026-03-09)

### tech-debt/ (14 files)

- [README.md](tech-debt/README.md) (3KB, 2026-07-03) **RECENT**
- [naive-aware-datetime-columns.md](tech-debt/naive-aware-datetime-columns.md) (3KB, 2026-07-03) **RECENT**
- [ruff-version-drift-ci.md](tech-debt/ruff-version-drift-ci.md) (2KB, 2026-07-03) **RECENT**
- [source-tagging-unreliable.md](tech-debt/source-tagging-unreliable.md) (2KB, 2026-03-12)
- [_TEMPLATE.md](tech-debt/_TEMPLATE.md) (1KB, 2026-03-09)
- [code-review-2026-03-08.md](tech-debt/code-review-2026-03-08.md) (41KB, 2026-03-09)
- [dependency-analysis-2026-03-08.md](tech-debt/dependency-analysis-2026-03-08.md) (14KB, 2026-03-09)
- [duplicated-html-stripping.md](tech-debt/duplicated-html-stripping.md) (<1KB, 2026-03-09)
- [global-mutable-state-main.md](tech-debt/global-mutable-state-main.md) (1KB, 2026-03-09)
- [missing-foreign-key-constraint.md](tech-debt/missing-foreign-key-constraint.md) (1KB, 2026-03-09)
- [newscard-summary-hidden-on-expand.md](tech-debt/newscard-summary-hidden-on-expand.md) (1KB, 2026-03-09)
- [pre-commit-grep-regex.md](tech-debt/pre-commit-grep-regex.md) (1KB, 2026-03-09)
- [security-audit-2026-03-08.md](tech-debt/security-audit-2026-03-08.md) (33KB, 2026-03-09)
- [security-ssrf-arbitrary-urls.md](tech-debt/security-ssrf-arbitrary-urls.md) (10KB, 2026-03-09)

### reference/decisions/ (10 files)

- [001-clean-architecture.md](reference/decisions/001-clean-architecture.md) (1KB, 2026-07-03) **RECENT**
- [002-privacy-first-ai.md](reference/decisions/002-privacy-first-ai.md) (1KB, 2026-07-03) **RECENT**
- [003-content-deduplication.md](reference/decisions/003-content-deduplication.md) (1KB, 2026-07-03) **RECENT**
- [004-master-detail-layout.md](reference/decisions/004-master-detail-layout.md) (2KB, 2026-07-03) **RECENT**
- [005-geographic-levels-navigation.md](reference/decisions/005-geographic-levels-navigation.md) (4KB, 2026-07-03) **RECENT**
- [006-headless-browser-scraping.md](reference/decisions/006-headless-browser-scraping.md) (2KB, 2026-07-03) **RECENT**
- [007-catalog-subscription-model.md](reference/decisions/007-catalog-subscription-model.md) (3KB, 2026-07-03) **RECENT**
- [008-data-locality-split.md](reference/decisions/008-data-locality-split.md) (3KB, 2026-07-03) **RECENT**
- [README.md](reference/decisions/README.md) (2KB, 2026-07-03) **RECENT**
- [_TEMPLATE.md](reference/decisions/_TEMPLATE.md) (1KB, 2026-07-03) **RECENT**

### reference/technical/ (2 files)

- [m4b-intelligence-design-brief.md](reference/technical/m4b-intelligence-design-brief.md) (12KB, 2026-07-04) **RECENT**
- [relevance-model-notes.md](reference/technical/relevance-model-notes.md) (5KB, 2026-07-04) **RECENT**

### archive/completed/ (6 files)

- [2026-03-11_core-entity-model-misalignment.md](archive/completed/2026-03-11_core-entity-model-misalignment.md) (4KB, 2026-03-12)
- [2026-03-11_feedparser-bypasses-uow.md](archive/completed/2026-03-11_feedparser-bypasses-uow.md) (2KB, 2026-03-12)
- [2026-03-08_deprecated-datetime-utcnow.md](archive/completed/2026-03-08_deprecated-datetime-utcnow.md) (1KB, 2026-03-09)
- [2026-03-08_deprecated-fastapi-pydantic-apis.md](archive/completed/2026-03-08_deprecated-fastapi-pydantic-apis.md) (1KB, 2026-03-09)
- [2026-03-08_security-unvalidated-settings-endpoint.md](archive/completed/2026-03-08_security-unvalidated-settings-endpoint.md) (3KB, 2026-03-09)
- [2026-03-08_security-xxe-feed-parser.md](archive/completed/2026-03-08_security-xxe-feed-parser.md) (10KB, 2026-03-09)

---

## Public Documentation (docs/)

*Committed to git - user-facing documentation*

### docs/

- [README.md](docs/README.md) (<1KB, 2026-03-09)
- [roadmap.md](docs/roadmap.md) (5KB, 2026-07-03) **RECENT**
- [technical.md](docs/technical.md) (4KB, 2026-07-03) **RECENT**
- [vision.md](docs/vision.md) (14KB, 2025-10-25)

---

## Recently Modified (last 7 days)

1. [ARCHITECTURE.md](ARCHITECTURE.md) (today)
2. [m4b-intelligence-design-brief.md](reference/technical/m4b-intelligence-design-brief.md) (today)
3. [relevance-model-notes.md](reference/technical/relevance-model-notes.md) (today)
4. [INDEX.md](INDEX.md) (today)
5. [README.md](tech-debt/README.md) (today)
6. [naive-aware-datetime-columns.md](tech-debt/naive-aware-datetime-columns.md) (today)
7. [CURRENT-STATUS.md](CURRENT-STATUS.md) (today)
8. [README.md](README.md) (today)
9. [001-clean-architecture.md](reference/decisions/001-clean-architecture.md) (today)
10. [002-privacy-first-ai.md](reference/decisions/002-privacy-first-ai.md) (today)

---

*Run `python .development/scripts/generate-index.py` to regenerate*