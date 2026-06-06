"""
End-to-end pipeline: prompt → LLM YAML → intract/testql contracts → plan → execute → verify.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from config import PACKAGE_FILENAME
from executor.docker_ops import get_container_logs
from executor.runner import execute_intent
from integrations.runtime_stop import stop_runtime_for_intent
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
    if ir.stack and ir.stack.services:
        from planner.stack_artifacts import write_stack_artifacts
        write_stack_artifacts(workspace, ir, plan_result)
    else:
        plan_payload = {"intent": ir.to_dict(), "plan": plan_result.to_dict()}
        (workspace / "plan.result.json").write_text(
            json.dumps(plan_payload, indent=2),
            encoding="utf-8",
        )
        if plan_result.generated_code:
            lang = ir.implementation.language
            app_name = "app.py" if lang == "python" else "app.js"
            (workspace / app_name).write_text(plan_result.generated_code, encoding="utf-8")
        if plan_result.dockerfile:
            (workspace / "Dockerfile").write_text(plan_result.dockerfile, encoding="utf-8")

    write_intract_manifest(yaml_path, workspace / "intract.yaml", prompt=prompt)
    write_testql_scenario(yaml_path, workspace / "service.testql.toon.yaml")
    try:
        from integrations.markpact_pack import pack_workspace

        pack_workspace(workspace, ir, pack_services=bool(ir.stack and ir.stack.services))
    except Exception:
        pass


def _expectations_summary(workspace: Path) -> str | None:
    import yaml

    exp_file = workspace / "expectations.yaml"
    if not exp_file.is_file():
        return None
    data = yaml.safe_load(exp_file.read_text(encoding="utf-8")) or {}
    lines: list[str] = []
    if data.get("name"):
        lines.append(f"intent name must be: {data['name']}")
    if data.get("framework"):
        lines.append(f"framework must be: {data['framework']}")
    for ep in data.get("endpoints", []) or []:
        method = ep.get("method", "GET").upper()
        path = ep.get("path", "/")
        lines.append(f"required endpoint: {method} {path}")
    return "\n".join(lines) if lines else None


def _build_repair_prompt(prompt: str, errors: list[str], workspace: Path | None) -> str:
    parts = [
        prompt,
        "",
        "Contract verification failed after deploy. Regenerate iterun.yaml so all endpoints work.",
        "Failures:",
        *[f"- {e}" for e in errors[-20:]],
    ]
    if workspace:
        summary = _expectations_summary(workspace)
        if summary:
            parts.extend(["", "Contract expectations (must satisfy):", summary])
    return "\n".join(parts)


def _container_logs(workspace: Path | None, container_id: str | None) -> str | None:
    if not workspace or not container_id:
        return None
    try:
        return get_container_logs(workspace, container_id, tail=200)
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
        try:
            from integrations.bridges.pipeline import refresh_registry_from_pipeline

            refresh_registry_from_pipeline(workspace, out)
        except Exception:
            pass
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
        effective_prompt = (
            _build_repair_prompt(prompt, contract_feedback, workspace)
            if contract_feedback
            else prompt
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

        if verify_round > 1:
            stop_runtime_for_intent(ir.intent.name, workspace)

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
            validation = exec_result.validation
            if validation and not validation.success:
                out.success = False
                out.error = "; ".join(validation.errors[:5]) or "Endpoint validation failed"
            else:
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
