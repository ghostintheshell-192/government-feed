#!/bin/bash
# Standard automation entry point (ADR-012): run the test suite.
# Contract: runs from repo root; no args = all tests; exit != 0 = failures.
# Optional arg selects a scope: backend | frontend | all (default).
set -euo pipefail

SCOPE="${1:-all}"

run_backend() {
    if [[ ! -x .venv/bin/pytest ]]; then
        echo "test: .venv/bin/pytest missing — pip install -e './backend[dev]'"
        exit 1
    fi
    PYTHONPATH=. .venv/bin/pytest backend/tests/
}

run_frontend() {
    if [[ ! -d frontend/node_modules ]]; then
        echo "test: frontend/node_modules missing — run (cd frontend && npm install) first"
        exit 1
    fi
    npm --prefix frontend run test
}

case "$SCOPE" in
    backend)  run_backend ;;
    frontend) run_frontend ;;
    all)      run_backend; run_frontend ;;
    *)        echo "test: unknown scope '$SCOPE' (use backend | frontend | all)"; exit 1 ;;
esac

echo "test: OK ($SCOPE)"
