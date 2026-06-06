"""Build pactown.yaml from iterun STACK IR."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ir.models import ActionType, IntentIR


def _health_path(svc) -> str:
    for action in svc.actions:
        if action.type == ActionType.API_EXPOSE and action.target:
            if action.target in ("/health", "/ping", "/live", "/ready"):
                return action.target
    for action in svc.actions:
        if action.type == ActionType.API_EXPOSE and action.target:
            return action.target
    return "/health"


def build_pactown_config(ir: IntentIR, workspace: str | Path) -> dict[str, Any]:
    """Generate pactown ecosystem config for iterun STACK."""
    ws = Path(workspace)
    name = ir.intent.name
    services: dict[str, Any] = {}

    if not ir.stack or not ir.stack.services:

        class _Svc:
            actions = ir.implementation.actions

        readme = "stack.markpact.md" if (ws / "stack.markpact.md").is_file() else "README.md"
        port = ir.environment.ports[0] if ir.environment.ports else 8000
        services[name] = {
            "readme": readme,
            "port": port,
            "health_check": _health_path(_Svc()),
        }
    else:
        for svc in ir.stack.services:
            if svc.image:
                continue
            readme = f"services/{svc.name}/README.md"
            entry: dict[str, Any] = {
                "readme": readme,
                "port": svc.host_port or svc.port or 8000,
                "health_check": _health_path(svc),
            }
            if svc.depends_on:
                entry["depends_on"] = [{"name": d} for d in svc.depends_on]
            services[svc.name] = entry

    return {
        "name": name,
        "version": "0.1.0",
        "description": ir.intent.goal or f"ITERUN stack {name}",
        "sandbox_root": str(ws / ".pactown-sandboxes"),
        "services": services,
    }


def write_pactown_config(ir: IntentIR, workspace: str | Path) -> Path:
    ws = Path(workspace)
    config = build_pactown_config(ir, ws)
    path = ws / "pactown.yaml"
    path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False), encoding="utf-8")
    return path
