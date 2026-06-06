# ITERUN

> DSL-based intent execution system with iterative refinement, ITERUN boundary, and AI-powered assistance

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.12-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$3.85-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-6.5h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $3.8541 (17 commits)
- 👤 **Human dev:** ~$646 (6.5h @ $100/h, 30min dedup)

Generated on 2026-06-06 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

## Overview

ITERUN is a system that allows you to:

1. **Generate intents from prompts** (LiteLLM / OpenRouter / Ollama) → **`iterun.yaml`**
2. **Define intents** manually in YAML DSL (sekcja `INTENT:`)
3. **Simulate execution** with dry-run planning
4. **Deploy services** via Docker (default) or **pactown** sandboxes (`--runtime pactown`)
5. **Pack stacks** to a single **markpact** file (`stack.markpact.md`)
6. **Orchestrate repair** with **contract verify** (TestQL + LLM retry via `--verify`)
7. **Monitor artifacts** with service registry (`iterun.registry.json`)
8. **Integrate** via REST, SDK, MCP (`iterun-mcp`)
9. **Get AI suggestions** in the interactive shell (Ollama / LiteLLM)
10. **Execute safely** with the ITERUN boundary (explicit approval when enabled)

**One-liner (prompt → running service):**

```bash
iterun generate "Create a REST API for user management" \
  -o generated/ --execute --verify
```

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  CLI · REST · SDK · MCP (iterun-mcp)                     │
│  interfaces/IterunService — wspólna warstwa API            │
└─────────────────────────┬────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  Generator (LLM) → iterun.yaml + intract + testql        │
│  Parser → IR · Planner → app.py / compose / STACK        │
│  markpact pack → stack.markpact.md                       │
└─────────────────────────┬────────────────────────────────┘
                          ↓
┌────────────────────┐    ┌─────────────────────────────┐
│ Runtime: docker    │ or │ Runtime: pactown            │
│ (Executor)         │    │ (integrations/pactown_*)    │
└─────────┬──────────┘    └──────────────┬──────────────┘
          └──────────────┬───────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  Contract verify (--verify) → LLM repair loop            │
│  Registry → iterun.registry.json (Backstage / OTel)      │
│  session.json — pełny log sesji                          │
└──────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/softreck/iterun.git
cd iterun

# Full setup (recommended)
make setup

# Editable install (recommended)
python3 -m venv venv && source venv/bin/activate
pip install -e ".[ai]"
pip install -e ".[runtime]"   # opcjonalnie: markpact + pactown
# lub lokalnie: pip install -e ../markpact -e ../pactown
cp .env.example .env
```

### Configuration (.env)

Copy `.env.example` to `.env` and adjust:

```bash
# LLM for `iterun generate` (priority: --model > LLM_MODEL > DEFAULT_MODEL)
OPENROUTER_API_KEY=sk-or-...
LLM_MODEL=openrouter/deepseek/deepseek-v4-pro

# Local Ollama (shell suggest/chat fallback)
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.2

# Server / execution
HOST=0.0.0.0
PORT=8080
SKIP_ITERUN_CONFIRMATION=true
CONTAINER_PORT=8000
ITERUN_RUNTIME=docker          # lub pactown (bez docker w iterun)
```

### Generate from prompt

```bash
source venv/bin/activate

# YAML only
iterun generate "Create a ping API" -o generated/

# Plan + artifacts
iterun generate "..." -o generated/ --run

# Docker + contract verify + LLM repair loop (--verify wymagane!)
iterun generate "..." -o generated/ --execute --verify --max-verify-iterations 5

# Pactown runtime (markpact sandboxes zamiast docker compose)
iterun generate "..." -o generated/ --execute --runtime pactown --verify

# Rejestr usług i artefaktów
iterun registry -o generated/

# Full JSON session log
iterun generate "..." -o generated/ --execute --verify --json
```

Output directory (`generated/` by default) — see [Session artifacts](#session-artifacts).

### AI Gateway Setup (Ollama)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start and pull model
make ollama-start
make ollama-pull

# Or manually
ollama serve
ollama pull llama3.2
```

### Using Makefile

```bash
make help          # Show all commands
make setup         # Full setup
make web           # Start web server
make shell         # Interactive shell
make execute       # Execute example intent
make test          # Run all tests
make ollama-models # List available models
make clean         # Clean temp files
```

### Shell Interface

```bash
# Start interactive shell
make shell
# Or: python -m cli.main

# Generate + execute from prompt
make execute
# Or: iterun generate "$(cat examples/01-user-api/prompt.txt)" -o examples/01-user-api/generated/ --execute --verify
```

**Interactive Shell Commands:**

```
intent> new my-api          # Create new intent
intent> load iterun.yaml    # Load package (generated/iterun.yaml)
intent> plan                # Run dry-run
intent> suggest             # Get AI suggestions
intent> apply               # Auto-apply AI suggestions
intent> chat                # Chat with AI
intent> iterate             # Apply manual changes
intent> iterun                # Approve execution
intent> execute             # Execute approved intent
intent> show [json]         # Show current state
intent> models              # List AI models
intent> ai-health           # Check AI Gateway status
intent> help                # Show help
intent> exit                # Exit shell

# Poza shell — registry i runtime
iterun registry -o generated/
iterun registry list examples/*/generated
```

### MCP (agents)

```bash
pip install -e ".[mcp]"
iterun-mcp   # z katalogu root iterun; nie z examples/*
```

### Web Interface

```bash
# Start web server
python -m web.app

# Open browser at http://localhost:8080
```

## AI Gateway

The AI Gateway uses **LiteLLM** for:

- **`iterun generate`** — cloud models via **OpenRouter** (`OPENROUTER_API_KEY`, `LLM_MODEL`)
- **Shell `suggest` / `chat`** — local **Ollama** (`OLLAMA_BASE_URL`, `DEFAULT_MODEL`)

### Supported Models (≤12B parameters)

| Model | Size | Description |
|-------|------|-------------|
| `llama3.2` | 3B | Default - Fast and efficient |
| `llama3.2:1b` | 1B | Ultra lightweight |
| `llama3.1:8b` | 8B | Balanced performance |
| `mistral` | 7B | Fast inference |
| `mistral-nemo` | 12B | Best quality under 12B |
| `gemma2` | 9B | Google Gemma 2 |
| `gemma2:2b` | 2B | Lightweight |
| `phi3` | 3.8B | Microsoft Phi-3 |
| `qwen2.5` | 7B | Alibaba Qwen 2.5 |
| `codellama` | 7B | Code generation |
| `codegemma` | 7B | Google CodeGemma |
| `deepseek-coder` | 6.7B | DeepSeek Coder |

### Configuration

Environment variables:

```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export DEFAULT_MODEL="llama3.2"
export MAX_MODEL_PARAMS="12.0"
```

### Package file: `iterun.yaml`

The canonical workspace filename is **`iterun.yaml`** (not `intent.yaml`). Full spec: [docs/INTENT_DSL_SPEC.md](docs/INTENT_DSL_SPEC.md).

```yaml
INTENT:
  name: user-api
  goal: Create a REST API for user management

ENVIRONMENT:
  runtime: docker
  base_image: python:3.12-slim
  ports:
    - 8000

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
    - api.expose GET /users
    - api.expose POST /users
    - api.expose DELETE /users/{id}

EXECUTION:
  mode: dry-run
```

### Supported Actions

| Action | Format | Description |
|--------|--------|-------------|
| `api.expose` | `api.expose METHOD /path` | Expose HTTP endpoint |
| `db.create` | `db.create table_name` | Create database table |
| `db.add_column` | `db.add_column table column type` | Add column to table |
| `shell.exec` | `shell.exec command` | Execute shell command |
| `rest.call` | `rest.call METHOD url` | Call external REST API |
| `file.create` | `file.create path` | Create file |

## API Reference

Pełna dokumentacja: **[docs/API.md](docs/API.md)** — REST, SDK, MCP, STACK.  
Rejestr usług/artefaktów: **[docs/REGISTRY.md](docs/REGISTRY.md)** — Backstage, OCI, OTel.  
Runtime markpact+pactown: **[docs/RUNTIME.md](docs/RUNTIME.md)** — odchudzone uruchamianie.

### Integration surfaces

| Surface | Entry |
|---------|-------|
| REST | `uvicorn web.app:app` → `/api/*`, OpenAPI `/docs` |
| CLI | `iterun generate`, `iterun plan`, … |
| SDK | `IterunClient()` — local lub `base_url="http://…"` |
| MCP | `iterun-mcp` / `python -m iterun_mcp.server` — narzędzia dla agentów LLM |

### REST Endpoints (skrót)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Liveness |
| `GET` | `/api/interfaces` | Lista powierzchni API |
| `GET` | `/api/schema` | JSON Schema for DSL |
| `POST` | `/api/intents/validate-yaml` | Validate YAML (`is_stack`) |
| `POST` | `/api/intents/plan-yaml` | Plan z YAML (STACK → compose) |
| `POST` | `/api/pipeline/run` | generate → plan → execute? → verify? |
| `POST` | `/api/intents/generate` | LLM → YAML |
| `POST` | `/api/intents/generate-and-run` | Alias `/api/pipeline/run` |
| `GET` | `/api/registry` | Service/artifact registry |
| `POST` | `/api/registry/refresh` | Refresh registry + exports |
| `GET` | `/api/intents` | List all intents |
| `POST` | `/api/intents/parse` | Parse DSL and create intent |
| `GET` | `/api/intents/{id}` | Get intent by ID |
| `POST` | `/api/intents/{id}/plan` | Dry-run (`compose_yaml` dla STACK) |
| `POST` | `/api/intents/{id}/execute` | Execute approved intent |

### AI Gateway Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/ai/status` | Check AI Gateway status |
| `GET` | `/api/ai/models` | List available models |
| `POST` | `/api/ai/complete` | Generate AI completion |
| `POST` | `/api/ai/chat` | Chat with AI |
| `POST` | `/api/intents/{id}/ai/suggest` | Get AI suggestions |
| `POST` | `/api/intents/{id}/ai/apply` | Auto-apply suggestions |

### Python API

```python
from generator.pipeline import run_pipeline
from parser import parse_dsl
from planner import plan_intent
from sdk import IterunClient

# Prompt → full pipeline
result = run_pipeline(
    "Create a REST API for user management",
    output_dir="generated",
    execute=True,
    verify=True,
)
print(result.yaml_path)       # generated/iterun.yaml
print(result.verification)    # testql + HTTP result

# Or SDK (local or remote REST)
client = IterunClient()
out = client.run_pipeline("Create a ping API", output_dir="generated", execute=True, verify=True)
# remote = IterunClient(base_url="http://localhost:8000")

# Manual DSL
ir = parse_dsl(open("generated/iterun.yaml").read())
plan = plan_intent(ir)
print(plan.generated_code)
```

## Examples

| Script | Opis |
|--------|------|
| `./examples/run-all.sh` | 01–08: prompt → `iterun.yaml` → plan |
| `./examples/run-e2e.sh` | 09–12: execute + TestQL + Intract |
| `./examples/run-resilience.sh` | 13–16: skrajne prompty, pętla naprawcza |
| `./examples/run-stacks.sh` | 17–19: multi-service STACK (compose / pactown) |

Szczegóły: [examples/README.md](examples/README.md) · operacje: [examples/OPERATIONS.md](examples/OPERATIONS.md).

## Session artifacts

Everything from one `iterun generate` run lands in `--output-dir` (default `generated/`):

| File | Content |
|------|---------|
| `iterun.yaml` | DSL package from LLM |
| `session.json` | **Full session** — prompt, generate attempts, plan, execute, verify |
| `intract.yaml` | Intract contract manifest |
| `service.testql.toon.yaml` | Auto-generated TestQL scenario |
| `plan.result.json` | Plan logs + IR |
| `execution.json` | Execute logs, endpoints, container id |
| `container.log` | Docker logs (tail) |
| `verify.result.json` | Contract verify result |
| `verify.rounds.json` | Repair loop history (`--verify`) |
| `app.py` / `Dockerfile` | Generated service |
| `stack.markpact.md` | Cały workspace w jednym pliku markpact |
| `pactown.yaml` | Konfiguracja ekosystemu pactown |
| `pactown.urls.json` | URL po `--runtime pactown` |
| `stack.urls.json` | URL gatewayów (STACK, docker) |
| `iterun.registry.json` | Rejestr usług i artefaktów |
| `catalog/` | Eksport Backstage (po `iterun registry`) |

## Testing

```bash
pytest
pytest tests/e2e/test_intent_generator.py -v
pytest tests/e2e/test_shell.py -v
pytest tests/e2e/test_web.py -v
pytest tests/e2e/test_ai_gateway.py -v
```

## Project Structure

```
iterun/
├── generator/          # LLM generate, pipeline, testql, intract, verify loop
│   ├── intent_generator.py
│   ├── pipeline.py
│   ├── contract_verify.py
│   └── session.py
├── dsl/                # Pydantic schema for LLM validation
├── ir/                 # Intermediate Representation
├── parser/             # DSL parser
├── planner/            # Dry-run simulator
├── executor/           # Docker execution + HTTP validation
├── ai_gateway/         # LiteLLM (Ollama + OpenRouter)
├── cli/                # `iterun` CLI
├── web/                # FastAPI web UI
├── sdk/                # Python SDK client
├── interfaces/         # IterunService — REST/SDK/MCP
├── integrations/       # markpact pack, pactown runtime, registry bridges
├── registry/           # iterun.registry.json catalog
├── iterun_mcp/         # MCP server (`iterun-mcp`; nie `mcp/` — konflikt PyPI)
├── examples/           # 01–19: prompt.txt + run.sh → generated/
├── docs/               # API, REGISTRY, RUNTIME, DSL spec
├── tests/e2e/
├── config.py           # PACKAGE_FILENAME = "iterun.yaml"
└── README.md
```

## Workflow

### Prompt-first (recommended)

1. **Prompt** → `iterun generate "..." -o generated/`
2. **Contracts** → auto `intract.yaml` + `service.testql.toon.yaml`
3. **Plan** → `app.py`, `Dockerfile`, `plan.result.json`
4. **Pack** → `stack.markpact.md` (+ per-service README dla pactown)
5. **Execute** → Docker (default) lub pactown (`--runtime pactown`)
6. **Verify** → TestQL + HTTP (`--verify`); **LLM repair** przy błędzie (bez `--verify` brak regeneracji YAML)
7. **Registry** → `iterun.registry.json`
8. **Session** → `session.json` aggregates all steps

### Manual / interactive

1. **Edit** `iterun.yaml` or use shell `new` / `load`
2. **Plan** → dry-run
3. **Suggest / iterate** → AI or manual refinement
4. **ITERUN** → approve (unless `SKIP_ITERUN_CONFIRMATION`)
5. **Execute** → deploy + endpoint validation

Documentation:

| Dokument | Temat |
|----------|-------|
| [docs/README.md](docs/README.md) | Indeks dokumentacji |
| [docs/INTENT_DSL_SPEC.md](docs/INTENT_DSL_SPEC.md) | DSL, pipeline, STACK |
| [docs/API.md](docs/API.md) | REST, SDK, MCP |
| [docs/REGISTRY.md](docs/REGISTRY.md) | Rejestr usług/artefaktów |
| [docs/RUNTIME.md](docs/RUNTIME.md) | markpact + pactown |

## Validation & Auto-Fix

After container deployment, the system automatically:

1. **Waits** for container startup (configurable `STARTUP_WAIT`)
2. **Validates** all exposed endpoints with HTTP requests
3. **Detects issues** like connection refused, timeouts, HTTP errors
4. **Auto-fixes** common problems:
   - Missing `__main__` block
   - Wrong port configuration
   - Missing dependencies
5. **Restarts** container with fixes
6. **Re-validates** until success or max iterations reached

### Configuration

```bash
# In .env
VALIDATE_AFTER_EXECUTE=true
AUTO_FIX_ENABLED=true
MAX_FIX_ITERATIONS=3
STARTUP_WAIT=2
VALIDATION_TIMEOUT=10
```

### Example Output

```
Execution Logs:
  [12:38:55] Container started: 8f35e0a2fb27
  [12:38:55] Waiting 2s for container startup...
  [12:38:57] ✓ http://localhost:8002 → 200
  [12:38:57] ✓ http://localhost:8002/ping → 200
  [12:38:57] ✓ http://localhost:8002/health → 200
  [12:38:57] ✓ All endpoints validated successfully
✓ Execution completed in 2.56s

Validation:
  ✓ All endpoints validated
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/intents/{id}/validate` | Validate running container |
| `GET` | `/api/containers/{id}/logs` | Get container logs |

## License

Licensed under Apache-2.0.
