# Daily Digest ("Rassegna Stampa")

**Milestone**: M4a-Feed-Infrastructure
**Status**: Backlog
**Priority**: High

## Problem

Users who follow multiple news sources have no unified daily overview. Visiting each newspaper individually is tedious. Google News is not configurable by source and mixes unreliable sources with no transparency. RSS readers provide raw lists without intelligence.

Government Feed already aggregates institutional sources. Adding a digest of preferred newspapers alongside institutional feeds gives users a complete daily briefing from trusted sources only.

## Feature Description

A daily digest view that aggregates **headlines and snippets** from the user's selected news sources (newspapers, magazines, institutional feeds) into a single chronological or grouped view.

### What it includes

- **Title** from RSS feed
- **Snippet/description** (the lead paragraph published in the feed)
- **Source name and publication date**
- **Link to original article** (opens in browser)

### What it does NOT include

- Full article text (no scraping — only RSS-provided content)
- Paywalled content extraction
- Any content not intentionally published in the feed by the source

### Legal basis

RSS feed content (titles, descriptions, links) is published by sources specifically for syndication and aggregation. Using this content is standard practice for feed readers and aggregators.

## User Experience

- User adds newspaper RSS feeds alongside institutional feeds (same source management)
- A "Digest" view shows today's headlines grouped by source or by time
- Configurable: which sources appear in digest, how many items per source
- Clean, scannable layout — emphasis on titles, snippets visible on expand/hover

## Data Model

No new tables needed. News sources already support multiple feed types. May need:
- A `source_type` or tag to distinguish "institutional" from "media" sources
- A view/filter mode in the frontend for digest vs. full feed

## Cross-referencing with Institutional Sources (→ M4b)

The digest enables a powerful M4b feature: **matching institutional news with media coverage**.

When an institution publishes a decision/regulation, the system can find related newspaper articles covering the same topic. This gives users:
- The **original source** (institutional feed)
- The **media interpretation** (newspaper coverage)
- The ability to judge coverage quality themselves

This is the core "disintermediation" value: not removing media, but placing it next to the source.

### Matching approach (M4b scope)

1. **Keyword overlap** in titles and snippets (baseline)
2. **Entity matching** — institution names, law numbers, acronyms (NER)
3. **Semantic similarity** via local AI embeddings (advanced)

## Implementation Notes

- RSS snippets provide enough text for matching without scraping
- Most Italian newspapers have RSS feeds (Il Post, Corriere, Sole 24 Ore, ANSA, etc.)
- Feed polling infrastructure already exists
- Consider snippet length limits for consistent UI

## Dependencies

- Existing feed parser and source management
- M4b-Intelligence for cross-referencing feature
