"""
ITERUN Python SDK — local in-process or remote REST client.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from dsl.schema import get_json_schema, validate_yaml_document
from generator.intent_generator import GenerateResult, IntentGenerator
from generator.pipeline import PipelineResult, run_pipeline
from interfaces.service import IterunService
from parser.dsl_parser import parse_dsl


class IterunClient:
    """Local SDK (in-process) or remote via REST base_url."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        max_iterations: int = 5,
        timeout: float = 300.0,
    ):
        self.base_url = base_url.rstrip("/") if base_url else None
        self.model = model
        self.max_iterations = max_iterations
        self.timeout = timeout
        self._service = IterunService(model=model, max_iterations=max_iterations)

    def health(self) -> dict[str, Any]:
        if self.base_url:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                r = client.get("/api/health")
                r.raise_for_status()
                return r.json()
        return {"status": "ok", "service": "iterun", "mode": "local"}

    def interfaces(self) -> dict[str, Any]:
        if self.base_url:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                r = client.get("/api/interfaces")
                r.raise_for_status()
                return r.json()
        return self._service.interfaces_info()

    def schema(self) -> dict[str, Any]:
        if self.base_url:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                r = client.get("/api/schema")
                r.raise_for_status()
                return r.json()
        return get_json_schema()

    def validate(self, yaml_content: str) -> dict[str, Any]:
        if self.base_url:
            return self._post_json("/api/intents/validate-yaml", {"content": yaml_content})
        doc, errors = validate_yaml_document(yaml_content)
        return {
            "valid": not errors,
            "errors": errors,
            "document": doc.model_dump() if doc else None,
            "is_stack": bool(doc and doc.STACK and doc.STACK.services),
        }

    def generate(self, prompt: str, *, model: str | None = None) -> GenerateResult:
        if self.base_url:
            return self._remote_generate(prompt, model=model)
        return self._service.generate(prompt, model=model)

    def run_pipeline(
        self,
        prompt: str,
        *,
        output_dir: str | Path | None = None,
        execute: bool = False,
        verify: bool = False,
        max_verify_iterations: int = 3,
        model: str | None = None,
    ) -> PipelineResult:
        if self.base_url:
            return self._remote_pipeline(
                prompt,
                output_dir,
                execute,
                verify,
                max_verify_iterations,
                model,
            )
        return self._service.run_pipeline(
            prompt,
            output_dir=output_dir,
            execute=execute,
            verify=verify,
            max_verify_iterations=max_verify_iterations,
            model=model,
        )

    def generate_and_run(
        self,
        prompt: str,
        *,
        output_dir: str | Path | None = None,
        execute: bool = False,
        verify: bool = False,
        model: str | None = None,
    ) -> PipelineResult:
        """Alias for run_pipeline (backward compatible)."""
        return self.run_pipeline(
            prompt,
            output_dir=output_dir,
            execute=execute,
            verify=verify,
            model=model,
        )

    def plan_yaml(
        self,
        yaml_content: str,
        *,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        if self.base_url:
            return self._post_json(
                "/api/intents/plan-yaml",
                {
                    "content": yaml_content,
                    "output_dir": str(output_dir) if output_dir else None,
                },
            )
        return self._service.plan_yaml(yaml_content, output_dir=output_dir)

    def registry_get(self, workspace: str | Path = "generated") -> dict[str, Any]:
        if self.base_url:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                r = client.get("/api/registry", params={"workspace": str(workspace)})
                r.raise_for_status()
                return r.json()
        return self._service.registry_get(workspace)

    def registry_refresh(
        self,
        workspace: str | Path = "generated",
        *,
        include_docker: bool = True,
    ) -> dict[str, Any]:
        if self.base_url:
            return self._post_json(
                "/api/registry/refresh",
                {"workspace": str(workspace), "include_docker": include_docker},
            )
        return self._service.registry_refresh(workspace, include_docker=include_docker)

    def registry_list(self, pattern: str = "examples/*/generated") -> list[dict[str, Any]]:
        if self.base_url:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                r = client.get("/api/registry/list", params={"pattern": pattern})
                r.raise_for_status()
                return r.json().get("registries", [])
        return self._service.registry_list(pattern)

    def parse(self, yaml_content: str):
        if self.base_url:
            data = self._post_json("/api/intents/parse", {"content": yaml_content})
            if not data.get("success"):
                raise ValueError(data.get("detail", "parse failed"))
            return parse_dsl(yaml_content)
        return parse_dsl(yaml_content)

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            r = client.post(path, json=payload)
            r.raise_for_status()
            return r.json()

    def _remote_generate(self, prompt: str, *, model: str | None = None) -> GenerateResult:
        data = self._post_json(
            "/api/intents/generate",
            {
                "prompt": prompt,
                "model": model or self.model,
                "max_iterations": self.max_iterations,
            },
        )
        return GenerateResult(
            success=data["success"],
            prompt=prompt,
            yaml_content=data.get("yaml_content"),
            iterations=data.get("iterations", 0),
            model=data.get("model"),
            error=data.get("error"),
        )

    def _remote_pipeline(
        self,
        prompt: str,
        output_dir: str | Path | None,
        execute: bool,
        verify: bool,
        max_verify_iterations: int,
        model: str | None,
    ) -> PipelineResult:
        data = self._post_json(
            "/api/pipeline/run",
            {
                "prompt": prompt,
                "output_dir": str(output_dir) if output_dir else None,
                "execute": execute,
                "verify": verify,
                "max_verify_iterations": max_verify_iterations,
                "model": model or self.model,
                "max_iterations": self.max_iterations,
            },
        )
        return PipelineResult(
            success=data["success"],
            prompt=prompt,
            yaml_path=data.get("yaml_path"),
            workspace=data.get("workspace"),
            error=data.get("error"),
        )
