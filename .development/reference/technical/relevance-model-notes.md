# Relevance Model — Founding Notes

**Date**: 2026-07-03
**Source**: conversation with Valentina at M4a close
**Status**: Answers §7.1 and §7.3 of the [M4b design brief](m4b-intelligence-design-brief.md); §7.2 (taxonomy seed) still open

These notes record the user's own definition of relevance — the oracle the
design brief said was required before any relevance work. Do not design
M4b.3 (relevance) or enrichment scheduling without reading this.

---

## 1. The founding definition (Valentina, verbatim in spirit)

**Event news (cronaca) outranks opinion/analysis.** The reason is not taste
but *temporal epistemics*: a fact is neutral at the moment of capture; from
then on, opinions accrete over it until the bare fact becomes hard to
retrieve in its original, neutral form. "Le opinioni fanno perdere la
neutralità; le notizie legate a eventi per definizione la mantengono,
altrimenti non sono più notizie."

Corollary — the **"telegiornale" criterion** for cadence: important news is
surfaced the moment it arrives; lesser news, deep-dives, and opinions are
shown at a calmer, less insistent rhythm.

### Anchor examples (use these in the golden set)

| Item | Class | Why |
|------|-------|-----|
| ECB changes interest rate | **Push immediately** | Perishable + consequential fact; the announcement *is* the event |
| Antarctic shelf calving (Wisconsin-sized) | **Push immediately** | Perishable + consequential fact; "declares a climate urgency better than anything else" |
| Essay on Lagarde vs the grey wolf | **Calm cadence** | Low consequence, opinion-adjacent, however illuminating |
| Report on the state of European forests | **Ambient / evergreen** | Worthy but retrievable "from Wikipedia at any time"; never front-page |

## 2. The axes

1. **Nature**: fact/event ↔ opinion/analysis. (Valentina's axis. Classic,
   evaluable NLP task.)
2. **Perishability**: time-to-stale — how fast the item loses value *or
   neutrality of context*. Perishable-critical ↔ evergreen. (Formalizes the
   founding insight.)
3. **Consequence**: changes the state of the world (rate cut, attack order,
   law enacted — often irreversible) ↔ describes it (statistics, reports).
4. **Action flag** (boolean, not an axis): deadlines, public consultations,
   compliance dates — the reader must *do* something.
5. *(Benched candidate)* **Novelty**: deviation from baseline (rate
   *changed*) vs confirmation (rate *held*). Revisit if axes 1–3 prove
   insufficient.

**The cadence matrix**: perishability × consequence reproduces the
telegiornale criterion — perishable+consequential → push; low-consequence →
calm; evergreen → ambient. The four anchor examples fall out correctly.

## 3. Resolution of "relevant to me" vs "relevant per se"

Valentina raised the fork explicitly: personal relevance (requires user
behavior modeling, adapts to any value system) vs universal importance
("this matters, read it", regardless of preferences). Resolution adopted:

> **The system judges epistemics (form); the user chooses topics (content).**

- The axes are judgments **about the object** — approximately universal,
  requiring zero user modeling.
- Personal scope enters through **subscriptions and category filters**,
  which the user already controls; subscribing *is* the preference
  expression.
- Consequences: no behavioral profiling (consistent with privacy-first,
  ADR-002 spirit); no filter-bubble mechanics (consistent with the
  verification north star); the tool's "opinion" is only ever about form
  (fact vs opinion, urgency), never about which position is right.

## 4. Implications for M4b

- **"Relevance scoring" decomposes**: axis classification + cadence policy,
  instead of a single opaque relevance scalar. Each axis is separately
  evaluable — far better fit for the eval harness than "relevance: 0.73".
- **Enrichment latency (§7.3) is not a constant**: it is a function of
  predicted importance. Cheap importance signals at poll time (source type,
  document type from URL/feed metadata — press release vs speech vs report;
  the boring baseline again) route items to a fast path (classify now) or
  the nightly batch.
- **Golden set**: label the anchor axes, not only categories. Valentina's
  four examples are the first four entries.
- **Sequencing unchanged**: categorization remains the wedge (M4b.1/2);
  axes are a second classifier sharing the same harness (M4b.3 becomes
  "axes + cadence" rather than "scoring").

## 5. Still open

- §7.2 taxonomy seed: brief proposed legislation, economy & finance,
  health, environment, security & defense, justice, infrastructure,
  education, foreign affairs (+ candidates: science & research, energy,
  labor & welfare, migration, digital). Awaiting Valentina's cut.
- Whether the fact↔opinion classifier needs its own golden subset with
  institutional edge cases (a minister's speech is an *act* — performative
  — even though it is made of opinions).
