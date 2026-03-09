# Government Feed - Technical Documentation

## Technology Stack

### Backend

- **Python 3.13** with full type hints (mypy strict)
- **FastAPI** — async web framework with OpenAPI docs
- **SQLAlchemy 2.0** — ORM with DeclarativeBase
- **Pydantic v2** — data validation with ConfigDict
- **APScheduler** — background job scheduling
- **tenacity** — retry policies for external services
- **feedparser** — RSS/Atom feed parsing
- **httpx** — async HTTP client
- **ruff** — linting and formatting

### Frontend

- **React 18** + **TypeScript**
- **Vite** — build tool
- **React Query** — server state management
- **Tailwind CSS** + **shadcn/ui** — styling and components
- **React Router** — client-side navigation
- **npm** — package manager

### AI

- **Ollama** — local LLM runtime
- **DeepSeek-R1 / Qwen3** — summarization models (configurable)

### Infrastructure

- **SQLite** — development database
- **PostgreSQL** — production database (planned)
- **Redis** — caching layer (optional, graceful fallback)
- **Docker** — containerized services

### Testing

- **pytest** + **pytest-asyncio** + **pytest-cov** + **pytest-mock**
- 177 tests, ~90% backend coverage

---

## System Requirements

### Development

**Minimum** (no AI):
- Dual-core CPU, 8GB RAM, 5GB storage

**Full** (with AI):
- Quad-core CPU, 16GB+ RAM, 30GB storage
- GPU recommended: AMD RX 7000+, NVIDIA GTX 1660+, Intel Arc A770+

**Software**:
- Python 3.13+, Node.js 18+, Docker, Git 2.30+
- Linux, macOS 12+, or Windows 10+ with WSL2

### Production (Single User)

- 1-2 vCPU, 1-2GB RAM, 5-10GB storage
- SQLite (no separate DB server needed)
- Cost: free (self-hosted)

### Production (Small Scale, 10-50 users)

- 2 vCPU, 4GB RAM, 20GB SSD
- PostgreSQL 15+, Redis 512MB
- Reverse proxy with HTTPS
- Cost: 5-10 EUR/month

---

## Deployment

### Development

```bash
# Backend
cd backend && uvicorn backend.src.api.main:app --reload

# Frontend
cd frontend && npm run dev

# Services (Redis, Ollama)
docker-compose up -d
```

### Production

**Recommended**: Docker Compose with all services containerized.

**Components**:
- Backend API (FastAPI + Uvicorn)
- Frontend (static build served by nginx/caddy)
- PostgreSQL database
- Redis cache
- Ollama (for AI features)
- Reverse proxy with HTTPS (Let's Encrypt)

**Cloud providers** (budget-friendly):
- Hetzner Cloud: from 4.15 EUR/month (GDPR-compliant)
- Oracle Cloud: always-free tier available
- DigitalOcean / Linode: from 5-6 USD/month

---

## Security

### Current

- **Input validation**: Pydantic schemas on all API endpoints
- **SQL injection**: prevented by SQLAlchemy ORM (no raw SQL from user input)
- **XSS**: React auto-escapes output
- **CORS**: whitelist-based (localhost only in development)
- **Privacy**: all AI processing local via Ollama, no telemetry or tracking

### Production Checklist

- [ ] HTTPS with TLS 1.3 (Let's Encrypt)
- [ ] CORS restricted to production domain
- [ ] SSH key auth only, no root login
- [ ] PostgreSQL: strong password, no public exposure
- [ ] Firewall: only ports 80, 443, SSH
- [ ] Automated security updates
- [ ] Container images run as non-root

### Future

- Rate limiting on API endpoints
- JWT authentication for multi-user
- API key management for external access
- Dependency auditing (pip-audit, dependabot)

---

## Performance

### API Response Targets (p95)

- GET endpoints: < 50ms
- POST/PUT/DELETE: < 100ms
- Feed processing: < 5s
- AI summarization: 2-10s (model-dependent)

### Optimization

- **Database**: indexes on published_at, source_id, content_hash; connection pooling
- **Caching**: Redis with TTL (news: 5min, sources: 1h); graceful fallback when unavailable
- **AI**: GPU acceleration via Ollama, model quantization (Q4_K_M recommended)

### Single Server Capacity

- 100-500 concurrent users
- 1000-5000 news items/day
- 10-50 AI summaries/minute

---

## Backup & Recovery

### Development

SQLite: file copy before major changes.

### Production

- Daily full database dumps + incremental every 6h
- 30 days retention, off-site storage
- Backup: database, settings.json
- Skip: AI models (re-downloadable), cache (ephemeral), logs (archived separately)
- Target RTO: 1 hour, RPO: 6 hours
