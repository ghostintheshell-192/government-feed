---
type: code-quality
priority: low
status: open
discovered: 2026-07-03
related: []
related_decision: null
report: null
---

# Tool version drift between local venv and CI (ruff, mypy)

## Problem

CI installs lint/type tools at their latest version (`pyproject.toml` dev
extras pin `ruff>=0.8.5`, `mypy>=1.14.0`), while the local `.venv` keeps
whatever version was installed at setup time. Every new ruff rule that lands
upstream can turn CI red on code that is green locally — it already happened
on the very first CI run: UP042 (`StrEnum` on Python 3.13) failed the build
while the local ruff didn't know the rule yet. The same class of failure can
come from mypy version bumps.

## Analysis

The dev extras use `>=` lower bounds, which is correct for *compatibility*
but gives no *reproducibility*: local and CI resolve to different versions
whenever upstream releases. The gap only grows with time since the venv is
rarely rebuilt. Lint rules are effectively part of the project's quality
gate, so the gate should be versioned like any other dependency — or the two
environments should be kept deliberately in sync.

## Possible Solutions

- **Option A — keep local up to date**: periodically run
  `.venv/bin/pip install -U ruff mypy` (e.g. when starting a new milestone),
  keeping `>=` pins. Pros: project benefits from new rules early, zero config.
  Cons: requires the habit; CI can still break first when upstream releases
  mid-milestone.
- **Option B — pin exact versions**: `ruff==X.Y.Z`, `mypy==X.Y.Z` in dev
  extras; bump deliberately in dedicated commits. Pros: local == CI, fully
  reproducible, breakage only at chosen upgrade time. Cons: rules go stale
  unless someone remembers to bump; upgrade commits can carry a batch of new
  violations to fix at once.

## Recommended Approach

**Option A**, made systematic: add "update ruff/mypy in the venv and fix any
new findings" as a start-of-milestone chore. The project is small enough that
new-rule fallout is minutes of work (UP042 was a 3-line fix), and staying
current with lint rules aligns with the coding standards (UP = pyupgrade,
modern syntax). Revisit Option B if the project gains contributors or the
fallout stops being trivial.

## Notes

First occurrence fixed in commit `d377b86` (StrEnum for GeographicLevel and
HealthStatus). If a CI run goes red on a rule the local ruff doesn't know,
the quick check is `.venv/bin/ruff --version` vs the version CI logs during
`pip install`.

## Related Documentation

- **Code Locations**: `backend/pyproject.toml` (`[project.optional-dependencies] dev`),
  `.github/workflows/ci.yml` (Install backend step),
  `.development/automation/format-check.sh`

---

Investigation Note: Read [ARCHITECTURE.md](../ARCHITECTURE.md) to locate relevant files and understand the architectural context before starting your analysis.
