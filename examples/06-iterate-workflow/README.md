# 06 — Iterate Workflow

Plan początkowy. Pełny cykl iterate → AMEN → execute w interaktywnej powłoce.

## Uruchomienie (plan)

```bash
./run.sh
```

## Interaktywna iteracja

```bash
python -m cli
```

```
intent> load examples/06-iterate-workflow/intent.yaml
intent> plan
intent> iterate
> action=api.expose GET /health
> action=api.expose POST /data
> done
intent> plan
intent> amen
intent> execute
```

## Jedna komenda (plan → execute, bez ręcznej iteracji)

```bash
python -m cli execute examples/06-iterate-workflow/intent.yaml \
  --workspace examples/06-iterate-workflow/generated
```

## `generated/`

`plan.result.json`, `app.py`, `Dockerfile`
