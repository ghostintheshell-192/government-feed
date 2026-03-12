---
type: feature
priority: medium
status: open
discovered: 2026-03-12
related: []
related_decision: reference/decisions/007-catalog-subscription-model.md
---

# Source tagging is unreliable

## Problem

39 out of 103 catalog sources have no tags. The current `infer_tags` approach in `scripts/crawl_feeds.py` matches keywords in the feed name/description, but most outlets use proper names ("Mediapart", "Repubblica", "Meduza.io") that carry no classifiable keyword.

This means we can't reliably distinguish a government gazette from a tabloid, which matters for a tool focused on institutional/government sources.

## Analysis

The affected sources are almost entirely generalist newspapers across FR, IT, PL, RU, UA, ES, DE, IE. They were imported from the `awesome-rss-feeds` OPML collection, which mixes press and institutional feeds without distinction.

Keyword matching on feed titles is inherently fragile — it only works when the name happens to contain a domain keyword (e.g., "EBA News" → economy, regulation).

## Possible Solutions

- **Option A**: Manual curation — tag sources by hand. Accurate but doesn't scale and requires domain knowledge per country.
- **Option B**: Feed content analysis — sample N entries per feed and classify based on actual content (topics, language, source domains). More robust but heavier.
- **Option C**: Metadata enrichment from external sources — use Wikidata, press directories, or similar to look up outlet type (government, agency, newspaper, etc.).
- **Option D**: LLM-assisted classification — send feed name + sample entries to local Ollama and ask for categorization. Leverages existing infrastructure.

## Recommended Approach

To be determined. Likely a combination: Option A for the current 39 sources (one-time effort), Option B or D for future automated imports.

## Notes

- Not blocking for M4a — tags are optional in the UI for now
- Becomes important when Starter Packs and filtering by source type are implemented
- The core question is broader: how do we verify that a source is actually institutional/governmental vs. commercial press?

## Related Documentation

- **Code Location**: `scripts/crawl_feeds.py:163` (`infer_tags` function)
- **Architecture Decision**: ADR-007 (catalog-subscription model)
