# Dokumentacja ITERUN

## Indeks

| Dokument | Opis |
|----------|------|
| [INTENT_DSL_SPEC.md](INTENT_DSL_SPEC.md) | Składnia DSL, `iterun.yaml`, STACK, pipeline, verify |
| [API.md](API.md) | REST, SDK, MCP (`iterun-mcp`), `IterunService` |
| [REGISTRY.md](REGISTRY.md) | Rejestr usług/artefaktów (`iterun.registry.json`) |
| [RUNTIME.md](RUNTIME.md) | markpact (`stack.markpact.md`) + pactown runtime |
| [../README.md](../README.md) | Instalacja, architektura, quick start |
| [../examples/README.md](../examples/README.md) | Przykłady 01–19, artefakty `generated/` |
| [../examples/OPERATIONS.md](../examples/OPERATIONS.md) | Logi, status, flagi CLI, Docker, registry |

## Architektura (skrót)

```text
prompt (NL)
  → Generator (LiteLLM)        → iterun.yaml
  → intract + testql             → kontrakty w generated/
  → Planner                    → app.py, Dockerfile, docker-compose (STACK)
  → markpact pack              → stack.markpact.md (+ services/*/README.md)
  → Execute
      · docker (domyślnie)     → Docker / compose
      · pactown                → ITERUN_RUNTIME=pactown / --runtime pactown
  → Contract verify (--verify) → TestQL + HTTP + pętla naprawy LLM
  → Registry                   → iterun.registry.json
  → session.json               → pełny log sesji
```

Warstwa API: `interfaces/service.py` (`IterunService`) — wspólny entry point dla REST, SDK, MCP, CLI.

## CLI — najczęstsze komendy

```bash
# Prompt → paczka → usługa → weryfikacja + naprawa LLM
iterun generate "Create a REST API for users" -o generated/ --execute --verify

# Pactown zamiast Docker
iterun generate "..." -o generated/ --execute --runtime pactown --verify

# Tylko YAML (+ auto intract + testql + markpact pack przy --run)
iterun generate "Create a ping API" -o generated/ --quiet

# Rejestr
iterun registry -o generated/
iterun registry list examples/*/generated

# Schema / walidacja ręcznego DSL
iterun schema
iterun validate generated/iterun.yaml

# Plan / execute istniejącej paczki
iterun plan generated/iterun.yaml -o generated/
iterun execute generated/iterun.yaml --workspace generated/

# MCP (osobny terminal, z root repo iterun)
pip install -e ".[mcp]"
iterun-mcp

# Shell interaktywny
iterun
```

### Flagi `iterun generate`

| Flaga | Domyślnie | Opis |
|-------|-----------|------|
| `-o`, `--output-dir` | `generated` | Katalog artefaktów sesji |
| `--run` | off | Plan po wygenerowaniu YAML (+ markpact pack) |
| `--execute` | off | Deploy po planie (docker lub pactown) |
| `--verify` | off | TestQL + HTTP; **pętla naprawy LLM** przy fail |
| `--runtime` | `docker` | `docker` lub `pactown` |
| `--max-iterations` | 5 | Limit walidacji YAML przez LLM |
| `--max-verify-iterations` | 3 | Limit rund naprawczych przy `--verify` |
| `-m`, `--model` | z `.env` | Model LiteLLM (np. OpenRouter) |
| `--json` | off | Wynik sesji na stdout (JSON) |
| `--quiet` | off | Minimalny output (skrypty) |

**Uwaga:** `--execute` bez `--verify` = deploy + HTTP smoke; **bez regeneracji YAML przez LLM**.

## Pliki w `generated/`

| Plik | Zawartość |
|------|-----------|
| `iterun.yaml` | Paczka DSL (główny artefakt) |
| `session.json` | **Pełny log** — prompt, generate, plan, execute, verify |
| `intract.yaml` | Kontrakt Intract (`require: implement.*`) |
| `service.testql.toon.yaml` | Scenariusz TestQL |
| `stack.markpact.md` | Cały workspace w jednym pliku markpact |
| `pactown.yaml` | Konfiguracja ekosystemu pactown |
| `pactown.urls.json` | URL usług (runtime pactown) |
| `stack.urls.json` | URL gatewayów (STACK, docker) |
| `iterun.registry.json` | Rejestr usług i artefaktów |
| `catalog/` | Eksport Backstage Component |
| `plan.result.json` | IR + logi planera |
| `execution.json` | Execute, endpointy, `container_id` |
| `container.log` | Tail logów (docker lub compose) |
| `verify.result.json` | Wynik ostatniego verify |
| `verify.rounds.json` | Historia rund naprawczych |
| `app.py` / `Dockerfile` | Wygenerowana usługa |
| `docker-compose.yaml` | STACK (multi-service) |
| `services/*/` | Per-service Dockerfile + kod (STACK) |

Pełna tabela: [examples/README.md § Gdzie są dane i logi](../examples/README.md#gdzie-są-dane-i-logi-generated).

## Przykłady

| Skrypt | Zakres |
|--------|--------|
| `./examples/run-all.sh` | 01–08: prompt → `iterun.yaml` → plan |
| `./examples/run-e2e.sh` | 09–12: execute + TestQL + Intract |
| `./examples/run-resilience.sh` | 13–16: skrajne prompty, pętla naprawcza |
| `./examples/run-stacks.sh` | 17–19: multi-service STACK |

| Katalog | Temat |
|---------|-------|
| `01-user-api` | FastAPI CRUD |
| `02-ping-smoke` | Minimalny `/ping` |
| `08-llm-generate` | SDK + MCP + REST |
| `09-e2e-ping-verify` | TestQL + Intract |
| `12-e2e-full-gate` | Pełny gate (intract graph/scan) |
| `13-resilience-vague` | Mglisty prompt vs expectations |
| `17-stack-shop-gateway` | STACK: gateway + users + catalog |
| `18-stack-blog` | STACK: blog API + worker + frontend |
| `19-stack-api-cache` | STACK: API + Redis cache |

Każdy `examples/NN-*/README.md` ma sekcje **Operacje** i **Nowe opcje** (`--runtime`, registry, API).

## Integracje zewnętrzne

| Narzędzie | Rola w ITERUN |
|-----------|----------------|
| [LiteLLM](https://github.com/BerriAI/litellm) | OpenRouter / Ollama w `iterun generate` |
| [TestQL](https://github.com/oqlos/testql) | `--verify`, `service.testql.toon.yaml` |
| [Intract](https://github.com/semcod/intract) | `intract.yaml`, walidacja kontraktu kodu |
| [markpact](https://github.com/wronai/markpact) | `stack.markpact.md` — jeden plik stacka |
| [pactown](https://github.com/wronai/pactown) | Universal runtime (`--runtime pactown`) |

## Konfiguracja (`.env`)

```bash
OPENROUTER_API_KEY=sk-or-...
LLM_MODEL=openrouter/deepseek/deepseek-v4-pro   # generate
DEFAULT_MODEL=llama3.2                          # shell suggest/chat (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
ITERUN_RUNTIME=docker                           # lub pactown
SKIP_ITERUN_CONFIRMATION=true
CONTAINER_PORT=8000
```

Priorytet modelu: `--model` CLI > `LLM_MODEL` > `DEFAULT_MODEL`.

Opcjonalne extra: `pip install -e ".[ai,mcp,runtime]"`.
