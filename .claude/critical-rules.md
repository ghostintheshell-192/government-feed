# Critical Architecture Rules

These rules apply across the entire codebase and must not be violated.

## Clean Architecture Layer Direction

Core has no knowledge of Infrastructure or API. Dependencies point inward: API -> Infrastructure -> Core. Core defines interfaces (abstract base classes), Infrastructure implements them.

## Privacy-First AI Processing

All AI processing happens locally via Ollama. Never send data to external cloud AI services. Content scraping and summarization are done server-side only.

## Content Deduplication

SHA256 hash on `title|content|source|date` for deduplication. Always check content_hash before inserting new items. Unique index on content_hash in database.

---

*These rules reflect foundational architectural decisions. See `.development/reference/decisions/` for detailed ADRs.*
