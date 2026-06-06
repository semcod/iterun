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
sumd_workflow_step('plan', 1, '$(PYTHON) -m cli.main plan examples/user-api.intent.yaml').
sumd_workflow('execute', 'manual').
sumd_workflow_step('execute', 1, '$(PYTHON) -m cli.main execute examples/user-api.intent.yaml').
sumd_workflow('run-intent', 'manual').
sumd_workflow_step('run-intent', 1, 'if [ -z "$(FILE)" ]').
sumd_workflow_step('run-intent', 2, 'echo "$(RED)ERROR: FILE not specified$(RESET)"').
sumd_workflow_step('run-intent', 3, 'echo "Usage: make run-intent FILE=path/to/intent.yaml"').
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
sumd_workflow_step('show-config', 9, 'echo "  SKIP_AMEN_CONFIRMATION=$(SKIP_AMEN_CONFIRMATION)"').
sumd_workflow_step('show-config', 10, 'echo ""').

