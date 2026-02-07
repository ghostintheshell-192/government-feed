# Decision Log

This folder contains documentation of significant architectural decisions made for the Government Feed project.

## Format

Each decision document follows this structure:

- **Date**: When the decision was made
- **Status**: Proposed, Active, Superseded, Deprecated
- **Context**: Why was this decision needed?
- **Decision**: What was decided
- **Rationale**: Why this option was chosen
- **Consequences**: Implications and trade-offs

## Status Legend

- **Proposed**: Decision accepted, awaiting implementation
- **Active**: Implemented and in effect
- **Superseded**: Replaced by another decision
- **Deprecated**: No longer applicable

## Decisions

1. [Clean Architecture](001-clean-architecture.md) - Layer separation and dependency direction
2. [Privacy-First AI](002-privacy-first-ai.md) - Local AI processing with Ollama
3. [Content Deduplication](003-content-deduplication.md) - SHA256 hashing strategy
