# 05 — IR Show

Parsowanie DSL do IntentIR (wszystkie typy akcji) + dry-run.

## Uruchomienie

```bash
./run.sh
```

## Komendy

```bash
# samo IR (IntentIR JSON)
python -m cli parse examples/05-ir-show/intent.yaml --output-dir examples/05-ir-show/generated

# plan + kod
python -m cli plan examples/05-ir-show/intent.yaml --output-dir examples/05-ir-show/generated
```

## `generated/`

| Plik | Opis |
|------|------|
| `ir.json` | IntentIR (z `--output-dir` przy parse) |
| `plan.result.json` | Wynik dry-run |
| `app.py`, `Dockerfile` | Wygenerowany kod |
