# System Architecture Analysis
<!-- generated in 0.00s -->

## Overview

- **Project**: /home/tom/github/wronai/amen
- **Primary Language**: python
- **Languages**: python: 16, yaml: 5, shell: 3, txt: 1, toml: 1
- **Analysis Mode**: static
- **Total Functions**: 148
- **Total Classes**: 33
- **Modules**: 27
- **Entry Points**: 140

## Architecture by Module

### cli.main
- **Functions**: 24
- **Classes**: 2
- **File**: `main.py`

### web.app
- **Functions**: 21
- **Classes**: 6
- **File**: `app.py`

### executor.runner
- **Functions**: 20
- **Classes**: 4
- **File**: `runner.py`

### ai_gateway.gateway
- **Functions**: 18
- **Classes**: 4
- **File**: `gateway.py`

### planner.simulator
- **Functions**: 16
- **Classes**: 2
- **File**: `simulator.py`

### ir.models
- **Functions**: 14
- **Classes**: 8
- **File**: `models.py`

### ai_gateway.feedback_loop
- **Functions**: 14
- **Classes**: 3
- **File**: `feedback_loop.py`

### parser.dsl_parser
- **Functions**: 13
- **Classes**: 3
- **File**: `dsl_parser.py`

### config
- **Functions**: 8
- **Classes**: 1
- **File**: `config.py`

## Key Entry Points

Main execution flows into the system:

### cli.main.CLI.cmd_execute
> Execute approved intent with validation.
- **Calls**: self.print_header, executor.runner.execute_intent, print, self.print_error, config.get_config, print, self.print_success, self.print_error

### cli.main.main
> Main entry point.
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.parse_args

### cli.main.CLI.interactive_mode
> Run interactive shell.
- **Calls**: self.print_header, print, print, print, None.strip, line.split, None.lower, print

### executor.runner.Executor._validate_endpoints
> Validate that endpoints are responding correctly.
- **Calls**: ValidationResult, set, result.add_log, checked.add, len, any, any, validation.suggestions.append

### ir.models.IntentIR.from_dict
- **Calls**: cls, data.get, data.get, data.get, data.get, Intent.from_dict, Environment.from_dict, Implementation.from_dict

### cli.main.CLI.cmd_plan
> Run dry-run planning/simulation.
- **Calls**: self.print_header, planner.simulator.plan_intent, print, print, enumerate, print, print, result.estimated_resources.items

### cli.main.CLI.cmd_show
> Show current IR state.
- **Calls**: self.print_error, print, ir.to_json, self.print_header, print, self.print_header, print, print

### cli.main.CLI.cmd_ai_suggest
> Get AI-powered suggestions for the current intent.
- **Calls**: self.print_header, self.print_info, self.print_error, self.print_error, ai_gateway.feedback_loop.create_feedback_loop, loop.analyze, self.print_success, loop.suggest_next_steps

### parser.dsl_parser.DSLParser._parse_action
> Parse single action string.
- **Calls**: isinstance, self.ACTION_PATTERN.match, match.group, match.group, Action, None.strip, self.errors.append, ActionType

### executor.runner.Executor._execute_docker
> Build and run Docker container.
- **Calls**: self._find_available_port, result.add_log, subprocess.run, result.add_log, subprocess.run, ir.environment.env_vars.items, run_cmd.append, result.add_log

### ai_gateway.feedback_loop.FeedbackLoop._parse_suggestions
> Parse suggestions from LLM response.
- **Calls**: json.loads, data.get, content.strip, suggestions.append, content.split, None.split, FeedbackSuggestion, None.split

### cli.main.CLI.cmd_iterate
> Apply iterative changes to current intent.
- **Calls**: self.print_header, self.print_error, print, print, print, print, ir.add_iteration, self.print_info

### planner.simulator.Planner.dry_run
> Perform dry-run simulation of the intent.
- **Calls**: DryRunResult, result.add_log, result.add_log, result.add_log, self._estimate_resources, result.add_log, result.add_log, result.add_log

### cli.main.CLI.cmd_amen
> Approve intent for execution (AMEN boundary).
- **Calls**: self.print_header, print, print, print, print, print, print, print

### cli.main.CLI.cmd_ai_chat
> Chat with AI about the intent.
- **Calls**: self.print_header, self.print_error, print, ai_gateway.gateway.get_gateway, ai_gateway.gateway.get_gateway, gateway.complete, print, self.print_error

### executor.runner.Executor.execute
> Execute an approved intent with optional validation and auto-fix.

Args:
    ir: IntentIR to execute
    skip_amen_check: Skip AMEN approval check
   
- **Calls**: ExecutionResult, datetime.now, result.add_log, result.add_log, None.total_seconds, self._write_artifacts, result.add_log, result.add_log

### executor.runner.Executor._validate_and_fix
> Run validation and attempt auto-fix if needed.
- **Calls**: result.add_log, time.sleep, self._validate_endpoints, result.add_log, result.add_log, self._attempt_fix, result.add_log, self._restart_container

### ai_gateway.gateway.AIGateway.suggest_improvements
> Use LLM to suggest improvements for an intent.

Args:
    ir: Current IntentIR state
    
Returns:
    Dict with suggestions
- **Calls**: self.complete, json.dumps, json.loads, None.join, response.get, a.to_dict, None.split, response.get

### cli.main.CLI.cmd_ai_health
> Check AI Gateway health.
- **Calls**: self.print_header, ai_gateway.gateway.get_gateway, gateway.health_check, print, print, print, print, health.get

### parser.dsl_parser.DSLParser._parse_environment
> Parse ENVIRONMENT section.
- **Calls**: data.get, Environment, isinstance, self.errors.append, Environment, RuntimeType, self.warnings.append, data.get

### parser.dsl_parser.DSLParser.parse
> Parse DSL string and return IR.
- **Calls**: IntentIR, self._validate, yaml.safe_load, ParseError, self._parse_intent, self.errors.append, self._parse_environment, self._parse_implementation

### ai_gateway.gateway.AIGateway.generate_code_snippet
> Generate code snippet based on description.
- **Calls**: self.complete, code.split, code.strip, len, code.startswith, None.strip, code.startswith, code.startswith

### ai_gateway.feedback_loop.FeedbackLoop.suggest_next_steps
> Get list of suggested next steps for the intent.
- **Calls**: any, suggestions.append, any, suggestions.append, len, suggestions.append, suggestions.append, suggestions.append

### cli.main.CLI.cmd_ai_apply
> Apply AI suggestions automatically.
- **Calls**: self.print_header, ai_gateway.feedback_loop.create_feedback_loop, loop.iterate, self.print_error, self.print_error, self.print_info, self.print_info, self.print_success

### executor.runner.Executor._write_artifacts
> Write generated code and config files.
- **Calls**: app_file.write_text, str, result.add_log, dockerfile.write_text, str, result.add_log, package_json.write_text, str

### web.app.validate_intent
> Validate running container endpoints for an intent.
- **Calls**: app.post, Executor, config.get_config, set, ExecutionResult, executor._validate_endpoints, HTTPException, seen_paths.add

### cli.main.CLI.cmd_models
> List available AI models.
- **Calls**: self.print_header, ai_gateway.gateway.get_gateway, gateway.list_models, print, print, print, print, self.print_error

### parser.dsl_parser.DSLParser._parse_intent
> Parse INTENT section.
- **Calls**: data.get, data.get, Intent, isinstance, self.errors.append, Intent, self.errors.append, self.errors.append

### parser.dsl_parser.DSLParser._parse_implementation
> Parse IMPLEMENTATION section.
- **Calls**: data.get, Implementation, isinstance, self.errors.append, Implementation, self._parse_action, actions.append, data.get

### executor.runner.Executor._attempt_fix
> Attempt to fix issues found during validation.
- **Calls**: result.add_log, ir.add_iteration, self._write_artifacts, self._add_main_block, fixes_applied.append, fixes_applied.append, ir.generated_code.replace, fixes_applied.append

## Process Flows

Key execution flows identified:

### Flow 1: cmd_execute
```
cmd_execute [cli.main.CLI]
  └─ →> execute_intent
  └─ →> get_config
```

### Flow 2: main
```
main [cli.main]
```

### Flow 3: interactive_mode
```
interactive_mode [cli.main.CLI]
```

### Flow 4: _validate_endpoints
```
_validate_endpoints [executor.runner.Executor]
```

### Flow 5: from_dict
```
from_dict [ir.models.IntentIR]
```

### Flow 6: cmd_plan
```
cmd_plan [cli.main.CLI]
  └─ →> plan_intent
```

### Flow 7: cmd_show
```
cmd_show [cli.main.CLI]
```

### Flow 8: cmd_ai_suggest
```
cmd_ai_suggest [cli.main.CLI]
  └─ →> create_feedback_loop
```

### Flow 9: _parse_action
```
_parse_action [parser.dsl_parser.DSLParser]
```

### Flow 10: _execute_docker
```
_execute_docker [executor.runner.Executor]
```

## Key Classes

### cli.main.CLI
> Interactive CLI for Intent-Iterative system.
- **Methods**: 22
- **Key Methods**: cli.main.CLI.__init__, cli.main.CLI.print_header, cli.main.CLI.print_success, cli.main.CLI.print_error, cli.main.CLI.print_warning, cli.main.CLI.print_info, cli.main.CLI.cmd_new, cli.main.CLI.cmd_load, cli.main.CLI.cmd_parse, cli.main.CLI.cmd_plan

### executor.runner.Executor
> Executes approved intents.
Only runs after AMEN boundary is passed.
Includes validation and auto-fix
- **Methods**: 13
- **Key Methods**: executor.runner.Executor.__init__, executor.runner.Executor.execute, executor.runner.Executor._validate_and_fix, executor.runner.Executor._validate_endpoints, executor.runner.Executor._attempt_fix, executor.runner.Executor._add_main_block, executor.runner.Executor._restart_container, executor.runner.Executor._write_artifacts, executor.runner.Executor._find_available_port, executor.runner.Executor._execute_docker

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
> Parser for INTENT-ITERATIVE DSL format.

Example DSL:
```yaml
INTENT:
  name: my-api
  goal: Create 
- **Methods**: 9
- **Key Methods**: parser.dsl_parser.DSLParser.__init__, parser.dsl_parser.DSLParser.parse_file, parser.dsl_parser.DSLParser.parse, parser.dsl_parser.DSLParser._parse_intent, parser.dsl_parser.DSLParser._parse_environment, parser.dsl_parser.DSLParser._parse_implementation, parser.dsl_parser.DSLParser._parse_action, parser.dsl_parser.DSLParser._parse_execution, parser.dsl_parser.DSLParser._validate

### ir.models.IntentIR
> Complete Intermediate Representation for an intent.
This is the canonical representation used by all
- **Methods**: 6
- **Key Methods**: ir.models.IntentIR.to_dict, ir.models.IntentIR.to_json, ir.models.IntentIR.from_dict, ir.models.IntentIR.from_json, ir.models.IntentIR.add_iteration, ir.models.IntentIR.approve_amen

### ai_gateway.gateway.GatewayConfig
> AI Gateway configuration.
- **Methods**: 4
- **Key Methods**: ai_gateway.gateway.GatewayConfig.__post_init__, ai_gateway.gateway.GatewayConfig.get_available_models, ai_gateway.gateway.GatewayConfig.get_model, ai_gateway.gateway.GatewayConfig.to_dict

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

### ir.models.Intent
> Main intent definition.
- **Methods**: 2
- **Key Methods**: ir.models.Intent.to_dict, ir.models.Intent.from_dict

### ai_gateway.gateway.ModelConfig
> Configuration for a specific model.
- **Methods**: 1
- **Key Methods**: ai_gateway.gateway.ModelConfig.to_dict

### ai_gateway.feedback_loop.FeedbackSuggestion
> A single improvement suggestion.
- **Methods**: 1
- **Key Methods**: ai_gateway.feedback_loop.FeedbackSuggestion.to_dict

### ai_gateway.feedback_loop.FeedbackResult
> Result of feedback loop iteration.
- **Methods**: 1
- **Key Methods**: ai_gateway.feedback_loop.FeedbackResult.to_dict

### cli.main.Colors
> ANSI color codes for terminal output.
- **Methods**: 1
- **Key Methods**: cli.main.Colors.disable

### parser.dsl_parser.ParseError
> Raised when DSL parsing fails.
- **Methods**: 1
- **Key Methods**: parser.dsl_parser.ParseError.__init__
- **Inherits**: Exception

## Data Transformation Functions

Key functions that process and transform data:

### web.app.parse_intent
> Parse DSL content and create new intent.
- **Output to**: app.post, parser.dsl_parser.parse_dsl, ir.to_dict, HTTPException, str

### web.app.validate_intent
> Validate running container endpoints for an intent.
- **Output to**: app.post, Executor, config.get_config, set, ExecutionResult

### ai_gateway.feedback_loop.FeedbackLoop._parse_suggestions
> Parse suggestions from LLM response.
- **Output to**: json.loads, data.get, content.strip, suggestions.append, content.split

### ai_gateway.feedback_loop.FeedbackLoop._parse_action
> Parse action string into Action object.
- **Output to**: DSLParser, parser._parse_action

### ai_gateway.feedback_loop.FeedbackLoop._process_user_feedback
> Process natural language user feedback.
- **Output to**: self.gateway.complete, self._parse_suggestions

### cli.main.CLI.cmd_parse
> Parse DSL content directly.
- **Output to**: self.print_header, parser.dsl_parser.parse_dsl, self.print_success, self.print_error

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

### parser.dsl_parser.DSLParser._parse_execution
> Parse EXECUTION section.
- **Output to**: data.get, isinstance, self.errors.append, ExecutionMode, self.warnings.append

### parser.dsl_parser.DSLParser._validate
> Validate the parsed IR.
- **Output to**: self.errors.append, self.errors.append, None.lower, self.warnings.append, str

### parser.dsl_parser.parse_dsl
> Convenience function to parse DSL content.
- **Output to**: DSLParser, parser.parse

### parser.dsl_parser.parse_dsl_file
> Convenience function to parse DSL file.
- **Output to**: DSLParser, parser.parse_file

### executor.runner.Executor._validate_and_fix
> Run validation and attempt auto-fix if needed.
- **Output to**: result.add_log, time.sleep, self._validate_endpoints, result.add_log, result.add_log

### executor.runner.Executor._validate_endpoints
> Validate that endpoints are responding correctly.
- **Output to**: ValidationResult, set, result.add_log, checked.add, len

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `cli.main.CLI.cmd_execute` - 37 calls
- `cli.main.main` - 37 calls
- `cli.main.CLI.interactive_mode` - 31 calls
- `ir.models.IntentIR.from_dict` - 25 calls
- `cli.main.CLI.cmd_plan` - 24 calls
- `cli.main.CLI.cmd_show` - 21 calls
- `cli.main.CLI.cmd_ai_suggest` - 21 calls
- `cli.main.CLI.cmd_iterate` - 19 calls
- `planner.simulator.Planner.dry_run` - 18 calls
- `cli.main.CLI.cmd_amen` - 18 calls
- `cli.main.CLI.cmd_ai_chat` - 18 calls
- `executor.runner.Executor.execute` - 18 calls
- `config.load_dotenv` - 15 calls
- `ai_gateway.gateway.AIGateway.suggest_improvements` - 12 calls
- `cli.main.CLI.cmd_ai_health` - 12 calls
- `parser.dsl_parser.DSLParser.parse` - 11 calls
- `ai_gateway.gateway.AIGateway.generate_code_snippet` - 10 calls
- `ai_gateway.feedback_loop.FeedbackLoop.suggest_next_steps` - 10 calls
- `cli.main.CLI.cmd_ai_apply` - 10 calls
- `web.app.validate_intent` - 9 calls
- `cli.main.CLI.cmd_models` - 9 calls
- `web.app.ai_suggest` - 8 calls
- `ir.models.Environment.from_dict` - 8 calls
- `ai_gateway.feedback_loop.FeedbackLoop.analyze` - 8 calls
- `cli.main.CLI.cmd_load` - 8 calls
- `web.app.iterate` - 7 calls
- `web.app.ai_chat` - 7 calls
- `web.app.ai_apply_suggestions` - 7 calls
- `ai_gateway.feedback_loop.FeedbackLoop.apply_suggestions` - 7 calls
- `cli.main.CLI.cmd_new` - 7 calls
- `web.app.ai_complete` - 6 calls
- `web.app.generate_code` - 6 calls
- `ai_gateway.gateway.AIGateway.complete` - 6 calls
- `ai_gateway.gateway.AIGateway.acomplete` - 6 calls
- `web.app.parse_intent` - 5 calls
- `web.app.execute` - 5 calls
- `web.app.ai_status` - 5 calls
- `ir.models.Action.from_dict` - 5 calls
- `ir.models.Implementation.from_dict` - 5 calls
- `ai_gateway.gateway.GatewayConfig.get_available_models` - 5 calls

## System Interactions

How components interact:

```mermaid
graph TD
    cmd_execute --> print_header
    cmd_execute --> execute_intent
    cmd_execute --> print
    cmd_execute --> print_error
    cmd_execute --> get_config
    main --> ArgumentParser
    main --> add_argument
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
    cmd_plan --> print_header
    cmd_plan --> plan_intent
    cmd_plan --> print
    cmd_plan --> enumerate
    cmd_show --> print_error
    cmd_show --> print
    cmd_show --> to_json
    cmd_show --> print_header
    cmd_ai_suggest --> print_header
    cmd_ai_suggest --> print_info
    cmd_ai_suggest --> print_error
    cmd_ai_suggest --> create_feedback_loop
    _parse_action --> isinstance
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.