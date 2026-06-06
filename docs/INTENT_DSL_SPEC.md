# ITERUN Intent DSL — Specification

## Overview

ITERUN opisuje **co** wdrożyć (API, akcje, runtime) w pliku paczki DSL. Domyślna nazwa pliku: **`iterun.yaml`** (`config.PACKAGE_FILENAME`). Wewnętrzna sekcja root nadal to `INTENT:`.

Dwa tryby wejścia:

| Tryb | Wejście | Wyjście |
|------|---------|---------|
| **Prompt-first** (zalecany) | NL prompt | `generated/iterun.yaml` + artefakty |
| **Ręczny DSL** | `iterun.yaml` | `plan` / `execute` |

## Interfejsy

Wszystkie powierzchnie korzystają z `interfaces/service.py` (`IterunService`). Pełna dokumentacja: [API.md](API.md).

| Interface | Entry |
|-----------|-------|
| CLI | `iterun generate`, `iterun registry`, `iterun schema` |
| REST | `GET /api/interfaces`, `POST /api/pipeline/run`, `GET /api/registry` |
| SDK | `IterunClient().run_pipeline()`, `.registry_refresh()` |
| MCP | `iterun-mcp` — `iterun_run_pipeline`, `iterun_registry_refresh`, … |
| Runtime | `ITERUN_RUNTIME=docker\|pactown` lub `--runtime` — [RUNTIME.md](RUNTIME.md) |
| Registry | `iterun registry -o generated/` — [REGISTRY.md](REGISTRY.md) |

### Generowanie

| Interface | Entry |
|-----------|-------|
| CLI | `iterun generate "prompt" -o generated/ [--run] [--execute] [--verify] [--runtime pactown]` |
| REST | `POST /api/pipeline/run` |
| SDK | `IterunClient().run_pipeline(prompt, execute=True, verify=True)` |
| MCP | `iterun_run_pipeline`, `iterun_generate_intent` |

## STACK (multi-service)

Jedna paczka `iterun.yaml` → wiele Dockerfile + `docker-compose.yaml`:

```yaml
INTENT:
  name: shop-stack
  goal: Multi-service application

STACK:
  network: shop-net
  services:
    api-gateway:
      language: python
      framework: fastapi
      port: 8000
      host_port: 18080          # publikacja na hoście (gateway)
      depends_on: [users-service]
      actions:
        - api.expose GET /ping
        - api.expose GET /users
    users-service:
      language: python
      framework: fastapi
      port: 8000                # tylko sieć Docker (brak host_port)
      actions:
        - api.expose GET /users
    redis-cache:
      image: redis:7-alpine     # bez własnego Dockerfile
      port: 6379

EXECUTION:
  mode: transactional
```

| Pole serwisu | Opis |
|--------------|------|
| `language` + `framework` | Generuje `services/<name>/Dockerfile` + kod |
| `image` | Gotowy obraz (Redis, Postgres, …) |
| `host_port` | Mapowanie na localhost (entrypoint) |
| `depends_on` | Kolejność startu w compose |
| `port` | Port wewnątrz kontenera (domyślnie 8000) |

Execute:

- **docker** (domyślnie): `docker compose up --build` (projekt `intent-<INTENT.name>`)
- **pactown**: `pactown.yaml` + Orchestrator — bez compose w iterun ([RUNTIME.md](RUNTIME.md))

Po planie: `stack.markpact.md` (markpact), `services/<name>/README.md` (per-service).

## Document structure (`iterun.yaml`)

```yaml
INTENT:          # required
  name: kebab-case-id
  goal: string
  description: optional

ENVIRONMENT:     # optional (defaults shown)
  runtime: docker | kubernetes | local
  base_image: python:3.12-slim
  ports: [8000]
  env_vars: {}

IMPLEMENTATION:  # required
  language: python | node
  framework: fastapi | flask | express
  actions:         # list of DSL strings
    - api.expose GET /ping

EXECUTION:       # optional
  mode: dry-run | transactional
```

## Action grammar

```
api.expose METHOD /path
db.create table
db.add_column table column type
shell.exec command
rest.call METHOD url
file.create path
```

## JSON Schema

```bash
iterun schema
# GET /api/schema
iterun validate generated/iterun.yaml
# POST /api/intents/validate-yaml
```

## Pipeline: prompt → usługa

```text
prompt (NL)
  → LLM + validate-retry (max 5)     → iterun.yaml
  → intract.yaml                     (kontrakt Intract)
  → service.testql.toon.yaml         (kontrakt TestQL)
  → plan                             → app.py, Dockerfile, compose (STACK)
  → markpact pack                    → stack.markpact.md, pactown.yaml
  → execute (docker | pactown)
  → verify (--verify)                → testql + HTTP + expectations.yaml
  → przy FAIL: ponowne generate z kontekstem błędów (max 3–5 rund)
  → registry                         → iterun.registry.json
  → session.json, execution.json, container.log, verify.rounds.json
```

**Bez `--verify`:** brak pętli naprawy LLM (tylko deploy + HTTP smoke w executorze).

### CLI

```bash
# tylko YAML + kontrakty
iterun generate "Create a REST API for user management" -o generated/ --quiet

# YAML + plan
iterun generate "..." -o generated/ --run

# YAML + plan + Docker
iterun generate "..." -o generated/ --execute

# pełny gate: deploy + testql + retry naprawczy LLM
iterun generate "..." -o generated/ --execute --verify
iterun generate "..." -o generated/ --execute --verify --max-verify-iterations 5

# pactown runtime (bez docker w iterun)
iterun generate "..." -o generated/ --execute --runtime pactown --verify

# rejestr po sesji
iterun registry -o generated/
```

### Artefakty w `--output-dir`

| Plik | Źródło |
|------|--------|
| `iterun.yaml` | LLM (`generator/intent_generator.py`) |
| `prompt.txt` | kopia promptu sesji |
| `intract.yaml` | `generator/intract_manifest.py` |
| `service.testql.toon.yaml` | `generator/testql_scenario.py` |
| `plan.result.json` | plan + logi dry-run |
| `execution.json` | execute + logi |
| `container.log` | `docker logs` (tail 200) |
| `verify.result.json` | TestQL + sondy HTTP |
| `verify.rounds.json` | historia rund `--verify` |
| `session.json` | **zbiorczy log całej sesji** |
| `expectations.yaml` | opcjonalny kontrakt (np. examples resilience) |
| `openapi.yaml` | OpenAPI + `x-intract` (E2E) |
| `stack.markpact.md` | markpact pack całego workspace |
| `pactown.yaml` | Konfiguracja ekosystemu pactown |
| `pactown.urls.json` | URL po `--runtime pactown` |
| `stack.urls.json` | URL gatewayów (STACK, docker) |
| `iterun.registry.json` | Rejestr usług i artefaktów |
| `docker-compose.yaml` | STACK multi-service |
| `services/*/` | Per-service artifacts (STACK) |

## LLM generation loop (YAML)

1. System prompt: JSON Schema + example + action rules
2. User prompt: natural language goal
3. LiteLLM completion → extract YAML
4. Validate: Pydantic + `parse_dsl()`
5. On failure: re-prompt with errors (max `--max-iterations`, default 5)

## Contract verify loop (`--verify`)

Po `execute`:

1. Czekaj na gotowość kontenera
2. `testql run generated/service.testql.toon.yaml --url <base>`
3. HTTP probe każdego `api.expose` z `iterun.yaml`
4. Jeśli `generated/expectations.yaml` — sprawdź brakujące endpointy / framework
5. Zapis `verify.result.json`; przy błędzie — nowa runda `generate` z listą failures w prompcie
6. Historia: `verify.rounds.json`

Integracje zewnętrzne (opcjonalnie w examples E2E):

- **[Intract](https://github.com/semcod/intract)** — `intract validate generated/ --manifest generated/intract.yaml`
- **[TestQL](https://github.com/oqlos/testql)** — scenariusz w `service.testql.toon.yaml`

## Environment (.env)

Priorytet modelu: `--model` CLI > `LLM_MODEL` > `DEFAULT_MODEL`

| Variable | Przykład | Opis |
|----------|----------|------|
| `OPENROUTER_API_KEY` | `sk-or-...` | OpenRouter (LiteLLM) |
| `LLM_MODEL` | `openrouter/deepseek/deepseek-v4-pro` | Model dla `generate` |
| `DEFAULT_MODEL` | `llama3.2` | Fallback Ollama (`suggest`, `chat`) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Lokalny Ollama |
| `SKIP_ITERUN_CONFIRMATION` | `true` | Bez interaktywnego `iterun` w CLI |
| `CONTAINER_PORT` | `8000` | Port w kontenerze |
| `ITERUN_RUNTIME` | `docker` | `pactown` — uruchomienie przez pactown |

```bash
pip install -e ".[ai]"
cp .env.example .env
iterun generate "Create a REST API for user management" -o generated/ --execute --verify
```

## Przykłady

| Zakres | Skrypt |
|--------|--------|
| Podstawowe (01–08) | `./examples/run-all.sh` |
| E2E testql + intract (09–12) | `./examples/run-e2e.sh` |
| Resilience / repair loop (13–16) | `./examples/run-resilience.sh` |
| STACK multi-service (17–19) | `./examples/run-stacks.sh` |

Szczegóły: [examples/README.md](../examples/README.md) · [OPERATIONS.md](../examples/OPERATIONS.md).

## SDK

```python
from sdk import IterunClient

client = IterunClient()
result = client.run_pipeline(
    "Create a REST API for user management",
    output_dir="generated",
    execute=True,
    verify=True,
)
print(result.yaml_path)
client.registry_refresh("generated")
```
