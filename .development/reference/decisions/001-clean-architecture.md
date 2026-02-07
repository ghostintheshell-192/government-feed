# ADR-001: Clean Architecture

**Date**: 2025-10-25
**Status**: Active
**Impact**: critical

## Context

The project needs a clear separation of concerns to allow independent evolution of business logic, data access, and presentation. The original C# implementation used Clean Architecture with separate projects; the Python migration needs an equivalent approach.

## Decision

Adopt Clean Architecture with three layers:

- **Core** (`backend/src/core/`): Domain entities, value objects, repository interfaces (abstract base classes)
- **Infrastructure** (`backend/src/infrastructure/`): Database models, repository implementations, external services (feed parser, AI, settings)
- **API** (`backend/src/api/`): FastAPI endpoints, Pydantic schemas, CORS configuration

## Rationale

- Proven pattern from the C# version, adapted to Python idioms
- Core layer has zero dependencies on frameworks (no SQLAlchemy, no FastAPI imports)
- Infrastructure implements core interfaces, allowing substitution (e.g., SQLite -> PostgreSQL)
- API layer handles HTTP concerns only, delegates to infrastructure

## Consequences

- **Positive**: Testable core logic, swappable infrastructure, clear dependency direction
- **Negative**: More files than a simple flat structure, requires discipline to maintain layer boundaries
- **Risk**: Python's lack of compile-time interface enforcement means violations must be caught by review
