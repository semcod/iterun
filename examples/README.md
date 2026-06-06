# Przykłady ITERUN

Każdy przykład to **3 pliki** + katalog `generated/` (tworzony przy uruchomieniu):

```
examples/01-user-api/
├── intent.yaml    # ŹRÓDŁO — ręcznie pisany DSL (fixture, w repo)
├── README.md      # opis + komendy
├── run.sh         # uruchomienie
└── generated/     # WYNIK — generowany przez CLI (gitignored)
```

## Źródło vs `generated/`

| Plik | Generowany? | Kiedy / jak |
|------|-------------|-------------|
| `intent.yaml` | **Nie** | Pisany ręcznie, commitowany do repo — to wejście DSL |
| `generated/plan.result.json` | **Tak** | `plan` — parser + symulator (bez LLM) |
| `generated/app.py` / `app.js` | **Tak** | `plan` — szablony w `planner/simulator.py` |
| `generated/Dockerfile` | **Tak** | `plan` — szablony w `planner/simulator.py` |
| `generated/ir.json` | **Tak** | `parse` — serializacja IntentIR |

**`./examples/run-all.sh` nie używa LLM ani promptów.** To deterministyczny pipeline:
`intent.yaml` → parse → plan → zapis do `generated/`.

Prompty LLM (Ollama) są tylko w interaktywnej powłoce: `suggest`, `apply`, `chat`
— nie w przykładach `run.sh`.

## Szybki start

```bash
cd /path/to/iterun
pip install -r requirements.txt
./examples/run-all.sh
```

Pojedynczy przykład:

```bash
cd examples/01-user-api
./run.sh
```

## Przykłady

| Katalog | Opis | Główna komenda |
|---------|------|----------------|
| [01-user-api](01-user-api/) | FastAPI CRUD | `plan` |
| [02-ping-smoke](02-ping-smoke/) | Minimalny smoke | `plan` |
| [03-flask-api](03-flask-api/) | Flask | `plan` |
| [04-express-api](04-express-api/) | Node/Express | `plan` |
| [05-ir-show](05-ir-show/) | IntentIR + plan | `parse` + `plan` |
| [06-iterate-workflow](06-iterate-workflow/) | Iteracja (shell) | `plan` / interaktywny `shell` |
| [07-execution-smoke](07-execution-smoke/) | Smoke plan/execute | `plan` (+ `execute`) |
| [08-llm-generate](08-llm-generate/) | **LLM** → YAML → plan | `generate` (LiteLLM) |

## `generated/`

CLI zapisuje artefakty przez `--output-dir`:

```bash
python -m cli plan examples/01-user-api/intent.yaml \
  --output-dir examples/01-user-api/generated
```

| Plik | Opis |
|------|------|
| `plan.result.json` | IR + wynik dry-run |
| `app.py` / `app.js` | Wygenerowany kod |
| `Dockerfile` | Obraz Docker |
| `ir.json` | IntentIR (przy `parse --output-dir`) |
| `execution.json` | Wynik execute (przy `execute --json`) |

## Zmienne

| Zmienna | Opis |
|---------|------|
| `ITERUN_EXECUTE=1` | Włącz Docker execute w 01 i 07 |
| `ITERUN_SKIP_CLEAN=1` | Nie czyść `generated/` przed runem |
