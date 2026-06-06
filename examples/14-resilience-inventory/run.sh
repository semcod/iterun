#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../_common.sh"
source "$SCRIPT_DIR/../_verify.sh"

ITERUN_MAX_VERIFY_ITERATIONS="${ITERUN_MAX_VERIFY_ITERATIONS:-5}"
_example_setup "$SCRIPT_DIR"
_example_copy_expectations
_example_generate execute
_example_show_verify_rounds

"$PYTHON" -c "import json,sys; s=json.load(open(sys.argv[1])); sys.exit(0 if s.get('success') else 1)" "$GENERATED/session.json"
_example_e2e_verify
echo "OK resilience-inventory"
