# Government Feed

An open-source aggregator that centralizes news and communications from official government and institutional sources, making them accessible, filterable, and understandable.

Government sources (central banks, ministries, regulatory agencies) publish information daily that directly impacts citizens' lives — but it's scattered across dozens of websites, buried in bureaucratic language, and filtered through media interpretation. Government Feed gives you direct access to primary sources, with local AI summarization to cut through the complexity.

**Key principles**: privacy-first (all AI processing runs locally via Ollama), no cloud dependencies, fully open source.

## What this tool will not do

Government Feed shows you evidence so that *you* judge it. It does not build a
profile of anyone — and that cuts both ways:

- **It does not profile you.** What you read is not used to decide what you
  see next. There is no behavioural tracking and no engagement optimization:
  you choose your sources and your topics explicitly, and that is the only
  preference the system knows about.
- **It does not profile news outlets.** When press coverage is shown next to
  the primary document it refers to, that is a per-item, verifiable fact with
  links you can check. The tool computes no bias score, no reliability
  ranking, no verdict about any publisher.

Where the system does form an opinion, it is only ever about the **form** of a
piece of information — is this a fact or an opinion, is it urgent or
evergreen — never about which position is right.

The reason is not caution. A tool built to reduce your dependence on someone
else's judgement has no business substituting its own.

See [ADR-009](.development/reference/decisions/009-no-profiling-readers-or-publishers.md)
for the full decision and its consequences.

## Current Status

<!-- AUTO:STATUS -->
✅ **MVP Backend** (9/9 features)

✅ **Production-Ready Backend** (5/5 features)

✅ **Frontend** (3/3 features)

📋 **Scaling & Multi-User** (0/1 features)
- [ ] Multi-User Authentication

<!-- /AUTO:STATUS -->

> Auto-generated from [feature specs](.development/specs/). See [docs/roadmap.md](docs/roadmap.md) for detailed planning.

## Roadmap

| | Milestone | Description | Progress |
|---|-----------|-------------|----------|
<!-- AUTO:ROADMAP -->
| ✅ M1-MVP | MVP Backend | 9/9 |
| ✅ M2-Production | Production-Ready Backend | 5/5 |
| ✅ M3-Frontend | Frontend | 3/3 |
| 📋 M5-Scaling | Scaling & Multi-User | 0/1 |
<!-- /AUTO:ROADMAP -->

See [docs/vision.md](docs/vision.md) for the full project vision and [docs/roadmap.md](docs/roadmap.md) for detailed milestone planning.

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.13 + FastAPI | Async API with OpenAPI docs |
| **Frontend** | React 18 + TypeScript + Vite | SPA interface |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Data persistence |
| **Migrations** | Alembic | Schema version control |
| **Cache** | Redis 7 | Response caching with graceful fallback |
| **AI** | Ollama (DeepSeek-R1) | Local summarization, no cloud |
| **UI** | Tailwind CSS + shadcn/ui | Component library with dark mode |
| **Quality** | ruff + mypy (strict) + pytest | Linting, type checking, 177 tests |

**Architecture**: Clean Architecture with Repository Pattern and Unit of Work. Dependencies flow inward: API → Infrastructure → Core.

## Getting Started

### Prerequisites

- Python 3.13+
- Node.js 18+ with npm
- Docker and Docker Compose (for Redis and Ollama)

### Installation

```bash
# Clone
git clone https://github.com/ghostintheshell-192/government-feed.git
cd government-feed

# Backend
python -m venv .venv
source .venv/bin/activate
cd backend && pip install -e ".[dev]" && cd ..

# Frontend
cd frontend && npm install && cd ..

# Project automation: git hooks (branch protection, security, derived docs)
bash .development/automation/bootstrap.sh

# Services (Redis + Ollama)
docker-compose up -d

# Pull AI model
docker exec government-feed-ollama ollama pull deepseek-r1:7b
```

### Running

```bash
# Backend — MUST run from the project root (imports resolve as backend.src.*)
uvicorn backend.src.api.main:app --reload

# Frontend (separate terminal)
cd frontend && npm run dev
```

- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

### Verify

```bash
# Health check
curl http://localhost:8000/

# Run tests (from project root)
PYTHONPATH=. .venv/bin/pytest backend/tests/ -v
# or: .development/automation/test.sh backend

# Lint + type check
.venv/bin/ruff check backend/src
.venv/bin/mypy backend/src --ignore-missing-imports --no-namespace-packages
```

## Project Structure

See [`.development/ARCHITECTURE.md`](.development/ARCHITECTURE.md) for the full annotated project tree.

```text
government-feed/
├── backend/
│   ├── src/
│   │   ├── api/            # FastAPI endpoints and schemas
│   │   ├── core/           # Domain entities and interfaces
│   │   └── infrastructure/ # Database, cache, AI, feed parser
│   ├── alembic/            # Database migrations
│   └── tests/              # Unit and integration tests
├── frontend/               # React + TypeScript SPA
├── shared/                 # Cross-cutting concerns (logging)
├── .githooks/              # Git hooks (pre-commit, pre-push, post-checkout)
├── docs/                   # Vision, concept, roadmap, architecture
└── docker-compose.yml      # Redis + Ollama services
```

## Contributing

Contributions are welcome. The project uses feature branches (`feature/*`, `fix/*`) merged into `develop`.

Setup:
- Run `git config core.hooksPath .githooks` to enable project hooks

Before submitting:
- Run `ruff check backend/src` (zero errors)
- Run `mypy backend/src --ignore-missing-imports --no-namespace-packages`
- Run `pytest backend/tests/` (all passing)

The pre-push hook runs the test suite automatically. Pre-commit hooks check for secrets and update auto-generated files.

## License

MIT License — see [LICENSE](LICENSE) file.
