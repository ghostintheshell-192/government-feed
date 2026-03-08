# Feed Administration Tools

**Status**: planned
**Milestone**: M3.1 (API endpoints), M4a (admin UI)
**Priority**: must-have
**Depends on**: [source-management](../implemented/source-management.md), [rest-api](../implemented/rest-api.md)

## Summary

Backend API endpoints and (later) an admin UI for inspecting, diagnosing, and cleaning up feed content — filling the gap between automated monitoring and human judgment on content quality.

## Motivation

Automated health monitoring (see [feed-health-monitor](feed-health-monitor.md)) detects *technical* failures (HTTP errors, dead URLs), but cannot judge *semantic* quality: a feed that returns staff bios instead of press releases is technically healthy but useless. Users need tools to quickly inspect what each feed is importing and correct problems.

## User Stories

- As an admin, I want to see what a specific feed is importing so I can judge content quality
- As an admin, I want to purge and re-import a feed after correcting its URL
- As an admin, I want to bulk-delete articles matching a pattern (e.g., all staff bios)
- As an admin, I want an overview of database health: articles per source, orphans, anomalies
- As an admin, I want to spot suspicious content: articles with residual HTML, duplicates, or unusually short/long text

## Requirements

### Phase 1 — API Endpoints (M3.1, no auth)

#### Feed Inspector

- [ ] `GET /api/admin/sources/{id}/preview` — last N articles from a specific source (title, date, snippet)
- [ ] `GET /api/admin/sources/{id}/stats` — article count, date range, avg content length, last fetch status

#### Content Cleanup

- [ ] `POST /api/admin/sources/{id}/purge` — delete all articles for a source (keeps the source record)
- [ ] `POST /api/admin/sources/{id}/reimport` — purge + trigger immediate re-import
- [ ] `POST /api/admin/cleanup/by-pattern` — delete articles matching title/content pattern (with dry-run mode)
- [ ] `POST /api/admin/cleanup/html-residue` — find and fix articles still containing HTML tags
- [ ] `POST /api/admin/cleanup/orphans` — delete articles whose source_id references a deleted source

#### Diagnostics

- [ ] `GET /api/admin/stats` — global DB stats: total articles, per-source counts, storage, articles/day trend
- [ ] `GET /api/admin/quality-report` — flag suspicious content:
  - Articles shorter than 50 chars
  - Articles longer than 50,000 chars
  - Articles with HTML tags in content or summary
  - Duplicate titles within same source
  - Sources with 0 articles

### Phase 2 — Admin UI (M4a)

- [ ] Admin page in frontend (accessible to all in single-user mode)
- [ ] Feed inspector: select source → see recent articles, stats, quality flags
- [ ] One-click purge/reimport per source
- [ ] Cleanup actions with confirmation dialogs
- [ ] DB stats dashboard with per-source breakdown
- [ ] When multi-user auth lands (M5): protect admin routes with role-based access

### Non-Functional

- Safety: destructive operations require confirmation (dry-run by default for bulk delete)
- Performance: stats queries should be efficient (use COUNT/GROUP BY, not load-all)
- Auditability: all admin actions logged with structured logging

## Technical Design

### API Structure

All admin endpoints live under `/api/admin/` prefix. In single-user mode (current), no auth required. When M5 auth lands, add middleware:

```python
# Future: role check middleware
async def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin access required")
```

### Pattern Cleanup (dry-run)

```
POST /api/admin/cleanup/by-pattern
Body: {
  "field": "title",           // "title" | "content"
  "pattern": "Executive Leadership",
  "source_id": 20,            // optional: limit to one source
  "dry_run": true             // default true — returns count without deleting
}

Response (dry_run=true):
{ "matched": 8, "dry_run": true, "message": "8 articles would be deleted" }

Response (dry_run=false):
{ "matched": 8, "deleted": 8, "dry_run": false }
```

### Quality Report Response

```json
{
  "total_articles": 450,
  "total_sources": 22,
  "issues": {
    "short_content": [{"id": 123, "title": "...", "length": 20}],
    "html_residue": [{"id": 456, "title": "...", "field": "summary"}],
    "duplicate_titles": [{"title": "...", "count": 3, "source_id": 5}],
    "empty_sources": [{"id": 7, "name": "Defunct Feed", "article_count": 0}]
  }
}
```

### File Organization

```
backend/src/api/
├── main.py              # Existing — add admin router
├── admin_routes.py      # New — all /api/admin/ endpoints
```

## Acceptance Criteria

### Phase 1 (M3.1)

- [ ] Feed inspector shows recent articles and stats for any source
- [ ] Purge removes all articles for a source without deleting the source
- [ ] Reimport purges and triggers immediate fetch
- [ ] Pattern cleanup supports dry-run mode
- [ ] HTML residue cleanup finds and fixes dirty content
- [ ] Orphan cleanup removes articles with no matching source
- [ ] Quality report identifies all issue categories
- [ ] All destructive actions are logged

### Phase 2 (M4a)

- [ ] Admin page accessible in frontend
- [ ] All Phase 1 capabilities available through UI
- [ ] Destructive actions require confirmation dialog

## Open Questions

- Should the quality report run on-demand or be cached/scheduled?
- Should pattern cleanup support regex, or is simple substring matching sufficient?
- Should there be an "undo" for purge operations (soft delete with TTL)?
