#!/bin/bash
# Smoke: plan kilku intentów; execute tylko gdy ITERUN_EXECUTE=1 i Docker dostępny.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../_common.sh"
_example_setup "$SCRIPT_DIR"

$CLI plan "$INTENT" --output-dir "$GENERATED" --quiet

for sub in 02-ping-smoke 03-flask-api 04-express-api; do
    sub_intent="$EXAMPLES_ROOT/$sub/intent.yaml"
    sub_gen="$EXAMPLES_ROOT/$sub/generated"
    mkdir -p "$sub_gen"
    $CLI plan "$sub_intent" --output-dir "$sub_gen" --quiet
done

if [ "${ITERUN_EXECUTE:-0}" = "1" ] && command -v docker >/dev/null 2>&1; then
    $CLI execute "$INTENT" --workspace "$GENERATED" --quiet
fi
