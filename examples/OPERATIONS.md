# Operacje — logi, status, parametry (wszystkie przykłady)

> Z katalogu przykładu: `cd ~/github/wronai/iterun/examples/NN-nazwa`  
> Wymaga: `source ../../venv/bin/activate` (lub `source ~/github/wronai/iterun/venv/bin/activate`)

### CWD — częsty błąd

| Jesteś w | `cat prompt.txt` | `cat examples/17-…/prompt.txt` |
|----------|------------------|----------------------------------|
| `examples/17-stack-shop-gateway/` | ✅ | ❌ No such file |
| `~/github/wronai/iterun/` (root) | ❌ | ✅ |

`Usage: iterun generate "..."` z pustym promptem → zwykle **zła ścieżka do `prompt.txt`**.

## Zmienne środowiskowe (`run.sh`)

| Zmienna | Domyślnie | Opis |
|---------|-----------|------|
| `ITERUN_PROMPT` | `prompt.txt` | Nadpisz prompt bez edycji pliku |
| `ITERUN_EXECUTE` | `0` (01–08), `1` (E2E/STACK) | `1` → Docker / compose po planie |
| `ITERUN_VERIFY` | `1` w E2E | `0` → bez TestQL `--verify` |
| `ITERUN_MAX_VERIFY_ITERATIONS` | `3` (resilience: `5`) | Rundy naprawcze przy fail verify |
| `ITERUN_SKIP_CLEAN` | `0` | `1` → nie czyść `generated/` przed runem |
| `ITERUN_SKIP_INTRACT` | `0` | `1` → pomiń `intract validate` w E2E |
| `ITERUN_RUNTIME` | `docker` | `pactown` → uruchomienie przez pactown (bez docker w iterun) |
| `LLM_MODEL` | z `.env` | Model dla `generate` |
| `OPENROUTER_API_KEY` | `.env` | Klucz LLM |

```bash
ITERUN_PROMPT="Minimal ping API" ./run.sh
ITERUN_EXECUTE=1 ITERUN_SKIP_CLEAN=1 ./run.sh
ITERUN_MAX_VERIFY_ITERATIONS=5 ./run.sh
```

## Flagi CLI (`iterun` / `python -m cli`)

| Flaga | Opis |
|-------|------|
| `--quiet` / `-q` | Minimum na stdout (skrypty) |
| `--json` | Pełna sesja na stdout (bez `--quiet`) |
| `-o generated/` | Katalog artefaktów |
| `--run` | Plan po `generate` |
| `--execute` | Docker po planie |
| `--verify` | TestQL + HTTP; retry przy błędzie |
| `--max-iterations N` | Retry walidacji YAML przez LLM (dom. 5) |
| `--max-verify-iterations N` | Retry deploy+verify (dom. 3) |
| `--runtime docker\|pactown` | Runtime wykonania (dom. `docker`; `pactown` = markpact sandboxes) |
| `-m MODEL` | Model LiteLLM |
| `--workspace DIR` | Workspace przy `execute` |
| `iterun registry -o DIR` | Odśwież `iterun.registry.json` (rejestr usług/artefaktów) |
| `iterun registry list` | Lista workspace’ów z rejestrem |

### Verbose — logi **w trakcie** (bez `--quiet`)

```bash
cd ~/github/wronai/iterun
iterun generate "$(cat examples/01-user-api/prompt.txt)" \
  -o examples/01-user-api/generated/ --run --execute --verify

iterun plan examples/01-user-api/generated/iterun.yaml \
  -o examples/01-user-api/generated/

iterun execute examples/01-user-api/generated/iterun.yaml \
  --workspace examples/01-user-api/generated/
```

### JSON na stdout (jedna sesja)

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --execute --verify --json | jq .
# równolegle zapis: generated/session.json
```

## Pliki po uruchomieniu (`generated/`)

| Plik | Co sprawdzić |
|------|----------------|
| `session.json` | `success`, `verify_iterations`, `error` |
| `execution.json` | `logs[]`, `endpoints[]`, `container_id` |
| `container.log` | tail stdout/stderr kontenera |
| `verify.result.json` | `service_url`, `testql_passed`, `probes` |
| `verify.rounds.json` | historia rund naprawczych |
| `plan.result.json` | `plan.logs[]` — dry-run |
| `stack.markpact.md` | Cały workspace w jednym pliku markpact (po `--run`) |
| `pactown.yaml` | Konfiguracja ekosystemu pactown (STACK / single) |
| `pactown.urls.json` | URL usług po `--runtime pactown` |
| `stack.urls.json` | URL gatewayów po compose (STACK, docker) |
| `iterun.registry.json` | Rejestr usług + artefaktów (Backstage/OTel export) |
| `catalog/` | Eksport Backstage Component (po `iterun registry`) |

### Pętla naprawy LLM

**`--verify`** jest wymagane, aby iterun **regenerował YAML** po błędach (testql + intract, do `--max-verify-iterations` rund).

`--execute` bez `--verify` = tylko deploy + HTTP smoke; **bez** iteracji LLM.

```bash
# naprawa automatyczna
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute --verify

# pactown zamiast docker
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute --runtime pactown --verify
```

Wymaga runtime: `pip install -e ../markpact ../pactown` lub `pip install -e ".[runtime]"`. Zobacz [RUNTIME.md](../docs/RUNTIME.md).

```bash
jq '{success, error, verify_iterations}' generated/session.json
jq '.execution.logs[]' generated/session.json
jq -r '.execution.endpoints[0]' generated/session.json
jq '.verification' generated/session.json
jq '.plan.logs[]' generated/plan.result.json
```

## Status usługi **po** uruchomieniu

### URL i port

```bash
# z ostatniego execute/verify
URL=$(jq -r '.verification.service_url // .execution.endpoints[0]' generated/session.json)
echo "$URL"

# lub z verify
jq -r .service_url generated/verify.result.json
```

### HTTP (health)

```bash
curl -s "$URL/ping" | jq .
curl -s "$URL/health" | jq .
curl -s -o /dev/null -w "%{http_code}\n" "$URL/ping"
```

### Docker — kontener pojedynczy

```bash
# nazwa intentu z iterun.yaml
NAME=$(python3 -c "import yaml; d=yaml.safe_load(open('generated/iterun.yaml')); print(d['INTENT']['name'])")

docker ps --filter "name=intent-${NAME}" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker logs -f "$(docker ps -q --filter name=intent-${NAME} | head -1)"
```

### Docker — STACK (compose)

Host port z `iterun.yaml` (np. `18080`) może być **przesunięty** gdy zajęty → sprawdź w `docker compose ps` (np. `18081`).

```bash
# po ./run.sh
cat generated/stack.urls.json

PORT=$(docker compose -f generated/docker-compose.yaml -p intent-shop-stack port api-gateway 8000 | cut -d: -f2)
curl -s "http://localhost:${PORT}/ping"

docker compose -f generated/docker-compose.yaml -p intent-shop-stack ps
docker compose -f generated/docker-compose.yaml -p intent-shop-stack logs -f api-gateway
```

### TestQL ręcznie

```bash
testql run generated/service.testql.toon.yaml --url "$URL" --output console
```

### Intract (E2E)

```bash
python -m intract validate generated/ --manifest generated/intract.yaml
```

### Rejestr i markpact

```bash
iterun registry -o generated/ -q
jq '.spec.services[] | {name, urls}' generated/iterun.registry.json
jq '.spec.artifacts | length' generated/iterun.registry.json

# jeden plik całego stacka (markpact)
ls -la generated/stack.markpact.md
```

### REST / SDK / MCP

```bash
cd ~/github/wronai/iterun
uvicorn web.app:app --port 8800
curl http://localhost:8800/api/registry?workspace=examples/01-user-api/generated

pip install -e ".[mcp]"
iterun-mcp
```

Dokumentacja: [API.md](../docs/API.md), [REGISTRY.md](../docs/REGISTRY.md).

## Interaktywna powłoka

```bash
cd ~/github/wronai/iterun && iterun
# intent> load generated/iterun.yaml
# intent> plan
# intent> show json
# intent> execute
```

## Web UI

```bash
python -m web.app   # http://localhost:8080
```

## Czyszczenie

```bash
docker ps -a --filter name=intent- -q | xargs -r docker rm -f
docker compose -f generated/docker-compose.yaml -p intent-NAZWA down
rm -rf generated/*
```
