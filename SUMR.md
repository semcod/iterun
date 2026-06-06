# INTENT-ITERATIVE

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `intent-iterative`
- **version**: `0.1.0`
- **python_requires**: `>=3.11`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, requirements.txt, Makefile, testql(3), app.doql.less, pyqual.yaml, goal.yaml, .env.example, project/(6 analysis files)

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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

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

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 27f 5595L | python:16,yaml:5,shell:3,txt:1,toml:1 | 2026-06-06
# generated in 0.01s
# CC̅=4.2 | critical:5/148 | dups:0 | cycles:0

HEALTH[7]:
  🔴 GOD   ai_gateway/gateway.py = 615L, 4 classes, 18m, max CC=10
  🔴 GOD   executor/runner.py = 614L, 4 classes, 20m, max CC=13
  🟡 CC    load_dotenv CC=15 (limit:15)
  🟡 CC    suggest_next_steps CC=17 (limit:15)
  🟡 CC    cmd_execute CC=36 (limit:15)
  🟡 CC    interactive_mode CC=30 (limit:15)
  🟡 CC    main CC=21 (limit:15)

REFACTOR[3]:
  1. split ai_gateway/gateway.py  (god module)
  2. split executor/runner.py  (god module)
  3. split 5 high-CC methods  (CC>15)

PIPELINES[120]:
  [1] Src [get_env]: get_env
      PURITY: 100% pure
  [2] Src [get_env_bool]: get_env_bool
      PURITY: 100% pure
  [3] Src [get_env_int]: get_env_int
      PURITY: 100% pure
  [4] Src [get_env_float]: get_env_float
      PURITY: 100% pure
  [5] Src [reload_config]: reload_config → load_dotenv
      PURITY: 100% pure
  [6] Src [configure]: configure
      PURITY: 100% pure
  [7] Src [add_log]: add_log
      PURITY: 100% pure
  [8] Src [dry_run]: dry_run
      PURITY: 100% pure
  [9] Src [_generate_python_code]: _generate_python_code
      PURITY: 100% pure
  [10] Src [_generate_fastapi_code]: _generate_fastapi_code
      PURITY: 100% pure
  [11] Src [_generate_flask_code]: _generate_flask_code
      PURITY: 100% pure
  [12] Src [_generate_node_code]: _generate_node_code
      PURITY: 100% pure
  [13] Src [_generate_express_code]: _generate_express_code
      PURITY: 100% pure
  [14] Src [_generate_dockerfile]: _generate_dockerfile
      PURITY: 100% pure
  [15] Src [_simulate_action]: _simulate_action
      PURITY: 100% pure
  [16] Src [_estimate_resources]: _estimate_resources
      PURITY: 100% pure
  [17] Src [home]: home
      PURITY: 100% pure
  [18] Src [list_intents]: list_intents
      PURITY: 100% pure
  [19] Src [parse_intent]: parse_intent → parse_dsl
      PURITY: 100% pure
  [20] Src [get_intent]: get_intent
      PURITY: 100% pure
  [21] Src [delete_intent]: delete_intent
      PURITY: 100% pure
  [22] Src [plan]: plan → plan_intent
      PURITY: 100% pure
  [23] Src [iterate]: iterate
      PURITY: 100% pure
  [24] Src [approve_amen]: approve_amen
      PURITY: 100% pure
  [25] Src [execute]: execute → execute_intent
      PURITY: 100% pure
  [26] Src [validate_intent]: validate_intent → get_config
      PURITY: 100% pure
  [27] Src [get_container_logs]: get_container_logs
      PURITY: 100% pure
  [28] Src [get_generated_code]: get_generated_code
      PURITY: 100% pure
  [29] Src [health]: health
      PURITY: 100% pure
  [30] Src [ai_status]: ai_status → get_gateway
      PURITY: 100% pure
  [31] Src [list_models]: list_models → get_gateway
      PURITY: 100% pure
  [32] Src [ai_complete]: ai_complete → get_gateway
      PURITY: 100% pure
  [33] Src [ai_chat]: ai_chat → get_gateway
      PURITY: 100% pure
  [34] Src [ai_suggest]: ai_suggest → create_feedback_loop
      PURITY: 100% pure
  [35] Src [ai_apply_suggestions]: ai_apply_suggestions → create_feedback_loop
      PURITY: 100% pure
  [36] Src [generate_code]: generate_code → get_gateway
      PURITY: 100% pure
  [37] Src [from_dict]: from_dict
      PURITY: 100% pure
  [38] Src [from_dict]: from_dict
      PURITY: 100% pure
  [39] Src [to_dict]: to_dict
      PURITY: 100% pure
  [40] Src [from_dict]: from_dict
      PURITY: 100% pure
  [41] Src [from_dict]: from_dict
      PURITY: 100% pure
  [42] Src [to_dict]: to_dict
      PURITY: 100% pure
  [43] Src [to_json]: to_json
      PURITY: 100% pure
  [44] Src [from_dict]: from_dict
      PURITY: 100% pure
  [45] Src [from_json]: from_json
      PURITY: 100% pure
  [46] Src [add_iteration]: add_iteration
      PURITY: 100% pure
  [47] Src [approve_amen]: approve_amen
      PURITY: 100% pure
  [48] Src [__post_init__]: __post_init__ → get_config
      PURITY: 100% pure
  [49] Src [get_available_models]: get_available_models
      PURITY: 100% pure
  [50] Src [to_dict]: to_dict
      PURITY: 100% pure

LAYERS:
  cli/                            CC̄=7.6    ←in:0  →out:13  !! split
  │ !! main                       763L  2C   24m  CC=36     ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  executor/                       CC̄=4.8    ←in:2  →out:1
  │ !! runner                     614L  4C   20m  CC=13     ←2
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  ai_gateway/                     CC̄=4.6    ←in:13  →out:1
  │ !! gateway                    615L  4C   18m  CC=10     ←3
  │ !! feedback_loop              384L  3C   14m  CC=17     ←2
  │ __init__                    34L  0C    0m  CC=0.0    ←0
  │
  parser/                         CC̄=3.5    ←in:4  →out:0
  │ dsl_parser                 263L  3C   13m  CC=8      ←2
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  planner/                        CC̄=3.2    ←in:2  →out:0
  │ simulator                  348L  2C   16m  CC=9      ←2
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=3.1    ←in:0  →out:0
  │ !! goal.yaml                  511L  0C    0m  CC=0.0    ←0
  │ planfile.yaml              474L  0C    0m  CC=0.0    ←0
  │ Makefile                   219L  0C    0m  CC=0.0    ←0
  │ !! config                     164L  1C    8m  CC=15     ←4
  │ run.sh                     158L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              97L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                82L  0C    0m  CC=0.0    ←0
  │ project.sh                  59L  0C    0m  CC=0.0    ←0
  │ pyqual.yaml                 55L  0C    0m  CC=0.0    ←0
  │ requirements.txt            20L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │
  web/                            CC̄=2.8    ←in:0  →out:11  !! split
  │ app                        459L  6C   21m  CC=6      ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  ir/                             CC̄=1.1    ←in:0  →out:0
  │ models                     223L  8C   14m  CC=2      ←0
  │ __init__                     9L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=0.0    ←in:0  →out:0
  │ user-api.intent.yaml        28L  0C    0m  CC=0.0    ←0
  │

COUPLING:
              ai_gateway         cli         web      config      parser    executor     planner
  ai_gateway          ──          ←6          ←7           1                                      hub
         cli           6          ──                       2           3           1           1  !! fan-out
         web           7                      ──           1           1           1           1  !! fan-out
      config          ←1          ←2          ←1          ──                      ←1              hub
      parser                      ←3          ←1                      ──                        
    executor                      ←1          ←1           1                      ──            
     planner                      ←1          ←1                                              ──
  CYCLES: none
  HUB: config/ (fan-in=5)
  HUB: ai_gateway/ (fan-in=13)
  SMELL: cli/ fan-out=13 → split needed
  SMELL: web/ fan-out=11 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 2 groups | 16f 3891L | 2026-06-06

SUMMARY:
  files_scanned: 16
  total_lines:   3891
  dup_groups:    2
  dup_fragments: 5
  saved_lines:   11
  scan_ms:       3724

HOTSPOTS[3] (files with most duplication):
  parser/dsl_parser.py  dup=8L  groups=1  frags=2  (0.2%)
  planner/simulator.py  dup=7L  groups=2  frags=2  (0.2%)
  executor/runner.py  dup=3L  groups=1  frags=1  (0.1%)

DUPLICATES[2] (ranked by impact):
  [d1ab1a804f1b435b]   STRU  parse_dsl  L=4 N=3 saved=8 sim=1.00
      parser/dsl_parser.py:254-257  (parse_dsl)
      parser/dsl_parser.py:260-263  (parse_dsl_file)
      planner/simulator.py:345-348  (plan_intent)
  [f041dec9367328ca]   EXAC  add_log  L=3 N=2 saved=3 sim=1.00
      executor/runner.py:93-95  (add_log)
      planner/simulator.py:26-28  (add_log)

REFACTOR[2] (ranked by priority):
  [1] ○ extract_function   → utils/parse_dsl.py
      WHY: 3 occurrences of 4-line block across 2 files — saves 8 lines
      FILES: parser/dsl_parser.py, planner/simulator.py
  [2] ○ extract_function   → utils/add_log.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: executor/runner.py, planner/simulator.py

QUICK_WINS[1] (low risk, high savings — do first):
  [1] extract_function   saved=8L  → utils/parse_dsl.py
      FILES: dsl_parser.py, simulator.py

DEPENDENCY_RISK[2] (duplicates spanning multiple packages):
  parse_dsl  packages=2  files=2
      parser/dsl_parser.py
      planner/simulator.py
  add_log  packages=2  files=2
      executor/runner.py
      planner/simulator.py

EFFORT_ESTIMATE (total ≈ 0.7h):
  medium parse_dsl                           saved=8L  ~32min
  easy   add_log                             saved=3L  ~12min

METRICS-TARGET:
  dup_groups:  2 → 0
  saved_lines: 11 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 148 func | 9f | 2026-06-06
# generated in 0.00s

NEXT[7] (ranked by impact):
  [1] !! SPLIT           cli/main.py
      WHY: 763L, 2 classes, max CC=36
      EFFORT: ~4h  IMPACT: 27468

  [2] !! SPLIT           executor/runner.py
      WHY: 614L, 4 classes, max CC=13
      EFFORT: ~4h  IMPACT: 7982

  [3] !! SPLIT           ai_gateway/gateway.py
      WHY: 615L, 4 classes, max CC=10
      EFFORT: ~4h  IMPACT: 6150

  [4] !! SPLIT-FUNC      CLI.interactive_mode  CC=30  fan=23
      WHY: CC=30 exceeds 15
      EFFORT: ~1h  IMPACT: 690

  [5] !! SPLIT-FUNC      CLI.cmd_execute  CC=36  fan=15
      WHY: CC=36 exceeds 15
      EFFORT: ~1h  IMPACT: 540

  [6] !  SPLIT-FUNC      main  CC=21  fan=21
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 441

  [7] !  SPLIT-FUNC      load_dotenv  CC=15  fan=14
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 210


RISKS[3]:
  ⚠ Splitting cli/main.py may break 24 import paths
  ⚠ Splitting ai_gateway/gateway.py may break 18 import paths
  ⚠ Splitting executor/runner.py may break 20 import paths

METRICS-TARGET:
  CC̄:          4.2 → ≤2.9
  max-CC:      36 → ≤18
  god-modules: 4 → 0
  high-CC(≥15): 5 → ≤2
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  (first run — no previous data)
```

### Validation (`project/validation.toon.yaml`)

```toon markpact:analysis path=project/validation.toon.yaml
# vallm batch | 38f | 9✓ 0⚠ 19✗ | 2026-03-31

SUMMARY:
  scanned: 38  passed: 9 (23.7%)  warnings: 0  errors: 19  unsupported: 10

ERRORS[19]{path,score}:
  ai_gateway/__init__.py,0.57
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'gateway' not found,1
      python.import.resolvable,error,Module 'feedback_loop' not found,12
  cli/__init__.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'main' not found,1
  executor/__init__.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'runner' not found,1
  ir/__init__.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'models' not found,1
  parser/__init__.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'dsl_parser' not found,1
  planner/__init__.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'simulator' not found,1
  web/__init__.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'app' not found,1
  tests/e2e/test_ai_gateway.py,0.64
    issues[26]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,14
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,22
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,30
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,41
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,55
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,67
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,70
      python.import.resolvable,error,Module 'config' not found,81
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,104
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,121
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,129
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,142
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,153
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,166
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,194
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,202
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,213
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,227
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,239
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,266
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,282
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,293
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,318
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,331
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,352
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,361
  web/app.py,0.71
    issues[15]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'fastapi' not found,6
      python.import.resolvable,error,Module 'fastapi.responses' not found,7
      python.import.resolvable,error,Module 'fastapi.staticfiles' not found,8
      python.import.resolvable,error,Module 'fastapi.templating' not found,9
      python.import.resolvable,error,Module 'ir.models' not found,19
      python.import.resolvable,error,Module 'parser.dsl_parser' not found,20
      python.import.resolvable,error,Module 'planner.simulator' not found,21
      python.import.resolvable,error,Module 'executor.runner' not found,22
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,26
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,27
      python.import.resolvable,error,Module 'executor.runner' not found,224
      python.import.resolvable,error,Module 'config' not found,228
      python.import.resolvable,error,Module 'executor.runner' not found,257
      python.import.resolvable,error,Module 'config' not found,455
      python.import.resolvable,error,Module 'parser.dsl_parser' not found,152
  cli/main.py,0.72
    issues[9]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,16
      python.import.resolvable,error,Module 'parser.dsl_parser' not found,17
      python.import.resolvable,error,Module 'planner.simulator' not found,18
      python.import.resolvable,error,Module 'executor.runner' not found,19
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,23
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,24
      python.import.resolvable,error,Module 'config' not found,229
      python.import.resolvable,error,Module 'config' not found,270
      python.import.resolvable,error,Module 'executor.runner' not found,350
  config.py,0.82
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'getv' not found,13
      python.import.resolvable,error,Module 'getv' not found,28
      python.import.resolvable,error,Module 'getv.integrations.pydantic_env' not found,29
  tests/e2e/test_shell.py,0.83
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,15
      python.import.resolvable,error,Module 'parser.dsl_parser' not found,16
      python.import.resolvable,error,Module 'planner.simulator' not found,17
      python.import.resolvable,error,Module 'cli.main' not found,18
  ai_gateway/feedback_loop.py,0.86
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,15
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,16
      python.import.resolvable,error,Module 'parser.dsl_parser' not found,333
  tests/conftest.py,0.89
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,47
  planner/simulator.py,0.91
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,13
  tests/e2e/test_web.py,0.91
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'web.app' not found,14
  ai_gateway/gateway.py,0.92
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,24
      python.import.resolvable,error,Module 'config' not found,220
  executor/runner.py,0.93
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,19
      python.import.resolvable,error,Module 'config' not found,20
  parser/dsl_parser.py,0.93
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,14

UNSUPPORTED[4]{bucket,count}:
  *.md,5
  *.txt,1
  *.example,1
  other,3
```

## Intent

DSL-based intent execution system with iterative refinement, featuring AI-powered suggestions via Ollama, safe simulation, and automatic health validation.
