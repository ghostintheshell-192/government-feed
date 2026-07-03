# Categorization Baseline (M4b.1) — Rules, Enrichment Storage, Sidebar Filters

**Status**: planned
**Milestone**: M4b-Intelligence
**Priority**: must-have
**Depends on**: [eval-harness](eval-harness.md)
**Related docs**: [M4b design brief](../../reference/technical/m4b-intelligence-design-brief.md) §2–3, §5, [relevance model notes](../../reference/technical/relevance-model-notes.md) §5 (taxonomy), [prior art](../../reference/technical/axes-classification-prior-art.md)

## Summary

The first categorization wedge, deliberately non-AI: assign taxonomy-v0
category labels to every news item using source metadata and keyword rules,
persist them in a new `enrichments` table, expose them as sidebar filters,
and measure the result on the golden set. This ships a working feature
immediately and creates the yardstick every model must beat.

## Why a rules baseline first (argued)

- **Institutions pre-classify their own output**: a CFTC feed is finance, an
  ARPA feed is environment, EUR-Lex document types name themselves. Source
  metadata (`category`, `source_type`, feed URL path) already encodes most of
  the answer at zero cost (brief §3).
- **Prior art supports low-tech**: a plain SVM hit 72P/67R on ClaimBuster
  check-worthiness; feature-based methods remain competitive on bounded label
  tasks. Rules are the degenerate-but-honest version, and they are fully
  explainable — important for a tool whose north star is verifiable trust.
- **It produces the ship-gate**: M4b.2's model may only ship if it beats this
  number on the golden set. No baseline, no gate, no discipline.

## Design

### Taxonomy v0 (from relevance notes §5)

Twelve flat, multi-label categories:
`security-defense, economy-finance, education, foreign-affairs,
science-research, energy, labor-welfare, digital, health, environment,
legislation, justice`.
Stored as string keys; display names come from i18n (4 languages).

### Rules engine (Core layer service, no I/O)

Deterministic, ordered signal sources — strongest first:

1. **Source-level mapping**: `source.category` / `source_type` → default
   categories for every item of that source (curated mapping table shipped as
   data, editable without code changes: `data/categorization/source-rules.json`)
2. **Feed-path hints**: URL segments (`/press/monetary/`, `/environment/`)
   → category hints (same data file)
3. **Keyword lexicon**: per-category keyword lists applied to title +
   first N chars of content; multilingual (EN/IT/DE/FR blocks;
   start EN+IT complete, DE/FR minimal) —
   `data/categorization/keywords.json`
4. **Confidence**: each rule contributes a weight; per-category score above
   threshold → label. No label above threshold → `uncategorized`
   (an honest, first-class outcome — feeds M4b.2's "unsure" routing).

### Enrichment storage (new table — design decision)

```
enrichments
  id             PK
  news_item_id   FK -> news_items (indexed, ON DELETE CASCADE)
  content_hash   str (indexed — cache key, survives re-import; ADR-003 reuse)
  categories     JSON list[str]
  confidence     float
  method         str   ("rules-v1" | "model-<id>" later)
  created_at     datetime (UTC — see tech-debt naive-aware-datetime-columns:
                 apply the UTCDateTime TypeDecorator fix BEFORE this table)
```

Argued: labels stay **out of `news_items`** so re-enrichment after rule/model
changes is DELETE + rerun, not a migration; `content_hash` doubles as a free
cache key (dedup infrastructure pays for M4b — brief §5); the table is
user-content-side per ADR-008's locality split. Axis columns (M4b.3) will be
added to this same table by a later migration.

### Execution model

- **Inline at ingest**: rules are microseconds; run in `parse_and_import`
  after dedup. No queue needed at this stage (queue arrives with M4b.2 where
  inference costs real time).
- **Backfill command**: `scripts/backfill_enrichments.py` for existing items
  (~idempotent via content_hash).

### API & Frontend

- `GET /api/news` accepts `categories` filter (multi, OR semantics),
  composing with existing geographic/source/date filters
- `NewsItemResponse` carries `categories`
- Sidebar: categories section below geographic levels (multi-toggle badges,
  same interaction grammar as geographic levels — this begins the
  custom-filters evolution from the starter-packs spec)
- **Feedback affordance**: one-click "wrong category" on NewsCard opens a
  minimal category picker; corrections stored as
  `enrichments.method = "user-correction"` rows (never overwritten by
  re-enrichment). Argued: the cheapest ground truth is Valentina reading;
  design the affordance *with* the feature, not after (brief §4).

## Requirements

### Functional

- [ ] Taxonomy v0 constants + i18n labels (4 languages)
- [ ] Rules engine with the 3 signal sources + threshold/uncategorized
- [ ] `enrichments` table + migration (after the UTC TypeDecorator fix)
- [ ] Inline enrichment at ingest + backfill script
- [ ] `categories` filter on news API; categories in response schema
- [ ] Sidebar category filters (desktop + mobile parity with geo badges)
- [ ] "Wrong category" feedback affordance storing corrections
- [ ] Golden-set eval run recorded in `history.jsonl` (the baseline number)

### Non-Functional

- Rules data files hot-editable (no redeploy to tune keywords)
- Zero added latency perceptible at ingest; backfill runs bounded
- Explainability: API can return *which rule fired* (debug field or log)

## Acceptance Criteria

- [ ] Every new item gets categories (or explicit `uncategorized`) at import
- [ ] Sidebar filters by category; composes with geographic filters
- [ ] Corrections persist and are visible in Admin (list of user corrections)
- [ ] Baseline macro-F1 on golden set measured and committed to history
- [ ] Works in all 4 languages (labels; keyword coverage may lag for DE/FR —
  measured per-language in the eval report)

## Out of Scope

- Any model inference (M4b.2)
- Axes / cadence (M4b.3)
- Category management UI (taxonomy changes are code+data edits for now)

## Open Questions

- Should `uncategorized` be visible as a sidebar filter? (Proposal: yes — it
  is the honest bucket and doubles as a to-fix queue for rules tuning.)
