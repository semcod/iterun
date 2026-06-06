#!/bin/bash
# Celowo mglisty prompt + surowe expectations → wymusza pętlę naprawczą --verify.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../_common.sh"
source "$SCRIPT_DIR/../_verify.sh"

ITERUN_MAX_VERIFY_ITERATIONS="${ITERUN_MAX_VERIFY_ITERATIONS:-5}"
_example_setup "$SCRIPT_DIR"
_example_copy_expectations

_example_generate execute
_example_show_verify_rounds

if [ ! -f "$GENERATED/session.json" ] || ! "$PYTHON" -c "import json,sys; s=json.load(open(sys.argv[1])); sys.exit(0 if s.get('success') else 1)" "$GENERATED/session.json"; then
    echo "FAIL: pipeline nie naprawił usługi — zobacz generated/verify.rounds.json" >&2
    exit 1
fi

_example_e2e_verify
echo "OK resilience-vague (rounds: $(python3 -c "import json; print(len(json.load(open('$GENERATED/verify.rounds.json'))))" 2>/dev/null || echo '?'))"
