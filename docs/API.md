# ITERUN API — REST, SDK, MCP

ITERUN exposes the same operations through several integration surfaces. All paths go through `IterunService` (`interfaces/service.py`).

## Surfaces

| Surface | Entry | Use case |
|---------|-------|----------|
| **REST** | `python -m web.app` → `http://localhost:8000` | HTTP clients, CI, remote SDK |
| **CLI** | `iterun generate`, `iterun plan`, … | Shell, examples |
| **SDK** | `from sdk import IterunClient` | Python apps (local or remote) |
| **MCP** | `iterun-mcp` | LLM agents (Cursor, Claude Desktop) |
| **Pipeline** | `run_pipeline()` | Full prompt → verify flow |

Discover surfaces at runtime:

```bash
curl http://localhost:8000/api/interfaces
```

## REST API

OpenAPI docs: `http://localhost:8000/docs`

### Meta

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Liveness probe |
| `GET` | `/api/interfaces` | List surfaces, endpoints, MCP tools |
| `GET` | `/api/schema` | JSON Schema for intent DSL |

### Intent document

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/intents/validate-yaml` | Validate YAML (`is_stack` in response) |
| `POST` | `/api/intents/parse` | Parse DSL → store intent |
| `POST` | `/api/intents/plan-yaml` | Plan from YAML (STACK → compose) |
| `POST` | `/api/intents/generate` | LLM → YAML only |

### Pipeline

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/pipeline/run` | generate → plan → execute? → verify? |
| `POST` | `/api/intents/generate-and-run` | Alias for `/api/pipeline/run` |

Request body (`POST /api/pipeline/run`):

```json
{
  "prompt": "Create a shop API with gateway and users service",
  "output_dir": "generated",
  "execute": false,
  "verify": false,
  "max_iterations": 5,
  "max_verify_iterations": 3,
  "model": null
}
```

### Stored intents (in-memory)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/intents` | List intents |
| `GET` | `/api/intents/{id}` | Get intent |
| `DELETE` | `/api/intents/{id}` | Delete |
| `POST` | `/api/intents/{id}/plan` | Plan stored intent (`compose_yaml` for STACK) |
| `POST` | `/api/intents/{id}/execute` | Run Docker / compose |
| `GET` | `/api/containers/{id}/logs` | Container logs |

## Python SDK

```python
from sdk import IterunClient

# Local (in-process)
client = IterunClient()
client.health()
client.interfaces()
client.validate(open("iterun.yaml").read())
client.generate("Create a ping API")
client.run_pipeline("…", output_dir="generated", execute=True, verify=True)
client.plan_yaml(open("iterun.yaml").read(), output_dir="generated")

# Remote REST server
remote = IterunClient(base_url="http://localhost:8000")
remote.run_pipeline("Create API", execute=False)
```

## MCP (Model Context Protocol)

Install: `pip install -e ".[mcp]"`

```bash
iterun-mcp
# or: python -m iterun_mcp.server
```

### Tools

| Tool | Description |
|------|-------------|
| `iterun_interfaces` | List surfaces and endpoints |
| `iterun_schema` | JSON Schema for DSL |
| `iterun_validate_intent` | Validate YAML |
| `iterun_parse_yaml` | Parse to IR JSON |
| `iterun_plan_yaml` | Dry-run plan (+ optional `output_dir`) |
| `iterun_generate_intent` | LLM → YAML |
| `iterun_run_pipeline` | Full pipeline (`execute`, `verify`) |
| `iterun_run_intent` | Deprecated alias (no `verify`) |

### Cursor / Claude Desktop config

```json
{
  "mcpServers": {
    "iterun": {
      "command": "iterun-mcp",
      "cwd": "/path/to/iterun"
    }
  }
}
```

## Registry (usługi i artefakty)

Pełna dokumentacja: **[REGISTRY.md](REGISTRY.md)**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/registry?workspace=generated` | Odczyt `iterun.registry.json` |
| `POST` | `/api/registry/refresh` | Odśwież rejestr + Backstage + OTel |
| `GET` | `/api/registry/list` | Lista workspace’ów (`pattern`) |

CLI: `iterun registry -o generated/`

## STACK (multi-service)

STACK intents use the same API. Responses include:

- `is_stack: true`
- `compose_yaml` — `docker-compose.yaml` content
- `service_artifacts` — per-service Dockerfiles and metadata

Example: plan a stack via REST:

```bash
curl -X POST http://localhost:8000/api/intents/plan-yaml \
  -H 'Content-Type: application/json' \
  -d '{"content": "'"$(cat examples/17-stack-shop-gateway/iterun.yaml)"'", "output_dir": "generated"}'
```

## Quick start

**Zawsze z katalogu głównego repozytorium** (`~/github/wronai/iterun`), nie z `examples/*`.

```bash
cd ~/github/wronai/iterun && source venv/bin/activate
pip install -e ".[ai]"

# REST (jeśli :8000 zajęty — użyj innego portu, np. 8800)
uvicorn web.app:app --reload --port 8800
curl http://localhost:8800/api/interfaces

# MCP (osobny terminal, ten sam katalog iterun/)
pip install -e ".[mcp]"
iterun-mcp
# lub: python -m iterun_mcp.server

# SDK (w pythonie / python -c, nie wklejaj do bash)
python -c "
from sdk import IterunClient
c = IterunClient()
print(c.interfaces())
"
```

### Typowe błędy

| Błąd | Przyczyna | Rozwiązanie |
|------|-----------|-------------|
| `address already in use :8000` | port zajęty (np. inna usługa) | `--port 8800` |
| `does not appear to be a Python project` przy `pip install -e ".[mcp]"` | jesteś w `examples/…` | `cd ~/github/wronai/iterun` |
| `cannot import name 'main' from 'mcp.server'` | stary konflikt nazw (naprawiony) | `pip install -e ".[mcp]"` + moduł `iterun_mcp` |
| `from sdk import` w bash | Python wklejony do shella | `python -c "..."` lub `python` REPL |
