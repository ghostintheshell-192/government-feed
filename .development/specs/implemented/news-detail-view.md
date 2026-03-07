# News Detail View

**Status**: implemented
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

- [x] Full-screen article layout with clean typography
- [x] AI summary displayed prominently (blue card)
- [x] Link to original source URL (opens in new tab)
- [x] Metadata display: date, source name, source badge
- [ ] Navigation to previous/next article (not implemented)
- [x] Back to list navigation
- [x] Trigger AI summarization if summary not yet generated
- [x] On-demand article content fetching

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

- [x] Article displays with clean, readable layout
- [x] AI summary is prominently visible
- [x] Original source link works correctly
- [x] All metadata is displayed
- [ ] Navigation between articles (not yet)
- [x] Back navigation works
