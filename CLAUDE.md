# Government Feed - Claude Project Context

## Project Overview
Government Feed is a specialized news aggregator that centralizes, filters, and contextualizes information from official government and institutional sources. Built with Python/FastAPI following Clean Architecture principles.

**Migration Note**: This project was migrated from a C#/.NET 8 implementation. The backup is available in `/data/repos/government-feed-csharp-backup/`.

## Development Environment
- **Platform**: Linux Debian 12 with VSCode
- **Language**: Python 3.13
- **Framework**: FastAPI 0.115+
- **Architecture**: Clean Architecture (core → infrastructure → api)
- **Database**: SQLite (dev) / PostgreSQL (prod) with SQLAlchemy 2.0
- **Frontend**: React 18 + TypeScript + Vite
- **AI Integration**: Local models via Ollama (privacy-first)
- **Package Management**: pyproject.toml with hatchling

## Current Project Status

### ✅ COMPLETED

1. **Backend Structure** - FULLY IMPLEMENTED:
   - Core entities: NewsItem, Source, Category with domain methods
   - Value objects: VerificationStatus enum
   - Content hashing for deduplication
   - Domain methods: update_content_hash(), mark_as_verified()

2. **Infrastructure Layer** - FULLY IMPLEMENTED:
   - SQLAlchemy ORM models (Source, NewsItem)
   - Database setup with init_db() and get_db()
   - Feed parser service (RSS/Atom support with feedparser)
   - AI service integration with Ollama
   - Settings store (JSON-based configuration)

3. **API Layer** - FULLY IMPLEMENTED:
   - FastAPI application with CORS middleware
   - Source CRUD endpoints (GET, POST, PUT, DELETE)
   - News retrieval endpoints
   - Feed processing endpoint (/api/sources/{id}/process)
   - AI summarization endpoint (/api/news/{id}/summarize)
   - Settings management endpoints
   - Feature flags endpoint

4. **Configuration** - COMPLETED:
   - pyproject.toml with dependencies and dev tools
   - ruff for linting (line-length=100, py313 target)
   - mypy for static type checking (strict mode)
   - Docker Compose for services
   - .gitignore configured

### 🔄 IN PROGRESS
- **Frontend**: React application structure exists but needs review
- **Testing**: Test infrastructure configured but tests need to be written
- **Documentation**: docs/ folder needs to be migrated from C# project

### ⏳ PENDING (Priority Order)

1. **Infrastructure Enhancements**:
   - Repository pattern implementations (if needed for better abstraction)
   - Caching layer with Redis (dependency already in pyproject.toml)
   - Web scraping service with BeautifulSoup4
   - Database migrations with Alembic

2. **Application Layer**:
   - Service layer for business logic
   - DTO validation with Pydantic
   - Use cases for complex operations
   - Background task processing

3. **Frontend Development**:
   - Dashboard components
   - News browsing interface
   - Settings management UI
   - Real-time updates integration

4. **Worker Services**:
   - Background feed polling
   - Scheduled content analysis
   - Periodic AI summarization jobs

5. **Testing**:
   - Unit tests with pytest
   - Integration tests for API
   - Test coverage reporting with pytest-cov

6. **Advanced Features**:
   - Blockchain verification integration
   - Advanced AI analysis and scoring
   - Multi-language support
   - Export functionality

7. **Git Repository**:
   - Initialize Git repository
   - Create develop branch as default
   - Set up proper branch workflow

## Key Technical Decisions Made

### Architecture
- **Clean Architecture**: Separation of concerns with core/infrastructure/api layers
- **Python 3.13**: Latest Python version with modern type hints
- **FastAPI**: Async-first web framework with automatic OpenAPI documentation
- **SQLAlchemy 2.0**: Modern ORM with async support

### Domain Design
- **Dataclasses**: Using Python dataclasses for domain entities
- **Type Hints**: Full type annotation throughout codebase
- **Content Hashing**: SHA256 for deduplication using title|content|source|date
- **Verification Status**: Enum-based status tracking

### Data Layer
- **SQLAlchemy ORM**: Declarative models with proper indexing
- **Migration Strategy**: Alembic ready for schema evolution
- **Database Flexibility**: SQLite for dev, PostgreSQL for production

### AI Integration
- **Local Processing**: Ollama integration for privacy-first AI
- **Async Operations**: Using httpx for non-blocking AI requests
- **Configurable Models**: Model selection via settings

## File Locations Reference

### Backend Structure
```
backend/
├── src/
│   ├── core/
│   │   ├── __init__.py ✅
│   │   └── entities.py ✅ (NewsItem, Source, Category, VerificationStatus)
│   ├── infrastructure/
│   │   ├── __init__.py ✅
│   │   ├── database.py ✅ (SQLAlchemy setup)
│   │   ├── models.py ✅ (ORM models)
│   │   ├── feed_parser.py ✅ (RSS/Atom parsing)
│   │   ├── ai_service.py ✅ (Ollama integration)
│   │   └── settings_store.py ✅ (JSON config)
│   └── api/
│       ├── __init__.py ✅
│       ├── main.py ✅ (FastAPI app + all endpoints)
│       └── schemas.py ✅ (Pydantic schemas)
└── pyproject.toml ✅
```

### Frontend Structure
```
frontend/
├── src/ ⏳ (React components - needs review)
├── package.json ⏳
└── vite.config.ts ⏳
```

### Root Files
```
/
├── docker-compose.yml ✅ (Ollama + services)
├── settings.json ✅ (Runtime settings)
├── government_feed.db ✅ (SQLite database)
├── CLAUDE.md ✅ (This file)
├── README.md ✅
├── LICENSE ✅ (MIT)
├── .gitignore ✅
└── docs/ ⏳ (To be migrated from C# project)
```

## Next Development Steps

### Immediate Priority (Next Session)

1. **Initialize Git Repository**:
   - `git init`
   - Create develop branch
   - Initial commit with current state
   - Set up branch workflow

2. **Migrate Documentation**:
   - Copy docs/ folder from government-feed-csharp-backup
   - Update references from C# to Python where needed
   - Preserve vision and roadmap documents

3. **Compare Functionality**:
   - Analyze C# implementation features
   - Identify missing functionality in Python version
   - Create migration checklist

4. **Frontend Review**:
   - Explore React application structure
   - Verify integration with backend API
   - Identify UI improvements needed

### Development Workflow

Following the global CLAUDE.md rules:

1. **Always work on feature branches** (never on main)
2. **One feature/fix per branch**
3. **Build and test before commit**
4. **Atomic commits** with clear messages

### Testing Strategy
```bash
# Run tests
pytest

# With coverage
pytest --cov=backend/src

# Type checking
mypy backend/src

# Linting
ruff check backend/src
```

### Running the Application
```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn backend.src.api.main:app --reload

# Frontend
cd frontend
pnpm install
pnpm dev

# Services (Ollama)
docker-compose up -d
```

## Important Notes

- **Python 3.13**: Using latest Python with modern syntax (union types with |)
- **Privacy Focus**: All AI processing happens locally via Ollama
- **Clean Architecture**: Strict separation of layers with proper dependency direction
- **Type Safety**: mypy strict mode enforced
- **Code Quality**: ruff for linting and formatting
- **Migration**: Some C# concepts translated to Python idioms

## Documentation References

- Vision: `docs/government-feed-visione.md` (to be migrated)
- Technical Spec: `docs/government-feed-tecnico.md` (to be migrated)
- Architecture: `docs/governmentfeed-architecture.md` (to be migrated)
- Roadmap: `docs/government-feed-roadmap.md` (to be migrated)
- Concept: `docs/government-feed-concept.md` (to be migrated)
- Blockchain Integration: `docs/government-feed-blockchain-integration.md` (to be migrated)

## Migration Notes from C# Version

### Implemented Features (Python ≈ C# parity)
✅ Core entities and domain models
✅ Database layer with ORM
✅ Feed parsing (RSS/Atom)
✅ AI integration with Ollama
✅ Content deduplication via hashing
✅ Basic CRUD operations
✅ Settings management

### Not Yet Migrated
⏳ Repository pattern abstraction
⏳ CQRS/MediatR pattern
⏳ Worker services for background jobs
⏳ Blazor UI → React UI (intentionally redesigned)
⏳ Unit tests and integration tests
⏳ Advanced caching layer
⏳ Blockchain verification implementation

### Architectural Differences
- **C#**: Separate Application/Domain/Infrastructure/Presentation projects
- **Python**: Simpler core/infrastructure/api structure (more Pythonic)
- **C#**: Heavy use of interfaces and DI container
- **Python**: Dataclasses and function-based design
- **C#**: Blazor Server for UI
- **Python**: React + TypeScript (modern SPA)

This project maintains the vision and goals of the C# version while embracing Python's ecosystem and idioms.
