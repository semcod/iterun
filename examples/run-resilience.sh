#!/bin/bash
# Skrajne prompty — test pętli naprawczej (--verify, max 5 rund).
# Wymaga: LLM, Docker, testql, intract (dla _example_e2e_verify).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -z "${OPENROUTER_API_KEY:-}" ] && [ -z "${OLLAMA_API_BASE:-}" ]; then
    echo "WARN: ustaw OPENROUTER_API_KEY lub Ollama w .env" >&2
fi

export ITERUN_MAX_VERIFY_ITERATIONS="${ITERUN_MAX_VERIFY_ITERATIONS:-5}"

echo "=== ITERUN resilience examples (repair loop) ==="
failed=0
for ex in 13-resilience-vague 14-resilience-inventory 15-resilience-nested-paths 16-resilience-framework-trap; do
    echo "--- $ex ---"
    bash "$SCRIPT_DIR/$ex/run.sh" || failed=1
done

if [ "$failed" -ne 0 ]; then
    echo "=== RESILIENCE FAILED ===" >&2
    exit 1
fi
echo "=== RESILIENCE OK (4 examples) ==="
