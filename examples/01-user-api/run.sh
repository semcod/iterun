#!/bin/bash
# Dry-run + opcjonalne wykonanie Docker (ITERUN_EXECUTE=1).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=../_common.sh
source "$SCRIPT_DIR/../_common.sh"
_example_setup "$SCRIPT_DIR"

$CLI plan "$INTENT" --output-dir "$GENERATED" --quiet

if [ "${ITERUN_EXECUTE:-0}" = "1" ]; then
    $CLI execute "$INTENT" --workspace "$GENERATED" --quiet
fi
