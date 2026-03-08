# Trend Detection

**Status**: backlog
**Milestone**: M4b-Intelligence
**Priority**: nice-to-have
**Depends on**: [ai-categorization](ai-categorization.md), [relevance-scoring](relevance-scoring.md)

## Summary

Analysis system for identifying recurring topics, clustering related news, building event timelines, and alerting on emerging trends across institutional sources.

## User Stories

- As a user, I want to see which topics are trending across multiple sources
- As a user, I want related news items grouped together
- As a user, I want alerts when a new trend is emerging

## Requirements

### Functional

- [ ] Recurring topic identification (same topic appearing in multiple items over time)
- [ ] News clustering: group related articles together
- [ ] Event timeline: chronological view of related items on a topic
- [ ] Emerging trend alerts: notify when a new topic starts gaining traction
- [ ] Trend visualization (chart or timeline view)

### Non-Functional

- Timeliness: Trends detected within hours of emergence
- Accuracy: Minimize false positive trend alerts
- Privacy: All analysis happens locally

## Technical Notes

- Topic identification can build on AI categorization and keyword extraction
- Clustering approaches:
  - Keyword-based: shared significant terms across items
  - Embedding-based: cosine similarity of article embeddings (Phase 3 of relevance scoring)
  - Time-windowed: cluster within recent time window (7 days default)
- Timeline generation: chronological ordering of clustered items
- Alert thresholds: configurable sensitivity (number of sources, time window)
- Builds on cross-source recurrence detection from [relevance-scoring](relevance-scoring.md)

## Acceptance Criteria

- [ ] Related news items are grouped correctly
- [ ] Trending topics are identified and displayed
- [ ] Event timelines show chronological progression
- [ ] Emerging trend alerts fire appropriately
- [ ] False positive rate is acceptably low
