# Feed Parsing

**Status**: implemented
**Milestone**: M1-MVP
**Priority**: must-have
**Depends on**: —

## Summary

RSS/Atom feed aggregation service that fetches, parses, and normalizes content from institutional sources into a unified format.

## User Stories

- As a user, I want to add an institutional RSS/Atom feed URL so that its content is automatically imported
- As a user, I want the system to handle different feed formats (RSS 2.0, Atom) transparently
- As a user, I want to trigger feed processing manually for a specific source

## Requirements

### Functional

- [x] Parse RSS 2.0 and Atom feeds via `feedparser` library
- [x] Extract title, content, published date, and URL from feed entries
- [x] Strip HTML tags from content to get clean text
- [x] Handle date parsing across different timezone and format conventions
- [x] Normalize entries into `NewsItem` domain entities
- [x] Support manual trigger via `POST /api/sources/{id}/process`

### Non-Functional

- Performance: Feed fetch + parse < 5s per source
- Reliability: Graceful handling of malformed feeds
- Logging: Structured log entries for each processing step (items processed, added, skipped)

## Technical Notes

- Implementation: `backend/src/infrastructure/feed_parser.py`
- Uses `feedparser` library for RSS/Atom parsing
- Uses `httpx` async client for fetching feed content
- HTML stripping via built-in utilities
- Integrates with `NewsRepository` for persistence and `AIService` for summarization
- Processing flow: fetch feed → parse entries → deduplicate → enrich with AI → persist
- See [ADR-001](../../reference/decisions/001-clean-architecture.md) for layer placement

## Acceptance Criteria

- [x] RSS 2.0 feeds are parsed correctly
- [x] Atom feeds are parsed correctly
- [x] HTML tags are stripped from content
- [x] Dates are parsed into consistent datetime objects
- [x] Malformed entries are skipped with warning log
- [x] Processing metrics logged (items processed, added, skipped)
