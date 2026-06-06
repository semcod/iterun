# 13 — Resilience: vague prompt

**Test:** mglisty prompt vs surowe `expectations.yaml` (pełny CRUD + health).

LLM często generuje za mało endpointów w rundzie 1 → `expectations` fail → retry z kontekstem błędów.

## Uruchomienie

```bash
ITERUN_MAX_VERIFY_ITERATIONS=5 ./run.sh
```

## Obserwacja iteracji

```bash
cat generated/verify.rounds.json   # każda runda: errors, testql, URL
cat generated/session.json         # final success + verify_iterations
```

Oczekiwane: `verify_iterations` ≥ 1, końcowy `success: true`.
## Operacje (logi, status, parametry)

Pełna ściągawka: [OPERATIONS.md](../OPERATIONS.md)

### Parametry tego przykładu

| Element | Wartość |
|---------|---------|
| Intent (`INTENT.name`) | `user-api` |
| Domyślny flow | `./run.sh` |

| Zmienna | Efekt |
|---------|--------|
| `ITERUN_MAX_VERIFY_ITERATIONS=5` | Więcej rund naprawczych |

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
jq .verify.rounds.json generated/; _example_show_verify_rounds w run.sh

# Docker
docker ps --filter name=intent-user-api --format 'table {{.Names}}	{{.Status}}	{{.Ports}}'

# logi kontenera
docker logs -f $(docker ps -q --filter name=user-api | head -1) 2>/dev/null || \
  cat generated/container.log
```

