# Government Feed - Technical Documentation

**Version**: 2.0
**Date**: 25 October 2025
**Status**: Production Implementation

---

## 1. System Requirements

### Development Environment

#### Hardware Minimums

**Basic Development** (no AI features):

- CPU: Dual-core x86_64 processor
- RAM: 8GB minimum
- Storage: 5GB free space
- Network: Standard broadband connection

**Full Development** (with AI):

- CPU: Quad-core x86_64 processor (8+ threads recommended)
- RAM: 16GB minimum (32GB recommended for multiple AI models)
- GPU: Optional but significantly improves AI inference speed
  - **AMD**: RX 7000 series or newer (tested: RX 7800 XT 16GB)
  - **NVIDIA**: GTX 1660 or newer with CUDA 11+ support
  - **Intel**: Arc A770 or newer with OneAPI support
- Storage: 30GB free space (AI models: 4-15GB each)
- Network: Fast connection for model downloads

#### Software Prerequisites

**Core Tools**:

- Python 3.13 or newer
- Node.js 18+ and pnpm (for frontend)
- Docker Desktop (latest stable)
- Git 2.30+

**Operating Systems Supported**:

- Linux: Debian 12+, Ubuntu 22.04+, Fedora 38+, Arch (rolling)
- macOS: 12 Monterey or newer (Apple Silicon and Intel)
- Windows: 10/11 with WSL2 (Ubuntu 22.04 recommended)

**IDE Recommendations**:

- VSCode with Python and TypeScript extensions
- PyCharm Professional (optional)
- Any text editor with LSP support

### Production Deployment

#### Single User (Personal Use)

**Minimum Specs**:

- CPU: 1 vCPU
- RAM: 1GB
- Storage: 5GB
- Database: SQLite (file-based)
- Cost: €0/month (self-hosted)

**Recommended Specs**:

- CPU: 2 vCPU
- RAM: 2GB
- Storage: 10GB SSD
- Database: SQLite or PostgreSQL
- Cost: €3-5/month (VPS providers)

#### Small Scale (10-50 Users)

**Server Specs**:

- CPU: 2 vCPU
- RAM: 4GB
- Storage: 20GB SSD
- Database: PostgreSQL 15+
- Redis: 512MB allocation
- Estimated load: ~100 requests/minute peak

**Infrastructure**:

- Reverse proxy (nginx/caddy) for HTTPS
- Let's Encrypt for SSL certificates
- Automated backups (daily)

#### Medium Scale (100-500 Users)

**Server Specs**:

- CPU: 4 vCPU
- RAM: 8GB
- Storage: 50GB SSD
- Database: PostgreSQL with connection pooling
- Redis: 2GB allocation
- Estimated load: ~500 requests/minute peak

**Additional Components**:

- CDN for static assets (optional)
- Database read replica (optional)
- Load balancer (for multiple API instances)

#### Large Scale (1000+ Users)

**Infrastructure Requirements**:

- Multiple API server instances (horizontal scaling)
- PostgreSQL with read replicas
- Redis cluster for caching
- CDN mandatory for frontend assets
- Object storage (S3-compatible) for media
- Monitoring and alerting systems

**Estimated Costs** (monthly):

- Small: €5-10
- Medium: €20-40
- Large: €100-200+

---

## 2. Deployment Options

### Option 1: Self-Hosted (Recommended for Privacy)

**Best For**:

- Personal use
- Maximum privacy
- Full control over data
- No recurring costs

**Setup**:

- Install on personal computer or home server
- Use SQLite for database (no separate DB server needed)
- AI processing entirely local via Ollama
- Access via localhost or local network

**Pros**:

- Zero infrastructure cost
- Complete data ownership
- No external dependencies
- Offline-capable (except feed fetching)

**Cons**:

- Requires technical setup
- No multi-device sync (unless self-hosted sync)
- Limited to local network access

### Option 2: Cloud VPS (Recommended for Small Teams)

#### Budget Providers

**Hetzner Cloud** (Germany-based, GDPR-compliant):

- CPX11: €4.15/month (2 vCPU, 2GB RAM, 40GB SSD)
- CPX21: €7.59/month (3 vCPU, 4GB RAM, 80GB SSD)
- CPX31: €13.90/month (4 vCPU, 8GB RAM, 160GB SSD)
- Pros: Best price/performance ratio, excellent network
- Cons: No free tier

**Oracle Cloud Free Tier**:

- 2x AMD EPYC (1/8 OCPU each), 1GB RAM each = always free
- 200GB block storage = always free
- Pros: Completely free forever
- Cons: Limited resources, occasional service interruptions

**DigitalOcean**:

- Basic Droplet: $6/month (1 vCPU, 1GB RAM, 25GB SSD)
- Regular Droplet: $12/month (2 vCPU, 2GB RAM, 50GB SSD)
- Pros: Simple interface, good documentation
- Cons: Pricier than Hetzner

**Linode (Akamai)**:

- Nanode: $5/month (1 vCPU, 1GB RAM, 25GB SSD)
- Shared 2GB: $12/month (1 vCPU, 2GB RAM, 50GB SSD)
- Pros: Reliable, good support
- Cons: Similar pricing to DigitalOcean

#### Enterprise Providers

**Not Recommended** (overkill for this project):

- AWS: Complex pricing, expensive for small projects
- Google Cloud: Same issues as AWS
- Azure: Same issues as AWS

**Exception**: Use their free tiers for learning/testing only.

### Option 3: Containerized Deployment

**Docker Compose Setup**:

- All services containerized (backend, frontend, DB, Redis, Ollama)
- Portable across environments
- Easy backup/restore
- One-command deployment

**Kubernetes** (future, if needed):

- Horizontal pod autoscaling
- Service mesh for microservices
- Required only for large scale (1000+ users)

### Option 4: Platform-as-a-Service

**Not Recommended** due to AI requirements:

- Heroku, Railway, Render: Don't support GPU for Ollama
- Vercel, Netlify: Frontend-only, can't run backend services

**Exception**: Deploy frontend on Vercel/Netlify + backend separately on VPS.

---

## 3. Security & Privacy

### Privacy-First Architecture

#### Local AI Processing

**Core Principle**: All content analysis happens on user's machine.

**Implementation**:

- Ollama runs locally (no cloud API calls)
- Article text never leaves the system
- User reading patterns not tracked
- No telemetry, no analytics, no profiling

**Benefits**:

- GDPR compliance by design (no personal data collection)
- No dependency on external AI services
- No recurring API costs
- User controls which models to use

#### Data Storage Philosophy

**What is stored**:

- News articles fetched from public feeds (already public data)
- User preferences (sources followed, UI settings)
- Database stored locally or on user-controlled server

**What is NOT stored**:

- User identity or authentication (single-user design)
- Reading history or behavior tracking
- Analytics or usage metrics
- Any personally identifiable information

**Future Multi-User Considerations**:

- If authentication added, use bcrypt for passwords
- JWT tokens with short expiration
- Optional: OAuth2 for third-party login (GitHub, Google)
- User data encrypted at rest

### Security Best Practices

#### Input Validation

**API Endpoints**:

- All inputs validated via Pydantic schemas
- URL sanitization for user-provided feed URLs
- Content-type validation for file uploads (future)

**Database Queries**:

- SQLAlchemy ORM prevents SQL injection
- Parameterized queries only
- No raw SQL from user input

**Cross-Site Scripting (XSS)**:

- React escapes output by default
- Markdown rendering sanitized (future)
- Content Security Policy headers

#### Dependency Security

**Current Status**:

- Minimal dependency tree (reduces attack surface)
- All dependencies from official PyPI and npm

**Planned**:

- Automated security audits via pip-audit
- Dependabot for automatic dependency updates
- Vulnerability scanning in CI/CD pipeline

#### Network Security

**HTTPS Enforcement**:

- Let's Encrypt for free SSL certificates
- Redirect HTTP → HTTPS in production
- HSTS headers for browser enforcement

**CORS Configuration**:

- Whitelist specific origins only
- No wildcard (*) in production
- Credentials-aware CORS for cookies (future)

**Rate Limiting** (future):

- Per-IP rate limits on API
- Stricter limits on expensive endpoints (AI summarization)
- Progressive backoff for abuse detection

#### Infrastructure Security

**Server Hardening**:

- Disable root SSH login
- SSH key authentication only (no passwords)
- Firewall rules (UFW/iptables): only 80, 443, SSH
- Automatic security updates enabled

**Database Security**:

- PostgreSQL: Strong password, no public exposure
- SQLite: File permissions 600 (owner read/write only)
- Backup encryption for sensitive deployments

**Container Security**:

- Run containers as non-root user
- Minimal base images (alpine/distroless)
- Regular image rebuilds for security patches

---

## 4. Development Standards

### Code Quality Tools

#### Python (Backend)

**Linting & Formatting**:

- Tool: ruff (replaces black + flake8 + isort)
- Line length: 100 characters
- Target: Python 3.13
- Auto-format on save (VSCode/PyCharm)

**Type Checking**:

- Tool: mypy in strict mode
- All functions must have type hints
- Generic types preferred over Any
- Enforced in pre-commit hooks (future)

**Testing**:

- Framework: pytest with pytest-asyncio
- Coverage target: 70% minimum
- Integration tests with test database
- Mocking via pytest-mock

#### TypeScript (Frontend)

**Linting**:

- ESLint with recommended React rules
- Prettier for formatting (future)
- Import sorting

**Type Safety**:

- Strict mode enabled in tsconfig.json
- No any types without explicit reason
- Props interfaces required for all components

### Git Workflow

#### Branch Strategy

**Default Branch**: develop (not main)

**Branch Types**:

- feature/* - New features
- fix/* - Bug fixes
- refactor/* - Code improvements
- docs/* - Documentation updates
- chore/* - Maintenance tasks

**Workflow**:

1. Create feature branch from develop
2. Work with frequent commits
3. Test thoroughly before merge
4. Merge to develop when complete
5. Delete feature branch after merge

#### Commit Standards

**Format**:

- English language
- Imperative mood (Add feature, not Added feature)
- Clear and concise
- Include Claude Code attribution when AI-assisted

**Example Good Commit**:

- Implement background worker for feed polling
- Add APScheduler integration for automatic feed updates
- Configurable polling interval per source

#### Code Review Checklist

**Before Committing**:

- Code follows style guidelines (ruff/eslint)
- Type hints complete (mypy passes)
- Tests written for new functionality
- No secrets or credentials hardcoded
- Documentation updated (if needed)
- No debug print() statements left
- Error handling implemented

**Before Merging**:

- All tests passing
- No merge conflicts
- Feature tested manually
- Performance impact evaluated (if relevant)

---

## 5. Performance Considerations

### Expected Performance

#### API Response Times

**Target Latency** (95th percentile):

- GET endpoints: < 50ms
- POST/PUT/DELETE: < 100ms
- Feed processing: < 5s (depends on feed size)
- AI summarization: 2-10s (model-dependent)

**Bottlenecks**:

- AI inference is slowest operation
- Database queries optimized with indexes
- Network latency for feed fetching

#### Optimization Strategies

**Database**:

- Indexes on published_at, source_id, content_hash
- Connection pooling (10-20 connections)
- Query optimization with EXPLAIN ANALYZE
- Pagination for large result sets

**Caching** (future):

- Redis for recent news queries (5-minute TTL)
- Source metadata (1-hour TTL)
- AI summaries (permanent until content changes)

**AI Performance**:

- GPU acceleration via Ollama (10x faster than CPU)
- Model quantization for lower memory (Q4_K_M recommended)
- Batch processing for multiple summaries

### Scalability Limits

#### Single Server

**Realistic Capacity**:

- 100-500 concurrent users
- 1000-5000 news items/day processing
- 10-50 AI summaries/minute

**Saturation Points**:

- Database: ~100 writes/second (PostgreSQL)
- API: ~1000 requests/second (FastAPI)
- AI: Limited by GPU memory and model size

#### Horizontal Scaling

**When Needed**: > 1000 active users

**Strategy**:

- Stateless API servers behind load balancer
- PostgreSQL with read replicas
- Redis cluster for distributed caching
- Separate worker pool for background jobs

---

## 6. Known Limitations & Planned Improvements

### Current Limitations

#### Infrastructure

1. **No Background Workers**
   - Feeds must be manually triggered via API
   - No automatic polling or scheduling
   - Impact: Requires user intervention or external cron job
   - Planned: APScheduler or Celery integration

2. **No Caching Layer**
   - All queries hit database directly
   - Repeated requests not optimized
   - Impact: Higher database load, slower response times
   - Planned: Redis integration for hot data

3. **Limited Error Handling**
   - Basic exception catching implemented
   - No retry logic for transient failures
   - Impact: Feed imports may fail unnecessarily
   - Planned: tenacity library for exponential backoff

#### Testing & Quality

1. **No Test Coverage**
   - Test infrastructure configured (pytest)
   - Zero tests written yet
   - Impact: Regressions not caught automatically
   - Planned: 70% coverage target

2. **No Database Migrations**
   - Alembic configured but unused
   - Schema changes require manual DB recreation
   - Impact: Production upgrades risky
   - Planned: Migration workflow establishment

#### Features

1. **Single-User Only**
   - No authentication or authorization
   - One database = one user
   - Impact: Can't share instance across users
   - Future: Multi-tenant support (long-term)

2. **No Feed Registry**
   - Users must manually find feed URLs
   - No starter packs or community sharing
   - Impact: High friction for new users
   - Planned: Community feed registry (see vision.md)

### Resolved Issues

#### Previously Limiting, Now Fixed

✅ **Structured Logging** (Resolved: Oct 2025)

- Was: Using print() statements
- Now: Centralized logging with shared/logging module
- Impact: Production observability significantly improved

✅ **Repository Pattern** (Resolved: Oct 2025)

- Was: Direct ORM queries in endpoints
- Now: Repository layer with Unit of Work
- Impact: Better testability and maintainability

---

## 7. Contributing Guidelines

### Getting Started

**First-Time Setup**:

1. Fork the repository
2. Clone your fork locally
3. Install pre-commit hooks (future)
4. Create a feature branch
5. Make your changes
6. Submit a pull request

### Code Contribution Standards

**What We Accept**:

- Bug fixes with tests
- New features aligned with vision.md
- Performance improvements with benchmarks
- Documentation improvements
- UI/UX enhancements

**What We Don't Accept**:

- Breaking changes without discussion
- Features out of scope (see vision.md)
- Code without tests (for non-trivial changes)
- Undocumented complex code

### Review Process

**Timeline**:

- Initial review: Within 1 week
- Feedback iteration: As needed
- Merge decision: When all checks pass

**Criteria for Approval**:

- Code quality meets standards
- Tests pass and coverage maintained
- Documentation updated
- No security vulnerabilities introduced

---

## 8. Monitoring & Observability (Future)

### Logging Strategy

**Current**: Structured logging to stdout

**Planned**:

- Log aggregation (Loki or ELK stack)
- Log levels configurable per module
- Correlation IDs for request tracing
- Error log alerts

### Metrics Collection

**Planned Metrics**:

- API response times (p50, p95, p99)
- Feed processing throughput
- AI inference latency
- Database query performance
- Cache hit rates

**Tools Considered**:

- Prometheus for metrics collection
- Grafana for visualization
- AlertManager for notifications

### Health Checks

**Endpoints to Add**:

- GET /health - Overall system health
- GET /health/db - Database connectivity
- GET /health/ollama - AI service availability
- GET /health/redis - Cache availability (future)

---

## 9. Backup & Recovery

### Backup Strategy

#### Development

**SQLite Database**:

- Manual backups via file copy
- Frequency: Before major changes
- Location: Local filesystem

#### Production

**Automated Backups**:

- Daily full database dumps
- Incremental backups every 6 hours
- Retention: 30 days rolling
- Off-site storage (S3-compatible)

**What to Backup**:

- Database (PostgreSQL dump)
- Configuration files (settings.json)
- User uploads (future)

**What NOT to Backup**:

- AI model files (re-downloadable)
- Cache data (ephemeral)
- Log files (archived separately)

### Recovery Procedures

**Database Restore**:

- PostgreSQL: Restore from dump file
- SQLite: Replace database file
- Test restore procedure quarterly

**Disaster Recovery**:

- RTO (Recovery Time Objective): 1 hour
- RPO (Recovery Point Objective): 6 hours (incremental backup interval)

---

**Version**: 2.0
**Last Updated**: 25 October 2025
**Maintained By**: Government Feed Contributors
