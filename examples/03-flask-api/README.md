# 03 — Flask API

Generowanie kodu Flask z DSL — 3 endpointy REST.

## Uruchomienie

```bash
./run.sh
```

## Komendy

```bash
python -m cli plan examples/03-flask-api/intent.yaml --output-dir examples/03-flask-api/generated
```

## `generated/`

`plan.result.json`, `app.py` (Flask + `@app.route`), `Dockerfile`
