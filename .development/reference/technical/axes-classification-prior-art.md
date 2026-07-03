# Axes Classification — Prior Art & Feasibility

**Date**: 2026-07-04
**Method**: 12-agent verified web research (4 angle searches → 19 sources
fetched → 66 claims extracted → top 24 adversarially verified: 23 confirmed,
1 refuted — disclosed below).
**Context**: grounds the axes defined in
[relevance-model-notes.md](relevance-model-notes.md) for M4b.3
([design brief](m4b-intelligence-design-brief.md) §8).

## Executive summary

All three axes are feasible with small local models, at three different
maturity levels. **Axis 1 (fact vs opinion) is a mature, benchmarked task**
with multilingual public datasets covering IT/DE/EN and a ~0.80 macro-F1
state of the art reachable by small encoders. **Axis 3 (consequence)** has
strong adjacent evidence from central-bank NLP, where domain-adapted small
encoders beat frontier generative LLMs on stance classification — but the
evidence is concentrated in monetary policy; generalizing to all government
text is untested. **Axis 2 (perishability) is the genuine research
frontier**: solid evidence that the signal exists and correlates with genre,
but no public dataset or established benchmark — it must be built here.

**The architectural verdict** (the single most consequential finding):
zero-shot prompting of small generative models — i.e. the naive Ollama
approach — is documented as the *wrong tool* for these classifiers.
Fine-tuned small encoders and embeddings+classifier heads are the right one.

---

## Axis 1 — Fact vs Opinion: mature

- **Task exists as "subjectivity detection"** with an operational definition
  matching ours: subjective (opinions/biases) vs objective (factual
  information) at sentence level. CLEF CheckThat! 2024 Task 2 ran it in five
  languages incl. **English, German, Italian** on 10,000+ news sentences.
  [CheckThat! 2024 overview](https://elmi.hbku.edu.qa/en/publications/overview-of-the-clef-2024-checkthat-lab-task-2-on-subjectivity-in-2/)
- **Language luck is on our side**: best 2024 results were on *Italian and
  German*, then English. **French is absent** from the task — our one
  coverage gap (handle via multilingual model or translation).
- **State of the art**: macro-F1 **0.8052** on English (CheckThat! 2025,
  feature-augmented DeBERTa-v3-large, 1st of 22 teams vs 0.537 baseline).
  Treat ~0.80 as the realistic ceiling.
  [QU-NLP system paper](https://arxiv.org/html/2507.21095v1)
- **Cheap pipelines are competitive**: a majority-vote ensemble of
  sentence-embeddings+classifier, SetFit, and multilingual BERT reached
  **0.77 macro-F1, 2nd place** (CheckThat! 2023) — all CPU/small-GPU
  friendly. [paper](https://arxiv.org/pdf/2309.06844)
- **Training data is small**: ~800–1,600 labeled sentences per language
  (2025 task); a self-built institutional set at this scale is realistic —
  ~100 golden articles yield thousands of sentences.
- **Claim detection is a *different* label**: OpinionFinder
  (MPQA-subjectivity) failed to separate check-worthy claims in ClaimBuster
  (574 non-factual sentences classified objective). "Is this an opinion?"
  and "is this a checkable claim?" need separate classifiers if we ever add
  check-worthiness (verification north star).
  [ClaimBuster KDD'17](https://ranger.uta.edu/~cli/pubs/2017/claimbuster-kdd17-hassan.pdf)
  — where a plain SVM hit 72P/67R: no neural net required for a baseline.
- **LLM caution**: GPT-4-turbo reaches F1 0.927 on ClaimBuster with tuned
  guideline prompts, but the *same* guidelines drop performance on another
  domain (0.773 → 0.596). Prompt recipes do not transfer across domains —
  a direct warning for institutional text.
  [benchmark](https://arxiv.org/html/2404.12174v1)

## Axis 2 — Perishability: the research frontier

- **The signal exists and correlates with genre**: on 18 months of traffic
  from a large international news site, shelf-life@90% averages **4.1 days
  for News vs 7.7 days for Opinion**; 48% of a News article's 30-day visits
  arrive within the first three days.
  [shelf-life study](https://arxiv.org/pdf/1807.06373)
  → Axis 1 output (report vs opinion) is itself a usable perishability
  feature, and short decay windows (days) are empirically justified.
- **No public dataset or benchmark survived verification.** This axis must
  be defined and annotated here: golden set + weak supervision from genre
  and temporal-deictic surface features.
- *Surfaced but not verified in this pass* (follow up before building):
  "Characterization and Early Detection of Evergreen News Articles"
  (ECML-PKDD 2019, Penn State + Washington Post) — appears to be the most
  on-point academic/industrial work on evergreen detection.
  [pdf](https://pike.psu.edu/publications/ecmlpkdd19.pdf)

## Axis 3 — Consequence/Impact: strong proxy, untested transfer

- **Public dataset**: "Trillion Dollar Words" (ACL 2023) — annotated FOMC
  speeches/minutes/press conferences, hawkish/dovish stance task; best model
  among tested PLMs was **fine-tuned RoBERTa-large** (a small encoder).
  [paper](https://aclanthology.org/2023.acl-long.368/)
- **Small domain-adapted encoders beat frontier LLMs**: BIS CB-LMs
  (BERT/RoBERTa adapted on 37k central-banking papers + 18k speeches)
  "surpass state-of-the-art generative LLMs in classifying monetary policy
  stance". Frontier LLMs win only on the most complex scenario (sentiment
  over extensive news) — that is where small-local stops being competitive.
  BIS's stated rationale (confidentiality/cost) mirrors our privacy-first
  constraint. [BIS WP 1215](https://www.bis.org/publ/work1215.pdf)
- **Zero-shot generative is documented as inferior**: zero-shot ChatGPT
  fails to beat fine-tuned RoBERTa on FOMC stance and claim detection, and
  ~12B open generative models perform *significantly worse* than ChatGPT on
  all financial tasks. [paper](https://arxiv.org/pdf/2305.16633)
- **Caveat**: all of this is monetary-policy domain. "Performative vs
  descriptive" for general government text (decrees, service announcements)
  has no public dataset — the FOMC recipe (small encoder + thousands of
  labeled sentences) is the template to replicate, not a model to reuse.
- *Refuted during verification* (transparency): the DCS preprint
  (arXiv 2603.14313, frozen 1–14B LLM representations → stance scores)
  exists and is method-inspiration, but its headline accuracy claims
  (Qwen3-4B 71.1% vs baselines ~44%) did **not** survive adversarial
  checking. Do not cite those numbers.

## Cross-cutting recommendations (for the M4b.3 spec)

1. **Architecture**: multilingual sentence embeddings (or fine-tuned small
   multilingual encoder — mDeBERTa / XLM-R class) + lightweight classifier
   head per axis, SetFit for few-shot bootstrap
   ([SetFit](https://arxiv.org/abs/2209.11055)). **Not** zero-shot prompting
   of generative models via Ollama — three independent verified findings
   point the same way. Generative LLMs remain fine for *summarization*
   (existing feature) and for offline label suggestion during golden-set
   construction.
2. **Data plan per axis**: Axis 1 bootstraps from public CheckThat! data
   (EN/IT/DE) + institutional golden set; Axis 3 replicates the FOMC
   annotation recipe on our corpus; Axis 2 is built from scratch with
   genre + temporal-deictic weak supervision.
3. **Golden set arithmetic works**: ~100 articles ≈ thousands of sentences ≈
   CheckThat! training scale. Label all three axes in one annotation pass.
4. **Known risks**: domain shift news→institutional prose (documented, not
   hypothetical — the prompt-transfer failure above); French coverage gap;
   calibration/abstention on a small eval set (per-class thresholds with an
   explicit "uncertain" bucket; conformal abstention as the fancier option).

## Open questions

1. Transfer test first: evaluate a CheckThat!-trained subjectivity model on
   ~100 held-out institutional sentences per language *before* any
   fine-tuning investment.
2. Verify the ECML-PKDD 2019 evergreen paper (methods, features, any
   released data) before designing Axis 2.
3. Operationalize "consequence" for general government text — performative
   speech-act annotation scheme, FOMC-style.
4. Abstention strategy for small-eval-set calibration.

---

*Produced 2026-07-04 by a budgeted deep-research run (12 agents, 19 sources,
adversarial verification). Claims above marked with their surviving status;
one refuted claim disclosed. Sources are linked inline.*
