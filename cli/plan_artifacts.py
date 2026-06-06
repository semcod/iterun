"""Write plan output artifacts to a workspace directory."""

from __future__ import annotations

import json
from pathlib import Path

from ir.models import IntentIR
from planner.simulator import DryRunResult


def write_plan_artifacts(
    ir: IntentIR, result: DryRunResult, output_dir: str | Path
) -> dict[str, str]:
    """Write plan output (JSON, app code, Dockerfile) into output_dir."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if ir.stack and ir.stack.services:
        from planner.stack_artifacts import write_stack_artifacts

        return write_stack_artifacts(out, ir, result)

    written: dict[str, str] = {}
    plan_payload = {"intent": ir.to_dict(), "plan": result.to_dict()}
    plan_file = out / "plan.result.json"
    plan_file.write_text(json.dumps(plan_payload, indent=2), encoding="utf-8")
    written["plan.result.json"] = str(plan_file)

    if result.generated_code:
        lang = ir.implementation.language
        app_name = "app.py" if lang == "python" else "app.js" if lang == "node" else "app.txt"
        app_file = out / app_name
        app_file.write_text(result.generated_code, encoding="utf-8")
        written[app_name] = str(app_file)

    if result.dockerfile:
        dockerfile = out / "Dockerfile"
        dockerfile.write_text(result.dockerfile, encoding="utf-8")
        written["Dockerfile"] = str(dockerfile)

    return written
