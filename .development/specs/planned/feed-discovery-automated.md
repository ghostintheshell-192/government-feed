# Automated Feed Discovery

**Status**: planned
**Milestone**: M4a-Feed-Infrastructure
**Priority**: must-have
**Depends on**: [source-management](../implemented/source-management.md), [error-resilience](../implemented/error-resilience.md)

## Summary

Replace the broken DuckDuckGo text search in `FeedDiscoveryService` with a multi-provider search system (Exa primary, Brave Search fallback), enabling both user-initiated feed discovery and system-initiated auto-recovery for dead feeds.

## User Stories

- As a user, I want to search for institutional feeds by topic/keyword and get validated results
- As a user, I want the system to automatically find replacement URLs when feeds break
- As a user, I want to add discovered feeds to my sources with one click
- As an operator, I want to configure which search providers are active without code changes

## Context

The current `FeedDiscoveryService` has two modes:

1. **URL-based discovery** (`_discover_from_url`) — works well, parses HTML for feed links + tries common paths
2. **Text search** (`_search_sites` via DuckDuckGo) — broken, returns no results

This spec replaces mode 2 with a provider-based search architecture and adds batch validation capabilities. Mode 1 remains unchanged.

## Requirements

### Functional

- [ ] Provider-based search architecture with pluggable backends
- [ ] Exa Search as primary provider (neural search, best for institutional content)
- [ ] Brave Search as fallback provider (generous free tier, 1000 queries/month)
- [ ] Automatic fallback: if primary fails or is over quota → try next provider
- [ ] Search query construction: accept keyword/topic, produce optimized queries per provider
- [ ] Result pipeline: search → extract candidate URLs → discover feeds from each URL → validate → rank
- [ ] Batch validation: given N candidate URLs, validate all concurrently (bounded concurrency)
- [ ] Deduplication: skip URLs already in the user's sources
- [ ] Return structured results: feed URL, title, type (RSS/Atom), entry count, source site
- [ ] Rate limiting: respect provider quotas (track usage, stop before exceeding limits)
- [ ] REST API endpoint for user-initiated discovery: `POST /api/discover`

### Non-Functional

- Performance: Discovery results returned within 30 seconds for typical queries
- Resilience: Provider failures are handled gracefully with fallback
- Security: API keys never in code, never in logs, never in API responses
- Cost: Minimize search API calls (cache results, batch efficiently)

## Technical Design

### Secrets Management

API keys are managed as environment variables, loaded via the existing settings infrastructure:

```text
# .env (local development — in .gitignore, NEVER committed)
EXA_API_KEY=exa-...
BRAVE_SEARCH_API_KEY=BSA...

# Production: set via deployment environment (systemd env, Docker secrets, etc.)
```

**Rules:**

1. `.env` is in `.gitignore` — verified at implementation time
2. Keys loaded via `os.environ` or pydantic `BaseSettings` — never hardcoded
3. Keys never logged — log `"Exa search OK"`, not `"Exa search with key exa-xxx"`
4. Keys never exposed in API responses — discovery endpoint returns feeds, not provider details
5. Provider availability determined at startup: if key is missing, provider is disabled (not an error)
6. A `.env.example` file documents required variables with placeholder values

### Provider Architecture

```python
class SearchProvider(ABC):
    """Abstract search provider interface."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> list[str]:
        """Search and return candidate site URLs."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and within quota."""
        ...

class ExaSearchProvider(SearchProvider):
    """Exa neural search — best for institutional/government content."""
    # Uses EXA_API_KEY from environment

class BraveSearchProvider(SearchProvider):
    """Brave Web Search — fallback with generous free tier."""
    # Uses BRAVE_SEARCH_API_KEY from environment
```

### Discovery Pipeline

```text
User query: "European Central Bank monetary policy"
  │
  ├─ 1. SearchProvider.search(query) → candidate URLs
  │     [ecb.europa.eu, ecb.europa.eu/press, ...]
  │
  ├─ 2. FeedDiscoveryService._discover_from_url(url) for each candidate
  │     (existing logic: HTML link tags + common paths + direct feed check)
  │
  ├─ 3. Validate with feedparser → DiscoveredFeed objects
  │
  ├─ 4. Deduplicate against existing sources
  │
  └─ 5. Return ranked results (by entry_count, feed_type preference)
```

### Integration with Health Monitor

The Health Monitor calls discovery in "recovery mode":

```python
# Recovery mode — search is more targeted
async def recover_feed(self, source: Source) -> DiscoveredFeed | None:
    """Attempt to find a replacement URL for a dead feed."""
    # Build recovery query from source metadata
    domain = urlparse(source.feed_url).netloc
    query = f"{source.name} RSS feed site:{domain}"

    # Try discovery with fallback chain
    feeds, _ = await self.discover(query)

    # Return best match (if any)
    return feeds[0] if feeds else None
```

### Modified FeedDiscoveryService

```python
class FeedDiscoveryService:
    def __init__(self, timeout: float = 15.0) -> None:
        self._timeout = timeout
        self._providers = self._init_providers()  # auto-detect available providers

    def _init_providers(self) -> list[SearchProvider]:
        """Initialize available search providers based on configured API keys."""
        providers: list[SearchProvider] = []
        if ExaSearchProvider.is_configured():
            providers.append(ExaSearchProvider())
        if BraveSearchProvider.is_configured():
            providers.append(BraveSearchProvider())
        if not providers:
            logger.warning("No search providers configured — text search disabled")
        return providers

    async def discover(self, query: str) -> tuple[list[DiscoveredFeed], list[str]]:
        # URL mode — unchanged
        if query.startswith("http"):
            return await self._discover_from_url(query), [query]

        # Text mode — provider chain with fallback
        for provider in self._providers:
            if not provider.is_available():
                continue
            try:
                candidate_urls = await provider.search(query)
                if candidate_urls:
                    return await self._discover_from_candidates(candidate_urls)
            except Exception as e:
                logger.warning("Provider %s failed: %s", provider.__class__.__name__, e)
                continue

        logger.warning("All search providers exhausted for query: %s", query)
        return [], []
```

### REST API

```text
POST /api/discover
Body: { "query": "European Central Bank monetary policy" }
Response: {
  "feeds": [
    {
      "url": "https://www.ecb.europa.eu/rss/press.html",
      "title": "ECB Press Releases",
      "feed_type": "RSS",
      "site_url": "https://www.ecb.europa.eu",
      "entry_count": 25
    },
    ...
  ],
  "providers_used": ["exa"],  // which providers were called (no keys exposed)
  "search_available": true     // false if no providers configured
}
```

### File Structure

```text
backend/src/infrastructure/
├── feed_discovery.py          # Existing — refactored with provider support
├── search_providers/          # New package
│   ├── __init__.py
│   ├── base.py                # SearchProvider ABC
│   ├── exa_provider.py        # Exa implementation
│   └── brave_provider.py      # Brave Search implementation
```

## Acceptance Criteria

- [ ] Text search works via Exa when API key is configured
- [ ] Brave Search works as fallback when Exa fails or is unavailable
- [ ] System starts without errors even if no API keys are configured (search disabled gracefully)
- [ ] API keys are loaded from environment only, never hardcoded or logged
- [ ] `.env.example` documents all required/optional keys
- [ ] `.env` is in `.gitignore`
- [ ] Discovery results are validated (only real RSS/Atom feeds returned)
- [ ] Results are deduplicated against existing sources
- [ ] `POST /api/discover` endpoint returns structured results
- [ ] Provider failures produce structured log entries (without exposing keys)
- [ ] Recovery mode works for the Health Monitor use case

## Open Questions

- Should we cache discovery results (e.g., same query within 24h returns cached)?
- Maximum concurrent URL validations — 5? 10? (to avoid overwhelming target sites)
- Should the API endpoint require authentication when multi-user is implemented?
