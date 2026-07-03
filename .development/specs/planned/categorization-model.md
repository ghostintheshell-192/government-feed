# Categorization Model (M4b.2) — Embeddings Classifier for the Unsure Cases

**Status**: planned
**Milestone**: M4b-Intelligence
**Priority**: should-have
**Depends on**: [categorization-baseline](categorization-baseline.md), [eval-harness](eval-harness.md)
**Related docs**: [prior art](../../reference/technical/axes-classification-prior-art.md) (architectural verdict), [M4b design brief](../../reference/technical/m4b-intelligence-design-brief.md) §3–5

## Summary

Add a local ML classifier for the items the rules baseline marks
`uncategorized` or low-confidence: multilingual sentence embeddings + a
lightweight classifier head (SetFit-style few-shot bootstrap from the golden
set + accumulated user corrections). Batch execution via the existing
scheduler pattern, results cached by `content_hash`, coverage visible in
Admin. **Ship gate: beats the rules baseline on the golden set — measured,
not assumed.**

## Why embeddings + head, not Ollama zero-shot (argued)

This is the strongest evidence-backed decision in M4b — three independent
verified findings from the prior-art research converge:

1. Embeddings+classifier ensembles reached 0.77 macro-F1 (2nd place,
   CheckThat! 2023) — CPU-friendly, no generative model involved.
2. Fine-tuned RoBERTa-class encoders beat zero-shot ChatGPT on institutional
   stance tasks, and BIS's domain-adapted small encoders beat *frontier*
   generative LLMs on FOMC stance.
3. ~12B open generative models zero-shot perform significantly worse than
   ChatGPT on all benchmarked financial tasks — and our Ollama models are in
   or below that class.

Ollama/DeepSeek-R1 keeps its existing job (summarization, where generation is
the task). Classification is not generation. A generative model may
optionally *suggest* labels during golden-set annotation (offline, human
decides) — never in the production path.

## Design

- **Model**: a multilingual sentence-transformer (candidate:
  `paraphrase-multilingual-MiniLM-L12-v2` or a current equivalent — small,
  CPU-viable, covers IT/EN/DE/FR) + logistic-regression / linear head per
  category (multi-label = 12 one-vs-rest heads). SetFit-style contrastive
  fine-tuning if plain embeddings underperform ([SetFit](https://arxiv.org/abs/2209.11055)).
  Model files vendored/downloaded once; inference fully local (privacy-first
  preserved — nothing leaves the machine).
- **Routing**: only items with `uncategorized` or `confidence < τ` from the
  baseline go to the model (brief §5: the baseline handles the easy majority;
  the model sees only ambiguity). τ tuned on golden set.
- **Execution**: APScheduler job (same pattern as polling/cleanup/health)
  draining a work queue after feed polls; nightly full pass + optional
  on-demand trigger from Admin. Results written to `enrichments` with
  `method = "model-<version>"`; cached by `content_hash` (never recompute
  unchanged content).
- **Training data**: golden set labels + accumulated `user-correction` rows
  (the feedback affordance from M4b.1 becomes the training signal —
  passive-labeling loop closes here).
- **Versioning & re-enrichment**: model version stamped per row; bumping the
  version invalidates via DELETE-where-method + rerun. Old user corrections
  are never overwritten.

### Silent-degradation monitoring (health-monitor philosophy applied to ML)

Admin gains an **Enrichment coverage** panel:
- % items enriched / uncategorized / low-confidence (overall + per source)
- enrichment age distribution; queue depth; last batch run + duration
- trend vs previous week — a model quietly degrading must *look* degraded
  (brief §6, silent-degradation trap)

## Requirements

### Functional

- [ ] Local embedding model integration (download, load, infer — no network
  at inference time)
- [ ] Multi-label heads trained from golden set + corrections; training
  script committed (`scripts/train_categorizer.py`)
- [ ] Unsure-only routing with tunable τ
- [ ] Batch scheduler job + queue + content_hash cache
- [ ] Model version on enrichment rows; re-enrichment command
- [ ] Admin enrichment-coverage panel (API + UI)
- [ ] Eval-harness comparison entry: model vs baseline, committed to history

### Non-Functional

- Nightly batch for the full backlog completes in tens of minutes on CPU
  (measure; if not, reduce scope to unsure-only which is the design anyway)
- Deterministic inference (fixed seeds/versions) so eval numbers reproduce

## Acceptance Criteria

- [ ] **Gate**: model macro-F1 > baseline macro-F1 on the golden set, per the
  harness, entry in `history.jsonl` — otherwise this spec does not ship and
  the baseline remains
- [ ] Coverage panel live; uncategorized rate visibly drops vs baseline-only
- [ ] No inference-time network calls (verified — privacy-first)
- [ ] Corrections keep winning over model output on conflict

## Out of Scope

- Axes classification (M4b.3 — same infrastructure, different heads)
- Fine-tuning generative models
- GPU requirements of any kind

## Open Questions

- Threshold τ: per-category or global? (Proposal: global first, per-category
  if the confusion report shows asymmetric categories.)
- DE/FR quality: multilingual embeddings should carry them, but the golden
  set must contain enough DE/FR items to *know* (eval per-language
  breakdown is the check).
