# ADR-009: No Profiling — Neither Readers Nor Publishers

**Date**: 2026-08-05
**Status**: Accepted
**Impact**: critical
**Summary**: The system never builds a profile of an actor — not of the reader from reading behaviour, nor of a news outlet from publishing behaviour; it may show per-item verifiable facts, never aggregate labels about who produced them.

## Context

Two commitments already existed independently, and this ADR unifies them
because they turn out to be the same rule applied to opposite ends of the same
pipeline.

**On the reader side**, the founding relevance model
([relevance model notes](../technical/relevance-model-notes.md) §3) resolved
"relevant to me" vs "relevant per se" with: *the system judges epistemics
(form); the user chooses topics (content)*. The stated consequences were no
behavioural profiling and no filter-bubble mechanics — the tool's opinion is
only ever about form (fact vs opinion, urgency), never about which position is
right.

**On the publisher side**, the press-coverage work
([spec](../../specs/planned/press-coverage-cross-referencing.md)) introduces
something new: the tool will hold both the primary institutional document and
the press coverage of it. That combination makes it trivially easy to compute
statements about outlets — "this one systematically ignores X", "this one
leans right". The data would be there; nothing but an explicit decision stops
the computation.

The pressure to cross that line is real, and it does not arrive as a proposal.
It arrives as a feature that seems obviously useful and one step away from
what already exists.

## Decision

The system does not build profiles of actors. Concretely:

1. **No behavioural profiling of the reader.** Read / save / dismiss signals
   may serve as tie-breakers and as evaluation inputs, never as the foundation
   of what gets shown. Personal scope is expressed through subscriptions and
   category filters, which the user controls explicitly.

2. **No profiling of publishers.** No score, ranking, badge, aggregate
   statistic or classification is computed or displayed *per outlet*. This
   includes political orientation, bias, reliability, and systematic-silence
   metrics.

3. **Per-item facts are permitted, and are the point.** "This communiqué was
   covered by these three articles, at these times" is an observation about a
   single event, verifiable in one click via the links. That is the
   verification substrate the project exists to build.

4. **Absence is reported as a limit of observation, never as a fact about the
   world.** The UI says *"not found in the feeds you follow"*; it never says
   or implies *"no one covered this"*. Absence from a monitored feed is not
   absence of coverage: feeds are partial and matchers have false negatives.

5. **No sentiment or political-orientation classification**, on any source
   type. (The M4b design brief already benched sentiment on evaluability
   grounds; here it is ruled out on principle as well.)

The operative distinction throughout: the system may measure **selection**
(observable, per-item, falsifiable) and must not attribute **orientation** (a
judgement about a position or an actor).

## Rationale

- **Coherence over convenience.** Refusing to profile readers while profiling
  publishers would be arbitrary — the objection to profiling is not about who
  is being profiled, but about a tool that issues verdicts on actors instead
  of showing evidence.
- **It protects the north star.** The project's long-term value is
  verifiability: putting evidence in front of the reader so *she* judges. An
  aggregate verdict replaces her judgement with the tool's — the exact failure
  mode the vision attributes to media intermediation.
- **The permitted version is more useful.** A verifiable, clickable per-item
  comparison beats a bias score, which is unfalsifiable, contestable, and
  reveals more about its own methodology than about its subject.
- **It is defensible under challenge.** "The system reports what it found in
  these feeds, with links" is a defensible claim. "This outlet is biased" is
  not one the tool has the evidence or the standing to make.
- **The methodology could not support it anyway.** Feed-derived coverage data
  has structural sample bias (partial feeds, section-only feeds, matcher false
  negatives). Aggregates built on it would be confidently wrong.

## Consequences

### Pros

- One rule to check any future feature against, on either side of the pipeline
- Keeps the project publishable without a reputational liability attached
- No behavioural tracking to store, secure, or explain — consistent with
  ADR-002 (privacy-first)
- Sets the design constraint early, while it is still cheap to honour

### Cons

- Gives up a genuinely interesting analytical capability that the data would
  support in raw form
- Cross-source patterns visible to the reader across many items cannot be
  summarized *for* her by the tool
- Requires discipline in UI wording — the tempting phrasings ("nobody covered
  this") are precisely the forbidden ones, and are the natural way to write
  them

### Neutral

- Does not prevent the *user* from drawing her own conclusions; it prevents
  the *system* from drawing them on her behalf. That asymmetry is the whole
  decision.
