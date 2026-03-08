# Government Feed - Roadmap

## Milestone Overview

| Milestone | Status | Description |
|-----------|--------|-------------|
| **M1 — MVP Backend** | Complete | Core API, feed parsing, AI summarization, repository pattern |
| **M2 — Production-Ready** | Complete | Testing (177 tests), background workers, Redis caching, error resilience |
| **M3 — Frontend** | In progress | Dashboard, news detail, sources management, dark mode, feed discovery |
| **M4 — Advanced Features** | Planned | Relevance scoring, AI categorization, trend detection, export |
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

- Feed discovery text search (search engine integration blocked)
- Settings page UI
- Frontend test coverage
- Accessibility improvements

---

## M4 — Advanced Features

### Relevance & Categorization

- Automatic relevance scoring for news ranking
- AI-powered categorization (hierarchical taxonomy)
- Multi-label classification
- Keyword-based and source-based ranking factors

### Analysis

- Trend detection across sources
- Clustering of related news
- Sentiment analysis (neutral, positive, alarming)
- Historical sentiment tracking

### Export & Notifications

- CSV, JSON, PDF export
- Configurable alert system
- Email digest (daily/weekly)
- Desktop push notifications
- Webhook integrations

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
