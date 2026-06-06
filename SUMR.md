# ITERUN

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

- **name**: `iterun`
- **version**: `0.1.9`
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
  name: iterun;
  version: 0.1.9;
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

*143 nodes · 131 edges · 36 modules · CC̄=4.6*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `discover_workspace` *(in registry.discover)* | 44 ⚠ | 2 | 75 | **77** |
| `execute_pactown` *(in integrations.pactown_runtime)* | 21 ⚠ | 1 | 50 | **51** |
| `cmd_execute` *(in cli.main.CLI)* | 37 ⚠ | 0 | 37 | **37** |
| `run_pipeline` *(in generator.pipeline)* | 33 ⚠ | 0 | 37 | **37** |
| `verify_contract` *(in generator.contract_verify)* | 16 ⚠ | 1 | 32 | **33** |
| `_discover_artifacts` *(in registry.discover)* | 12 ⚠ | 1 | 28 | **29** |
| `verify` *(in examples._scripts.verify_expectations)* | 23 ⚠ | 1 | 27 | **28** |
| `check_expectations` *(in generator.expectations)* | 23 ⚠ | 1 | 26 | **27** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/wronai/iterun
# generated in 0.06s
# nodes: 143 | edges: 131 | modules: 36
# CC̄=4.6

HUBS[20]:
  registry.discover.discover_workspace
    CC=44  in:2  out:75  total:77
  integrations.pactown_runtime.execute_pactown
    CC=21  in:1  out:50  total:51
  cli.main.CLI.cmd_execute
    CC=37  in:0  out:37  total:37
  generator.pipeline.run_pipeline
    CC=33  in:0  out:37  total:37
  generator.contract_verify.verify_contract
    CC=16  in:1  out:32  total:33
  registry.discover._discover_artifacts
    CC=12  in:1  out:28  total:29
  examples._scripts.verify_expectations.verify
    CC=23  in:1  out:27  total:28
  generator.expectations.check_expectations
    CC=23  in:1  out:26  total:27
  planner.stack_artifacts.write_stack_artifacts
    CC=9  in:3  out:22  total:25
  cli.main.CLI.cmd_plan
    CC=11  in:0  out:24  total:24
  executor.runner.Executor.execute
    CC=18  in:0  out:22  total:22
  planner.stack_planner.plan_stack
    CC=18  in:1  out:21  total:22
  generator.intent_generator.IntentGenerator.generate
    CC=11  in:0  out:21  total:21
  cli.main.CLI.cmd_ai_suggest
    CC=11  in:0  out:21  total:21
  cli.main.CLI.cmd_ai_chat
    CC=12  in:0  out:18  total:18
  examples._scripts.intent_to_openapi.intent_to_openapi
    CC=8  in:1  out:17  total:18
  executor.runner.Executor._validate_and_fix
    CC=8  in:0  out:17  total:17
  generator.session.write_session_artifacts
    CC=5  in:1  out:16  total:17
  integrations.adapters.docker.DockerAdapter.enrich
    CC=16  in:0  out:16  total:16
  integrations.bridges.pipeline.refresh_registry
    CC=5  in:3  out:13  total:16

MODULES:
  ai_gateway.feedback_loop  [2 funcs]
    __init__  CC=3  out:1
    create_feedback_loop  CC=1  out:1
  ai_gateway.gateway  [4 funcs]
    __post_init__  CC=15  out:8
    complete  CC=1  out:2
    get_gateway  CC=3  out:1
    suggest_improvements  CC=1  out:2
  cli.main  [11 funcs]
    cmd_ai_apply  CC=8  out:10
    cmd_ai_chat  CC=12  out:18
    cmd_ai_health  CC=4  out:12
    cmd_ai_suggest  CC=11  out:21
    cmd_execute  CC=37  out:37
    cmd_load  CC=3  out:8
    cmd_models  CC=3  out:9
    cmd_new  CC=4  out:7
    cmd_parse  CC=2  out:4
    cmd_plan  CC=11  out:24
  config  [3 funcs]
    get_config  CC=2  out:1
    load_dotenv  CC=15  out:15
    reload_config  CC=1  out:2
  dsl.schema  [3 funcs]
    get_json_schema  CC=1  out:1
    get_system_prompt  CC=1  out:2
    validate_yaml_document  CC=10  out:8
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
    _parse_actions  CC=6  out:9
    main  CC=3  out:9
    verify  CC=23  out:27
  examples._verify  [1 funcs]
    write_intract_manifest  CC=0  out:0
  executor.runner  [6 funcs]
    __init__  CC=3  out:5
    _validate_and_fix  CC=8  out:17
    execute  CC=18  out:22
    _filter_validation_endpoints  CC=9  out:6
    execute_intent  CC=1  out:2
    stop_containers_for_intent  CC=5  out:6
  generator.contract_verify  [6 funcs]
    _endpoint_responding  CC=3  out:2
    _probe_path  CC=1  out:1
    readiness_paths  CC=5  out:2
    verify_contract  CC=16  out:32
    wait_for_service  CC=5  out:4
    write_contract_artifacts  CC=1  out:2
  generator.expectations  [2 funcs]
    check_expectations  CC=23  out:26
    load_and_check_expectations  CC=4  out:8
  generator.intent_generator  [4 funcs]
    __init__  CC=2  out:2
    generate  CC=11  out:21
    _build_user_prompt  CC=4  out:1
    extract_yaml_from_llm  CC=6  out:11
  generator.intract_manifest  [7 funcs]
    _parse_action_strings  CC=4  out:7
    _safe_id  CC=1  out:3
    _slug  CC=2  out:4
    build_intract_manifest  CC=6  out:11
    intent_to_intract_dict  CC=2  out:4
    parse_api_actions  CC=9  out:11
    write_intract_manifest  CC=1  out:5
  generator.pipeline  [6 funcs]
    _build_repair_prompt  CC=4  out:3
    _container_logs  CC=4  out:3
    _expectations_summary  CC=8  out:13
    _finalize  CC=3  out:4
    _write_plan_artifacts  CC=8  out:11
    run_pipeline  CC=33  out:37
  generator.session  [1 funcs]
    write_session_artifacts  CC=5  out:16
  generator.testql_scenario  [4 funcs]
    _probe_path  CC=1  out:1
    _startup_wait_ms  CC=7  out:3
    build_testql_scenario  CC=7  out:10
    write_testql_scenario  CC=2  out:7
  integrations.adapters.docker  [2 funcs]
    enrich  CC=16  out:16
    _running_iterun_containers  CC=11  out:8
  integrations.adapters.filesystem  [1 funcs]
    collect  CC=1  out:1
  integrations.bridges.pipeline  [2 funcs]
    refresh_registry  CC=5  out:13
    refresh_registry_from_pipeline  CC=2  out:2
  integrations.markpact_pack  [2 funcs]
    _run_command_for_ir  CC=8  out:0
    pack_workspace  CC=18  out:12
  integrations.pactown_config  [3 funcs]
    _health_path  CC=8  out:0
    build_pactown_config  CC=12  out:6
    write_pactown_config  CC=1  out:4
  integrations.pactown_runtime  [3 funcs]
    _validate_urls  CC=6  out:10
    execute_pactown  CC=21  out:50
    stop_pactown_for_intent  CC=5  out:6
  integrations.runtime_stop  [1 funcs]
    stop_runtime_for_intent  CC=3  out:4
  interfaces.service  [9 funcs]
    execute_ir  CC=3  out:4
    parse  CC=1  out:1
    plan_ir  CC=1  out:1
    plan_yaml  CC=3  out:6
    registry_list  CC=1  out:1
    registry_refresh  CC=1  out:1
    schema  CC=1  out:1
    validate_yaml  CC=4  out:3
    _write_plan_output  CC=7  out:14
  parser.dsl_parser  [2 funcs]
    parse_dsl  CC=1  out:2
    parse_dsl_file  CC=1  out:2
  planner.simulator  [4 funcs]
    _generate_fastapi_code  CC=5  out:7
    _generate_flask_code  CC=5  out:5
    _endpoint_to_func_name  CC=5  out:10
    plan_intent  CC=3  out:3
  planner.stack_artifacts  [1 funcs]
    write_stack_artifacts  CC=9  out:22
  planner.stack_planner  [4 funcs]
    _build_compose  CC=9  out:4
    _gateway_proxy_code  CC=10  out:12
    _resolve_upstream  CC=12  out:2
    plan_stack  CC=18  out:21
  registry.catalog  [2 funcs]
    discover  CC=1  out:1
    discover_glob  CC=7  out:11
  registry.discover  [6 funcs]
    _discover_artifacts  CC=12  out:28
    _intent_from_workspace  CC=8  out:7
    _load_session  CC=3  out:3
    _load_stack_urls  CC=3  out:3
    _phase_from_session  CC=7  out:5
    discover_workspace  CC=44  out:75
  registry.labels  [1 funcs]
    build_service_labels  CC=4  out:0
  sdk.client  [3 funcs]
    parse  CC=3  out:6
    schema  CC=2  out:5
    validate  CC=5  out:4
  web.app  [22 funcs]
    _get_service  CC=2  out:1
    ai_apply_suggestions  CC=4  out:7
    ai_chat  CC=4  out:7
    ai_complete  CC=3  out:6
    ai_status  CC=2  out:5
    ai_suggest  CC=6  out:8
    execute  CC=5  out:5
    generate_and_run_api  CC=1  out:2
    generate_code  CC=3  out:6
    generate_intent_api  CC=3  out:4

EDGES:
  generator.expectations.check_expectations → generator.intract_manifest.parse_api_actions
  generator.expectations.load_and_check_expectations → generator.expectations.check_expectations
  generator.testql_scenario.build_testql_scenario → generator.intract_manifest.parse_api_actions
  generator.testql_scenario.build_testql_scenario → generator.testql_scenario._startup_wait_ms
  generator.testql_scenario.build_testql_scenario → generator.testql_scenario._probe_path
  generator.testql_scenario.write_testql_scenario → generator.testql_scenario.build_testql_scenario
  examples._scripts.verify_expectations.verify → examples._scripts.verify_expectations._load_yaml
  examples._scripts.verify_expectations.verify → examples._scripts.verify_expectations._parse_actions
  examples._scripts.verify_expectations.main → examples._scripts.verify_expectations.verify
  examples._scripts.annotate_intract._comment → examples._scripts.annotate_intract._slug
  examples._scripts.annotate_intract.annotate_python → examples._scripts.annotate_intract._actions
  examples._scripts.annotate_intract.annotate_express → examples._scripts.annotate_intract._actions
  examples._scripts.annotate_intract.main → examples._scripts.annotate_intract.annotate_python
  examples._scripts.annotate_intract.main → examples._scripts.annotate_intract.annotate_express
  examples._scripts.intent_to_testql.main → generator.testql_scenario.write_testql_scenario
  examples._scripts.intent_to_intract.main → examples._verify.write_intract_manifest
  examples._scripts.intent_to_openapi.intent_to_openapi → examples._scripts.intent_to_openapi._slug
  examples._scripts.intent_to_openapi.main → examples._scripts.intent_to_openapi.intent_to_openapi
  ai_gateway.gateway.GatewayConfig.__post_init__ → config.get_config
  ai_gateway.gateway.complete → ai_gateway.gateway.get_gateway
  ai_gateway.gateway.suggest_improvements → ai_gateway.gateway.get_gateway
  ai_gateway.feedback_loop.FeedbackLoop.__init__ → ai_gateway.gateway.get_gateway
  generator.intract_manifest.parse_api_actions → generator.intract_manifest._parse_action_strings
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest._safe_id
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest.parse_api_actions
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest._slug
  generator.intract_manifest.intent_to_intract_dict → generator.intract_manifest.build_intract_manifest
  generator.intract_manifest.write_intract_manifest → generator.intract_manifest.intent_to_intract_dict
  planner.simulator.Planner._generate_fastapi_code → planner.simulator._endpoint_to_func_name
  planner.simulator.Planner._generate_flask_code → planner.simulator._endpoint_to_func_name
  planner.simulator.plan_intent → planner.stack_planner.plan_stack
  registry.catalog.RegistryCatalog.discover → registry.discover.discover_workspace
  planner.stack_planner._gateway_proxy_code → planner.stack_planner._resolve_upstream
  planner.stack_planner._build_compose → registry.labels.build_service_labels
  planner.stack_planner.plan_stack → planner.stack_planner._build_compose
  interfaces.service._write_plan_output → planner.stack_artifacts.write_stack_artifacts
  interfaces.service.IterunService.schema → dsl.schema.get_json_schema
  interfaces.service.IterunService.validate_yaml → dsl.schema.validate_yaml_document
  interfaces.service.IterunService.parse → parser.dsl_parser.parse_dsl
  interfaces.service.IterunService.plan_ir → planner.simulator.plan_intent
  interfaces.service.IterunService.plan_yaml → parser.dsl_parser.parse_dsl
  interfaces.service.IterunService.plan_yaml → planner.simulator.plan_intent
  interfaces.service.IterunService.plan_yaml → interfaces.service._write_plan_output
  interfaces.service.IterunService.execute_ir → executor.runner.execute_intent
  interfaces.service.IterunService.registry_refresh → integrations.bridges.pipeline.refresh_registry
  interfaces.service.IterunService.registry_list → registry.catalog.discover_glob
  executor.runner.Executor.__init__ → config.get_config
  executor.runner.Executor.execute → integrations.pactown_runtime.execute_pactown
  executor.runner.Executor._validate_and_fix → executor.runner._filter_validation_endpoints
  executor.runner.stop_containers_for_intent → config.get_config
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
# code2llm call graph | /home/tom/github/wronai/iterun
# generated in 0.06s
# nodes: 143 | edges: 131 | modules: 36
# CC̄=4.6

HUBS[20]:
  registry.discover.discover_workspace
    CC=44  in:2  out:75  total:77
  integrations.pactown_runtime.execute_pactown
    CC=21  in:1  out:50  total:51
  cli.main.CLI.cmd_execute
    CC=37  in:0  out:37  total:37
  generator.pipeline.run_pipeline
    CC=33  in:0  out:37  total:37
  generator.contract_verify.verify_contract
    CC=16  in:1  out:32  total:33
  registry.discover._discover_artifacts
    CC=12  in:1  out:28  total:29
  examples._scripts.verify_expectations.verify
    CC=23  in:1  out:27  total:28
  generator.expectations.check_expectations
    CC=23  in:1  out:26  total:27
  planner.stack_artifacts.write_stack_artifacts
    CC=9  in:3  out:22  total:25
  cli.main.CLI.cmd_plan
    CC=11  in:0  out:24  total:24
  executor.runner.Executor.execute
    CC=18  in:0  out:22  total:22
  planner.stack_planner.plan_stack
    CC=18  in:1  out:21  total:22
  generator.intent_generator.IntentGenerator.generate
    CC=11  in:0  out:21  total:21
  cli.main.CLI.cmd_ai_suggest
    CC=11  in:0  out:21  total:21
  cli.main.CLI.cmd_ai_chat
    CC=12  in:0  out:18  total:18
  examples._scripts.intent_to_openapi.intent_to_openapi
    CC=8  in:1  out:17  total:18
  executor.runner.Executor._validate_and_fix
    CC=8  in:0  out:17  total:17
  generator.session.write_session_artifacts
    CC=5  in:1  out:16  total:17
  integrations.adapters.docker.DockerAdapter.enrich
    CC=16  in:0  out:16  total:16
  integrations.bridges.pipeline.refresh_registry
    CC=5  in:3  out:13  total:16

MODULES:
  ai_gateway.feedback_loop  [2 funcs]
    __init__  CC=3  out:1
    create_feedback_loop  CC=1  out:1
  ai_gateway.gateway  [4 funcs]
    __post_init__  CC=15  out:8
    complete  CC=1  out:2
    get_gateway  CC=3  out:1
    suggest_improvements  CC=1  out:2
  cli.main  [11 funcs]
    cmd_ai_apply  CC=8  out:10
    cmd_ai_chat  CC=12  out:18
    cmd_ai_health  CC=4  out:12
    cmd_ai_suggest  CC=11  out:21
    cmd_execute  CC=37  out:37
    cmd_load  CC=3  out:8
    cmd_models  CC=3  out:9
    cmd_new  CC=4  out:7
    cmd_parse  CC=2  out:4
    cmd_plan  CC=11  out:24
  config  [3 funcs]
    get_config  CC=2  out:1
    load_dotenv  CC=15  out:15
    reload_config  CC=1  out:2
  dsl.schema  [3 funcs]
    get_json_schema  CC=1  out:1
    get_system_prompt  CC=1  out:2
    validate_yaml_document  CC=10  out:8
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
    _parse_actions  CC=6  out:9
    main  CC=3  out:9
    verify  CC=23  out:27
  examples._verify  [1 funcs]
    write_intract_manifest  CC=0  out:0
  executor.runner  [6 funcs]
    __init__  CC=3  out:5
    _validate_and_fix  CC=8  out:17
    execute  CC=18  out:22
    _filter_validation_endpoints  CC=9  out:6
    execute_intent  CC=1  out:2
    stop_containers_for_intent  CC=5  out:6
  generator.contract_verify  [6 funcs]
    _endpoint_responding  CC=3  out:2
    _probe_path  CC=1  out:1
    readiness_paths  CC=5  out:2
    verify_contract  CC=16  out:32
    wait_for_service  CC=5  out:4
    write_contract_artifacts  CC=1  out:2
  generator.expectations  [2 funcs]
    check_expectations  CC=23  out:26
    load_and_check_expectations  CC=4  out:8
  generator.intent_generator  [4 funcs]
    __init__  CC=2  out:2
    generate  CC=11  out:21
    _build_user_prompt  CC=4  out:1
    extract_yaml_from_llm  CC=6  out:11
  generator.intract_manifest  [7 funcs]
    _parse_action_strings  CC=4  out:7
    _safe_id  CC=1  out:3
    _slug  CC=2  out:4
    build_intract_manifest  CC=6  out:11
    intent_to_intract_dict  CC=2  out:4
    parse_api_actions  CC=9  out:11
    write_intract_manifest  CC=1  out:5
  generator.pipeline  [6 funcs]
    _build_repair_prompt  CC=4  out:3
    _container_logs  CC=4  out:3
    _expectations_summary  CC=8  out:13
    _finalize  CC=3  out:4
    _write_plan_artifacts  CC=8  out:11
    run_pipeline  CC=33  out:37
  generator.session  [1 funcs]
    write_session_artifacts  CC=5  out:16
  generator.testql_scenario  [4 funcs]
    _probe_path  CC=1  out:1
    _startup_wait_ms  CC=7  out:3
    build_testql_scenario  CC=7  out:10
    write_testql_scenario  CC=2  out:7
  integrations.adapters.docker  [2 funcs]
    enrich  CC=16  out:16
    _running_iterun_containers  CC=11  out:8
  integrations.adapters.filesystem  [1 funcs]
    collect  CC=1  out:1
  integrations.bridges.pipeline  [2 funcs]
    refresh_registry  CC=5  out:13
    refresh_registry_from_pipeline  CC=2  out:2
  integrations.markpact_pack  [2 funcs]
    _run_command_for_ir  CC=8  out:0
    pack_workspace  CC=18  out:12
  integrations.pactown_config  [3 funcs]
    _health_path  CC=8  out:0
    build_pactown_config  CC=12  out:6
    write_pactown_config  CC=1  out:4
  integrations.pactown_runtime  [3 funcs]
    _validate_urls  CC=6  out:10
    execute_pactown  CC=21  out:50
    stop_pactown_for_intent  CC=5  out:6
  integrations.runtime_stop  [1 funcs]
    stop_runtime_for_intent  CC=3  out:4
  interfaces.service  [9 funcs]
    execute_ir  CC=3  out:4
    parse  CC=1  out:1
    plan_ir  CC=1  out:1
    plan_yaml  CC=3  out:6
    registry_list  CC=1  out:1
    registry_refresh  CC=1  out:1
    schema  CC=1  out:1
    validate_yaml  CC=4  out:3
    _write_plan_output  CC=7  out:14
  parser.dsl_parser  [2 funcs]
    parse_dsl  CC=1  out:2
    parse_dsl_file  CC=1  out:2
  planner.simulator  [4 funcs]
    _generate_fastapi_code  CC=5  out:7
    _generate_flask_code  CC=5  out:5
    _endpoint_to_func_name  CC=5  out:10
    plan_intent  CC=3  out:3
  planner.stack_artifacts  [1 funcs]
    write_stack_artifacts  CC=9  out:22
  planner.stack_planner  [4 funcs]
    _build_compose  CC=9  out:4
    _gateway_proxy_code  CC=10  out:12
    _resolve_upstream  CC=12  out:2
    plan_stack  CC=18  out:21
  registry.catalog  [2 funcs]
    discover  CC=1  out:1
    discover_glob  CC=7  out:11
  registry.discover  [6 funcs]
    _discover_artifacts  CC=12  out:28
    _intent_from_workspace  CC=8  out:7
    _load_session  CC=3  out:3
    _load_stack_urls  CC=3  out:3
    _phase_from_session  CC=7  out:5
    discover_workspace  CC=44  out:75
  registry.labels  [1 funcs]
    build_service_labels  CC=4  out:0
  sdk.client  [3 funcs]
    parse  CC=3  out:6
    schema  CC=2  out:5
    validate  CC=5  out:4
  web.app  [22 funcs]
    _get_service  CC=2  out:1
    ai_apply_suggestions  CC=4  out:7
    ai_chat  CC=4  out:7
    ai_complete  CC=3  out:6
    ai_status  CC=2  out:5
    ai_suggest  CC=6  out:8
    execute  CC=5  out:5
    generate_and_run_api  CC=1  out:2
    generate_code  CC=3  out:6
    generate_intent_api  CC=3  out:4

EDGES:
  generator.expectations.check_expectations → generator.intract_manifest.parse_api_actions
  generator.expectations.load_and_check_expectations → generator.expectations.check_expectations
  generator.testql_scenario.build_testql_scenario → generator.intract_manifest.parse_api_actions
  generator.testql_scenario.build_testql_scenario → generator.testql_scenario._startup_wait_ms
  generator.testql_scenario.build_testql_scenario → generator.testql_scenario._probe_path
  generator.testql_scenario.write_testql_scenario → generator.testql_scenario.build_testql_scenario
  examples._scripts.verify_expectations.verify → examples._scripts.verify_expectations._load_yaml
  examples._scripts.verify_expectations.verify → examples._scripts.verify_expectations._parse_actions
  examples._scripts.verify_expectations.main → examples._scripts.verify_expectations.verify
  examples._scripts.annotate_intract._comment → examples._scripts.annotate_intract._slug
  examples._scripts.annotate_intract.annotate_python → examples._scripts.annotate_intract._actions
  examples._scripts.annotate_intract.annotate_express → examples._scripts.annotate_intract._actions
  examples._scripts.annotate_intract.main → examples._scripts.annotate_intract.annotate_python
  examples._scripts.annotate_intract.main → examples._scripts.annotate_intract.annotate_express
  examples._scripts.intent_to_testql.main → generator.testql_scenario.write_testql_scenario
  examples._scripts.intent_to_intract.main → examples._verify.write_intract_manifest
  examples._scripts.intent_to_openapi.intent_to_openapi → examples._scripts.intent_to_openapi._slug
  examples._scripts.intent_to_openapi.main → examples._scripts.intent_to_openapi.intent_to_openapi
  ai_gateway.gateway.GatewayConfig.__post_init__ → config.get_config
  ai_gateway.gateway.complete → ai_gateway.gateway.get_gateway
  ai_gateway.gateway.suggest_improvements → ai_gateway.gateway.get_gateway
  ai_gateway.feedback_loop.FeedbackLoop.__init__ → ai_gateway.gateway.get_gateway
  generator.intract_manifest.parse_api_actions → generator.intract_manifest._parse_action_strings
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest._safe_id
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest.parse_api_actions
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest._slug
  generator.intract_manifest.intent_to_intract_dict → generator.intract_manifest.build_intract_manifest
  generator.intract_manifest.write_intract_manifest → generator.intract_manifest.intent_to_intract_dict
  planner.simulator.Planner._generate_fastapi_code → planner.simulator._endpoint_to_func_name
  planner.simulator.Planner._generate_flask_code → planner.simulator._endpoint_to_func_name
  planner.simulator.plan_intent → planner.stack_planner.plan_stack
  registry.catalog.RegistryCatalog.discover → registry.discover.discover_workspace
  planner.stack_planner._gateway_proxy_code → planner.stack_planner._resolve_upstream
  planner.stack_planner._build_compose → registry.labels.build_service_labels
  planner.stack_planner.plan_stack → planner.stack_planner._build_compose
  interfaces.service._write_plan_output → planner.stack_artifacts.write_stack_artifacts
  interfaces.service.IterunService.schema → dsl.schema.get_json_schema
  interfaces.service.IterunService.validate_yaml → dsl.schema.validate_yaml_document
  interfaces.service.IterunService.parse → parser.dsl_parser.parse_dsl
  interfaces.service.IterunService.plan_ir → planner.simulator.plan_intent
  interfaces.service.IterunService.plan_yaml → parser.dsl_parser.parse_dsl
  interfaces.service.IterunService.plan_yaml → planner.simulator.plan_intent
  interfaces.service.IterunService.plan_yaml → interfaces.service._write_plan_output
  interfaces.service.IterunService.execute_ir → executor.runner.execute_intent
  interfaces.service.IterunService.registry_refresh → integrations.bridges.pipeline.refresh_registry
  interfaces.service.IterunService.registry_list → registry.catalog.discover_glob
  executor.runner.Executor.__init__ → config.get_config
  executor.runner.Executor.execute → integrations.pactown_runtime.execute_pactown
  executor.runner.Executor._validate_and_fix → executor.runner._filter_validation_endpoints
  executor.runner.stop_containers_for_intent → config.get_config
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 125f 12031L | python:59,shell:27,txt:20,yaml:17,toml:1 | 2026-06-06
# generated in 0.02s
# CC̅=4.6 | critical:18/337 | dups:0 | cycles:1

HEALTH[20]:
  🔴 GOD   ai_gateway/gateway.py = 644L, 4 classes, 20m, max CC=15
  🔴 GOD   executor/runner.py = 776L, 4 classes, 24m, max CC=18
  🔴 GOD   web/app.py = 597L, 11 classes, 32m, max CC=6
  🟡 CC    check_expectations CC=23 (limit:15)
  🟡 CC    verify CC=23 (limit:15)
  🟡 CC    __post_init__ CC=15 (limit:15)
  🟡 CC    suggest_next_steps CC=17 (limit:15)
  🟡 CC    plan_stack CC=18 (limit:15)
  🟡 CC    execute CC=18 (limit:15)
  🟡 CC    pack_workspace CC=18 (limit:15)
  🟡 CC    _collect_endpoints CC=18 (limit:15)
  🟡 CC    execute_pactown CC=21 (limit:15)
  🟡 CC    enrich CC=16 (limit:15)
  🟡 CC    discover_workspace CC=44 (limit:15)
  🟡 CC    verify_contract CC=16 (limit:15)
  🟡 CC    load_dotenv CC=15 (limit:15)
  🟡 CC    _validate CC=21 (limit:15)
  🟡 CC    cmd_execute CC=37 (limit:15)
  🟡 CC    interactive_mode CC=30 (limit:15)
  🟡 CC    main CC=92 (limit:15)

REFACTOR[5]:
  1. split ai_gateway/gateway.py  (god module)
  2. split executor/runner.py  (god module)
  3. split web/app.py  (god module)
  4. split 17 high-CC methods  (CC>15)
  5. break 1 circular dependencies

PIPELINES[190]:
  [1] Src [main]: main → verify → _load_yaml
      PURITY: 100% pure
  [2] Src [main]: main → annotate_python → _actions
      PURITY: 100% pure
  [3] Src [main]: main → write_testql_scenario → build_testql_scenario → parse_api_actions → ...(1 more)
      PURITY: 100% pure
  [4] Src [main]: main → write_intract_manifest
      PURITY: 100% pure
  [5] Src [main]: main → intent_to_openapi → _slug
      PURITY: 100% pure
  [6] Src [__post_init__]: __post_init__ → get_config
      PURITY: 100% pure
  [7] Src [litellm_model_id]: litellm_model_id
      PURITY: 100% pure
  [8] Src [get_available_models]: get_available_models
      PURITY: 100% pure
  [9] Src [to_dict]: to_dict
      PURITY: 100% pure
  [10] Src [__init__]: __init__
      PURITY: 100% pure
  [11] Src [complete]: complete
      PURITY: 100% pure
  [12] Src [acomplete]: acomplete
      PURITY: 100% pure
  [13] Src [suggest_improvements]: suggest_improvements
      PURITY: 100% pure
  [14] Src [generate_code_snippet]: generate_code_snippet
      PURITY: 100% pure
  [15] Src [explain_error]: explain_error
      PURITY: 100% pure
  [16] Src [list_models]: list_models
      PURITY: 100% pure
  [17] Src [health_check]: health_check
      PURITY: 100% pure
  [18] Src [complete]: complete → get_gateway
      PURITY: 100% pure
  [19] Src [suggest_improvements]: suggest_improvements → get_gateway
      PURITY: 100% pure
  [20] Src [to_dict]: to_dict
      PURITY: 100% pure
  [21] Src [__init__]: __init__ → get_gateway
      PURITY: 100% pure
  [22] Src [analyze]: analyze
      PURITY: 100% pure
  [23] Src [apply_suggestions]: apply_suggestions
      PURITY: 100% pure
  [24] Src [iterate]: iterate
      PURITY: 100% pure
  [25] Src [suggest_next_steps]: suggest_next_steps
      PURITY: 100% pure
  [26] Src [_build_analysis_prompt]: _build_analysis_prompt
      PURITY: 100% pure
  [27] Src [_parse_suggestions]: _parse_suggestions
      PURITY: 100% pure
  [28] Src [_extract_action]: _extract_action
      PURITY: 100% pure
  [29] Src [_parse_action]: _parse_action
      PURITY: 100% pure
  [30] Src [_process_user_feedback]: _process_user_feedback
      PURITY: 100% pure
  [31] Src [analyze_intent]: analyze_intent
      PURITY: 100% pure
  [32] Src [__getattr__]: __getattr__
      PURITY: 100% pure
  [33] Src [write_intract_manifest]: write_intract_manifest → intent_to_intract_dict → build_intract_manifest → _safe_id
      PURITY: 100% pure
  [34] Src [add_log]: add_log
      PURITY: 100% pure
  [35] Src [to_dict]: to_dict
      PURITY: 100% pure
  [36] Src [dry_run]: dry_run
      PURITY: 100% pure
  [37] Src [_generate_python_code]: _generate_python_code
      PURITY: 100% pure
  [38] Src [_generate_fastapi_code]: _generate_fastapi_code → _endpoint_to_func_name
      PURITY: 100% pure
  [39] Src [_generate_flask_code]: _generate_flask_code → _endpoint_to_func_name
      PURITY: 100% pure
  [40] Src [_generate_node_code]: _generate_node_code
      PURITY: 100% pure
  [41] Src [_generate_express_code]: _generate_express_code
      PURITY: 100% pure
  [42] Src [_generate_dockerfile]: _generate_dockerfile
      PURITY: 100% pure
  [43] Src [_simulate_action]: _simulate_action
      PURITY: 100% pure
  [44] Src [_estimate_resources]: _estimate_resources
      PURITY: 100% pure
  [45] Src [__init__]: __init__
      PURITY: 100% pure
  [46] Src [discover]: discover → discover_workspace → _load_session
      PURITY: 100% pure
  [47] Src [load]: load
      PURITY: 100% pure
  [48] Src [refresh]: refresh
      PURITY: 100% pure
  [49] Src [write]: write
      PURITY: 100% pure
  [50] Src [summary]: summary
      PURITY: 100% pure

LAYERS:
  cli/                            CC̄=10.6   ←in:0  →out:22  !! split
  │ !! main                       994L  2C   25m  CC=92     ←0
  │ __init__                    20L  0C    1m  CC=3      ←0
  │ __main__                     4L  0C    0m  CC=0.0    ←0
  │
  integrations/                   CC̄=7.1    ←in:3  →out:3
  │ !! pactown_runtime            195L  0C    4m  CC=21     ←2
  │ !! markpact_pack              104L  0C    2m  CC=18     ←2
  │ !! docker                      79L  1C    3m  CC=16     ←0
  │ backstage                   74L  1C    1m  CC=5      ←0
  │ pactown_config              70L  0C    3m  CC=12     ←1
  │ pipeline                    49L  0C    2m  CC=5      ←3
  │ base                        29L  2C    3m  CC=1      ←0
  │ opentelemetry               28L  1C    1m  CC=5      ←0
  │ runtime_stop                22L  0C    1m  CC=3      ←1
  │ __init__                    18L  0C    0m  CC=0.0    ←0
  │ filesystem                  16L  1C    1m  CC=1      ←0
  │ __init__                    14L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  registry/                       CC̄=6.2    ←in:5  →out:0
  │ !! discover                   273L  0C    7m  CC=44     ←2
  │ models                     103L  8C    1m  CC=1      ←0
  │ catalog                     71L  1C    7m  CC=7      ←2
  │ labels                      53L  0C    2m  CC=4      ←3
  │ __init__                    13L  0C    0m  CC=0.0    ←0
  │
  executor/                       CC̄=5.8    ←in:6  →out:4
  │ !! runner                     776L  4C   24m  CC=18     ←6
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  generator/                      CC̄=5.7    ←in:2  →out:12  !! split
  │ !! pipeline                   277L  1C    7m  CC=33     ←0
  │ intent_generator           238L  3C    7m  CC=11     ←0
  │ !! contract_verify            228L  1C   10m  CC=16     ←1
  │ intract_manifest           119L  0C    7m  CC=9      ←3
  │ !! expectations                96L  0C    4m  CC=23     ←1
  │ testql_scenario             79L  0C    4m  CC=7      ←4
  │ session                     52L  0C    1m  CC=5      ←1
  │ __init__                    23L  0C    0m  CC=0.0    ←0
  │
  planner/                        CC̄=5.3    ←in:8  →out:1
  │ simulator                  384L  2C   17m  CC=9      ←4
  │ !! stack_planner              226L  0C    5m  CC=18     ←1
  │ stack_artifacts             66L  0C    1m  CC=9      ←3
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  parser/                         CC̄=5.2    ←in:11  →out:0
  │ !! dsl_parser                 330L  3C   14m  CC=21     ←6
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  ai_gateway/                     CC̄=4.6    ←in:14  →out:1
  │ !! gateway                    644L  4C   20m  CC=15     ←4
  │ !! feedback_loop              384L  3C   14m  CC=17     ←2
  │ __init__                    34L  0C    0m  CC=0.0    ←0
  │
  dsl/                            CC̄=3.2    ←in:8  →out:1
  │ schema                     250L  7C    6m  CC=10     ←4
  │ __init__                    17L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=3.1    ←in:0  →out:0
  │ !! planfile.yaml             1085L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ Makefile                   222L  0C    0m  CC=0.0    ←0
  │ !! config                     171L  1C    8m  CC=15     ←5
  │ run.sh                     160L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             109L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                82L  0C    0m  CC=0.0    ←0
  │ project.sh                  59L  0C    0m  CC=0.0    ←0
  │ pyqual.yaml                 55L  0C    0m  CC=0.0    ←0
  │ requirements.txt            20L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │
  web/                            CC̄=2.5    ←in:0  →out:12  !! split
  │ !! app                        597L  11C   32m  CC=6      ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  interfaces/                     CC̄=2.3    ←in:1  →out:10  !! split
  │ service                    252L  1C   14m  CC=7      ←1
  │ models                      52L  7C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │
  sdk/                            CC̄=2.2    ←in:0  →out:4
  │ client                     225L  1C   16m  CC=5      ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=1.7    ←in:4  →out:0
  │ _verify.sh                 165L  0C   13m  CC=0.0    ←4
  │ _common.sh                 148L  0C   11m  CC=0.0    ←0
  │ !! verify_expectations        127L  0C    5m  CC=23     ←0
  │ annotate_intract            97L  0C    6m  CC=7      ←0
  │ intent_to_openapi           76L  0C    3m  CC=8      ←0
  │ _bootstrap_deps.sh          63L  0C    4m  CC=0.0    ←0
  │ run.sh                      41L  0C    0m  CC=0.0    ←0
  │ run-resilience.sh           41L  0C    0m  CC=0.0    ←0
  │ iterun.yaml                 39L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           31L  0C    0m  CC=0.0    ←0
  │ run-stacks.sh               30L  0C    0m  CC=0.0    ←0
  │ intent_to_intract           29L  0C    1m  CC=3      ←0
  │ expectations.yaml           27L  0C    0m  CC=0.0    ←0
  │ intent_to_testql            26L  0C    1m  CC=1      ←0
  │ expectations.yaml           26L  0C    0m  CC=0.0    ←0
  │ iterun.yaml                 26L  0C    0m  CC=0.0    ←0
  │ run-all.sh                  24L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           24L  0C    0m  CC=0.0    ←0
  │ run-e2e.sh                  24L  0C    0m  CC=0.0    ←0
  │ run.sh                      23L  0C    0m  CC=0.0    ←0
  │ run.sh                      22L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           20L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           20L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           19L  0C    0m  CC=0.0    ←0
  │ run.sh                      19L  0C    0m  CC=0.0    ←0
  │ run.sh                      18L  0C    0m  CC=0.0    ←0
  │ run.sh                      17L  0C    0m  CC=0.0    ←0
  │ run.sh                      16L  0C    0m  CC=0.0    ←0
  │ run.sh                      16L  0C    0m  CC=0.0    ←0
  │ run.sh                      16L  0C    0m  CC=0.0    ←0
  │ run.sh                      14L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           13L  0C    0m  CC=0.0    ←0
  │ run.sh                      13L  0C    0m  CC=0.0    ←0
  │ run-generate.sh             12L  0C    0m  CC=0.0    ←0
  │ run.sh                      11L  0C    0m  CC=0.0    ←0
  │ run.sh                      10L  0C    0m  CC=0.0    ←0
  │ run.sh                       9L  0C    0m  CC=0.0    ←0
  │ run.sh                       9L  0C    0m  CC=0.0    ←0
  │ run.sh                       8L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   5L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   5L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   4L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │
  ir/                             CC̄=1.7    ←in:0  →out:0
  │ models                     298L  10C   18m  CC=5      ←0
  │ __init__                     9L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-from-pytests.testql.toon.yaml    42L  0C    0m  CC=0.0    ←0
  │ generated-api-smoke.testql.toon.yaml    40L  0C    0m  CC=0.0    ←0
  │ generated-api-integration.testql.toon.yaml    18L  0C    0m  CC=0.0    ←0
  │
  iterun_mcp/                     CC̄=0.0    ←in:0  →out:0
  │ server                     145L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │

COUPLING:
                                         cli            ai_gateway             generator                   web            interfaces                parser              executor                   dsl               planner                config          integrations              registry              examples                   sdk  integrations.bridges
                   cli                    ──                     6                     1                                           1                     3                     1                     2                     2                     3                                           1                     1                                           1  !! fan-out
            ai_gateway                    ←6                    ──                    ←1                    ←7                                                                                                                                   1                                                                                                                hub
             generator                    ←1                     1                    ──                                                                 1                     1                     2                     2                                           2                                           2                                           1  !! fan-out
                   web                                           7                                          ──                                           2                     1                                           1                     1                                                                                                                !! fan-out
            interfaces                    ←1                                                                                      ──                     2                     1                     2                     3                                                                 1                                                                 1  !! fan-out
                parser                    ←3                                          ←1                    ←2                    ←2                    ──                                          ←1                                                                                                                                  ←2                        hub
              executor                    ←1                                          ←1                    ←1                    ←1                                          ──                                                                 2                     1                     1                                                                    hub
                   dsl                    ←2                                          ←2                                          ←2                     1                                          ──                                                                                                                                  ←2                        hub
               planner                    ←2                                          ←2                    ←1                    ←3                                                                                      ──                                                                 1                                                                    hub
                config                    ←3                    ←1                                          ←1                                                                ←2                                                                ──                    ←1                                                                                          hub
          integrations                                                                ←2                                                                                       2                                                                 1                    ──                                                                                        
              registry                    ←1                                                                                      ←1                                          ←1                                          ←1                                                                ──                                                                    hub
              examples                    ←1                                          ←2                                                                                                                                                                                                                          ──                                            
                   sdk                                                                                                                                   2                                           2                                                                                                                                  ──                      
  integrations.bridges                    ←1                                          ←1                                          ←1                                                                                                                                                                                                                          ──
  CYCLES: 1
  HUB: parser/ (fan-in=11)
  HUB: ai_gateway/ (fan-in=14)
  HUB: registry/ (fan-in=5)
  HUB: dsl/ (fan-in=8)
  HUB: planner/ (fan-in=8)
  HUB: executor/ (fan-in=6)
  HUB: config/ (fan-in=8)
  SMELL: interfaces/ fan-out=10 → split needed
  SMELL: cli/ fan-out=22 → split needed
  SMELL: web/ fan-out=12 → split needed
  SMELL: generator/ fan-out=12 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 6 groups | 77f 9271L | 2026-06-06

SUMMARY:
  files_scanned: 77
  total_lines:   9271
  dup_groups:    6
  dup_fragments: 104
  saved_lines:   310
  scan_ms:       2632

HOTSPOTS[7] (files with most duplication):
  examples/14-resilience-inventory/generated/app.py  dup=51L  groups=1  frags=17  (0.6%)
  examples/15-resilience-nested-paths/generated/app.py  dup=39L  groups=1  frags=13  (0.4%)
  examples/01-user-api/generated/app.py  dup=21L  groups=1  frags=7  (0.2%)
  examples/08-llm-generate/generated/app.py  dup=21L  groups=1  frags=7  (0.2%)
  examples/10-e2e-user-crud-verify/generated/app.py  dup=21L  groups=1  frags=7  (0.2%)
  examples/13-resilience-vague/generated/app.py  dup=21L  groups=1  frags=7  (0.2%)
  examples/16-resilience-framework-trap/generated/app.py  dup=21L  groups=1  frags=7  (0.2%)

DUPLICATES[6] (ranked by impact):
  [032a6ddde45774c9] !! STRU  ping  L=3 N=91 saved=270 sim=1.00
      examples/01-user-api/generated/app.py:9-11  (ping)
      examples/01-user-api/generated/app.py:14-16  (health)
      examples/01-user-api/generated/app.py:19-21  (users)
      examples/01-user-api/generated/app.py:24-26  (users_post)
      examples/01-user-api/generated/app.py:29-31  (users_by_id)
      examples/01-user-api/generated/app.py:34-36  (users_by_id_put)
      examples/01-user-api/generated/app.py:39-41  (users_by_id_delete)
      examples/02-ping-smoke/generated/app.py:9-11  (ping)
      examples/02-ping-smoke/generated/app.py:14-16  (health)
      examples/05-ir-show/generated/app.py:9-11  (ping)
      examples/05-ir-show/generated/app.py:14-16  (health)
      examples/06-iterate-workflow/generated/app.py:9-11  (ping)
      examples/07-execution-smoke/generated/app.py:9-11  (ping)
      examples/07-execution-smoke/generated/app.py:14-16  (health)
      examples/08-llm-generate/generated/app.py:9-11  (ping)
      examples/08-llm-generate/generated/app.py:14-16  (health)
      examples/08-llm-generate/generated/app.py:19-21  (users)
      examples/08-llm-generate/generated/app.py:24-26  (users_post)
      examples/08-llm-generate/generated/app.py:29-31  (users_by_id)
      examples/08-llm-generate/generated/app.py:34-36  (users_by_id_put)
      examples/08-llm-generate/generated/app.py:39-41  (users_by_id_delete)
      examples/09-e2e-ping-verify/generated/app.py:10-12  (ping)
      examples/09-e2e-ping-verify/generated/app.py:16-18  (health)
      examples/10-e2e-user-crud-verify/generated/app.py:10-12  (ping)
      examples/10-e2e-user-crud-verify/generated/app.py:16-18  (health)
      examples/10-e2e-user-crud-verify/generated/app.py:22-24  (users)
      examples/10-e2e-user-crud-verify/generated/app.py:28-30  (users_post)
      examples/10-e2e-user-crud-verify/generated/app.py:34-36  (users_by_id)
      examples/10-e2e-user-crud-verify/generated/app.py:40-42  (users_by_id_put)
      examples/10-e2e-user-crud-verify/generated/app.py:46-48  (users_by_id_delete)
      examples/12-e2e-full-gate/generated/app.py:10-12  (ping)
      examples/12-e2e-full-gate/generated/app.py:16-18  (health)
      examples/12-e2e-full-gate/generated/app.py:22-24  (products)
      examples/12-e2e-full-gate/generated/app.py:28-30  (products_post)
      examples/12-e2e-full-gate/generated/app.py:34-36  (products_by_id)
      examples/12-e2e-full-gate/generated/app.py:40-42  (metrics)
      examples/13-resilience-vague/generated/app.py:10-12  (ping)
      examples/13-resilience-vague/generated/app.py:16-18  (health)
      examples/13-resilience-vague/generated/app.py:22-24  (users)
      examples/13-resilience-vague/generated/app.py:28-30  (users_post)
      examples/13-resilience-vague/generated/app.py:34-36  (users_by_id)
      examples/13-resilience-vague/generated/app.py:40-42  (users_by_id_put)
      examples/13-resilience-vague/generated/app.py:46-48  (users_by_id_delete)
      examples/14-resilience-inventory/generated/app.py:10-12  (ping)
      examples/14-resilience-inventory/generated/app.py:16-18  (health)
      examples/14-resilience-inventory/generated/app.py:22-24  (products)
      examples/14-resilience-inventory/generated/app.py:28-30  (products_post)
      examples/14-resilience-inventory/generated/app.py:34-36  (products_by_id)
      examples/14-resilience-inventory/generated/app.py:40-42  (products_by_id_put)
      examples/14-resilience-inventory/generated/app.py:46-48  (products_by_id_delete)
      examples/14-resilience-inventory/generated/app.py:52-54  (categories)
      examples/14-resilience-inventory/generated/app.py:58-60  (categories_post)
      examples/14-resilience-inventory/generated/app.py:64-66  (categories_by_id)
      examples/14-resilience-inventory/generated/app.py:70-72  (categories_by_id_put)
      examples/14-resilience-inventory/generated/app.py:76-78  (categories_by_id_delete)
      examples/14-resilience-inventory/generated/app.py:82-84  (suppliers)
      examples/14-resilience-inventory/generated/app.py:88-90  (suppliers_post)
      examples/14-resilience-inventory/generated/app.py:94-96  (suppliers_by_id)
      examples/14-resilience-inventory/generated/app.py:100-102  (suppliers_by_id_put)
      examples/14-resilience-inventory/generated/app.py:106-108  (suppliers_by_id_delete)
      examples/15-resilience-nested-paths/generated/app.py:10-12  (ping)
      examples/15-resilience-nested-paths/generated/app.py:16-18  (health)
      examples/15-resilience-nested-paths/generated/app.py:22-24  (orders)
      examples/15-resilience-nested-paths/generated/app.py:28-30  (orders_post)
      examples/15-resilience-nested-paths/generated/app.py:34-36  (orders_by_order_id)
      examples/15-resilience-nested-paths/generated/app.py:40-42  (orders_by_order_id_status)
      examples/15-resilience-nested-paths/generated/app.py:46-48  (orders_by_order_id_delete)
      examples/15-resilience-nested-paths/generated/app.py:52-54  (customers)
      examples/15-resilience-nested-paths/generated/app.py:58-60  (customers_post)
      examples/15-resilience-nested-paths/generated/app.py:64-66  (customers_by_customer_id)
      examples/15-resilience-nested-paths/generated/app.py:70-72  (customers_by_customer_id_put)
      examples/15-resilience-nested-paths/generated/app.py:76-78  (customers_by_customer_id_delete)
      examples/15-resilience-nested-paths/generated/app.py:82-84  (customers_by_customer_id_orders)
      examples/16-resilience-framework-trap/generated/app.py:10-12  (live)
      examples/16-resilience-framework-trap/generated/app.py:16-18  (ready)
      examples/16-resilience-framework-trap/generated/app.py:22-24  (api_v1_items)
      examples/16-resilience-framework-trap/generated/app.py:28-30  (api_v1_items_post)
      examples/16-resilience-framework-trap/generated/app.py:34-36  (api_v1_items_by_sku)
      examples/16-resilience-framework-trap/generated/app.py:40-42  (api_v1_items_by_sku_put)
      examples/16-resilience-framework-trap/generated/app.py:46-48  (api_v1_items_by_sku_delete)
      examples/17-stack-shop-gateway/generated/services/users-service/app.py:9-11  (health)
      examples/17-stack-shop-gateway/generated/services/users-service/app.py:14-16  (users)
      examples/18-stack-blog/generated/services/blog-worker/app.py:9-11  (health)
      examples/18-stack-blog/generated/services/blog-worker/app.py:14-16  (jobs)
      generated/app.py:9-11  (ping)
      generated/app.py:14-16  (health)
      generated/app.py:19-21  (users)
      generated/app.py:24-26  (users_post)
      generated/app.py:29-31  (users_by_id)
      generated/app.py:34-36  (users_by_id_put)
      generated/app.py:39-41  (users_by_id_delete)
  [b0a8ffc5a9306a38]   STRU  users  L=8 N=4 saved=24 sim=1.00
      examples/17-stack-shop-gateway/generated/services/api-gateway/app.py:18-25  (users)
      examples/17-stack-shop-gateway/generated/services/api-gateway/app.py:28-35  (products)
      examples/18-stack-blog/generated/services/blog-api/app.py:18-25  (posts)
      examples/19-stack-api-cache/generated/services/api-service/app.py:18-25  (cache_status)
  [ad19acd787fb5e4b]   EXAC  _slug  L=3 N=3 saved=6 sim=1.00
      examples/_scripts/annotate_intract.py:13-15  (_slug)
      examples/_scripts/intent_to_openapi.py:13-15  (_slug)
      generator/intract_manifest.py:12-14  (_slug)
  [d1ab1a804f1b435b]   STRU  parse_dsl  L=4 N=2 saved=4 sim=1.00
      parser/dsl_parser.py:321-324  (parse_dsl)
      parser/dsl_parser.py:327-330  (parse_dsl_file)
  [f041dec9367328ca]   EXAC  add_log  L=3 N=2 saved=3 sim=1.00
      executor/runner.py:116-118  (add_log)
      planner/simulator.py:53-55  (add_log)
  [02262db14f1137ad]   STRU  list_interfaces  L=3 N=2 saved=3 sim=1.00
      web/app.py:111-113  (list_interfaces)
      web/app.py:166-168  (get_schema)

REFACTOR[6] (ranked by priority):
  [1] ○ extract_function   → utils/ping.py
      WHY: 91 occurrences of 3-line block across 16 files — saves 270 lines
      FILES: examples/01-user-api/generated/app.py, examples/02-ping-smoke/generated/app.py, examples/05-ir-show/generated/app.py, examples/06-iterate-workflow/generated/app.py, examples/07-execution-smoke/generated/app.py +11 more
  [2] ○ extract_function   → examples/utils/users.py
      WHY: 4 occurrences of 8-line block across 3 files — saves 24 lines
      FILES: examples/17-stack-shop-gateway/generated/services/api-gateway/app.py, examples/18-stack-blog/generated/services/blog-api/app.py, examples/19-stack-api-cache/generated/services/api-service/app.py
  [3] ○ extract_function   → utils/_slug.py
      WHY: 3 occurrences of 3-line block across 3 files — saves 6 lines
      FILES: examples/_scripts/annotate_intract.py, examples/_scripts/intent_to_openapi.py, generator/intract_manifest.py
  [4] ○ extract_function   → parser/utils/parse_dsl.py
      WHY: 2 occurrences of 4-line block across 1 files — saves 4 lines
      FILES: parser/dsl_parser.py
  [5] ○ extract_function   → utils/add_log.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: executor/runner.py, planner/simulator.py
  [6] ○ extract_function   → web/utils/list_interfaces.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: web/app.py

QUICK_WINS[3] (low risk, high savings — do first):
  [1] extract_function   saved=270L  → utils/ping.py
      FILES: app.py, app.py, app.py +13
  [2] extract_function   saved=24L  → examples/utils/users.py
      FILES: app.py, app.py, app.py
  [3] extract_function   saved=6L  → utils/_slug.py
      FILES: annotate_intract.py, intent_to_openapi.py, intract_manifest.py

DEPENDENCY_RISK[3] (duplicates spanning multiple packages):
  ping  packages=2  files=16
      examples/01-user-api/generated/app.py
      examples/02-ping-smoke/generated/app.py
      examples/05-ir-show/generated/app.py
      examples/06-iterate-workflow/generated/app.py
      +12 more
  _slug  packages=2  files=3
      examples/_scripts/annotate_intract.py
      examples/_scripts/intent_to_openapi.py
      generator/intract_manifest.py
  add_log  packages=2  files=2
      executor/runner.py
      planner/simulator.py

EFFORT_ESTIMATE (total ≈ 19.6h):
  hard   ping                                saved=270L  ~1080min
  medium users                               saved=24L  ~48min
  easy   _slug                               saved=6L  ~24min
  easy   parse_dsl                           saved=4L  ~8min
  easy   add_log                             saved=3L  ~12min
  easy   list_interfaces                     saved=3L  ~6min

METRICS-TARGET:
  dup_groups:  6 → 0
  saved_lines: 310 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 293 func | 36f | 2026-06-06
# generated in 0.00s

NEXT[10] (ranked by impact):
  [1] !! SPLIT           cli/main.py
      WHY: 994L, 2 classes, max CC=92
      EFFORT: ~4h  IMPACT: 91448

  [2] !! SPLIT           executor/runner.py
      WHY: 776L, 4 classes, max CC=18
      EFFORT: ~4h  IMPACT: 13968

  [3] !! SPLIT-FUNC      main  CC=92  fan=44
      WHY: CC=92 exceeds 15
      EFFORT: ~1h  IMPACT: 4048

  [4] !! SPLIT-FUNC      discover_workspace  CC=44  fan=35
      WHY: CC=44 exceeds 15
      EFFORT: ~1h  IMPACT: 1540

  [5] !! SPLIT-FUNC      run_pipeline  CC=33  fan=25
      WHY: CC=33 exceeds 15
      EFFORT: ~1h  IMPACT: 825

  [6] !! SPLIT-FUNC      CLI.interactive_mode  CC=30  fan=23
      WHY: CC=30 exceeds 15
      EFFORT: ~1h  IMPACT: 690

  [7] !  SPLIT-FUNC      execute_pactown  CC=21  fan=31
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 651

  [8] !! SPLIT-FUNC      CLI.cmd_execute  CC=37  fan=15
      WHY: CC=37 exceeds 15
      EFFORT: ~1h  IMPACT: 555

  [9] !  SPLIT-FUNC      verify_contract  CC=16  fan=26
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 416

  [10] !  SPLIT-FUNC      check_expectations  CC=23  fan=12
      WHY: CC=23 exceeds 15
      EFFORT: ~1h  IMPACT: 276


RISKS[3]:
  ⚠ Splitting planfile.yaml may break 0 import paths
  ⚠ Splitting cli/main.py may break 25 import paths
  ⚠ Splitting executor/runner.py may break 24 import paths

METRICS-TARGET:
  CC̄:          5.0 → ≤3.5
  max-CC:      92 → ≤20
  god-modules: 6 → 0
  high-CC(≥15): 17 → ≤8
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
  prev CC̄=4.6 → now CC̄=5.0
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
