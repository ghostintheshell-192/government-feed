# Repository Pattern

**Status**: implemented
**Milestone**: M1-MVP
**Priority**: must-have
**Depends on**: —

## Summary

Repository + Unit of Work pattern that abstracts data access behind interfaces defined in core, with concrete SQLAlchemy implementations in infrastructure, enabling testability and database portability.

## User Stories

- As a developer, I want data access abstracted so business logic is independent of the database
- As a developer, I want to easily mock repositories in unit tests

## Requirements

### Functional

- [x] Abstract base classes for `INewsRepository` and `ISourceRepository` in core layer
- [x] Concrete SQLAlchemy implementations in infrastructure layer
- [x] Unit of Work pattern for transaction coordination
- [x] Lazy initialization of repositories in UoW
- [x] Centralized commit/rollback via UoW
- [x] Dependency injection via FastAPI `Depends`

### Non-Functional

- Architecture: Core has no knowledge of infrastructure (dependency inversion)
- Testability: Repositories mockable for unit testing

## Technical Notes

- Core interfaces: `backend/src/core/repositories/`
  - `news_repository.py` — `INewsRepository` ABC
  - `source_repository.py` — `ISourceRepository` ABC
- Infrastructure implementations: `backend/src/infrastructure/repositories/`
  - `news_repository.py` — SQLAlchemy `NewsRepository`
  - `source_repository.py` — SQLAlchemy `SourceRepository`
- Unit of Work: `backend/src/infrastructure/unit_of_work.py`
- DI helpers: `backend/src/api/dependencies.py`
- Key repository methods: `get_by_id`, `get_all`, `get_recent`, `get_by_content_hash`, `search`, `get_by_date_range`, `add`, `update`, `delete`
- See [ADR-001](../../reference/decisions/001-clean-architecture.md)

## Acceptance Criteria

- [x] Core interfaces have no infrastructure imports
- [x] Infrastructure implements all core interfaces
- [x] UoW manages transaction lifecycle (commit/rollback)
- [x] Repositories are injected via FastAPI dependency system
- [x] Database session lifecycle is properly managed
