"""
End-to-end pipeline: prompt → LLM YAML → intract/testql contracts → plan → execute → verify.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from config import PACKAGE_FILENAME
from executor.runner import Executor, execute_intent
from generator.contract_verify import verify_contract
from generator.intract_manifest import write_intract_manifest
from generator.intent_generator import GenerateResult, IntentGenerator
from generator.session import write_session_artifacts
from generator.testql_scenario import write_testql_scenario
from ir.models import IntentIR
from planner.simulator import plan_intent


@dataclass
class PipelineResult:
    success: bool
    prompt: str
    generate: GenerateResult | None = None
    plan: dict[str, Any] | None = None
    execution: dict[str, Any] | None = None
    verification: dict[str, Any] | None = None
    verify_iterations: int = 0
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
            "verification": self.verification,
            "verify_iterations": self.verify_iterations,
            "yaml_path": self.yaml_path,
            "workspace": self.workspace,
            "error": self.error,
        }


def _write_plan_artifacts(
    workspace: Path,
    ir: IntentIR,
    plan_result,
    *,
    prompt: str,
    yaml_path: Path,
) -> None:
    plan_payload = {"intent": ir.to_dict(), "plan": plan_result.to_dict()}
    (workspace / "plan.result.json").write_text(
        json.dumps(plan_payload, indent=2),
        encoding="utf-8",
    )
    write_intract_manifest(yaml_path, workspace / "intract.yaml", prompt=prompt)
    write_testql_scenario(yaml_path, workspace / "service.testql.toon.yaml")
    if plan_result.generated_code:
        lang = ir.implementation.language
        app_name = "app.py" if lang == "python" else "app.js"
        (workspace / app_name).write_text(plan_result.generated_code, encoding="utf-8")
    if plan_result.dockerfile:
        (workspace / "Dockerfile").write_text(plan_result.dockerfile, encoding="utf-8")


def _container_logs(workspace: Path | None, container_id: str | None) -> str | None:
    if not workspace or not container_id:
        return None
    try:
        return Executor(str(workspace)).get_container_logs(container_id, tail=200)
    except Exception:
        return None


def _finalize(
    out: PipelineResult,
    workspace: Path | None,
    *,
    container_id: str | None = None,
) -> PipelineResult:
    if workspace:
        logs = _container_logs(workspace, container_id)
        write_session_artifacts(workspace, out, container_logs=logs)
        out.workspace = str(workspace)
    return out


def run_pipeline(
    prompt: str,
    *,
    output_dir: str | Path | None = None,
    yaml_filename: str | None = None,
    execute: bool = False,
    verify: bool = False,
    max_iterations: int = 5,
    max_verify_iterations: int = 3,
    model: str | None = None,
) -> PipelineResult:
    out = PipelineResult(success=False, prompt=prompt)
    workspace = Path(output_dir) if output_dir else None
    package_name = yaml_filename or PACKAGE_FILENAME
    if workspace:
        workspace.mkdir(parents=True, exist_ok=True)

    generator = IntentGenerator(max_iterations=max_iterations, model=model)
    contract_feedback: list[str] = []
    verify_rounds = max_verify_iterations if (verify and execute) else 1
    last_container_id: str | None = None
    verify_rounds_log: list[dict[str, Any]] = []

    for verify_round in range(1, verify_rounds + 1):
        out.verify_iterations = verify_round
        effective_prompt = prompt
        if contract_feedback:
            effective_prompt = (
                f"{prompt}\n\n"
                "Contract verification failed after deploy. "
                "Regenerate intent so all endpoints work and match the prompt.\n"
                "Failures:\n" + "\n".join(f"- {e}" for e in contract_feedback[-20:])
            )

        gen_result = generator.generate(effective_prompt)
        out.generate = gen_result

        if not gen_result.success or not gen_result.yaml_content or not gen_result.ir:
            out.error = gen_result.error or "Generation failed"
            return _finalize(out, workspace)

        ir = gen_result.ir
        yaml_path: Path | None = None
        if workspace:
            yaml_path = workspace / package_name
            yaml_path.write_text(gen_result.yaml_content, encoding="utf-8")
            out.yaml_path = str(yaml_path)

        plan_result = plan_intent(ir)
        out.plan = plan_result.to_dict()

        if workspace and yaml_path:
            _write_plan_artifacts(workspace, ir, plan_result, prompt=prompt, yaml_path=yaml_path)

        if not execute:
            out.success = True
            return _finalize(out, workspace)

        ir.approve_iterun()
        exec_result = execute_intent(
            ir,
            str(workspace) if workspace else None,
            skip_iterun_check=True,
        )
        out.execution = exec_result.to_dict()
        last_container_id = exec_result.container_id

        if exec_result.error:
            contract_feedback.append(f"Execute error: {exec_result.error}")
            verify_rounds_log.append({
                "round": verify_round,
                "phase": "execute",
                "success": False,
                "errors": [exec_result.error],
            })
            if workspace:
                (workspace / "verify.rounds.json").write_text(
                    json.dumps(verify_rounds_log, indent=2), encoding="utf-8"
                )
            if verify_round >= verify_rounds:
                out.error = exec_result.error
                return _finalize(out, workspace, container_id=last_container_id)
            continue

        if not verify:
            out.success = exec_result.success
            if not exec_result.success:
                out.error = exec_result.error
            return _finalize(out, workspace, container_id=last_container_id)

        if not workspace or not yaml_path:
            out.error = "verify requires output_dir"
            return _finalize(out, workspace, container_id=last_container_id)

        vr = verify_contract(
            workspace,
            yaml_path,
            prompt=prompt,
            execution_endpoints=exec_result.endpoints,
        )
        out.verification = vr.to_dict()
        verify_rounds_log.append({
            "round": verify_round,
            "phase": "verify",
            "success": vr.success,
            "errors": vr.errors,
            "service_url": vr.service_url,
            "testql_passed": vr.testql_passed,
        })
        if workspace:
            (workspace / "verify.rounds.json").write_text(
                json.dumps(verify_rounds_log, indent=2), encoding="utf-8"
            )

        if vr.success:
            out.success = True
            return _finalize(out, workspace, container_id=last_container_id)

        contract_feedback.extend(vr.errors)
        if verify_round >= verify_rounds:
            out.error = "; ".join(vr.errors[:5]) or "Contract verification failed"
            return _finalize(out, workspace, container_id=last_container_id)

    out.error = out.error or "Pipeline ended without success"
    return _finalize(out, workspace, container_id=last_container_id)
