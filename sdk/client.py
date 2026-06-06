"""
ITERUN Python SDK — generate, validate, plan, execute intents.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from dsl.schema import get_json_schema, validate_yaml_document
from generator.intent_generator import GenerateResult, IntentGenerator
from generator.pipeline import PipelineResult, run_pipeline
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
        self._generator = IntentGenerator(model=model, max_iterations=max_iterations)

    def schema(self) -> dict[str, Any]:
        return get_json_schema()

    def validate(self, yaml_content: str) -> dict[str, Any]:
        doc, errors = validate_yaml_document(yaml_content)
        return {
            "valid": not errors,
            "errors": errors,
            "document": doc.model_dump() if doc else None,
        }

    def generate(self, prompt: str, *, model: str | None = None) -> GenerateResult:
        if self.base_url:
            return self._remote_generate(prompt, model=model)
        gen = IntentGenerator(model=model or self.model, max_iterations=self.max_iterations)
        return gen.generate(prompt)

    def generate_and_run(
        self,
        prompt: str,
        *,
        output_dir: str | Path | None = None,
        execute: bool = False,
        model: str | None = None,
    ) -> PipelineResult:
        if self.base_url:
            return self._remote_pipeline(prompt, output_dir, execute, model)
        return run_pipeline(
            prompt,
            output_dir=output_dir,
            execute=execute,
            max_iterations=self.max_iterations,
            model=model or self.model,
        )

    def parse(self, yaml_content: str):
        return parse_dsl(yaml_content)

    def _remote_generate(self, prompt: str, *, model: str | None = None) -> GenerateResult:
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            r = client.post(
                "/api/intents/generate",
                json={
                    "prompt": prompt,
                    "model": model or self.model,
                    "max_iterations": self.max_iterations,
                },
            )
            r.raise_for_status()
            data = r.json()
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
        model: str | None,
    ) -> PipelineResult:
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            r = client.post(
                "/api/intents/generate-and-run",
                json={
                    "prompt": prompt,
                    "output_dir": str(output_dir) if output_dir else None,
                    "execute": execute,
                    "model": model or self.model,
                    "max_iterations": self.max_iterations,
                },
            )
            r.raise_for_status()
            data = r.json()
        return PipelineResult(
            success=data["success"],
            prompt=prompt,
            yaml_path=data.get("yaml_path"),
            workspace=data.get("workspace"),
            error=data.get("error"),
        )
