# Evaluation Harness — Golden Set & Regression Metrics

**Status**: planned
**Milestone**: M4b-Intelligence
**Priority**: must-have
**Depends on**: (none — this is the foundation for all M4b classifiers)
**Related docs**: [M4b design brief](../../reference/technical/m4b-intelligence-design-brief.md) §4, [relevance model notes](../../reference/technical/relevance-model-notes.md), [prior art](../../reference/technical/axes-classification-prior-art.md)

## Summary

Build the measurement apparatus before building any classifier: a hand-labeled
golden set of real articles from the DB, a pytest-based evaluation suite that
scores any classifier against it, and persisted result history so "the model
got worse" is a diff, not a debate. Every M4b classifier (categories, axes)
ships only if its number on this harness justifies it.

## Why this comes first (argued)

- The design brief's core discipline is the **boring-baseline rule**: AI ships
  only when it measurably beats a non-AI baseline. Without this harness the
  word "measurably" is empty — so the harness precedes both baseline and model.
- The prior-art research confirmed the arithmetic: public benchmarks
  (CheckThat!) train on ~800–1,600 labeled *sentences* per language. ~100
  articles yield thousands of sentences. **One labeling effort at this scale
  is enough to both evaluate and, later, fine-tune.**
- Quality is a property of the corpus, not the demo: sampling must be
  stratified over the real DB (source type, language, geographic level),
  including the ugly cases (legal boilerplate, 55-char stubs, mixed language).

## Requirements

### Functional

- [ ] **Golden set fixture**: `backend/tests/fixtures/golden/articles.json` —
  ~100 articles sampled stratified from the live DB (by language, source
  type, geographic level; include degenerate cases deliberately)
- [ ] **Label schema per article**: `categories` (multi-label, taxonomy v0 —
  see relevance notes §5), `nature` (fact | opinion | uncertain),
  `perishability` (perishable | standard | evergreen | uncertain),
  `consequence` (consequential | descriptive | uncertain), optional
  `action_required` (bool), `notes` (free text)
- [ ] **Anchor entries**: Valentina's four examples from the relevance notes
  (ECB rate change, Antarctic shelf, Lagarde/wolf essay, forest report) are
  the first four rows — real or reconstructed equivalents from the DB
- [ ] **Sampling script**: `scripts/sample_golden_set.py` — extracts the
  stratified sample and emits a pre-filled JSON for hand-labeling (optionally
  with local-LLM *suggested* labels to speed annotation — suggestions are
  drafts, human decision is the label)
- [ ] **Eval suite**: `backend/tests/eval/` marked `@pytest.mark.eval`,
  **excluded from CI and default runs** (`-m "not eval"` semantics preserved);
  takes any classifier implementing a minimal protocol
  (`classify(article) -> labels`) and reports per-task macro-F1, per-class
  precision/recall, confusion pairs, abstention rate
- [ ] **Result history**: each eval run appends
  `{date, git_sha, classifier_id, metrics}` to
  `backend/tests/eval/history.jsonl` (tracked in git) — regressions become
  visible diffs in review
- [ ] **Reporting**: human-readable summary printed at end of run (worst
  confused pairs, per-language breakdown)

### Non-Functional

- Eval run completes in minutes on CPU (no GPU assumption)
- Golden set is versioned: schema carries `labeled_at` and `labeler`;
  articles referenced by `content_hash` so DB cleanup cannot orphan them
  (store full text in the fixture, not just IDs)
- Privacy: fixture contains only public institutional content — safe to track

## Technical Notes

- **Why per-task macro-F1**: classes are imbalanced (CheckThat! Italian is
  ~3:1 OBJ:SUBJ; our categories will be worse). Accuracy would reward
  majority-class parroting.
- **Why abstention is a first-class metric**: the design brief and prior art
  both mandate an "uncertain" output. A classifier that abstains honestly on
  20% and is right on the rest beats one that guesses everywhere. Report
  coverage/accuracy pairs, not a single number.
- **Why history.jsonl in git**: the dev-dash-style automation regenerates
  derived docs on commit; eval history is the same philosophy applied to
  model quality — provenance of quality claims.
- Labeling UX: hand-labeling ~100 articles ≈ 2–4 focused hours. The sampling
  script's suggested labels + the rubric below cut this further. Do NOT
  crowdsource; single-labeler consistency (Valentina) is the point — she is
  the metric (brief §8).
- **Labeling rubric lives next to the fixture**
  (`backend/tests/fixtures/golden/RUBRIC.md`): operational definitions per
  axis with the anchor examples. The rubric IS the operational definition of
  the axes (prior art: "we don't need philosophical truth, we need an
  operational definition encoded in a rubric").

## Acceptance Criteria

- [ ] Golden set exists with ≥100 labeled articles covering all 4 languages
  and ≥8 of the 12 categories
- [ ] `pytest -m eval` runs any registered classifier and prints the report
- [ ] History file records runs; a second run produces a comparable entry
- [ ] Rubric document exists with all anchor examples
- [ ] CI is untouched (eval excluded by default)

## Out of Scope

- Admin UI coverage metrics (belongs to [categorization-model](categorization-model.md))
- Online feedback capture ("wrong category" clicks — belongs to
  [categorization-baseline](categorization-baseline.md))
- Fine-tuning pipelines (the golden set enables them later; not built here)

## Open Questions

- Sentence-level vs article-level labels for the `nature` axis: article-level
  is cheaper and matches the feed use case; sentence-level matches CheckThat!
  and enables fine-tuning. Proposal: article-level labels + optionally mark
  1–2 *representative sentences* per article (cheap middle ground).
