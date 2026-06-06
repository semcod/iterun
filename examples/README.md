# Przykłady ITERUN

> **Repo:** `~/github/wronai/iterun` (nie `koru`).

```bash
cd ~/github/wronai/iterun
source venv/bin/activate      # nie: source ~/github/semcod/koru/.venv/bin/activate
pip install -e ".[ai]"        # komenda `iterun` + LiteLLM
pip install -e ".[runtime]"   # opcjonalnie: markpact + pactown
pip install -e ../markpact -e ../pactown   # z lokalnych repo wronai
```

`Command 'iterun' not found` → zły venv lub brak `pip install -e .`. Użyj: `python -m cli …` z katalogu repo.

Każdy przykład: **prompt.txt** + **run.sh** + katalog **`generated/`** (cała sesja, gitignored).

## Zależności E2E

```bash
# z katalogu iterun (auto-szuka ../../semcod/intract)
./examples/run-e2e.sh

# ręcznie
export INTRACT_PATH=~/github/semcod/intract
pip install -e "$INTRACT_PATH" testql

# bez intract (tylko pipeline --verify + testql)
ITERUN_SKIP_INTRACT=1 ./examples/run-resilience.sh
```

```
examples/01-user-api/
├── prompt.txt
├── run.sh
└── generated/              # ← wszystko od promptu do testów
    ├── iterun.yaml         # paczka DSL (dawne intent.yaml)
    ├── session.json        # pełny zapis sesji
    ├── plan.result.json
    ├── execution.json
    ├── verify.result.json
    ├── container.log
    └── app.py, Dockerfile, …
```

## Paczka `iterun.yaml`

Główny plik DSL w workspace to **`iterun.yaml`** (nie `intent.yaml`). Stała: `config.PACKAGE_FILENAME`.

```bash
iterun plan examples/01-user-api/generated/iterun.yaml -o generated/
iterun execute examples/01-user-api/generated/iterun.yaml --workspace generated/
```

## Gdzie są dane i logi? (`generated/`)

Wszystko z jednego uruchomienia trafia do **`--output-dir`** (domyślnie `generated/`):

| Plik | Zawartość |
|------|-----------|
| **`prompt.txt`** | Kopia promptu użytego w sesji |
| **`iterun.yaml`** | Paczka DSL z LLM (INTENT + IMPLEMENTATION + …) |
| **`session.json`** | **Główny log sesji** — prompt, generate attempts, plan, execute, verify, błędy |
| **`plan.result.json`** | IR + logi dry-run planera (`plan.logs` wewnątrz JSON) |
| **`execution.json`** | Wynik execute: `logs`, `endpoints`, `container_id`, walidacja HTTP |
| **`container.log`** | Ostatnie ~200 linii `docker logs` kontenera usługi |
| **`verify.result.json`** | TestQL + sondy HTTP (`--verify`) |
| **`verify.rounds.json`** | Historia każdej rundy naprawczej (błędy, faza) |
| **`expectations.yaml`** | Kontrakt promptu (kopiowany z example, opcjonalnie) |
| **`intract.yaml`** | Kontrakt Intract (`require: implement.*`) |
| **`service.testql.toon.yaml`** | Scenariusz TestQL wygenerowany z endpointów |
| **`openapi.yaml`** | OpenAPI + `x-intract` (E2E, przed `intract validate`) |
| **`app.py` / `app.js`** | Wygenerowany kod usługi |
| **`Dockerfile`** | Obraz Docker |
| **`stack.markpact.md`** | Cały workspace w jednym pliku markpact |
| **`pactown.yaml`** | Konfiguracja uruchomienia pactown |
| **`iterun.registry.json`** | Rejestr usług i artefaktów |

### Co jest w `session.json`?

```json
{
  "timestamp": "...",
  "success": true,
  "prompt": "...",
  "generate": { "attempts": [...], "iterations": 1 },
  "plan": { "logs": ["[12:00:01] Dry-run started", "..."] },
  "execution": { "logs": [...], "endpoints": ["http://localhost:8003"] },
  "verification": { "testql_passed": true, "service_url": "..." },
  "verify_iterations": 1,
  "yaml_path": ".../iterun.yaml"
}
```

### Logi runtime usługi (działający kontener)

| Źródło | Gdzie |
|--------|--------|
| Build/run pipeline | `execution.json` → pole `logs` |
| Docker stdout/stderr | `generated/container.log` |
| Na żywo | `docker logs intent-<nazwa>-<id>` |
| API (web) | `GET /api/containers/{id}/logs` |

### Poza `generated/`

| Co | Gdzie |
|----|--------|
| Konfiguracja LLM | `.env` w root repo (`OPENROUTER_API_KEY`, `LLM_MODEL`) |
| Stary fixture prompt | `examples/*/prompt.txt` (repo) |
| Expectations (E2E) | `examples/*/expectations.yaml` (repo, opcjonalnie) |

## Pipeline

```text
prompt.txt
  → iterun generate --execute --verify -o generated/
  → iterun.yaml + intract.yaml + service.testql.toon.yaml
  → plan + Docker
  → verify (testql)
  → session.json + execution.json + container.log
```

## Resilience (skrajne prompty → naprawa usługi)

| Katalog | Pułapka |
|---------|---------|
| [13-resilience-vague](13-resilience-vague/) | Mglisty prompt vs pełne expectations |
| [14-resilience-inventory](14-resilience-inventory/) | Wiele encji / endpointów |
| [15-resilience-nested-paths](15-resilience-nested-paths/) | Zagnieżdżone `{id}` w ścieżkach |
| [16-resilience-framework-trap](16-resilience-framework-trap/) | Flask vs FastAPI w promptcie |

```bash
./examples/run-resilience.sh
jq . generated/verify.rounds.json    # historia rund naprawczych
```

`expectations.yaml` jest **surowszy niż prompt** — wymusza `--verify` retry (domyślnie 5 rund).

## STACK — wiele Dockerfile w jednej aplikacji

Sekcja **`STACK.services`** w `iterun.yaml` → N serwisów + `docker-compose.yaml`:

```bash
./examples/run-stacks.sh
```

| # | Katalog | Serwisy |
|---|---------|---------|
| 17 | `17-stack-shop-gateway` | gateway + users + catalog |
| 18 | `18-stack-blog` | API + worker + frontend |
| 19 | `19-stack-api-cache` | FastAPI + redis (image) |

Spec: [docs/INTENT_DSL_SPEC.md](../docs/INTENT_DSL_SPEC.md#stack-multi-service)

## Katalog przykładów

| # | Katalog | Opis |
|---|---------|------|
| 01 | `01-user-api` | FastAPI CRUD z promptu |
| 02 | `02-ping-smoke` | `/ping` + `/health` |
| 03 | `03-flask-api` | Flask zamiast FastAPI |
| 04 | `04-express-api` | Node/Express |
| 05 | `05-ir-show` | `iterun parse` → IR JSON |
| 06 | `06-iterate-workflow` | Shell: suggest → iterate |
| 07 | `07-execution-smoke` | Execute w Docker |
| 08 | `08-llm-generate` | SDK + MCP |
| 09 | `09-e2e-ping-verify` | TestQL + Intract (ping) |
| 10 | `10-e2e-user-crud-verify` | CRUD + expectations |
| 11 | `11-e2e-express-verify` | Express E2E |
| 12 | `12-e2e-full-gate` | Pełny gate (graph/scan) |
| 13 | `13-resilience-vague` | Mglisty prompt |
| 14 | `14-resilience-inventory` | Wiele encji |
| 15 | `15-resilience-nested-paths` | Zagnieżdżone `{id}` |
| 16 | `16-resilience-framework-trap` | Flask vs FastAPI |

## Szybki start

```bash
pip install -e ".[ai]"
./examples/run-all.sh
cd examples/01-user-api && ./run.sh
```

## Jedna komenda

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --execute --verify --json
# pełny log: generated/session.json
```

## Operacje — logi, status, parametry

**Ściągawka:** [OPERATIONS.md](OPERATIONS.md) (pełna lista flag CLI, `jq`, Docker, TestQL).

Każdy katalog `examples/NN-*/README.md` ma sekcje **Operacje** i **Nowe opcje** (`--runtime`, `--verify`, markpact, registry, API) z komendami pod dany przykład.

```bash
# verbose (bez --quiet)
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute --verify

# status po runie
jq '{success, error}' examples/01-user-api/generated/session.json
URL=$(jq -r '.execution.endpoints[0]' examples/01-user-api/generated/session.json)
curl -s "$URL/ping"

# logi na żywo
docker logs -f $(docker ps -q --filter name=intent-user-api | head -1)
```

## Zmienne (`run.sh`)

| Zmienna | Opis |
|---------|------|
| `ITERUN_PROMPT` | Nadpisz `prompt.txt` |
| `ITERUN_EXECUTE=1` | Docker execute (01, 07, 08) |
| `ITERUN_RUNTIME=pactown` | Uruchomienie przez pactown zamiast docker |
| `--runtime pactown` | To samo (flaga CLI) |
| `iterun registry -o generated/` | Rejestr po deploy |
| `ITERUN_VERIFY=1` | TestQL po execute (domyślnie w E2E) |
| `ITERUN_SKIP_CLEAN=1` | Nie czyść `generated/` przed runem |
| `ITERUN_MAX_VERIFY_ITERATIONS` | Rundy naprawcze (resilience, dom. 5) |
| `ITERUN_SKIP_INTRACT=1` | Pomiń intract w E2E |

Szczegóły: [OPERATIONS.md](OPERATIONS.md).
