# 07 — Execution Smoke

Plan własnego intentu + plan 02/03/04. Opcjonalne wykonanie Docker.

## Uruchomienie

```bash
# tylko plan (domyślnie)
./run.sh

# z execute
ITERUN_EXECUTE=1 ./run.sh
```

## Komendy

```bash
# plan smoke
./run.sh

# execute jednego intentu
python -m cli execute examples/07-execution-smoke/intent.yaml \
  --workspace examples/07-execution-smoke/generated
```

## `generated/`

`plan.result.json`, `app.py`, `Dockerfile` (+ artefakty execute w `generated/`)
