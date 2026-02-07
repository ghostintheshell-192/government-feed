# Content Deduplication

**Status**: implemented
**Milestone**: M1-MVP
**Priority**: must-have
**Depends on**: repository-pattern.md

## Summary

SHA256-based content deduplication system that prevents duplicate news items from being stored, using a hash of key fields with a unique database index.

## User Stories

- As a user, I want the system to automatically skip duplicate news so my feed stays clean
- As a user, I want deduplication to work even if the same article appears in multiple feeds

## Requirements

### Functional

- [x] Compute SHA256 hash from `title|content|source|date` concatenation
- [x] Check existing content_hash before inserting new items
- [x] Skip insertion when duplicate hash is found
- [x] Unique database index on content_hash column
- [x] Log skipped duplicates for transparency

### Non-Functional

- Performance: Hash computation is O(1) per item, index lookup is O(log n)
- Reliability: Unique index guarantees no duplicates even under concurrent writes

## Technical Notes

- Hash formula: `SHA256(title + "|" + content + "|" + source_id + "|" + published_date)`
- Unique index on `content_hash` column in NewsItem table
- Repository method `get_by_content_hash()` for pre-insert check
- See [ADR-003](../../reference/decisions/003-content-deduplication.md) for design decision

## Acceptance Criteria

- [x] Duplicate articles are not stored in database
- [x] Same article from different fetch cycles is correctly identified as duplicate
- [x] Unique index prevents duplicates at database level
- [x] Skipped duplicates are logged with item details
