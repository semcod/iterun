# 17 — STACK: Shop Gateway

**Jedna aplikacja, trzy Dockerfile + `docker-compose.yaml`:**

| Serwis | Technologia | Port hosta |
|--------|-------------|------------|
| `api-gateway` | FastAPI (proxy) | 18080 (lub kolejny wolny) |
| `users-service` | FastAPI (wewnętrzny) | — |
| `catalog-service` | Express (wewnętrzny) | — |

## Uruchomienie (fixture `iterun.yaml` w repo)

```bash
cd ~/github/wronai/iterun/examples/17-stack-shop-gateway
source ../../venv/bin/activate
./run.sh
```

## Z promptu (LLM)

**Ważne:** `prompt.txt` jest w **tym katalogu** — nie używaj ścieżki `examples/17-.../prompt.txt`, gdy już tu jesteś.

```bash
cd ~/github/wronai/iterun/examples/17-stack-shop-gateway
source ../../venv/bin/activate

./run-generate.sh
# lub (z tego katalogu!):
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute

iterun generate "$(cat prompt.txt)" -o generated/ --run --execute --verify --json

# Pactown (bez docker w iterun) — wymaga: pip install -e ../../.[runtime]
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute --runtime pactown --verify
```

Po planie: `generated/stack.markpact.md` (cały stack), `generated/pactown.yaml`. Zobacz [RUNTIME.md](../../docs/RUNTIME.md).

Z root repo iterun:

```bash
cd ~/github/wronai/iterun && source venv/bin/activate
python -m cli generate "$(cat examples/17-stack-shop-gateway/prompt.txt)" \
  -o examples/17-stack-shop-gateway/generated/ --run --execute
```

`Command 'iterun' not found` → `pip install -e ".[ai]"` w venv iterun.

## Pliki

| Plik | Rola |
|------|------|
| **`iterun.yaml`** (tu) | Źródło STACK w repo |
| **`generated/`** | `docker-compose.yaml`, `services/*/`, `plan.result.json` |
| **`stack.markpact.md`** | Cały stack w jednym pliku markpact |
| **`pactown.yaml`** | Konfiguracja pactown (przy `--runtime pactown`) |
| **`iterun.registry.json`** | Rejestr usług i artefaktów |

`./run.sh` **nie** tworzy `session.json` (to robi `iterun generate`). Logi execute: `plan.result.json` + `docker compose logs`.

## Operacje (logi, status, parametry)

Pełna ściągawka: [OPERATIONS.md](../OPERATIONS.md)

### Nowe opcje (runtime, markpact, registry, API)

| Opcja | Opis |
|-------|------|
| `--runtime docker` | Domyślnie — `docker compose` |
| `--runtime pactown` | STACK przez pactown Orchestrator |
| `--verify` | Pętla naprawy LLM przy fail kontraktu |
| `iterun registry -o generated/` | Rejestr usług STACK |

Artefakty: `stack.markpact.md`, `pactown.yaml`, `stack.urls.json` / `pactown.urls.json`, `iterun.registry.json`.

```bash
iterun registry -o generated/ -q
jq '.spec.services[] | {name, urls}' generated/iterun.registry.json
```

Zobacz [RUNTIME.md](../../docs/RUNTIME.md), [REGISTRY.md](../../docs/REGISTRY.md), [API.md](../../docs/API.md).

### Parametry

| Zmienna | Efekt |
|---------|--------|
| `ITERUN_EXECUTE=0` | Tylko plan (bez `docker compose`) |
| `ITERUN_SKIP_CLEAN=1` | Zachowaj poprzednie `generated/` |

### Logi w trakcie

```bash
cd ~/github/wronai/iterun/examples/17-stack-shop-gateway

# verbose (bez --quiet)
python -m cli plan iterun.yaml -o generated/
python -m cli execute iterun.yaml --workspace generated/

# z promptu — pełny JSON sesji
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute --json | jq .
```

### Status po `./run.sh`

```bash
# faktyczne URL (po run.sh → generated/stack.urls.json)
cat generated/stack.urls.json
PORT=$(docker compose -f generated/docker-compose.yaml -p intent-shop-stack port api-gateway 8000 | cut -d: -f2)
echo "gateway http://localhost:$PORT"

# compose
docker compose -f generated/docker-compose.yaml -p intent-shop-stack ps

# HTTP — użyj PORT z powyżej (często 18081, nie 18080 z iterun.yaml)
curl -s "http://localhost:${PORT}/ping"
curl -s "http://localhost:${PORT}/users"

# logi gateway na żywo
docker compose -f generated/docker-compose.yaml -p intent-shop-stack logs -f api-gateway

# logi planera
jq '.plan.logs[]' generated/plan.result.json
```

### Po `iterun generate` (jest `session.json`)

```bash
jq '{success, error}' generated/session.json
URL=$(jq -r '.execution.endpoints[0]' generated/session.json)
curl -s "$URL/ping"
```
