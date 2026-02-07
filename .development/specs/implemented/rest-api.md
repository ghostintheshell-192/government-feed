# REST API

**Status**: implemented
**Milestone**: M1-MVP
**Priority**: must-have
**Depends on**: repository-pattern.md

## Summary

FastAPI-based REST API providing 11 endpoints for source management, news access, AI summarization, settings configuration, and health monitoring, with automatic OpenAPI documentation.

## User Stories

- As a frontend developer, I want a well-documented REST API to build the UI against
- As a user, I want to interact with all system features via HTTP endpoints
- As an integrator, I want OpenAPI/Swagger documentation for API discovery

## Requirements

### Functional

- [x] Sources endpoints (6): list, get, create, update, delete, process
- [x] News endpoints (2): list recent, get by ID
- [x] AI endpoint (1): trigger summarization for a news item
- [x] Settings endpoints (3): get settings, update settings, feature flags
- [x] Health check: `GET /` returns system status
- [x] Pydantic schema validation on all inputs/outputs
- [x] Automatic OpenAPI/Swagger documentation

### Non-Functional

- Performance: < 50ms for GET, < 100ms for POST/PUT/DELETE (excluding AI)
- Standards: RESTful conventions (proper HTTP methods and status codes)
- Documentation: Interactive Swagger UI at `/docs`

## Technical Notes

- Implementation: `backend/src/api/main.py`
- Schemas: `backend/src/api/schemas.py`
- DI: `backend/src/api/dependencies.py`
- CORS configured for local frontend development
- Full endpoint list:
  - `GET /` — health check
  - `GET /api/sources` — list sources
  - `GET /api/sources/{id}` — get source
  - `POST /api/sources` — create source
  - `PUT /api/sources/{id}` — update source
  - `DELETE /api/sources/{id}` — delete source
  - `POST /api/sources/{id}/process` — process feed
  - `GET /api/news` — list recent news
  - `GET /api/news/{id}` — get news item
  - `POST /api/news/{id}/summarize` — generate AI summary
  - `GET /api/settings` — get settings
  - `PUT /api/settings` — update settings
  - `GET /api/settings/features` — feature flags

## Acceptance Criteria

- [x] All 11 endpoints respond correctly
- [x] Swagger UI accessible at `/docs`
- [x] Input validation via Pydantic prevents malformed requests
- [x] Proper HTTP status codes (200, 201, 204, 400, 404, 500)
- [x] CORS allows frontend access during development
