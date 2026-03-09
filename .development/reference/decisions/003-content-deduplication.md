# ADR-003: Content Deduplication via SHA256

**Date**: 2025-10-25
**Status**: Active
**Impact**: critical

## Context

RSS/Atom feeds may contain duplicate entries across fetches, or the same news item may appear in multiple feeds. The system needs a reliable deduplication mechanism.

## Decision

Use SHA256 hash computed from `title|content|source|date` as a unique content identifier. The hash is stored in a column with a unique database index.

## Rationale

- SHA256 provides collision resistance sufficient for this use case
- Combining four fields catches duplicates even when individual fields partially match
- Unique index in database provides atomicity guarantee
- Simple to compute, no external dependencies
- Hash is computed in the feed parser before database insertion

## Consequences

- **Positive**: Reliable deduplication, fast lookup via index, no external services needed
- **Negative**: Articles with minor edits (typo fixes) will be treated as new items
- **Trade-off**: Content changes that alter any of the four fields create a new entry
