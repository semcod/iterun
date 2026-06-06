# 10 — E2E User CRUD Verify

Pełny CRUD z promptu — weryfikacja 7 endpointów przez testql + intract + `expectations.yaml`.

## Uruchomienie

```bash
./run.sh
```

## Oneliner (bez run.sh)

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --execute --json | jq '.execution.endpoints[0]'
testql run tests/service.testql.toon.yaml --url "$(docker ps --filter name=intent-user-api --format '{{.Ports}}' | grep -oE '[0-9]+' | head -1 | xargs -I{} echo http://localhost:{})"
```

## Co sprawdzamy

1. **iterun.yaml** — czy LLM dodał wszystkie akcje z promptu
2. **testql** — czy kontener odpowiada HTTP 200
3. **intract** — `generated/intract.yaml` (auto z intent) vs kod + openapi
4. **expectations** — pola JSON (`status`, `endpoint`, `method`)
## Operacje (logi, status, parametry)

Pełna ściągawka: [OPERATIONS.md](../OPERATIONS.md)

### Parametry tego przykładu

| Element | Wartość |
|---------|---------|
| Intent (`INTENT.name`) | `user-api` |
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
iterun generate "$(cat prompt.txt)" -o generated/ --execute --verify --json

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
curl -s "$URL/users"; python ../_scripts/verify_expectations.py expectations.yaml generated/iterun.yaml --url "$URL"

# Docker
docker ps --filter name=intent-user-api --format 'table {{.Names}}	{{.Status}}	{{.Ports}}'

# logi kontenera
docker logs -f $(docker ps -q --filter name=user-api | head -1) 2>/dev/null || \
  cat generated/container.log
```

