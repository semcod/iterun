#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../_common.sh"
_example_setup "$SCRIPT_DIR"

$CLI parse "$INTENT" --output-dir "$GENERATED" --quiet
$CLI plan "$INTENT" --output-dir "$GENERATED" --quiet
