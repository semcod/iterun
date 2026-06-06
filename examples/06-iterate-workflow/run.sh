#!/bin/bash
# Krok 1: plan. Pełna iteracja wymaga interaktywnej powłoki (patrz README).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../_common.sh"
_example_setup "$SCRIPT_DIR"

$CLI plan "$INTENT" --output-dir "$GENERATED" --quiet
