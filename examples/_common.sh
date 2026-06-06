# Wspólne zmienne dla examples/*/run.sh (source, nie uruchamiaj bezpośrednio).
_example_setup() {
    local script_dir="$1"
    EXAMPLE_DIR="$(cd "$script_dir" && pwd)"
    REPO_ROOT="$(cd "$EXAMPLE_DIR/../.." && pwd)"
    EXAMPLES_ROOT="$(cd "$EXAMPLE_DIR/.." && pwd)"
    INTENT="$EXAMPLE_DIR/intent.yaml"
    GENERATED="$EXAMPLE_DIR/generated"
    PYTHON="${PYTHON:-python3}"
    CLI="$PYTHON -m cli"

    cd "$REPO_ROOT"
    mkdir -p "$GENERATED"

    if [ "${ITERUN_SKIP_CLEAN:-}" != "1" ]; then
        rm -rf "$GENERATED"/*
    fi
}
