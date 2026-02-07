# Testing Suite

**Status**: planned
**Milestone**: M2-Production
**Priority**: must-have
**Depends on**: [repository-pattern](../implemented/repository-pattern.md), [rest-api](../implemented/rest-api.md)

## Summary

Comprehensive test suite with pytest and pytest-asyncio covering unit tests for repositories and domain logic, integration tests for API endpoints, with a 70% minimum coverage target.

## User Stories

- As a developer, I want automated tests to catch regressions before deployment
- As a developer, I want to run tests quickly during development (< 30s for unit tests)

## Requirements

### Functional

- [ ] Unit tests for domain entities and value objects
- [ ] Unit tests for repository implementations (with test database)
- [ ] Unit tests for AI service (mocked Ollama)
- [ ] Unit tests for feed parser (mocked HTTP responses)
- [ ] Integration tests for all API endpoints
- [ ] Integration tests for database transactions and UoW
- [ ] Test fixtures for common test data (sources, news items)
- [ ] Test database isolation (in-memory SQLite or temp file)

### Non-Functional

- Coverage: 70% minimum overall, higher for core logic
- Speed: Unit tests < 30s, full suite < 2 minutes
- Isolation: Tests don't affect each other or production data

## Technical Notes

- Frameworks: `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-mock`
- Test structure: `backend/tests/`
  - `unit/` — pure unit tests with mocks
  - `integration/` — tests with real database and HTTP
  - `conftest.py` — shared fixtures
- Fixture strategy:
  - `test_db` — in-memory SQLite session
  - `test_client` — FastAPI TestClient with test database
  - `sample_source`, `sample_news` — domain entity factories
- Mocking strategy:
  - AI service: mock httpx responses from Ollama
  - Feed parser: mock feedparser output
  - External HTTP: mock httpx client for web scraping
- CI integration: run on every push to develop (future)

## Acceptance Criteria

- [ ] `pytest` runs successfully with all tests passing
- [ ] Coverage report shows >= 70% on `backend/src/`
- [ ] Unit tests run in < 30 seconds
- [ ] Tests are isolated (parallel execution possible)
- [ ] Test fixtures are reusable and well-documented
