# Database Migrations

**Status**: planned
**Milestone**: M2-Production
**Priority**: should-have
**Depends on**: [repository-pattern](../implemented/repository-pattern.md)

## Summary

Alembic-based migration workflow for safe schema evolution, supporting both SQLite (development) and PostgreSQL (production) databases with versioned, reversible migrations.

## User Stories

- As a developer, I want to evolve the database schema safely without losing data
- As an operator, I want database upgrades to be automated and reversible

## Requirements

### Functional

- [ ] Alembic initialized with migration environment
- [ ] Auto-generate migrations from SQLAlchemy model changes
- [ ] Support both SQLite (dev) and PostgreSQL (prod) dialects
- [ ] Forward migrations (upgrade) for schema changes
- [ ] Reverse migrations (downgrade) for rollback capability
- [ ] Migration history tracking in database
- [ ] Initial migration capturing current schema as baseline

### Non-Functional

- Safety: Migrations are tested before production deployment
- Reversibility: Every migration has a corresponding downgrade
- Compatibility: Same migration files work on SQLite and PostgreSQL

## Technical Notes

- Alembic is already configured but unused (noted in technical.md)
- Configuration: `alembic.ini` + `alembic/env.py`
- Migration directory: `backend/alembic/versions/`
- Workflow:
  1. Modify SQLAlchemy models
  2. `alembic revision --autogenerate -m "description"`
  3. Review generated migration
  4. `alembic upgrade head` to apply
  5. `alembic downgrade -1` to rollback if needed
- Considerations for SQLite limitations (ALTER TABLE constraints)
- Production workflow: run migrations before deploying new code

## Acceptance Criteria

- [ ] Initial baseline migration created from current schema
- [ ] Auto-generation detects model changes correctly
- [ ] Migrations run on both SQLite and PostgreSQL
- [ ] Downgrade works for all migrations
- [ ] Migration state is tracked in `alembic_version` table
