# 01 — User API (FastAPI CRUD)

Pełne REST API użytkowników — 7 endpointów (ping, health, CRUD).

## `intent.yaml` — źródło (nie generowane)

Plik `intent.yaml` jest **fixture'em** — pisany ręcznie, trzymany w repo.
`run.sh` go tylko **czyta**, nigdy nie nadpisuje.

## Uruchomienie

```bash
./run.sh
```

## Komendy w `run.sh`

```bash
# 1. plan (domyślnie) — bez LLM, szablony kodu w planner/simulator.py
python -m cli plan intent.yaml --output-dir generated/ --quiet

# 2. opcjonalnie execute (ITERUN_EXECUTE=1, wymaga Docker)
python -m cli execute intent.yaml --workspace generated/ --quiet
```

Pełne ścieżki z roota repo:

```bash
python -m cli plan examples/01-user-api/intent.yaml --output-dir examples/01-user-api/generated
ITERUN_EXECUTE=1 ./run.sh
```

## Co trafia do `generated/` (generowane przy `plan`)

| Plik | Skąd |
|------|------|
| `plan.result.json` | IR + logi dry-run |
| `app.py` | `_generate_fastapi_code()` w `planner/simulator.py` |
| `Dockerfile` | `_generate_dockerfile()` w `planner/simulator.py` |

Przy `execute` — te same pliki + build/run kontenera Docker.

## Kiedy są prompty LLM?

**Nie w tym przykładzie.** LLM (Ollama) używany jest dopiero w powłoce:

```bash
python -m cli          # interaktywnie
intent> load intent.yaml
intent> suggest        # prompt do Ollama — analiza intentu
intent> apply          # auto-zastosowanie sugestii
intent> chat           # rozmowa o intencie
```

System prompt dla `suggest`: `ai_gateway/feedback_loop.py` → `SYSTEM_PROMPT`.
