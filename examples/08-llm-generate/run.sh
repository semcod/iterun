#!/bin/bash
# Generuj intent.yaml z promptu NL (LiteLLM) → plan → opcjonalnie execute.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../_common.sh"
_example_setup "$SCRIPT_DIR"

PROMPT="${ITERUN_PROMPT:-Create a REST API for user management}"

$CLI generate "$PROMPT" --output-dir "$GENERATED" --quiet --max-iterations 5

if [ "${ITERUN_RUN:-1}" = "1" ]; then
    $CLI plan "$GENERATED/intent.yaml" --output-dir "$GENERATED" --quiet
fi

if [ "${ITERUN_EXECUTE:-0}" = "1" ]; then
    $CLI execute "$GENERATED/intent.yaml" --workspace "$GENERATED" --quiet
fi
