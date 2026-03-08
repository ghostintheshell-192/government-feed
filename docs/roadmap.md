# Government Feed - Roadmap

## Milestone Overview

| Milestone | Status | Description |
|-----------|--------|-------------|
| **M1 — MVP Backend** | Complete | Core API, feed parsing, AI summarization, repository pattern |
| **M2 — Production-Ready** | Complete | Testing (177 tests), background workers, Redis caching, error resilience |
| **M3 — Frontend** | In progress | Dashboard, news detail, sources management, dark mode, feed discovery |
| **M4a — Feed Infrastructure** | Planned | Health monitoring, automated discovery, starter packs, export, config |
| **M4b — Intelligence** | Planned | AI categorization, relevance scoring, trend detection, sentiment analysis |
| **M5 — Scaling & Multi-User** | Planned | Authentication, multi-tenancy, PostgreSQL, cloud deployment |

For current status details, see [`.development/CURRENT-STATUS.md`](../.development/CURRENT-STATUS.md).

---

## M3 — Frontend (in progress)

### Done

- Dashboard with paginated news, filters (source, date, keyword), read/unread tracking
- News detail page with on-demand content fetching and AI summarization
- Sources management: CRUD, feed processing trigger, active/inactive toggle
- Feed discovery: URL-based detection (HTML link tags, common paths, feedparser validation)
- Dark mode (light/dark/system), shadcn/ui + Tailwind CSS
- Recent and saved searches

### Remaining

- Feed discovery text search (moves to M4a — depends on search provider integration)
- Settings page UI
- Frontend test coverage
- Accessibility improvements

---

## M4a — Feed Infrastructure

Robust, autonomous feed management — no AI/ML required.

**Prerequisite**: Core entity/model refactoring ([tech-debt](../.development/tech-debt/core-entity-model-misalignment.md))

### Feed Health & Recovery

- Feed health monitoring with stateful escalation (healthy → degraded → unhealthy → dead)
- Automatic URL recovery for dead feeds via search providers
- Health status visible in UI and API
- See: [`specs/planned/feed-health-monitor.md`](../.development/specs/planned/feed-health-monitor.md)

### Automated Feed Discovery

- Multi-provider search (Exa primary, Brave Search fallback)
- Text search replacing broken DuckDuckGo integration
- Batch feed validation and deduplication
- See: [`specs/planned/feed-discovery-automated.md`](../.development/specs/planned/feed-discovery-automated.md)

### Starter Packs

- Pre-configured feed bundles by topic and geography
- One-click import into personal sources
- See: [`specs/backlog/starter-packs.md`](../.development/specs/backlog/starter-packs.md)

### Export & Configuration

- Data export (CSV, JSON, PDF)
- Import/export feed configuration
- Settings page UI
- Configurable notifications (email digest, push, webhooks)

---

## M4b — Intelligence

AI/ML-powered features — depends on Ollama and local model infrastructure.

### Relevance & Categorization

- Automatic relevance scoring for news ranking
- AI-powered categorization (hierarchical taxonomy)
- Multi-label classification
- Keyword-based and source-based ranking factors
- User preference learning (collaborative filtering)

### Analysis

- Trend detection across sources
- Clustering of related news
- Sentiment analysis (neutral, positive, alarming)
- Historical sentiment tracking

---

## M5 — Scaling & Multi-User

### User Management

- JWT authentication
- User profiles with preferences
- Role-based access control

### Infrastructure

- PostgreSQL migration with connection pooling
- Kubernetes deployment (optional)
- Prometheus + Grafana monitoring
- Automated backups

### Public API

- OpenAPI documentation
- Rate limiting
- API key management

---

## Long-Term Vision

- **Feed Registry**: Community-driven marketplace of curated institutional feeds
- **Multi-model AI**: Ensemble models, per-topic specialization, BYOK providers
- **Advanced NLP**: Entity extraction, fact-checking, multi-language summarization
- **Community features**: Comments, upvotes, collaborative fact-checking

See [vision.md](vision.md) for the full project vision.
