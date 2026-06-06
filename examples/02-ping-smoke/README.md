# 02 — Ping Smoke

Minimalny intent: `/ping` + `/health`. Szybki smoke test parsera i planera.

## Uruchomienie

```bash
./run.sh
```

## Komendy

```bash
python -m cli plan examples/02-ping-smoke/intent.yaml --output-dir examples/02-ping-smoke/generated
```

## `generated/`

`plan.result.json`, `app.py`, `Dockerfile`
