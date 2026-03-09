# AI Categorization

**Status**: backlog
**Milestone**: M4b-Intelligence
**Priority**: nice-to-have
**Depends on**: [ai-summarization](../implemented/ai-summarization.md)

## Summary

Automatic classification of news items via local AI, using a hierarchical taxonomy with multi-label support for organizing content by topic (economy, politics, health, environment, etc.).

## User Stories

- As a user, I want news items automatically categorized so I can filter by topic
- As a user, I want to see multiple categories per item when relevant
- As a user, I want to suggest corrections to misclassified items

## Requirements

### Functional

- [ ] Hierarchical category taxonomy (e.g., Economy > Monetary Policy > Interest Rates)
- [ ] Multi-label classification (one article can belong to multiple categories)
- [ ] Automatic classification via local AI (Ollama)
- [ ] Manual category suggestion/correction by user
- [ ] Category-based filtering in news browsing
- [ ] Confidence score per classification

### Non-Functional

- Accuracy: > 80% correct classification
- Performance: Classification during feed processing (not blocking UI)
- Privacy: All classification happens locally

## Technical Notes

- Classification via Ollama prompt engineering (structured output)
- Taxonomy stored in database (Categories table, planned in schema)
- Many-to-many relationship: NewsItem ↔ Category
- Could reuse AI service with specialized classification prompt
- Consider batch classification during feed processing
- Fallback: manual categorization if AI accuracy is insufficient

## Open Questions

- Fixed taxonomy vs user-extensible categories?
- Classification at import time vs on-demand?
- How to handle category hierarchy depth

## Acceptance Criteria

- [ ] News items are automatically categorized on import
- [ ] Multi-label classification works correctly
- [ ] Category-based filtering works in the UI
- [ ] Classification accuracy exceeds 80%
- [ ] Users can correct misclassifications
