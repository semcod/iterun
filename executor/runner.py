"""
INTENT-ITERATIVE: Executor
Handles actual execution of approved intents (after AMEN boundary).
Includes post-execution validation and auto-fix capabilities.
"""

import subprocess
import tempfile
import shutil
import time
import socket
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

import sys

CONSTANT_3 = 3
CONSTANT_12 = 12
CONSTANT_30 = 30
PORT_50 = 50
CONSTANT_60 = 60
CONSTANT_300 = 300
CONSTANT_400 = 400
CONSTANT_500 = 500
CONSTANT_8000 = 8000


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from ir.models import IntentIR, ExecutionMode, RuntimeType
from config import get_config

# Try to import httpx for validation
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class ExecutionError(Exception):
    """Raised when execution fails."""
    pass


class ValidationResult:
    """Result of post-execution validation."""
    def __init__(self):
        self.success: bool = False
        self.checks: List[Dict[str, Any]] = []
        self.failed_endpoints: List[str] = []
        self.errors: List[str] = []
        self.suggestions: List[str] = []
    
    def add_check(self, endpoint: str, status: int, ok: bool, error: str = None):
        self.checks.append({
            "endpoint": endpoint,
            "status": status,
            "ok": ok,
            "error": error
        })
        if not ok:
            self.failed_endpoints.append(endpoint)
            if error:
                self.errors.append(f"{endpoint}: {error}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "checks": self.checks,
            "failed_endpoints": self.failed_endpoints,
            "errors": self.errors,
            "suggestions": self.suggestions
        }


class ExecutionResult:
    """Result of intent execution."""
    def __init__(self):
        self.success: bool = False
        self.logs: List[str] = []
        self.artifacts: Dict[str, str] = {}  # filename -> path
        self.container_id: Optional[str] = None
        self.endpoints: List[str] = []
        self.error: Optional[str] = None
        self.execution_time: float = 0.0
        self.validation: Optional[ValidationResult] = None
        self.auto_fix_applied: bool = False
        self.fix_iterations: int = 0
    
    def add_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "logs": self.logs,
            "artifacts": self.artifacts,
            "container_id": self.container_id,
            "endpoints": self.endpoints,
            "error": self.error,
            "execution_time": self.execution_time,
            "validation": self.validation.to_dict() if self.validation else None,
            "auto_fix_applied": self.auto_fix_applied,
            "fix_iterations": self.fix_iterations
        }


class Executor:
    """
    Executes approved intents.
    Only runs after AMEN boundary is passed.
    Includes validation and auto-fix capabilities.
    """
    
    MAX_FIX_ITERATIONS = 3
    VALIDATION_TIMEOUT = 10
    STARTUP_WAIT = 2
    
    def __init__(self, workspace: str = None):
        self.config = get_config()
        workspace = workspace or self.config.workspace_dir
        self.workspace = Path(workspace) if workspace else Path(tempfile.mkdtemp(prefix="intent-"))
        self.workspace.mkdir(parents=True, exist_ok=True)
    
    def execute(
        self,
        ir: IntentIR,
        skip_amen_check: bool = None,
        validate: bool = True,
        auto_fix: bool = True
    ) -> ExecutionResult:
        """
        Execute an approved intent with optional validation and auto-fix.
        
        Args:
            ir: IntentIR to execute
            skip_amen_check: Skip AMEN approval check
            validate: Run post-execution validation
            auto_fix: Attempt automatic fixes if validation fails
        """
        result = ExecutionResult()
        start_time = datetime.now()
        
        # Check if we should skip AMEN check
        skip_check = skip_amen_check if skip_amen_check is not None else self.config.skip_amen_confirmation
        
        # Check AMEN approval (unless skipped)
        if not skip_check:
            if not ir.amen_approved:
                result.error = "Intent not approved. Call approve_amen() first."
                result.add_log("ERROR: Execution blocked - AMEN boundary not passed")
                return result
            
            if ir.execution_mode != ExecutionMode.TRANSACTIONAL:
                result.error = "Intent is in dry-run mode. Change to transactional mode."
                result.add_log("ERROR: Execution blocked - still in dry-run mode")
                return result
        else:
            # Auto-approve if skipping check
            if not ir.amen_approved:
                ir.approve_amen()
                result.add_log("Auto-approved intent (SKIP_AMEN_CONFIRMATION=true)")
        
        result.add_log(f"Starting execution for: {ir.intent.name}")
        result.add_log(f"Workspace: {self.workspace}")
        
        try:
            # Write generated files
            self._write_artifacts(ir, result)
            
            # Execute based on runtime
            if ir.environment.runtime == RuntimeType.DOCKER:
                self._execute_docker(ir, result)
            elif ir.environment.runtime == RuntimeType.LOCAL:
                self._execute_local(ir, result)
            else:
                result.add_log(f"Runtime {ir.environment.runtime.value} not yet supported")
                result.error = f"Unsupported runtime: {ir.environment.runtime.value}"
            
            # Validation and auto-fix loop
            if not result.error and validate and result.endpoints:
                self._validate_and_fix(ir, result, auto_fix)
            
            if not result.error:
                result.success = True
                result.add_log("Execution completed successfully")
        
        except Exception as e:
            result.error = str(e)
            result.add_log(f"ERROR: {e}")
        
        result.execution_time = (datetime.now() - start_time).total_seconds()
        return result
    
    def _validate_and_fix(self, ir: IntentIR, result: ExecutionResult, auto_fix: bool):
        """Run validation and attempt auto-fix if needed."""
        iteration = 0
        
        while iteration < self.MAX_FIX_ITERATIONS:
            # Wait for container to start
            result.add_log(f"Waiting {self.STARTUP_WAIT}s for container startup...")
            time.sleep(self.STARTUP_WAIT)
            
            # Run validation
            validation = self._validate_endpoints(result.endpoints, result)
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
            
            # Attempt auto-fix
            result.add_log(f"Attempting auto-fix (iteration {iteration}/{self.MAX_FIX_ITERATIONS})")
            
            fixed = self._attempt_fix(ir, result, validation)
            
            if not fixed:
                result.add_log("Could not apply automatic fix")
                break
            
            result.auto_fix_applied = True
            
            # Restart container with fixed code
            result.add_log("Restarting container with fixes...")
            self._restart_container(ir, result)
        
        if not result.validation.success:
            result.add_log("⚠ Some endpoints may not be working correctly")
            result.add_log("Suggestions:")
            for suggestion in result.validation.suggestions:
                result.add_log(f"  • {suggestion}")
    
    def _validate_endpoints(self, endpoints: List[str], result: ExecutionResult) -> ValidationResult:
        """Validate that endpoints are responding correctly."""
        validation = ValidationResult()
        
        if not HTTPX_AVAILABLE:
            validation.success = True
            result.add_log("httpx not available, skipping validation")
            return validation
        
        # Filter to unique base endpoints
        checked = set()
        
        for endpoint in endpoints:
            if endpoint in checked:
                continue
            checked.add(endpoint)
            
            try:
                # Try to connect
                with httpx.Client(timeout=self.VALIDATION_TIMEOUT) as client:
                    response = client.get(endpoint)
                    
                    if response.status_code < 400:
                        validation.add_check(endpoint, response.status_code, True)
                        result.add_log(f"  ✓ {endpoint} → {response.status_code}")
                    else:
                        validation.add_check(
                            endpoint,
                            response.status_code,
                            False,
                            f"HTTP {response.status_code}"
                        )
                        result.add_log(f"  ✗ {endpoint} → {response.status_code}")
            
            except httpx.ConnectError as e:
                validation.add_check(endpoint, 0, False, "Connection refused")
                result.add_log(f"  ✗ {endpoint} → Connection refused")
                validation.suggestions.append(
                    "Container may still be starting or crashed. Check 'docker logs'"
                )
            
            except httpx.TimeoutException:
                validation.add_check(endpoint, 0, False, "Timeout")
                result.add_log(f"  ✗ {endpoint} → Timeout")
                validation.suggestions.append(
                    "Endpoint is taking too long to respond"
                )
            
            except Exception as e:
                validation.add_check(endpoint, 0, False, str(e))
                result.add_log(f"  ✗ {endpoint} → {e}")
        
        validation.success = len(validation.failed_endpoints) == 0
        
        # Add suggestions based on errors
        if not validation.success:
            if any("Connection refused" in e for e in validation.errors):
                validation.suggestions.append(
                    "Check if the application is listening on the correct port"
                )
                validation.suggestions.append(
                    "Verify Dockerfile EXPOSE matches application port"
                )
            
            if any("404" in str(c.get("status")) for c in validation.checks):
                validation.suggestions.append(
                    "Some routes may not be registered correctly"
                )
        
        return validation
    
    def _attempt_fix(self, ir: IntentIR, result: ExecutionResult, validation: ValidationResult) -> bool:
        """Attempt to fix issues found during validation."""
        fixes_applied = []
        
        # Analyze errors and apply fixes
        for error in validation.errors:
            # Connection refused - might be wrong port or app not starting
            if "Connection refused" in error:
                # Check if app has proper __main__ block
                if ir.generated_code and "if __name__" not in ir.generated_code:
                    ir.generated_code = self._add_main_block(ir)
                    fixes_applied.append("Added __main__ block")
                
                # Check if port is correct
                if ir.implementation.framework == "fastapi":
                    port = self.config.container_port
                    if f"port={port}" not in ir.generated_code:
                        ir.generated_code = ir.generated_code.replace(
                            'uvicorn.run(app, host="0.0.0.0")',
                            f'uvicorn.run(app, host="0.0.0.0", port={port})'
                        )
                        fixes_applied.append(f"Fixed port to {port}")
            
            # 500 errors - internal server error
            if "500" in error:
                # Add error handling
                if "try:" not in ir.generated_code:
                    fixes_applied.append("Consider adding try/except blocks")
        
        if fixes_applied:
            result.add_log(f"Applied fixes: {', '.join(fixes_applied)}")
            
            # Record as iteration
            ir.add_iteration({
                "auto_fix": True,
                "fixes": fixes_applied,
                "validation_errors": validation.errors
            }, source="auto_fix")
            
            # Re-write artifacts
            self._write_artifacts(ir, result)
            return True
        
        return False
    
    def _add_main_block(self, ir: IntentIR) -> str:
        """Add missing __main__ block to code."""
        code = ir.generated_code
        
        if ir.implementation.framework == "fastapi":
            if "if __name__" not in code:
                port = self.config.container_port
                code += f'''

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port={port})
'''
        elif ir.implementation.framework == "flask":
            if "if __name__" not in code:
                port = self.config.container_port
                code += f'''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port={port})
'''
        elif ir.implementation.framework == "express":
            if "app.listen" not in code:
                port = self.config.container_port
                code += f'''

app.listen({port}, '0.0.0.0', () => {{
    console.log('Server running on port {port}');
}});
'''
        
        return code
    
    def _restart_container(self, ir: IntentIR, result: ExecutionResult):
        """Stop old container and start new one with fixes."""
        if result.container_id:
            # Stop and remove old container
            subprocess.run(
                ["docker", "rm", "-f", result.container_id],
                capture_output=True,
                timeout=30
            )
            result.add_log(f"Stopped container: {result.container_id}")
        
        # Rebuild and run
        self._execute_docker(ir, result)
    
    def _write_artifacts(self, ir: IntentIR, result: ExecutionResult):
        """Write generated code and config files."""
        lang = ir.implementation.language
        
        # Main application file
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
        
        # Dockerfile
        if ir.dockerfile:
            dockerfile = self.workspace / "Dockerfile"
            dockerfile.write_text(ir.dockerfile)
            result.artifacts["Dockerfile"] = str(dockerfile)
            result.add_log("Written: Dockerfile")
        
        # Package files
        if lang == "node":
            package_json = self.workspace / "package.json"
            deps = {}
            if ir.implementation.framework == "express":
                deps["express"] = "^4.18.0"
            
            package_content = {
                "name": ir.intent.name,
                "version": "1.0.0",
                "main": "app.js",
                "dependencies": deps
            }
            
            import json
            package_json.write_text(json.dumps(package_content, indent=2))
            result.artifacts["package.json"] = str(package_json)
            result.add_log("Written: package.json")
    
    def _find_available_port(self, start_port: int = 8000) -> int:
        """Find an available port starting from start_port."""
        port = start_port
        max_attempts = 100
        
        for _ in range(max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                port += 1
        
        return start_port + max_attempts  # Fallback
    
    def _execute_docker(self, ir: IntentIR, result: ExecutionResult):
        """Build and run Docker container."""
        prefix = self.config.container_prefix
        image_name = f"{prefix}-{ir.intent.name}:latest"
        container_name = f"{prefix}-{ir.intent.name}-{ir.id}"
        
        # Find available port
        requested_port = self.config.container_port
        if ir.environment.ports:
            requested_port = ir.environment.ports[0]
        
        host_port = self._find_available_port(requested_port)
        if host_port != requested_port:
            result.add_log(f"Port {requested_port} in use, using {host_port}")
        
        result.add_log(f"Building Docker image: {image_name}")
        
        # Build image
        build_cmd = ["docker", "build", "-t", image_name, str(self.workspace)]
        build_result = subprocess.run(
            build_cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if build_result.returncode != 0:
            result.error = f"Docker build failed: {build_result.stderr}"
            result.add_log(f"Build error: {build_result.stderr[:500]}")
            return
        
        result.add_log("Docker image built successfully")
        
        # Stop existing container with same name if exists
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            capture_output=True,
            timeout=30
        )
        
        # Run container
        container_port = self.config.container_port
        run_cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "-p", f"{host_port}:{container_port}",
        ]
        
        # Add environment variables
        for key, value in ir.environment.env_vars.items():
            run_cmd.extend(["-e", f"{key}={value}"])
        
        # Add additional ports
        for port in ir.environment.ports:
            if port != container_port:
                extra_host_port = self._find_available_port(port)
                run_cmd.extend(["-p", f"{extra_host_port}:{port}"])
        
        run_cmd.append(image_name)
        
        result.add_log(f"Starting container: {container_name}")
        
        run_result = subprocess.run(
            run_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if run_result.returncode != 0:
            result.error = f"Docker run failed: {run_result.stderr}"
            result.add_log(f"Run error: {run_result.stderr[:500]}")
            return
        
        result.container_id = run_result.stdout.strip()[:12]
        result.add_log(f"Container started: {result.container_id}")
        
        # Record endpoints (deduplicated)
        base_url = f"http://localhost:{host_port}"
        result.endpoints = [base_url]
        
        seen_paths = set()
        for action in ir.implementation.actions:
            if action.type.value == "api.expose" and action.target:
                path = action.target
                if path not in seen_paths:
                    seen_paths.add(path)
                    result.endpoints.append(f"{base_url}{path}")
    
    def _execute_local(self, ir: IntentIR, result: ExecutionResult):
        """Execute locally without Docker."""
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
        
        # Start as background process
        result.add_log(f"Command: {' '.join(cmd)}")
        result.add_log("Application would start here (non-blocking in production)")
        
        # In production, we'd use subprocess.Popen for non-blocking execution
        port = self._find_available_port(self.config.container_port)
        result.endpoints.append(f"http://localhost:{port}")
    
    def get_container_logs(self, container_id: str, tail: int = 50) -> str:
        """Get logs from a container."""
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(tail), container_id],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error getting logs: {e}"
    
    def cleanup(self):
        """Clean up workspace."""
        if self.workspace.exists():
            shutil.rmtree(self.workspace)


def execute_intent(
    ir: IntentIR,
    workspace: str = None,
    skip_amen_check: bool = None,
    validate: bool = True,
    auto_fix: bool = True
) -> ExecutionResult:
    """Convenience function to execute an approved intent."""
    executor = Executor(workspace)
    return executor.execute(ir, skip_amen_check=skip_amen_check, validate=validate, auto_fix=auto_fix)
