#!/usr/bin/env python3
"""Generate auto-updated Current Status and Roadmap sections for README.md.

Reads spec files from .development/specs/ subdirectories to determine
milestone completion. Updates README.md between marker comments.

Usage: python3 .development/scripts/generate-readme-status.py
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SPECS_DIR = PROJECT_ROOT / ".development" / "specs"
README_PATH = PROJECT_ROOT / "README.md"

# Milestone definitions (order matters for display)
MILESTONES = {
    "M1-MVP": "MVP Backend",
    "M2-Production": "Production-Ready Backend",
    "M3-Frontend": "Frontend",
    "M4-Advanced": "Advanced Features",
    "M5-Scaling": "Scaling & Multi-User",
}

# Status directories map to these states
STATUS_DIRS = ["implemented", "in-progress", "planned", "backlog"]


def parse_spec_frontmatter(filepath: Path) -> dict[str, str]:
    """Extract frontmatter fields from a spec file."""
    result = {}
    text = filepath.read_text(encoding="utf-8")
    # Title from first heading
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()
    # Frontmatter fields
    for field in ("Status", "Milestone", "Priority"):
        match = re.search(rf"^\*\*{field}\*\*:\s*(.+)$", text, re.MULTILINE)
        if match:
            result[field.lower()] = match.group(1).strip()
    return result


def collect_specs() -> list[dict[str, str]]:
    """Collect all specs with their status from directory location."""
    specs = []
    for status_dir in STATUS_DIRS:
        dir_path = SPECS_DIR / status_dir
        if not dir_path.exists():
            continue
        for spec_file in sorted(dir_path.glob("*.md")):
            if spec_file.name == "README.md":
                continue
            info = parse_spec_frontmatter(spec_file)
            info["dir_status"] = status_dir
            info["filename"] = spec_file.stem
            specs.append(info)
    return specs


def group_by_milestone(specs: list[dict[str, str]]) -> dict[str, dict[str, list]]:
    """Group specs by milestone, then by status."""
    grouped: dict[str, dict[str, list]] = {}
    for ms_key in MILESTONES:
        grouped[ms_key] = {s: [] for s in STATUS_DIRS}

    for spec in specs:
        ms = spec.get("milestone", "unassigned")
        if ms in grouped:
            status = spec["dir_status"]
            grouped[ms][status].append(spec)

    return grouped


def milestone_status_label(counts: dict[str, int]) -> str:
    """Determine milestone status from spec counts."""
    total = sum(counts.values())
    if total == 0:
        return "planned"
    if counts["implemented"] == total:
        return "done"
    if counts["in-progress"] > 0 or (
        counts["implemented"] > 0 and counts["implemented"] < total
    ):
        return "in-progress"
    return "planned"


STATUS_ICONS = {
    "done": "✅",
    "in-progress": "🔧",
    "planned": "📋",
}


def generate_status_section(grouped: dict[str, dict[str, list]]) -> str:
    """Generate the Current Status markdown section."""
    lines = []

    for ms_key, ms_label in MILESTONES.items():
        by_status = grouped[ms_key]
        counts = {s: len(by_status[s]) for s in STATUS_DIRS}
        total = sum(counts.values())
        if total == 0:
            continue

        status = milestone_status_label(counts)
        icon = STATUS_ICONS[status]

        impl = counts["implemented"]
        lines.append(f"{icon} **{ms_label}** ({impl}/{total} features)")

        if status == "done":
            lines.append("")
            continue

        # Show implemented features as checked, rest as unchecked
        for spec in by_status["implemented"]:
            lines.append(f"- [x] {spec.get('title', spec['filename'])}")
        for s in ("in-progress", "planned", "backlog"):
            for spec in by_status[s]:
                lines.append(f"- [ ] {spec.get('title', spec['filename'])}")
        lines.append("")

    return "\n".join(lines)


def generate_roadmap_section(grouped: dict[str, dict[str, list]]) -> str:
    """Generate the Roadmap markdown section."""
    lines = []

    for ms_key, ms_label in MILESTONES.items():
        by_status = grouped[ms_key]
        counts = {s: len(by_status[s]) for s in STATUS_DIRS}
        total = sum(counts.values())
        if total == 0:
            continue

        status = milestone_status_label(counts)
        icon = STATUS_ICONS[status]
        impl = counts["implemented"]

        lines.append(f"| {icon} {ms_key} | {ms_label} | {impl}/{total} |")

    return "\n".join(lines)


def update_readme(status_content: str, roadmap_content: str) -> bool:
    """Update README.md between marker comments. Returns True if changed."""
    if not README_PATH.exists():
        return False

    text = README_PATH.read_text(encoding="utf-8")
    original = text

    # Replace status section
    text = re.sub(
        r"<!-- AUTO:STATUS -->.*?<!-- /AUTO:STATUS -->",
        f"<!-- AUTO:STATUS -->\n{status_content}\n<!-- /AUTO:STATUS -->",
        text,
        flags=re.DOTALL,
    )

    # Replace roadmap section
    text = re.sub(
        r"<!-- AUTO:ROADMAP -->.*?<!-- /AUTO:ROADMAP -->",
        f"<!-- AUTO:ROADMAP -->\n{roadmap_content}\n<!-- /AUTO:ROADMAP -->",
        text,
        flags=re.DOTALL,
    )

    if text != original:
        README_PATH.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    specs = collect_specs()
    grouped = group_by_milestone(specs)

    status_section = generate_status_section(grouped)
    roadmap_section = generate_roadmap_section(grouped)

    changed = update_readme(status_section, roadmap_section)
    if changed:
        print(f"Updated: {README_PATH}")
    else:
        print("No changes to README.md")


if __name__ == "__main__":
    main()
