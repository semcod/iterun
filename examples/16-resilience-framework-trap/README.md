# 16 — Resilience: conflicting framework signals

Prompt z pułapkami: Flask vs FastAPI, Node vs Python, `/live` zamiast `/health`.

`expectations.yaml` wymusza **fastapi** + 7 konkretnych tras — typowy fail rundy 1: zły framework lub brakujące ścieżki.

## Metryki

```bash
jq '.verify_iterations, .success' generated/session.json
jq '[.[] | {round, success, errors: .errors[0]}]' generated/verify.rounds.json
```
