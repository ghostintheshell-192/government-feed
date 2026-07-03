# M4b Intelligence — Design Brief

**Date**: 2026-07-03
**Status**: Reference — read before designing or implementing any M4b spec
**Audience**: Valentina + future development sessions

This is not a spec. It is the frame *above* the specs: the reasoning that
should shape M4b decisions, written down before implementation pressure
distorts it. When an M4b choice feels hard, come back here first.

---

## 1. What M4b is actually for

The roadmap lists features (categorization, relevance, trends, sentiment).
The real goal is one sentence:

> Turn "here is everything your institutions published" into
> "here is what deserves your attention, and why".

Every M4b feature is a means to that end. A feature that doesn't visibly
serve it — however interesting — belongs in `.memory-bank/ideas/`, not in a
spec. This is also the bridge to the long-term north star (the verification
framework in `.personal/strategy/`): before you can verify claims, you must
be able to *locate and classify* them. M4b builds that substrate.

## 2. The wedge argument: one thing first

M4b as listed is five research projects wearing one milestone's name.
Each has open problems in quality, throughput, and evaluation. Attempting
them together guarantees five half-working features and no way to tell
which half works.

Candidate wedges, compared on what matters:

| Wedge | User value now | Evaluable? | Local-model feasible? | Unlocks |
|-------|----------------|------------|----------------------|---------|
| **Categorization** | High — feeds the custom-filter sidebar already designed (starter-packs Future Evolution) | **Yes** — bounded label set, right/wrong is checkable | **Yes** — bounded output; small models or even non-LLM methods work | Custom filters, verification substrate, better search |
| Relevance scoring | High, but "relevant" is undefined (see §7) | Hard — no ground truth, single user | Medium | Ranking, digest |
| Trend detection | Medium — needs volume the catalog doesn't have yet | Very hard | Medium | Analysis views |
| Sentiment | Low for institutional text (deliberately neutral register) | Hard, and misleading on this corpus | Poor fit | Little |

**Recommendation: categorization first.** It is the only candidate that is
simultaneously useful today, honestly evaluable, cheap to run locally, and
load-bearing for what comes after (custom filters are *the* sidebar
evolution already specced; verification needs classified claims). Relevance
comes second, *fed by* categorization plus user signals. Trends need data
volume; sentiment likely never fits this corpus — drop it unless a concrete
need appears.

## 3. The boring-baseline rule

Every AI feature in this project must have a non-AI baseline it measurably
beats before the AI version ships. For categorization: keyword/rule-based
assignment (source category + title keywords) is an afternoon of work,
fully local, zero latency — and probably scores surprisingly well on
institutional feeds, because institutions *pre-classify their own output*
(a CFTC feed is finance; an ARPA feed is environment; source metadata
already carries category and geographic level).

This rule is not modesty. It produces three things M4b desperately needs:
a working feature immediately, a yardstick that makes "the LLM is worth
its cost" a measured claim instead of a hope, and a fallback when the
model degrades. Sequence every wedge as: baseline → measure → LLM only
where the baseline demonstrably fails (multi-topic articles, untagged
sources, cross-cutting themes).

## 4. The evaluation problem (the hard core)

This is the intellectually serious challenge of M4b, more than any model
plumbing: **how do you know it works, with one user and no ground truth?**

Principles first:

- For institutional content, **faithfulness beats fluency**. A wrong
  attribution ("the ministry announced X" when it didn't) is worse than no
  output at all. Errors of omission are tolerable; errors of assertion are
  not. This inverts the usual LLM quality intuition and must shape every
  prompt, metric, and UI decision. (The
  `summarization-faithfulness-benchmark` idea in `.personal/ideas/` is the
  seed of exactly this — it deserves promotion to a spec.)
- **Quality is a property of the corpus, not the demo.** Working on ten
  hand-picked articles means nothing; institutional feeds contain legal
  boilerplate, multilingual text, tables, 55-character stubs. Evaluate on
  stratified reality.

Concrete minimal apparatus (an afternoon, not a research project):

1. **Golden set**: 50–100 articles sampled from the real DB, stratified by
   source type, language, and geographic level. Hand-label them once
   (categorization labels are quick — this is precisely why the wedge is
   evaluable). Store as JSON fixture in `backend/tests/fixtures/golden/`.
2. **Eval harness**: a pytest-marked suite (`@pytest.mark.eval`, excluded
   from CI by default) that runs the current classifier against the golden
   set and reports accuracy / per-category confusion. Run it on every
   prompt or model change. Regression = the number went down; no debates.
3. **Signals from use**: the cheapest ground truth is Valentina reading.
   One-click "wrong category" on a NewsCard costs nothing at read time and
   accumulates labels passively. Design the feedback affordance *with* the
   feature, not after.
4. **Coverage metrics in Admin**: % of items enriched, % low-confidence,
   enrichment age. AI features fail *silently* — the health-monitor
   philosophy (stateful, visible, escalating) applies to model output
   quality exactly as it does to feeds.

## 5. Architecture directions (with trade-offs, not verdicts)

- **Enrichment as a separate concern.** Keep AI-derived data (labels,
  scores, confidence, model version) out of `NewsItem`'s core columns — an
  `enrichments` table keyed by news item (or content_hash) keeps the domain
  clean, makes re-enrichment after model changes a DELETE+rerun instead of
  a migration, and respects ADR-008's locality split (enrichments are
  user-content-side, regenerable, ephemeral by nature).
- **content_hash is a free cache key.** Deduplication (ADR-003) already
  computes a stable identity per article. Enrichment results cached by
  content_hash never recompute for unchanged content — the existing
  architecture pays for M4b before it starts.
- **Batch at ingest, not on-demand.** The current on-demand AI pattern
  (summarize when the user clicks) does not scale to classify-everything.
  Enrichment should be an APScheduler job draining a queue after feed
  polls — same pattern as the existing polling/cleanup/health jobs, so the
  infrastructure precedent exists. On-demand stays for expensive artifacts
  (full summaries) where a user is actually waiting.
- **Throughput budget, in numbers.** ~100 sources × a few items/day is
  hundreds of classifications daily. At 7B-model speeds (seconds per item,
  CPU-bound on typical hardware) that is tens of minutes of nightly batch —
  feasible but not free. Two mitigations, in order: smaller task models
  (classification does not need a reasoning model — a 1–3B instruct model,
  or embeddings + a linear head, may match R1-7B on a bounded label task at
  10× the speed), and the boring baseline handling the easy 80% so the LLM
  only sees ambiguous cases.
- **Taxonomy: flat, small, multi-label.** Start with ≤12 categories derived
  from what institutions actually publish (legislation, economy & finance,
  health, environment, security & defense, justice, infrastructure,
  education, foreign affairs…). Multi-label from day one — the sidebar
  design already assumes multi-membership. Resist hierarchy: it feels
  rigorous and costs UI, evaluation, and prompt complexity while serving no
  current user story. A hierarchy can be layered on later; removing one
  cannot.

## 6. Named traps

- **The five-projects trap** — building all of M4b at once. Antidote: §2.
- **The demo-quality trap** — judging on hand-picked articles. Antidote: §4.
- **The cloud temptation** — "just this one feature would be so much better
  with a hosted model". ADR-002 is not a constraint to negotiate; it is the
  project's identity (see §1: the audience monitors governments — privacy
  *is* the feature). If local quality is insufficient, ship the baseline
  and wait for local models to improve; they do, fast. BYOK cloudAI, if
  ever, is a user choice in M5+, never a default.
- **The silent-degradation trap** — enrichment quietly failing or drifting
  for weeks. Antidote: §4 coverage metrics; treat the model like a feed
  that can go `degraded`.
- **The taxonomy-rabbit-hole** — designing the perfect category tree
  instead of shipping twelve labels. Antidote: §5 last point; the golden
  set will reveal which categories actually occur.

## 7. Questions only Valentina can answer

> **Update 2026-07-04**: all three answered — see
> [relevance-model-notes.md](relevance-model-notes.md) (fact-vs-opinion axis,
> telegiornale cadence criterion, epistemics/topics split, taxonomy seed v0:
> Valentina's eight + four institutional inevitables). Nothing in this
> section blocks M4b any longer.

These are not blockers to start (the wedge doesn't need them), but relevance
work is blocked on the first one, and writing answers down — even
provisional — will save future sessions from guessing:

1. **What does "relevant" mean to you, personally?** Novelty? Impact on
   your life/region? Proximity to themes you track? Urgency? Relevance
   scoring without an explicit definition becomes the model's opinion,
   which is worse than no ranking. One honest paragraph in
   `.personal/` would unblock the entire second wedge.
2. **The taxonomy seed**: which ~12 categories would *you* want as sidebar
   filters? (Your usage is the spec — this tool is single-user by design
   until M5.)
3. **Latency tolerance**: is nightly enrichment acceptable, or do new
   articles need labels within minutes of the poll?

## 8. Suggested sequencing

*(Revised 2026-07-04 after the relevance conversation — see
[relevance-model-notes.md](relevance-model-notes.md).)*

- **Track 0 (parallel, ongoing) — Catalog critical mass**: robust categories
  need corpus breadth (105 sources, 6 subscribed, zero GLOBAL/LOCAL as of
  2026-07-03 is not it). Grow by *enumerating institutions, not searching
  for feeds*: Wikidata/SPARQL as the entity index + the existing URL-based
  feed discovery on each official website; national government directories;
  official gazettes; central banks and statistical offices. This reframes
  the carried-over `feed-discovery-automated` spec (text search demoted to
  last resort). Runs alongside every M4b phase.
- **M4b.1 — Baseline categorization**: source-metadata + keyword rules,
  taxonomy seed v0 (twelve flat multi-label categories, notes §5), labels
  visible on cards + sidebar filter integration, golden set + eval harness
  built alongside. Golden set is labeled on categories **and** on the
  relevance axes, with Valentina's four anchor examples as the first
  entries. *Done when: the sidebar filters by category and the eval number
  exists.*
- **M4b.2 — Model-assisted categorization**: LLM (or embedding classifier)
  only on items where the baseline is unsure; must beat baseline on the
  golden set to ship. Enrichment table, batch job, coverage in Admin.
  *Done when: measured lift over baseline, silent-failure metrics live.*
- **M4b.3 — Axes & cadence** (formerly "relevance from signals" — no longer
  blocked, and decomposed): classify nature (fact↔opinion), perishability,
  consequence per item; cadence policy (push / standard / ambient) from the
  perishability × consequence matrix; enrichment latency stratified by the
  same signal (fast path at poll time via cheap document-type heuristics,
  nightly batch for the rest). Read/save/dismiss signals become a
  tie-breaker and an eval input, not the foundation — no behavioral
  profiling (notes §3). *Done when: the default ordering is measurably more
  useful to Valentina than chronological — she is the metric.*
- **Later / conditional**: trends (needs the corpus volume Track 0 is
  building), clustering of related items (useful for the verification
  substrate), sentiment (probably never — see §2).

---

*Written 2026-07-03, at the close of M4a, as durable context for M4b design
sessions. If reality contradicts this document, update the document — but
do it consciously, in a commit that says why.*
