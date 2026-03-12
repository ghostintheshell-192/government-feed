# Bulk Fetch Content for All Sources

**Status**: planned
**Milestone**: M4a-Feed-Infrastructure
**Priority**: should-have
**Depends on**: [source-catalog-subscriptions](source-catalog-subscriptions.md)

## Summary

Add an endpoint to fetch full article content for all subscribed sources at once, not one source at a time. Useful for initial setup and for the admin page.

## Current State

- `POST /api/admin/sources/{source_id}/fetch-content` — fetches content for one source (streams NDJSON progress)
- No way to trigger this for all sources at once

## Requirements

- [ ] `POST /api/admin/bulk-fetch-all` — fetches content for all subscribed (or all active) sources
- [ ] Streams progress as NDJSON (same format as per-source endpoint)
- [ ] Respects polite delay between requests
- [ ] Skips articles that already have substantial content (unless `force=True`)
- [ ] Frontend: button in admin page to trigger bulk fetch for all sources

## Technical Notes

- Iterates over subscribed sources, for each runs the same logic as the per-source endpoint
- Could reuse `ContentScraper` and the existing streaming pattern
- Consider a global progress indicator: "Source 3/15 — Article 12/42"
- Rate limiting is important: hundreds of sources × dozens of articles = thousands of requests
