# Automated Feed Discovery — Enumerate Institutions, Not Search for Feeds

**Status**: planned
**Milestone**: M4b-Intelligence (Track 0 — catalog critical mass, runs in parallel)
**Priority**: must-have
**Depends on**: [source-management](../implemented/source-management.md), [source-catalog-subscriptions](../implemented/source-catalog-subscriptions.md), [error-resilience](../implemented/error-resilience.md)
**Related docs**: [M4b design brief](../../reference/technical/m4b-intelligence-design-brief.md) §8 Track 0

> **Rewritten 2026-07-04.** The original spec made text search (Exa/Brave)
> the primary mechanism. This version inverts the strategy: **institutions
> are enumerable; feeds are not.** Authoritative registries give us the
> entity list; our existing URL-based discovery does the rest. Text search
> is demoted to last resort. Catalog state motivating this: 105 sources,
> zero GLOBAL, zero LOCAL, 2 were untagged — both breadth and metadata
> quality must scale together.

## Summary

Grow the catalog from ~100 to thousands of institutional sources by
enumerating institutions from structured registries (Wikidata first,
official government directories second), running the existing URL-based
feed discovery against each institution's official website, validating and
importing into the catalog **with geographic metadata attached at the
source** — fixing the tagging-quality debt at its root instead of after
the fact.

## Why enumeration-first (argued)

- **The entity list already exists.** Wikidata models government agencies,
  ministries, central banks, statistical offices, courts, and international
  organizations with `official website` properties and country/instance-of
  relations. One SPARQL query per country/class yields hundreds of
  candidates *with metadata we need anyway* (country, institution type).
- **Our best tool is already built.** URL-based discovery
  (`_discover_from_url`: HTML link tags + common paths + feedparser
  validation) works well — it lacked only a systematic list of URLs to
  visit. Enumeration supplies exactly that.
- **Metadata comes free and fixes a known debt.** `source-tagging-unreliable`
  (39/103 untagged) exists because tagging happened after import, by hand.
  Wikidata's country + institution class map directly to `country_code` and
  `geographic_level` (international org → GLOBAL/CONTINENTAL; national
  ministry → NATIONAL; regional agency → LOCAL) at import time. This also
  fills the empty GLOBAL and LOCAL levels the sidebar currently shows.
- **Privacy posture improves**: queries to the public Wikidata endpoint are
  about institutions, not user interests; text-search providers (which see
  query intent) become optional instead of central.
- Categorization robustness (M4b) needs corpus breadth — brief §8 Track 0.

## Design

### Pipeline

```text
1. ENUMERATE   Wikidata SPARQL per (country × institution class)
               + curated directory seed lists (data/feed-sources/registries/)
               → candidates: {name, official_url, country, class, wikidata_id}
2. DISCOVER    existing FeedDiscoveryService._discover_from_url(official_url)
               (bounded concurrency, resilience patterns already in place)
3. VALIDATE    feedparser dry-run + HTTP check (existing validation path)
4. MAP         wikidata class/country → source_type, geographic_level,
               country_code, tags (mapping table in data/, editable)
5. IMPORT      into catalog (NOT auto-subscribed — catalog/subscription
               split per ADR-007 means growth never spams the user's feed)
               provenance stored: wikidata_id, registry, discovered_at
6. REPORT      NDJSON streaming progress (existing pattern), summary:
               found / no-feed / dead / already-known per registry
```

### Enumeration sources, in priority order

1. **Wikidata SPARQL** — government agencies, ministries, central banks,
   statistical offices, supreme/constitutional courts, international
   organizations; start with project languages' countries (IT, DE, FR, CH,
   AT, BE, NL, EU institutions) + GLOBAL class (UN system, IMF, World Bank,
   OECD, WTO, BIS, international courts)
2. **Curated registry seeds** (checked-in JSON/OPML under
   `data/feed-sources/registries/`): gov.uk organisations list, admin.ch,
   EU agencies list, official gazettes index — high-value lists that
   Wikidata may lag on
3. **Text search providers (Exa/Brave)** — LAST RESORT, user-initiated only
   (`POST /api/discover` with a query), for institutions the registries
   miss. Provider architecture, secrets management (env vars, never logged,
   `.env.example`), quota tracking and graceful fallback as specified in the
   previous revision of this spec — that design carries over unchanged for
   this mode.

### Execution model

- Admin script first (`scripts/enumerate_institutions.py`), same pattern as
  the existing feed crawler; Admin UI trigger with streaming progress later
- Idempotent: candidates deduped by normalized official_url and feed_url
  against the catalog; re-runs only add news
- Politeness: bounded concurrency, per-domain rate limiting, standard
  browser UA (existing scraper conventions), respect robots.txt for
  crawled directory pages

## Requirements

### Functional

- [ ] SPARQL enumeration for ≥8 countries + GLOBAL/CONTINENTAL classes
- [ ] Registry seed-list loader (JSON/OPML) + ≥2 curated lists checked in
- [ ] Discovery+validation reuse with bounded concurrency
- [ ] Metadata mapping table (wikidata class → source fields) as data file
- [ ] Catalog import with provenance fields; never auto-subscribes
- [ ] NDJSON progress + final report; failures listed, not silent
- [ ] Search-provider mode preserved as user-initiated endpoint (optional,
  disabled when no API key — existing availability rules)

### Non-Functional

- Full enumeration run for one country completes unattended (resumable on
  interruption; state by registry+entity id)
- Catalog quality gate: imported sources must carry geographic_level and
  country_code (the two-empty-sources incident cannot recur by construction)
- No user data leaves the machine; only institution-related queries to
  public endpoints

## Acceptance Criteria

- [ ] Catalog grows by ≥300 validated sources across ≥8 countries
- [ ] GLOBAL and LOCAL levels are populated (sidebar shows all 4 levels
  with real content available to subscribe)
- [ ] 100% of newly imported sources have geographic_level + country_code
- [ ] Re-running the script is a no-op on unchanged registries
- [ ] Health monitor covers new sources automatically (subscribed ones)

## Out of Scope

- Auto-recovery of dead feeds ([feed-auto-recovery](feed-auto-recovery.md))
- Community feed registry (backlog — the public-contribution evolution)
- Auto-subscription or starter-pack bundling of the new catalog entries

## Open Questions

- Wikidata completeness varies by country — measure hit-rate per country in
  the first run and decide where curated lists must compensate
- Some institutions expose feeds only per-section (e.g. per-ministry
  newsroom paths): extend common-path list with institutional patterns
  (`/press/rss`, `/newsroom/feed`, `/aktuelles/rss`) as data, not code
