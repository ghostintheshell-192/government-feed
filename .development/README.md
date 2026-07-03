# .development/ - Development Documentation

Private development documentation for spec-driven development workflow.

**Committed to git** - shared development documentation.

## Quick Start

1. Read `CURRENT-STATUS.md` for project state
2. Read `INDEX.md` for full navigation (auto-generated)
3. Check `tech-debt/` for active issues

## Structure

```
.development/
├── CURRENT-STATUS.md      # Current project state
├── INDEX.md               # Auto-generated navigation
│
├── specs/                 # Feature specifications
│   ├── implemented/       # Completed features
│   ├── in-progress/       # Currently being developed
│   ├── planned/           # Confirmed for next milestones
│   ├── backlog/           # Validated but not scheduled
│   └── archived/          # Deprecated/cancelled
│
├── tech-debt/             # Active technical debt
│   ├── _TEMPLATE.md       # Template for new issues
│   └── issue-name.md      # Individual tracked issues
│
├── reference/             # Reference documentation
│   ├── decisions/         # Architecture Decision Records (ADR)
│   ├── technical/         # Technical notes
│   └── checklists/        # Workflow checklists
│
├── archive/               # Historical
│   ├── completed/         # Resolved issues
│   ├── analysis/          # Agent reports
│   ├── postmortems/       # Post-mortems
│   └── legacy/            # Old files
│
├── automation/            # Standard entry points (ADR-012 pattern)
│   ├── bootstrap.sh       # Once-per-clone activation (hooksPath, exec bits)
│   ├── build.sh           # Build the project (stack knowledge lives here)
│   ├── test.sh            # Run tests (backend | frontend | all)
│   ├── format-check.sh    # Verify lint gate (ruff)
│   ├── format-fix.sh      # Apply lint fixes + formatting
│   └── docs-update.sh     # Regenerate derived docs
│
└── scripts/               # Utility scripts (generators, workflow backends)
    ├── generate-index.py
    ├── generate-architecture.sh
    ├── generate-readme-status.py
    ├── generate-claude-config.sh
    ├── update-tech-debt-index.py
    ├── spec-workflow.py
    ├── session-archive.py
    └── archive-resolved-issues.sh
```

### Automation entry points

Git hooks and CI are **generic orchestrators**: they contain no stack-specific
commands. All stack knowledge lives in the entry points under `automation/`.
Activate hooks once per clone with `bash .development/automation/bootstrap.sh`.

## Workflow

### Tech Debt

```
1. Create: tech-debt/issue-name.md (use _TEMPLATE.md)
2. Work: Update notes, track progress
3. Resolve: Change status to "resolved"
4. Archive: Run scripts/archive-resolved-issues.sh
```

### Architecture Decisions (ADR)

Create in `reference/decisions/` when:
- Architectural pattern choice
- Technology selection
- Cross-cutting concern decision
- Trade-off impacting multiple components

Format: `NNN-descriptive-name.md`

### Agent Reports

Agents write to:
- Full report -> `archive/analysis/YYYY-MM-DD_report_agent-name.md`
- Critical findings -> `tech-debt/` as individual issues

## Related

- Public docs: `docs/`
- Personal notes: `.personal/`

---

*Run `python scripts/generate-index.py` to regenerate INDEX.md*
