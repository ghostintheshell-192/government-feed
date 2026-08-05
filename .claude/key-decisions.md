# Key Decisions

⚠️ **Auto-generated digest of high-impact architecture decisions (ADR Impact ≥ high).**
Loaded into every session via the @include in `.claude/CLAUDE.md`. Open the linked ADR for full context.

## Critical — must not be violated

Constraints that apply across the whole codebase.

- **[ADR-001: Clean Architecture](../.development/reference/decisions/001-clean-architecture.md)** — Clean Architecture with inward-pointing dependencies (API -> Infrastructure -> Core); Core defines interfaces and knows nothing about outer layers.
- **[ADR-002: Privacy-First AI Processing](../.development/reference/decisions/002-privacy-first-ai.md)** — All AI processing happens locally via Ollama — no content is ever sent to external cloud AI services.
- **[ADR-003: Content Deduplication via SHA256](../.development/reference/decisions/003-content-deduplication.md)** — News items are deduplicated via SHA256 hash of title|content|source|date, enforced by a unique index on content_hash.
- **[ADR-009: No Profiling — Neither Readers Nor Publishers](../.development/reference/decisions/009-no-profiling-readers-or-publishers.md)** — The system never builds a profile of an actor — not of the reader from reading behaviour, nor of a news outlet from publishing behaviour; it may show per-item verifiable facts, never aggregate labels about who produced them.

## High-impact context

Decisions that shape ongoing work — know these before deciding.

- **[ADR-004: Master-Detail Panel Layout for Dashboard](../.development/reference/decisions/004-master-detail-layout.md)** — Proposed responsive master-detail dashboard layout: side-by-side list and detail panel on desktop, separate detail page on mobile.
- **[ADR-005: Geographic Levels as Primary Navigation Structure](../.development/reference/decisions/005-geographic-levels-navigation.md)** — Concentric geographic levels (LOCAL -> NATIONAL -> CONTINENTAL -> GLOBAL) are the primary navigation structure for sources.
- **[ADR-007: Catalog-Subscription Model for Source Management](../.development/reference/decisions/007-catalog-subscription-model.md)** — Single Source table acts as the global catalog with a subscriptions pivot table linking users to sources — no data duplication between catalog and user selection.
- **[ADR-008: Data Locality — Catalog vs User Content](../.development/reference/decisions/008-data-locality-split.md)** — Deferred to M5: split storage into a stable catalog DB (sources, subscriptions) and an ephemeral user content DB (news items, read state).

---

*Auto-generated from ADRs with Impact ≥ high. Run `.development/scripts/generate-claude-config.sh` to update.*
