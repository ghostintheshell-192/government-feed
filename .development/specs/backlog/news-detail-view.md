# News Detail View

**Status**: backlog
**Milestone**: M3-Frontend
**Priority**: must-have
**Depends on**: [dashboard-news-browsing](dashboard-news-browsing.md)

## Summary

Full-screen article view with prominent AI summary display, link to original source, complete metadata, and navigation between articles.

## User Stories

- As a user, I want to read the full article content in a clean layout
- As a user, I want to see the AI summary prominently before the full content
- As a user, I want a direct link to the original institutional source

## Requirements

### Functional

- [ ] Full-screen article layout with clean typography
- [ ] AI summary displayed prominently at the top
- [ ] Link to original source URL (opens in new tab)
- [ ] Metadata display: date, source name, source URL
- [ ] Navigation to previous/next article
- [ ] Back to list navigation preserving scroll position
- [ ] Trigger AI summarization if summary not yet generated

### Non-Functional

- UX: Reading-focused layout, minimal distractions
- Performance: Article loads in < 500ms
- Accessibility: Proper heading hierarchy, readable fonts

## Technical Notes

- Route: `/news/{id}` with React Router
- Integrate with `GET /api/news/{id}` and `POST /api/news/{id}/summarize`
- Preserve list scroll position when navigating back
- Consider sharing/bookmarking functionality (future)

## Acceptance Criteria

- [ ] Article displays with clean, readable layout
- [ ] AI summary is prominently visible
- [ ] Original source link works correctly
- [ ] All metadata is displayed
- [ ] Navigation between articles works
- [ ] Back navigation preserves list state
