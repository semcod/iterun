# Przykłady ITERUN

Każdy przykład: **prompt.txt** + **run.sh** + katalog **`generated/`** (cała sesja, gitignored).

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

## Zmienne

| Zmienna | Opis |
|---------|------|
| `ITERUN_PROMPT` | Nadpisz `prompt.txt` |
| `ITERUN_EXECUTE=1` | Docker execute (01, 07, 08) |
| `ITERUN_VERIFY=1` | TestQL po execute (domyślnie w E2E) |
| `ITERUN_SKIP_CLEAN=1` | Nie czyść `generated/` przed runem |
