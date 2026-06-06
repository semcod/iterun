"""
End-to-end pipeline: prompt → LLM YAML → validate → plan → execute.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from executor.runner import execute_intent
from generator.intent_generator import GenerateResult, IntentGenerator
from ir.models import IntentIR
from planner.simulator import plan_intent


@dataclass
class PipelineResult:
    success: bool
    prompt: str
    generate: GenerateResult | None = None
    plan: dict[str, Any] | None = None
    execution: dict[str, Any] | None = None
    yaml_path: str | None = None
    workspace: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "prompt": self.prompt,
            "generate": self.generate.to_dict() if self.generate else None,
            "plan": self.plan,
            "execution": self.execution,
            "yaml_path": self.yaml_path,
            "workspace": self.workspace,
            "error": self.error,
        }


def run_pipeline(
    prompt: str,
    *,
    output_dir: str | Path | None = None,
    yaml_filename: str = "intent.yaml",
    execute: bool = False,
    max_iterations: int = 5,
    model: str | None = None,
) -> PipelineResult:
    out = PipelineResult(success=False, prompt=prompt)
    workspace = Path(output_dir) if output_dir else None
    if workspace:
        workspace.mkdir(parents=True, exist_ok=True)

    generator = IntentGenerator(max_iterations=max_iterations, model=model)
    gen_result = generator.generate(prompt)
    out.generate = gen_result

    if not gen_result.success or not gen_result.yaml_content or not gen_result.ir:
        out.error = gen_result.error or "Generation failed"
        return out

    ir = gen_result.ir
    if workspace:
        yaml_path = workspace / yaml_filename
        yaml_path.write_text(gen_result.yaml_content, encoding="utf-8")
        out.yaml_path = str(yaml_path)

    plan_result = plan_intent(ir)
    out.plan = plan_result.to_dict()

    if workspace and plan_result.generated_code:
        lang = ir.implementation.language
        app_name = "app.py" if lang == "python" else "app.js"
        (workspace / app_name).write_text(plan_result.generated_code, encoding="utf-8")
        if plan_result.dockerfile:
            (workspace / "Dockerfile").write_text(plan_result.dockerfile, encoding="utf-8")

    if execute:
        ir.approve_amen()
        exec_result = execute_intent(
            ir,
            str(workspace) if workspace else None,
            skip_amen_check=True,
        )
        out.execution = exec_result.to_dict()
        out.workspace = str(workspace) if workspace else None
        out.success = exec_result.success
        if not exec_result.success:
            out.error = exec_result.error
        return out

    out.success = True
    out.workspace = str(workspace) if workspace else None
    return out
