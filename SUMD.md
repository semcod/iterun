# INTENT-ITERATIVE

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

- **name**: `intent-iterative`
- **version**: `0.1.0`
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
  name: intent-iterative;
  version: 0.1.0;
}

dependencies {
  runtime: "pyyaml>=6.0, pydantic>=2.0, fastapi>=0.109.0, uvicorn>=0.27.0, jinja2>=3.1.0";
  dev: "pytest>=8.0.0, pytest-asyncio>=0.23.0, httpx>=0.26.0, anyio>=4.0.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

interface[type="api"] {
  type: rest;
  framework: fastapi;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="intent-cli"] {

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
  step-1: run cmd=$(PYTHON) -m cli.main plan examples/user-api.intent.yaml;
}

workflow[name="execute"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m cli.main execute examples/user-api.intent.yaml;
}

workflow[name="run-intent"] {
  trigger: manual;
  step-1: run cmd=if [ -z "$(FILE)" ]; then \;
  step-2: run cmd=echo "$(RED)ERROR: FILE not specified$(RESET)"; \;
  step-3: run cmd=echo "Usage: make run-intent FILE=path/to/intent.yaml"; \;
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
  step-9: run cmd=echo "  SKIP_AMEN_CONFIRMATION=$(SKIP_AMEN_CONFIRMATION)";
  step-10: run cmd=echo "";
}

deploy {
  target: makefile;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  python_version: >=3.11;
}
```

## Interfaces

### CLI Entry Points

- `intent-cli`

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
  name: amen-quality

  metrics:
    cc_max: 15
    critical_max: 0

  custom_tools:
    - name: code2llm_amen
      binary: code2llm
      command: >-
        code2llm {workdir} -f toon -o ./project --no-chunk
        --exclude .git .venv .venv_test build dist __pycache__ .pytest_cache .code2llm_cache .benchmarks .mypy_cache .ruff_cache node_modules
      output: ""
      allow_failure: false

    - name: vallm_amen
      binary: vallm
      command: >-
        vallm batch {workdir} --recursive --format toon --output ./project
        --exclude .git,.venv,.venv_test,build,dist,__pycache__,.pytest_cache,.code2llm_cache,.benchmarks,.mypy_cache,.ruff_cache,node_modules
      output: ""
      allow_failure: false

  stages:
    - name: analyze
      tool: code2llm_amen
      optional: true
      timeout: 0

    - name: validate
      tool: vallm_amen
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
  name: intent-iterative
  version: 0.1.0
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
pip install intent-iterative

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
| `OLLAMA_BASE_URL` | `http://localhost:11434` |  |
| `DEFAULT_MODEL` | `llama3.2` |  |
| `MAX_MODEL_PARAMS` | `12.0` |  |
| `OLLAMA_TIMEOUT` | `120` |  |
| `DOCKER_ENABLED` | `true` | ============================================================================= |
| `WORKSPACE_DIR` | `/tmp/intent-iterative` |  |
| `AUTO_EXECUTE` | `true` |  |
| `SKIP_AMEN_CONFIRMATION` | `true` |  |
| `CONTAINER_PORT` | `8000` | ============================================================================= |
| `CONTAINER_PREFIX` | `intent` |  |
| `VALIDATE_AFTER_EXECUTE` | `true` | Enable post-execution validation |
| `AUTO_FIX_ENABLED` | `true` | Enable automatic fixing if validation fails |
| `MAX_FIX_ITERATIONS` | `3` | Maximum auto-fix iterations |
| `STARTUP_WAIT` | `2` | Seconds to wait for container startup before validation |
| `VALIDATION_TIMEOUT` | `10` | Validation request timeout in seconds |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`intent-iterative`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `pyproject.toml:version`, `venv/lib/python3.13/site-packages/httpcore/__init__.py:__version__`

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
- `run-intent` — Run with custom intent file: make run-intent FILE=path/to/intent.yaml
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
# amen | 25f 5727L | python:21,shell:3,less:1 | 2026-06-06
# stats: 47 func | 52 cls | 25 mod | CC̄=3.0 | critical:3 | cycles:0
# alerts[5]: CC main=21; CC load_dotenv=15; CC complete=10; CC suggest_improvements=8; CC iterate=6
# hotspots[5]: main fan=21; load_dotenv fan=11; validate_intent fan=9; iterate fan=7; ai_suggest fan=6
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[25]:
  ai_gateway/__init__.py,35
  ai_gateway/feedback_loop.py,385
  ai_gateway/gateway.py,616
  app.doql.less,231
  cli/__init__.py,4
  cli/main.py,764
  config.py,165
  executor/__init__.py,4
  executor/runner.py,615
  ir/__init__.py,10
  ir/models.py,224
  parser/__init__.py,4
  parser/dsl_parser.py,264
  planner/__init__.py,4
  planner/simulator.py,349
  project.sh,59
  run.sh,159
  tests/__init__.py,2
  tests/conftest.py,59
  tests/e2e/test_ai_gateway.py,376
  tests/e2e/test_shell.py,373
  tests/e2e/test_web.py,559
  tree.sh,2
  web/__init__.py,4
  web/app.py,460
D:
  ai_gateway/__init__.py:
  ai_gateway/feedback_loop.py:
    e: create_feedback_loop,analyze_intent,FeedbackSuggestion,FeedbackResult,FeedbackLoop
    FeedbackSuggestion: to_dict(0)  # A single improvement suggestion.
    FeedbackResult: to_dict(0)  # Result of feedback loop iteration.
    FeedbackLoop: __init__(2),analyze(2),apply_suggestions(3),iterate(4),suggest_next_steps(1),_build_analysis_prompt(2),_parse_suggestions(1),_extract_action(1),_parse_action(1),_process_user_feedback(2)  # LLM-powered feedback loop for iterative intent refinement.
    create_feedback_loop(model)
    analyze_intent(ir;focus)
  ai_gateway/gateway.py:
    e: get_gateway,complete,suggest_improvements,ModelProvider,ModelConfig,GatewayConfig,AIGateway
    ModelProvider:  # Supported model providers.
    ModelConfig: to_dict(0)  # Configuration for a specific model.
    GatewayConfig: __post_init__(0),get_available_models(1),get_model(1),to_dict(0)  # AI Gateway configuration.
    AIGateway: __init__(1),_setup_litellm(0),complete(5),acomplete(5),_mock_response(2),suggest_improvements(1),generate_code_snippet(3),explain_error(2),list_models(1),health_check(0)  # AI Gateway using LiteLLM for unified model access.
    get_gateway(config)
    complete(prompt)
    suggest_improvements(ir)
  cli/__init__.py:
  cli/main.py:
    e: main,Colors,CLI
    Colors: disable(1)  # ANSI color codes for terminal output.
    CLI: __init__(1),print_header(1),print_success(1),print_error(1),print_warning(1),print_info(1),cmd_new(2),cmd_load(1),cmd_parse(1),cmd_plan(1),cmd_iterate(2),cmd_amen(2),cmd_execute(4),cmd_show(2),cmd_save(2),interactive_mode(0),cmd_ai_suggest(2),cmd_ai_apply(1),cmd_ai_chat(2),cmd_models(1),cmd_ai_health(0),_show_help(0)  # Interactive CLI for Intent-Iterative system.
    main()
  config.py:
    e: load_dotenv,get_env,get_env_bool,get_env_int,get_env_float,get_config,reload_config,configure,AppConfig
    AppConfig:  # Main application configuration.
    load_dotenv(env_path)
    get_env(key;default)
    get_env_bool(key;default)
    get_env_int(key;default)
    get_env_float(key;default)
    get_config()
    reload_config()
    configure()
  executor/__init__.py:
  executor/runner.py:
    e: execute_intent,ExecutionError,ValidationResult,ExecutionResult,Executor
    ExecutionError:  # Raised when execution fails.
    ValidationResult: __init__(0),add_check(4),to_dict(0)  # Result of post-execution validation.
    ExecutionResult: __init__(0),add_log(1),to_dict(0)  # Result of intent execution.
    Executor: __init__(1),execute(4),_validate_and_fix(3),_validate_endpoints(2),_attempt_fix(3),_add_main_block(1),_restart_container(2),_write_artifacts(2),_find_available_port(1),_execute_docker(2),_execute_local(2),get_container_logs(2),cleanup(0)  # Executes approved intents.
    execute_intent(ir;workspace;skip_amen_check;validate;auto_fix)
  ir/__init__.py:
  ir/models.py:
    e: ExecutionMode,RuntimeType,ActionType,Action,Environment,Implementation,Intent,IntentIR
    ExecutionMode:
    RuntimeType:
    ActionType:
    Action: to_dict(0),from_dict(2)  # Single action in the implementation plan.
    Environment: to_dict(0),from_dict(2)  # Runtime environment configuration.
    Implementation: to_dict(0),from_dict(2)  # Implementation details.
    Intent: to_dict(0),from_dict(2)  # Main intent definition.
    IntentIR: to_dict(0),to_json(1),from_dict(2),from_json(2),add_iteration(2),approve_amen(0)  # Complete Intermediate Representation for an intent.
  parser/__init__.py:
  parser/dsl_parser.py:
    e: parse_dsl,parse_dsl_file,ParseError,ValidationError,DSLParser
    ParseError: __init__(2)  # Raised when DSL parsing fails.
    ValidationError: __init__(1)  # Raised when DSL validation fails.
    DSLParser: __init__(0),parse_file(1),parse(1),_parse_intent(1),_parse_environment(1),_parse_implementation(1),_parse_action(1),_parse_execution(1),_validate(1)  # Parser for INTENT-ITERATIVE DSL format.
    parse_dsl(content)
    parse_dsl_file(filepath)
  planner/__init__.py:
  planner/simulator.py:
    e: plan_intent,DryRunResult,Planner
    DryRunResult: __init__(0),add_log(1),to_dict(0)  # Result of a dry-run simulation.
    Planner: __init__(0),dry_run(1),_generate_python_code(1),_generate_fastapi_code(1),_generate_flask_code(1),_generate_basic_python_code(1),_generate_node_code(1),_generate_express_code(1),_generate_basic_node_code(1),_generate_dockerfile(1),_simulate_action(2),_estimate_resources(1)  # Plans and simulates intent execution.
    plan_intent(ir)
  tests/__init__.py:
  tests/conftest.py:
    e: project_root,sample_dsl,sample_ir
    project_root()
    sample_dsl()
    sample_ir()
  tests/e2e/test_ai_gateway.py:
    e: run_tests,TestModelConfig,TestGatewayConfig,TestAIGateway,TestFeedbackLoop,TestFeedbackSuggestion,TestConvenienceFunctions
    TestModelConfig: test_ollama_models_exist(0),test_model_config_properties(0),test_models_under_12b(0)  # Test model configuration.
    TestGatewayConfig: test_default_config(0),test_config_from_env(0),test_get_model(0)  # Test gateway configuration.
    TestAIGateway: test_gateway_creation(0),test_mock_response_when_litellm_unavailable(0),test_list_models(0),test_health_check(0),test_complete_without_litellm(0)  # Test AI Gateway functionality.
    TestFeedbackLoop: sample_ir(0),test_feedback_loop_creation(0),test_suggest_next_steps(1),test_suggest_next_steps_with_health(1),test_build_analysis_prompt(1),test_parse_suggestions_json(0),test_parse_suggestions_raw(0),test_extract_action(0),test_feedback_result_to_dict(0)  # Test feedback loop functionality.
    TestFeedbackSuggestion: test_suggestion_defaults(0),test_suggestion_to_dict(0)  # Test FeedbackSuggestion dataclass.
    TestConvenienceFunctions: test_get_gateway_singleton(0),test_complete_function(0)  # Test convenience functions.
    run_tests()
  tests/e2e/test_shell.py:
    e: run_tests,TestDSLParser,TestPlanner,TestCLI,TestIRModel,TestEndToEnd
    TestDSLParser: test_parse_valid_dsl(0),test_parse_missing_intent(0),test_parse_invalid_yaml(0),test_parse_multiple_actions(0),test_parse_action_formats(0)  # Test DSL parsing functionality.
    TestPlanner: test_dry_run_fastapi(0),test_dry_run_express(0),test_resource_estimation(0)  # Test planner/simulator functionality.
    TestCLI: test_cli_new_intent(0),test_cli_plan(0),test_cli_iterate(0),test_cli_amen_not_approved_without_confirmation(0)  # Test CLI functionality.
    TestIRModel: test_ir_serialization(0),test_ir_iteration_history(0),test_ir_amen_approval(0)  # Test IR model functionality.
    TestEndToEnd: test_complete_workflow_dry_run(0),test_file_based_workflow(0)  # End-to-end workflow tests.
    run_tests()
  tests/e2e/test_web.py:
    e: anyio_backend,client,run_tests,TestHealthEndpoint,TestIntentsCRUD,TestPlanningEndpoint,TestIterationEndpoint,TestAmenAndExecution,TestGeneratedCodeEndpoint,TestEndToEndWorkflow,TestHomePage
    TestHealthEndpoint: test_health_check(1)  # Test health check endpoint.
    TestIntentsCRUD: test_list_intents_empty(1),test_parse_valid_dsl(1),test_parse_invalid_dsl(1),test_parse_missing_intent_section(1),test_get_intent(1),test_get_nonexistent_intent(1),test_delete_intent(1)  # Test intents CRUD operations.
    TestPlanningEndpoint: test_plan_intent(1),test_plan_express(1)  # Test dry-run planning endpoint.
    TestIterationEndpoint: test_iterate_add_action(1),test_iterate_change_framework(1),test_multiple_iterations(1)  # Test iteration endpoint.
    TestAmenAndExecution: test_amen_approval(1),test_execute_without_amen(1)  # Test AMEN approval and execution endpoints.
    TestGeneratedCodeEndpoint: test_get_generated_code(1)  # Test generated code endpoint.
    TestEndToEndWorkflow: test_complete_workflow(1)  # Complete end-to-end workflow tests.
    TestHomePage: test_home_page_renders(1)  # Test home page rendering.
    anyio_backend()
    client()
    run_tests()
  web/__init__.py:
  web/app.py:
    e: home,list_intents,parse_intent,get_intent,delete_intent,plan,iterate,approve_amen,execute,validate_intent,get_container_logs,get_generated_code,health,ai_status,list_models,ai_complete,ai_chat,ai_suggest,ai_apply_suggestions,generate_code,create_app,DSLInput,IterationInput,ExecutionRequest,AICompletionRequest,AISuggestRequest,AIChatRequest
    DSLInput:
    IterationInput:
    ExecutionRequest:
    AICompletionRequest:
    AISuggestRequest:
    AIChatRequest:
    home(request)
    list_intents()
    parse_intent(data)
    get_intent(intent_id)
    delete_intent(intent_id)
    plan(intent_id)
    iterate(intent_id;data)
    approve_amen(intent_id)
    execute(intent_id;data;validate;auto_fix)
    validate_intent(intent_id)
    get_container_logs(container_id;tail)
    get_generated_code(intent_id)
    health()
    ai_status()
    list_models(max_params)
    ai_complete(request)
    ai_chat(request)
    ai_suggest(intent_id;request)
    ai_apply_suggestions(intent_id)
    generate_code(description;language;framework)
    create_app()
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('amen', '0.1.0', 'python').

% ── Project Files ────────────────────────────────────────
project_file('ai_gateway/__init__.py', 35, 'python').
project_file('ai_gateway/feedback_loop.py', 385, 'python').
project_file('ai_gateway/gateway.py', 616, 'python').
project_file('app.doql.less', 231, 'less').
project_file('cli/__init__.py', 4, 'python').
project_file('cli/main.py', 764, 'python').
project_file('config.py', 165, 'python').
project_file('executor/__init__.py', 4, 'python').
project_file('executor/runner.py', 615, 'python').
project_file('ir/__init__.py', 10, 'python').
project_file('ir/models.py', 224, 'python').
project_file('parser/__init__.py', 4, 'python').
project_file('parser/dsl_parser.py', 264, 'python').
project_file('planner/__init__.py', 4, 'python').
project_file('planner/simulator.py', 349, 'python').
project_file('project.sh', 59, 'shell').
project_file('run.sh', 159, 'shell').
project_file('tests/__init__.py', 2, 'python').
project_file('tests/conftest.py', 59, 'python').
project_file('tests/e2e/test_ai_gateway.py', 376, 'python').
project_file('tests/e2e/test_shell.py', 373, 'python').
project_file('tests/e2e/test_web.py', 559, 'python').
project_file('tree.sh', 2, 'shell').
project_file('web/__init__.py', 4, 'python').
project_file('web/app.py', 460, 'python').

% ── Python Functions ─────────────────────────────────────
python_function('ai_gateway/feedback_loop.py', 'create_feedback_loop', 1, 1, 1).
python_function('ai_gateway/feedback_loop.py', 'analyze_intent', 2, 1, 2).
python_function('ai_gateway/gateway.py', 'get_gateway', 1, 3, 1).
python_function('ai_gateway/gateway.py', 'complete', 1, 10, 2).
python_function('ai_gateway/gateway.py', 'suggest_improvements', 1, 8, 2).
python_function('cli/main.py', 'main', 0, 21, 21).
python_function('config.py', 'load_dotenv', 1, 15, 11).
python_function('config.py', 'get_env', 2, 1, 1).
python_function('config.py', 'get_env_bool', 2, 1, 3).
python_function('config.py', 'get_env_int', 2, 2, 3).
python_function('config.py', 'get_env_float', 2, 2, 3).
python_function('config.py', 'get_config', 0, 2, 1).
python_function('config.py', 'reload_config', 0, 1, 2).
python_function('config.py', 'configure', 0, 1, 1).
python_function('executor/runner.py', 'execute_intent', 5, 1, 2).
python_function('parser/dsl_parser.py', 'parse_dsl', 1, 1, 2).
python_function('parser/dsl_parser.py', 'parse_dsl_file', 1, 1, 2).
python_function('planner/simulator.py', 'plan_intent', 1, 1, 2).
python_function('tests/conftest.py', 'project_root', 0, 1, 2).
python_function('tests/conftest.py', 'sample_dsl', 0, 1, 0).
python_function('tests/conftest.py', 'sample_ir', 0, 1, 4).
python_function('tests/e2e/test_ai_gateway.py', 'run_tests', 0, 1, 1).
python_function('tests/e2e/test_shell.py', 'run_tests', 0, 1, 1).
python_function('tests/e2e/test_web.py', 'anyio_backend', 0, 1, 0).
python_function('tests/e2e/test_web.py', 'client', 0, 1, 2).
python_function('tests/e2e/test_web.py', 'run_tests', 0, 1, 1).
python_function('web/app.py', 'home', 1, 1, 4).
python_function('web/app.py', 'list_intents', 0, 2, 2).
python_function('web/app.py', 'parse_intent', 1, 2, 5).
python_function('web/app.py', 'get_intent', 1, 2, 3).
python_function('web/app.py', 'delete_intent', 1, 2, 2).
python_function('web/app.py', 'plan', 1, 2, 3).
python_function('web/app.py', 'iterate', 2, 6, 7).
python_function('web/app.py', 'approve_amen', 1, 2, 3).
python_function('web/app.py', 'execute', 4, 5, 5).
python_function('web/app.py', 'validate_intent', 1, 6, 9).
python_function('web/app.py', 'get_container_logs', 2, 1, 3).
python_function('web/app.py', 'get_generated_code', 1, 2, 2).
python_function('web/app.py', 'health', 0, 1, 1).
python_function('web/app.py', 'ai_status', 0, 2, 3).
python_function('web/app.py', 'list_models', 1, 2, 4).
python_function('web/app.py', 'ai_complete', 1, 3, 5).
python_function('web/app.py', 'ai_chat', 1, 4, 5).
python_function('web/app.py', 'ai_suggest', 2, 6, 6).
python_function('web/app.py', 'ai_apply_suggestions', 1, 4, 5).
python_function('web/app.py', 'generate_code', 3, 3, 5).
python_function('web/app.py', 'create_app', 0, 1, 0).

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
python_method('FeedbackLoop', 'suggest_next_steps', 1, 17, 3).
python_method('FeedbackLoop', '_build_analysis_prompt', 2, 7, 1).
python_method('FeedbackLoop', '_parse_suggestions', 1, 8, 7).
python_method('FeedbackLoop', '_extract_action', 1, 4, 3).
python_method('FeedbackLoop', '_parse_action', 1, 1, 2).
python_method('FeedbackLoop', '_process_user_feedback', 2, 4, 2).
python_class('ai_gateway/gateway.py', 'ModelProvider').
python_class('ai_gateway/gateway.py', 'ModelConfig').
python_method('ModelConfig', 'to_dict', 0, 2, 0).
python_class('ai_gateway/gateway.py', 'GatewayConfig').
python_method('GatewayConfig', '__post_init__', 0, 9, 2).
python_method('GatewayConfig', 'get_available_models', 1, 6, 3).
python_method('GatewayConfig', 'get_model', 1, 3, 0).
python_method('GatewayConfig', 'to_dict', 0, 2, 2).
python_class('ai_gateway/gateway.py', 'AIGateway').
python_method('AIGateway', '__init__', 1, 2, 2).
python_method('AIGateway', '_setup_litellm', 0, 5, 0).
python_method('AIGateway', 'complete', 5, 10, 5).
python_method('AIGateway', 'acomplete', 5, 10, 5).
python_method('AIGateway', '_mock_response', 2, 2, 0).
python_method('AIGateway', 'suggest_improvements', 1, 8, 8).
python_method('AIGateway', 'generate_code_snippet', 3, 10, 5).
python_method('AIGateway', 'explain_error', 2, 2, 1).
python_method('AIGateway', 'list_models', 1, 2, 2).
python_method('AIGateway', 'health_check', 0, 3, 4).
python_class('cli/main.py', 'Colors').
python_method('Colors', 'disable', 1, 1, 0).
python_class('cli/main.py', 'CLI').
python_method('CLI', '__init__', 1, 2, 3).
python_method('CLI', 'print_header', 1, 1, 1).
python_method('CLI', 'print_success', 1, 1, 1).
python_method('CLI', 'print_error', 1, 1, 1).
python_method('CLI', 'print_warning', 1, 1, 1).
python_method('CLI', 'print_info', 1, 1, 1).
python_method('CLI', 'cmd_new', 2, 4, 7).
python_method('CLI', 'cmd_load', 1, 3, 6).
python_method('CLI', 'cmd_parse', 1, 2, 4).
python_method('CLI', 'cmd_plan', 1, 10, 11).
python_method('CLI', 'cmd_iterate', 2, 12, 12).
python_method('CLI', 'cmd_amen', 2, 7, 10).
python_method('CLI', 'cmd_execute', 4, 36, 15).
python_method('CLI', 'cmd_show', 2, 8, 5).
python_method('CLI', 'cmd_save', 2, 3, 5).
python_method('CLI', 'interactive_mode', 0, 30, 23).
python_method('CLI', 'cmd_ai_suggest', 2, 11, 12).
python_method('CLI', 'cmd_ai_apply', 1, 8, 8).
python_method('CLI', 'cmd_ai_chat', 2, 12, 10).
python_method('CLI', 'cmd_models', 1, 3, 5).
python_method('CLI', 'cmd_ai_health', 0, 4, 7).
python_method('CLI', '_show_help', 0, 1, 1).
python_class('config.py', 'AppConfig').
python_class('executor/runner.py', 'ExecutionError').
python_class('executor/runner.py', 'ValidationResult').
python_method('ValidationResult', '__init__', 0, 3, 0).
python_method('ValidationResult', 'add_check', 4, 3, 1).
python_method('ValidationResult', 'to_dict', 0, 2, 0).
python_class('executor/runner.py', 'ExecutionResult').
python_method('ExecutionResult', '__init__', 0, 3, 0).
python_method('ExecutionResult', 'add_log', 1, 1, 3).
python_method('ExecutionResult', 'to_dict', 0, 2, 1).
python_class('executor/runner.py', 'Executor').
python_method('Executor', '__init__', 1, 3, 4).
python_method('Executor', 'execute', 4, 13, 10).
python_method('Executor', '_validate_and_fix', 3, 8, 6).
python_method('Executor', '_validate_endpoints', 2, 13, 11).
python_method('Executor', '_attempt_fix', 3, 10, 7).
python_method('Executor', '_add_main_block', 1, 7, 0).
python_method('Executor', '_restart_container', 2, 2, 3).
python_method('Executor', '_write_artifacts', 2, 7, 4).
python_method('Executor', '_find_available_port', 1, 3, 3).
python_method('Executor', '_execute_docker', 2, 12, 10).
python_method('Executor', '_execute_local', 2, 4, 5).
python_method('Executor', 'get_container_logs', 2, 2, 2).
python_method('Executor', 'cleanup', 0, 2, 2).
python_class('ir/models.py', 'ExecutionMode').
python_class('ir/models.py', 'RuntimeType').
python_class('ir/models.py', 'ActionType').
python_class('ir/models.py', 'Action').
python_method('Action', 'to_dict', 0, 1, 0).
python_method('Action', 'from_dict', 2, 1, 3).
python_class('ir/models.py', 'Environment').
python_method('Environment', 'to_dict', 0, 1, 0).
python_method('Environment', 'from_dict', 2, 1, 3).
python_class('ir/models.py', 'Implementation').
python_method('Implementation', 'to_dict', 0, 1, 1).
python_method('Implementation', 'from_dict', 2, 1, 3).
python_class('ir/models.py', 'Intent').
python_method('Intent', 'to_dict', 0, 1, 0).
python_method('Intent', 'from_dict', 2, 1, 2).
python_class('ir/models.py', 'IntentIR').
python_method('IntentIR', 'to_dict', 0, 1, 1).
python_method('IntentIR', 'to_json', 1, 1, 2).
python_method('IntentIR', 'from_dict', 2, 1, 8).
python_method('IntentIR', 'from_json', 2, 1, 2).
python_method('IntentIR', 'add_iteration', 2, 1, 3).
python_method('IntentIR', 'approve_amen', 0, 1, 2).
python_class('parser/dsl_parser.py', 'ParseError').
python_method('ParseError', '__init__', 2, 1, 2).
python_class('parser/dsl_parser.py', 'ValidationError').
python_method('ValidationError', '__init__', 1, 1, 3).
python_class('parser/dsl_parser.py', 'DSLParser').
python_method('DSLParser', '__init__', 0, 1, 0).
python_method('DSLParser', 'parse_file', 1, 1, 3).
python_method('DSLParser', 'parse', 1, 8, 10).
python_method('DSLParser', '_parse_intent', 1, 4, 4).
python_method('DSLParser', '_parse_environment', 1, 3, 5).
python_method('DSLParser', '_parse_implementation', 1, 4, 5).
python_method('DSLParser', '_parse_action', 1, 8, 10).
python_method('DSLParser', '_parse_execution', 1, 3, 4).
python_method('DSLParser', '_validate', 1, 8, 3).
python_class('planner/simulator.py', 'DryRunResult').
python_method('DryRunResult', '__init__', 0, 1, 0).
python_method('DryRunResult', 'add_log', 1, 1, 3).
python_method('DryRunResult', 'to_dict', 0, 1, 0).
python_class('planner/simulator.py', 'Planner').
python_method('Planner', '__init__', 0, 1, 0).
python_method('Planner', 'dry_run', 1, 4, 8).
python_method('Planner', '_generate_python_code', 1, 3, 3).
python_method('Planner', '_generate_fastapi_code', 1, 6, 6).
python_method('Planner', '_generate_flask_code', 1, 6, 4).
python_method('Planner', '_generate_basic_python_code', 1, 1, 0).
python_method('Planner', '_generate_node_code', 1, 2, 2).
python_method('Planner', '_generate_express_code', 1, 5, 4).
python_method('Planner', '_generate_basic_node_code', 1, 1, 0).
python_method('Planner', '_generate_dockerfile', 1, 8, 4).
python_method('Planner', '_simulate_action', 2, 9, 2).
python_method('Planner', '_estimate_resources', 1, 2, 1).
python_class('tests/e2e/test_ai_gateway.py', 'TestModelConfig').
python_method('TestModelConfig', 'test_ollama_models_exist', 0, 4, 1).
python_method('TestModelConfig', 'test_model_config_properties', 0, 7, 1).
python_method('TestModelConfig', 'test_models_under_12b', 0, 3, 2).
python_class('tests/e2e/test_ai_gateway.py', 'TestGatewayConfig').
python_method('TestGatewayConfig', 'test_default_config', 0, 5, 1).
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
python_class('tests/e2e/test_shell.py', 'TestDSLParser').
python_method('TestDSLParser', 'test_parse_valid_dsl', 0, 8, 2).
python_method('TestDSLParser', 'test_parse_missing_intent', 0, 2, 3).
python_method('TestDSLParser', 'test_parse_invalid_yaml', 0, 1, 2).
python_method('TestDSLParser', 'test_parse_multiple_actions', 0, 5, 2).
python_method('TestDSLParser', 'test_parse_action_formats', 0, 5, 2).
python_class('tests/e2e/test_shell.py', 'TestPlanner').
python_method('TestPlanner', 'test_dry_run_fastapi', 0, 7, 4).
python_method('TestPlanner', 'test_dry_run_express', 0, 5, 3).
python_method('TestPlanner', 'test_resource_estimation', 0, 4, 2).
python_class('tests/e2e/test_shell.py', 'TestCLI').
python_method('TestCLI', 'test_cli_new_intent', 0, 4, 2).
python_method('TestCLI', 'test_cli_plan', 0, 4, 4).
python_method('TestCLI', 'test_cli_iterate', 0, 3, 3).
python_method('TestCLI', 'test_cli_amen_not_approved_without_confirmation', 0, 2, 2).
python_class('tests/e2e/test_shell.py', 'TestIRModel').
python_method('TestIRModel', 'test_ir_serialization', 0, 4, 4).
python_method('TestIRModel', 'test_ir_iteration_history', 0, 4, 3).
python_method('TestIRModel', 'test_ir_amen_approval', 0, 5, 2).
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
python_class('tests/e2e/test_web.py', 'TestAmenAndExecution').
python_method('TestAmenAndExecution', 'test_amen_approval', 1, 5, 2).
python_method('TestAmenAndExecution', 'test_execute_without_amen', 1, 3, 2).
python_class('tests/e2e/test_web.py', 'TestGeneratedCodeEndpoint').
python_method('TestGeneratedCodeEndpoint', 'test_get_generated_code', 1, 4, 3).
python_class('tests/e2e/test_web.py', 'TestEndToEndWorkflow').
python_method('TestEndToEndWorkflow', 'test_complete_workflow', 1, 14, 3).
python_class('tests/e2e/test_web.py', 'TestHomePage').
python_method('TestHomePage', 'test_home_page_renders', 1, 4, 1).
python_class('web/app.py', 'DSLInput').
python_class('web/app.py', 'IterationInput').
python_class('web/app.py', 'ExecutionRequest').
python_class('web/app.py', 'AICompletionRequest').
python_class('web/app.py', 'AISuggestRequest').
python_class('web/app.py', 'AIChatRequest').

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
makefile_target('run-intent', 'Run with custom intent file: make run-intent FILE=path/to/intent.yaml').
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
env_variable('OLLAMA_BASE_URL', 'http://localhost:11434', '').
env_variable('DEFAULT_MODEL', 'llama3.2', '').
env_variable('MAX_MODEL_PARAMS', '12.0', '').
env_variable('OLLAMA_TIMEOUT', '120', '').
env_variable('DOCKER_ENABLED', 'true', '=============================================================================').
env_variable('WORKSPACE_DIR', '/tmp/intent-iterative', '').
env_variable('AUTO_EXECUTE', 'true', '').
env_variable('SKIP_AMEN_CONFIRMATION', 'true', '').
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
```

## Call Graph

*35 nodes · 28 edges · 8 modules · CC̄=4.2*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `cmd_execute` *(in cli.main.CLI)* | 36 ⚠ | 0 | 37 | **37** |
| `cmd_plan` *(in cli.main.CLI)* | 10 ⚠ | 0 | 24 | **24** |
| `cmd_ai_suggest` *(in cli.main.CLI)* | 11 ⚠ | 0 | 21 | **21** |
| `cmd_ai_chat` *(in cli.main.CLI)* | 12 ⚠ | 0 | 18 | **18** |
| `load_dotenv` *(in config)* | 15 ⚠ | 1 | 15 | **16** |
| `get_gateway` *(in ai_gateway.gateway)* | 3 | 12 | 1 | **13** |
| `cmd_ai_health` *(in cli.main.CLI)* | 4 | 0 | 12 | **12** |
| `cmd_ai_apply` *(in cli.main.CLI)* | 8 | 0 | 10 | **10** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/wronai/amen
# generated in 0.02s
# nodes: 35 | edges: 28 | modules: 8
# CC̄=4.2

HUBS[20]:
  cli.main.CLI.cmd_execute
    CC=36  in:0  out:37  total:37
  cli.main.CLI.cmd_plan
    CC=10  in:0  out:24  total:24
  cli.main.CLI.cmd_ai_suggest
    CC=11  in:0  out:21  total:21
  cli.main.CLI.cmd_ai_chat
    CC=12  in:0  out:18  total:18
  config.load_dotenv
    CC=15  in:1  out:15  total:16
  ai_gateway.gateway.get_gateway
    CC=3  in:12  out:1  total:13
  cli.main.CLI.cmd_ai_health
    CC=4  in:0  out:12  total:12
  cli.main.CLI.cmd_ai_apply
    CC=8  in:0  out:10  total:10
  web.app.validate_intent
    CC=6  in:0  out:9  total:9
  cli.main.CLI.cmd_models
    CC=3  in:0  out:9  total:9
  cli.main.CLI.cmd_load
    CC=3  in:0  out:8  total:8
  web.app.ai_suggest
    CC=6  in:0  out:8  total:8
  cli.main.CLI.cmd_new
    CC=4  in:0  out:7  total:7
  web.app.ai_chat
    CC=4  in:0  out:7  total:7
  web.app.ai_apply_suggestions
    CC=4  in:0  out:7  total:7
  config.get_config
    CC=2  in:5  out:1  total:6
  web.app.generate_code
    CC=3  in:0  out:6  total:6
  web.app.ai_complete
    CC=3  in:0  out:6  total:6
  ai_gateway.gateway.GatewayConfig.__post_init__
    CC=9  in:0  out:6  total:6
  web.app.ai_status
    CC=2  in:0  out:5  total:5

MODULES:
  ai_gateway.feedback_loop  [2 funcs]
    __init__  CC=3  out:1
    create_feedback_loop  CC=1  out:1
  ai_gateway.gateway  [4 funcs]
    __post_init__  CC=9  out:6
    complete  CC=1  out:2
    get_gateway  CC=3  out:1
    suggest_improvements  CC=1  out:2
  cli.main  [10 funcs]
    cmd_ai_apply  CC=8  out:10
    cmd_ai_chat  CC=12  out:18
    cmd_ai_health  CC=4  out:12
    cmd_ai_suggest  CC=11  out:21
    cmd_execute  CC=36  out:37
    cmd_load  CC=3  out:8
    cmd_models  CC=3  out:9
    cmd_new  CC=4  out:7
    cmd_parse  CC=2  out:4
    cmd_plan  CC=10  out:24
  config  [3 funcs]
    get_config  CC=2  out:1
    load_dotenv  CC=15  out:15
    reload_config  CC=1  out:2
  executor.runner  [2 funcs]
    __init__  CC=3  out:5
    execute_intent  CC=1  out:2
  parser.dsl_parser  [2 funcs]
    parse_dsl  CC=1  out:2
    parse_dsl_file  CC=1  out:2
  planner.simulator  [1 funcs]
    plan_intent  CC=1  out:2
  web.app  [11 funcs]
    ai_apply_suggestions  CC=4  out:7
    ai_chat  CC=4  out:7
    ai_complete  CC=3  out:6
    ai_status  CC=2  out:5
    ai_suggest  CC=6  out:8
    execute  CC=5  out:5
    generate_code  CC=3  out:6
    list_models  CC=2  out:4
    parse_intent  CC=2  out:5
    plan  CC=2  out:3

EDGES:
  config.reload_config → config.load_dotenv
  web.app.parse_intent → parser.dsl_parser.parse_dsl
  web.app.plan → planner.simulator.plan_intent
  web.app.execute → executor.runner.execute_intent
  web.app.validate_intent → config.get_config
  web.app.ai_status → ai_gateway.gateway.get_gateway
  web.app.list_models → ai_gateway.gateway.get_gateway
  web.app.ai_complete → ai_gateway.gateway.get_gateway
  web.app.ai_chat → ai_gateway.gateway.get_gateway
  web.app.ai_suggest → ai_gateway.feedback_loop.create_feedback_loop
  web.app.ai_apply_suggestions → ai_gateway.feedback_loop.create_feedback_loop
  web.app.generate_code → ai_gateway.gateway.get_gateway
  ai_gateway.gateway.GatewayConfig.__post_init__ → config.get_config
  ai_gateway.gateway.complete → ai_gateway.gateway.get_gateway
  ai_gateway.gateway.suggest_improvements → ai_gateway.gateway.get_gateway
  ai_gateway.feedback_loop.FeedbackLoop.__init__ → ai_gateway.gateway.get_gateway
  cli.main.CLI.cmd_new → parser.dsl_parser.parse_dsl
  cli.main.CLI.cmd_load → parser.dsl_parser.parse_dsl_file
  cli.main.CLI.cmd_parse → parser.dsl_parser.parse_dsl
  cli.main.CLI.cmd_plan → planner.simulator.plan_intent
  cli.main.CLI.cmd_execute → executor.runner.execute_intent
  cli.main.CLI.cmd_execute → config.get_config
  cli.main.CLI.cmd_ai_suggest → ai_gateway.feedback_loop.create_feedback_loop
  cli.main.CLI.cmd_ai_apply → ai_gateway.feedback_loop.create_feedback_loop
  cli.main.CLI.cmd_ai_chat → ai_gateway.gateway.get_gateway
  cli.main.CLI.cmd_models → ai_gateway.gateway.get_gateway
  cli.main.CLI.cmd_ai_health → ai_gateway.gateway.get_gateway
  executor.runner.Executor.__init__ → config.get_config
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
