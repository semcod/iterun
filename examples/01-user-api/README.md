# 01 — User API (FastAPI CRUD)

Pełne REST API użytkowników — prompt → LLM → **iterun.yaml** → plan (+ opcjonalnie execute).

## Uruchomienie

```bash
./run.sh
```

## Komendy

```bash
# generate + plan
iterun generate "$(cat prompt.txt)" -o generated/ --run --quiet

# prompt → plan → Docker
ITERUN_EXECUTE=1 ./run.sh
# lub:
iterun generate "$(cat prompt.txt)" -o generated/ --execute --quiet
```

## `prompt.txt` — źródło

Prompt NL w repo. `generated/iterun.yaml` powstaje przy `generate`. Logi sesji: `generated/session.json`.

## `generated/`

| Plik | Skąd |
|------|------|
| `iterun.yaml` | LLM + validate-retry |
| `session.json` | pełny log sesji (prompt → verify) |
| `plan.result.json` | plan w pipeline |
| `app.py`, `Dockerfile` | plan w pipeline |
| `stack.markpact.md` | markpact pack (po `--run`) |
| `iterun.registry.json` | rejestr (`iterun registry -o generated/`) |

## Operacje (logi, status, parametry)

Pełna ściągawka: [OPERATIONS.md](../OPERATIONS.md)

### Parametry tego przykładu

| Element | Wartość |
|---------|---------|
| Intent (`INTENT.name`) | `user-api` |
| Domyślny flow | `./run.sh` |

| Zmienna | Efekt |
|---------|--------|
| `ITERUN_EXECUTE=1` | Deploy w Docker |
| `ITERUN_VERIFY=1` | TestQL po deploy |

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
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute --verify

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
curl -s "$URL/ping"; curl -s "$URL/users"

# Docker
docker ps --filter name=intent-user-api --format 'table {{.Names}}	{{.Status}}	{{.Ports}}'

# logi kontenera
docker logs -f $(docker ps -q --filter name=user-api | head -1) 2>/dev/null || \
  cat generated/container.log
```

