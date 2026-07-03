---
type: bug
priority: medium
status: open
discovered: 2026-07-03
related: []
related_decision: null
report: null
---

# Naive/aware datetime mismatch between DB columns and code

## Problem

All SQLAlchemy `DateTime` columns (SQLite) store and return **offset-naive**
datetimes, while the codebase — since the `datetime.utcnow()` deprecation fix
of 2026-03-08 — produces **offset-aware** `datetime.now(UTC)` values. Any
arithmetic or comparison between a column value and a fresh timestamp raises
`TypeError: can't subtract offset-naive and offset-aware datetimes`.

First casualty: the scheduler's poll loop crashed on the first source with a
non-null `last_fetched`, and because the try/except wrapped the whole loop,
**scheduled feed polling was silently dead from 2026-03-08 to 2026-07-03**
(feeds only updated via manual fetch). Fixed point-wise in
`fix/scheduler-naive-datetime` (naive→UTC normalization + per-source error
isolation), but the mismatch remains latent for every other datetime column.

## Analysis

- SQLite has no timezone-aware storage; SQLAlchemy's `DateTime` strips tzinfo
  on write and returns naive values on read. `DateTime(timezone=True)` is not
  honored by the SQLite dialect.
- Affected columns: `last_fetched`, `last_health_check`, `last_healthy_at`,
  `published_date`, `created_at`, `verified_at`, subscription timestamps.
- Unit tests did not catch it because mocks used aware datetimes — a
  mock-reality gap. The regression test now uses a naive value on purpose.
- Comparisons executed *inside SQL* (e.g. cleanup `cutoff`) work by string
  comparison and mostly order correctly, but only by accident.

## Possible Solutions

- **Option A — UTCDateTime TypeDecorator**: a custom type that converts to
  naive UTC on bind and attaches `tzinfo=UTC` on result. Applied to all
  datetime columns in `models.py`. Pros: single systemic fix, code can assume
  aware everywhere, no data migration needed (stored values are already UTC).
  Cons: touches every model; needs a sweep of tests that pass naive values.
- **Option B — normalize at each usage site**: the scheduler-style
  `if dt.tzinfo is None: dt = dt.replace(tzinfo=UTC)` wherever arithmetic
  happens. Pros: zero model changes. Cons: whack-a-mole; every new feature
  (M4b enrichment timestamps!) can reintroduce the crash.
- **Option C — go all-naive**: store and compute naive UTC everywhere.
  Pros: consistent. Cons: regression to the pre-March style the project
  deliberately abandoned; loses explicitness.

## Recommended Approach

Option A, scheduled **before M4b implementation starts** — enrichment jobs
will add new datetime arithmetic and would inherit the trap. It also matters
for the M5 PostgreSQL migration (which *does* honor `timezone=True`): the
TypeDecorator gives one consistent behavior across both engines.

## Notes

Point fix in place: `backend/src/infrastructure/scheduler.py`
(`_poll_all_feeds`). Regression tests:
`test_polls_source_with_naive_last_fetched`,
`test_broken_source_does_not_abort_cycle`.

## Related Documentation

- **Code Locations**: `backend/src/infrastructure/models.py` (all DateTime
  columns), `backend/src/infrastructure/scheduler.py:86`,
  `backend/src/infrastructure/health_monitor.py:100`
- **Related Issues**: archived `2026-03-08_deprecated-datetime-utcnow.md`
  (the fix that exposed this)

---

Investigation Note: Read [ARCHITECTURE.md](../ARCHITECTURE.md) to locate relevant files and understand the architectural context before starting your analysis.
