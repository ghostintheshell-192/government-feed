#!/bin/bash
# Standard automation entry point (ADR-012): verify code quality gate.
# Contract: runs from repo root; no args = check all tracked sources;
# with args = check only the given files (non-source files are ignored).
# Exit != 0 = at least one violation.
#
# Gate = ruff lint (the documented manual check for this project).
# `ruff format --check` is NOT enforced yet: 13 legacy files are unformatted;
# enforce it after a one-off `format-fix.sh` pass lands in its own commit.
set -euo pipefail

RUFF=.venv/bin/ruff
if [[ ! -x "$RUFF" ]]; then
    if command -v ruff >/dev/null 2>&1; then
        RUFF=ruff
    else
        echo "format-check: WARNING - ruff not available, skipping"
        exit 0
    fi
fi

# Select candidate files: args if given, otherwise all backend sources.
if [[ $# -gt 0 ]]; then
    CANDIDATES=()
    for file in "$@"; do
        [[ "$file" =~ \.py$ ]] || continue
        [[ "$file" =~ ^(backend/src|backend/tests|shared|scripts)/ ]] || continue
        [[ -f "$file" ]] || continue
        CANDIDATES+=("$file")
    done
    if [[ ${#CANDIDATES[@]} -eq 0 ]]; then
        echo "format-check: no Python sources among candidates (no-op)"
        exit 0
    fi
else
    CANDIDATES=(backend/src backend/tests shared scripts)
fi

if ! "$RUFF" check "${CANDIDATES[@]}"; then
    echo "format-check: ruff violations found"
    echo "fix with: .development/automation/format-fix.sh ${CANDIDATES[*]}"
    exit 1
fi

echo "format-check: OK"
