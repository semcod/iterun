# System Architecture Analysis
<!-- generated in 0.00s -->

## Overview

- **Project**: /home/tom/github/wronai/iterun
- **Primary Language**: python
- **Languages**: python: 59, shell: 27, txt: 20, yaml: 17, toml: 1
- **Analysis Mode**: static
- **Total Functions**: 337
- **Total Classes**: 76
- **Modules**: 125
- **Entry Points**: 244

## Architecture by Module

### web.app
- **Functions**: 33
- **Classes**: 11
- **File**: `app.py`

### cli.main
- **Functions**: 25
- **Classes**: 2
- **File**: `main.py`

### executor.runner
- **Functions**: 24
- **Classes**: 4
- **File**: `runner.py`

### ai_gateway.gateway
- **Functions**: 20
- **Classes**: 4
- **File**: `gateway.py`

### ir.models
- **Functions**: 18
- **Classes**: 10
- **File**: `models.py`

### planner.simulator
- **Functions**: 17
- **Classes**: 2
- **File**: `simulator.py`

### sdk.client
- **Functions**: 16
- **Classes**: 1
- **File**: `client.py`

### ai_gateway.feedback_loop
- **Functions**: 14
- **Classes**: 3
- **File**: `feedback_loop.py`

### interfaces.service
- **Functions**: 14
- **Classes**: 1
- **File**: `service.py`

### parser.dsl_parser
- **Functions**: 14
- **Classes**: 3
- **File**: `dsl_parser.py`

### examples._verify
- **Functions**: 13
- **File**: `_verify.sh`

### examples._common
- **Functions**: 11
- **File**: `_common.sh`

### generator.contract_verify
- **Functions**: 10
- **Classes**: 1
- **File**: `contract_verify.py`

### config
- **Functions**: 8
- **Classes**: 1
- **File**: `config.py`

### generator.intract_manifest
- **Functions**: 7
- **File**: `intract_manifest.py`

### registry.catalog
- **Functions**: 7
- **Classes**: 1
- **File**: `catalog.py`

### registry.discover
- **Functions**: 7
- **File**: `discover.py`

### generator.intent_generator
- **Functions**: 7
- **Classes**: 3
- **File**: `intent_generator.py`

### generator.pipeline
- **Functions**: 7
- **Classes**: 1
- **File**: `pipeline.py`

### examples._scripts.annotate_intract
- **Functions**: 6
- **File**: `annotate_intract.py`

## Key Entry Points

Main execution flows into the system:

### cli.main.main
> Main entry point.
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument

### cli.main.CLI.cmd_execute
> Execute approved intent with validation.
- **Calls**: self.print_header, executor.runner.execute_intent, print, self.print_error, config.get_config, print, self.print_success, self.print_error

### generator.pipeline.run_pipeline
- **Calls**: PipelineResult, IntentGenerator, range, generator.pipeline._finalize, Path, workspace.mkdir, generator.generate, planner.simulator.plan_intent

### parser.dsl_parser.DSLParser._parse_stack
- **Calls**: services_raw.items, Stack, isinstance, self.errors.append, Stack, data.get, isinstance, self.errors.append

### cli.main.CLI.interactive_mode
> Run interactive shell.
- **Calls**: self.print_header, print, print, print, None.strip, line.split, None.lower, print

### executor.runner.Executor._validate_endpoints
> Validate that endpoints are responding correctly.
- **Calls**: ValidationResult, set, result.add_log, checked.add, len, any, any, validation.suggestions.append

### ir.models.IntentIR.from_dict
- **Calls**: cls, data.get, data.get, data.get, data.get, Intent.from_dict, Environment.from_dict, Implementation.from_dict

### executor.runner.Executor._execute_docker
> Build and run Docker container.
- **Calls**: self._find_available_port, result.add_log, subprocess.run, result.add_log, subprocess.run, None.items, ir.environment.env_vars.items, run_cmd.append

### cli.main.CLI.cmd_plan
> Run dry-run planning/simulation.
- **Calls**: self.print_header, planner.simulator.plan_intent, print, print, enumerate, print, print, result.estimated_resources.items

### executor.runner.Executor.execute
> Execute an approved intent with optional validation and auto-fix.

Args:
    ir: IntentIR to execute
    skip_iterun_check: Skip ITERUN approval check
- **Calls**: ExecutionResult, datetime.now, result.add_log, result.add_log, None.total_seconds, integrations.pactown_runtime.execute_pactown, self._write_artifacts, result.add_log

### parser.dsl_parser.DSLParser._parse_action
> Parse single action string.
- **Calls**: isinstance, self.ACTION_PATTERN.match, match.group, match.group, Action, None.strip, self.errors.append, ActionType

### cli.main.CLI.cmd_show
> Show current IR state.
- **Calls**: self.print_error, print, ir.to_json, self.print_header, print, self.print_header, print, print

### cli.main.CLI.cmd_ai_suggest
> Get AI-powered suggestions for the current intent.
- **Calls**: self.print_header, self.print_info, self.print_error, self.print_error, ai_gateway.feedback_loop.create_feedback_loop, loop.analyze, self.print_success, loop.suggest_next_steps

### generator.intent_generator.IntentGenerator.generate
- **Calls**: GenerateResult, range, GenerateAttempt, generator.intent_generator._build_user_prompt, self.gateway.complete, response.get, response.get, generator.intent_generator.extract_yaml_from_llm

### cli.main.CLI.cmd_iterun
> Approve intent for execution (ITERUN boundary).
- **Calls**: self.print_header, print, print, print, len, print, print, print

### ai_gateway.feedback_loop.FeedbackLoop._parse_suggestions
> Parse suggestions from LLM response.
- **Calls**: json.loads, data.get, content.strip, suggestions.append, content.split, None.split, FeedbackSuggestion, None.split

### cli.main.CLI.cmd_iterate
> Apply iterative changes to current intent.
- **Calls**: self.print_header, self.print_error, print, print, print, print, ir.add_iteration, self.print_info

### planner.simulator.Planner.dry_run
> Perform dry-run simulation of the intent.
- **Calls**: DryRunResult, result.add_log, result.add_log, result.add_log, self._estimate_resources, result.add_log, result.add_log, result.add_log

### cli.main.CLI.cmd_ai_chat
> Chat with AI about the intent.
- **Calls**: self.print_header, self.print_error, print, ai_gateway.gateway.get_gateway, ai_gateway.gateway.get_gateway, gateway.complete, print, self.print_error

### executor.runner.Executor._validate_and_fix
> Run validation and attempt auto-fix if needed.
- **Calls**: result.add_log, time.sleep, executor.runner._filter_validation_endpoints, self._validate_endpoints, result.add_log, result.add_log, self._attempt_fix, result.add_log

### integrations.adapters.backstage.BackstageExporter.export
- **Calls**: Path, catalog_dir.mkdir, system_path.write_text, str, yaml.dump, manifest.spec.get, svc.get, comp_path.write_text

### integrations.adapters.docker.DockerAdapter.enrich
- **Calls**: integrations.adapters.docker._running_iterun_containers, manifest.spec.get, svc.get, c.get, None.update, c.get, c.get, c.get

### ir.models.StackService.from_dict
- **Calls**: cls, data.get, data.get, data.get, data.get, int, data.get, list

### executor.runner.Executor._write_artifacts
> Write generated code and config files.
- **Calls**: None.is_file, result.add_log, str, app_file.write_text, str, result.add_log, dockerfile.write_text, str

### ai_gateway.gateway.AIGateway.suggest_improvements
> Use LLM to suggest improvements for an intent.

Args:
    ir: Current IntentIR state
    
Returns:
    Dict with suggestions
- **Calls**: self.complete, json.dumps, json.loads, None.join, response.get, a.to_dict, None.split, response.get

### parser.dsl_parser.DSLParser.parse
> Parse DSL string and return IR.
- **Calls**: IntentIR, self._validate, yaml.safe_load, ParseError, self._parse_intent, self.errors.append, self._parse_environment, self._parse_implementation

### parser.dsl_parser.DSLParser._parse_environment
> Parse ENVIRONMENT section.
- **Calls**: data.get, Environment, isinstance, self.errors.append, Environment, RuntimeType, self.warnings.append, data.get

### cli.main.CLI.cmd_ai_health
> Check AI Gateway health.
- **Calls**: self.print_header, ai_gateway.gateway.get_gateway, gateway.health_check, print, print, print, print, health.get

### executor.runner.Executor._execute_compose_stack
> Build and run multi-service STACK via docker compose.
- **Calls**: result.add_log, subprocess.run, self._patch_compose_host_ports, subprocess.run, result.add_log, result.add_log, str, str

### ai_gateway.gateway.AIGateway.generate_code_snippet
> Generate code snippet based on description.
- **Calls**: self.complete, code.split, code.strip, len, code.startswith, None.strip, code.startswith, code.startswith

## Process Flows

Key execution flows identified:

### Flow 1: main
```
main [cli.main]
```

### Flow 2: cmd_execute
```
cmd_execute [cli.main.CLI]
  └─ →> execute_intent
  └─ →> get_config
```

### Flow 3: run_pipeline
```
run_pipeline [generator.pipeline]
  └─> _finalize
      └─> _container_logs
      └─ →> write_session_artifacts
      └─ →> refresh_registry_from_pipeline
```

### Flow 4: _parse_stack
```
_parse_stack [parser.dsl_parser.DSLParser]
```

### Flow 5: interactive_mode
```
interactive_mode [cli.main.CLI]
```

### Flow 6: _validate_endpoints
```
_validate_endpoints [executor.runner.Executor]
```

### Flow 7: from_dict
```
from_dict [ir.models.IntentIR]
```

### Flow 8: _execute_docker
```
_execute_docker [executor.runner.Executor]
```

### Flow 9: cmd_plan
```
cmd_plan [cli.main.CLI]
  └─ →> plan_intent
      └─ →> plan_stack
          └─> _build_compose
```

### Flow 10: execute
```
execute [executor.runner.Executor]
```

## Key Classes

### cli.main.CLI
> Interactive CLI for iterun system.
- **Methods**: 22
- **Key Methods**: cli.main.CLI.__init__, cli.main.CLI.print_header, cli.main.CLI.print_success, cli.main.CLI.print_error, cli.main.CLI.print_warning, cli.main.CLI.print_info, cli.main.CLI.cmd_new, cli.main.CLI.cmd_load, cli.main.CLI.cmd_parse, cli.main.CLI.cmd_plan

### sdk.client.IterunClient
> Local SDK (in-process) or remote via REST base_url.
- **Methods**: 16
- **Key Methods**: sdk.client.IterunClient.__init__, sdk.client.IterunClient.health, sdk.client.IterunClient.interfaces, sdk.client.IterunClient.schema, sdk.client.IterunClient.validate, sdk.client.IterunClient.generate, sdk.client.IterunClient.run_pipeline, sdk.client.IterunClient.generate_and_run, sdk.client.IterunClient.plan_yaml, sdk.client.IterunClient.registry_get

### executor.runner.Executor
> Executes approved intents.
Only runs after ITERUN boundary is passed.
Includes validation and auto-f
- **Methods**: 15
- **Key Methods**: executor.runner.Executor.__init__, executor.runner.Executor.execute, executor.runner.Executor._validate_and_fix, executor.runner.Executor._validate_endpoints, executor.runner.Executor._attempt_fix, executor.runner.Executor._add_main_block, executor.runner.Executor._restart_container, executor.runner.Executor._write_artifacts, executor.runner.Executor._find_available_port, executor.runner.Executor._patch_compose_host_ports

### interfaces.service.IterunService
> Single entry point for programmatic access to ITERUN.
- **Methods**: 13
- **Key Methods**: interfaces.service.IterunService.__init__, interfaces.service.IterunService.interfaces_info, interfaces.service.IterunService.schema, interfaces.service.IterunService.validate_yaml, interfaces.service.IterunService.parse, interfaces.service.IterunService.generate, interfaces.service.IterunService.run_pipeline, interfaces.service.IterunService.plan_ir, interfaces.service.IterunService.plan_yaml, interfaces.service.IterunService.execute_ir

### planner.simulator.Planner
> Plans and simulates intent execution.
Generates code, Dockerfiles, and estimates without actual exec
- **Methods**: 12
- **Key Methods**: planner.simulator.Planner.__init__, planner.simulator.Planner.dry_run, planner.simulator.Planner._generate_python_code, planner.simulator.Planner._generate_fastapi_code, planner.simulator.Planner._generate_flask_code, planner.simulator.Planner._generate_basic_python_code, planner.simulator.Planner._generate_node_code, planner.simulator.Planner._generate_express_code, planner.simulator.Planner._generate_basic_node_code, planner.simulator.Planner._generate_dockerfile

### ai_gateway.gateway.AIGateway
> AI Gateway using LiteLLM for unified model access.
Default: Ollama with models up to 12B parameters.
- **Methods**: 10
- **Key Methods**: ai_gateway.gateway.AIGateway.__init__, ai_gateway.gateway.AIGateway._setup_litellm, ai_gateway.gateway.AIGateway.complete, ai_gateway.gateway.AIGateway.acomplete, ai_gateway.gateway.AIGateway._mock_response, ai_gateway.gateway.AIGateway.suggest_improvements, ai_gateway.gateway.AIGateway.generate_code_snippet, ai_gateway.gateway.AIGateway.explain_error, ai_gateway.gateway.AIGateway.list_models, ai_gateway.gateway.AIGateway.health_check

### ai_gateway.feedback_loop.FeedbackLoop
> LLM-powered feedback loop for iterative intent refinement.
Uses AI Gateway to suggest and apply impr
- **Methods**: 10
- **Key Methods**: ai_gateway.feedback_loop.FeedbackLoop.__init__, ai_gateway.feedback_loop.FeedbackLoop.analyze, ai_gateway.feedback_loop.FeedbackLoop.apply_suggestions, ai_gateway.feedback_loop.FeedbackLoop.iterate, ai_gateway.feedback_loop.FeedbackLoop.suggest_next_steps, ai_gateway.feedback_loop.FeedbackLoop._build_analysis_prompt, ai_gateway.feedback_loop.FeedbackLoop._parse_suggestions, ai_gateway.feedback_loop.FeedbackLoop._extract_action, ai_gateway.feedback_loop.FeedbackLoop._parse_action, ai_gateway.feedback_loop.FeedbackLoop._process_user_feedback

### parser.dsl_parser.DSLParser
> Parser for ITERUN DSL format.

Example DSL:
```yaml
INTENT:
  name: my-api
  goal: Create REST API


- **Methods**: 10
- **Key Methods**: parser.dsl_parser.DSLParser.__init__, parser.dsl_parser.DSLParser.parse_file, parser.dsl_parser.DSLParser.parse, parser.dsl_parser.DSLParser._parse_intent, parser.dsl_parser.DSLParser._parse_environment, parser.dsl_parser.DSLParser._parse_implementation, parser.dsl_parser.DSLParser._parse_action, parser.dsl_parser.DSLParser._parse_stack, parser.dsl_parser.DSLParser._parse_execution, parser.dsl_parser.DSLParser._validate

### registry.catalog.RegistryCatalog
> Workspace-scoped service and artifact registry.
- **Methods**: 7
- **Key Methods**: registry.catalog.RegistryCatalog.__init__, registry.catalog.RegistryCatalog.registry_path, registry.catalog.RegistryCatalog.discover, registry.catalog.RegistryCatalog.load, registry.catalog.RegistryCatalog.refresh, registry.catalog.RegistryCatalog.write, registry.catalog.RegistryCatalog.summary

### ai_gateway.gateway.GatewayConfig
> AI Gateway configuration.
- **Methods**: 6
- **Key Methods**: ai_gateway.gateway.GatewayConfig.__post_init__, ai_gateway.gateway.GatewayConfig.resolve_model, ai_gateway.gateway.GatewayConfig.litellm_model_id, ai_gateway.gateway.GatewayConfig.get_available_models, ai_gateway.gateway.GatewayConfig.get_model, ai_gateway.gateway.GatewayConfig.to_dict

### ir.models.IntentIR
> Complete Intermediate Representation for an intent.
This is the canonical representation used by all
- **Methods**: 6
- **Key Methods**: ir.models.IntentIR.to_dict, ir.models.IntentIR.to_json, ir.models.IntentIR.from_dict, ir.models.IntentIR.from_json, ir.models.IntentIR.add_iteration, ir.models.IntentIR.approve_iterun

### planner.simulator.DryRunResult
> Result of a dry-run simulation.
- **Methods**: 3
- **Key Methods**: planner.simulator.DryRunResult.__init__, planner.simulator.DryRunResult.add_log, planner.simulator.DryRunResult.to_dict

### executor.runner.ValidationResult
> Result of post-execution validation.
- **Methods**: 3
- **Key Methods**: executor.runner.ValidationResult.__init__, executor.runner.ValidationResult.add_check, executor.runner.ValidationResult.to_dict

### executor.runner.ExecutionResult
> Result of intent execution.
- **Methods**: 3
- **Key Methods**: executor.runner.ExecutionResult.__init__, executor.runner.ExecutionResult.add_log, executor.runner.ExecutionResult.to_dict

### integrations.adapters.base.RegistryAdapter
> Collect or export registry data from an external system.
- **Methods**: 2
- **Key Methods**: integrations.adapters.base.RegistryAdapter.collect, integrations.adapters.base.RegistryAdapter.enrich
- **Inherits**: ABC

### integrations.adapters.docker.DockerAdapter
> Merge docker ps / compose state into registry manifest.
- **Methods**: 2
- **Key Methods**: integrations.adapters.docker.DockerAdapter.collect, integrations.adapters.docker.DockerAdapter.enrich
- **Inherits**: FilesystemAdapter

### ir.models.Action
> Single action in the implementation plan.
- **Methods**: 2
- **Key Methods**: ir.models.Action.to_dict, ir.models.Action.from_dict

### ir.models.Environment
> Runtime environment configuration.
- **Methods**: 2
- **Key Methods**: ir.models.Environment.to_dict, ir.models.Environment.from_dict

### ir.models.Implementation
> Implementation details.
- **Methods**: 2
- **Key Methods**: ir.models.Implementation.to_dict, ir.models.Implementation.from_dict

### ir.models.StackService
> Single service inside a multi-container STACK application.
- **Methods**: 2
- **Key Methods**: ir.models.StackService.to_dict, ir.models.StackService.from_dict

## Data Transformation Functions

Key functions that process and transform data:

### examples._scripts.verify_expectations._parse_actions
- **Output to**: None.get, re.match, isinstance, action.strip, parsed.append

### ai_gateway.feedback_loop.FeedbackLoop._parse_suggestions
> Parse suggestions from LLM response.
- **Output to**: json.loads, data.get, content.strip, suggestions.append, content.split

### ai_gateway.feedback_loop.FeedbackLoop._parse_action
> Parse action string into Action object.
- **Output to**: DSLParser, parser._parse_action

### ai_gateway.feedback_loop.FeedbackLoop._process_user_feedback
> Process natural language user feedback.
- **Output to**: self.gateway.complete, self._parse_suggestions

### generator.intract_manifest._parse_action_strings
- **Output to**: re.match, isinstance, action.strip, parsed.append, None.upper

### generator.intract_manifest.parse_api_actions
- **Output to**: generator.intract_manifest._parse_action_strings, None.items, intent_data.get, parsed.extend, None.get

### interfaces.service.IterunService.validate_yaml
- **Output to**: dsl.schema.validate_yaml_document, bool, doc.model_dump

### interfaces.service.IterunService.parse
- **Output to**: parser.dsl_parser.parse_dsl

### executor.runner.Executor._validate_and_fix
> Run validation and attempt auto-fix if needed.
- **Output to**: result.add_log, time.sleep, executor.runner._filter_validation_endpoints, self._validate_endpoints, result.add_log

### executor.runner.Executor._validate_endpoints
> Validate that endpoints are responding correctly.
- **Output to**: ValidationResult, set, result.add_log, checked.add, len

### sdk.client.IterunClient.validate
- **Output to**: dsl.schema.validate_yaml_document, self._post_json, bool, doc.model_dump

### sdk.client.IterunClient.parse
- **Output to**: parser.dsl_parser.parse_dsl, self._post_json, parser.dsl_parser.parse_dsl, data.get, ValueError

### integrations.pactown_runtime._validate_urls
- **Output to**: ValidationResult, executor.runner._filter_validation_endpoints, len, httpx.Client, client.get

### parser.dsl_parser.DSLParser.parse_file
> Parse DSL file and return IR.
- **Output to**: self.parse, open, f.read

### parser.dsl_parser.DSLParser.parse
> Parse DSL string and return IR.
- **Output to**: IntentIR, self._validate, yaml.safe_load, ParseError, self._parse_intent

### parser.dsl_parser.DSLParser._parse_intent
> Parse INTENT section.
- **Output to**: data.get, data.get, Intent, isinstance, self.errors.append

### parser.dsl_parser.DSLParser._parse_environment
> Parse ENVIRONMENT section.
- **Output to**: data.get, Environment, isinstance, self.errors.append, Environment

### parser.dsl_parser.DSLParser._parse_implementation
> Parse IMPLEMENTATION section.
- **Output to**: data.get, Implementation, isinstance, self.errors.append, Implementation

### parser.dsl_parser.DSLParser._parse_action
> Parse single action string.
- **Output to**: isinstance, self.ACTION_PATTERN.match, match.group, match.group, Action

### parser.dsl_parser.DSLParser._parse_stack
- **Output to**: services_raw.items, Stack, isinstance, self.errors.append, Stack

### parser.dsl_parser.DSLParser._parse_execution
> Parse EXECUTION section.
- **Output to**: data.get, isinstance, self.errors.append, ExecutionMode, self.warnings.append

### parser.dsl_parser.DSLParser._validate
> Validate the parsed IR.
- **Output to**: self.errors.append, self.errors.append, self.errors.append, self.errors.append, self.errors.append

### parser.dsl_parser.parse_dsl
> Convenience function to parse DSL content.
- **Output to**: DSLParser, parser.parse

### parser.dsl_parser.parse_dsl_file
> Convenience function to parse DSL file.
- **Output to**: DSLParser, parser.parse_file

### cli.main.CLI.cmd_parse
> Parse DSL content directly.
- **Output to**: self.print_header, parser.dsl_parser.parse_dsl, self.print_success, self.print_error

## Behavioral Patterns

### recursion_run_pipeline
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: interfaces.service.IterunService.run_pipeline

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `cli.main.main` - 122 calls
- `registry.discover.discover_workspace` - 75 calls
- `integrations.pactown_runtime.execute_pactown` - 50 calls
- `cli.main.CLI.cmd_execute` - 37 calls
- `generator.pipeline.run_pipeline` - 37 calls
- `generator.contract_verify.verify_contract` - 32 calls
- `cli.main.CLI.interactive_mode` - 31 calls
- `examples._scripts.verify_expectations.verify` - 27 calls
- `ir.models.IntentIR.from_dict` - 27 calls
- `generator.expectations.check_expectations` - 26 calls
- `cli.main.CLI.cmd_plan` - 24 calls
- `executor.runner.Executor.execute` - 22 calls
- `planner.stack_artifacts.write_stack_artifacts` - 22 calls
- `planner.stack_planner.plan_stack` - 21 calls
- `cli.main.CLI.cmd_show` - 21 calls
- `cli.main.CLI.cmd_ai_suggest` - 21 calls
- `generator.intent_generator.IntentGenerator.generate` - 21 calls
- `cli.main.CLI.cmd_iterun` - 20 calls
- `cli.main.CLI.cmd_iterate` - 19 calls
- `planner.simulator.Planner.dry_run` - 18 calls
- `cli.main.CLI.cmd_ai_chat` - 18 calls
- `examples._scripts.intent_to_openapi.intent_to_openapi` - 17 calls
- `generator.session.write_session_artifacts` - 16 calls
- `integrations.adapters.backstage.BackstageExporter.export` - 16 calls
- `integrations.adapters.docker.DockerAdapter.enrich` - 16 calls
- `config.load_dotenv` - 15 calls
- `ir.models.StackService.from_dict` - 14 calls
- `examples._scripts.annotate_intract.annotate_express` - 13 calls
- `integrations.bridges.pipeline.refresh_registry` - 13 calls
- `ai_gateway.gateway.AIGateway.suggest_improvements` - 12 calls
- `integrations.markpact_pack.pack_workspace` - 12 calls
- `parser.dsl_parser.DSLParser.parse` - 12 calls
- `cli.main.write_plan_artifacts` - 12 calls
- `cli.main.CLI.cmd_ai_health` - 12 calls
- `examples._scripts.annotate_intract.annotate_python` - 11 calls
- `generator.intract_manifest.parse_api_actions` - 11 calls
- `generator.intract_manifest.build_intract_manifest` - 11 calls
- `registry.catalog.discover_glob` - 11 calls
- `generator.intent_generator.extract_yaml_from_llm` - 11 calls
- `generator.testql_scenario.build_testql_scenario` - 10 calls

## System Interactions

How components interact:

```mermaid
graph TD
    main --> ArgumentParser
    main --> add_argument
    cmd_execute --> print_header
    cmd_execute --> execute_intent
    cmd_execute --> print
    cmd_execute --> print_error
    cmd_execute --> get_config
    run_pipeline --> PipelineResult
    run_pipeline --> IntentGenerator
    run_pipeline --> range
    run_pipeline --> _finalize
    run_pipeline --> Path
    _parse_stack --> items
    _parse_stack --> Stack
    _parse_stack --> isinstance
    _parse_stack --> append
    interactive_mode --> print_header
    interactive_mode --> print
    interactive_mode --> strip
    _validate_endpoints --> ValidationResult
    _validate_endpoints --> set
    _validate_endpoints --> add_log
    _validate_endpoints --> add
    _validate_endpoints --> len
    from_dict --> cls
    from_dict --> get
    _execute_docker --> _find_available_port
    _execute_docker --> add_log
    _execute_docker --> run
    cmd_plan --> print_header
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.