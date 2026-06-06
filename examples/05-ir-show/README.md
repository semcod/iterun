# 05 — IR Show

Prompt → IntentIR (różne typy akcji) + dry-run.

## Uruchomienie

```bash
./run.sh
```

## Komendy

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --run --quiet
iterun parse generated/iterun.yaml --output-dir generated/ --quiet
```

## `generated/`

| Plik | Opis |
|------|------|
| `iterun.yaml` | LLM |
| `ir.json` | IntentIR (parse) |
| `plan.result.json` | Wynik dry-run |
| `app.py`, `Dockerfile` | Wygenerowany kod |

## Operacje (logi, status, parametry)

Pełna ściągawka: [OPERATIONS.md](../OPERATIONS.md)

### Parametry tego przykładu

| Element | Wartość |
|---------|---------|
| Intent (`INTENT.name`) | `ir-show` |
| Domyślny flow | `./run.sh` |

| Zmienna | Efekt |
|---------|--------|
| — | Tylko plan + `iterun parse` → `ir.json` |

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
iterun parse generated/iterun.yaml -o generated/

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
jq . generated/ir.json

# Docker
# brak kontenera (dry-run)

# logi kontenera
docker logs -f $(docker ps -q --filter name=ir-show | head -1) 2>/dev/null || \
  cat generated/container.log
```

