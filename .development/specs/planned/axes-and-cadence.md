# Axes & Cadence (M4b.3) — Epistemics Classification and Telegiornale Ordering

**Status**: planned
**Milestone**: M4b-Intelligence
**Priority**: should-have
**Depends on**: [eval-harness](eval-harness.md), [categorization-baseline](categorization-baseline.md) (enrichments table, genre signals); benefits from [categorization-model](categorization-model.md) (shared embedding infrastructure)
**Related docs**: [relevance model notes](../../reference/technical/relevance-model-notes.md) (the founding definition — read first), [prior art](../../reference/technical/axes-classification-prior-art.md), [design brief](../../reference/technical/m4b-intelligence-design-brief.md) §8

## Summary

Implement the decomposed relevance model: classify each item along the
epistemic axes (nature: fact↔opinion; perishability; consequence), derive a
cadence class (push / standard / ambient) from the perishability×consequence
matrix, and use it for default feed ordering and enrichment prioritization.
No relevance scalar, no behavioral profiling: **the system judges form, the
user chooses topics** (relevance notes §3).

## Why decomposed axes instead of a relevance score (argued)

- A scalar "relevance: 0.73" is unexplainable and unevaluable; axes are
  separately measurable on the golden set, and failures are localizable
  ("perishability over-triggers on speeches") — the eval-harness philosophy
  applied to ranking.
- The axes are object-judgments requiring zero user modeling — consistent
  with privacy-first (no profiling) and with the anti-filter-bubble stance
  demanded by the verification north star.
- Valentina's own definition (the oracle): cronaca beats opinion because
  facts are neutral at capture and opinions accrete over them. The cadence
  matrix reproduces her four anchor examples exactly (relevance notes §1–2).

## Design — three phases inside one spec

### Phase A — Nature axis (fact/event ↔ opinion/analysis)

The mature one (prior art: CheckThat! subjectivity, IT/DE best-covered,
~0.80 F1 ceiling, ~1–2k sentences/language to train):

- Bootstrap: fine-tune a small multilingual encoder (or SetFit on the shared
  embedding stack from M4b.2) on public CheckThat! subjectivity data
  (EN/IT/DE) + our golden set. **French**: multilingual transfer, measured
  separately (no public FR benchmark exists — prior-art gap).
- **Transfer test BEFORE fine-tuning investment** (prior-art open question 1):
  run a CheckThat!-trained model on ~100 held-out institutional sentences;
  if transfer is poor, weight our golden set higher.
- Document-type prior: press release / decision → fact-leaning; speech /
  blog / editorial → opinion-leaning (URL + feed metadata heuristics, free).
- Edge case recorded in the notes: a minister's speech is an *act* even when
  made of opinions ("whatever it takes" was an event). The rubric decides;
  the classifier follows the rubric.

### Phase B — Perishability axis (perishable | standard | evergreen)

The research frontier (prior art: signal exists — News 4.1d vs Opinion 7.7d
shelf-life@90% — but no public benchmark). Built here, weakly supervised:

- Weak signals: genre/nature output (Phase A), document type, temporal
  deictics in title/lead ("today", "just", dates near now vs none),
  source rhythm (a gazette pulses daily; an annual-report feed does not)
- Golden-set labels are the only strong supervision; start as a
  rules+features classifier, upgrade to a learned head only if the eval says
  the rules aren't enough
- Verify the ECML-PKDD 2019 evergreen-detection paper (features, any data)
  before finalizing the feature set (prior-art follow-up)

### Phase C — Consequence axis (consequential | descriptive)

Template exists, dataset does not (prior art: FOMC recipe — small encoder +
thousands of labeled sentences — but monetary-policy only):

- Start with document-type heuristics: decisions, decrees, regulations,
  rate/appointment/sanction announcements → consequential; reports,
  statistics, studies → descriptive (institutional feeds *name* their acts)
- Golden-set labels measure the heuristic; a learned head replicating the
  FOMC recipe on our annotations is the upgrade path, gated by the harness

### Cadence policy & ordering

- `cadence = f(perishability, consequence)` per the matrix in relevance
  notes §2: perishable+consequential → **push**; evergreen → **ambient**;
  rest → **standard**
- Stored on `enrichments` (new columns: `nature`, `perishability`,
  `consequence`, `cadence`, each with confidence; `uncertain` is a valid
  value everywhere — abstention is first-class)
- **Default feed ordering**: push items first (within freshness window),
  then standard chronological, ambient de-emphasized (never hidden — this
  is ordering, not censorship; user can always sort chronologically)
- **Enrichment prioritization**: push-candidates (cheap heuristic at poll
  time) classified on the fast path; the rest join the nightly batch —
  the latency answer from relevance notes §4
- UI: minimal — a subtle cadence marker on cards (e.g. dot/label for push),
  a "sort: smart | chronological" toggle. No red breaking-news banners; this
  tool's register is calm.
- Read/save/dismiss signals: recorded (locally) only as *eval input* and
  tie-breaker experiments — explicitly NOT a profiling feature; any use
  beyond eval requires a new decision.

## Requirements

### Functional

- [ ] Phase A classifier + transfer test documented in eval history
- [ ] Phase B weak-supervision classifier
- [ ] Phase C heuristic classifier
- [ ] Enrichment columns + migration; abstention value everywhere
- [ ] Cadence computation + smart ordering (API: `sort=smart|date`)
- [ ] Fast-path enrichment for push candidates at poll time
- [ ] Frontend: cadence marker + sort toggle (4 languages)
- [ ] Golden-set eval per axis committed to history

### Non-Functional

- All inference local (no network at inference)
- Smart sort adds no perceptible API latency (cadence precomputed)
- Every axis output explainable: which signals fired (debug field)

## Acceptance Criteria

- [ ] Each axis beats its trivial baseline (majority class) on the golden
  set, with abstention rate reported
- [ ] The four anchor examples land in their intended cadence classes
- [ ] **The human gate**: with smart ordering on, Valentina finds the top of
  her feed more useful than chronological — she is the metric (brief §8).
  Evaluate honestly after ≥1 week of real use; if it fails, chronological
  stays default and the spec iterates
- [ ] No behavioral profiling introduced anywhere

## Out of Scope

- Relevance scalar / learned ranking from engagement
- Notifications/push delivery (cadence "push" is feed ordering, not alerts —
  notifications remain a backlog spec)
- Trends, clustering (later, per brief §8)

## Open Questions

- Freshness window for push ordering: reuse `news_freshness_hours` or a
  separate, shorter window? (Proposal: reuse — one knob until proven wrong.)
- Should ambient items get a dedicated "evergreen shelf" view instead of
  de-emphasis? (Candidate for the custom-filters evolution.)
