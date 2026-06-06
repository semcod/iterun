# 09 — E2E Ping Verify (testql + intract)

Flow: **prompt → iterun.yaml → intract.yaml (kontrakt) → service → walidacja**.

## Uruchomienie

```bash
./run.sh
```

## Co ląduje w `generated/`

| Plik | Skąd |
|------|------|
| `iterun.yaml` | LLM z `prompt.txt` |
| `intract.yaml` | **auto** — `generator/intract_manifest.py` |
| `service.testql.toon.yaml` | auto — `generator/testql_scenario.py` |
| `verify.result.json` | auto — `iterun generate --verify` |
| `openapi.yaml` | auto — `intent_to_openapi.py` (przed intract) |
| `app.py`, `Dockerfile` | plan + execute |
| `stack.markpact.md` | markpact pack |
| `iterun.registry.json` | rejestr artefaktów |

## Komendy ręczne

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --execute --verify --quiet
testql run generated/service.testql.toon.yaml --url "$(jq -r .service_url generated/verify.result.json)"
python ../_scripts/intent_to_intract.py generated/iterun.yaml -o generated/intract.yaml -p prompt.txt
python -m intract validate generated/ --manifest generated/intract.yaml
testql run tests/service.testql.toon.yaml --url http://localhost:<port>
```

## Wymagania

`pip install -e ".[ai]"`, `testql`, `intract` (semcod/intract), Docker.
## Operacje (logi, status, parametry)

Pełna ściągawka: [OPERATIONS.md](../OPERATIONS.md)

### Parametry tego przykładu

| Element | Wartość |
|---------|---------|
| Intent (`INTENT.name`) | `ping-smoke` |
| Domyślny flow | `./run.sh` |

| Zmienna | Efekt |
|---------|--------|
| `ITERUN_VERIFY=0` | Bez TestQL w pipeline |

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
iterun generate "$(cat prompt.txt)" -o generated/ --execute --verify

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
curl -s "$URL/ping"; testql run generated/service.testql.toon.yaml --url "$URL"

# Docker
docker ps --filter name=intent-ping-smoke --format 'table {{.Names}}	{{.Status}}	{{.Ports}}'

# logi kontenera
docker logs -f $(docker ps -q --filter name=ping-smoke | head -1) 2>/dev/null || \
  cat generated/container.log
```

