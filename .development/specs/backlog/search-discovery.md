# Search & Discovery

**Status**: backlog
**Milestone**: M3-Frontend
**Priority**: should-have
**Depends on**: [dashboard-news-browsing](dashboard-news-browsing.md), [rest-api](../implemented/rest-api.md)

## Summary

Full-text search across news titles and content with combined filters, saved searches, and search suggestions for efficient information discovery.

## User Stories

- As a user, I want to search for specific topics across all news items
- As a user, I want to save frequent searches for quick access
- As a user, I want search suggestions based on my history

## Requirements

### Functional

- [ ] Full-text search on title and content fields
- [ ] Combined search + filters (source, date range)
- [ ] Search result highlighting (matched terms)
- [ ] Saved searches with custom names
- [ ] Recent search history
- [ ] Search suggestions based on popular/recent terms

### Non-Functional

- Performance: Search results < 500ms for typical queries
- UX: Results update as user types (debounced)

## Technical Notes

- Backend: may need dedicated search endpoint or enhanced `GET /api/news` with `q` parameter
- SQLite: use FTS5 extension for full-text search
- PostgreSQL: use `tsvector` + `tsquery` for full-text search
- Frontend: debounced input (300ms), result highlighting
- Saved searches stored in localStorage initially, backend persistence later

## Acceptance Criteria

- [ ] Search returns relevant results across title and content
- [ ] Search can be combined with source and date filters
- [ ] Matched terms are highlighted in results
- [ ] Saved searches are persisted and accessible
- [ ] Search is responsive (< 500ms for typical queries)
