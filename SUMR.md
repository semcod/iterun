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
- **version**: `0.1.11`
- **python_requires**: `>=3.11`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, requirements.txt, Makefile, testql(3), app.doql.less, pyqual.yaml, goal.yaml, .env.example, project/(5 analysis files)

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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

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

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 149f 12799L | python:82,shell:27,txt:20,yaml:18,toml:1 | 2026-06-06
# generated in 0.02s
# CC̅=3.8 | critical:0/421 | dups:0 | cycles:0

HEALTH[0]: ok

REFACTOR[0]: none needed

PIPELINES[199]:
  [1] Src [get_env]: get_env
      PURITY: 100% pure
  [2] Src [get_env_bool]: get_env_bool
      PURITY: 100% pure
  [3] Src [get_env_int]: get_env_int
      PURITY: 100% pure
  [4] Src [get_env_float]: get_env_float
      PURITY: 100% pure
  [5] Src [configure]: configure
      PURITY: 100% pure
  [6] Src [to_dict]: to_dict
      PURITY: 100% pure
  [7] Src [__init__]: __init__ → get_system_prompt → get_json_schema
      PURITY: 100% pure
  [8] Src [generate]: generate → _build_user_prompt
      PURITY: 100% pure
  [9] Src [to_dict]: to_dict
      PURITY: 100% pure
  [10] Src [main]: main → verify → _load_yaml
      PURITY: 100% pure
  [11] Src [main]: main → annotate_python → _actions
      PURITY: 100% pure
  [12] Src [main]: main → write_testql_scenario → build_testql_scenario → parse_api_actions → ...(1 more)
      PURITY: 100% pure
  [13] Src [main]: main → write_intract_manifest → intent_to_intract_dict → build_intract_manifest → ...(1 more)
      PURITY: 100% pure
  [14] Src [main]: main → intent_to_openapi → _slug
      PURITY: 100% pure
  [15] Src [add_log]: add_log
      PURITY: 100% pure
  [16] Src [to_dict]: to_dict
      PURITY: 100% pure
  [17] Src [dry_run]: dry_run
      PURITY: 100% pure
  [18] Src [_generate_python_code]: _generate_python_code
      PURITY: 100% pure
  [19] Src [_generate_fastapi_code]: _generate_fastapi_code → _endpoint_to_func_name
      PURITY: 100% pure
  [20] Src [_generate_flask_code]: _generate_flask_code → _endpoint_to_func_name
      PURITY: 100% pure
  [21] Src [_generate_node_code]: _generate_node_code
      PURITY: 100% pure
  [22] Src [_generate_express_code]: _generate_express_code
      PURITY: 100% pure
  [23] Src [_generate_dockerfile]: _generate_dockerfile
      PURITY: 100% pure
  [24] Src [_simulate_action]: _simulate_action
      PURITY: 100% pure
  [25] Src [_estimate_resources]: _estimate_resources
      PURITY: 100% pure
  [26] Src [home]: home
      PURITY: 100% pure
  [27] Src [health]: health
      PURITY: 100% pure
  [28] Src [list_interfaces]: list_interfaces → _get_service
      PURITY: 100% pure
  [29] Src [get_registry]: get_registry → _get_service
      PURITY: 100% pure
  [30] Src [refresh_registry_api]: refresh_registry_api → _get_service
      PURITY: 100% pure
  [31] Src [list_registries]: list_registries → _get_service
      PURITY: 100% pure
  [32] Src [health]: health
      PURITY: 100% pure
  [33] Src [ai_status]: ai_status → get_gateway
      PURITY: 100% pure
  [34] Src [list_models]: list_models → get_gateway
      PURITY: 100% pure
  [35] Src [ai_complete]: ai_complete → get_gateway
      PURITY: 100% pure
  [36] Src [ai_chat]: ai_chat → get_gateway
      PURITY: 100% pure
  [37] Src [ai_suggest]: ai_suggest → _intents_store
      PURITY: 100% pure
  [38] Src [ai_apply_suggestions]: ai_apply_suggestions → _intents_store
      PURITY: 100% pure
  [39] Src [generate_code]: generate_code → get_gateway
      PURITY: 100% pure
  [40] Src [get_schema]: get_schema → _get_service
      PURITY: 100% pure
  [41] Src [validate_yaml]: validate_yaml → _get_service
      PURITY: 100% pure
  [42] Src [generate_intent_api]: generate_intent_api → _get_service
      PURITY: 100% pure
  [43] Src [generate_and_run_api]: generate_and_run_api → run_pipeline_api → _get_service
      PURITY: 100% pure
  [44] Src [plan_yaml_api]: plan_yaml_api → parse_dsl
      PURITY: 100% pure
  [45] Src [parse_intent]: parse_intent → parse_dsl
      PURITY: 100% pure
  [46] Src [list_intents]: list_intents → _intents_store
      PURITY: 100% pure
  [47] Src [get_intent]: get_intent → _intents_store
      PURITY: 100% pure
  [48] Src [delete_intent]: delete_intent → _intents_store
      PURITY: 100% pure
  [49] Src [plan]: plan → _intents_store
      PURITY: 100% pure
  [50] Src [iterate]: iterate → _intents_store
      PURITY: 100% pure

LAYERS:
  cli/                            CC̄=5.6    ←in:0  →out:25  !! split
  │ shell                      480L  1C   24m  CC=12     ←0
  │ dispatch                   294L  0C   15m  CC=14     ←1
  │ main                        98L  0C    2m  CC=2      ←0
  │ shell_output                97L  0C    7m  CC=8      ←1
  │ shell_interactive           92L  0C    4m  CC=12     ←1
  │ plan_artifacts              42L  0C    1m  CC=7      ←1
  │ __init__                    20L  0C    1m  CC=3      ←0
  │ colors                      16L  1C    1m  CC=1      ←0
  │ __main__                     4L  0C    0m  CC=0.0    ←0
  │
  executor/                       CC̄=5.2    ←in:10  →out:5
  │ runner                     315L  1C   12m  CC=9      ←5
  │ docker_ops                 283L  0C    6m  CC=13     ←2
  │ pactown                    226L  0C   11m  CC=10     ←2
  │ validation                 184L  0C    4m  CC=13     ←3
  │ models                      75L  3C    6m  CC=3      ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  planner/                        CC̄=5.0    ←in:8  →out:1
  │ simulator                  377L  2C   16m  CC=9      ←0
  │ stack_planner              234L  0C    7m  CC=12     ←1
  │ stack_artifacts             66L  0C    1m  CC=9      ←3
  │ plan                        15L  0C    1m  CC=3      ←4
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │
  contracts/                      CC̄=4.8    ←in:6  →out:0
  │ expectations               108L  0C    8m  CC=7      ←2
  │ api_actions                 35L  0C    2m  CC=9      ←4
  │ __init__                    10L  0C    0m  CC=0.0    ←0
  │
  registry/                       CC̄=4.7    ←in:5  →out:0
  │ models                     103L  8C    1m  CC=1      ←0
  │ discover_artifacts          97L  0C    2m  CC=12     ←1
  │ discover_services           96L  0C    2m  CC=13     ←1
  │ discover_context            77L  1C    4m  CC=6      ←1
  │ catalog                     71L  1C    7m  CC=7      ←2
  │ discover_io                 65L  0C    4m  CC=8      ←1
  │ discover                    61L  0C    2m  CC=6      ←2
  │ labels                      53L  0C    2m  CC=4      ←3
  │ __init__                    13L  0C    0m  CC=0.0    ←0
  │
  integrations/                   CC̄=4.7    ←in:4  →out:3
  │ markpact_pack              115L  0C    4m  CC=12     ←2
  │ docker                      90L  1C    6m  CC=11     ←0
  │ backstage                   74L  1C    1m  CC=5      ←0
  │ pactown_config              70L  0C    3m  CC=12     ←1
  │ pipeline                    47L  0C    2m  CC=5      ←2
  │ base                        29L  2C    3m  CC=1      ←0
  │ opentelemetry               28L  1C    1m  CC=5      ←0
  │ filesystem                  17L  1C    1m  CC=1      ←0
  │ __init__                    15L  0C    0m  CC=0.0    ←0
  │ __init__                    14L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ runtime_stop                 0L  0C    1m  CC=3      ←1
  │
  generator/                      CC̄=4.5    ←in:5  →out:15  !! split
  │ pipeline                   358L  0C   12m  CC=11     ←1
  │ intent_generator           238L  3C    7m  CC=11     ←0
  │ contract_verify            236L  1C   13m  CC=10     ←1
  │ intract_manifest            92L  0C    5m  CC=6      ←4
  │ testql_scenario             79L  0C    4m  CC=7      ←4
  │ session                     51L  0C    1m  CC=5      ←1
  │ results                     37L  1C    1m  CC=2      ←0
  │ __init__                    24L  0C    0m  CC=0.0    ←0
  │
  parser/                         CC̄=4.3    ←in:10  →out:0
  │ dsl_parser                 337L  3C   18m  CC=14     ←5
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  ai_gateway/                     CC̄=4.0    ←in:14  →out:1
  │ feedback_loop              386L  3C   17m  CC=10     ←2
  │ gateway                    352L  1C   13m  CC=10     ←4
  │ model_catalog              290L  3C   10m  CC=7      ←0
  │ __init__                    30L  0C    0m  CC=0.0    ←0
  │
  dsl/                            CC̄=2.8    ←in:8  →out:0
  │ schema                     242L  7C    6m  CC=8      ←4
  │ __init__                    17L  0C    0m  CC=0.0    ←0
  │
  web/                            CC̄=2.4    ←in:0  →out:0
  │ intents                    280L  0C   19m  CC=6      ←0
  │ ai                         148L  0C    9m  CC=6      ←0
  │ schemas                     67L  11C    0m  CC=0.0    ←0
  │ app                         65L  0C    2m  CC=1      ←0
  │ registry                    48L  0C    6m  CC=2      ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  interfaces/                     CC̄=2.4    ←in:0  →out:11  !! split
  │ service                    261L  1C   14m  CC=7      ←0
  │ models                      52L  7C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=2.3    ←in:0  →out:0
  │ !! planfile.yaml             1319L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ Makefile                   222L  0C    0m  CC=0.0    ←0
  │ config                     182L  1C   12m  CC=5      ←8
  │ run.sh                     160L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             109L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                82L  0C    0m  CC=0.0    ←0
  │ project.sh                  59L  0C    0m  CC=0.0    ←0
  │ pyqual.yaml                 55L  0C    0m  CC=0.0    ←0
  │ requirements.txt            20L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │
  sdk/                            CC̄=2.2    ←in:0  →out:4
  │ client                     225L  1C   16m  CC=5      ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │
  ir/                             CC̄=1.7    ←in:0  →out:0
  │ models                     298L  10C   18m  CC=5      ←0
  │ __init__                     9L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=1.2    ←in:0  →out:0
  │ _verify.sh                 165L  0C   13m  CC=0.0    ←0
  │ _common.sh                 153L  0C   11m  CC=0.0    ←0
  │ annotate_intract            97L  0C    6m  CC=7      ←0
  │ intent_to_openapi           76L  0C    3m  CC=8      ←0
  │ verify_expectations         66L  0C    4m  CC=8      ←0
  │ _bootstrap_deps.sh          63L  0C    4m  CC=0.0    ←0
  │ run-resilience.sh           41L  0C    0m  CC=0.0    ←0
  │ run.sh                      41L  0C    0m  CC=0.0    ←0
  │ iterun.yaml                 39L  0C    0m  CC=0.0    ←0
  │ iterun.yaml                 37L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           31L  0C    0m  CC=0.0    ←0
  │ run-stacks.sh               30L  0C    0m  CC=0.0    ←0
  │ intent_to_intract           29L  0C    1m  CC=3      ←0
  │ expectations.yaml           27L  0C    0m  CC=0.0    ←0
  │ intent_to_testql            26L  0C    1m  CC=1      ←0
  │ iterun.yaml                 26L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           26L  0C    0m  CC=0.0    ←0
  │ run-all.sh                  24L  0C    0m  CC=0.0    ←0
  │ run-e2e.sh                  24L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           24L  0C    0m  CC=0.0    ←0
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
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-from-pytests.testql.toon.yaml    42L  0C    0m  CC=0.0    ←0
  │ generated-api-smoke.testql.toon.yaml    40L  0C    0m  CC=0.0    ←0
  │ generated-api-integration.testql.toon.yaml    18L  0C    0m  CC=0.0    ←0
  │
  iterun_mcp/                     CC̄=0.0    ←in:0  →out:0
  │ server                     145L  0C    0m  CC=0.0    ←0
  │
  mcp/                            CC̄=0.0    ←in:0  →out:0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     integrations/runtime_stop.py              0L
     mcp/__init__.py                           0L

COUPLING:
                                         cli             generator            ai_gateway              executor            web.routes            interfaces                config                parser               planner                   dsl          integrations             contracts              registry  integrations.bridges                   sdk
                   cli                    ──                     3                     6                     2                                                                 4                     3                     2                     2                                                                 1                     2                        !! fan-out
             generator                    ←3                    ──                     1                     2                                                                                       1                     2                     2                     2                     5                                                                    hub
            ai_gateway                    ←6                    ←1                    ──                                          ←7                                           1                                                                                                                                                                                  hub
              executor                    ←2                    ←2                                          ──                    ←3                    ←1                     2                                                                                       2                                           1                                              hub
            web.routes                                                                 7                     3                    ──                                           2                     2                     1                                                                                                                                      !! fan-out
            interfaces                                                                                       1                                          ──                                           2                     3                     2                                                                 1                     2                        !! fan-out
                config                    ←4                                          ←1                    ←2                    ←2                                          ──                                                                                      ←1                                                                                          hub
                parser                    ←3                    ←1                                                                ←2                    ←2                                          ──                                                                                                                                                        ←2  hub
               planner                    ←2                    ←2                                                                ←1                    ←3                                                                ──                                                                                       1                                              hub
                   dsl                    ←2                    ←2                                                                                      ←2                                                                                      ──                                                                                                            ←2  hub
          integrations                                          ←2                                           2                                                                 1                                                                                      ──                                                                                        
             contracts                                          ←5                                                                                                                                                                                                                          ──                                                                    hub
              registry                    ←1                                                                ←1                                          ←1                                                                ←1                                                                                      ──                                              hub
  integrations.bridges                    ←2                                                                                                            ←2                                                                                                                                                                              ──                      
                   sdk                                                                                                                                                                               2                                           2                                                                                                            ──
  CYCLES: none
  HUB: executor/ (fan-in=10)
  HUB: dsl/ (fan-in=8)
  HUB: generator/ (fan-in=5)
  HUB: config/ (fan-in=10)
  HUB: contracts/ (fan-in=6)
  HUB: planner/ (fan-in=8)
  HUB: registry/ (fan-in=5)
  HUB: parser/ (fan-in=10)
  HUB: ai_gateway/ (fan-in=14)
  SMELL: generator/ fan-out=15 → split needed
  SMELL: web.routes/ fan-out=15 → split needed
  SMELL: cli/ fan-out=25 → split needed
  SMELL: interfaces/ fan-out=11 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 5 groups | 100f 9768L | 2026-06-06

SUMMARY:
  files_scanned: 100
  total_lines:   9768
  dup_groups:    5
  dup_fragments: 99
  saved_lines:   302
  scan_ms:       2646

HOTSPOTS[7] (files with most duplication):
  examples/14-resilience-inventory/generated/app.py  dup=51L  groups=1  frags=17  (0.5%)
  examples/15-resilience-nested-paths/generated/app.py  dup=36L  groups=1  frags=12  (0.4%)
  examples/01-user-api/generated/app.py  dup=21L  groups=1  frags=7  (0.2%)
  examples/08-llm-generate/generated/app.py  dup=21L  groups=1  frags=7  (0.2%)
  examples/10-e2e-user-crud-verify/generated/app.py  dup=21L  groups=1  frags=7  (0.2%)
  examples/16-resilience-framework-trap/generated/app.py  dup=21L  groups=1  frags=7  (0.2%)
  generated/app.py  dup=21L  groups=1  frags=7  (0.2%)

DUPLICATES[5] (ranked by impact):
  [032a6ddde45774c9] !! STRU  ping  L=3 N=88 saved=261 sim=1.00
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
      examples/15-resilience-nested-paths/generated/app.py:40-42  (orders_by_order_id_put)
      examples/15-resilience-nested-paths/generated/app.py:46-48  (orders_by_order_id_status)
      examples/15-resilience-nested-paths/generated/app.py:52-54  (customers)
      examples/15-resilience-nested-paths/generated/app.py:58-60  (customers_post)
      examples/15-resilience-nested-paths/generated/app.py:64-66  (customers_by_customer_id)
      examples/15-resilience-nested-paths/generated/app.py:70-72  (customers_by_customer_id_put)
      examples/15-resilience-nested-paths/generated/app.py:76-78  (customers_by_customer_id_orders)
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
  [33fc900014c45f4a]   EXAC  _get_service  L=7 N=2 saved=7 sim=1.00
      web/routes/intents.py:35-41  (_get_service)
      web/routes/registry.py:14-20  (_get_service)
  [ad19acd787fb5e4b]   EXAC  _slug  L=3 N=3 saved=6 sim=1.00
      examples/_scripts/annotate_intract.py:13-15  (_slug)
      examples/_scripts/intent_to_openapi.py:13-15  (_slug)
      generator/intract_manifest.py:14-16  (_slug)
  [d1ab1a804f1b435b]   STRU  parse_dsl  L=4 N=2 saved=4 sim=1.00
      parser/dsl_parser.py:328-331  (parse_dsl)
      parser/dsl_parser.py:334-337  (parse_dsl_file)

REFACTOR[5] (ranked by priority):
  [1] ○ extract_function   → utils/ping.py
      WHY: 88 occurrences of 3-line block across 16 files — saves 261 lines
      FILES: examples/01-user-api/generated/app.py, examples/02-ping-smoke/generated/app.py, examples/05-ir-show/generated/app.py, examples/06-iterate-workflow/generated/app.py, examples/07-execution-smoke/generated/app.py +11 more
  [2] ○ extract_function   → examples/utils/users.py
      WHY: 4 occurrences of 8-line block across 3 files — saves 24 lines
      FILES: examples/17-stack-shop-gateway/generated/services/api-gateway/app.py, examples/18-stack-blog/generated/services/blog-api/app.py, examples/19-stack-api-cache/generated/services/api-service/app.py
  [3] ○ extract_function   → web/routes/utils/_get_service.py
      WHY: 2 occurrences of 7-line block across 2 files — saves 7 lines
      FILES: web/routes/intents.py, web/routes/registry.py
  [4] ○ extract_function   → utils/_slug.py
      WHY: 3 occurrences of 3-line block across 3 files — saves 6 lines
      FILES: examples/_scripts/annotate_intract.py, examples/_scripts/intent_to_openapi.py, generator/intract_manifest.py
  [5] ○ extract_function   → parser/utils/parse_dsl.py
      WHY: 2 occurrences of 4-line block across 1 files — saves 4 lines
      FILES: parser/dsl_parser.py

QUICK_WINS[4] (low risk, high savings — do first):
  [1] extract_function   saved=261L  → utils/ping.py
      FILES: app.py, app.py, app.py +13
  [2] extract_function   saved=24L  → examples/utils/users.py
      FILES: app.py, app.py, app.py
  [3] extract_function   saved=7L  → web/routes/utils/_get_service.py
      FILES: intents.py, registry.py
  [4] extract_function   saved=6L  → utils/_slug.py
      FILES: annotate_intract.py, intent_to_openapi.py, intract_manifest.py

DEPENDENCY_RISK[2] (duplicates spanning multiple packages):
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

EFFORT_ESTIMATE (total ≈ 19.0h):
  hard   ping                                saved=261L  ~1044min
  medium users                               saved=24L  ~48min
  easy   _get_service                        saved=7L  ~14min
  easy   _slug                               saved=6L  ~24min
  easy   parse_dsl                           saved=4L  ~8min

METRICS-TARGET:
  dup_groups:  5 → 0
  saved_lines: 302 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 378 func | 56f | 2026-06-06
# generated in 0.00s

NEXT[2] (ranked by impact):
  [1] !! SPLIT           planfile.yaml
      WHY: 1319L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0

  [2] !! SPLIT           goal.yaml
      WHY: 512L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[2]:
  ⚠ Splitting planfile.yaml may break 0 import paths
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          4.1 → ≤2.9
  max-CC:      14 → ≤7
  god-modules: 2 → 0
  high-CC(≥15): 0 → ≤0
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

## Intent

DSL-based intent execution system with iterative refinement, featuring AI-powered suggestions via Ollama, safe simulation, and automatic health validation.
