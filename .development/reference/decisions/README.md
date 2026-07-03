# Decision Log

This folder contains documentation of significant architectural decisions made for the Government Feed project.

## Format

Each decision document follows the structure in `_TEMPLATE.md`:

- **Date**: When the decision was made
- **Status**: Proposed, Accepted, Active, Deferred, Superseded, Deprecated
- **Impact**: critical | high | medium | low
- **Summary**: One sentence — *what* the ADR decides (extracted by generators)
- **Context**: Why was this decision needed?
- **Decision**: What was decided
- **Rationale**: Why this option was chosen
- **Consequences**: Implications and trade-offs

## Impact Scale

Controls how far the decision reaches into the agent's context:

- **critical** → rule that must never be violated. Loaded into `.claude/key-decisions.md`, read at every session start.
- **high** → context that shapes decisions. Loaded into `.claude/key-decisions.md`.
- **medium** → relevant, consult on demand. Indexed only.
- **low** → historical or narrow record. Indexed only.

Run `.development/scripts/generate-claude-config.sh` after changing Impact or
Summary fields to regenerate `key-decisions.md`.

## Status Legend

- **Proposed**: Under discussion or awaiting implementation
- **Accepted / Active**: Implemented and in effect
- **Deferred**: Decision made to postpone (target milestone noted)
- **Superseded**: Replaced by another decision
- **Deprecated**: No longer applicable

## Decisions

1. [Clean Architecture](001-clean-architecture.md) - Layer separation and dependency direction
2. [Privacy-First AI](002-privacy-first-ai.md) - Local AI processing with Ollama
3. [Content Deduplication](003-content-deduplication.md) - SHA256 hashing strategy
4. [Master-Detail Layout](004-master-detail-layout.md) - Dashboard panel layout (proposed)
5. [Geographic Levels Navigation](005-geographic-levels-navigation.md) - Concentric geographic levels as primary navigation
6. [Headless Browser Scraping](006-headless-browser-scraping.md) - Deferred to M5+
7. [Catalog-Subscription Model](007-catalog-subscription-model.md) - Single Source table + subscriptions pivot
8. [Data Locality Split](008-data-locality-split.md) - Catalog DB vs user content DB (deferred to M5)
