# Dashboard & News Browsing

**Status**: implemented
**Milestone**: M3-Frontend
**Priority**: must-have
**Depends on**: [frontend-base](../implemented/frontend-base.md), [rest-api](../implemented/rest-api.md)

## Summary

Main dashboard with infinite scroll news feed, filtering by source/date/keyword, read/unread indicators, and paginated navigation for efficient news browsing.

## User Stories

- As a user, I want to see recent news in a scrollable feed on the main page
- As a user, I want to filter news by source, date range, or keyword
- As a user, I want to see which news items I haven't read yet
- As a user, I want the list to load more items as I scroll down

## Requirements

### Functional

- [x] Load-more pagination for news list ("Carica altre notizie" button)
- [x] Filter by source (single or multiple)
- [x] Filter by date range (from/to)
- [x] Filter by keyword (free text search on title)
- [x] Visual indicators for new/unread items (blue dot, localStorage)
- [x] Summary preview in list view
- [x] Responsive layout (desktop and tablet)

### Non-Functional

- Performance: Initial load < 1s, scroll load < 500ms
- UX: Filters persist across navigation
- Accessibility: Keyboard navigable, screen reader compatible

## Technical Notes

- Build on existing React 18 + TypeScript scaffold
- Integrate with `GET /api/news` endpoint (needs pagination params)
- May require backend changes: add query params for filtering and pagination
- State management: React Query for data fetching and caching
- Technologies planned: TailwindCSS for styling (see [ui-preferences](ui-preferences.md))

## Acceptance Criteria

- [x] News feed loads and displays correctly
- [x] Load-more pagination loads additional items
- [x] All filters work correctly and can be combined
- [x] Read/unread state is visually distinct
- [x] Page is responsive on desktop and tablet
