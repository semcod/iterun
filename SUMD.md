# ITERUN

DSL-based intent execution system with iterative refinement, featuring AI-powered suggestions via Ollama, safe simulation, and automatic health validation.

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Makefile Targets](#makefile-targets)
- [Code Analysis](#code-analysis)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `iterun`
- **version**: `0.1.11`
- **python_requires**: `>=3.11`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, requirements.txt, Makefile, testql(3), app.doql.less, pyqual.yaml, goal.yaml, .env.example, project/(3 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: iterun;
  version: 0.1.11;
}

dependencies {
  runtime: "pyyaml>=6.0, pydantic>=2.0, fastapi>=0.109.0, uvicorn>=0.27.0, jinja2>=3.1.0";
  dev: "pytest>=8.0.0, pytest-asyncio>=0.23.0, httpx>=0.26.0, anyio>=4.0.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

entity[name="ArtifactRecord"] {
  name: string!;
  path: string!;
  kind: string!;
  role: ArtifactRole!;
  mime_type: str | None;
  standard: str | None;
  size_bytes: int | None;
  checksum_sha256: str | None;
  labels: dict[str, str]!;
}

entity[name="ServiceRecord"] {
  name: string!;
  type: string!;
  owner: string!;
  lifecycle: string!;
  urls: list[str]!;
  health_paths: list[str]!;
  framework: str | None;
  language: str | None;
  port: int | None;
  host_port: int | None;
  container_id: str | None;
  image: str | None;
  depends_on: list[str]!;
  labels: dict[str, str]!;
  otel: dict[str, Any]!;
}

entity[name="RegistryMetadata"] {
  name: string!;
  intent_id: str | None;
  workspace: string!;
  generated_at: string!;
  prompt: str | None;
  is_stack: bool!;
}

entity[name="RegistryStatus"] {
  phase: LifecyclePhase!;
  success: bool | None;
  session_path: str | None;
  verification: dict[str, Any] | None;
  endpoints: list[str]!;
}

entity[name="RegistryManifest"] {
  api_version: string!;
  kind: string!;
  metadata: RegistryMetadata!;
  spec: dict[str, Any]!;
  status: RegistryStatus!;
}

entity[name="InterfacesInfo"] {
  rest_base: string!;
  cli: string!;
  mcp_server: string!;
  sdk: string!;
  surfaces: list[dict[str, Any]]!;
}

entity[name="DSLInput"] {
  content: string!;
}

entity[name="IterationInput"] {
  changes: dict[str, Any]!;
  source: string!;
}

interface[type="api"] {
  type: rest;
  framework: fastapi;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="iterun"] {

}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install -r requirements.txt;
}

workflow[name="install-dev"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install pytest pytest-asyncio httpx anyio;
}

workflow[name="install-ai"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install litellm;
}

workflow[name="setup"] {
  trigger: manual;
  step-1: run cmd=echo "$(GREEN)✓ Setup complete$(RESET)";
}

workflow[name="env"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f .env ]; then \;
  step-2: run cmd=cp .env.example .env; \;
  step-3: run cmd=echo "$(GREEN)✓ Created .env from .env.example$(RESET)"; \;
  step-4: run cmd=else \;
  step-5: run cmd=echo "$(YELLOW)⚠ .env already exists$(RESET)"; \;
  step-6: run cmd=fi;
}

workflow[name="run"] {
  trigger: manual;
  step-1: depend target=web;
}

workflow[name="web"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Starting web server on http://$(HOST):$(PORT)$(RESET)";
  step-2: run cmd=$(PYTHON) -m web.app;
}

workflow[name="shell"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Starting interactive shell$(RESET)";
  step-2: run cmd=$(PYTHON) -m cli.main;
}

workflow[name="plan"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m cli.main plan examples/01-user-api/generated/iterun.yaml -o examples/01-user-api/generated/;
}

workflow[name="execute"] {
  trigger: manual;
  step-1: run cmd=ITERUN_EXECUTE=1 ./examples/01-user-api/run.sh;
}

workflow[name="examples"] {
  trigger: manual;
  step-1: run cmd=./examples/run-all.sh;
}

workflow[name="run-intent"] {
  trigger: manual;
  step-1: run cmd=if [ -z "$(FILE)" ]; then \;
  step-2: run cmd=echo "$(RED)ERROR: FILE not specified$(RESET)"; \;
  step-3: run cmd=echo "Usage: make run-intent FILE=path/to/iterun.yaml"; \;
  step-4: run cmd=exit 1; \;
  step-5: run cmd=fi;
  step-6: run cmd=$(PYTHON) -m cli.main execute $(FILE);
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/ -v;
}

workflow[name="test-shell"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/e2e/test_shell.py -v;
}

workflow[name="test-web"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/e2e/test_web.py -v;
}

workflow[name="test-ai"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/e2e/test_ai_gateway.py -v;
}

workflow[name="test-cov"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term;
}

workflow[name="ollama-start"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Starting Ollama server...$(RESET)";
  step-2: run cmd=ollama serve &;
  step-3: run cmd=sleep 2;
  step-4: run cmd=echo "$(GREEN)✓ Ollama server started$(RESET)";
}

workflow[name="ollama-pull"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Pulling model: $(DEFAULT_MODEL)$(RESET)";
  step-2: run cmd=ollama pull $(DEFAULT_MODEL);
  step-3: run cmd=echo "$(GREEN)✓ Model $(DEFAULT_MODEL) ready$(RESET)";
}

workflow[name="ollama-models"] {
  trigger: manual;
  step-1: run cmd=echo "";
  step-2: run cmd=echo "$(CYAN)Recommended Ollama models (≤12B):$(RESET)";
  step-3: run cmd=echo "  $(GREEN)llama3.2$(RESET)       - 3B  - Default, fast";
  step-4: run cmd=echo "  llama3.2:1b    - 1B  - Ultra lightweight";
  step-5: run cmd=echo "  llama3.1:8b    - 8B  - Balanced";
  step-6: run cmd=echo "  mistral        - 7B  - Fast inference";
  step-7: run cmd=echo "  mistral-nemo   - 12B - Best quality";
  step-8: run cmd=echo "  gemma2         - 9B  - Google Gemma 2";
  step-9: run cmd=echo "  phi3           - 3.8B - Microsoft Phi-3";
  step-10: run cmd=echo "  qwen2.5        - 7B  - Alibaba Qwen";
  step-11: run cmd=echo "  codellama      - 7B  - Code generation";
  step-12: run cmd=echo "";
  step-13: run cmd=echo "$(YELLOW)Install:$(RESET) ollama pull <model>";
  step-14: run cmd=echo "";
}

workflow[name="ollama-status"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Checking Ollama status...$(RESET)";
  step-2: run cmd=curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && \;
  step-3: run cmd=echo "$(GREEN)✓ Ollama is running$(RESET)" || \;
  step-4: run cmd=echo "$(RED)✗ Ollama is not running$(RESET)";
}

workflow[name="lint"] {
  trigger: manual;
  step-1: run cmd=which ruff > /dev/null 2>&1 && ruff check . || echo "$(YELLOW)ruff not installed$(RESET)";
}

workflow[name="format"] {
  trigger: manual;
  step-1: run cmd=which ruff > /dev/null 2>&1 && ruff format . || echo "$(YELLOW)ruff not installed$(RESET)";
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Cleaning...$(RESET)";
  step-2: run cmd=rm -rf __pycache__ */__pycache__ */*/__pycache__;
  step-3: run cmd=rm -rf .pytest_cache */.pytest_cache;
  step-4: run cmd=rm -rf *.egg-info .eggs;
  step-5: run cmd=rm -rf htmlcov .coverage;
  step-6: run cmd=rm -rf /tmp/intent-*;
  step-7: run cmd=echo "$(GREEN)✓ Cleaned$(RESET)";
}

workflow[name="docker-clean"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Cleaning Docker resources...$(RESET)";
  step-2: run cmd=-docker ps -a --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker rm -f;
  step-3: run cmd=-docker images --filter "reference=$(CONTAINER_PREFIX)-*" -q | xargs -r docker rmi -f;
  step-4: run cmd=echo "$(GREEN)✓ Docker cleaned$(RESET)";
}

workflow[name="docker-ps"] {
  trigger: manual;
  step-1: run cmd=docker ps --filter "name=$(CONTAINER_PREFIX)-";
}

workflow[name="docker-stop"] {
  trigger: manual;
  step-1: run cmd=docker ps --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker stop;
  step-2: run cmd=echo "$(GREEN)✓ Containers stopped$(RESET)";
}

workflow[name="dev"] {
  trigger: manual;
  step-1: run cmd=uvicorn web.app:app --reload --host $(HOST) --port $(PORT);
}

workflow[name="new-intent"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m cli.main new;
}

workflow[name="show-config"] {
  trigger: manual;
  step-1: run cmd=echo "";
  step-2: run cmd=echo "$(CYAN)Current Configuration:$(RESET)";
  step-3: run cmd=echo "  HOST=$(HOST)";
  step-4: run cmd=echo "  PORT=$(PORT)";
  step-5: run cmd=echo "  DEFAULT_MODEL=$(DEFAULT_MODEL)";
  step-6: run cmd=echo "  CONTAINER_PORT=$(CONTAINER_PORT)";
  step-7: run cmd=echo "  CONTAINER_PREFIX=$(CONTAINER_PREFIX)";
  step-8: run cmd=echo "  OLLAMA_BASE_URL=$(OLLAMA_BASE_URL)";
  step-9: run cmd=echo "  SKIP_ITERUN_CONFIRMATION=$(SKIP_ITERUN_CONFIRMATION)";
  step-10: run cmd=echo "";
}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  python_version: >=3.11;
}
```

## Interfaces

### CLI Entry Points

- `iterun`
- `iterun-mcp`

### testql Scenarios

#### `testql-scenarios/generated-api-integration.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-api-integration.testql.toon.yaml
# SCENARIO: API Integration Tests
# TYPE: api
# GENERATED: true

CONFIG[3]{key, value}:
  base_url, http://localhost:8101
  timeout_ms, 30000
  retry_count, 3

API[4]{method, endpoint, expected_status}:
  GET, /health, 200
  GET, /api/v1/status, 200
  POST, /api/v1/test, 201
  GET, /api/v1/docs, 200

ASSERT[2]{field, operator, expected}:
  status, ==, ok
  response_time, <, 1000
```

#### `testql-scenarios/generated-api-smoke.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-api-smoke.testql.toon.yaml
# SCENARIO: Auto-generated API Smoke Tests
# TYPE: api
# GENERATED: true
# DETECTORS: FastAPIDetector, TestEndpointDetector, ConfigEndpointDetector

CONFIG[5]{key, value}:
  base_url, http://localhost:8101
  timeout_ms, 10000
  retry_count, 3
  retry_backoff_ms, 1000
  detected_frameworks, FastAPIDetector, TestEndpointDetector, ConfigEndpointDetector

# Wait for service to be ready
WAIT 1000

# Health check
API GET /api/health 200
ASSERT_STATUS 200

# REST API Endpoints (1 unique)
API[1]{method, endpoint, expected_status}:
  GET, /, 200

# Capture useful values from responses for subsequent tests
# CAPTURE request_id FROM 'headers.x-request-id'
# CAPTURE session_token FROM 'body.token'

ASSERT[2]{field, operator, expected}:
  _status, <, 500
  _status, >=, 200

# Conditional flow for error handling
FLOW[2]{condition, action}:
  _status >= 500, LOG 'Server error detected'
  _status == 429, WAIT 2000  # Rate limit - wait and retry


# Summary by Framework:
#   fastapi: 1 endpoints
#   env: 2 endpoints
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# Converted 32 assertions from pytest
ASSERT[32]{field, operator, expected}:
  len(ir.implementation.actions), ==, 3
  ir.implementation.actions[0].type.value, ==, "api.expose"
  ir.implementation.actions[1].type.value, ==, "db.create"
  ir.implementation.actions[2].type.value, ==, "rest.call"
  len(ir.implementation.actions), ==, 3
  ir.implementation.actions[0].type.value, ==, "api.expose"
  ir.implementation.actions[1].type.value, ==, "db.create"
  ir.implementation.actions[2].type.value, ==, "rest.call"
  config.default_provider, ==, ModelProvider.OLLAMA
  config.default_model, ==, "llama3.2"
  config.ollama_base_url, ==, "http://localhost:11434"
  config.max_parameters_billions, ==, 12.0
  config.default_provider, ==, ModelProvider.OLLAMA
  config.default_model, ==, "llama3.2"
  config.ollama_base_url, ==, "http://localhost:11434"
  config.max_parameters_billions, ==, 12.0
  len(ir.implementation.actions), ==, 3
  ir.implementation.actions[0].type.value, ==, "api.expose"
  ir.implementation.actions[1].type.value, ==, "db.create"
  ir.implementation.actions[2].type.value, ==, "rest.call"
  len(ir.implementation.actions), ==, 3
  ir.implementation.actions[0].type.value, ==, "api.expose"
  ir.implementation.actions[1].type.value, ==, "db.create"
  ir.implementation.actions[2].type.value, ==, "rest.call"
  config.default_provider, ==, ModelProvider.OLLAMA
  config.default_model, ==, "llama3.2"
  config.ollama_base_url, ==, "http://localhost:11434"
  config.max_parameters_billions, ==, 12.0
  config.default_provider, ==, ModelProvider.OLLAMA
  config.default_model, ==, "llama3.2"
  config.ollama_base_url, ==, "http://localhost:11434"
  config.max_parameters_billions, ==, 12.0
```

## Workflows

## Quality Pipeline (`pyqual.yaml`)

```yaml markpact:pyqual path=pyqual.yaml
pipeline:
  name: iterun-quality

  metrics:
    cc_max: 15
    critical_max: 0

  custom_tools:
    - name: code2llm_iterun
      binary: code2llm
      command: >-
        code2llm {workdir} -f toon -o ./project --no-chunk
        --exclude .git .venv .venv_test build dist __pycache__ .pytest_cache .code2llm_cache .benchmarks .mypy_cache .ruff_cache node_modules
      output: ""
      allow_failure: false

    - name: vallm_iterun
      binary: vallm
      command: >-
        vallm batch {workdir} --recursive --format toon --output ./project
        --exclude .git,.venv,.venv_test,build,dist,__pycache__,.pytest_cache,.code2llm_cache,.benchmarks,.mypy_cache,.ruff_cache,node_modules
      output: ""
      allow_failure: false

  stages:
    - name: analyze
      tool: code2llm_iterun
      optional: true
      timeout: 0

    - name: validate
      tool: vallm_iterun
      optional: true
      timeout: 0

    - name: lint
      tool: ruff
      optional: true

    - name: fix
      tool: prefact
      optional: true
      when: metrics_fail
      timeout: 900

    - name: test
      run: python3 -m pytest -q
      when: always

  loop:
    max_iterations: 3
    on_fail: report

  env:
    LLM_MODEL: openrouter/qwen/qwen3-coder-next
```

## Configuration

```yaml
project:
  name: iterun
  version: 0.1.11
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
pyyaml>=6.0
pydantic>=2.0
fastapi>=0.109.0
uvicorn>=0.27.0
jinja2>=3.1.0
```

### Development

```text markpact:deps python scope=dev
pytest>=8.0.0
pytest-asyncio>=0.23.0
httpx>=0.26.0
anyio>=4.0.0
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Deployment

```bash markpact:run
pip install iterun

# development install
pip install -e .[dev]
```

### Requirements Files

#### `requirements.txt`

- `pyyaml>=6.0`
- `pydantic>=2.0`
- `fastapi>=0.109.0`
- `uvicorn>=0.27.0`
- `jinja2>=3.1.0`
- `litellm>=1.30.0`
- `pytest>=8.0.0`
- `pytest-asyncio>=0.23.0`
- `httpx>=0.26.0`
- `anyio>=4.0.0`
- `python-multipart>=0.0.6`

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | ============================================================================= |
| `PORT` | `8080` |  |
| `DEBUG` | `false` |  |
| `LOG_LEVEL` | `INFO` |  |
| `AI_ENABLED` | `true` | ============================================================================= |
| `OPENROUTER_API_KEY` | `sk-or-...` | OpenRouter (zalecane gdy masz klucz) — LLM_MODEL ma pierwszeństwo nad DEFAULT_MODEL |
| `LLM_MODEL` | `openrouter/deepseek/deepseek-v4-pro` |  |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama (lokalny fallback / suggest w shell) |
| `DEFAULT_MODEL` | `llama3.2` |  |
| `MAX_MODEL_PARAMS` | `12.0` |  |
| `OLLAMA_TIMEOUT` | `120` |  |
| `DOCKER_ENABLED` | `true` | ============================================================================= |
| `WORKSPACE_DIR` | `/tmp/iterun` |  |
| `AUTO_EXECUTE` | `true` |  |
| `SKIP_ITERUN_CONFIRMATION` | `true` |  |
| `CONTAINER_PORT` | `8000` | ============================================================================= |
| `CONTAINER_PREFIX` | `intent` |  |
| `VALIDATE_AFTER_EXECUTE` | `true` | Enable post-execution validation |
| `AUTO_FIX_ENABLED` | `true` | Enable automatic fixing if validation fails |
| `MAX_FIX_ITERATIONS` | `3` | Maximum auto-fix iterations |
| `STARTUP_WAIT` | `2` | Seconds to wait for container startup before validation |
| `VALIDATION_TIMEOUT` | `10` | Validation request timeout in seconds |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`iterun`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `venv/lib/python3.13/site-packages/cryptography/__init__.py:__version__`

## Makefile Targets

- `CYAN` — Colors
- `GREEN`
- `YELLOW`
- `RED`
- `RESET`
- `help`
- `install`
- `install-dev`
- `install-ai`
- `setup`
- `env`
- `run`
- `web`
- `shell`
- `plan`
- `execute`
- `examples`
- `run-intent` — Run with custom package file: make run-intent FILE=path/to/iterun.yaml
- `test`
- `test-shell`
- `test-web`
- `test-ai`
- `test-cov`
- `ollama-start`
- `ollama-pull`
- `ollama-models`
- `ollama-status`
- `lint`
- `format`
- `clean`
- `docker-clean`
- `docker-ps`
- `docker-stop`
- `dev`
- `new-intent`
- `show-config`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# iterun | 129f 12714L | python:98,shell:30,less:1 | 2026-06-06
# stats: 257 func | 100 cls | 129 mod | CC̄=4.5 | critical:20 | cycles:0
# alerts[5]: CC dispatch_command=14; CC execute_docker=13; CC validate_endpoints=13; CC build_stack_services=13; CC _dispatch_plan=12
# hotspots[5]: verify_contract fan=15; _dispatch_generate_yaml_only fan=13; discover_artifacts fan=13; dispatch_command fan=12; _finalize_pactown fan=12
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[129]:
  ai_gateway/__init__.py,31
  ai_gateway/feedback_loop.py,387
  ai_gateway/gateway.py,353
  ai_gateway/model_catalog.py,291
  app.doql.less,308
  cli/__init__.py,21
  cli/__main__.py,5
  cli/colors.py,17
  cli/dispatch.py,295
  cli/main.py,99
  cli/plan_artifacts.py,43
  cli/shell.py,481
  cli/shell_interactive.py,93
  cli/shell_output.py,98
  config.py,183
  contracts/__init__.py,11
  contracts/api_actions.py,36
  contracts/expectations.py,109
  dsl/__init__.py,18
  dsl/schema.py,243
  examples/01-user-api/run.sh,15
  examples/02-ping-smoke/run.sh,9
  examples/03-flask-api/run.sh,9
  examples/04-express-api/run.sh,9
  examples/05-ir-show/run.sh,10
  examples/06-iterate-workflow/run.sh,10
  examples/07-execution-smoke/run.sh,18
  examples/08-llm-generate/run.sh,14
  examples/09-e2e-ping-verify/run.sh,12
  examples/10-e2e-user-crud-verify/run.sh,11
  examples/11-e2e-express-verify/run.sh,11
  examples/12-e2e-full-gate/run.sh,42
  examples/13-resilience-vague/run.sh,23
  examples/14-resilience-inventory/run.sh,17
  examples/15-resilience-nested-paths/run.sh,17
  examples/16-resilience-framework-trap/run.sh,17
  examples/17-stack-shop-gateway/run-generate.sh,13
  examples/17-stack-shop-gateway/run.sh,24
  examples/18-stack-blog/run.sh,20
  examples/19-stack-api-cache/run.sh,19
  examples/_bootstrap_deps.sh,64
  examples/_common.sh,154
  examples/_scripts/annotate_intract.py,98
  examples/_scripts/intent_to_intract.py,30
  examples/_scripts/intent_to_openapi.py,77
  examples/_scripts/intent_to_testql.py,27
  examples/_scripts/verify_expectations.py,67
  examples/_verify.sh,166
  examples/run-all.sh,25
  examples/run-e2e.sh,25
  examples/run-resilience.sh,42
  examples/run-stacks.sh,31
  executor/__init__.py,2
  executor/docker_ops.py,284
  executor/models.py,76
  executor/pactown.py,227
  executor/runner.py,316
  executor/runtime_stop.py,23
  executor/validation.py,185
  generator/__init__.py,25
  generator/contract_verify.py,237
  generator/intent_generator.py,239
  generator/intract_manifest.py,93
  generator/pipeline.py,359
  generator/results.py,38
  generator/session.py,52
  generator/testql_scenario.py,80
  integrations/__init__.py,16
  integrations/adapters/__init__.py,15
  integrations/adapters/backstage.py,75
  integrations/adapters/base.py,30
  integrations/adapters/docker.py,91
  integrations/adapters/filesystem.py,18
  integrations/adapters/opentelemetry.py,29
  integrations/bridges/__init__.py,4
  integrations/bridges/pipeline.py,48
  integrations/markpact_pack.py,116
  integrations/pactown_config.py,71
  interfaces/__init__.py,6
  interfaces/models.py,53
  interfaces/service.py,262
  ir/__init__.py,10
  ir/models.py,299
  iterun_mcp/__init__.py,2
  iterun_mcp/server.py,146
  parser/__init__.py,4
  parser/dsl_parser.py,338
  planner/__init__.py,5
  planner/plan.py,16
  planner/simulator.py,378
  planner/stack_artifacts.py,67
  planner/stack_planner.py,235
  project.sh,59
  registry/__init__.py,14
  registry/catalog.py,72
  registry/discover.py,62
  registry/discover_artifacts.py,98
  registry/discover_context.py,78
  registry/discover_io.py,66
  registry/discover_services.py,97
  registry/labels.py,54
  registry/models.py,104
  run.sh,161
  sdk/__init__.py,6
  sdk/client.py,226
  tests/__init__.py,2
  tests/conftest.py,59
  tests/e2e/test_ai_gateway.py,389
  tests/e2e/test_contract_verify.py,43
  tests/e2e/test_executor_validation.py,21
  tests/e2e/test_expectations.py,68
  tests/e2e/test_intent_generator.py,109
  tests/e2e/test_intract_manifest.py,42
  tests/e2e/test_pipeline_repair.py,42
  tests/e2e/test_shell.py,403
  tests/e2e/test_stack_planner.py,90
  tests/e2e/test_testql_scenario.py,49
  tests/e2e/test_web.py,559
  tests/test_interfaces.py,107
  tests/test_pactown_config.py,51
  tests/test_registry.py,144
  tree.sh,2
  web/__init__.py,4
  web/app.py,66
  web/routes/__init__.py,2
  web/routes/ai.py,149
  web/routes/intents.py,281
  web/routes/registry.py,49
  web/schemas.py,68
D:
  ai_gateway/__init__.py:
  ai_gateway/feedback_loop.py:
    e: create_feedback_loop,analyze_intent,FeedbackSuggestion,FeedbackResult,FeedbackLoop
    FeedbackSuggestion: to_dict(0)  # A single improvement suggestion.
    FeedbackResult: to_dict(0)  # Result of feedback loop iteration.
    FeedbackLoop: __init__(2),analyze(2),apply_suggestions(3),iterate(4),_endpoint_paths(1),_suggest_health_endpoints(1),_suggest_workflow_steps(1),suggest_next_steps(1),_build_analysis_prompt(2),_parse_suggestions(1),_extract_action(1),_parse_action(1),_process_user_feedback(2)  # LLM-powered feedback loop for iterative intent refinement.
    create_feedback_loop(model)
    analyze_intent(ir;focus)
  ai_gateway/gateway.py:
    e: get_gateway,complete,suggest_improvements,AIGateway
    AIGateway: __init__(1),_setup_litellm(0),complete(5),acomplete(5),_mock_response(2),suggest_improvements(1),generate_code_snippet(3),explain_error(2),list_models(1),health_check(0)  # AI Gateway using LiteLLM for unified model access.
    get_gateway(config)
    complete(prompt)
    suggest_improvements(ir)
  ai_gateway/model_catalog.py:
    e: ModelProvider,ModelConfig,GatewayConfig
    ModelProvider:  # Supported model providers.
    ModelConfig: to_dict(0)  # Configuration for a specific model.
    GatewayConfig: _load_from_app_config(0),_load_from_env(0),_resolve_default_provider(0),__post_init__(0),resolve_model(1),litellm_model_id(1),get_available_models(1),get_model(1),to_dict(0)  # AI Gateway configuration.
  cli/__init__.py:
    e: __getattr__
    __getattr__(name)
  cli/__main__.py:
  cli/colors.py:
    e: Colors
    Colors: disable(1)
  cli/dispatch.py:
    e: dispatch_command,_dispatch_plan,_workspace_has_artifacts,_maybe_plan_before_execute,_print_execute_result,_dispatch_execute,_dispatch_parse,_dispatch_validate,_dispatch_generate,_print_generate_success,_print_generate_failure,_refresh_pipeline_registry,_dispatch_generate_pipeline,_dispatch_generate_yaml_only,_dispatch_registry
    dispatch_command(args;cli)
    _dispatch_plan(args;cli)
    _workspace_has_artifacts(ws)
    _maybe_plan_before_execute(args;cli;ir)
    _print_execute_result(args;cli;ir;result)
    _dispatch_execute(args;cli)
    _dispatch_parse(args;cli)
    _dispatch_validate(args;cli)
    _dispatch_generate(args;cli)
    _print_generate_success(args;cli;result;output_dir)
    _print_generate_failure(args;cli;result)
    _refresh_pipeline_registry(result)
    _dispatch_generate_pipeline(args;cli;prompt;output_dir;run_pipeline)
    _dispatch_generate_yaml_only(args;cli;prompt;output_dir)
    _dispatch_registry(args;cli)
  cli/main.py:
    e: build_parser,main
    build_parser()
    main()
  cli/plan_artifacts.py:
    e: write_plan_artifacts
    write_plan_artifacts(ir;result;output_dir)
  cli/shell.py:
    e: CLI
    CLI: __init__(2),print_header(1),print_success(1),print_error(1),print_warning(1),print_info(1),cmd_new(2),cmd_load(1),cmd_parse(1),cmd_plan(1),cmd_iterate(2),cmd_iterun(2),_skip_iterun_confirmation(0),_ensure_execute_approved(1),cmd_execute(4),cmd_show(2),cmd_save(2),interactive_mode(0),cmd_ai_suggest(2),cmd_ai_apply(1),cmd_ai_chat(2),cmd_models(1),cmd_ai_health(0),_show_help(0)  # Interactive CLI for iterun system.
  cli/shell_interactive.py:
    e: _dispatch_basic,_dispatch_ai,handle_interactive_line,build_prompt
    _dispatch_basic(cli;cmd;args)
    _dispatch_ai(cli;cmd;args;ai_available)
    handle_interactive_line(cli;line)
    build_prompt(cli)
  cli/shell_output.py:
    e: log_status_color,print_execution_logs,print_validation_success,print_execution_success,print_validation_errors,print_container_logs,print_execution_failure
    log_status_color(log)
    print_execution_logs(result)
    print_validation_success(result)
    print_execution_success(cli;result)
    print_validation_errors(result)
    print_container_logs(workspace;container_id)
    print_execution_failure(cli;result;workspace)
  config.py:
    e: _load_getv_profiles,_apply_env_pairs,_load_envstore,_parse_dotenv_lines,load_dotenv,get_env,get_env_bool,get_env_int,get_env_float,get_config,reload_config,configure,AppConfig
    AppConfig:  # Main application configuration.
    _load_getv_profiles()
    _apply_env_pairs(pairs)
    _load_envstore(env_path)
    _parse_dotenv_lines(env_path)
    load_dotenv(env_path)
    get_env(key;default)
    get_env_bool(key;default)
    get_env_int(key;default)
    get_env_float(key;default)
    get_config()
    reload_config()
    configure()
  contracts/__init__.py:
  contracts/api_actions.py:
    e: _parse_action_strings,parse_api_actions
    _parse_action_strings(actions)
    parse_api_actions(intent_data)
  contracts/expectations.py:
    e: _probe_path,_http_probe,_check_metadata,_check_declared_endpoints,_check_endpoint_response,_check_live_endpoint,check_expectations,load_and_check_expectations
    _probe_path(path)
    _http_probe(base_url;method;path)
    _check_metadata(intent_data;expectations)
    _check_declared_endpoints(intent_data;expectations)
    _check_endpoint_response(endpoint;data;path)
    _check_live_endpoint(base_url;endpoint)
    check_expectations(intent_data;expectations;base_url)
    load_and_check_expectations(workspace;intent_path;base_url)
  dsl/__init__.py:
  dsl/schema.py:
    e: get_json_schema,document_to_yaml,validate_yaml_document,get_system_prompt,IntentSection,EnvironmentSection,ImplementationSection,StackServiceSection,StackSection,ExecutionSection,IntentDSLDocument
    IntentSection: name_kebab(2)
    EnvironmentSection:
    ImplementationSection:
    StackServiceSection:
    StackSection:
    ExecutionSection:
    IntentDSLDocument: stack_services_named(2)  # Canonical structure for LLM-generated intent YAML.
    get_json_schema()
    document_to_yaml(doc)
    validate_yaml_document(yaml_content)
    get_system_prompt()
  examples/_scripts/annotate_intract.py:
    e: _slug,_actions,_comment,annotate_python,annotate_express,main
    _slug(path)
    _actions(intent_path)
    _comment(method;path)
    annotate_python(app_path;intent_path)
    annotate_express(app_path;intent_path)
    main()
  examples/_scripts/intent_to_intract.py:
    e: main
    main()
  examples/_scripts/intent_to_openapi.py:
    e: _slug,intent_to_openapi,main
    _slug(path)
    intent_to_openapi(intent_path)
    main()
  examples/_scripts/intent_to_testql.py:
    e: main
    main()
  examples/_scripts/verify_expectations.py:
    e: _load_yaml,_map_expectation_errors,verify,main
    _load_yaml(path)
    _map_expectation_errors(raw_errors)
    verify(expectations_path;intent_path;base_url)
    main()
  executor/__init__.py:
  executor/docker_ops.py:
    e: find_available_port,stop_containers_for_intent,get_container_logs,patch_compose_host_ports,execute_compose_stack,execute_docker
    find_available_port(start_port)
    stop_containers_for_intent(intent_name;prefix)
    get_container_logs(workspace;container_id;tail)
    patch_compose_host_ports(ir;compose_file;result)
    execute_compose_stack(ir;workspace;result)
    execute_docker(ir;workspace;result)
  executor/models.py:
    e: ExecutionError,ValidationResult,ExecutionResult
    ExecutionError:  # Raised when execution fails.
    ValidationResult: __init__(0),add_check(4),to_dict(0)  # Result of post-execution validation.
    ExecutionResult: __init__(0),add_log(1),to_dict(0)  # Result of intent execution.
  executor/pactown.py:
    e: _append_action_urls,_collect_stack_endpoints,_collect_single_endpoints,_collect_endpoints,_validate_urls,stop_pactown_for_intent,_prepare_pactown_workspace,_start_pactown_stack,_start_pactown_single,_finalize_pactown,execute_pactown
    _append_action_urls(endpoints;base;actions)
    _collect_stack_endpoints(ir;extra)
    _collect_single_endpoints(ir;base_url)
    _collect_endpoints(ir;base_url;extra)
    _validate_urls(endpoints;result;timeout)
    stop_pactown_for_intent(intent_name;workspace)
    _prepare_pactown_workspace(ir;ws;result)
    _start_pactown_stack(ws;ir;result)
    _start_pactown_single(ws;ir;result)
    _finalize_pactown(ir;ws;result;service_urls)
    execute_pactown(ir;workspace)
  executor/runner.py:
    e: execute_intent,Executor
    Executor: __init__(1),_check_iterun_boundary(3),_run_runtime(2),_finalize_success(1),execute(4),_validate_and_fix(3),_restart_container(2),_write_artifacts(2),_execute_local(2),get_container_logs(2),cleanup(0)  # Executes approved intents with validation and auto-fix.
    execute_intent(ir;workspace;skip_iterun_check;validate;auto_fix)
  executor/runtime_stop.py:
    e: stop_runtime_for_intent
    stop_runtime_for_intent(intent_name;workspace)
  executor/validation.py:
    e: filter_validation_endpoints,validate_endpoints,add_main_block,attempt_auto_fix
    filter_validation_endpoints(endpoints)
    validate_endpoints(endpoints;result)
    add_main_block(ir;container_port)
    attempt_auto_fix(ir;result;validation)
  generator/__init__.py:
  generator/contract_verify.py:
    e: _probe_path,discover_service_url,readiness_paths,_endpoint_responding,wait_for_service,_http_probe,run_testql,write_contract_artifacts,_run_testql_checks,_run_http_probes,_write_verify_result,verify_contract,VerifyResult
    VerifyResult: to_dict(0)
    _probe_path(path)
    discover_service_url(intent_name;fallback_endpoints)
    readiness_paths(intent_data)
    _endpoint_responding(base_url;path)
    wait_for_service(base_url;attempts;paths;intent_data)
    _http_probe(base_url;method;path)
    run_testql(scenario_path;base_url;timeout_ms)
    write_contract_artifacts(workspace;intent_path)
    _run_testql_checks(result;scenario;base_url)
    _run_http_probes(result;data;base_url)
    _write_verify_result(ws;result)
    verify_contract(workspace;intent_path)
  generator/intent_generator.py:
    e: extract_yaml_from_llm,_fallback_yaml,_build_user_prompt,GenerateAttempt,GenerateResult,IntentGenerator
    GenerateAttempt: to_dict(0)
    GenerateResult: to_dict(0)
    IntentGenerator: __init__(4),generate(1)  # Generate intent YAML via LiteLLM with validate-and-retry.
    extract_yaml_from_llm(content)
    _fallback_yaml(prompt)
    _build_user_prompt(user_prompt)
  generator/intract_manifest.py:
    e: _slug,_safe_id,build_intract_manifest,intent_to_intract_dict,write_intract_manifest
    _slug(path)
    _safe_id(name)
    build_intract_manifest(intent_data)
    intent_to_intract_dict(intent_path)
    write_intract_manifest(intent_path;output_path)
  generator/pipeline.py:
    e: _write_plan_artifacts,_expectations_summary,_build_repair_prompt,_container_logs,_finalize,_write_verify_round_log,_generate_and_plan,_finish_without_verify,_handle_verify_round,_handle_execute_error,_run_pipeline_round,run_pipeline
    _write_plan_artifacts(workspace;ir;plan_result)
    _expectations_summary(workspace)
    _build_repair_prompt(prompt;errors;workspace)
    _container_logs(workspace;container_id)
    _finalize(out;workspace)
    _write_verify_round_log(workspace;rounds)
    _generate_and_plan(out)
    _finish_without_verify(out;exec_result;workspace;container_id)
    _handle_verify_round(out)
    _handle_execute_error(out)
    _run_pipeline_round(out)
    run_pipeline(prompt)
  generator/results.py:
    e: PipelineResult
    PipelineResult: to_dict(0)
  generator/session.py:
    e: write_session_artifacts
    write_session_artifacts(workspace;result)
  generator/testql_scenario.py:
    e: _probe_path,_startup_wait_ms,build_testql_scenario,write_testql_scenario
    _probe_path(path)
    _startup_wait_ms(intent_data)
    build_testql_scenario(intent_data)
    write_testql_scenario(intent_path;output_path)
  integrations/__init__.py:
  integrations/adapters/__init__.py:
  integrations/adapters/backstage.py:
    e: BackstageExporter
    BackstageExporter: export(2)  # Export iterun services as Backstage Component entities.
  integrations/adapters/base.py:
    e: RegistryAdapter,RegistryExporter
    RegistryAdapter: collect(1),enrich(2)  # Collect or export registry data from an external system.
    RegistryExporter: export(2)  # Export registry to industry-standard formats.
  integrations/adapters/docker.py:
    e: _match_service_containers,_apply_container_to_service,_running_iterun_containers,DockerAdapter
    DockerAdapter: collect(1),enrich(2),_merge_container_state(2)  # Merge docker ps / compose state into registry manifest.
    _match_service_containers(name;intent;running)
    _apply_container_to_service(svc;container)
    _running_iterun_containers()
  integrations/adapters/filesystem.py:
    e: FilesystemAdapter
    FilesystemAdapter: collect(1)  # Discover artifacts and services from iterun workspace files.
  integrations/adapters/opentelemetry.py:
    e: OpenTelemetryExporter
    OpenTelemetryExporter: export(2)  # Write OTel resource descriptors for generated services.
  integrations/bridges/__init__.py:
  integrations/bridges/pipeline.py:
    e: refresh_registry,refresh_registry_from_pipeline
    refresh_registry(workspace)
    refresh_registry_from_pipeline(workspace;result)
  integrations/markpact_pack.py:
    e: _run_command_for_ir,_service_run_command,_pack_service_readmes,pack_workspace
    _run_command_for_ir(ir)
    _service_run_command(svc)
    _pack_service_readmes(ws;ir;title;pack_directory)
    pack_workspace(workspace;ir)
  integrations/pactown_config.py:
    e: _health_path,build_pactown_config,write_pactown_config
    _health_path(svc)
    build_pactown_config(ir;workspace)
    write_pactown_config(ir;workspace)
  interfaces/__init__.py:
  interfaces/models.py:
    e: ValidateYAMLRequest,GenerateRequest,PipelineRequest,PlanYAMLRequest,ParseRequest,ExecuteRequest,InterfacesInfo
    ValidateYAMLRequest:
    GenerateRequest:
    PipelineRequest:
    PlanYAMLRequest:
    ParseRequest:
    ExecuteRequest:
    InterfacesInfo:  # Available integration surfaces.
  interfaces/service.py:
    e: _write_plan_output,IterunService
    IterunService: __init__(0),interfaces_info(0),schema(0),validate_yaml(1),parse(1),generate(1),run_pipeline(1),plan_ir(1),plan_yaml(1),execute_ir(1),registry_refresh(1),registry_get(1),registry_list(1)  # Single entry point for programmatic access to ITERUN.
    _write_plan_output(ir;result;output_dir)
  ir/__init__.py:
  ir/models.py:
    e: ExecutionMode,RuntimeType,ActionType,Action,Environment,Implementation,StackService,Stack,Intent,IntentIR
    ExecutionMode:
    RuntimeType:
    ActionType:
    Action: to_dict(0),from_dict(2)  # Single action in the implementation plan.
    Environment: to_dict(0),from_dict(2)  # Runtime environment configuration.
    Implementation: to_dict(0),from_dict(2)  # Implementation details.
    StackService: to_dict(0),from_dict(2)  # Single service inside a multi-container STACK application.
    Stack: to_dict(0),from_dict(2)  # Multi-service application (docker compose).
    Intent: to_dict(0),from_dict(2)  # Main intent definition.
    IntentIR: to_dict(0),to_json(1),from_dict(2),from_json(2),add_iteration(2),approve_iterun(0)  # Complete Intermediate Representation for an intent.
  iterun_mcp/__init__.py:
  iterun_mcp/server.py:
  parser/__init__.py:
  parser/dsl_parser.py:
    e: parse_dsl,parse_dsl_file,ParseError,ValidationError,DSLParser
    ParseError: __init__(2)  # Raised when DSL parsing fails.
    ValidationError: __init__(1)  # Raised when DSL validation fails.
    DSLParser: __init__(0),parse_file(1),parse(1),_parse_intent(1),_parse_environment(1),_parse_implementation(1),_parse_action(1),_parse_stack(1),_parse_execution(1),_validate_stack_services(1),_validate_actions_required(1),_validate_dangerous_actions(1),_validate_framework_compat(1),_validate(1)  # Parser for ITERUN DSL format.
    parse_dsl(content)
    parse_dsl_file(filepath)
  planner/__init__.py:
  planner/plan.py:
    e: plan_intent
    plan_intent(ir)
  planner/simulator.py:
    e: _endpoint_to_func_name,DryRunResult,Planner
    DryRunResult: __init__(0),add_log(1),to_dict(0)  # Result of a dry-run simulation.
    Planner: __init__(0),dry_run(1),_generate_python_code(1),_generate_fastapi_code(1),_generate_flask_code(1),_generate_basic_python_code(1),_generate_node_code(1),_generate_express_code(1),_generate_basic_node_code(1),_generate_dockerfile(1),_simulate_action(2),_estimate_resources(1)  # Plans and simulates intent execution.
    _endpoint_to_func_name(endpoint;method;used)
  planner/stack_artifacts.py:
    e: write_stack_artifacts
    write_stack_artifacts(workspace;ir;plan_result)
  planner/stack_planner.py:
    e: _service_ir,_gateway_proxy_code,_resolve_upstream,_build_compose,_plan_prebuilt_service,_plan_generated_service,plan_stack
    _service_ir(parent;svc)
    _gateway_proxy_code(svc;upstreams)
    _resolve_upstream(path;gateway;services)
    _build_compose(parent;artifacts)
    _plan_prebuilt_service(result;svc)
    _plan_generated_service(result;ir;svc;svc_map;planner)
    plan_stack(ir)
  registry/__init__.py:
  registry/catalog.py:
    e: discover_glob,RegistryCatalog
    RegistryCatalog: __init__(1),registry_path(0),discover(0),load(0),refresh(0),write(1),summary(0)  # Workspace-scoped service and artifact registry.
    discover_glob(pattern)
  registry/discover.py:
    e: _build_services,discover_workspace
    _build_services(ctx)
    discover_workspace(workspace)
  registry/discover_artifacts.py:
    e: sha256_file,discover_artifacts
    sha256_file(path)
    discover_artifacts(workspace)
  registry/discover_context.py:
    e: _intent_identity,_stack_metadata,_workspace_prompt,load_workspace_context,WorkspaceContext
    WorkspaceContext:
    _intent_identity(ws;intent_doc;session)
    _stack_metadata(intent_doc;ws)
    _workspace_prompt(ws;session)
    load_workspace_context(workspace)
  registry/discover_io.py:
    e: load_session,load_stack_urls,intent_from_workspace,phase_from_session
    load_session(workspace)
    load_stack_urls(workspace)
    intent_from_workspace(workspace)
    phase_from_session(session)
  registry/discover_services.py:
    e: build_stack_services,build_single_service
    build_stack_services()
    build_single_service()
  registry/labels.py:
    e: build_service_labels,build_otel_resource
    build_service_labels(intent_name;service_name)
    build_otel_resource(intent_name;service_name)
  registry/models.py:
    e: DeploymentKind,LifecyclePhase,ArtifactRole,ArtifactRecord,ServiceRecord,RegistryMetadata,RegistryStatus,RegistryManifest
    DeploymentKind:
    LifecyclePhase:
    ArtifactRole:
    ArtifactRecord:  # Tracked file or logical artifact (aligns with SPDX/CycloneDX
    ServiceRecord:  # Runnable unit — maps to Backstage Component + OTel service.n
    RegistryMetadata:
    RegistryStatus:
    RegistryManifest: to_dict(0)  # Canonical iterun registry document (JSON, machine-readable).
  sdk/__init__.py:
  sdk/client.py:
    e: IterunClient
    IterunClient: __init__(4),health(0),interfaces(0),schema(0),validate(1),generate(1),run_pipeline(1),generate_and_run(1),plan_yaml(1),registry_get(1),registry_refresh(1),registry_list(1),parse(1),_post_json(2),_remote_generate(1),_remote_pipeline(6)  # Local SDK (in-process) or remote via REST base_url.
  tests/__init__.py:
  tests/conftest.py:
    e: project_root,sample_dsl,sample_ir
    project_root()
    sample_dsl()
    sample_ir()
  tests/e2e/test_ai_gateway.py:
    e: run_tests,TestModelConfig,TestGatewayConfig,TestAIGateway,TestFeedbackLoop,TestFeedbackSuggestion,TestConvenienceFunctions
    TestModelConfig: test_ollama_models_exist(0),test_model_config_properties(0),test_models_under_12b(0)  # Test model configuration.
    TestGatewayConfig: test_default_config(1),test_resolve_model_prefers_llm_model(1),test_config_from_env(0),test_get_model(0)  # Test gateway configuration.
    TestAIGateway: test_gateway_creation(0),test_mock_response_when_litellm_unavailable(0),test_list_models(0),test_health_check(0),test_complete_without_litellm(0)  # Test AI Gateway functionality.
    TestFeedbackLoop: sample_ir(0),test_feedback_loop_creation(0),test_suggest_next_steps(1),test_suggest_next_steps_with_health(1),test_build_analysis_prompt(1),test_parse_suggestions_json(0),test_parse_suggestions_raw(0),test_extract_action(0),test_feedback_result_to_dict(0)  # Test feedback loop functionality.
    TestFeedbackSuggestion: test_suggestion_defaults(0),test_suggestion_to_dict(0)  # Test FeedbackSuggestion dataclass.
    TestConvenienceFunctions: test_get_gateway_singleton(0),test_complete_function(0)  # Test convenience functions.
    run_tests()
  tests/e2e/test_contract_verify.py:
    e: test_readiness_paths_from_intent,test_wait_for_service_accepts_http_404_as_up,test_wait_for_service_default_includes_live_ready
    test_readiness_paths_from_intent()
    test_wait_for_service_accepts_http_404_as_up()
    test_wait_for_service_default_includes_live_ready()
  tests/e2e/test_executor_validation.py:
    e: test_filter_validation_endpoints_skips_bare_root_when_routes_exist,test_filter_validation_endpoints_keeps_root_when_only_base
    test_filter_validation_endpoints_skips_bare_root_when_routes_exist()
    test_filter_validation_endpoints_keeps_root_when_only_base()
  tests/e2e/test_expectations.py:
    e: test_check_expectations_missing_endpoints,test_check_expectations_framework_mismatch,test_check_expectations_body_contains
    test_check_expectations_missing_endpoints()
    test_check_expectations_framework_mismatch()
    test_check_expectations_body_contains()
  tests/e2e/test_intent_generator.py:
    e: TestSchema,TestExtractYaml,TestIntentGenerator,TestPipeline
    TestSchema: test_json_schema_has_intent(0),test_example_yaml_valid(0),test_invalid_yaml_rejected(0)
    TestExtractYaml: test_strips_fences(0),test_plain_yaml(0)
    TestIntentGenerator: test_generate_success_mock(0),test_retry_on_invalid_llm_output(0),test_fails_after_max_iterations(0)
    TestPipeline: test_pipeline_generate_only(1)
  tests/e2e/test_intract_manifest.py:
    e: test_build_intract_manifest_require_list,test_write_intract_manifest
    test_build_intract_manifest_require_list()
    test_write_intract_manifest(tmp_path)
  tests/e2e/test_pipeline_repair.py:
    e: test_expectations_summary_lists_endpoints,test_build_repair_prompt_includes_expectations
    test_expectations_summary_lists_endpoints(tmp_path)
    test_build_repair_prompt_includes_expectations(tmp_path)
  tests/e2e/test_shell.py:
    e: run_tests,TestDSLParser,TestPlanner,TestCLI,TestIRModel,TestEndToEnd
    TestDSLParser: test_parse_valid_dsl(0),test_parse_missing_intent(0),test_parse_invalid_yaml(0),test_parse_multiple_actions(0),test_parse_action_formats(0)  # Test DSL parsing functionality.
    TestPlanner: test_dry_run_fastapi(0),test_dry_run_fastapi_path_params(0),test_dry_run_express(0),test_resource_estimation(0)  # Test planner/simulator functionality.
    TestCLI: test_cli_new_intent(0),test_cli_plan(0),test_cli_iterate(0),test_cli_iterun_not_approved_without_confirmation(0)  # Test CLI functionality.
    TestIRModel: test_ir_serialization(0),test_ir_iteration_history(0),test_ir_iterun_approval(0)  # Test IR model functionality.
    TestEndToEnd: test_complete_workflow_dry_run(0),test_file_based_workflow(0)  # End-to-end workflow tests.
    run_tests()
  tests/e2e/test_stack_planner.py:
    e: test_parse_stack_ir,test_plan_stack_compose_and_services,test_write_stack_artifacts,test_intract_parse_stack_actions
    test_parse_stack_ir()
    test_plan_stack_compose_and_services()
    test_write_stack_artifacts(tmp_path)
    test_intract_parse_stack_actions()
  tests/e2e/test_testql_scenario.py:
    e: test_build_testql_contains_endpoints,test_build_testql_express_longer_wait,test_write_testql_scenario
    test_build_testql_contains_endpoints()
    test_build_testql_express_longer_wait()
    test_write_testql_scenario(tmp_path)
  tests/e2e/test_web.py:
    e: anyio_backend,client,run_tests,TestHealthEndpoint,TestIntentsCRUD,TestPlanningEndpoint,TestIterationEndpoint,TestiterunAndExecution,TestGeneratedCodeEndpoint,TestEndToEndWorkflow,TestHomePage
    TestHealthEndpoint: test_health_check(1)  # Test health check endpoint.
    TestIntentsCRUD: test_list_intents_empty(1),test_parse_valid_dsl(1),test_parse_invalid_dsl(1),test_parse_missing_intent_section(1),test_get_intent(1),test_get_nonexistent_intent(1),test_delete_intent(1)  # Test intents CRUD operations.
    TestPlanningEndpoint: test_plan_intent(1),test_plan_express(1)  # Test dry-run planning endpoint.
    TestIterationEndpoint: test_iterate_add_action(1),test_iterate_change_framework(1),test_multiple_iterations(1)  # Test iteration endpoint.
    TestiterunAndExecution: test_iterun_approval(1),test_execute_without_iterun(1)  # Test ITERUN approval and execution endpoints.
    TestGeneratedCodeEndpoint: test_get_generated_code(1)  # Test generated code endpoint.
    TestEndToEndWorkflow: test_complete_workflow(1)  # Complete end-to-end workflow tests.
    TestHomePage: test_home_page_renders(1)  # Test home page rendering.
    anyio_backend()
    client()
    run_tests()
  tests/test_interfaces.py:
    e: test_interfaces_info_lists_surfaces,test_validate_yaml_detects_stack,test_plan_yaml_stack_compose,test_plan_yaml_single_service,test_sdk_local_interfaces_and_plan,test_rest_health_and_interfaces
    test_interfaces_info_lists_surfaces()
    test_validate_yaml_detects_stack()
    test_plan_yaml_stack_compose(tmp_path)
    test_plan_yaml_single_service(tmp_path)
    test_sdk_local_interfaces_and_plan()
    test_rest_health_and_interfaces()
  tests/test_pactown_config.py:
    e: test_build_pactown_config_stack,test_write_pactown_config
    test_build_pactown_config_stack()
    test_write_pactown_config(tmp_path)
  tests/test_registry.py:
    e: _seed_workspace,test_discover_single_service,test_discover_stack,test_refresh_registry_exports,test_backstage_exporter,test_otel_exporter,test_catalog_refresh,test_rest_registry_endpoints
    _seed_workspace(tmp_path;yaml_content)
    test_discover_single_service(tmp_path)
    test_discover_stack(tmp_path)
    test_refresh_registry_exports(tmp_path)
    test_backstage_exporter(tmp_path)
    test_otel_exporter(tmp_path)
    test_catalog_refresh(tmp_path)
    test_rest_registry_endpoints(tmp_path)
  web/__init__.py:
  web/app.py:
    e: home,create_app
    home(request)
    create_app()
  web/routes/__init__.py:
  web/routes/ai.py:
    e: _intents_store,health,ai_status,list_models,ai_complete,ai_chat,ai_suggest,ai_apply_suggestions,generate_code
    _intents_store()
    health()
    ai_status()
    list_models(max_params)
    ai_complete(request)
    ai_chat(request)
    ai_suggest(intent_id;request)
    ai_apply_suggestions(intent_id)
    generate_code(description;language;framework)
  web/routes/intents.py:
    e: _get_service,_intents_store,get_schema,validate_yaml,generate_intent_api,run_pipeline_api,generate_and_run_api,plan_yaml_api,parse_intent,list_intents,get_intent,delete_intent,plan,iterate,approve_iterun,execute,validate_intent,container_logs,get_generated_code
    _get_service()
    _intents_store()
    get_schema()
    validate_yaml(data)
    generate_intent_api(data)
    run_pipeline_api(data)
    generate_and_run_api(data)
    plan_yaml_api(data)
    parse_intent(data)
    list_intents()
    get_intent(intent_id)
    delete_intent(intent_id)
    plan(intent_id)
    iterate(intent_id;data)
    approve_iterun(intent_id)
    execute(intent_id;data;validate;auto_fix)
    validate_intent(intent_id)
    container_logs(container_id;tail;workspace)
    get_generated_code(intent_id)
  web/routes/registry.py:
    e: _get_service,health,list_interfaces,get_registry,refresh_registry_api,list_registries
    _get_service()
    health()
    list_interfaces()
    get_registry(workspace)
    refresh_registry_api(data)
    list_registries(pattern)
  web/schemas.py:
    e: DSLInput,IterationInput,ExecutionRequest,GenerateRequest,GenerateAndRunRequest,PlanYAMLRequest,RegistryRefreshRequest,ValidateYAMLRequest,AICompletionRequest,AISuggestRequest,AIChatRequest
    DSLInput:
    IterationInput:
    ExecutionRequest:
    GenerateRequest:
    GenerateAndRunRequest:
    PlanYAMLRequest:
    RegistryRefreshRequest:
    ValidateYAMLRequest:
    AICompletionRequest:
    AISuggestRequest:
    AIChatRequest:
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('iterun', '0.1.11', 'python').

% ── Project Files ────────────────────────────────────────
project_file('ai_gateway/__init__.py', 31, 'python').
project_file('ai_gateway/feedback_loop.py', 387, 'python').
project_file('ai_gateway/gateway.py', 353, 'python').
project_file('ai_gateway/model_catalog.py', 291, 'python').
project_file('app.doql.less', 308, 'less').
project_file('cli/__init__.py', 21, 'python').
project_file('cli/__main__.py', 5, 'python').
project_file('cli/colors.py', 17, 'python').
project_file('cli/dispatch.py', 295, 'python').
project_file('cli/main.py', 99, 'python').
project_file('cli/plan_artifacts.py', 43, 'python').
project_file('cli/shell.py', 481, 'python').
project_file('cli/shell_interactive.py', 93, 'python').
project_file('cli/shell_output.py', 98, 'python').
project_file('config.py', 183, 'python').
project_file('contracts/__init__.py', 11, 'python').
project_file('contracts/api_actions.py', 36, 'python').
project_file('contracts/expectations.py', 109, 'python').
project_file('dsl/__init__.py', 18, 'python').
project_file('dsl/schema.py', 243, 'python').
project_file('examples/01-user-api/run.sh', 15, 'shell').
project_file('examples/02-ping-smoke/run.sh', 9, 'shell').
project_file('examples/03-flask-api/run.sh', 9, 'shell').
project_file('examples/04-express-api/run.sh', 9, 'shell').
project_file('examples/05-ir-show/run.sh', 10, 'shell').
project_file('examples/06-iterate-workflow/run.sh', 10, 'shell').
project_file('examples/07-execution-smoke/run.sh', 18, 'shell').
project_file('examples/08-llm-generate/run.sh', 14, 'shell').
project_file('examples/09-e2e-ping-verify/run.sh', 12, 'shell').
project_file('examples/10-e2e-user-crud-verify/run.sh', 11, 'shell').
project_file('examples/11-e2e-express-verify/run.sh', 11, 'shell').
project_file('examples/12-e2e-full-gate/run.sh', 42, 'shell').
project_file('examples/13-resilience-vague/run.sh', 23, 'shell').
project_file('examples/14-resilience-inventory/run.sh', 17, 'shell').
project_file('examples/15-resilience-nested-paths/run.sh', 17, 'shell').
project_file('examples/16-resilience-framework-trap/run.sh', 17, 'shell').
project_file('examples/17-stack-shop-gateway/run-generate.sh', 13, 'shell').
project_file('examples/17-stack-shop-gateway/run.sh', 24, 'shell').
project_file('examples/18-stack-blog/run.sh', 20, 'shell').
project_file('examples/19-stack-api-cache/run.sh', 19, 'shell').
project_file('examples/_bootstrap_deps.sh', 64, 'shell').
project_file('examples/_common.sh', 154, 'shell').
project_file('examples/_scripts/annotate_intract.py', 98, 'python').
project_file('examples/_scripts/intent_to_intract.py', 30, 'python').
project_file('examples/_scripts/intent_to_openapi.py', 77, 'python').
project_file('examples/_scripts/intent_to_testql.py', 27, 'python').
project_file('examples/_scripts/verify_expectations.py', 67, 'python').
project_file('examples/_verify.sh', 166, 'shell').
project_file('examples/run-all.sh', 25, 'shell').
project_file('examples/run-e2e.sh', 25, 'shell').
project_file('examples/run-resilience.sh', 42, 'shell').
project_file('examples/run-stacks.sh', 31, 'shell').
project_file('executor/__init__.py', 2, 'python').
project_file('executor/docker_ops.py', 284, 'python').
project_file('executor/models.py', 76, 'python').
project_file('executor/pactown.py', 227, 'python').
project_file('executor/runner.py', 316, 'python').
project_file('executor/runtime_stop.py', 23, 'python').
project_file('executor/validation.py', 185, 'python').
project_file('generator/__init__.py', 25, 'python').
project_file('generator/contract_verify.py', 237, 'python').
project_file('generator/intent_generator.py', 239, 'python').
project_file('generator/intract_manifest.py', 93, 'python').
project_file('generator/pipeline.py', 359, 'python').
project_file('generator/results.py', 38, 'python').
project_file('generator/session.py', 52, 'python').
project_file('generator/testql_scenario.py', 80, 'python').
project_file('integrations/__init__.py', 16, 'python').
project_file('integrations/adapters/__init__.py', 15, 'python').
project_file('integrations/adapters/backstage.py', 75, 'python').
project_file('integrations/adapters/base.py', 30, 'python').
project_file('integrations/adapters/docker.py', 91, 'python').
project_file('integrations/adapters/filesystem.py', 18, 'python').
project_file('integrations/adapters/opentelemetry.py', 29, 'python').
project_file('integrations/bridges/__init__.py', 4, 'python').
project_file('integrations/bridges/pipeline.py', 48, 'python').
project_file('integrations/markpact_pack.py', 116, 'python').
project_file('integrations/pactown_config.py', 71, 'python').
project_file('interfaces/__init__.py', 6, 'python').
project_file('interfaces/models.py', 53, 'python').
project_file('interfaces/service.py', 262, 'python').
project_file('ir/__init__.py', 10, 'python').
project_file('ir/models.py', 299, 'python').
project_file('iterun_mcp/__init__.py', 2, 'python').
project_file('iterun_mcp/server.py', 146, 'python').
project_file('parser/__init__.py', 4, 'python').
project_file('parser/dsl_parser.py', 338, 'python').
project_file('planner/__init__.py', 5, 'python').
project_file('planner/plan.py', 16, 'python').
project_file('planner/simulator.py', 378, 'python').
project_file('planner/stack_artifacts.py', 67, 'python').
project_file('planner/stack_planner.py', 235, 'python').
project_file('project.sh', 59, 'shell').
project_file('registry/__init__.py', 14, 'python').
project_file('registry/catalog.py', 72, 'python').
project_file('registry/discover.py', 62, 'python').
project_file('registry/discover_artifacts.py', 98, 'python').
project_file('registry/discover_context.py', 78, 'python').
project_file('registry/discover_io.py', 66, 'python').
project_file('registry/discover_services.py', 97, 'python').
project_file('registry/labels.py', 54, 'python').
project_file('registry/models.py', 104, 'python').
project_file('run.sh', 161, 'shell').
project_file('sdk/__init__.py', 6, 'python').
project_file('sdk/client.py', 226, 'python').
project_file('tests/__init__.py', 2, 'python').
project_file('tests/conftest.py', 59, 'python').
project_file('tests/e2e/test_ai_gateway.py', 389, 'python').
project_file('tests/e2e/test_contract_verify.py', 43, 'python').
project_file('tests/e2e/test_executor_validation.py', 21, 'python').
project_file('tests/e2e/test_expectations.py', 68, 'python').
project_file('tests/e2e/test_intent_generator.py', 109, 'python').
project_file('tests/e2e/test_intract_manifest.py', 42, 'python').
project_file('tests/e2e/test_pipeline_repair.py', 42, 'python').
project_file('tests/e2e/test_shell.py', 403, 'python').
project_file('tests/e2e/test_stack_planner.py', 90, 'python').
project_file('tests/e2e/test_testql_scenario.py', 49, 'python').
project_file('tests/e2e/test_web.py', 559, 'python').
project_file('tests/test_interfaces.py', 107, 'python').
project_file('tests/test_pactown_config.py', 51, 'python').
project_file('tests/test_registry.py', 144, 'python').
project_file('tree.sh', 2, 'shell').
project_file('web/__init__.py', 4, 'python').
project_file('web/app.py', 66, 'python').
project_file('web/routes/__init__.py', 2, 'python').
project_file('web/routes/ai.py', 149, 'python').
project_file('web/routes/intents.py', 281, 'python').
project_file('web/routes/registry.py', 49, 'python').
project_file('web/schemas.py', 68, 'python').

% ── Python Functions ─────────────────────────────────────
python_function('ai_gateway/feedback_loop.py', 'create_feedback_loop', 1, 1, 1).
python_function('ai_gateway/feedback_loop.py', 'analyze_intent', 2, 1, 2).
python_function('ai_gateway/gateway.py', 'get_gateway', 1, 3, 1).
python_function('ai_gateway/gateway.py', 'complete', 1, 9, 2).
python_function('ai_gateway/gateway.py', 'suggest_improvements', 1, 8, 2).
python_function('cli/__init__.py', '__getattr__', 1, 3, 1).
python_function('cli/dispatch.py', 'dispatch_command', 2, 14, 12).
python_function('cli/dispatch.py', '_dispatch_plan', 2, 12, 10).
python_function('cli/dispatch.py', '_workspace_has_artifacts', 1, 3, 2).
python_function('cli/dispatch.py', '_maybe_plan_before_execute', 3, 6, 4).
python_function('cli/dispatch.py', '_print_execute_result', 4, 8, 3).
python_function('cli/dispatch.py', '_dispatch_execute', 2, 3, 7).
python_function('cli/dispatch.py', '_dispatch_parse', 2, 10, 11).
python_function('cli/dispatch.py', '_dispatch_validate', 2, 6, 8).
python_function('cli/dispatch.py', '_dispatch_generate', 2, 8, 4).
python_function('cli/dispatch.py', '_print_generate_success', 4, 8, 6).
python_function('cli/dispatch.py', '_print_generate_failure', 3, 7, 2).
python_function('cli/dispatch.py', '_refresh_pipeline_registry', 1, 3, 1).
python_function('cli/dispatch.py', '_dispatch_generate_pipeline', 5, 2, 5).
python_function('cli/dispatch.py', '_dispatch_generate_yaml_only', 4, 6, 13).
python_function('cli/dispatch.py', '_dispatch_registry', 2, 10, 7).
python_function('cli/main.py', 'build_parser', 0, 1, 2).
python_function('cli/main.py', 'main', 0, 2, 5).
python_function('cli/plan_artifacts.py', 'write_plan_artifacts', 3, 7, 7).
python_function('cli/shell_interactive.py', '_dispatch_basic', 3, 12, 10).
python_function('cli/shell_interactive.py', '_dispatch_ai', 4, 10, 6).
python_function('cli/shell_interactive.py', 'handle_interactive_line', 2, 6, 7).
python_function('cli/shell_interactive.py', 'build_prompt', 1, 2, 0).
python_function('cli/shell_output.py', 'log_status_color', 1, 8, 1).
python_function('cli/shell_output.py', 'print_execution_logs', 1, 2, 2).
python_function('cli/shell_output.py', 'print_validation_success', 1, 4, 2).
python_function('cli/shell_output.py', 'print_execution_success', 2, 8, 4).
python_function('cli/shell_output.py', 'print_validation_errors', 1, 6, 1).
python_function('cli/shell_output.py', 'print_container_logs', 2, 7, 6).
python_function('cli/shell_output.py', 'print_execution_failure', 3, 2, 3).
python_function('config.py', '_load_getv_profiles', 0, 5, 3).
python_function('config.py', '_apply_env_pairs', 1, 3, 0).
python_function('config.py', '_load_envstore', 1, 1, 4).
python_function('config.py', '_parse_dotenv_lines', 1, 5, 5).
python_function('config.py', 'load_dotenv', 1, 4, 6).
python_function('config.py', 'get_env', 2, 1, 1).
python_function('config.py', 'get_env_bool', 2, 1, 3).
python_function('config.py', 'get_env_int', 2, 2, 3).
python_function('config.py', 'get_env_float', 2, 2, 3).
python_function('config.py', 'get_config', 0, 2, 1).
python_function('config.py', 'reload_config', 0, 1, 2).
python_function('config.py', 'configure', 0, 1, 1).
python_function('contracts/api_actions.py', '_parse_action_strings', 1, 4, 6).
python_function('contracts/api_actions.py', 'parse_api_actions', 1, 9, 5).
python_function('contracts/expectations.py', '_probe_path', 1, 1, 1).
python_function('contracts/expectations.py', '_http_probe', 3, 3, 7).
python_function('contracts/expectations.py', '_check_metadata', 2, 7, 2).
python_function('contracts/expectations.py', '_check_declared_endpoints', 2, 5, 4).
python_function('contracts/expectations.py', '_check_endpoint_response', 3, 7, 3).
python_function('contracts/expectations.py', '_check_live_endpoint', 2, 4, 7).
python_function('contracts/expectations.py', 'check_expectations', 3, 4, 5).
python_function('contracts/expectations.py', 'load_and_check_expectations', 3, 4, 5).
python_function('dsl/schema.py', 'get_json_schema', 0, 1, 1).
python_function('dsl/schema.py', 'document_to_yaml', 1, 1, 2).
python_function('dsl/schema.py', 'validate_yaml_document', 1, 8, 4).
python_function('dsl/schema.py', 'get_system_prompt', 0, 1, 2).
python_function('examples/_scripts/annotate_intract.py', '_slug', 1, 2, 3).
python_function('examples/_scripts/annotate_intract.py', '_actions', 1, 7, 9).
python_function('examples/_scripts/annotate_intract.py', '_comment', 2, 1, 1).
python_function('examples/_scripts/annotate_intract.py', 'annotate_python', 2, 5, 10).
python_function('examples/_scripts/annotate_intract.py', 'annotate_express', 2, 6, 11).
python_function('examples/_scripts/annotate_intract.py', 'main', 0, 3, 7).
python_function('examples/_scripts/intent_to_intract.py', 'main', 0, 3, 7).
python_function('examples/_scripts/intent_to_openapi.py', '_slug', 1, 2, 3).
python_function('examples/_scripts/intent_to_openapi.py', 'intent_to_openapi', 1, 8, 11).
python_function('examples/_scripts/intent_to_openapi.py', 'main', 0, 1, 8).
python_function('examples/_scripts/intent_to_testql.py', 'main', 0, 1, 5).
python_function('examples/_scripts/verify_expectations.py', '_load_yaml', 1, 2, 2).
python_function('examples/_scripts/verify_expectations.py', '_map_expectation_errors', 1, 8, 3).
python_function('examples/_scripts/verify_expectations.py', 'verify', 3, 1, 3).
python_function('examples/_scripts/verify_expectations.py', 'main', 0, 3, 6).
python_function('executor/docker_ops.py', 'find_available_port', 1, 3, 3).
python_function('executor/docker_ops.py', 'stop_containers_for_intent', 2, 5, 5).
python_function('executor/docker_ops.py', 'get_container_logs', 3, 7, 6).
python_function('executor/docker_ops.py', 'patch_compose_host_ports', 3, 7, 7).
python_function('executor/docker_ops.py', 'execute_compose_stack', 3, 9, 6).
python_function('executor/docker_ops.py', 'execute_docker', 3, 13, 11).
python_function('executor/pactown.py', '_append_action_urls', 3, 5, 2).
python_function('executor/pactown.py', '_collect_stack_endpoints', 2, 8, 2).
python_function('executor/pactown.py', '_collect_single_endpoints', 2, 1, 1).
python_function('executor/pactown.py', '_collect_endpoints', 3, 3, 2).
python_function('executor/pactown.py', '_validate_urls', 3, 6, 8).
python_function('executor/pactown.py', 'stop_pactown_for_intent', 2, 5, 6).
python_function('executor/pactown.py', '_prepare_pactown_workspace', 3, 2, 4).
python_function('executor/pactown.py', '_start_pactown_stack', 3, 4, 6).
python_function('executor/pactown.py', '_start_pactown_single', 3, 5, 7).
python_function('executor/pactown.py', '_finalize_pactown', 4, 10, 12).
python_function('executor/pactown.py', 'execute_pactown', 2, 8, 12).
python_function('executor/runner.py', 'execute_intent', 5, 1, 2).
python_function('executor/runtime_stop.py', 'stop_runtime_for_intent', 2, 3, 4).
python_function('executor/validation.py', 'filter_validation_endpoints', 1, 9, 4).
python_function('executor/validation.py', 'validate_endpoints', 2, 13, 11).
python_function('executor/validation.py', 'add_main_block', 2, 7, 0).
python_function('executor/validation.py', 'attempt_auto_fix', 3, 10, 6).
python_function('generator/contract_verify.py', '_probe_path', 1, 1, 1).
python_function('generator/contract_verify.py', 'discover_service_url', 2, 10, 7).
python_function('generator/contract_verify.py', 'readiness_paths', 1, 5, 2).
python_function('generator/contract_verify.py', '_endpoint_responding', 2, 3, 2).
python_function('generator/contract_verify.py', 'wait_for_service', 4, 5, 4).
python_function('generator/contract_verify.py', '_http_probe', 3, 9, 9).
python_function('generator/contract_verify.py', 'run_testql', 3, 4, 4).
python_function('generator/contract_verify.py', 'write_contract_artifacts', 2, 1, 2).
python_function('generator/contract_verify.py', '_run_testql_checks', 3, 8, 7).
python_function('generator/contract_verify.py', '_run_http_probes', 3, 3, 4).
python_function('generator/contract_verify.py', '_write_verify_result', 2, 1, 4).
python_function('generator/contract_verify.py', 'verify_contract', 2, 6, 15).
python_function('generator/intent_generator.py', 'extract_yaml_from_llm', 1, 6, 7).
python_function('generator/intent_generator.py', '_fallback_yaml', 1, 7, 3).
python_function('generator/intent_generator.py', '_build_user_prompt', 1, 4, 1).
python_function('generator/intract_manifest.py', '_slug', 1, 2, 3).
python_function('generator/intract_manifest.py', '_safe_id', 1, 1, 3).
python_function('generator/intract_manifest.py', 'build_intract_manifest', 1, 6, 7).
python_function('generator/intract_manifest.py', 'intent_to_intract_dict', 1, 2, 4).
python_function('generator/intract_manifest.py', 'write_intract_manifest', 2, 1, 5).
python_function('generator/pipeline.py', '_write_plan_artifacts', 3, 8, 8).
python_function('generator/pipeline.py', '_expectations_summary', 1, 8, 7).
python_function('generator/pipeline.py', '_build_repair_prompt', 3, 4, 3).
python_function('generator/pipeline.py', '_container_logs', 2, 4, 1).
python_function('generator/pipeline.py', '_finalize', 2, 2, 3).
python_function('generator/pipeline.py', '_write_verify_round_log', 2, 1, 2).
python_function('generator/pipeline.py', '_generate_and_plan', 1, 9, 7).
python_function('generator/pipeline.py', '_finish_without_verify', 4, 5, 2).
python_function('generator/pipeline.py', '_handle_verify_round', 1, 6, 7).
python_function('generator/pipeline.py', '_handle_execute_error', 1, 3, 3).
python_function('generator/pipeline.py', '_run_pipeline_round', 1, 7, 10).
python_function('generator/pipeline.py', 'run_pipeline', 1, 11, 8).
python_function('generator/session.py', 'write_session_artifacts', 2, 5, 9).
python_function('generator/testql_scenario.py', '_probe_path', 1, 1, 1).
python_function('generator/testql_scenario.py', '_startup_wait_ms', 1, 7, 1).
python_function('generator/testql_scenario.py', 'build_testql_scenario', 1, 7, 8).
python_function('generator/testql_scenario.py', 'write_testql_scenario', 2, 2, 6).
python_function('integrations/adapters/docker.py', '_match_service_containers', 3, 6, 1).
python_function('integrations/adapters/docker.py', '_apply_container_to_service', 2, 5, 5).
python_function('integrations/adapters/docker.py', '_running_iterun_containers', 0, 11, 7).
python_function('integrations/bridges/pipeline.py', 'refresh_registry', 1, 5, 11).
python_function('integrations/bridges/pipeline.py', 'refresh_registry_from_pipeline', 2, 2, 3).
python_function('integrations/markpact_pack.py', '_run_command_for_ir', 1, 8, 0).
python_function('integrations/markpact_pack.py', '_service_run_command', 1, 4, 0).
python_function('integrations/markpact_pack.py', '_pack_service_readmes', 4, 4, 5).
python_function('integrations/markpact_pack.py', 'pack_workspace', 2, 12, 8).
python_function('integrations/pactown_config.py', '_health_path', 1, 8, 0).
python_function('integrations/pactown_config.py', 'build_pactown_config', 2, 12, 5).
python_function('integrations/pactown_config.py', 'write_pactown_config', 2, 1, 4).
python_function('interfaces/service.py', '_write_plan_output', 3, 7, 7).
python_function('parser/dsl_parser.py', 'parse_dsl', 1, 1, 2).
python_function('parser/dsl_parser.py', 'parse_dsl_file', 1, 1, 2).
python_function('planner/plan.py', 'plan_intent', 1, 3, 3).
python_function('planner/simulator.py', '_endpoint_to_func_name', 3, 5, 6).
python_function('planner/stack_artifacts.py', 'write_stack_artifacts', 3, 9, 8).
python_function('planner/stack_planner.py', '_service_ir', 2, 5, 6).
python_function('planner/stack_planner.py', '_gateway_proxy_code', 2, 10, 7).
python_function('planner/stack_planner.py', '_resolve_upstream', 3, 12, 1).
python_function('planner/stack_planner.py', '_build_compose', 2, 9, 3).
python_function('planner/stack_planner.py', '_plan_prebuilt_service', 2, 1, 1).
python_function('planner/stack_planner.py', '_plan_generated_service', 5, 10, 6).
python_function('planner/stack_planner.py', 'plan_stack', 1, 9, 10).
python_function('registry/catalog.py', 'discover_glob', 1, 7, 8).
python_function('registry/discover.py', '_build_services', 1, 3, 2).
python_function('registry/discover.py', 'discover_workspace', 1, 6, 10).
python_function('registry/discover_artifacts.py', 'sha256_file', 1, 2, 3).
python_function('registry/discover_artifacts.py', 'discover_artifacts', 1, 12, 13).
python_function('registry/discover_context.py', '_intent_identity', 3, 6, 1).
python_function('registry/discover_context.py', '_stack_metadata', 2, 5, 4).
python_function('registry/discover_context.py', '_workspace_prompt', 2, 4, 3).
python_function('registry/discover_context.py', 'load_workspace_context', 1, 6, 12).
python_function('registry/discover_io.py', 'load_session', 1, 3, 3).
python_function('registry/discover_io.py', 'load_stack_urls', 1, 3, 3).
python_function('registry/discover_io.py', 'intent_from_workspace', 1, 8, 5).
python_function('registry/discover_io.py', 'phase_from_session', 1, 7, 1).
python_function('registry/discover_services.py', 'build_stack_services', 0, 13, 11).
python_function('registry/discover_services.py', 'build_single_service', 0, 8, 6).
python_function('registry/labels.py', 'build_service_labels', 2, 4, 0).
python_function('registry/labels.py', 'build_otel_resource', 2, 3, 0).
python_function('tests/conftest.py', 'project_root', 0, 1, 2).
python_function('tests/conftest.py', 'sample_dsl', 0, 1, 0).
python_function('tests/conftest.py', 'sample_ir', 0, 1, 4).
python_function('tests/e2e/test_ai_gateway.py', 'run_tests', 0, 1, 1).
python_function('tests/e2e/test_contract_verify.py', 'test_readiness_paths_from_intent', 0, 5, 2).
python_function('tests/e2e/test_contract_verify.py', 'test_wait_for_service_accepts_http_404_as_up', 0, 2, 3).
python_function('tests/e2e/test_contract_verify.py', 'test_wait_for_service_default_includes_live_ready', 0, 3, 1).
python_function('tests/e2e/test_executor_validation.py', 'test_filter_validation_endpoints_skips_bare_root_when_routes_exist', 0, 4, 1).
python_function('tests/e2e/test_executor_validation.py', 'test_filter_validation_endpoints_keeps_root_when_only_base', 0, 2, 1).
python_function('tests/e2e/test_expectations.py', 'test_check_expectations_missing_endpoints', 0, 4, 3).
python_function('tests/e2e/test_expectations.py', 'test_check_expectations_framework_mismatch', 0, 2, 3).
python_function('tests/e2e/test_expectations.py', 'test_check_expectations_body_contains', 0, 3, 4).
python_function('tests/e2e/test_intract_manifest.py', 'test_build_intract_manifest_require_list', 0, 5, 3).
python_function('tests/e2e/test_intract_manifest.py', 'test_write_intract_manifest', 1, 3, 5).
python_function('tests/e2e/test_pipeline_repair.py', 'test_expectations_summary_lists_endpoints', 1, 4, 3).
python_function('tests/e2e/test_pipeline_repair.py', 'test_build_repair_prompt_includes_expectations', 1, 4, 2).
python_function('tests/e2e/test_shell.py', 'run_tests', 0, 1, 1).
python_function('tests/e2e/test_stack_planner.py', 'test_parse_stack_ir', 0, 5, 2).
python_function('tests/e2e/test_stack_planner.py', 'test_plan_stack_compose_and_services', 0, 9, 2).
python_function('tests/e2e/test_stack_planner.py', 'test_write_stack_artifacts', 1, 6, 4).
python_function('tests/e2e/test_stack_planner.py', 'test_intract_parse_stack_actions', 0, 5, 2).
python_function('tests/e2e/test_testql_scenario.py', 'test_build_testql_contains_endpoints', 0, 6, 2).
python_function('tests/e2e/test_testql_scenario.py', 'test_build_testql_express_longer_wait', 0, 2, 2).
python_function('tests/e2e/test_testql_scenario.py', 'test_write_testql_scenario', 1, 3, 3).
python_function('tests/e2e/test_web.py', 'anyio_backend', 0, 1, 0).
python_function('tests/e2e/test_web.py', 'client', 0, 1, 2).
python_function('tests/e2e/test_web.py', 'run_tests', 0, 1, 1).
python_function('tests/test_interfaces.py', 'test_interfaces_info_lists_surfaces', 0, 4, 1).
python_function('tests/test_interfaces.py', 'test_validate_yaml_detects_stack', 0, 3, 2).
python_function('tests/test_interfaces.py', 'test_plan_yaml_stack_compose', 1, 5, 3).
python_function('tests/test_interfaces.py', 'test_plan_yaml_single_service', 1, 4, 3).
python_function('tests/test_interfaces.py', 'test_sdk_local_interfaces_and_plan', 0, 3, 3).
python_function('tests/test_interfaces.py', 'test_rest_health_and_interfaces', 0, 7, 5).
python_function('tests/test_pactown_config.py', 'test_build_pactown_config_stack', 0, 5, 2).
python_function('tests/test_pactown_config.py', 'test_write_pactown_config', 1, 2, 4).
python_function('tests/test_registry.py', '_seed_workspace', 2, 2, 2).
python_function('tests/test_registry.py', 'test_discover_single_service', 1, 6, 4).
python_function('tests/test_registry.py', 'test_discover_stack', 1, 6, 4).
python_function('tests/test_registry.py', 'test_refresh_registry_exports', 1, 5, 4).
python_function('tests/test_registry.py', 'test_backstage_exporter', 1, 3, 5).
python_function('tests/test_registry.py', 'test_otel_exporter', 1, 2, 6).
python_function('tests/test_registry.py', 'test_catalog_refresh', 1, 4, 4).
python_function('tests/test_registry.py', 'test_rest_registry_endpoints', 1, 5, 7).
python_function('web/app.py', 'home', 1, 1, 4).
python_function('web/app.py', 'create_app', 0, 1, 0).
python_function('web/routes/ai.py', '_intents_store', 0, 1, 0).
python_function('web/routes/ai.py', 'health', 0, 1, 1).
python_function('web/routes/ai.py', 'ai_status', 0, 2, 3).
python_function('web/routes/ai.py', 'list_models', 1, 2, 4).
python_function('web/routes/ai.py', 'ai_complete', 1, 3, 5).
python_function('web/routes/ai.py', 'ai_chat', 1, 4, 5).
python_function('web/routes/ai.py', 'ai_suggest', 2, 6, 7).
python_function('web/routes/ai.py', 'ai_apply_suggestions', 1, 4, 6).
python_function('web/routes/ai.py', 'generate_code', 3, 3, 5).
python_function('web/routes/intents.py', '_get_service', 0, 2, 1).
python_function('web/routes/intents.py', '_intents_store', 0, 1, 0).
python_function('web/routes/intents.py', 'get_schema', 0, 1, 3).
python_function('web/routes/intents.py', 'validate_yaml', 1, 1, 3).
python_function('web/routes/intents.py', 'generate_intent_api', 1, 3, 5).
python_function('web/routes/intents.py', 'run_pipeline_api', 1, 3, 5).
python_function('web/routes/intents.py', 'generate_and_run_api', 1, 1, 2).
python_function('web/routes/intents.py', 'plan_yaml_api', 1, 4, 8).
python_function('web/routes/intents.py', 'parse_intent', 1, 2, 6).
python_function('web/routes/intents.py', 'list_intents', 0, 2, 3).
python_function('web/routes/intents.py', 'get_intent', 1, 2, 4).
python_function('web/routes/intents.py', 'delete_intent', 1, 2, 3).
python_function('web/routes/intents.py', 'plan', 1, 3, 5).
python_function('web/routes/intents.py', 'iterate', 2, 6, 8).
python_function('web/routes/intents.py', 'approve_iterun', 1, 2, 4).
python_function('web/routes/intents.py', 'execute', 4, 5, 6).
python_function('web/routes/intents.py', 'validate_intent', 1, 6, 9).
python_function('web/routes/intents.py', 'container_logs', 3, 3, 4).
python_function('web/routes/intents.py', 'get_generated_code', 1, 2, 3).
python_function('web/routes/registry.py', '_get_service', 0, 2, 1).
python_function('web/routes/registry.py', 'health', 0, 1, 1).
python_function('web/routes/registry.py', 'list_interfaces', 0, 1, 3).
python_function('web/routes/registry.py', 'get_registry', 1, 1, 3).
python_function('web/routes/registry.py', 'refresh_registry_api', 1, 1, 3).
python_function('web/routes/registry.py', 'list_registries', 1, 1, 3).

% ── Python Classes ───────────────────────────────────────
python_class('ai_gateway/feedback_loop.py', 'FeedbackSuggestion').
python_method('FeedbackSuggestion', 'to_dict', 0, 2, 0).
python_class('ai_gateway/feedback_loop.py', 'FeedbackResult').
python_method('FeedbackResult', 'to_dict', 0, 2, 1).
python_class('ai_gateway/feedback_loop.py', 'FeedbackLoop').
python_method('FeedbackLoop', '__init__', 2, 3, 1).
python_method('FeedbackLoop', 'analyze', 2, 3, 5).
python_method('FeedbackLoop', 'apply_suggestions', 3, 10, 5).
python_method('FeedbackLoop', 'iterate', 4, 4, 4).
python_method('FeedbackLoop', '_endpoint_paths', 1, 3, 0).
python_method('FeedbackLoop', '_suggest_health_endpoints', 1, 7, 2).
python_method('FeedbackLoop', '_suggest_workflow_steps', 1, 4, 2).
python_method('FeedbackLoop', 'suggest_next_steps', 1, 5, 6).
python_method('FeedbackLoop', '_build_analysis_prompt', 2, 7, 1).
python_method('FeedbackLoop', '_parse_suggestions', 1, 8, 7).
python_method('FeedbackLoop', '_extract_action', 1, 4, 3).
python_method('FeedbackLoop', '_parse_action', 1, 1, 2).
python_method('FeedbackLoop', '_process_user_feedback', 2, 4, 2).
python_class('ai_gateway/gateway.py', 'AIGateway').
python_method('AIGateway', '__init__', 1, 2, 2).
python_method('AIGateway', '_setup_litellm', 0, 5, 0).
python_method('AIGateway', 'complete', 5, 9, 7).
python_method('AIGateway', 'acomplete', 5, 9, 7).
python_method('AIGateway', '_mock_response', 2, 2, 0).
python_method('AIGateway', 'suggest_improvements', 1, 8, 8).
python_method('AIGateway', 'generate_code_snippet', 3, 10, 5).
python_method('AIGateway', 'explain_error', 2, 2, 1).
python_method('AIGateway', 'list_models', 1, 2, 2).
python_method('AIGateway', 'health_check', 0, 3, 6).
python_class('ai_gateway/model_catalog.py', 'ModelProvider').
python_class('ai_gateway/model_catalog.py', 'ModelConfig').
python_method('ModelConfig', 'to_dict', 0, 2, 0).
python_class('ai_gateway/model_catalog.py', 'GatewayConfig').
python_method('GatewayConfig', '_load_from_app_config', 0, 5, 1).
python_method('GatewayConfig', '_load_from_env', 0, 7, 1).
python_method('GatewayConfig', '_resolve_default_provider', 0, 5, 1).
python_method('GatewayConfig', '__post_init__', 0, 1, 3).
python_method('GatewayConfig', 'resolve_model', 1, 3, 0).
python_method('GatewayConfig', 'litellm_model_id', 1, 3, 1).
python_method('GatewayConfig', 'get_available_models', 1, 6, 3).
python_method('GatewayConfig', 'get_model', 1, 3, 0).
python_method('GatewayConfig', 'to_dict', 0, 2, 4).
python_class('cli/colors.py', 'Colors').
python_method('Colors', 'disable', 1, 1, 0).
python_class('cli/shell.py', 'CLI').
python_method('CLI', '__init__', 2, 3, 3).
python_method('CLI', 'print_header', 1, 2, 1).
python_method('CLI', 'print_success', 1, 2, 1).
python_method('CLI', 'print_error', 1, 1, 1).
python_method('CLI', 'print_warning', 1, 2, 1).
python_method('CLI', 'print_info', 1, 2, 1).
python_method('CLI', 'cmd_new', 2, 4, 7).
python_method('CLI', 'cmd_load', 1, 3, 6).
python_method('CLI', 'cmd_parse', 1, 2, 4).
python_method('CLI', 'cmd_plan', 1, 11, 11).
python_method('CLI', 'cmd_iterate', 2, 12, 12).
python_method('CLI', 'cmd_iterun', 2, 11, 11).
python_method('CLI', '_skip_iterun_confirmation', 0, 2, 1).
python_method('CLI', '_ensure_execute_approved', 1, 3, 4).
python_method('CLI', 'cmd_execute', 4, 6, 8).
python_method('CLI', 'cmd_show', 2, 8, 5).
python_method('CLI', 'cmd_save', 2, 3, 5).
python_method('CLI', 'interactive_mode', 0, 6, 6).
python_method('CLI', 'cmd_ai_suggest', 2, 11, 12).
python_method('CLI', 'cmd_ai_apply', 1, 8, 8).
python_method('CLI', 'cmd_ai_chat', 2, 12, 10).
python_method('CLI', 'cmd_models', 1, 3, 5).
python_method('CLI', 'cmd_ai_health', 0, 4, 7).
python_method('CLI', '_show_help', 0, 1, 1).
python_class('config.py', 'AppConfig').
python_class('dsl/schema.py', 'IntentSection').
python_method('IntentSection', 'name_kebab', 2, 2, 3).
python_class('dsl/schema.py', 'EnvironmentSection').
python_class('dsl/schema.py', 'ImplementationSection').
python_class('dsl/schema.py', 'StackServiceSection').
python_class('dsl/schema.py', 'StackSection').
python_class('dsl/schema.py', 'ExecutionSection').
python_class('dsl/schema.py', 'IntentDSLDocument').
python_method('IntentDSLDocument', 'stack_services_named', 2, 4, 3).
python_class('executor/models.py', 'ExecutionError').
python_class('executor/models.py', 'ValidationResult').
python_method('ValidationResult', '__init__', 0, 1, 0).
python_method('ValidationResult', 'add_check', 4, 3, 1).
python_method('ValidationResult', 'to_dict', 0, 2, 0).
python_class('executor/models.py', 'ExecutionResult').
python_method('ExecutionResult', '__init__', 0, 1, 0).
python_method('ExecutionResult', 'add_log', 1, 1, 3).
python_method('ExecutionResult', 'to_dict', 0, 2, 1).
python_class('executor/runner.py', 'Executor').
python_method('Executor', '__init__', 1, 3, 4).
python_method('Executor', '_check_iterun_boundary', 3, 5, 2).
python_method('Executor', '_run_runtime', 2, 5, 6).
python_method('Executor', '_finalize_success', 1, 3, 1).
python_method('Executor', 'execute', 4, 9, 10).
python_method('Executor', '_validate_and_fix', 3, 9, 8).
python_method('Executor', '_restart_container', 2, 2, 3).
python_method('Executor', '_write_artifacts', 2, 9, 5).
python_method('Executor', '_execute_local', 2, 4, 5).
python_method('Executor', 'get_container_logs', 2, 1, 1).
python_method('Executor', 'cleanup', 0, 2, 2).
python_class('generator/contract_verify.py', 'VerifyResult').
python_method('VerifyResult', 'to_dict', 0, 1, 0).
python_class('generator/intent_generator.py', 'GenerateAttempt').
python_method('GenerateAttempt', 'to_dict', 0, 3, 0).
python_class('generator/intent_generator.py', 'GenerateResult').
python_method('GenerateResult', 'to_dict', 0, 3, 1).
python_class('generator/intent_generator.py', 'IntentGenerator').
python_method('IntentGenerator', '__init__', 4, 2, 2).
python_method('IntentGenerator', 'generate', 1, 11, 14).
python_class('generator/results.py', 'PipelineResult').
python_method('PipelineResult', 'to_dict', 0, 2, 1).
python_class('integrations/adapters/backstage.py', 'BackstageExporter').
python_method('BackstageExporter', 'export', 2, 5, 7).
python_class('integrations/adapters/base.py', 'RegistryAdapter').
python_method('RegistryAdapter', 'collect', 1, 1, 0).
python_method('RegistryAdapter', 'enrich', 2, 1, 0).
python_class('integrations/adapters/base.py', 'RegistryExporter').
python_method('RegistryExporter', 'export', 2, 1, 0).
python_class('integrations/adapters/docker.py', 'DockerAdapter').
python_method('DockerAdapter', 'collect', 1, 1, 3).
python_method('DockerAdapter', 'enrich', 2, 4, 2).
python_method('DockerAdapter', '_merge_container_state', 2, 4, 3).
python_class('integrations/adapters/filesystem.py', 'FilesystemAdapter').
python_method('FilesystemAdapter', 'collect', 1, 1, 1).
python_class('integrations/adapters/opentelemetry.py', 'OpenTelemetryExporter').
python_method('OpenTelemetryExporter', 'export', 2, 5, 6).
python_class('interfaces/models.py', 'ValidateYAMLRequest').
python_class('interfaces/models.py', 'GenerateRequest').
python_class('interfaces/models.py', 'PipelineRequest').
python_class('interfaces/models.py', 'PlanYAMLRequest').
python_class('interfaces/models.py', 'ParseRequest').
python_class('interfaces/models.py', 'ExecuteRequest').
python_class('interfaces/models.py', 'InterfacesInfo').
python_class('interfaces/service.py', 'IterunService').
python_method('IterunService', '__init__', 0, 1, 0).
python_method('IterunService', 'interfaces_info', 0, 1, 0).
python_method('IterunService', 'schema', 0, 1, 1).
python_method('IterunService', 'validate_yaml', 1, 4, 3).
python_method('IterunService', 'parse', 1, 1, 1).
python_method('IterunService', 'generate', 1, 3, 2).
python_method('IterunService', 'run_pipeline', 1, 5, 2).
python_method('IterunService', 'plan_ir', 1, 1, 1).
python_method('IterunService', 'plan_yaml', 1, 3, 5).
python_method('IterunService', 'execute_ir', 1, 3, 4).
python_method('IterunService', 'registry_refresh', 1, 1, 1).
python_method('IterunService', 'registry_get', 1, 2, 4).
python_method('IterunService', 'registry_list', 1, 1, 1).
python_class('ir/models.py', 'ExecutionMode').
python_class('ir/models.py', 'RuntimeType').
python_class('ir/models.py', 'ActionType').
python_class('ir/models.py', 'Action').
python_method('Action', 'to_dict', 0, 2, 0).
python_method('Action', 'from_dict', 2, 2, 3).
python_class('ir/models.py', 'Environment').
python_method('Environment', 'to_dict', 0, 2, 0).
python_method('Environment', 'from_dict', 2, 2, 3).
python_class('ir/models.py', 'Implementation').
python_method('Implementation', 'to_dict', 0, 2, 1).
python_method('Implementation', 'from_dict', 2, 2, 3).
python_class('ir/models.py', 'StackService').
python_method('StackService', 'to_dict', 0, 2, 1).
python_method('StackService', 'from_dict', 2, 2, 6).
python_class('ir/models.py', 'Stack').
python_method('Stack', 'to_dict', 0, 2, 1).
python_method('Stack', 'from_dict', 2, 2, 5).
python_class('ir/models.py', 'Intent').
python_method('Intent', 'to_dict', 0, 2, 0).
python_method('Intent', 'from_dict', 2, 2, 2).
python_class('ir/models.py', 'IntentIR').
python_method('IntentIR', 'to_dict', 0, 2, 1).
python_method('IntentIR', 'to_json', 1, 1, 2).
python_method('IntentIR', 'from_dict', 2, 2, 8).
python_method('IntentIR', 'from_json', 2, 1, 2).
python_method('IntentIR', 'add_iteration', 2, 1, 3).
python_method('IntentIR', 'approve_iterun', 0, 1, 2).
python_class('parser/dsl_parser.py', 'ParseError').
python_method('ParseError', '__init__', 2, 1, 2).
python_class('parser/dsl_parser.py', 'ValidationError').
python_method('ValidationError', '__init__', 1, 1, 3).
python_class('parser/dsl_parser.py', 'DSLParser').
python_method('DSLParser', '__init__', 0, 1, 0).
python_method('DSLParser', 'parse_file', 1, 1, 3).
python_method('DSLParser', 'parse', 1, 9, 11).
python_method('DSLParser', '_parse_intent', 1, 4, 4).
python_method('DSLParser', '_parse_environment', 1, 3, 5).
python_method('DSLParser', '_parse_implementation', 1, 4, 5).
python_method('DSLParser', '_parse_action', 1, 8, 10).
python_method('DSLParser', '_parse_stack', 1, 14, 11).
python_method('DSLParser', '_parse_execution', 1, 3, 4).
python_method('DSLParser', '_validate_stack_services', 1, 11, 1).
python_method('DSLParser', '_validate_actions_required', 1, 3, 1).
python_method('DSLParser', '_validate_dangerous_actions', 1, 4, 3).
python_method('DSLParser', '_validate_framework_compat', 1, 5, 1).
python_method('DSLParser', '_validate', 1, 2, 4).
python_class('planner/simulator.py', 'DryRunResult').
python_method('DryRunResult', '__init__', 0, 1, 0).
python_method('DryRunResult', 'add_log', 1, 1, 3).
python_method('DryRunResult', 'to_dict', 0, 4, 1).
python_class('planner/simulator.py', 'Planner').
python_method('Planner', '__init__', 0, 1, 0).
python_method('Planner', 'dry_run', 1, 4, 8).
python_method('Planner', '_generate_python_code', 1, 3, 3).
python_method('Planner', '_generate_fastapi_code', 1, 5, 6).
python_method('Planner', '_generate_flask_code', 1, 5, 4).
python_method('Planner', '_generate_basic_python_code', 1, 1, 0).
python_method('Planner', '_generate_node_code', 1, 2, 2).
python_method('Planner', '_generate_express_code', 1, 5, 4).
python_method('Planner', '_generate_basic_node_code', 1, 1, 0).
python_method('Planner', '_generate_dockerfile', 1, 8, 4).
python_method('Planner', '_simulate_action', 2, 9, 2).
python_method('Planner', '_estimate_resources', 1, 2, 1).
python_class('registry/catalog.py', 'RegistryCatalog').
python_method('RegistryCatalog', '__init__', 1, 1, 2).
python_method('RegistryCatalog', 'registry_path', 0, 1, 0).
python_method('RegistryCatalog', 'discover', 0, 1, 1).
python_method('RegistryCatalog', 'load', 0, 2, 4).
python_method('RegistryCatalog', 'refresh', 0, 1, 2).
python_method('RegistryCatalog', 'write', 1, 2, 5).
python_method('RegistryCatalog', 'summary', 0, 4, 4).
python_class('registry/discover_context.py', 'WorkspaceContext').
python_class('registry/models.py', 'DeploymentKind').
python_class('registry/models.py', 'LifecyclePhase').
python_class('registry/models.py', 'ArtifactRole').
python_class('registry/models.py', 'ArtifactRecord').
python_class('registry/models.py', 'ServiceRecord').
python_class('registry/models.py', 'RegistryMetadata').
python_class('registry/models.py', 'RegistryStatus').
python_class('registry/models.py', 'RegistryManifest').
python_method('RegistryManifest', 'to_dict', 0, 1, 1).
python_class('sdk/client.py', 'IterunClient').
python_method('IterunClient', '__init__', 4, 2, 2).
python_method('IterunClient', 'health', 0, 2, 4).
python_method('IterunClient', 'interfaces', 0, 2, 5).
python_method('IterunClient', 'schema', 0, 2, 5).
python_method('IterunClient', 'validate', 1, 5, 4).
python_method('IterunClient', 'generate', 1, 2, 2).
python_method('IterunClient', 'run_pipeline', 1, 2, 2).
python_method('IterunClient', 'generate_and_run', 1, 1, 1).
python_method('IterunClient', 'plan_yaml', 1, 3, 3).
python_method('IterunClient', 'registry_get', 1, 2, 6).
python_method('IterunClient', 'registry_refresh', 1, 2, 3).
python_method('IterunClient', 'registry_list', 1, 2, 5).
python_method('IterunClient', 'parse', 1, 3, 4).
python_method('IterunClient', '_post_json', 2, 1, 4).
python_method('IterunClient', '_remote_generate', 1, 2, 3).
python_method('IterunClient', '_remote_pipeline', 6, 3, 4).
python_class('tests/e2e/test_ai_gateway.py', 'TestModelConfig').
python_method('TestModelConfig', 'test_ollama_models_exist', 0, 4, 1).
python_method('TestModelConfig', 'test_model_config_properties', 0, 7, 1).
python_method('TestModelConfig', 'test_models_under_12b', 0, 3, 2).
python_class('tests/e2e/test_ai_gateway.py', 'TestGatewayConfig').
python_method('TestGatewayConfig', 'test_default_config', 1, 4, 2).
python_method('TestGatewayConfig', 'test_resolve_model_prefers_llm_model', 1, 3, 5).
python_method('TestGatewayConfig', 'test_config_from_env', 0, 4, 3).
python_method('TestGatewayConfig', 'test_get_model', 0, 4, 2).
python_class('tests/e2e/test_ai_gateway.py', 'TestAIGateway').
python_method('TestAIGateway', 'test_gateway_creation', 0, 3, 1).
python_method('TestAIGateway', 'test_mock_response_when_litellm_unavailable', 0, 4, 2).
python_method('TestAIGateway', 'test_list_models', 0, 4, 3).
python_method('TestAIGateway', 'test_health_check', 0, 5, 2).
python_method('TestAIGateway', 'test_complete_without_litellm', 0, 2, 3).
python_class('tests/e2e/test_ai_gateway.py', 'TestFeedbackLoop').
python_method('TestFeedbackLoop', 'sample_ir', 0, 1, 4).
python_method('TestFeedbackLoop', 'test_feedback_loop_creation', 0, 3, 1).
python_method('TestFeedbackLoop', 'test_suggest_next_steps', 1, 3, 5).
python_method('TestFeedbackLoop', 'test_suggest_next_steps_with_health', 1, 2, 5).
python_method('TestFeedbackLoop', 'test_build_analysis_prompt', 1, 5, 3).
python_method('TestFeedbackLoop', 'test_parse_suggestions_json', 0, 5, 3).
python_method('TestFeedbackLoop', 'test_parse_suggestions_raw', 0, 2, 3).
python_method('TestFeedbackLoop', 'test_extract_action', 0, 2, 2).
python_method('TestFeedbackLoop', 'test_feedback_result_to_dict', 0, 4, 5).
python_class('tests/e2e/test_ai_gateway.py', 'TestFeedbackSuggestion').
python_method('TestFeedbackSuggestion', 'test_suggestion_defaults', 0, 4, 1).
python_method('TestFeedbackSuggestion', 'test_suggestion_to_dict', 0, 3, 2).
python_class('tests/e2e/test_ai_gateway.py', 'TestConvenienceFunctions').
python_method('TestConvenienceFunctions', 'test_get_gateway_singleton', 0, 2, 1).
python_method('TestConvenienceFunctions', 'test_complete_function', 0, 3, 1).
python_class('tests/e2e/test_intent_generator.py', 'TestSchema').
python_method('TestSchema', 'test_json_schema_has_intent', 0, 2, 1).
python_method('TestSchema', 'test_example_yaml_valid', 0, 4, 1).
python_method('TestSchema', 'test_invalid_yaml_rejected', 0, 2, 1).
python_class('tests/e2e/test_intent_generator.py', 'TestExtractYaml').
python_method('TestExtractYaml', 'test_strips_fences', 0, 2, 2).
python_method('TestExtractYaml', 'test_plain_yaml', 0, 2, 2).
python_class('tests/e2e/test_intent_generator.py', 'TestIntentGenerator').
python_method('TestIntentGenerator', 'test_generate_success_mock', 0, 5, 3).
python_method('TestIntentGenerator', 'test_retry_on_invalid_llm_output', 0, 3, 4).
python_method('TestIntentGenerator', 'test_fails_after_max_iterations', 0, 3, 4).
python_class('tests/e2e/test_intent_generator.py', 'TestPipeline').
python_method('TestPipeline', 'test_pipeline_generate_only', 1, 7, 4).
python_class('tests/e2e/test_shell.py', 'TestDSLParser').
python_method('TestDSLParser', 'test_parse_valid_dsl', 0, 8, 2).
python_method('TestDSLParser', 'test_parse_missing_intent', 0, 2, 3).
python_method('TestDSLParser', 'test_parse_invalid_yaml', 0, 1, 2).
python_method('TestDSLParser', 'test_parse_multiple_actions', 0, 5, 2).
python_method('TestDSLParser', 'test_parse_action_formats', 0, 5, 2).
python_class('tests/e2e/test_shell.py', 'TestPlanner').
python_method('TestPlanner', 'test_dry_run_fastapi', 0, 7, 4).
python_method('TestPlanner', 'test_dry_run_fastapi_path_params', 0, 4, 3).
python_method('TestPlanner', 'test_dry_run_express', 0, 5, 3).
python_method('TestPlanner', 'test_resource_estimation', 0, 4, 2).
python_class('tests/e2e/test_shell.py', 'TestCLI').
python_method('TestCLI', 'test_cli_new_intent', 0, 4, 2).
python_method('TestCLI', 'test_cli_plan', 0, 4, 4).
python_method('TestCLI', 'test_cli_iterate', 0, 3, 3).
python_method('TestCLI', 'test_cli_iterun_not_approved_without_confirmation', 0, 2, 2).
python_class('tests/e2e/test_shell.py', 'TestIRModel').
python_method('TestIRModel', 'test_ir_serialization', 0, 4, 4).
python_method('TestIRModel', 'test_ir_iteration_history', 0, 4, 3).
python_method('TestIRModel', 'test_ir_iterun_approval', 0, 5, 2).
python_class('tests/e2e/test_shell.py', 'TestEndToEnd').
python_method('TestEndToEnd', 'test_complete_workflow_dry_run', 0, 8, 3).
python_method('TestEndToEnd', 'test_file_based_workflow', 0, 4, 7).
python_class('tests/e2e/test_web.py', 'TestHealthEndpoint').
python_method('TestHealthEndpoint', 'test_health_check', 1, 4, 2).
python_class('tests/e2e/test_web.py', 'TestIntentsCRUD').
python_method('TestIntentsCRUD', 'test_list_intents_empty', 1, 4, 3).
python_method('TestIntentsCRUD', 'test_parse_valid_dsl', 1, 5, 2).
python_method('TestIntentsCRUD', 'test_parse_invalid_dsl', 1, 2, 1).
python_method('TestIntentsCRUD', 'test_parse_missing_intent_section', 1, 3, 2).
python_method('TestIntentsCRUD', 'test_get_intent', 1, 3, 3).
python_method('TestIntentsCRUD', 'test_get_nonexistent_intent', 1, 2, 1).
python_method('TestIntentsCRUD', 'test_delete_intent', 1, 4, 4).
python_class('tests/e2e/test_web.py', 'TestPlanningEndpoint').
python_method('TestPlanningEndpoint', 'test_plan_intent', 1, 10, 4).
python_method('TestPlanningEndpoint', 'test_plan_express', 1, 4, 3).
python_class('tests/e2e/test_web.py', 'TestIterationEndpoint').
python_method('TestIterationEndpoint', 'test_iterate_add_action', 1, 5, 3).
python_method('TestIterationEndpoint', 'test_iterate_change_framework', 1, 3, 2).
python_method('TestIterationEndpoint', 'test_multiple_iterations', 1, 4, 3).
python_class('tests/e2e/test_web.py', 'TestiterunAndExecution').
python_method('TestiterunAndExecution', 'test_iterun_approval', 1, 5, 2).
python_method('TestiterunAndExecution', 'test_execute_without_iterun', 1, 3, 2).
python_class('tests/e2e/test_web.py', 'TestGeneratedCodeEndpoint').
python_method('TestGeneratedCodeEndpoint', 'test_get_generated_code', 1, 4, 3).
python_class('tests/e2e/test_web.py', 'TestEndToEndWorkflow').
python_method('TestEndToEndWorkflow', 'test_complete_workflow', 1, 14, 3).
python_class('tests/e2e/test_web.py', 'TestHomePage').
python_method('TestHomePage', 'test_home_page_renders', 1, 4, 1).
python_class('web/schemas.py', 'DSLInput').
python_class('web/schemas.py', 'IterationInput').
python_class('web/schemas.py', 'ExecutionRequest').
python_class('web/schemas.py', 'GenerateRequest').
python_class('web/schemas.py', 'GenerateAndRunRequest').
python_class('web/schemas.py', 'PlanYAMLRequest').
python_class('web/schemas.py', 'RegistryRefreshRequest').
python_class('web/schemas.py', 'ValidateYAMLRequest').
python_class('web/schemas.py', 'AICompletionRequest').
python_class('web/schemas.py', 'AISuggestRequest').
python_class('web/schemas.py', 'AIChatRequest').

% ── Dependencies ─────────────────────────────────────────
project_dependency('pyyaml>=6.0', 'requirements.txt').
project_dependency('pydantic>=2.0', 'requirements.txt').
project_dependency('fastapi>=0.109.0', 'requirements.txt').
project_dependency('uvicorn>=0.27.0', 'requirements.txt').
project_dependency('jinja2>=3.1.0', 'requirements.txt').
project_dependency('litellm>=1.30.0', 'requirements.txt').
project_dependency('pytest>=8.0.0', 'requirements.txt').
project_dependency('pytest-asyncio>=0.23.0', 'requirements.txt').
project_dependency('httpx>=0.26.0', 'requirements.txt').
project_dependency('anyio>=4.0.0', 'requirements.txt').
project_dependency('python-multipart>=0.0.6', 'requirements.txt').

% ── Makefile Targets ─────────────────────────────────────
makefile_target('CYAN', 'Colors').
makefile_target('GREEN', '').
makefile_target('YELLOW', '').
makefile_target('RED', '').
makefile_target('RESET', '').
makefile_target('help', '').
makefile_target('install', '').
makefile_target('install-dev', '').
makefile_target('install-ai', '').
makefile_target('setup', '').
makefile_target('env', '').
makefile_target('run', '').
makefile_target('web', '').
makefile_target('shell', '').
makefile_target('plan', '').
makefile_target('execute', '').
makefile_target('examples', '').
makefile_target('run-intent', 'Run with custom package file: make run-intent FILE=path/to/iterun.yaml').
makefile_target('test', '').
makefile_target('test-shell', '').
makefile_target('test-web', '').
makefile_target('test-ai', '').
makefile_target('test-cov', '').
makefile_target('ollama-start', '').
makefile_target('ollama-pull', '').
makefile_target('ollama-models', '').
makefile_target('ollama-status', '').
makefile_target('lint', '').
makefile_target('format', '').
makefile_target('clean', '').
makefile_target('docker-clean', '').
makefile_target('docker-ps', '').
makefile_target('docker-stop', '').
makefile_target('dev', '').
makefile_target('new-intent', '').
makefile_target('show-config', '').

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('HOST', '0.0.0.0', '=============================================================================').
env_variable('PORT', '8080', '').
env_variable('DEBUG', 'false', '').
env_variable('LOG_LEVEL', 'INFO', '').
env_variable('AI_ENABLED', 'true', '=============================================================================').
env_variable('OPENROUTER_API_KEY', 'sk-or-...', 'OpenRouter (zalecane gdy masz klucz) — LLM_MODEL ma pierwszeństwo nad DEFAULT_MODEL').
env_variable('LLM_MODEL', 'openrouter/deepseek/deepseek-v4-pro', '').
env_variable('OLLAMA_BASE_URL', 'http://localhost:11434', 'Ollama (lokalny fallback / suggest w shell)').
env_variable('DEFAULT_MODEL', 'llama3.2', '').
env_variable('MAX_MODEL_PARAMS', '12.0', '').
env_variable('OLLAMA_TIMEOUT', '120', '').
env_variable('DOCKER_ENABLED', 'true', '=============================================================================').
env_variable('WORKSPACE_DIR', '/tmp/iterun', '').
env_variable('AUTO_EXECUTE', 'true', '').
env_variable('SKIP_ITERUN_CONFIRMATION', 'true', '').
env_variable('CONTAINER_PORT', '8000', '=============================================================================').
env_variable('CONTAINER_PREFIX', 'intent', '').
env_variable('VALIDATE_AFTER_EXECUTE', 'true', 'Enable post-execution validation').
env_variable('AUTO_FIX_ENABLED', 'true', 'Enable automatic fixing if validation fails').
env_variable('MAX_FIX_ITERATIONS', '3', 'Maximum auto-fix iterations').
env_variable('STARTUP_WAIT', '2', 'Seconds to wait for container startup before validation').
env_variable('VALIDATION_TIMEOUT', '10', 'Validation request timeout in seconds').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-api-integration.testql.toon.yaml', 'api').
testql_scenario('generated-api-smoke.testql.toon.yaml', 'api').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-api-integration.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-api-smoke.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('pyqual.yaml', 'pyqual').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('api', '').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').
sumd_workflow('install', 'manual').
sumd_workflow_step('install', 1, '$(PIP) install -r requirements.txt').
sumd_workflow('install-dev', 'manual').
sumd_workflow_step('install-dev', 1, '$(PIP) install pytest pytest-asyncio httpx anyio').
sumd_workflow('install-ai', 'manual').
sumd_workflow_step('install-ai', 1, '$(PIP) install litellm').
sumd_workflow('setup', 'manual').
sumd_workflow_step('setup', 1, 'echo "$(GREEN)✓ Setup complete$(RESET)"').
sumd_workflow('env', 'manual').
sumd_workflow_step('env', 1, 'if [ ! -f .env ]').
sumd_workflow_step('env', 2, 'cp .env.example .env').
sumd_workflow_step('env', 3, 'echo "$(GREEN)✓ Created .env from .env.example$(RESET)"').
sumd_workflow_step('env', 4, 'else \').
sumd_workflow_step('env', 5, 'echo "$(YELLOW)⚠ .env already exists$(RESET)"').
sumd_workflow_step('env', 6, 'fi').
sumd_workflow('run', 'manual').
sumd_workflow('web', 'manual').
sumd_workflow_step('web', 1, 'echo "$(CYAN)Starting web server on http://$(HOST):$(PORT)$(RESET)"').
sumd_workflow_step('web', 2, '$(PYTHON) -m web.app').
sumd_workflow('shell', 'manual').
sumd_workflow_step('shell', 1, 'echo "$(CYAN)Starting interactive shell$(RESET)"').
sumd_workflow_step('shell', 2, '$(PYTHON) -m cli.main').
sumd_workflow('plan', 'manual').
sumd_workflow_step('plan', 1, '$(PYTHON) -m cli.main plan examples/01-user-api/generated/iterun.yaml -o examples/01-user-api/generated/').
sumd_workflow('execute', 'manual').
sumd_workflow_step('execute', 1, 'ITERUN_EXECUTE=1 ./examples/01-user-api/run.sh').
sumd_workflow('examples', 'manual').
sumd_workflow_step('examples', 1, './examples/run-all.sh').
sumd_workflow('run-intent', 'manual').
sumd_workflow_step('run-intent', 1, 'if [ -z "$(FILE)" ]').
sumd_workflow_step('run-intent', 2, 'echo "$(RED)ERROR: FILE not specified$(RESET)"').
sumd_workflow_step('run-intent', 3, 'echo "Usage: make run-intent FILE=path/to/iterun.yaml"').
sumd_workflow_step('run-intent', 4, 'exit 1').
sumd_workflow_step('run-intent', 5, 'fi').
sumd_workflow_step('run-intent', 6, '$(PYTHON) -m cli.main execute $(FILE)').
sumd_workflow('test', 'manual').
sumd_workflow_step('test', 1, '$(PYTHON) -m pytest tests/ -v').
sumd_workflow('test-shell', 'manual').
sumd_workflow_step('test-shell', 1, '$(PYTHON) -m pytest tests/e2e/test_shell.py -v').
sumd_workflow('test-web', 'manual').
sumd_workflow_step('test-web', 1, '$(PYTHON) -m pytest tests/e2e/test_web.py -v').
sumd_workflow('test-ai', 'manual').
sumd_workflow_step('test-ai', 1, '$(PYTHON) -m pytest tests/e2e/test_ai_gateway.py -v').
sumd_workflow('test-cov', 'manual').
sumd_workflow_step('test-cov', 1, '$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term').
sumd_workflow('ollama-start', 'manual').
sumd_workflow_step('ollama-start', 1, 'echo "$(CYAN)Starting Ollama server...$(RESET)"').
sumd_workflow_step('ollama-start', 2, 'ollama serve &').
sumd_workflow_step('ollama-start', 3, 'sleep 2').
sumd_workflow_step('ollama-start', 4, 'echo "$(GREEN)✓ Ollama server started$(RESET)"').
sumd_workflow('ollama-pull', 'manual').
sumd_workflow_step('ollama-pull', 1, 'echo "$(CYAN)Pulling model: $(DEFAULT_MODEL)$(RESET)"').
sumd_workflow_step('ollama-pull', 2, 'ollama pull $(DEFAULT_MODEL)').
sumd_workflow_step('ollama-pull', 3, 'echo "$(GREEN)✓ Model $(DEFAULT_MODEL) ready$(RESET)"').
sumd_workflow('ollama-models', 'manual').
sumd_workflow_step('ollama-models', 1, 'echo ""').
sumd_workflow_step('ollama-models', 2, 'echo "$(CYAN)Recommended Ollama models (≤12B):$(RESET)"').
sumd_workflow_step('ollama-models', 3, 'echo "  $(GREEN)llama3.2$(RESET)       - 3B  - Default, fast"').
sumd_workflow_step('ollama-models', 4, 'echo "  llama3.2:1b    - 1B  - Ultra lightweight"').
sumd_workflow_step('ollama-models', 5, 'echo "  llama3.1:8b    - 8B  - Balanced"').
sumd_workflow_step('ollama-models', 6, 'echo "  mistral        - 7B  - Fast inference"').
sumd_workflow_step('ollama-models', 7, 'echo "  mistral-nemo   - 12B - Best quality"').
sumd_workflow_step('ollama-models', 8, 'echo "  gemma2         - 9B  - Google Gemma 2"').
sumd_workflow_step('ollama-models', 9, 'echo "  phi3           - 3.8B - Microsoft Phi-3"').
sumd_workflow_step('ollama-models', 10, 'echo "  qwen2.5        - 7B  - Alibaba Qwen"').
sumd_workflow_step('ollama-models', 11, 'echo "  codellama      - 7B  - Code generation"').
sumd_workflow_step('ollama-models', 12, 'echo ""').
sumd_workflow_step('ollama-models', 13, 'echo "$(YELLOW)Install:$(RESET) ollama pull <model>"').
sumd_workflow_step('ollama-models', 14, 'echo ""').
sumd_workflow('ollama-status', 'manual').
sumd_workflow_step('ollama-status', 1, 'echo "$(CYAN)Checking Ollama status...$(RESET)"').
sumd_workflow_step('ollama-status', 2, 'curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && \').
sumd_workflow_step('ollama-status', 3, 'echo "$(GREEN)✓ Ollama is running$(RESET)" || \').
sumd_workflow_step('ollama-status', 4, 'echo "$(RED)✗ Ollama is not running$(RESET)"').
sumd_workflow('lint', 'manual').
sumd_workflow_step('lint', 1, 'which ruff > /dev/null 2>&1 && ruff check . || echo "$(YELLOW)ruff not installed$(RESET)"').
sumd_workflow('format', 'manual').
sumd_workflow_step('format', 1, 'which ruff > /dev/null 2>&1 && ruff format . || echo "$(YELLOW)ruff not installed$(RESET)"').
sumd_workflow('clean', 'manual').
sumd_workflow_step('clean', 1, 'echo "$(CYAN)Cleaning...$(RESET)"').
sumd_workflow_step('clean', 2, 'rm -rf __pycache__ */__pycache__ */*/__pycache__').
sumd_workflow_step('clean', 3, 'rm -rf .pytest_cache */.pytest_cache').
sumd_workflow_step('clean', 4, 'rm -rf *.egg-info .eggs').
sumd_workflow_step('clean', 5, 'rm -rf htmlcov .coverage').
sumd_workflow_step('clean', 6, 'rm -rf /tmp/intent-*').
sumd_workflow_step('clean', 7, 'echo "$(GREEN)✓ Cleaned$(RESET)"').
sumd_workflow('docker-clean', 'manual').
sumd_workflow_step('docker-clean', 1, 'echo "$(CYAN)Cleaning Docker resources...$(RESET)"').
sumd_workflow_step('docker-clean', 2, '-docker ps -a --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker rm -f').
sumd_workflow_step('docker-clean', 3, '-docker images --filter "reference=$(CONTAINER_PREFIX)-*" -q | xargs -r docker rmi -f').
sumd_workflow_step('docker-clean', 4, 'echo "$(GREEN)✓ Docker cleaned$(RESET)"').
sumd_workflow('docker-ps', 'manual').
sumd_workflow_step('docker-ps', 1, 'docker ps --filter "name=$(CONTAINER_PREFIX)-"').
sumd_workflow('docker-stop', 'manual').
sumd_workflow_step('docker-stop', 1, 'docker ps --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker stop').
sumd_workflow_step('docker-stop', 2, 'echo "$(GREEN)✓ Containers stopped$(RESET)"').
sumd_workflow('dev', 'manual').
sumd_workflow_step('dev', 1, 'uvicorn web.app:app --reload --host $(HOST) --port $(PORT)').
sumd_workflow('new-intent', 'manual').
sumd_workflow_step('new-intent', 1, '$(PYTHON) -m cli.main new').
sumd_workflow('show-config', 'manual').
sumd_workflow_step('show-config', 1, 'echo ""').
sumd_workflow_step('show-config', 2, 'echo "$(CYAN)Current Configuration:$(RESET)"').
sumd_workflow_step('show-config', 3, 'echo "  HOST=$(HOST)"').
sumd_workflow_step('show-config', 4, 'echo "  PORT=$(PORT)"').
sumd_workflow_step('show-config', 5, 'echo "  DEFAULT_MODEL=$(DEFAULT_MODEL)"').
sumd_workflow_step('show-config', 6, 'echo "  CONTAINER_PORT=$(CONTAINER_PORT)"').
sumd_workflow_step('show-config', 7, 'echo "  CONTAINER_PREFIX=$(CONTAINER_PREFIX)"').
sumd_workflow_step('show-config', 8, 'echo "  OLLAMA_BASE_URL=$(OLLAMA_BASE_URL)"').
sumd_workflow_step('show-config', 9, 'echo "  SKIP_ITERUN_CONFIRMATION=$(SKIP_ITERUN_CONFIRMATION)"').
sumd_workflow_step('show-config', 10, 'echo ""').
```

## Call Graph

*235 nodes · 254 edges · 51 modules · CC̄=3.8*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `discover_artifacts` *(in registry.discover_artifacts)* | 12 ⚠ | 1 | 28 | **29** |
| `validate_endpoints` *(in executor.validation)* | 13 ⚠ | 2 | 27 | **29** |
| `execute_docker` *(in executor.docker_ops)* | 13 ⚠ | 2 | 24 | **26** |
| `write_stack_artifacts` *(in planner.stack_artifacts)* | 9 | 3 | 22 | **25** |
| `build_stack_services` *(in registry.discover_services)* | 13 ⚠ | 1 | 24 | **25** |
| `cmd_plan` *(in cli.shell.CLI)* | 11 ⚠ | 0 | 24 | **24** |
| `cmd_ai_suggest` *(in cli.shell.CLI)* | 11 ⚠ | 0 | 21 | **21** |
| `generate` *(in generator.intent_generator.IntentGenerator)* | 11 ⚠ | 0 | 21 | **21** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/wronai/iterun
# generated in 0.10s
# nodes: 235 | edges: 254 | modules: 51
# CC̄=3.8

HUBS[20]:
  registry.discover_artifacts.discover_artifacts
    CC=12  in:1  out:28  total:29
  executor.validation.validate_endpoints
    CC=13  in:2  out:27  total:29
  executor.docker_ops.execute_docker
    CC=13  in:2  out:24  total:26
  planner.stack_artifacts.write_stack_artifacts
    CC=9  in:3  out:22  total:25
  registry.discover_services.build_stack_services
    CC=13  in:1  out:24  total:25
  cli.shell.CLI.cmd_plan
    CC=11  in:0  out:24  total:24
  cli.shell.CLI.cmd_ai_suggest
    CC=11  in:0  out:21  total:21
  generator.intent_generator.IntentGenerator.generate
    CC=11  in:0  out:21  total:21
  generator.contract_verify.verify_contract
    CC=6  in:1  out:20  total:21
  examples._scripts.verify_expectations._map_expectation_errors
    CC=8  in:1  out:19  total:20
  executor.runner.Executor._validate_and_fix
    CC=9  in:0  out:18  total:18
  examples._scripts.intent_to_openapi.intent_to_openapi
    CC=8  in:1  out:17  total:18
  executor.pactown.execute_pactown
    CC=8  in:1  out:17  total:18
  cli.shell.CLI.cmd_ai_chat
    CC=12  in:0  out:18  total:18
  cli.main.build_parser
    CC=1  in:1  out:17  total:18
  generator.session.write_session_artifacts
    CC=5  in:1  out:16  total:17
  planner.stack_planner.plan_stack
    CC=9  in:1  out:15  total:16
  integrations.bridges.pipeline.refresh_registry
    CC=5  in:3  out:13  total:16
  cli.dispatch._dispatch_generate_yaml_only
    CC=6  in:1  out:15  total:16
  contracts.api_actions.parse_api_actions
    CC=9  in:5  out:11  total:16

MODULES:
  ai_gateway.feedback_loop  [2 funcs]
    __init__  CC=3  out:1
    create_feedback_loop  CC=1  out:1
  ai_gateway.gateway  [3 funcs]
    complete  CC=1  out:2
    get_gateway  CC=3  out:1
    suggest_improvements  CC=1  out:2
  ai_gateway.model_catalog  [1 funcs]
    _load_from_app_config  CC=5  out:1
  cli.dispatch  [15 funcs]
    _dispatch_execute  CC=3  out:8
    _dispatch_generate  CC=8  out:6
    _dispatch_generate_pipeline  CC=2  out:5
    _dispatch_generate_yaml_only  CC=6  out:15
    _dispatch_parse  CC=10  out:14
    _dispatch_plan  CC=12  out:13
    _dispatch_registry  CC=10  out:12
    _dispatch_validate  CC=6  out:10
    _maybe_plan_before_execute  CC=6  out:4
    _print_execute_result  CC=8  out:4
  cli.main  [2 funcs]
    build_parser  CC=1  out:17
    main  CC=2  out:5
  cli.plan_artifacts  [1 funcs]
    write_plan_artifacts  CC=7  out:12
  cli.shell  [12 funcs]
    _skip_iterun_confirmation  CC=2  out:1
    cmd_ai_apply  CC=8  out:10
    cmd_ai_chat  CC=12  out:18
    cmd_ai_health  CC=4  out:12
    cmd_ai_suggest  CC=11  out:21
    cmd_execute  CC=6  out:8
    cmd_load  CC=3  out:8
    cmd_models  CC=3  out:9
    cmd_new  CC=4  out:7
    cmd_parse  CC=2  out:4
  cli.shell_interactive  [4 funcs]
    _dispatch_ai  CC=10  out:6
    _dispatch_basic  CC=12  out:11
    build_prompt  CC=2  out:0
    handle_interactive_line  CC=6  out:8
  cli.shell_output  [7 funcs]
    log_status_color  CC=8  out:3
    print_container_logs  CC=7  out:8
    print_execution_failure  CC=2  out:3
    print_execution_logs  CC=2  out:3
    print_execution_success  CC=8  out:9
    print_validation_errors  CC=6  out:4
    print_validation_success  CC=4  out:6
  config  [7 funcs]
    _apply_env_pairs  CC=3  out:0
    _load_envstore  CC=1  out:4
    _load_getv_profiles  CC=5  out:3
    _parse_dotenv_lines  CC=5  out:9
    get_config  CC=2  out:1
    load_dotenv  CC=4  out:6
    reload_config  CC=1  out:2
  contracts.api_actions  [2 funcs]
    _parse_action_strings  CC=4  out:7
    parse_api_actions  CC=9  out:11
  contracts.expectations  [8 funcs]
    _check_declared_endpoints  CC=5  out:4
    _check_endpoint_response  CC=7  out:5
    _check_live_endpoint  CC=4  out:7
    _check_metadata  CC=7  out:8
    _http_probe  CC=3  out:8
    _probe_path  CC=1  out:1
    check_expectations  CC=4  out:6
    load_and_check_expectations  CC=4  out:8
  dsl.schema  [3 funcs]
    get_json_schema  CC=1  out:1
    get_system_prompt  CC=1  out:2
    validate_yaml_document  CC=8  out:5
  examples._scripts.annotate_intract  [6 funcs]
    _actions  CC=7  out:11
    _comment  CC=1  out:1
    _slug  CC=2  out:4
    annotate_express  CC=6  out:13
    annotate_python  CC=5  out:11
    main  CC=3  out:8
  examples._scripts.intent_to_intract  [1 funcs]
    main  CC=3  out:9
  examples._scripts.intent_to_openapi  [3 funcs]
    _slug  CC=2  out:4
    intent_to_openapi  CC=8  out:17
    main  CC=1  out:9
  examples._scripts.intent_to_testql  [1 funcs]
    main  CC=1  out:6
  examples._scripts.verify_expectations  [4 funcs]
    _load_yaml  CC=2  out:2
    _map_expectation_errors  CC=8  out:19
    main  CC=3  out:9
    verify  CC=1  out:4
  executor.docker_ops  [5 funcs]
    execute_compose_stack  CC=9  out:11
    execute_docker  CC=13  out:24
    find_available_port  CC=3  out:3
    patch_compose_host_ports  CC=7  out:7
    stop_containers_for_intent  CC=5  out:6
  executor.pactown  [10 funcs]
    _append_action_urls  CC=5  out:2
    _collect_endpoints  CC=3  out:2
    _collect_single_endpoints  CC=1  out:1
    _collect_stack_endpoints  CC=8  out:2
    _finalize_pactown  CC=10  out:15
    _prepare_pactown_workspace  CC=2  out:7
    _start_pactown_stack  CC=4  out:6
    _validate_urls  CC=6  out:10
    execute_pactown  CC=8  out:17
    stop_pactown_for_intent  CC=5  out:6
  executor.runner  [8 funcs]
    __init__  CC=3  out:5
    _execute_local  CC=4  out:7
    _restart_container  CC=2  out:3
    _run_runtime  CC=5  out:6
    _validate_and_fix  CC=9  out:18
    execute  CC=9  out:15
    get_container_logs  CC=1  out:1
    execute_intent  CC=1  out:2
  executor.validation  [4 funcs]
    add_main_block  CC=7  out:0
    attempt_auto_fix  CC=10  out:8
    filter_validation_endpoints  CC=9  out:6
    validate_endpoints  CC=13  out:27
  generator.contract_verify  [11 funcs]
    _endpoint_responding  CC=3  out:2
    _http_probe  CC=9  out:11
    _probe_path  CC=1  out:1
    _run_http_probes  CC=3  out:5
    _run_testql_checks  CC=8  out:8
    _write_verify_result  CC=1  out:4
    readiness_paths  CC=5  out:2
    run_testql  CC=4  out:5
    verify_contract  CC=6  out:20
    wait_for_service  CC=5  out:4
  generator.intent_generator  [4 funcs]
    __init__  CC=2  out:2
    generate  CC=11  out:21
    _build_user_prompt  CC=4  out:1
    extract_yaml_from_llm  CC=6  out:11
  generator.intract_manifest  [5 funcs]
    _safe_id  CC=1  out:3
    _slug  CC=2  out:4
    build_intract_manifest  CC=6  out:11
    intent_to_intract_dict  CC=2  out:4
    write_intract_manifest  CC=1  out:5
  generator.pipeline  [12 funcs]
    _build_repair_prompt  CC=4  out:3
    _container_logs  CC=4  out:1
    _expectations_summary  CC=8  out:13
    _finalize  CC=2  out:3
    _finish_without_verify  CC=5  out:2
    _generate_and_plan  CC=9  out:7
    _handle_execute_error  CC=3  out:4
    _handle_verify_round  CC=6  out:9
    _run_pipeline_round  CC=7  out:11
    _write_plan_artifacts  CC=8  out:11
  generator.session  [1 funcs]
    write_session_artifacts  CC=5  out:16
  generator.testql_scenario  [4 funcs]
    _probe_path  CC=1  out:1
    _startup_wait_ms  CC=7  out:3
    build_testql_scenario  CC=7  out:10
    write_testql_scenario  CC=2  out:7
  integrations.adapters.docker  [5 funcs]
    _merge_container_state  CC=4  out:4
    enrich  CC=4  out:2
    _apply_container_to_service  CC=5  out:8
    _match_service_containers  CC=6  out:5
    _running_iterun_containers  CC=11  out:8
  integrations.adapters.filesystem  [1 funcs]
    collect  CC=1  out:1
  integrations.bridges.pipeline  [2 funcs]
    refresh_registry  CC=5  out:13
    refresh_registry_from_pipeline  CC=2  out:3
  integrations.markpact_pack  [4 funcs]
    _pack_service_readmes  CC=4  out:5
    _run_command_for_ir  CC=8  out:0
    _service_run_command  CC=4  out:0
    pack_workspace  CC=12  out:10
  integrations.pactown_config  [3 funcs]
    _health_path  CC=8  out:0
    build_pactown_config  CC=12  out:6
    write_pactown_config  CC=1  out:4
  integrations.runtime_stop  [1 funcs]
    stop_runtime_for_intent  CC=3  out:4
  interfaces.service  [10 funcs]
    execute_ir  CC=3  out:4
    parse  CC=1  out:1
    plan_ir  CC=1  out:1
    plan_yaml  CC=3  out:6
    registry_list  CC=1  out:1
    registry_refresh  CC=1  out:1
    run_pipeline  CC=5  out:2
    schema  CC=1  out:1
    validate_yaml  CC=4  out:3
    _write_plan_output  CC=7  out:14
  parser.dsl_parser  [2 funcs]
    parse_dsl  CC=1  out:2
    parse_dsl_file  CC=1  out:2
  planner.plan  [1 funcs]
    plan_intent  CC=3  out:3
  planner.simulator  [3 funcs]
    _generate_fastapi_code  CC=5  out:7
    _generate_flask_code  CC=5  out:5
    _endpoint_to_func_name  CC=5  out:10
  planner.stack_artifacts  [1 funcs]
    write_stack_artifacts  CC=9  out:22
  planner.stack_planner  [6 funcs]
    _build_compose  CC=9  out:4
    _gateway_proxy_code  CC=10  out:12
    _plan_generated_service  CC=10  out:7
    _resolve_upstream  CC=12  out:2
    _service_ir  CC=5  out:6
    plan_stack  CC=9  out:15
  registry.catalog  [2 funcs]
    discover  CC=1  out:1
    discover_glob  CC=7  out:11
  registry.discover  [2 funcs]
    _build_services  CC=3  out:2
    discover_workspace  CC=6  out:13
  registry.discover_artifacts  [1 funcs]
    discover_artifacts  CC=12  out:28
  registry.discover_context  [3 funcs]
    _intent_identity  CC=6  out:7
    _stack_metadata  CC=5  out:5
    load_workspace_context  CC=6  out:14
  registry.discover_io  [3 funcs]
    intent_from_workspace  CC=8  out:7
    load_session  CC=3  out:3
    load_stack_urls  CC=3  out:3
  registry.discover_services  [2 funcs]
    build_single_service  CC=8  out:14
    build_stack_services  CC=13  out:24
  registry.labels  [2 funcs]
    build_otel_resource  CC=3  out:0
    build_service_labels  CC=4  out:0
  sdk.client  [3 funcs]
    parse  CC=3  out:6
    schema  CC=2  out:5
    validate  CC=5  out:4
  web.routes.ai  [8 funcs]
    _intents_store  CC=1  out:0
    ai_apply_suggestions  CC=4  out:8
    ai_chat  CC=4  out:7
    ai_complete  CC=3  out:6
    ai_status  CC=2  out:5
    ai_suggest  CC=6  out:9
    generate_code  CC=3  out:6
    list_models  CC=2  out:4
  web.routes.intents  [19 funcs]
    _get_service  CC=2  out:1
    _intents_store  CC=1  out:0
    approve_iterun  CC=2  out:4
    container_logs  CC=3  out:5
    delete_intent  CC=2  out:3
    execute  CC=5  out:6
    generate_and_run_api  CC=1  out:2
    generate_intent_api  CC=3  out:5
    get_generated_code  CC=2  out:3
    get_intent  CC=2  out:4
  web.routes.registry  [5 funcs]
    _get_service  CC=2  out:1
    get_registry  CC=1  out:3
    list_interfaces  CC=1  out:3
    list_registries  CC=1  out:3
    refresh_registry_api  CC=1  out:3

EDGES:
  config._load_envstore → config._apply_env_pairs
  config.load_dotenv → config._load_getv_profiles
  config.load_dotenv → config._apply_env_pairs
  config.load_dotenv → config._load_envstore
  config.load_dotenv → config._parse_dotenv_lines
  config.reload_config → config.load_dotenv
  generator.intent_generator.IntentGenerator.__init__ → dsl.schema.get_system_prompt
  generator.intent_generator.IntentGenerator.__init__ → ai_gateway.gateway.get_gateway
  generator.intent_generator.IntentGenerator.generate → generator.intent_generator._build_user_prompt
  generator.intent_generator.IntentGenerator.generate → generator.intent_generator.extract_yaml_from_llm
  generator.intent_generator.IntentGenerator.generate → dsl.schema.validate_yaml_document
  generator.testql_scenario.build_testql_scenario → contracts.api_actions.parse_api_actions
  generator.testql_scenario.build_testql_scenario → generator.testql_scenario._startup_wait_ms
  generator.testql_scenario.build_testql_scenario → generator.testql_scenario._probe_path
  generator.testql_scenario.write_testql_scenario → generator.testql_scenario.build_testql_scenario
  generator.pipeline._write_plan_artifacts → generator.intract_manifest.write_intract_manifest
  generator.pipeline._write_plan_artifacts → generator.testql_scenario.write_testql_scenario
  generator.pipeline._write_plan_artifacts → planner.stack_artifacts.write_stack_artifacts
  generator.pipeline._write_plan_artifacts → integrations.markpact_pack.pack_workspace
  generator.pipeline._build_repair_prompt → generator.pipeline._expectations_summary
  generator.pipeline._container_logs → executor.runner.Executor.get_container_logs
  generator.pipeline._finalize → generator.pipeline._container_logs
  generator.pipeline._finalize → generator.session.write_session_artifacts
  generator.pipeline._generate_and_plan → planner.plan.plan_intent
  generator.pipeline._generate_and_plan → generator.pipeline._build_repair_prompt
  generator.pipeline._generate_and_plan → generator.pipeline._write_plan_artifacts
  generator.pipeline._finish_without_verify → generator.pipeline._finalize
  generator.pipeline._handle_verify_round → generator.contract_verify.verify_contract
  generator.pipeline._handle_verify_round → generator.pipeline._write_verify_round_log
  generator.pipeline._handle_verify_round → generator.pipeline._finalize
  generator.pipeline._handle_execute_error → generator.pipeline._write_verify_round_log
  generator.pipeline._handle_execute_error → generator.pipeline._finalize
  generator.pipeline._run_pipeline_round → generator.pipeline._generate_and_plan
  generator.pipeline._run_pipeline_round → executor.runner.execute_intent
  generator.pipeline._run_pipeline_round → generator.pipeline._handle_verify_round
  generator.pipeline._run_pipeline_round → generator.pipeline._finalize
  generator.pipeline._run_pipeline_round → integrations.runtime_stop.stop_runtime_for_intent
  generator.pipeline._run_pipeline_round → generator.pipeline._handle_execute_error
  generator.pipeline._run_pipeline_round → generator.pipeline._finish_without_verify
  generator.pipeline.run_pipeline → generator.pipeline._finalize
  generator.pipeline.run_pipeline → generator.pipeline._run_pipeline_round
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest._safe_id
  generator.intract_manifest.build_intract_manifest → contracts.api_actions.parse_api_actions
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest._slug
  generator.intract_manifest.intent_to_intract_dict → generator.intract_manifest.build_intract_manifest
  generator.intract_manifest.write_intract_manifest → generator.intract_manifest.intent_to_intract_dict
  generator.contract_verify.readiness_paths → generator.contract_verify._probe_path
  generator.contract_verify.readiness_paths → contracts.api_actions.parse_api_actions
  generator.contract_verify.wait_for_service → generator.contract_verify.readiness_paths
  generator.contract_verify.wait_for_service → generator.contract_verify._endpoint_responding
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Api (2)

**`API Integration Tests`**
- `GET /health` → `200`
- `GET /api/v1/status` → `200`
- `POST /api/v1/test` → `201`
- assert `status == ok`
- assert `response_time < 1000`

**`Auto-generated API Smoke Tests`**
- assert `_status < 500`
- assert `_status >= 200`
- detectors: FastAPIDetector, TestEndpointDetector, ConfigEndpointDetector

### Integration (1)

**`Auto-generated from Python Tests`**

## Intent

DSL-based intent execution system with iterative refinement, featuring AI-powered suggestions via Ollama, safe simulation, and automatic health validation.
