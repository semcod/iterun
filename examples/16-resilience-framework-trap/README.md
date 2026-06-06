# 16 — Resilience: conflicting framework signals

Prompt z pułapkami: Flask vs FastAPI, Node vs Python, `/live` zamiast `/health`.

`expectations.yaml` wymusza **fastapi** + 7 konkretnych tras — typowy fail rundy 1: zły framework lub brakujące ścieżki.

## Metryki

```bash
jq '.verify_iterations, .success' generated/session.json
jq '[.[] | {round, success, errors: .errors[0]}]' generated/verify.rounds.json
```

## Operacje (logi, status, parametry)

Pełna ściągawka: [OPERATIONS.md](../OPERATIONS.md)

### Parametry tego przykładu

| Element | Wartość |
|---------|---------|
| Intent (`INTENT.name`) | `items-api` |
| Domyślny flow | `./run.sh` |

| Zmienna | Efekt |
|---------|--------|
| `ITERUN_MAX_VERIFY_ITERATIONS=5` | Pułapka Flask/FastAPI |

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
ITERUN_MAX_VERIFY_ITERATIONS=5 ./run.sh

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
curl -s "$URL/live"; curl -s "$URL/api/v1/items"

# Docker
docker ps --filter name=intent-items-api

# logi kontenera
docker logs -f $(docker ps -q --filter name=items-api | head -1) 2>/dev/null || \
  cat generated/container.log
```

