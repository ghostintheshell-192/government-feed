# INDEX - Government Feed Development Documentation

*A map of what exists and what each document is for.*
*For when and why something changed, ask git.*

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

- [ARCHITECTURE.md](ARCHITECTURE.md) — Architecture Reference
- [CURRENT-STATUS.md](CURRENT-STATUS.md) — Government Feed - Current Status
- [INDEX.md](INDEX.md) — INDEX - Government Feed Development Documentation
- [README.md](README.md) — .development/ - Development Documentation

### specs/ (1 files)

- [README.md](specs/README.md) — Feature Specifications

### specs/backlog/ (9 files)

- [ai-categorization.md](specs/backlog/ai-categorization.md) — AI Categorization
- [data-export.md](specs/backlog/data-export.md) — Data Export
- [feed-registry.md](specs/backlog/feed-registry.md) — Feed Registry
- [import-export-config.md](specs/backlog/import-export-config.md) — Import/Export Configuration
- [multi-user-auth.md](specs/backlog/multi-user-auth.md) — Multi-User Authentication
- [notifications.md](specs/backlog/notifications.md) — Notifications
- [relevance-scoring.md](specs/backlog/relevance-scoring.md) — Relevance Scoring
- [trend-detection.md](specs/backlog/trend-detection.md) — Trend Detection
- [ui-preferences.md](specs/backlog/ui-preferences.md) — UI Preferences

### specs/implemented/ (22 files)

- [ai-summarization.md](specs/implemented/ai-summarization.md) — AI Summarization
- [background-workers.md](specs/implemented/background-workers.md) — Background Workers
- [bulk-fetch-all-sources.md](specs/implemented/bulk-fetch-all-sources.md) — Bulk Fetch Content for All Sources
- [catalog-browse-ui.md](specs/implemented/catalog-browse-ui.md) — Catalog Browse & Search UI
- [content-deduplication.md](specs/implemented/content-deduplication.md) — Content Deduplication
- [dashboard-news-browsing.md](specs/implemented/dashboard-news-browsing.md) — Dashboard & News Browsing
- [database-migrations.md](specs/implemented/database-migrations.md) — Database Migrations
- [error-resilience.md](specs/implemented/error-resilience.md) — Error Resilience
- [feed-health-monitor.md](specs/implemented/feed-health-monitor.md) — Feed Health Monitor
- [feed-parsing.md](specs/implemented/feed-parsing.md) — Feed Parsing
- [frontend-base.md](specs/implemented/frontend-base.md) — Frontend Base
- [news-detail-view.md](specs/implemented/news-detail-view.md) — News Detail View
- [redis-caching.md](specs/implemented/redis-caching.md) — Redis Caching
- [repository-pattern.md](specs/implemented/repository-pattern.md) — Repository Pattern
- [rest-api.md](specs/implemented/rest-api.md) — REST API
- [search-discovery.md](specs/implemented/search-discovery.md) — Search & Discovery
- [settings-management.md](specs/implemented/settings-management.md) — Settings Management
- [source-catalog-subscriptions.md](specs/implemented/source-catalog-subscriptions.md) — Source Catalog & Subscriptions
- [source-management.md](specs/implemented/source-management.md) — Source Management
- [starter-packs.md](specs/implemented/starter-packs.md) — Starter Packs — Geographic Navigation
- [structured-logging.md](specs/implemented/structured-logging.md) — Structured Logging
- [testing-suite.md](specs/implemented/testing-suite.md) — Testing Suite

### specs/planned/ (10 files)

- [axes-and-cadence.md](specs/planned/axes-and-cadence.md) — Axes & Cadence (M4b.3) — Epistemics Classification and Telegiornale Ordering
- [categorization-baseline.md](specs/planned/categorization-baseline.md) — Categorization Baseline (M4b.1) — Rules, Enrichment Storage, Sidebar Filters
- [categorization-model.md](specs/planned/categorization-model.md) — Categorization Model (M4b.2) — Embeddings Classifier for the Unsure Cases
- [document-indexing.md](specs/planned/document-indexing.md) — Document Indexing
- [eval-harness.md](specs/planned/eval-harness.md) — Evaluation Harness — Golden Set & Regression Metrics
- [feed-admin-tools.md](specs/planned/feed-admin-tools.md) — Feed Administration Tools
- [feed-auto-recovery.md](specs/planned/feed-auto-recovery.md) — Feed Auto-Recovery
- [feed-discovery-automated.md](specs/planned/feed-discovery-automated.md) — Automated Feed Discovery — Enumerate Institutions, Not Search for Feeds
- [i18n-additional-languages.md](specs/planned/i18n-additional-languages.md) — i18n: Add German and French
- [press-coverage-cross-referencing.md](specs/planned/press-coverage-cross-referencing.md) — Press Coverage — Media Sources and Cross-Referencing

### tech-debt/ (14 files)

- [README.md](tech-debt/README.md) — Tech Debt Issues
- [_TEMPLATE.md](tech-debt/_TEMPLATE.md) — [Issue Title]
- [code-review-2026-03-08.md](tech-debt/code-review-2026-03-08.md) — Code Review Report - Government Feed Backend
- [dependency-analysis-2026-03-08.md](tech-debt/dependency-analysis-2026-03-08.md) — Dependency Analysis Report - Government Feed
- [duplicated-html-stripping.md](tech-debt/duplicated-html-stripping.md) — Duplicated HTML stripping logic across services
- [global-mutable-state-main.md](tech-debt/global-mutable-state-main.md) — Global mutable state in main.py
- [missing-foreign-key-constraint.md](tech-debt/missing-foreign-key-constraint.md) — Missing foreign key constraint from news_items to sources
- [naive-aware-datetime-columns.md](tech-debt/naive-aware-datetime-columns.md) — Naive/aware datetime mismatch between DB columns and code
- [newscard-summary-hidden-on-expand.md](tech-debt/newscard-summary-hidden-on-expand.md) — NewsCard: AI summary hidden when article content is expanded
- [pre-commit-grep-regex.md](tech-debt/pre-commit-grep-regex.md) — Pre-commit hook: grep doesn't support \s+ regex
- [ruff-version-drift-ci.md](tech-debt/ruff-version-drift-ci.md) — Tool version drift between local venv and CI (ruff, mypy)
- [security-audit-2026-03-08.md](tech-debt/security-audit-2026-03-08.md) — Security Audit Report - Government Feed
- [security-ssrf-arbitrary-urls.md](tech-debt/security-ssrf-arbitrary-urls.md) — Security Issue: Server-Side Request Forgery (SSRF) — Arbitrary URL Fetching
- [source-tagging-unreliable.md](tech-debt/source-tagging-unreliable.md) — Source tagging is unreliable

### reference/decisions/ (11 files)

- [001-clean-architecture.md](reference/decisions/001-clean-architecture.md) — ADR-001: Clean Architecture
- [002-privacy-first-ai.md](reference/decisions/002-privacy-first-ai.md) — ADR-002: Privacy-First AI Processing
- [003-content-deduplication.md](reference/decisions/003-content-deduplication.md) — ADR-003: Content Deduplication via SHA256
- [004-master-detail-layout.md](reference/decisions/004-master-detail-layout.md) — ADR-004: Master-Detail Panel Layout for Dashboard
- [005-geographic-levels-navigation.md](reference/decisions/005-geographic-levels-navigation.md) — ADR-005: Geographic Levels as Primary Navigation Structure
- [006-headless-browser-scraping.md](reference/decisions/006-headless-browser-scraping.md) — ADR-006: Headless Browser for Anti-Bot Protected Sources
- [007-catalog-subscription-model.md](reference/decisions/007-catalog-subscription-model.md) — ADR-007: Catalog-Subscription Model for Source Management
- [008-data-locality-split.md](reference/decisions/008-data-locality-split.md) — ADR-008: Data Locality — Catalog vs User Content
- [009-no-profiling-readers-or-publishers.md](reference/decisions/009-no-profiling-readers-or-publishers.md) — ADR-009: No Profiling — Neither Readers Nor Publishers
- [README.md](reference/decisions/README.md) — Decision Log
- [_TEMPLATE.md](reference/decisions/_TEMPLATE.md) — ADR-NNN: <concise decision title>

### reference/technical/ (3 files)

- [axes-classification-prior-art.md](reference/technical/axes-classification-prior-art.md) — Axes Classification — Prior Art & Feasibility
- [m4b-intelligence-design-brief.md](reference/technical/m4b-intelligence-design-brief.md) — M4b Intelligence — Design Brief
- [relevance-model-notes.md](reference/technical/relevance-model-notes.md) — Relevance Model — Founding Notes

### archive/completed/ (6 files)

- [2026-03-08_deprecated-datetime-utcnow.md](archive/completed/2026-03-08_deprecated-datetime-utcnow.md) — Deprecated datetime.utcnow() usage throughout codebase
- [2026-03-08_deprecated-fastapi-pydantic-apis.md](archive/completed/2026-03-08_deprecated-fastapi-pydantic-apis.md) — Deprecated FastAPI and Pydantic APIs
- [2026-03-08_security-unvalidated-settings-endpoint.md](archive/completed/2026-03-08_security-unvalidated-settings-endpoint.md) — Security Issue: Unvalidated Settings Endpoint — Arbitrary Configuration Injection
- [2026-03-08_security-xxe-feed-parser.md](archive/completed/2026-03-08_security-xxe-feed-parser.md) — Security Issue: XXE (XML External Entity) Vulnerability in Feed Parser
- [2026-03-11_core-entity-model-misalignment.md](archive/completed/2026-03-11_core-entity-model-misalignment.md) — Core Entity / Infrastructure Model Misalignment
- [2026-03-11_feedparser-bypasses-uow.md](archive/completed/2026-03-11_feedparser-bypasses-uow.md) — FeedParserService bypasses Unit of Work pattern

---

## Public Documentation (docs/)

*Committed to git - user-facing documentation*

### docs/

- [README.md](../docs/README.md) — Government Feed - Documentation
- [roadmap.md](../docs/roadmap.md) — Government Feed - Roadmap
- [technical.md](../docs/technical.md) — Government Feed - Technical Documentation
- [vision.md](../docs/vision.md) — Government Feed - Documento di Visione

---

*Run `python .development/scripts/generate-index.py` to regenerate*