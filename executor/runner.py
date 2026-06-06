"""
ITERUN: Executor
Handles actual execution of approved intents (after ITERUN boundary).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path

import sys

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from executor.docker_ops import (
    execute_compose_stack,
    execute_docker,
    get_container_logs as fetch_container_logs,
)
from executor.models import ExecutionResult
from executor.validation import attempt_auto_fix, filter_validation_endpoints, validate_endpoints
from ir.models import ExecutionMode, IntentIR, RuntimeType


class Executor:
    """Executes approved intents with validation and auto-fix."""

    MAX_FIX_ITERATIONS = 3
    VALIDATION_TIMEOUT = 10
    STARTUP_WAIT = 2

    def __init__(self, workspace: str | None = None):
        self.config = get_config()
        workspace = workspace or self.config.workspace_dir
        self.workspace = Path(workspace) if workspace else Path(tempfile.mkdtemp(prefix="intent-"))
        self.workspace.mkdir(parents=True, exist_ok=True)

    def execute(
        self,
        ir: IntentIR,
        skip_iterun_check: bool | None = None,
        validate: bool = True,
        auto_fix: bool = True,
    ) -> ExecutionResult:
        """Execute an approved intent with optional validation and auto-fix."""
        result = ExecutionResult()
        start_time = datetime.now()

        skip_check = (
            skip_iterun_check
            if skip_iterun_check is not None
            else self.config.skip_iterun_confirmation
        )

        if not skip_check:
            if not ir.iterun_approved:
                result.error = "Intent not approved. Call approve_iterun() first."
                result.add_log("ERROR: Execution blocked - ITERUN boundary not passed")
                return result

            if ir.execution_mode != ExecutionMode.TRANSACTIONAL:
                result.error = "Intent is in dry-run mode. Change to transactional mode."
                result.add_log("ERROR: Execution blocked - still in dry-run mode")
                return result
        elif not ir.iterun_approved:
            ir.approve_iterun()
            result.add_log("Auto-approved intent (SKIP_ITERUN_CONFIRMATION=true)")

        result.add_log(f"Starting execution for: {ir.intent.name}")
        result.add_log(f"Workspace: {self.workspace}")

        if self.config.runtime == "pactown":
            from integrations.pactown_runtime import execute_pactown

            return execute_pactown(
                ir,
                self.workspace,
                validate=validate,
                startup_wait=self.config.startup_wait,
            )

        try:
            self._write_artifacts(ir, result)

            if ir.environment.runtime == RuntimeType.DOCKER:
                if ir.stack and (self.workspace / "docker-compose.yaml").is_file():
                    execute_compose_stack(
                        ir,
                        self.workspace,
                        result,
                        container_prefix=self.config.container_prefix,
                    )
                else:
                    execute_docker(
                        ir,
                        self.workspace,
                        result,
                        container_prefix=self.config.container_prefix,
                        container_port=self.config.container_port,
                    )
            elif ir.environment.runtime == RuntimeType.LOCAL:
                self._execute_local(ir, result)
            else:
                result.add_log(f"Runtime {ir.environment.runtime.value} not yet supported")
                result.error = f"Unsupported runtime: {ir.environment.runtime.value}"

            if not result.error and validate and result.endpoints:
                self._validate_and_fix(ir, result, auto_fix)

            if not result.error:
                if result.validation and not result.validation.success:
                    result.add_log("Execution deployed but endpoint validation failed")
                else:
                    result.success = True
                    result.add_log("Execution completed successfully")

        except Exception as e:
            result.error = str(e)
            result.add_log(f"ERROR: {e}")

        result.execution_time = (datetime.now() - start_time).total_seconds()
        return result

    def _validate_and_fix(
        self, ir: IntentIR, result: ExecutionResult, auto_fix: bool
    ) -> None:
        """Run validation and attempt auto-fix if needed."""
        iteration = 0

        while iteration < self.MAX_FIX_ITERATIONS:
            result.add_log(f"Waiting {self.STARTUP_WAIT}s for container startup...")
            time.sleep(self.STARTUP_WAIT)

            endpoints = filter_validation_endpoints(result.endpoints)
            validation = validate_endpoints(
                endpoints,
                result,
                timeout=self.VALIDATION_TIMEOUT,
            )
            result.validation = validation

            if validation.success:
                result.add_log("✓ All endpoints validated successfully")
                break

            result.add_log(f"✗ Validation failed: {len(validation.failed_endpoints)} endpoints")

            if not auto_fix:
                result.add_log("Auto-fix disabled, stopping")
                break

            iteration += 1
            result.fix_iterations = iteration

            if iteration >= self.MAX_FIX_ITERATIONS:
                result.add_log(f"Max fix iterations ({self.MAX_FIX_ITERATIONS}) reached")
                break

            result.add_log(
                f"Attempting auto-fix (iteration {iteration}/{self.MAX_FIX_ITERATIONS})"
            )

            fixed = attempt_auto_fix(
                ir,
                result,
                validation,
                container_port=self.config.container_port,
            )

            if not fixed:
                result.add_log("Could not apply automatic fix")
                break

            result.auto_fix_applied = True
            result.add_log("Restarting container with fixes...")
            self._write_artifacts(ir, result)
            self._restart_container(ir, result)

        if result.validation and not result.validation.success:
            result.add_log("⚠ Some endpoints may not be working correctly")
            result.add_log("Suggestions:")
            for suggestion in result.validation.suggestions:
                result.add_log(f"  • {suggestion}")

    def _restart_container(self, ir: IntentIR, result: ExecutionResult) -> None:
        """Stop old container and start new one with fixes."""
        if result.container_id:
            subprocess.run(
                ["docker", "rm", "-f", result.container_id],
                capture_output=True,
                timeout=30,
            )
            result.add_log(f"Stopped container: {result.container_id}")

        execute_docker(
            ir,
            self.workspace,
            result,
            container_prefix=self.config.container_prefix,
            container_port=self.config.container_port,
        )

    def _write_artifacts(self, ir: IntentIR, result: ExecutionResult) -> None:
        """Write generated code and config files."""
        if ir.stack and (self.workspace / "docker-compose.yaml").is_file():
            result.add_log("STACK workspace: using services/* + docker-compose.yaml")
            result.artifacts["docker-compose.yaml"] = str(
                self.workspace / "docker-compose.yaml"
            )
            return

        lang = ir.implementation.language

        if ir.generated_code:
            if lang == "python":
                app_file = self.workspace / "app.py"
            elif lang == "node":
                app_file = self.workspace / "app.js"
            else:
                app_file = self.workspace / "app.txt"

            app_file.write_text(ir.generated_code)
            result.artifacts["app"] = str(app_file)
            result.add_log(f"Written: {app_file.name}")

        if ir.dockerfile:
            dockerfile = self.workspace / "Dockerfile"
            dockerfile.write_text(ir.dockerfile)
            result.artifacts["Dockerfile"] = str(dockerfile)
            result.add_log("Written: Dockerfile")

        if lang == "node":
            package_json = self.workspace / "package.json"
            deps: dict[str, str] = {}
            if ir.implementation.framework == "express":
                deps["express"] = "^4.18.0"

            package_content = {
                "name": ir.intent.name,
                "version": "1.0.0",
                "main": "app.js",
                "dependencies": deps,
            }
            package_json.write_text(json.dumps(package_content, indent=2))
            result.artifacts["package.json"] = str(package_json)
            result.add_log("Written: package.json")

    def _execute_local(self, ir: IntentIR, result: ExecutionResult) -> None:
        """Execute locally without Docker."""
        from executor.docker_ops import find_available_port

        lang = ir.implementation.language
        app_file = result.artifacts.get("app")

        if not app_file:
            result.error = "No application file generated"
            return

        result.add_log(f"Starting local execution: {app_file}")

        if lang == "python":
            cmd = ["python", app_file]
        elif lang == "node":
            cmd = ["node", app_file]
        else:
            result.error = f"Unsupported language for local execution: {lang}"
            return

        result.add_log(f"Command: {' '.join(cmd)}")
        result.add_log("Application would start here (non-blocking in production)")

        port = find_available_port(self.config.container_port)
        result.endpoints.append(f"http://localhost:{port}")

    def get_container_logs(self, container_id: str, tail: int = 50) -> str:
        """Get logs from a container or docker compose project (STACK)."""
        return fetch_container_logs(self.workspace, container_id, tail=tail)

    def cleanup(self) -> None:
        """Clean up workspace."""
        if self.workspace.exists():
            shutil.rmtree(self.workspace)


def execute_intent(
    ir: IntentIR,
    workspace: str | None = None,
    skip_iterun_check: bool | None = None,
    validate: bool = True,
    auto_fix: bool = True,
) -> ExecutionResult:
    """Convenience function to execute an approved intent."""
    executor = Executor(workspace)
    return executor.execute(
        ir,
        skip_iterun_check=skip_iterun_check,
        validate=validate,
        auto_fix=auto_fix,
    )
