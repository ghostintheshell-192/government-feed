# Workflow

## Session Start

At the beginning of every session, before starting any work:

1. **Read the latest handoff** in `.memory-bank/` (the most recent `.md` file by date in the filename)
2. **Read any linked files** referenced in the handoff (e.g., progress specs, related notes)
3. **Cross-reference** with `memory/MEMORY.md` for stable project facts (if present)

This ensures continuity between sessions. The `.memory-bank/` contains detailed
session diaries (what was done, why, what's next), while `memory/MEMORY.md`
(when present) holds a compact index of stable facts.

## Session End

**Write a handoff note before ending any session.** This is non-negotiable: the
`.memory-bank/` diary is the primary continuity mechanism between sessions, and
skipping it breaks that continuity.

When the user signals end of session — in any form, in any language — invoke
the `session-handoff` skill **before** replying farewell.

The handoff lives in `.memory-bank/` with filename `YYYY-MM-DD-HHmm-<slug>.md`
and structure **Done / Next / Notes**. If the session touched multiple branches
or merges, include commit hashes and branch names so the next session can resume
git state without hunting. If anything was deferred or flagged for later,
capture it in **Next** so it does not get lost.

Do not rely only on the `SessionEnd` hook in `.claude/settings.json` — that
archives the raw transcript, it does not produce a semantic handoff.

---

## Git Workflow

**Branch strategy:**

- `main`: releases only
- `develop`: default branch for development
- `feature/*`, `fix/*`, `docs/*`, `refactor/*`, `experiment/*`, `chore/*`: task branches

**NEVER work on `main` or `develop` directly.** Branch protection is enforced by
the pre-commit hook (`.githooks/pre-commit.d/00-branch-protection`), which blocks
direct commits on these branches. Merge commits (`git merge --no-ff`) are
explicitly allowed — that is the supported path to land work.

**ALWAYS run git commands from the project root** (`/data/repos/government-feed`).
Before staging or committing, verify `pwd` — subdirectories cause path mismatches.

**Typical workflow:**

```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/task-name

# Work and commit
git add <files>
git commit -m "feat: descriptive message"

# Merge when complete
git checkout develop
git merge --no-ff feature/task-name
git push origin develop
```

### Spec lifecycle automation

Spec files are moved between `specs/{planned,in-progress,implemented}/` based
on git activity:

- **`post-checkout`**: on `git checkout -b {feature,fix,docs,refactor,experiment}/<name>`,
  the matching spec in `specs/planned/<name>.md` is moved to `specs/in-progress/`
  and its frontmatter `status` field is updated.
- **`post-merge`**: on no-conflict merges into `develop` (the normal case —
  git creates those commits directly and pre-commit does NOT run), the merged
  branch is parsed from the merge commit subject and the matching spec is
  moved to `specs/implemented/` and staged. The hook then prints the
  one-liner to fold it in (`git commit --amend --no-edit`) — run it right
  after the merge.
- **`pre-commit.d/05-spec-workflow`**: covers the complementary case only —
  conflicted merges concluded manually via `git commit`, where `MERGE_HEAD`
  still exists and pre-commit does run.

The script at `.development/scripts/spec-workflow.py` is the shared backend;
missing specs, unknown branch prefixes, and non-merge commits all exit silently.

### Automation entry points

Hooks and CI are **generic orchestrators**: they contain no stack-specific
commands. All stack knowledge lives in standard entry points under
`.development/automation/`:

| Entry point | Contract |
| ----------- | -------- |
| `build.sh` | Frontend production bundle (tsc + vite); exit != 0 on failure |
| `test.sh [backend\|frontend\|all]` | Run tests (pytest + vitest) |
| `format-check.sh [files...]` | Ruff lint gate; no args = all backend sources |
| `format-fix.sh [files...]` | Apply ruff autofix + formatting |
| `docs-update.sh` | Regenerate ARCHITECTURE.md, INDEX.md, tech-debt index, README status |

No args = act on everything. Multi-stack knowledge (which command for which
part of the tree) belongs *inside* the entry point, never in hooks or CI.

### Hook activation (once per clone)

```bash
bash .development/automation/bootstrap.sh
```

Sets `core.hooksPath .githooks` locally, verifies prerequisites, and makes
hooks/entry points executable. Without this, branch protection and the
project hooks are NOT active.

## Investigation & Analysis Workflow

When analyzing tech-debt, bugs, or investigating issues:

1. **Read the tech-debt/issue description** - Understand the problem
2. **Read `.development/ARCHITECTURE.md`** - Find relevant files using:
   - Project Tree (file index with descriptions)
   - Layer Overview (understand dependencies)
   - Related ADRs (architectural context)
3. **Read files in logical order** - Follow layer structure (Core <- Infrastructure -> API)
4. **Report findings** - Summary of what you found and where

**Always read ARCHITECTURE.md before exploring code** - it's your navigation map.

## Quick Commands

```bash
# Backend - run
cd backend && uvicorn backend.src.api.main:app --reload

# Frontend - run
cd frontend && pnpm dev

# Tests (entry point — stack knowledge lives inside the script)
.development/automation/test.sh            # all
.development/automation/test.sh backend    # pytest only

# Lint gate
.development/automation/format-check.sh

# Type checking
mypy backend/src

# Regenerate derived docs
.development/automation/docs-update.sh

# Docker services (Redis, Ollama)
docker-compose up -d
```
