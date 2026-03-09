# Relevance Scoring

**Status**: backlog
**Milestone**: M4b-Intelligence
**Priority**: should-have
**Depends on**: [ai-summarization](../implemented/ai-summarization.md), [dashboard-news-browsing](dashboard-news-browsing.md)

## Summary

Multi-phase relevance ranking system: Phase 1 with heuristic scoring (source authority, act type, keywords, cross-source recurrence), Phase 2 with user preference learning via collaborative filtering, Phase 3 with semantic matching.

## User Stories

- As a user, I want important news to appear at the top of my feed
- As a user, I want the system to learn my interests over time
- As a user, I want to manually mark items as important or irrelevant

## Requirements

### Functional

#### Phase 1 — Heuristic Scoring
- [ ] Ranking by source authority (e.g., BCE > Ministero > Agenzia locale)
- [ ] Ranking by act type (Decreto > Comunicato > Verbale)
- [ ] Keyword boost for critical terms ("scadenza", "modifica fiscale", "bando", "allerta")
- [ ] Cross-source recurrence detection (3+ sources on same topic → priority bump)

#### Phase 2 — User Preference Learning
- [ ] Track user interactions (click/read → +1, hide/ignore → -1)
- [ ] Build user preference profile: source weights, keyword weights, category weights
- [ ] Adapt ranking based on accumulated preferences
- [ ] Reset preferences option

#### Phase 3 — Semantic Matching (future)
- [ ] Embedding-based similarity for "articles like ones you read"
- [ ] Automatic topic clustering

### Non-Functional

- Transparency: Users understand why items are ranked a certain way
- Control: Users can override or reset the scoring system

## Technical Notes

- Phase 1 scoring formula (from vision.md):
  - Source authority weight (configurable per source)
  - Act type weight (keyword-based detection)
  - Critical keyword detection (configurable keyword list)
  - Cross-source recurrence (count sources mentioning similar topics)
- Phase 2 user preference model:
  ```python
  user_preferences = {
      'sources': {'BCE': 0.8, 'Comune_Milano': 0.2},
      'keywords': {'tassi': 0.9, 'cultura': 0.1},
      'categories': {'economia': 0.95, 'sport': 0.05}
  }
  ```
- UI controls: "Segna come importante", "Nascondi", toggle for generic press releases
- Phase 3 requires embedding model (local via Ollama or sentence-transformers)

## Acceptance Criteria

- [ ] News items are ranked by relevance score (Phase 1)
- [ ] Cross-source recurrence correctly boosts priority
- [ ] User interactions update preference profile (Phase 2)
- [ ] Users can reset their preferences
- [ ] Scoring factors are transparent to the user
