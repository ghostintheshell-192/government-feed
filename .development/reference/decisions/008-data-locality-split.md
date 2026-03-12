# ADR-008: Data Locality — Catalog vs User Content

**Date**: 2026-03-12
**Status**: Proposed
**Impact**: significant
**Target milestone**: M5

## Context

Government Feed currently stores everything in a single SQLite database: the source catalog (stable, curated), user subscriptions, and news articles (high-volume, ephemeral). This works for the current single-user, fully local setup, but raises concerns as the system evolves:

1. **Different lifecycles**: Catalog data is stable and grows slowly. Articles are volatile, high-volume, and subject to automatic cleanup (30-day retention).
2. **Different ownership**: The catalog is a shared, curated asset (maintained by the project). Articles are personal — what a user has fetched based on their subscriptions.
3. **Reset without damage**: A user should be able to wipe their articles (or let them expire) without affecting the catalog or their subscriptions.
4. **Multi-user preparation (M5)**: When multiple users exist, each will accumulate their own articles. A shared catalog with per-user article stores is the natural model.
5. **Portability**: A user's article database could be backed up, exported, or moved independently from the catalog.

## Decision

**Deferred to M5.** When multi-user support is implemented, split storage into two logical stores:

| Store | Contains | Lifecycle | Owner |
|-------|----------|-----------|-------|
| **Catalog DB** | `sources`, `subscriptions`, app config | Stable, persisted indefinitely | Server / project |
| **Content DB** | `news_items`, read state, user annotations | Ephemeral, auto-cleaned after retention period | User |

### Current state (M4)

The separation is already **logically** in place:
- `sources` and `subscriptions` are stable catalog/config data
- `news_items` are ephemeral with a 30-day cleanup job in the scheduler
- Read/unread state uses `localStorage` (already client-side)

No code changes are needed now. The current single-SQLite setup is appropriate for single-user local use.

### Future state (M5)

When implementing multi-user:
- Evaluate whether the split should be **two SQLite files**, **SQLite + PostgreSQL**, or **server DB + IndexedDB** (browser-local), depending on the deployment model chosen in M5
- The `news_items` table already has no FK constraint to `sources` (noted as tech-debt), which coincidentally makes the split easier
- `content_hash` deduplication remains per-user (each user fetches their own copy)

## Rationale

- **No premature optimization**: The current architecture handles the single-user case well. Splitting now would add complexity without benefit.
- **Clear migration path**: The logical separation (catalog tables vs content tables) is already clean, making a future physical split straightforward.
- **User mental model**: Users think of "my articles" as temporary/disposable and "my sources" as their configuration. The architecture should reflect this.

## Consequences

- **Now**: No code changes. This ADR documents the architectural intent for M5 planning.
- **M5**: Database configuration will need to support multiple stores. Migration tooling (Alembic) may need adjustment.
- **Positive**: Clean data ownership model, independent lifecycle management, natural multi-user scaling.
- **Risk**: If the deployment model changes significantly (e.g., fully cloud-hosted), the split strategy may need revisiting.

## Related

- [ADR-007: Catalog-Subscription Model](007-catalog-subscription-model.md) — defines the catalog/subscription separation this builds on
- Tech-debt: Missing FK constraint `news_items → sources` — relevant to future split
- M5 milestone: Multi-user support
