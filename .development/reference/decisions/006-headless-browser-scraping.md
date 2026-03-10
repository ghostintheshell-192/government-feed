# ADR-006: Headless Browser for Anti-Bot Protected Sources

**Date**: 2026-03-10
**Status**: Deferred
**Impact**: moderate

## Context

The content scraper uses httpx to fetch article pages and extract full text. This works for most government sources, but some (notably SEC, and potentially other US federal agencies) deploy enterprise-grade anti-bot protection (Akamai, Cloudflare) that blocks all non-browser HTTP clients regardless of User-Agent headers.

These protections rely on TLS fingerprinting and JavaScript challenges that cannot be bypassed with simple header adjustments. The RSS feed itself remains accessible (different endpoint, different protection level), so article metadata and short snippets are always available — only full-text scraping is affected.

Currently affected sources: SEC (sec.gov). Others may surface as more sources are added.

## Decision

Defer the choice of a headless browser solution to a future milestone (M5 or later). For now:

- The scraper uses realistic browser headers (helps with simpler protections)
- Sources behind enterprise WAFs gracefully degrade to RSS snippet content
- The bulk fetch progress bar reports failures transparently to the admin

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Playwright** | Modern, fast, good Python async support, Chromium/Firefox/WebKit | Heavy dependency (~200MB), requires system-level install |
| **Selenium** | Mature ecosystem, wide browser support | Slower, more complex setup, synchronous API |
| **requests-html / pyppeteer** | Lighter weight | Abandoned/unmaintained, pyppeteer lags behind Puppeteer |
| **Do nothing** | Simple, no added complexity | Some sources permanently limited to RSS snippets |

Playwright is the likely choice when this becomes a priority, given its async API and active maintenance.

## Consequences

- Some sources will only show RSS snippet content until this is implemented
- No additional dependencies or infrastructure needed for now
- Admin UI clearly shows which articles failed content fetch
- When implemented, should be opt-in per source (most sources don't need it)
