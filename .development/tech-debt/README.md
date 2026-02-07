# Tech Debt Issues

This folder contains individual technical debt issues for Government Feed.

## Structure

Each issue is a separate markdown file with standardized frontmatter:

```yaml
---
type: [bug|feature|refactor|performance|testing|code-quality|security]
priority: [high|medium|low]
status: [open|in-progress|resolved|closed|rejected]
discovered: YYYY-MM-DD
related: []  # List of related issue filenames
related_decision: null  # Optional: link to reference/decisions/NNN-name.md
report: null  # Optional: link to archive/analysis/YYYY-MM-DD_report_agent-name.md
---
```

## Workflow

### Creating New Issues

1. Copy `_TEMPLATE.md`
2. Rename to descriptive slug: `issue-name.md` (NO DATE PREFIX)
3. Fill in frontmatter and content
4. Status starts as `open`

### Working on Issues

1. Update status to `in-progress`
2. Work on fix/implementation
3. When complete, add resolution sections:
   - Solution Implemented
   - Testing
   - Impact

### Archiving Completed Issues

**Automatic** (recommended):
1. Change status to `resolved`, `closed`, or `rejected` in frontmatter
2. Run: `../scripts/archive-resolved-issues.sh`
3. Script automatically moves to `archive/completed/` with date prefix

**Manual**:
1. Add date prefix: `YYYY-MM-DD_issue-name.md`
2. Move to `../archive/completed/`
3. Delete from `tech-debt/`

## Current Issues by Priority

*Auto-updated: 2026-02-07*

**High Priority:** None currently

**Medium Priority:** None currently

**Low Priority:** None currently

## Integration with Reference Documentation

### Linking to Architecture Decisions

If an issue relates to an architectural decision:

```yaml
---
related_decision: 001-clean-architecture.md
---
```

### Agent-Generated Issues

When agents (code-reviewer, security-auditor, etc.) find issues:
- Issue created automatically in `tech-debt/`
- Full report in `archive/analysis/YYYY-MM-DD_report_agent-name.md`
- Issue links to report via `report:` field

### Creating Architecture Decisions

If resolving an issue requires a significant architectural choice:
1. Document decision in `../reference/decisions/NNN-name.md`
2. Link from issue: `related_decision: NNN-name.md`

## Tips

- Use descriptive slugs for filenames
- Keep frontmatter up to date
- Link related issues in `related` field
- Date prefix ONLY when moving to archive (automatically handled by script)
- Check `_TEMPLATE.md` for structure
