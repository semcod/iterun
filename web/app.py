"""
ITERUN: Web Interface
FastAPI-based web UI for intent management.
"""

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import uuid

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ir.models import IntentIR, ExecutionMode
from parser.dsl_parser import parse_dsl, ParseError, ValidationError
from planner.simulator import plan_intent, DryRunResult
from executor.runner import execute_intent, ExecutionResult

# AI Gateway imports (optional)
try:
    from ai_gateway.gateway import AIGateway, GatewayConfig, get_gateway, OLLAMA_MODELS
    from ai_gateway.feedback_loop import FeedbackLoop, create_feedback_loop
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


app = FastAPI(
    title="ITERUN",
    description="DSL-based intent execution system with iterative refinement",
    version="0.1.0"
)

# In-memory storage for intents (in production, use a database)
intents_store: Dict[str, IntentIR] = {}

# Templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


# Pydantic models for API
class DSLInput(BaseModel):
    content: str


class IterationInput(BaseModel):
    changes: Dict[str, Any]
    source: str = "web"


class ExecutionRequest(BaseModel):
    workspace: Optional[str] = None


class GenerateRequest(BaseModel):
    prompt: str
    max_iterations: int = 5
    model: Optional[str] = None


class GenerateAndRunRequest(BaseModel):
    prompt: str
    output_dir: Optional[str] = None
    execute: bool = False
    verify: bool = False
    max_iterations: int = 5
    max_verify_iterations: int = 3
    model: Optional[str] = None


class PlanYAMLRequest(BaseModel):
    content: str
    output_dir: Optional[str] = None


class RegistryRefreshRequest(BaseModel):
    workspace: str = "generated"
    include_docker: bool = True


class ValidateYAMLRequest(BaseModel):
    content: str


# API Endpoints

_service = None


def _get_service():
    global _service
    if _service is None:
        from interfaces.service import IterunService
        _service = IterunService()
    return _service


@app.get("/api/health")
async def health():
    """Liveness probe for REST clients and orchestrators."""
    return {"status": "ok", "service": "iterun"}


@app.get("/api/interfaces")
async def list_interfaces():
    """Describe available integration surfaces (REST, CLI, SDK, MCP)."""
    return _get_service().interfaces_info()


@app.get("/api/registry")
async def get_registry(workspace: str = "generated"):
    """Service & artifact registry for a workspace (iterun.registry.json)."""
    return _get_service().registry_get(workspace)


@app.post("/api/registry/refresh")
async def refresh_registry_api(data: RegistryRefreshRequest):
    """Rescan workspace, write iterun.registry.json + Backstage + OTel exports."""
    return _get_service().registry_refresh(
        data.workspace,
        include_docker=data.include_docker,
    )


@app.get("/api/registry/list")
async def list_registries(pattern: str = "examples/*/generated"):
    """List registry summaries across workspace glob."""
    return {"registries": _get_service().registry_list(pattern)}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main dashboard."""
    return templates.TemplateResponse(
        request,
        "index.html",
        {"intents": list(intents_store.values())},
    )


@app.get("/api/intents")
async def list_intents():
    """List all stored intents."""
    return {
        "intents": [
            {
                "id": ir.id,
                "name": ir.intent.name,
                "goal": ir.intent.goal,
                "mode": ir.execution_mode.value,
                "iterun_approved": ir.iterun_approved,
                "iterations": ir.iteration_count
            }
            for ir in intents_store.values()
        ]
    }


@app.get("/api/schema")
async def get_schema():
    """JSON Schema for ITERUN intent DSL (LLM generation)."""
    return _get_service().schema()


@app.post("/api/intents/validate-yaml")
async def validate_yaml(data: ValidateYAMLRequest):
    """Validate YAML against schema + DSL parser."""
    return _get_service().validate_yaml(data.content)


@app.post("/api/intents/generate")
async def generate_intent_api(data: GenerateRequest):
    """Generate intent YAML from natural language (LiteLLM + retry loop)."""
    result = _get_service().generate(
        data.prompt,
        model=data.model,
        max_iterations=data.max_iterations,
    )
    if result.success and result.ir:
        intents_store[result.ir.id] = result.ir
    return result.to_dict()


@app.post("/api/pipeline/run")
async def run_pipeline_api(data: GenerateAndRunRequest):
    """Full pipeline: generate → plan → optional execute → optional verify."""
    result = _get_service().run_pipeline(
        data.prompt,
        output_dir=data.output_dir,
        execute=data.execute,
        verify=data.verify,
        max_iterations=data.max_iterations,
        max_verify_iterations=data.max_verify_iterations,
        model=data.model,
    )
    if result.generate and result.generate.ir:
        intents_store[result.generate.ir.id] = result.generate.ir
    return result.to_dict()


@app.post("/api/intents/generate-and-run")
async def generate_and_run_api(data: GenerateAndRunRequest):
    """Alias for POST /api/pipeline/run (backward compatible)."""
    return await run_pipeline_api(data)


@app.post("/api/intents/plan-yaml")
async def plan_yaml_api(data: PlanYAMLRequest):
    """Parse YAML and dry-run plan (single service or STACK)."""
    try:
        result = _get_service().plan_yaml(data.content, output_dir=data.output_dir)
        ir_dict = result.get("intent")
        if ir_dict and ir_dict.get("id"):
            intents_store[ir_dict["id"]] = parse_dsl(data.content)
        return result
    except (ParseError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/intents/parse")
async def parse_intent(data: DSLInput):
    """Parse DSL content and create new intent."""
    try:
        ir = parse_dsl(data.content)
        intents_store[ir.id] = ir
        return {
            "success": True,
            "id": ir.id,
            "intent": ir.to_dict()
        }
    except (ParseError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/intents/{intent_id}")
async def get_intent(intent_id: str):
    """Get intent by ID."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    return intents_store[intent_id].to_dict()


@app.delete("/api/intents/{intent_id}")
async def delete_intent(intent_id: str):
    """Delete intent by ID."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    del intents_store[intent_id]
    return {"success": True, "deleted": intent_id}


@app.post("/api/intents/{intent_id}/plan")
async def plan(intent_id: str):
    """Run dry-run planning for intent."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    ir = intents_store[intent_id]
    result = plan_intent(ir)
    
    return {
        "success": result.success,
        "logs": result.logs,
        "generated_code": result.generated_code,
        "dockerfile": result.dockerfile,
        "compose_yaml": result.compose_yaml,
        "service_artifacts": result.service_artifacts,
        "is_stack": bool(ir.stack and ir.stack.services),
        "warnings": result.warnings,
        "estimated_resources": result.estimated_resources,
    }


@app.post("/api/intents/{intent_id}/iterate")
async def iterate(intent_id: str, data: IterationInput):
    """Apply iterative changes to intent."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    ir = intents_store[intent_id]
    ir.add_iteration(data.changes, source=data.source)
    
    # Apply simple changes
    if "action" in data.changes:
        from parser.dsl_parser import DSLParser
        parser = DSLParser()
        action = parser._parse_action(data.changes["action"])
        if action:
            ir.implementation.actions.append(action)
    
    if "framework" in data.changes:
        ir.implementation.framework = data.changes["framework"]
    
    if "language" in data.changes:
        ir.implementation.language = data.changes["language"]
    
    return {
        "success": True,
        "iteration_count": ir.iteration_count,
        "intent": ir.to_dict()
    }


@app.post("/api/intents/{intent_id}/iterun")
async def approve_iterun(intent_id: str):
    """Approve intent for execution (ITERUN boundary)."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    ir = intents_store[intent_id]
    ir.approve_iterun()
    
    return {
        "success": True,
        "iterun_approved": True,
        "execution_mode": ir.execution_mode.value
    }


@app.post("/api/intents/{intent_id}/execute")
async def execute(intent_id: str, data: ExecutionRequest = None, validate: bool = True, auto_fix: bool = True):
    """Execute approved intent with validation and auto-fix."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    ir = intents_store[intent_id]
    
    # Auto-approve if not approved (skip ITERUN)
    if not ir.iterun_approved:
        ir.approve_iterun()
    
    workspace = data.workspace if data else None
    result = execute_intent(ir, workspace, skip_iterun_check=True, validate=validate, auto_fix=auto_fix)
    
    return {
        "success": result.success,
        "logs": result.logs,
        "artifacts": result.artifacts,
        "container_id": result.container_id,
        "endpoints": result.endpoints,
        "error": result.error,
        "execution_time": result.execution_time,
        "validation": result.validation.to_dict() if result.validation else None,
        "auto_fix_applied": result.auto_fix_applied,
        "fix_iterations": result.fix_iterations
    }


@app.post("/api/intents/{intent_id}/validate")
async def validate_intent(intent_id: str):
    """Validate running container endpoints for an intent."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    ir = intents_store[intent_id]
    
    from executor.runner import Executor, ExecutionResult
    executor = Executor()
    
    # Build endpoints from intent
    from config import get_config
    config = get_config()
    port = config.container_port
    base_url = f"http://localhost:{port}"
    endpoints = [base_url]
    
    seen_paths = set()
    for action in ir.implementation.actions:
        if action.type.value == "api.expose" and action.target:
            if action.target not in seen_paths:
                seen_paths.add(action.target)
                endpoints.append(f"{base_url}{action.target}")
    
    result = ExecutionResult()
    validation = executor._validate_endpoints(endpoints, result)
    
    return {
        "success": validation.success,
        "checks": validation.checks,
        "failed_endpoints": validation.failed_endpoints,
        "errors": validation.errors,
        "suggestions": validation.suggestions,
        "logs": result.logs
    }


@app.get("/api/containers/{container_id}/logs")
async def get_container_logs(container_id: str, tail: int = 50):
    """Get logs from a running container."""
    from executor.runner import Executor
    executor = Executor()
    logs = executor.get_container_logs(container_id, tail=tail)
    return {"container_id": container_id, "logs": logs}


@app.get("/api/intents/{intent_id}/code")
async def get_generated_code(intent_id: str):
    """Get generated code for intent."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    ir = intents_store[intent_id]
    return {
        "generated_code": ir.generated_code,
        "dockerfile": ir.dockerfile
    }


# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.1.0", "ai_available": AI_AVAILABLE}


# AI Gateway Endpoints

class AICompletionRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096


class AISuggestRequest(BaseModel):
    focus: Optional[str] = None


class AIChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


@app.get("/api/ai/status")
async def ai_status():
    """Check AI Gateway status."""
    if not AI_AVAILABLE:
        return {
            "available": False,
            "error": "AI Gateway not installed. Run: pip install litellm"
        }
    
    gateway = get_gateway()
    health = gateway.health_check()
    return {
        "available": True,
        "litellm_available": health["litellm_available"],
        "ollama_connected": health.get("ollama_connected", False),
        "default_model": health["default_model"],
        "ollama_url": health["ollama_url"],
        "available_models": health["available_models"],
        "error": health.get("error")
    }


@app.get("/api/ai/models")
async def list_models(max_params: float = 12.0):
    """List available AI models."""
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Gateway not available")
    
    gateway = get_gateway()
    models = gateway.list_models(max_params)
    return {
        "models": models,
        "default": gateway.config.default_model,
        "max_parameters": max_params
    }


@app.post("/api/ai/complete")
async def ai_complete(request: AICompletionRequest):
    """Generate AI completion."""
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Gateway not available")
    
    gateway = get_gateway()
    result = gateway.complete(
        prompt=request.prompt,
        model=request.model,
        system_prompt=request.system_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Completion failed"))
    
    return result


@app.post("/api/ai/chat")
async def ai_chat(request: AIChatRequest):
    """Chat with AI."""
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Gateway not available")
    
    gateway = get_gateway()
    
    prompt = request.message
    if request.context:
        prompt = f"{request.context}\n\nUser: {request.message}"
    
    result = gateway.complete(prompt, temperature=0.7)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Chat failed"))
    
    return {
        "response": result["content"],
        "model": result["model"],
        "usage": result.get("usage")
    }


@app.post("/api/intents/{intent_id}/ai/suggest")
async def ai_suggest(intent_id: str, request: AISuggestRequest = None):
    """Get AI suggestions for intent improvement."""
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Gateway not available")
    
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    ir = intents_store[intent_id]
    focus = request.focus if request else None
    
    loop = create_feedback_loop()
    result = loop.analyze(ir, focus)
    
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    
    return {
        "success": True,
        "suggestions": [s.to_dict() for s in result.suggestions],
        "model": result.model_used,
        "tokens_used": result.tokens_used,
        "next_steps": loop.suggest_next_steps(ir)
    }


@app.post("/api/intents/{intent_id}/ai/apply")
async def ai_apply_suggestions(intent_id: str):
    """Auto-apply AI suggestions to intent."""
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Gateway not available")
    
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    ir = intents_store[intent_id]
    
    loop = create_feedback_loop()
    result = loop.iterate(ir, auto_apply=True)
    
    return {
        "success": True,
        "applied_changes": result.applied_changes,
        "warnings": result.warnings,
        "suggestions": [s.to_dict() for s in result.suggestions],
        "intent": ir.to_dict()
    }


@app.post("/api/ai/generate-code")
async def generate_code(description: str, language: str = "python", framework: str = None):
    """Generate code snippet from description."""
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Gateway not available")
    
    gateway = get_gateway()
    result = gateway.generate_code_snippet(description, language, framework)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Code generation failed"))
    
    return result


def create_app() -> FastAPI:
    """Factory function for creating the app."""
    return app


if __name__ == "__main__":
    import uvicorn
    from config import get_config
    
    config = get_config()
    uvicorn.run(app, host=config.host, port=config.port)
