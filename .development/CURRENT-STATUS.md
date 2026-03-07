# Government Feed - Current Status

*Last updated: 2026-03-07*

## Project Phase

**Current milestone**: M3-Frontend (mostly complete)
**Next milestone**: M4-Advanced (AI categorization, relevance scoring, notifications)

## Completed

### M1 — MVP Backend

- Core Domain: NewsItem, Source, Category entities with content hashing
- Repository Pattern + Unit of Work: Full data access abstraction
- Feed Parsing: RSS/Atom with feedparser, HTML stripping, deduplication
- AI Summarization: Ollama integration with web scraping and content cleaning
- REST API: 18 endpoints (Sources CRUD, News, AI, Settings, Features, Scheduler, Cache, Discovery)
- Pydantic Schemas: Full request/response validation
- Structured Logging: Centralized logging across all layers
- Settings Management: JSON-based runtime configuration
- Frontend Base: React 18 + TypeScript scaffold

See: `specs/implemented/` for completed specifications.

### M2 — Production-Ready Backend

- Testing Suite: 177 tests, ~90% coverage (unit + integration)
- Background Workers: APScheduler with feed polling (15m), cleanup (24h), health checks (6h)
- Redis Caching: Graceful fallback when Redis unavailable
- Database Migrations: Alembic configured (not yet actively used)
- Error Resilience: Retry decorators (tenacity) + custom circuit breaker pattern

### M3 — Frontend (in progress)

- Dashboard & News Browsing: paginated feed, filters (source, date, keyword), read/unread tracking (localStorage), "Carica altri" pagination
- News Detail Page: full article view, on-demand content fetching, AI summarization
- Dark Mode: Light/Dark/System with persistence
- UI Components: shadcn/ui + Tailwind CSS (Card, Button, Badge, Input, Select, Skeleton, Separator)
- Recent & Saved Searches: localStorage-based with debounce
- Feed Discovery: URL-based feed detection (HTML link tags + common paths + feedparser validation)
- Sources Management: CRUD UI with modal form, import trigger, toggle active

## Partially Complete / Known Gaps

- **Feed Discovery text search**: DuckDuckGo integration not returning results — URL discovery works, text search blocked
- **Database migrations**: Alembic configured but never used — no FK constraints enforced
- **Frontend tests**: 0 test coverage on frontend
- **Accessibility**: No aria labels, no keyboard navigation on modals, no error boundaries

## Tech Debt

See `tech-debt/` for tracked issues. Key items:

| Issue | Priority | File |
|-------|----------|------|
| `datetime.utcnow()` deprecation (77 warnings) | High | `deprecated-datetime-utcnow.md` |
| FeedParserService bypasses UnitOfWork | Medium | `feedparser-bypasses-uow.md` |
| Deprecated FastAPI/Pydantic/SQLAlchemy APIs | Medium | `deprecated-fastapi-pydantic-apis.md` |
| Missing FK constraint news_items → sources | Medium | `missing-foreign-key-constraint.md` |
| NewsCard summary hidden on expand | Medium | `newscard-summary-hidden-on-expand.md` |
| Pre-commit grep regex | Low | `pre-commit-grep-regex.md` |
| Duplicated HTML stripping | Low | `duplicated-html-stripping.md` |
| Global mutable state in main.py | Low | `global-mutable-state-main.md` |

## Quick Links

| What | Where |
|------|-------|
| **Specs** | `specs/` |
| **Tech debt** | `tech-debt/` |
| **ADR** | `reference/decisions/` |
| **Architecture** | `ARCHITECTURE.md` |
| **Public docs** | `docs/` |
