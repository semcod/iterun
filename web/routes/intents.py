"""Intent CRUD, planning, and execution API routes."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException

from config import get_config
from executor.docker_ops import get_container_logs
from executor.models import ExecutionResult
from executor.runner import execute_intent
from executor.validation import validate_endpoints
from parser.dsl_parser import parse_dsl, ParseError, ValidationError
from planner.plan import plan_intent
from web.schemas import (
    DSLInput,
    ExecutionRequest,
    GenerateAndRunRequest,
    GenerateRequest,
    IterationInput,
    PlanYAMLRequest,
    ValidateYAMLRequest,
)

if TYPE_CHECKING:
    from ir.models import IntentIR

router = APIRouter(tags=["intents"])

_service = None


def _get_service():
    global _service
    if _service is None:
        from interfaces.service import IterunService

        _service = IterunService()
    return _service


def _intents_store() -> dict[str, IntentIR]:
    from web.app import intents_store

    return intents_store


@router.get("/api/schema")
async def get_schema():
    return _get_service().schema()


@router.post("/api/intents/validate-yaml")
async def validate_yaml(data: ValidateYAMLRequest):
    return _get_service().validate_yaml(data.content)


@router.post("/api/intents/generate")
async def generate_intent_api(data: GenerateRequest):
    result = _get_service().generate(
        data.prompt,
        model=data.model,
        max_iterations=data.max_iterations,
    )
    if result.success and result.ir:
        _intents_store()[result.ir.id] = result.ir
    return result.to_dict()


@router.post("/api/pipeline/run")
async def run_pipeline_api(data: GenerateAndRunRequest):
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
        _intents_store()[result.generate.ir.id] = result.generate.ir
    return result.to_dict()


@router.post("/api/intents/generate-and-run")
async def generate_and_run_api(data: GenerateAndRunRequest):
    return await run_pipeline_api(data)


@router.post("/api/intents/plan-yaml")
async def plan_yaml_api(data: PlanYAMLRequest):
    try:
        result = _get_service().plan_yaml(data.content, output_dir=data.output_dir)
        ir_dict = result.get("intent")
        if ir_dict and ir_dict.get("id"):
            _intents_store()[ir_dict["id"]] = parse_dsl(data.content)
        return result
    except (ParseError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/api/intents/parse")
async def parse_intent(data: DSLInput):
    try:
        ir = parse_dsl(data.content)
        _intents_store()[ir.id] = ir
        return {"success": True, "id": ir.id, "intent": ir.to_dict()}
    except (ParseError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/api/intents")
async def list_intents():
    return {
        "intents": [
            {
                "id": ir.id,
                "name": ir.intent.name,
                "goal": ir.intent.goal,
                "mode": ir.execution_mode.value,
                "iterun_approved": ir.iterun_approved,
                "iterations": ir.iteration_count,
            }
            for ir in _intents_store().values()
        ]
    }


@router.get("/api/intents/{intent_id}")
async def get_intent(intent_id: str):
    store = _intents_store()
    if intent_id not in store:
        raise HTTPException(status_code=404, detail="Intent not found")
    return store[intent_id].to_dict()


@router.delete("/api/intents/{intent_id}")
async def delete_intent(intent_id: str):
    store = _intents_store()
    if intent_id not in store:
        raise HTTPException(status_code=404, detail="Intent not found")
    del store[intent_id]
    return {"success": True, "deleted": intent_id}


@router.post("/api/intents/{intent_id}/plan")
async def plan(intent_id: str):
    store = _intents_store()
    if intent_id not in store:
        raise HTTPException(status_code=404, detail="Intent not found")
    ir = store[intent_id]
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


@router.post("/api/intents/{intent_id}/iterate")
async def iterate(intent_id: str, data: IterationInput):
    store = _intents_store()
    if intent_id not in store:
        raise HTTPException(status_code=404, detail="Intent not found")
    ir = store[intent_id]
    ir.add_iteration(data.changes, source=data.source)
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
        "intent": ir.to_dict(),
    }


@router.post("/api/intents/{intent_id}/iterun")
async def approve_iterun(intent_id: str):
    store = _intents_store()
    if intent_id not in store:
        raise HTTPException(status_code=404, detail="Intent not found")
    ir = store[intent_id]
    ir.approve_iterun()
    return {
        "success": True,
        "iterun_approved": True,
        "execution_mode": ir.execution_mode.value,
    }


@router.post("/api/intents/{intent_id}/execute")
async def execute(
    intent_id: str,
    data: ExecutionRequest = None,
    validate: bool = True,
    auto_fix: bool = True,
):
    store = _intents_store()
    if intent_id not in store:
        raise HTTPException(status_code=404, detail="Intent not found")
    ir = store[intent_id]
    if not ir.iterun_approved:
        ir.approve_iterun()
    workspace = data.workspace if data else None
    result = execute_intent(
        ir, workspace, skip_iterun_check=True, validate=validate, auto_fix=auto_fix
    )
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
        "fix_iterations": result.fix_iterations,
    }


@router.post("/api/intents/{intent_id}/validate")
async def validate_intent(intent_id: str):
    store = _intents_store()
    if intent_id not in store:
        raise HTTPException(status_code=404, detail="Intent not found")
    ir = store[intent_id]
    config = get_config()
    port = config.container_port
    base_url = f"http://localhost:{port}"
    endpoints = [base_url]
    seen_paths: set[str] = set()
    for action in ir.implementation.actions:
        if action.type.value == "api.expose" and action.target:
            if action.target not in seen_paths:
                seen_paths.add(action.target)
                endpoints.append(f"{base_url}{action.target}")
    result = ExecutionResult()
    validation = validate_endpoints(endpoints, result, timeout=10)
    return {
        "success": validation.success,
        "checks": validation.checks,
        "failed_endpoints": validation.failed_endpoints,
        "errors": validation.errors,
        "suggestions": validation.suggestions,
        "logs": result.logs,
    }


@router.get("/api/containers/{container_id}/logs")
async def container_logs(container_id: str, tail: int = 50, workspace: str | None = None):
    ws = Path(workspace) if workspace else Path(get_config().workspace_dir or ".")
    logs = get_container_logs(ws, container_id, tail=tail)
    return {"container_id": container_id, "logs": logs}


@router.get("/api/intents/{intent_id}/code")
async def get_generated_code(intent_id: str):
    store = _intents_store()
    if intent_id not in store:
        raise HTTPException(status_code=404, detail="Intent not found")
    ir = store[intent_id]
    return {"generated_code": ir.generated_code, "dockerfile": ir.dockerfile}
