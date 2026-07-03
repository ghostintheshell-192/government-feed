#!/bin/bash
# Standard automation entry point (ADR-012): apply lint fixes + formatting.
# Contract: runs from repo root; no args = fix all backend sources;
# with args = fix only the given files.
set -euo pipefail

RUFF=.venv/bin/ruff
if [[ ! -x "$RUFF" ]]; then
    if command -v ruff >/dev/null 2>&1; then
        RUFF=ruff
    else
        echo "format-fix: ERROR - ruff not available"
        exit 1
    fi
fi

if [[ $# -gt 0 ]]; then
    TARGETS=("$@")
else
    TARGETS=(backend/src backend/tests shared scripts)
fi

"$RUFF" check --fix "${TARGETS[@]}"
"$RUFF" format "${TARGETS[@]}"

echo "format-fix: done"
