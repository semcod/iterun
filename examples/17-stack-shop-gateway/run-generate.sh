#!/bin/bash
# Prompt → LLM → iterun.yaml w generated/ → plan → docker compose
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../_common.sh"
_example_setup "$SCRIPT_DIR"

_example_read_prompt
$CLI generate "$PROMPT" --output-dir "$GENERATED" --run --execute --quiet \
    --max-iterations 5
echo "OK generate+stack → $GENERATED (see docker-compose.yaml)"
