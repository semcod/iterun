# 08 — LLM Generate

Generuje `intent.yaml` z promptu NL (LiteLLM + pętla walidacji), potem plan/execute.

## Uruchomienie

```bash
./run.sh
```

## Komendy

```bash
# tylko YAML
iterun generate "Create a REST API for user management" \
  -o examples/08-llm-generate/generated --quiet

# YAML + plan + execute
iterun generate "Create a REST API for user management" \
  -o examples/08-llm-generate/generated --run --execute

# JSON Schema
iterun schema

# walidacja
iterun validate examples/08-llm-generate/generated/intent.yaml
```

## SDK

```python
from sdk import IterunClient

client = IterunClient()
result = client.generate_and_run(
    "Create a REST API for user management",
    output_dir="generated",
    execute=False,
)
print(result.yaml_path)
```

## MCP

```bash
pip install mcp litellm
python -m mcp.server
# tool: iterun_generate_intent(prompt=...)
```

## `generated/`

| Plik | Skąd |
|------|------|
| `intent.yaml` | LLM + validate-retry |
| `app.py`, `Dockerfile` | `plan` |

Wymaga: `pip install litellm` + działający Ollama lub klucz API.
