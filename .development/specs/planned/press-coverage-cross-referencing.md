# Press Coverage — Media Sources and Cross-Referencing

**Status**: planned
**Milestone**: M4b-Intelligence (Phase 1 has no M4b dependency and can ship first)
**Priority**: should-have (Phase 1 is high-value at near-zero cost)
**Depends on**: existing feed parser and catalog/subscription model (Phase 1); [categorization-baseline](categorization-baseline.md) and [eval-harness](eval-harness.md) (Phase 2 matching)
**Related docs**: [relevance model notes](../../reference/technical/relevance-model-notes.md) §3, [ADR-009](../../reference/decisions/009-no-profiling-readers-or-publishers.md), [design brief](../../reference/technical/m4b-intelligence-design-brief.md) §Later/conditional (clustering)
**History**: was `specs/backlog/daily-digest.md` ("Rassegna Stampa", M4a). Rewritten 2026-08-05 after a design conversation that reframed the feature around cross-referencing rather than around the digest view, and drew the ethical boundary now recorded in ADR-009.

## Summary

Let press outlets (newspapers, magazines) live in the same catalog as
institutional sources, marked as a distinct source type — then place their
coverage **next to** the primary institutional document that occasioned it.

The value is not "read my newspapers in one place" (an RSS reader does that).
It is **disintermediation without removing the intermediary**: showing the
official communiqué and the press coverage of it side by side, so the reader
judges the coverage instead of receiving it alone. The corollary — which
institutional documents got *no* coverage at all — is information no
aggregator currently provides.

## Problem

The user follows several outlets (The Conversation, The Information, WSJ, Il
Post, Axios) and drowns in the volume: newsletters, digests, and article
floods, of which only a fraction is worth reading. Meanwhile the institutional
side of the tool has no way to show how — or whether — the press treated a
given official document.

Two separate needs are involved, and conflating them was the original spec's
weakness:

1. **Triage**: see titles and standfirsts from chosen outlets, in one clean
   surface, to decide what deserves reading. Solved by RSS alone.
2. **Cross-referencing**: connect an institutional item to the press coverage
   of it. Requires matching, i.e. M4b machinery.

## Phase 1 — Media sources in the catalog

No new machinery. The catalog (ADR-007) already holds arbitrary feeds; the
parser, the health monitor and the subscription model apply unchanged.

### What it includes

- **Title** from the RSS feed
- **Snippet / description** (the standfirst as published in the feed)
- **Source name and publication date**
- **Link to the original article** (opens in the browser)

### What it does NOT include

- Full article text — no scraping
- Paywalled content extraction
- Any content the source did not intentionally publish in its feed

### Legal basis

RSS feed content (titles, descriptions, links) is published by sources
specifically for syndication and aggregation. Consuming it is the standard,
intended behaviour of feed readers. This spec never goes beyond the feed.

### Data model

- `Source.source_type` — `institutional` | `media`. Needed for the geographic
  sidebar too: press outlets have no meaningful `geographic_level`, and
  forcing them into the LOCAL→GLOBAL ladder (ADR-005) would corrupt the
  institutional navigation.
- No new tables in this phase.

### UX

- Media sources are added and subscribed exactly like institutional ones
- The dashboard can filter by source type; press items never dilute the
  institutional stream unless the reader asks for them
- Emphasis on titles, snippets on expand — a scannable surface, not a reader

### Note on outlet coverage

Four of the five outlets above publish public RSS (The Conversation, Il Post,
Axios, WSJ per section). The Information appears to offer a subscriber feed
with a personal token — **unverified, check before promising it**. Most
Italian newspapers publish RSS (Il Post, Corriere, Sole 24 Ore, ANSA).

## Phase 2 — Cross-referencing (M4b)

When an institution publishes a decision or regulation, find the press
articles covering the same fact, and attach them to it.

The reader gets: the **original document**, the **press interpretation**, and
the ability to judge the distance between them.

### Matching approach

Same boring-baseline discipline as the rest of M4b — each step ships only if
it measurably beats the previous one on the harness:

1. **Keyword overlap** in titles and snippets (baseline)
2. **Entity matching** — institution names, act numbers, acronyms (NER)
3. **Semantic similarity** via local embeddings (reuses the M4b.2
   infrastructure — see [categorization-model](categorization-model.md))

Time proximity is a cheap, strong prior: coverage follows the source document
within hours to days, never before it. Use it to bound the candidate set.

### Two models of the comparison — a product decision, not an architectural one

The same pipeline supports both. What differs is *how many outlets sit in the
catalog* and *what the UI claims*. Both are reversible at any time; **do not
treat this as a fork to resolve before building**.

| | **A. The mirror** | **B. The observatory** |
|---|---|---|
| Scope | Only outlets the user subscribes to | A broad, deliberately chosen set, subscribed or not |
| What it measures | The user's own information diet | The editorial behaviour of third parties |
| Claim made | About oneself | About organizations |
| Risk | None | Reputational and epistemic (see below) |

**Start with A.** It is what the user actually needs as a reader, it makes her
own bubble visible from the inside — a genuine finding, not a lesser one — and
it asserts nothing about anyone else.

**B is a change in kind, not in degree**: it turns a reader into a media
monitor. It is not illegal (public feeds only) but it produces public-facing
measurements about named organizations, and it must not be entered by drift.

### The boundary (binding — see ADR-009)

The system may show **what was covered and when**: a per-item, verifiable,
clickable fact. It must never aggregate those observations into **a label
about an actor** ("this outlet systematically ignores X", "this outlet leans
right").

The distinction is between measuring **selection** (observable, falsifiable)
and attributing **orientation** (a judgement of position). The latter is
already forbidden by the founding relevance model: *the system judges form,
never which position is right* ([relevance model notes](../../reference/technical/relevance-model-notes.md) §3).
ADR-009 extends the no-profiling principle from readers to publishers.

### The statistical caveat — this constrains the UI wording

**Absence from a monitored feed is not absence of coverage.** Many outlets
publish partial, section-only or truncated feeds; and the matcher has false
negatives (an article may cover the fact without naming the document).

Measured silence is therefore an **upper bound, never a fact**. This is the
claim most likely to be wrong and most likely to be attacked, so it is a
wording constraint, not a footnote:

- Say *"not found in the feeds you follow"* — never *"no one covered this"*
- Always link the evidence, so any claim is one click from verification
- Never render silence as a score, a ranking, or a badge on the outlet

## Deliberately out of scope

- **Newsletter / email ingestion** — considered and set aside. Newsletters are
  digests of digests: splitting one into items duplicates what RSS already
  provides and multiplies volume; not splitting it leaves an unreadable HTML
  blob. Per-outlet parsers break on every restyle. If email ever returns, it
  returns as a *prominence signal* (an editor's explicit ordering), not as a
  second ingestion pipeline — captured in
  `.memory-bank/ideas/2026-08-05-newsletter-ingestion.md`.
- Full-text and paywalled content (unchanged from the original spec)
- Any sentiment or political-orientation classification (ADR-009)

## Open questions

- Does `source_type` belong on `Source` as a column, or is it a tag? A column
  is simpler and the sidebar needs to filter on it server-side.
- Should press items have their own view, or a filter on the existing
  dashboard? A filter is cheaper and defers the layout question.
- For Phase 2: attach coverage to the institutional item (one-to-many), or
  build a symmetric cluster entity? The design brief lists clustering as
  conditional — decide when the matcher's precision is actually known.

## Acceptance criteria

**Phase 1**

- [ ] `source_type` distinguishes institutional from media sources
- [ ] Press feeds can be subscribed and polled like any other source
- [ ] Press items are excluded from the institutional stream by default
- [ ] Press sources do not appear under geographic levels (ADR-005 intact)

**Phase 2**

- [ ] An institutional item displays the press articles matched to it, with links
- [ ] Matching quality is measured on the eval harness, not asserted
- [ ] No UI surface states or implies "no one covered this"
- [ ] No aggregate metric is computed or displayed per outlet (ADR-009)

## A side benefit worth noting

Journalistic text next to institutional text is excellent material for the
M4b golden set: press articles are the natural hard cases for the
fact↔opinion axis, which institutional corpora barely exercise. Phase 1 may
be worth doing early for the eval harness alone.
