# Git Workflow & Development Commands

## Git Workflow

**Quick reference:**

- `main`: releases only
- `develop`: default branch for development
- `feature/*`, `fix/*`, `docs/*`, `experiment/*`: task branches

**NEVER work on main directly.**

**ALWAYS run git commands from the project root** (`/data/repos/government-feed`). Before staging or committing, verify `pwd` — subdirectories cause path mismatches.

**Typical workflow:**

```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/task-name

# Work and commit
git add .
git commit -m "feat: descriptive message"

# Merge when complete
git checkout develop
git merge feature/task-name
git push origin develop
```

## Investigation & Analysis Workflow

When analyzing tech-debt, bugs, or investigating issues:

1. **Read the tech-debt/issue description** - Understand the problem
2. **Read `.development/ARCHITECTURE.md`** - Find relevant files using:
   - Project Tree (file index with descriptions)
   - Layer Overview (understand dependencies)
   - Related ADRs (architectural context)
3. **Read files in logical order** - Follow layer structure (Core <- Infrastructure -> API)
4. **Report findings** - Summary of what you found and where

**Always read ARCHITECTURE.md before exploring code** - it's your navigation map.

## Quick Commands

```bash
# Backend - run
cd backend && uvicorn backend.src.api.main:app --reload

# Frontend - run
cd frontend && pnpm dev

# Linting
ruff check backend/src

# Type checking
mypy backend/src

# Tests
pytest

# Tests with coverage
pytest --cov=backend/src

# Docker services (Redis, Ollama)
docker-compose up -d
```
