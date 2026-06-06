"""
E2E Tests for ITERUN Shell Interface
"""

import pytest
import subprocess
import sys
import json
import tempfile
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ir.models import IntentIR, ExecutionMode
from parser.dsl_parser import parse_dsl, ParseError, ValidationError
from planner.simulator import plan_intent
from cli.shell import CLI


class TestDSLParser:
    """Test DSL parsing functionality."""
    
    def test_parse_valid_dsl(self):
        """Test parsing a valid DSL document."""
        dsl = """
INTENT:
  name: test-api
  goal: Test API service

ENVIRONMENT:
  runtime: docker
  base_image: python:3.12

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping

EXECUTION:
  mode: dry-run
"""
        ir = parse_dsl(dsl)
        
        assert ir.intent.name == "test-api"
        assert ir.intent.goal == "Test API service"
        assert ir.environment.runtime.value == "docker"
        assert ir.implementation.language == "python"
        assert ir.implementation.framework == "fastapi"
        assert len(ir.implementation.actions) == 1
        assert ir.execution_mode == ExecutionMode.DRY_RUN
    
    def test_parse_missing_intent(self):
        """Test that missing INTENT section raises error."""
        dsl = """
ENVIRONMENT:
  runtime: docker

IMPLEMENTATION:
  language: python
  actions:
    - api.expose GET /ping
"""
        with pytest.raises(ValidationError) as exc_info:
            parse_dsl(dsl)
        assert "INTENT" in str(exc_info.value)
    
    def test_parse_invalid_yaml(self):
        """Test that invalid YAML raises error."""
        dsl = """
INTENT:
  name: test
  goal: [invalid yaml
"""
        with pytest.raises(ParseError):
            parse_dsl(dsl)
    
    def test_parse_multiple_actions(self):
        """Test parsing multiple actions."""
        dsl = """
INTENT:
  name: multi-action
  goal: Test multiple actions

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
    - api.expose POST /users
    - api.expose DELETE /users/{id}
"""
        ir = parse_dsl(dsl)
        
        assert len(ir.implementation.actions) == 3
        assert ir.implementation.actions[0].method == "GET"
        assert ir.implementation.actions[1].method == "POST"
        assert ir.implementation.actions[2].method == "DELETE"
    
    def test_parse_action_formats(self):
        """Test different action formats."""
        dsl = """
INTENT:
  name: action-test
  goal: Test action formats

IMPLEMENTATION:
  language: python
  actions:
    - api.expose GET /health
    - db.create users
    - rest.call GET https://api.example.com/data
"""
        ir = parse_dsl(dsl)
        
        assert len(ir.implementation.actions) == 3
        assert ir.implementation.actions[0].type.value == "api.expose"
        assert ir.implementation.actions[1].type.value == "db.create"
        assert ir.implementation.actions[2].type.value == "rest.call"


class TestPlanner:
    """Test planner/simulator functionality."""
    
    def test_dry_run_fastapi(self):
        """Test dry-run for FastAPI project."""
        dsl = """
INTENT:
  name: fastapi-test
  goal: Test FastAPI generation

ENVIRONMENT:
  runtime: docker
  base_image: python:3.12-slim

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
    - api.expose POST /users
"""
        ir = parse_dsl(dsl)
        result = plan_intent(ir)
        
        assert result.success
        assert "fastapi" in result.generated_code.lower()
        assert "@app.get" in result.generated_code
        assert "@app.post" in result.generated_code
        assert "FROM python:3.12-slim" in result.dockerfile
        assert len(result.logs) > 0

    def test_dry_run_fastapi_path_params(self):
        """Path params and duplicate routes produce valid Python identifiers."""
        dsl = """
INTENT:
  name: fastapi-params
  goal: Test path param naming

ENVIRONMENT:
  runtime: docker
  base_image: python:3.12-slim

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /users
    - api.expose POST /users
    - api.expose GET /users/{id}
    - api.expose PUT /users/{id}
    - api.expose DELETE /users/{id}
"""
        ir = parse_dsl(dsl)
        result = plan_intent(ir)

        assert result.success
        code = result.generated_code
        assert "async def users_by_id" in code
        assert "users_{id}" not in code
        compile(code, "<generated>", "exec")
    
    def test_dry_run_express(self):
        """Test dry-run for Express.js project."""
        dsl = """
INTENT:
  name: express-test
  goal: Test Express generation

ENVIRONMENT:
  runtime: docker
  base_image: node:20

IMPLEMENTATION:
  language: node
  framework: express
  actions:
    - api.expose GET /health
"""
        ir = parse_dsl(dsl)
        result = plan_intent(ir)
        
        assert result.success
        assert "express" in result.generated_code.lower()
        assert "app.get" in result.generated_code
        assert "FROM node:20" in result.dockerfile
    
    def test_resource_estimation(self):
        """Test resource estimation."""
        dsl = """
INTENT:
  name: resource-test
  goal: Test resources

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
"""
        ir = parse_dsl(dsl)
        result = plan_intent(ir)
        
        assert "memory" in result.estimated_resources
        assert "cpu" in result.estimated_resources
        assert result.estimated_resources["memory"] == "512MB"  # FastAPI estimate


class TestCLI:
    """Test CLI functionality."""
    
    def test_cli_new_intent(self):
        """Test creating new intent via CLI."""
        cli = CLI(no_color=True)
        ir = cli.cmd_new("test-new", "Test goal")
        
        assert ir is not None
        assert ir.intent.name == "test-new"
        assert "Test goal" in ir.intent.goal
    
    def test_cli_plan(self):
        """Test planning via CLI."""
        cli = CLI(no_color=True)
        ir = cli.cmd_new("plan-test", "Test planning")
        result = cli.cmd_plan(ir)
        
        assert result is not None
        assert result.success
        assert len(result.logs) > 0
    
    def test_cli_iterate(self):
        """Test iteration via CLI."""
        cli = CLI(no_color=True)
        ir = cli.cmd_new("iter-test", "Test iteration")
        
        initial_count = ir.iteration_count
        ir = cli.cmd_iterate({"framework": "flask"}, ir)
        
        assert ir.iteration_count == initial_count + 1
        assert ir.implementation.framework == "flask"
    
    def test_cli_iterun_not_approved_without_confirmation(self):
        """Test that ITERUN requires explicit confirmation."""
        cli = CLI(no_color=True)
        ir = cli.cmd_new("iterun-test", "Test ITERUN")
        
        # Without explicit "ITERUN" input, should not approve
        assert not ir.iterun_approved


class TestIRModel:
    """Test IR model functionality."""
    
    def test_ir_serialization(self):
        """Test IR to JSON and back."""
        dsl = """
INTENT:
  name: serial-test
  goal: Test serialization

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
"""
        ir = parse_dsl(dsl)
        json_str = ir.to_json()
        ir_restored = IntentIR.from_json(json_str)
        
        assert ir_restored.intent.name == ir.intent.name
        assert ir_restored.intent.goal == ir.intent.goal
        assert len(ir_restored.implementation.actions) == len(ir.implementation.actions)
    
    def test_ir_iteration_history(self):
        """Test iteration history tracking."""
        ir = IntentIR()
        ir.intent.name = "history-test"
        ir.intent.goal = "Test history"
        
        ir.add_iteration({"action": "added"}, source="test")
        ir.add_iteration({"framework": "flask"}, source="test")
        
        assert ir.iteration_count == 2
        assert len(ir.iteration_history) == 2
        assert ir.iteration_history[0]["source"] == "test"
    
    def test_ir_iterun_approval(self):
        """Test ITERUN approval."""
        ir = IntentIR()
        ir.intent.name = "iterun-test"
        ir.intent.goal = "Test ITERUN"
        
        assert not ir.iterun_approved
        assert ir.execution_mode == ExecutionMode.DRY_RUN
        
        ir.approve_iterun()
        
        assert ir.iterun_approved
        assert ir.execution_mode == ExecutionMode.TRANSACTIONAL


class TestEndToEnd:
    """End-to-end workflow tests."""
    
    def test_complete_workflow_dry_run(self):
        """Test complete workflow up to dry-run."""
        # 1. Parse DSL
        dsl = """
INTENT:
  name: e2e-test
  goal: End-to-end test

ENVIRONMENT:
  runtime: docker
  base_image: python:3.12-slim

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
    - api.expose GET /health

EXECUTION:
  mode: dry-run
"""
        ir = parse_dsl(dsl)
        assert ir.intent.name == "e2e-test"
        
        # 2. Run dry-run
        result = plan_intent(ir)
        assert result.success
        assert ir.generated_code is not None
        assert ir.dockerfile is not None
        
        # 3. Iterate
        ir.add_iteration({"action": "api.expose POST /users"}, source="e2e-test")
        assert ir.iteration_count == 1
        
        # 4. Verify state
        assert not ir.iterun_approved
        assert ir.execution_mode == ExecutionMode.DRY_RUN
    
    def test_file_based_workflow(self):
        """Test workflow using DSL file."""
        cli = CLI(no_color=True)
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
INTENT:
  name: file-test
  goal: Test file loading

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /test
""")
            temp_path = f.name
        
        try:
            ir = cli.cmd_load(temp_path)
            assert ir is not None
            assert ir.intent.name == "file-test"
            
            result = cli.cmd_plan(ir)
            assert result.success
        finally:
            Path(temp_path).unlink()


def run_tests():
    """Run all tests and report results."""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
