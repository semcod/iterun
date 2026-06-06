# 18 — STACK: Blog (API + worker + frontend)

Trzy połączone kontenery: API (18000), worker (internal), frontend Express (13000).

```bash
./run.sh
ITERUN_RUNTIME=pactown ./run.sh   # opcjonalnie: pactown zamiast compose
```

## Operacje (logi, status, parametry)

Pełna ściągawka: [OPERATIONS.md](../OPERATIONS.md)

### Parametry tego przykładu

| Element | Wartość |
|---------|---------|
| Intent (`INTENT.name`) | `blog-stack` |
| Domyślny flow | `./run.sh` |

Wspólne: `ITERUN_PROMPT`, `ITERUN_SKIP_CLEAN=1`, `ITERUN_SKIP_INTRACT=1` (E2E) — patrz OPERATIONS.md.

### Nowe opcje (runtime, markpact, registry, API)

| Opcja | Opis |
|-------|------|
| `--runtime docker` | Domyślnie — `docker compose` |
| `--runtime pactown` | STACK przez pactown Orchestrator |
| `--verify` | Pętla naprawy LLM przy fail kontraktu |
| `iterun registry -o generated/` | Rejestr usług STACK |

Artefakty: `stack.markpact.md` (cały stack w jednym pliku), `pactown.yaml`, `stack.urls.json` / `pactown.urls.json`.

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute --runtime pactown --verify
iterun registry -o generated/ -q
jq '.spec.services[] | {name, urls}' generated/iterun.registry.json
```

Zobacz [RUNTIME.md](../../docs/RUNTIME.md), [REGISTRY.md](../../docs/REGISTRY.md).


### Logi w trakcie uruchomienia

```bash
# bez --quiet: pełny output plan/execute na terminalu
cd ~/github/wronai/iterun
./run.sh

# JSON całej sesji (generate)
iterun generate "$(cat prompt.txt)" -o generated/ --execute --verify --json | jq .

# podgląd logów planera / execute z plików (w trakcie kolejnego kroku)
tail -f generated/plan.result.json   # po --run
```

### Status po uruchomieniu

```bash
# sukces sesji
jq '{success, verify_iterations, error}' generated/session.json

# URL usługi (port dynamiczny!)
URL=$(jq -r '.verification.service_url // .execution.endpoints[0]' generated/session.json)

# HTTP
curl -s http://localhost:18000/posts; curl -s http://localhost:13000/

# Docker
docker compose -f generated/docker-compose.yaml -p intent-blog-stack logs -f blog-api

# logi kontenera
docker logs -f $(docker ps -q --filter name=blog-stack | head -1) 2>/dev/null || \
  cat generated/container.log
```

