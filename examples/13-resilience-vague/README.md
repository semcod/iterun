# 13 — Resilience: vague prompt

**Test:** mglisty prompt vs surowe `expectations.yaml` (pełny CRUD + health).

LLM często generuje za mało endpointów w rundzie 1 → `expectations` fail → retry z kontekstem błędów.

## Uruchomienie

```bash
ITERUN_MAX_VERIFY_ITERATIONS=5 ./run.sh
```

## Obserwacja iteracji

```bash
cat generated/verify.rounds.json   # każda runda: errors, testql, URL
cat generated/session.json         # final success + verify_iterations
```

Oczekiwane: `verify_iterations` ≥ 1, końcowy `success: true`.
