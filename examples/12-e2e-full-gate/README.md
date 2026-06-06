# 12 — E2E Full Gate (iterun + intract + testql)

```text
prompt.txt
  → iterun generate --execute
  → generated/iterun.yaml
  → generated/intract.yaml      # kontrakt (nie ręczny fixture!)
  → generated/openapi.yaml
  → Docker service
  → intract validate / graph / scan
  → testql run + testql auto
  → verify_expectations.py
```

## Uruchomienie

```bash
./run.sh
```

## `generated/intract.yaml`

Powstaje automatycznie z `iterun.yaml` — lista `require: implement.*` odzwierciedla `api.expose` z promptu. Nie trzymaj ręcznego `intract.yaml` w katalogu przykładu.

```bash
python ../_scripts/intent_to_intract.py generated/iterun.yaml \
  -o generated/intract.yaml -p prompt.txt
```

## Operacje (logi, status, parametry)

Pełna ściągawka: [OPERATIONS.md](../OPERATIONS.md)

### Parametry tego przykładu

| Element | Wartość |
|---------|---------|
| Intent (`INTENT.name`) | `product-api` |
| Domyślny flow | `./run.sh` |

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
./run.sh  # intract graph + testql auto

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
cat generated/intract.graph.mmd; jq . generated/intract.artifacts.json

# Docker
docker ps --filter name=intent-product-api

# logi kontenera
docker logs -f $(docker ps -q --filter name=product-api | head -1) 2>/dev/null || \
  cat generated/container.log
```

