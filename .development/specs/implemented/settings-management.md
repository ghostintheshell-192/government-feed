# Settings Management

**Status**: implemented
**Milestone**: M1-MVP
**Priority**: should-have
**Depends on**: rest-api.md

## Summary

JSON-based runtime configuration system for managing application settings (Ollama endpoint/model, AI toggle, summary parameters) with persistence and API access.

## User Stories

- As a user, I want to configure the AI model and endpoint without restarting the application
- As a user, I want to enable/disable AI summarization on the fly
- As a user, I want to control summary length (max words)

## Requirements

### Functional

- [x] JSON file-based settings persistence (`settings.json`)
- [x] Runtime-configurable Ollama endpoint URL
- [x] Runtime-configurable Ollama model name
- [x] Toggle AI summarization on/off (`ai_enabled`)
- [x] Configurable `summary_max_words` parameter
- [x] API endpoints for reading and updating settings
- [x] Feature flags endpoint

### Non-Functional

- Persistence: Settings survive application restarts
- Validation: Invalid settings rejected with clear error messages

## Technical Notes

- Implementation: `backend/src/infrastructure/settings_store.py`
- Storage: `settings.json` file in project root
- API endpoints:
  - `GET /api/settings` — read current settings
  - `PUT /api/settings` — update settings
  - `GET /api/settings/features` — feature flags
- Default values applied when settings file is missing

## Acceptance Criteria

- [x] Settings are persisted to disk as JSON
- [x] Settings are readable and writable via API
- [x] Default values are applied for missing settings
- [x] AI service uses current settings for each request
- [x] Invalid settings are rejected with appropriate error
