# 06 — Iterate Workflow

Generate + plan początkowy. Pełny cykl iterate → ITERUN → execute w interaktywnej powłoce.

## Uruchomienie (generate + plan)

```bash
./run.sh
```

## Interaktywna iteracja

```bash
python -m cli
```

```
intent> load examples/06-iterate-workflow/generated/iterun.yaml
intent> plan
intent> iterate
> action=api.expose GET /health
> action=api.expose POST /data
> done
intent> plan
intent> iterun
intent> execute
```

## Jedna komenda (generate → execute)

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
| Intent (`INTENT.name`) | `iterate-demo` |
| Domyślny flow | `./run.sh` |

| Zmienna | Efekt |
|---------|--------|
| — | Pełna iteracja: `iterun` shell interaktywny |

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
iterun  # shell → load generated/iterun.yaml → suggest → iterate

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
curl -s "$URL/ping"  # po execute

# Docker
docker ps --filter name=intent-iterate-demo

# logi kontenera
docker logs -f $(docker ps -q --filter name=iterate-demo | head -1) 2>/dev/null || \
  cat generated/container.log
```

