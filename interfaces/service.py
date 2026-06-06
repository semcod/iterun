"""Unified ITERUN service layer — used by REST, SDK, MCP, CLI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dsl.schema import get_json_schema, validate_yaml_document
from executor.runner import execute_intent
from generator.intent_generator import GenerateResult, IntentGenerator
from generator.pipeline import PipelineResult, run_pipeline as run_generator_pipeline
from ir.models import IntentIR
from parser.dsl_parser import parse_dsl, ParseError, ValidationError
from planner.plan import plan_intent
from planner.simulator import DryRunResult


def _write_plan_output(ir: IntentIR, result: DryRunResult, output_dir: str | Path) -> dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}

    if ir.stack and ir.stack.services:
        from planner.stack_artifacts import write_stack_artifacts
        return write_stack_artifacts(out, ir, result)

    plan_file = out / "plan.result.json"
    plan_file.write_text(
        json.dumps({"intent": ir.to_dict(), "plan": result.to_dict()}, indent=2),
        encoding="utf-8",
    )
    written["plan.result.json"] = str(plan_file)

    if result.generated_code:
        app_name = "app.py" if ir.implementation.language == "python" else "app.js"
        app_path = out / app_name
        app_path.write_text(result.generated_code, encoding="utf-8")
        written[app_name] = str(app_path)
    if result.dockerfile:
        df = out / "Dockerfile"
        df.write_text(result.dockerfile, encoding="utf-8")
        written["Dockerfile"] = str(df)
    if result.compose_yaml:
        compose = out / "docker-compose.yaml"
        compose.write_text(result.compose_yaml, encoding="utf-8")
        written["docker-compose.yaml"] = str(compose)
    return written


class IterunService:
    """Single entry point for programmatic access to ITERUN."""

    def __init__(self, *, model: str | None = None, max_iterations: int = 5):
        self.model = model
        self.max_iterations = max_iterations

    @staticmethod
    def interfaces_info() -> dict[str, Any]:
        return {
            "name": "iterun",
            "version": "0.1.7",
            "surfaces": [
                {
                    "id": "rest",
                    "description": "FastAPI HTTP API",
                    "entry": "python -m web.app",
                    "docs": "/docs",
                    "health": "/api/health",
                },
                {
                    "id": "cli",
                    "description": "Command-line interface",
                    "entry": "iterun",
                    "commands": ["generate", "plan", "execute", "validate", "schema", "shell"],
                },
                {
                    "id": "sdk",
                    "description": "Python SDK (local or remote)",
                    "entry": "from sdk import IterunClient",
                },
                {
                    "id": "mcp",
                    "description": "Model Context Protocol tools for LLM agents",
                    "entry": "iterun-mcp",
                    "optional": "pip install -e '.[mcp]'",
                },
                {
                    "id": "pipeline",
                    "description": "Prompt → iterun.yaml → plan → execute → verify",
                    "entry": "generator.pipeline.run_pipeline",
                },
                {
                    "id": "markpact",
                    "description": "Pack workspace → stack.markpact.md",
                    "entry": "integrations.markpact_pack.pack_workspace",
                },
                {
                    "id": "pactown",
                    "description": "Universal runtime (ITERUN_RUNTIME=pactown)",
                    "entry": "executor.pactown.execute_pactown",
                },
            ],
            "rest_endpoints": [
                "GET /api/health",
                "GET /api/interfaces",
                "GET /api/schema",
                "POST /api/intents/validate-yaml",
                "POST /api/intents/parse",
                "POST /api/intents/generate",
                "POST /api/pipeline/run",
                "POST /api/intents/plan-yaml",
                "POST /api/intents/generate-and-run",
                "GET /api/intents",
                "GET /api/intents/{id}",
                "POST /api/intents/{id}/plan",
                "POST /api/intents/{id}/execute",
                "GET /api/containers/{id}/logs",
                "GET /api/registry",
                "POST /api/registry/refresh",
                "GET /api/registry/list",
            ],
            "mcp_tools": [
                "iterun_schema",
                "iterun_validate_intent",
                "iterun_generate_intent",
                "iterun_run_pipeline",
                "iterun_plan_yaml",
                "iterun_parse_yaml",
                "iterun_registry_refresh",
                "iterun_registry_list",
            ],
            "registry": {
                "manifest": "iterun.registry.json",
                "backstage": "catalog/catalog-info.yaml",
                "otel": "otel.resources.json",
                "standards": ["Backstage", "OCI labels", "OpenTelemetry resource"],
            },
        }

    def schema(self) -> dict[str, Any]:
        return get_json_schema()

    def validate_yaml(self, content: str) -> dict[str, Any]:
        doc, errors = validate_yaml_document(content)
        return {
            "valid": not errors,
            "errors": errors,
            "document": doc.model_dump() if doc else None,
            "is_stack": bool(doc and doc.STACK and doc.STACK.services),
        }

    def parse(self, content: str) -> IntentIR:
        return parse_dsl(content)

    def generate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        max_iterations: int | None = None,
    ) -> GenerateResult:
        gen = IntentGenerator(
            model=model or self.model,
            max_iterations=max_iterations or self.max_iterations,
        )
        return gen.generate(prompt)

    def run_pipeline(
        self,
        prompt: str,
        *,
        output_dir: str | Path | None = None,
        execute: bool = False,
        verify: bool = False,
        max_iterations: int | None = None,
        max_verify_iterations: int = 3,
        model: str | None = None,
    ) -> PipelineResult:
        result = run_generator_pipeline(
            prompt,
            output_dir=output_dir,
            execute=execute,
            verify=verify,
            max_iterations=max_iterations or self.max_iterations,
            max_verify_iterations=max_verify_iterations,
            model=model or self.model,
        )
        if result.workspace:
            try:
                from integrations.bridges.pipeline import refresh_registry_from_pipeline

                refresh_registry_from_pipeline(result.workspace, result)
            except Exception:
                pass
        return result

    def plan_ir(self, ir: IntentIR) -> DryRunResult:
        return plan_intent(ir)

    def plan_yaml(
        self,
        content: str,
        *,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        ir = parse_dsl(content)
        result = plan_intent(ir)
        written: dict[str, str] = {}
        if output_dir:
            written = _write_plan_output(ir, result, output_dir)
        payload = result.to_dict()
        payload["is_stack"] = bool(ir.stack and ir.stack.services)
        return {
            "success": result.success,
            "intent_id": ir.id,
            "intent": ir.to_dict(),
            "plan": payload,
            "artifacts": written,
        }

    def execute_ir(
        self,
        ir: IntentIR,
        *,
        workspace: str | Path | None = None,
        validate: bool = True,
        auto_fix: bool = True,
    ) -> dict[str, Any]:
        if not ir.iterun_approved:
            ir.approve_iterun()
        result = execute_intent(
            ir,
            str(workspace) if workspace else None,
            skip_iterun_check=True,
            validate=validate,
            auto_fix=auto_fix,
        )
        return result.to_dict()

    def registry_refresh(
        self,
        workspace: str | Path,
        *,
        include_docker: bool = True,
    ) -> dict[str, Any]:
        from integrations.bridges.pipeline import refresh_registry

        return refresh_registry(workspace, include_docker=include_docker)

    def registry_get(self, workspace: str | Path) -> dict[str, Any]:
        from registry.catalog import RegistryCatalog

        cat = RegistryCatalog(workspace)
        manifest = cat.load() or cat.discover()
        return manifest.to_dict()

    def registry_list(self, pattern: str = "examples/*/generated") -> list[dict[str, Any]]:
        from registry.catalog import discover_glob

        return discover_glob(pattern)
