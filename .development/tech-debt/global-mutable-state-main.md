---
type: refactor
priority: low
status: partially-resolved
discovered: 2026-03-07
related: [feedparser-bypasses-uow.md]
related_decision: 001-clean-architecture.md
report: null
---

# Global mutable state in main.py

## Problem

Module-level mutable variables in `main.py`:

```python
_scheduler: FeedScheduler | None = None
_cache: RedisCache | None = None
```

These are mutated during startup/shutdown events and accessed by endpoint handlers. Similarly, `OllamaService` is re-instantiated per request (main.py:408) with settings lookups each time.

## Impact

- Makes parallel testing difficult (shared state between test runs)
- No clear lifecycle management
- OllamaService settings are read from disk on every summarize request

## Recommended Approach

This will naturally resolve when migrating from `on_event` to FastAPI's lifespan pattern, which uses `app.state` for shared resources. The lifespan context manager provides clean setup/teardown semantics.

## Notes

- Low priority as a standalone fix — couple with the deprecated APIs migration
- Consider making OllamaService a singleton stored in `app.state`
