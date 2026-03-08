# Data Export

**Status**: backlog
**Milestone**: M4a-Feed-Infrastructure
**Priority**: nice-to-have
**Depends on**: [rest-api](../implemented/rest-api.md), [dashboard-news-browsing](dashboard-news-browsing.md)

## Summary

Multi-format data export capabilities including CSV for analysis, PDF reports, JSON API for integrations, custom RSS feed generation, and webhook support for external services.

## User Stories

- As a user, I want to export news data as CSV for external analysis
- As a user, I want periodic PDF reports of important news
- As an integrator, I want a JSON API and webhooks for building on top of Government Feed

## Requirements

### Functional

- [ ] CSV export of news items (with filters: date range, source, category)
- [ ] PDF report generation (daily/weekly digest format)
- [ ] JSON API export endpoint for external consumption
- [ ] Custom RSS feed generation from filtered news
- [ ] Webhook integration for real-time event notifications

### Non-Functional

- Performance: CSV/JSON exports < 5s for typical data volumes
- Standards: RSS 2.0 compliant feed output
- Compatibility: CSV readable by Excel/Google Sheets

## Technical Notes

- CSV: Python `csv` module, streamed response for large datasets
- PDF: `reportlab` or `weasyprint` library
- RSS: generate valid RSS 2.0 XML from news items
- Webhooks: HTTP POST to configured URLs on new items
- API endpoint design:
  - `GET /api/export/csv?from=&to=&source=`
  - `GET /api/export/pdf?period=weekly`
  - `GET /api/feed/rss?source=&category=`
- Webhook configuration via settings API

## Acceptance Criteria

- [ ] CSV export produces valid, importable files
- [ ] PDF reports are readable and well-formatted
- [ ] RSS feed validates against RSS 2.0 specification
- [ ] Webhooks fire on new news items
- [ ] All exports respect applied filters
