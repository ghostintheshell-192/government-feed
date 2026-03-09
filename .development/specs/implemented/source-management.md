# Source Management

**Status**: implemented
**Milestone**: M1-MVP
**Priority**: must-have
**Depends on**: repository-pattern.md, rest-api.md

## Summary

Full CRUD management for institutional feed sources, allowing users to add, configure, and manage the RSS/Atom feeds they want to follow.

## User Stories

- As a user, I want to add new institutional feed sources by URL
- As a user, I want to view all my configured sources and their status
- As a user, I want to edit source details (name, URL, active status)
- As a user, I want to delete sources I no longer need
- As a user, I want to manually trigger feed processing for a specific source

## Requirements

### Functional

- [x] Create source with name, feed URL, and optional description
- [x] Read single source by ID with full details
- [x] List all sources with status information
- [x] Update source name, URL, description, and is_active flag
- [x] Delete source and associated data
- [x] Trigger manual feed processing per source
- [x] Track last_fetched timestamp per source

### Non-Functional

- Validation: Feed URL format validation via Pydantic
- Consistency: Atomic operations via Unit of Work pattern

## Technical Notes

- 6 API endpoints under `/api/sources`:
  - `GET /api/sources` — list all
  - `GET /api/sources/{id}` — get by ID
  - `POST /api/sources` — create new
  - `PUT /api/sources/{id}` — update
  - `DELETE /api/sources/{id}` — delete
  - `POST /api/sources/{id}/process` — trigger feed processing
- Source model: `backend/src/infrastructure/models.py`
- Repository interface: `backend/src/core/repositories/source_repository.py`
- Repository implementation: `backend/src/infrastructure/repositories/source_repository.py`
- Pydantic schemas: `backend/src/api/schemas.py`

## Acceptance Criteria

- [x] All 6 CRUD + process endpoints are functional
- [x] Input validation prevents malformed data
- [x] Source deletion is handled cleanly
- [x] last_fetched updates after successful processing
- [x] API returns appropriate HTTP status codes (201, 200, 204, 404)
