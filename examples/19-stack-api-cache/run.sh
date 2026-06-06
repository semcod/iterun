#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../_common.sh"
_example_setup "$SCRIPT_DIR"
_example_use_source_pkg

$CLI plan "$ITERUN_PKG" --output-dir "$GENERATED" --quiet

if [ "${ITERUN_EXECUTE:-1}" = "1" ] && command -v docker >/dev/null 2>&1; then
    $CLI execute "$ITERUN_PKG" --workspace "$GENERATED" --quiet
    _example_echo_stack_urls
    api_port="$(_example_compose_port api-service)"
    echo "OK api-cache-stack — http://localhost:${api_port:-?}/ping"
else
    echo "OK api-cache-stack planned in $GENERATED"
fi
