# 08 — LLM Generate (SDK / MCP)

Ten sam flow co pozostałe przykłady (`prompt.txt` → `generate`). Dodatkowo: SDK i MCP.

## Uruchomienie

```bash
./run.sh
```

## Komendy

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --run --quiet
iterun generate "$(cat prompt.txt)" -o generated/ --execute --quiet
iterun schema
iterun validate generated/iterun.yaml
```

## SDK

```python
from sdk import IterunClient

client = IterunClient()
result = client.generate_and_run(
    open("prompt.txt").read(),
    output_dir="generated",
    execute=False,
)
print(result.yaml_path)
```

## MCP

```bash
pip install -e ".[mcp]"
iterun-mcp
# lub: python -m iterun_mcp.server
```

Narzędzia MCP: `iterun_interfaces`, `iterun_schema`, `iterun_validate_intent`, `iterun_parse_yaml`, `iterun_plan_yaml`, `iterun_generate_intent`, `iterun_run_pipeline` (z `verify`).

## REST API

```bash
uvicorn web.app:app --port 8000
curl http://localhost:8000/api/interfaces
curl -X POST http://localhost:8000/api/pipeline/run \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"'"$(cat prompt.txt)"'","output_dir":"generated","execute":false}'
```

Szczegóły: [docs/API.md](../../docs/API.md)

## Wymagania

`pip install -e ".[ai]"` + `.env` z `OPENROUTER_API_KEY` lub lokalny Ollama.
## Operacje (logi, status, parametry)

Pełna ściągawka: [OPERATIONS.md](../OPERATIONS.md)

### Parametry tego przykładu

| Element | Wartość |
|---------|---------|
| Intent (`INTENT.name`) | `(z LLM)` |
| Domyślny flow | `./run.sh` |

| Zmienna | Efekt |
|---------|--------|
| `ITERUN_EXECUTE=1` | Execute po generate |

Wspólne: `ITERUN_PROMPT`, `ITERUN_SKIP_CLEAN=1`, `ITERUN_SKIP_INTRACT=1` (E2E) — patrz OPERATIONS.md.

### Nowe opcje (runtime, markpact, registry, API)

| Opcja | Opis |
|-------|------|
| `--runtime docker` | Domyślnie — Docker przy `--execute` |
| `--runtime pactown` | Pactown sandbox zamiast docker ([RUNTIME.md](../../docs/RUNTIME.md)) |
| `--verify` | **Pętla naprawy LLM** (testql + intract); bez flagi brak regeneracji YAML |
| `iterun registry -o generated/` | `iterun.registry.json` — monitoring artefaktów |

Po `--run`: `stack.markpact.md`, `pactown.yaml`. REST/SDK/MCP: [API.md](../../docs/API.md), rejestr: [REGISTRY.md](../../docs/REGISTRY.md).

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute --verify
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute --runtime pactown --verify
iterun registry -o generated/ -q
```


### Logi w trakcie uruchomienia

```bash
# bez --quiet: pełny output plan/execute na terminalu
cd ~/github/wronai/iterun
iterun generate "$(cat prompt.txt)" -o generated/ --run --json | jq .success

# JSON całej sesji (generate)
iterun generate "$(cat prompt.txt)" -o generated/ --execute --verify --json | jq .

# podgląd logów planera / execute z plików (w trakcie kolejnego kroku)
tail -f generated/plan.result.json   # po --run
```

### Status po uruchomieniu

```bash
# sukces sesji
jq '{success, verify_iterations, error}' generated/session.json

# URL usługi (port dynamiczny!)
URL=$(jq -r '.verification.service_url // .execution.endpoints[0]' generated/session.json)

# HTTP
curl -s "$URL/ping"

# Docker
docker ps --filter name=intent-

# logi kontenera
docker logs -f $(docker ps -q --filter name=(z LLM) | head -1) 2>/dev/null || \
  cat generated/container.log
```

