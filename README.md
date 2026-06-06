# INTENT-ITERATIVE

> DSL-based intent execution system with iterative refinement, AMEN boundary, and AI-powered assistance

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.1-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.33-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-3.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.3304 (4 commits)
- 👤 **Human dev:** ~$300 (3.0h @ $100/h, 30min dedup)

Generated on 2026-06-06 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

## Overview

INTENT-ITERATIVE is a system that allows you to:

1. **Define intents** using a simple YAML-based DSL
2. **Simulate execution** with dry-run planning
3. **Get AI suggestions** using local LLMs via Ollama
4. **Iteratively refine** your intent through feedback loops
5. **Execute safely** with the AMEN boundary (explicit approval required)

## Architecture

```
┌─────────────────────┐
│  CLI / Web UI       │  ← User interface
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Parser / Validator  │  ← DSL → IR
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Intermediate Rep.   │  ← Canonical state
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Planner / Simulator │  ← Dry-run
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ AI Gateway (Ollama) │  ← LLM suggestions
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Feedback Loop       │  ← Iterate
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ AMEN Boundary       │  ← Explicit approval
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Executor            │  ← Real execution
└─────────────────────┘
```

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/softreck/iterun.git
cd iterun

# Full setup (recommended)
make setup

# Or manual install
pip install -r requirements.txt
pip install litellm
cp .env.example .env
```

### Configuration (.env)

Copy `.env.example` to `.env` and adjust:

```bash
# Server
HOST=0.0.0.0
PORT=8080

# AI Gateway
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.2
MAX_MODEL_PARAMS=12.0

# Execution (no AMEN prompt by default)
SKIP_AMEN_CONFIRMATION=true
CONTAINER_PORT=8000
```

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

# Execute intent directly (no AMEN prompt)
make execute
# Or: python -m cli.main execute examples/user-api.intent.yaml
```

**Interactive Shell Commands:**

```
intent> new my-api          # Create new intent
intent> load file.yaml      # Load from file
intent> plan                # Run dry-run
intent> suggest             # Get AI suggestions
intent> apply               # Auto-apply AI suggestions
intent> chat                # Chat with AI
intent> iterate             # Apply manual changes
intent> amen                # Approve execution
intent> execute             # Execute approved intent
intent> show [json]         # Show current state
intent> models              # List AI models
intent> ai-health           # Check AI Gateway status
intent> help                # Show help
intent> exit                # Exit shell
```

### Web Interface

```bash
# Start web server
python -m web.app

# Open browser at http://localhost:8080
```

## AI Gateway

The AI Gateway uses **LiteLLM** to provide unified access to local LLMs via Ollama.

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

### DSL Format

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

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/intents` | List all intents |
| `POST` | `/api/intents/parse` | Parse DSL and create intent |
| `GET` | `/api/intents/{id}` | Get intent by ID |
| `DELETE` | `/api/intents/{id}` | Delete intent |
| `POST` | `/api/intents/{id}/plan` | Run dry-run |
| `POST` | `/api/intents/{id}/iterate` | Apply changes |
| `POST` | `/api/intents/{id}/amen` | Approve for execution |
| `POST` | `/api/intents/{id}/execute` | Execute approved intent |
| `GET` | `/api/intents/{id}/code` | Get generated code |

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
from ir.models import IntentIR
from parser import parse_dsl
from planner import plan_intent
from ai_gateway import get_gateway, create_feedback_loop

# Parse DSL
ir = parse_dsl(dsl_content)

# Run dry-run
result = plan_intent(ir)
print(result.generated_code)

# Get AI suggestions
loop = create_feedback_loop()
suggestions = loop.analyze(ir, focus="security")
print(suggestions.suggestions)

# Apply AI suggestions
loop.iterate(ir, auto_apply=True)

# Or chat directly
gateway = get_gateway()
response = gateway.complete("Explain FastAPI middleware")
print(response["content"])
```

## Testing

```bash
# Run all tests (58 tests)
pytest

# Run specific test suites
pytest tests/e2e/test_shell.py -v      # 17 tests
pytest tests/e2e/test_web.py -v        # 18 tests  
pytest tests/e2e/test_ai_gateway.py -v # 23 tests

# Run with coverage
pytest --cov=. --cov-report=html
```

## Project Structure

```
intent-iterative/
├── ir/                 # Intermediate Representation models
├── parser/             # DSL parser
├── planner/            # Dry-run simulator
├── executor/           # Execution engine
├── ai_gateway/         # LiteLLM AI Gateway
│   ├── gateway.py      # Main gateway with Ollama models
│   └── feedback_loop.py # LLM-powered feedback loop
├── cli/                # Shell interface
├── web/                # Web interface (FastAPI)
├── tests/e2e/          # E2E test suite
│   ├── test_shell.py
│   ├── test_web.py
│   └── test_ai_gateway.py
├── examples/           # Example DSL files
├── config.py           # Configuration loader
├── Makefile            # Build automation
├── .env.example        # Environment template
├── requirements.txt
└── README.md
```

## Workflow

1. **Define Intent** → Write DSL or use web editor
2. **Parse** → Convert DSL to IR (Intermediate Representation)
3. **Plan** → Run dry-run simulation, review generated code
4. **Get AI Suggestions** → Analyze with local LLM
5. **Iterate** → Make changes, re-plan until satisfied
6. **Execute** → Run with auto-validation and auto-fix
7. **Validate** → Automatic health checks on all endpoints

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
