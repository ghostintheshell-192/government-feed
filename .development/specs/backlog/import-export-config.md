# Import/Export Configuration

**Status**: backlog
**Milestone**: M4-Advanced
**Priority**: should-have
**Depends on**: [source-management](../implemented/source-management.md)

## Summary

JSON-based export and import of feed configurations, enabling backup, sharing, and migration of source setups between instances, with drag-and-drop import support.

## User Stories

- As a user, I want to export my feed configuration as a backup
- As a user, I want to import a configuration shared by someone else
- As a user, I want drag-and-drop import for ease of use

## Requirements

### Functional

- [ ] Export all sources as JSON file (matching feed registry schema)
- [ ] Import sources from JSON file
- [ ] Drag-and-drop import in the UI
- [ ] Import preview: show what will be added/updated before confirming
- [ ] Conflict resolution: skip duplicates or update existing
- [ ] Selective import: choose which sources to import from a file

### Non-Functional

- Compatibility: JSON format matches feed registry schema for interoperability
- Safety: Import validates all data before applying changes

## Technical Notes

- JSON schema (from vision.md):
  ```json
  {
    "version": "1.0",
    "metadata": { "name": "", "description": "", "author": "", "tags": [] },
    "feeds": [{ "url": "", "source": "", "category": "", "language": "", "description": "" }]
  }
  ```
- Backend endpoints:
  - `GET /api/config/export` — download current configuration
  - `POST /api/config/import` — upload and import configuration
- Frontend: HTML5 drag-and-drop API + file input fallback
- Reused by [starter-packs](starter-packs.md) for pack import

## Acceptance Criteria

- [ ] Export produces valid, importable JSON file
- [ ] Import correctly adds new sources
- [ ] Drag-and-drop works in modern browsers
- [ ] Import preview shows changes before applying
- [ ] Duplicate sources are handled gracefully
