#!/bin/bash
# Standard automation entry point (ADR-012): build the project.
# Contract: runs from repo root; no args = full build; exit != 0 = failure.
# All stack-specific knowledge lives HERE, not in hooks/CI.
#
# The backend is interpreted Python (no build step); "build" means the
# frontend production bundle, which also runs tsc and fails on type errors.
set -euo pipefail

if [[ ! -d frontend/node_modules ]]; then
    echo "build: frontend/node_modules missing — run (cd frontend && npm install) first"
    exit 1
fi

npm --prefix frontend run build

echo "build: OK (frontend bundle)"
