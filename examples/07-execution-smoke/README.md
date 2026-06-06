# 07 — Execution Smoke

Generate+plan własnego intentu + 02/03/04. Opcjonalne wykonanie Docker.

## Uruchomienie

```bash
# tylko plan (domyślnie)
./run.sh

# z execute
ITERUN_EXECUTE=1 ./run.sh
```

## Komendy

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --execute --quiet
```

## `generated/`

`iterun.yaml`, `plan.result.json`, `app.py`, `Dockerfile`
## Operacje (logi, status, parametry)

Pełna ściągawka: [OPERATIONS.md](../OPERATIONS.md)

### Parametry tego przykładu

| Element | Wartość |
|---------|---------|
| Intent (`INTENT.name`) | `exec-smoke` |
| Domyślny flow | `./run.sh` |

| Zmienna | Efekt |
|---------|--------|
| `ITERUN_EXECUTE=1` | **Wymagane** dla transactional smoke |

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
iterun generate "$(cat prompt.txt)" -o generated/ --execute

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
curl -s "$URL/ping"; curl -s "$URL/health"

# Docker
docker ps --filter name=intent-exec-smoke

# logi kontenera
docker logs -f $(docker ps -q --filter name=exec-smoke | head -1) 2>/dev/null || \
  cat generated/container.log
```

