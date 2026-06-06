# ITERUN Intent DSL — Specification

## Overview

ITERUN intent DSL is YAML describing **what** to deploy (API, actions, runtime).
Generation paths:

| Interface | Entry |
|-----------|-------|
| CLI | `iterun generate "prompt" -o generated/` |
| REST | `POST /api/intents/generate` |
| SDK | `IterunClient().generate(prompt)` |
| MCP | `iterun_generate_intent` tool |

## Document structure

```yaml
INTENT:          # required
  name: kebab-case-id
  goal: string
  description: optional

ENVIRONMENT:     # optional (defaults shown)
  runtime: docker | kubernetes | local
  base_image: python:3.12-slim
  ports: [8000]
  env_vars: {}

IMPLEMENTATION:  # required
  language: python | node
  framework: fastapi | flask | express
  actions:         # list of DSL strings
    - api.expose GET /ping

EXECUTION:       # optional
  mode: dry-run | transactional
```

## Action grammar

```
api.expose METHOD /path
db.create table
db.add_column table column type
shell.exec command
rest.call METHOD url
file.create path
```

## JSON Schema

```bash
iterun schema
# GET /api/schema
```

## LLM generation loop

1. System prompt includes JSON Schema + example + action rules
2. User prompt: natural language goal
3. LiteLLM completion → extract YAML
4. Validate: Pydantic schema + `parse_dsl()`
5. On failure: re-prompt with errors + previous YAML (max 5 iterations default)
6. Optional: `plan` → `execute` (Docker)

```bash
iterun generate "Create a REST API for user management" \
  -o examples/08-llm-generate/generated \
  --run

ITERUN_EXECUTE=1 iterun generate "..." -o out/ --execute
```

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_MODEL` | llama3.2 | LiteLLM model |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama |
| `OPENROUTER_API_KEY` | — | OpenRouter via LiteLLM |
