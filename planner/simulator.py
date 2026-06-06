"""
ITERUN: Planner / Simulator
Performs dry-run execution and generates artifacts without side effects.
"""

import re
from typing import Dict, Any, List, Set
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ir.models import IntentIR, ActionType, RuntimeType


def _endpoint_to_func_name(endpoint: str, method: str, used: Set[str]) -> str:
    """Turn a route path into a valid, unique Python function name."""
    name = endpoint.strip("/")
    name = re.sub(r"\{([^}]+)\}", r"_by_\1", name)
    name = name.replace("/", "_")
    name = re.sub(r"[^\w]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        name = "root"
    if name[0].isdigit():
        name = f"_{name}"

    candidate = name
    if candidate in used:
        candidate = f"{name}_{method.lower()}"
    suffix = 2
    while candidate in used:
        candidate = f"{name}_{method.lower()}_{suffix}"
        suffix += 1

    used.add(candidate)
    return candidate


class DryRunResult:
    """Result of a dry-run simulation."""
    def __init__(self):
        self.success: bool = True
        self.logs: List[str] = []
        self.generated_code: str = ""
        self.dockerfile: str = ""
        self.compose_yaml: str = ""
        self.service_artifacts: Dict[str, Dict[str, Any]] = {}
        self.warnings: List[str] = []
        self.estimated_resources: Dict[str, Any] = {}
    
    def add_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "logs": self.logs,
            "generated_code": self.generated_code,
            "dockerfile": self.dockerfile,
            "compose_yaml": self.compose_yaml,
            "service_artifacts": {
                k: {kk: vv for kk, vv in v.items() if kk != "code"}
                for k, v in self.service_artifacts.items()
            },
            "warnings": self.warnings,
            "estimated_resources": self.estimated_resources
        }


class Planner:
    """
    Plans and simulates intent execution.
    Generates code, Dockerfiles, and estimates without actual execution.
    """
    
    def __init__(self):
        self.code_generators = {
            "python": self._generate_python_code,
            "node": self._generate_node_code,
        }
    
    def dry_run(self, ir: IntentIR) -> DryRunResult:
        """Perform dry-run simulation of the intent."""
        result = DryRunResult()
        
        result.add_log(f"Starting dry-run for intent: {ir.intent.name}")
        result.add_log(f"Goal: {ir.intent.goal}")
        
        # Generate code based on language
        lang = ir.implementation.language
        if lang in self.code_generators:
            result.add_log(f"Generating {lang} code...")
            result.generated_code = self.code_generators[lang](ir)
            result.add_log(f"Generated {len(result.generated_code)} bytes of code")
        else:
            result.warnings.append(f"No code generator for language: {lang}")
        
        # Generate Dockerfile
        if ir.environment.runtime == RuntimeType.DOCKER:
            result.add_log("Generating Dockerfile...")
            result.dockerfile = self._generate_dockerfile(ir)
            result.add_log("Dockerfile generated")
        
        # Simulate actions
        result.add_log("Simulating actions...")
        for action in ir.implementation.actions:
            self._simulate_action(action, result)
        
        # Estimate resources
        result.estimated_resources = self._estimate_resources(ir)
        result.add_log(f"Estimated memory: {result.estimated_resources.get('memory', 'N/A')}")
        result.add_log(f"Estimated CPU: {result.estimated_resources.get('cpu', 'N/A')}")
        
        result.add_log("Dry-run completed successfully")
        
        # Update IR with results
        ir.dry_run_logs = result.logs
        ir.generated_code = result.generated_code
        ir.dockerfile = result.dockerfile
        
        return result
    
    def _generate_python_code(self, ir: IntentIR) -> str:
        """Generate Python code based on IR."""
        framework = ir.implementation.framework
        
        if framework == "fastapi":
            return self._generate_fastapi_code(ir)
        elif framework == "flask":
            return self._generate_flask_code(ir)
        else:
            return self._generate_basic_python_code(ir)
    
    def _generate_fastapi_code(self, ir: IntentIR) -> str:
        """Generate FastAPI application code."""
        imports = [
            "from fastapi import FastAPI, HTTPException",
            "from pydantic import BaseModel",
            "from typing import Optional, List",
            "import uvicorn",
        ]
        
        code_lines = imports + [
            "",
            f'app = FastAPI(title="{ir.intent.name}", description="{ir.intent.goal}")',
            "",
        ]
        
        # Generate endpoints from actions
        used_func_names: Set[str] = set()
        for action in ir.implementation.actions:
            if action.type == ActionType.API_EXPOSE:
                method = (action.method or "GET").lower()
                endpoint = action.target or "/"
                func_name = _endpoint_to_func_name(endpoint, method, used_func_names)
                
                code_lines.extend([
                    f'@app.{method}("{endpoint}")',
                    f'async def {func_name}():',
                    f'    """Auto-generated endpoint for {endpoint}"""',
                    f'    return {{"status": "ok", "endpoint": "{endpoint}", "method": "{method.upper()}"}}',
                    "",
                ])
        
        # Add main block
        code_lines.extend([
            "",
            'if __name__ == "__main__":',
            '    uvicorn.run(app, host="0.0.0.0", port=8000)',
        ])
        
        return "\n".join(code_lines)
    
    def _generate_flask_code(self, ir: IntentIR) -> str:
        """Generate Flask application code."""
        code_lines = [
            "from flask import Flask, jsonify, request",
            "",
            "app = Flask(__name__)",
            "",
        ]
        
        used_func_names: Set[str] = set()
        for action in ir.implementation.actions:
            if action.type == ActionType.API_EXPOSE:
                method = action.method or "GET"
                endpoint = action.target or "/"
                func_name = _endpoint_to_func_name(endpoint, method, used_func_names)
                
                code_lines.extend([
                    f'@app.route("{endpoint}", methods=["{method}"])',
                    f'def {func_name}():',
                    f'    return jsonify({{"status": "ok", "endpoint": "{endpoint}"}})',
                    "",
                ])
        
        code_lines.extend([
            'if __name__ == "__main__":',
            '    app.run(host="0.0.0.0", port=8000)',
        ])
        
        return "\n".join(code_lines)
    
    def _generate_basic_python_code(self, ir: IntentIR) -> str:
        """Generate basic Python script."""
        return f'''#!/usr/bin/env python3
"""
Auto-generated script for: {ir.intent.name}
Goal: {ir.intent.goal}
"""

def main():
    print("Intent: {ir.intent.name}")
    print("Goal: {ir.intent.goal}")
    # TODO: Implement actions
    
if __name__ == "__main__":
    main()
'''
    
    def _generate_node_code(self, ir: IntentIR) -> str:
        """Generate Node.js code based on IR."""
        framework = ir.implementation.framework
        
        if framework == "express":
            return self._generate_express_code(ir)
        else:
            return self._generate_basic_node_code(ir)
    
    def _generate_express_code(self, ir: IntentIR) -> str:
        """Generate Express.js application code."""
        code_lines = [
            "const express = require('express');",
            "const app = express();",
            "",
            "app.use(express.json());",
            "",
        ]
        
        for action in ir.implementation.actions:
            if action.type == ActionType.API_EXPOSE:
                method = (action.method or "GET").lower()
                endpoint = action.target or "/"
                
                code_lines.extend([
                    f"app.{method}('{endpoint}', (req, res) => {{",
                    f"    res.json({{ status: 'ok', endpoint: '{endpoint}', method: '{method.upper()}' }});",
                    "});",
                    "",
                ])
        
        code_lines.extend([
            "const PORT = process.env.PORT || 8000;",
            "app.listen(PORT, () => {",
            f"    console.log(`{ir.intent.name} running on port ${{PORT}}`);",
            "});",
        ])
        
        return "\n".join(code_lines)
    
    def _generate_basic_node_code(self, ir: IntentIR) -> str:
        """Generate basic Node.js script."""
        return f'''// Auto-generated script for: {ir.intent.name}
// Goal: {ir.intent.goal}

console.log("Intent: {ir.intent.name}");
console.log("Goal: {ir.intent.goal}");
// TODO: Implement actions
'''
    
    def _generate_dockerfile(self, ir: IntentIR) -> str:
        """Generate Dockerfile based on IR."""
        lang = ir.implementation.language
        base_image = ir.environment.base_image
        
        lines = [
            f"# Auto-generated Dockerfile for: {ir.intent.name}",
            f"FROM {base_image}",
            "",
            "WORKDIR /app",
            "",
        ]
        
        if lang == "python":
            framework = ir.implementation.framework
            deps = ["uvicorn"] if framework == "fastapi" else []
            if framework:
                deps.append(framework)
            
            if deps:
                lines.extend([
                    f"RUN pip install --no-cache-dir {' '.join(deps)}",
                    "",
                ])
            
            lines.extend([
                "COPY app.py .",
                "",
                "EXPOSE 8000",
                "",
                'CMD ["python", "app.py"]',
            ])
        
        elif lang == "node":
            lines.extend([
                "COPY package*.json ./",
                "RUN npm install",
                "",
                "COPY . .",
                "",
                "EXPOSE 8000",
                "",
                'CMD ["node", "app.js"]',
            ])
        
        # Add ports from environment
        for port in ir.environment.ports:
            if port != 8000:
                lines.insert(-2, f"EXPOSE {port}")
        
        return "\n".join(lines)
    
    def _simulate_action(self, action, result: DryRunResult):
        """Simulate a single action."""
        action_str = f"{action.type.value}"
        if action.method:
            action_str += f" {action.method}"
        if action.target:
            action_str += f" {action.target}"
        
        result.add_log(f"  → Simulating: {action_str}")
        
        # Simulate based on action type
        if action.type == ActionType.API_EXPOSE:
            result.add_log(f"    ✓ Would expose endpoint: {action.method} {action.target}")
        
        elif action.type == ActionType.DB_CREATE:
            result.add_log(f"    ✓ Would create table: {action.target}")
        
        elif action.type == ActionType.DB_ADD_COLUMN:
            result.add_log(f"    ✓ Would add column to: {action.target}")
        
        elif action.type == ActionType.SHELL_EXEC:
            result.add_log(f"    ⚠ Would execute shell command: {action.target}")
            result.warnings.append(f"Shell execution planned: {action.target}")
        
        elif action.type == ActionType.REST_CALL:
            result.add_log(f"    ✓ Would call: {action.method} {action.target}")
        
        elif action.type == ActionType.FILE_CREATE:
            result.add_log(f"    ✓ Would create file: {action.target}")
    
    def _estimate_resources(self, ir: IntentIR) -> Dict[str, Any]:
        """Estimate resource requirements."""
        # Base estimates by language
        base_memory = {
            "python": "256MB",
            "node": "128MB",
        }
        
        memory = base_memory.get(ir.implementation.language, "256MB")
        
        # Adjust for framework
        if ir.implementation.framework in ["fastapi", "django"]:
            memory = "512MB"
        
        return {
            "memory": memory,
            "cpu": "0.5",
            "estimated_build_time": "30s",
            "estimated_startup_time": "5s",
        }


