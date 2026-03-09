---
type: code-quality
priority: low
status: open
discovered: 2026-03-07
related: []
related_decision: null
report: null
---

# Duplicated HTML stripping logic across services

## Problem

The same HTML-to-text stripping logic is implemented independently in three places:

1. `FeedParserService._strip_html()` — feed_parser.py
2. `OllamaService._strip_html()` — ai_service.py
3. `ContentScraper` inline logic — content_scraper.py

All three use BeautifulSoup to remove script/style tags and collapse whitespace, with minor variations.

## Recommended Approach

Extract a shared `strip_html(html: str) -> str` function in a utility module (e.g., `backend/src/infrastructure/html_utils.py`). Import it in all three services.

## Notes

- Low priority since the logic is simple and stable
- Only worth doing when touching any of these files for another reason
