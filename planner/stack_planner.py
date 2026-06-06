"""Plan multi-service STACK applications: N Dockerfiles + docker-compose.yaml."""

from __future__ import annotations

from typing import Any

import yaml

from ir.models import (
    Action,
    ActionType,
    Environment,
    Implementation,
    Intent,
    IntentIR,
    RuntimeType,
    StackService,
)
from planner.simulator import DryRunResult, Planner


def _service_ir(parent: IntentIR, svc: StackService) -> IntentIR:
    base_image = svc.base_image
    if not base_image and svc.language == "node":
        base_image = "node:20-slim"
    elif not base_image:
        base_image = "python:3.12-slim"

    return IntentIR(
        intent=Intent(name=svc.name, goal=parent.intent.goal),
        environment=Environment(
            runtime=RuntimeType.DOCKER,
            base_image=base_image,
            ports=[svc.port],
            env_vars=dict(svc.env_vars),
        ),
        implementation=Implementation(
            language=svc.language or "python",
            framework=svc.framework,
            actions=list(svc.actions),
        ),
        execution_mode=parent.execution_mode,
    )


def _gateway_proxy_code(svc: StackService, upstreams: dict[str, StackService]) -> str:
    """Generate FastAPI gateway that proxies api.expose routes to internal services."""
    imports = [
        "from fastapi import FastAPI, HTTPException",
        "import httpx",
        "import uvicorn",
    ]
    lines = imports + [
        "",
        f'app = FastAPI(title="{svc.name}")',
        "",
        f'UPSTREAM = "{svc.name}"',
        "",
    ]

    for action in svc.actions:
        if action.type != ActionType.API_EXPOSE:
            continue
        method = (action.method or "GET").lower()
        path = action.target or "/"
        func = path.strip("/").replace("/", "_").replace("{", "").replace("}", "") or "root"
        func = "".join(c if c.isalnum() or c == "_" else "_" for c in func)

        if path in ("/ping", "/health"):
            lines.extend([
                f'@app.{method}("{path}")',
                f"async def {func}():",
                f'    return {{"status": "ok", "endpoint": "{path}", "service": "{svc.name}"}}',
                "",
            ])
            continue

        upstream_url = _resolve_upstream(path, svc, upstreams)
        lines.extend([
            f'@app.{method}("{path}")',
            f"async def {func}():",
            f'    url = "{upstream_url}"',
            "    try:",
            "        async with httpx.AsyncClient(timeout=10.0) as client:",
            f"            resp = await client.{method}(url)",
            "            return resp.json() if resp.headers.get('content-type', '').startswith('application/json') else {'status': 'ok'}",
            "    except Exception as exc:",
            "        raise HTTPException(status_code=502, detail=str(exc))",
            "",
        ])

    lines.extend([
        'if __name__ == "__main__":',
        f"    uvicorn.run(app, host='0.0.0.0', port={svc.port})",
    ])
    return "\n".join(lines)


def _resolve_upstream(
    path: str,
    gateway: StackService,
    services: dict[str, StackService],
) -> str:
    """Map gateway route to internal service URL."""
    for name, svc in services.items():
        if name == gateway.name or svc.image:
            continue
        for action in svc.actions:
            if action.type == ActionType.API_EXPOSE and action.target == path:
                return f"http://{name}:{svc.port}{path}"
    for name, svc in services.items():
        if name == gateway.name or svc.image:
            continue
        for action in svc.actions:
            if action.type == ActionType.API_EXPOSE:
                return f"http://{name}:{svc.port}{action.target}"
    return f"http://127.0.0.1:{gateway.port}{path}"


def _build_compose(parent: IntentIR, artifacts: dict[str, dict[str, Any]]) -> str:
    network = parent.stack.network if parent.stack else "app-net"
    compose_services: dict[str, Any] = {}

    for svc in parent.stack.services:
        spec: dict[str, Any] = {
            "networks": [network],
        }
        if svc.depends_on:
            spec["depends_on"] = svc.depends_on

        if svc.image:
            spec["image"] = svc.image
            if svc.port:
                spec["expose"] = [str(svc.port)]
        else:
            spec["build"] = {
                "context": f"./services/{svc.name}",
                "dockerfile": "Dockerfile",
            }

        if svc.host_port:
            spec["ports"] = [f"{svc.host_port}:{svc.port}"]
        elif not svc.image:
            spec["expose"] = [str(svc.port)]

        if svc.env_vars:
            spec["environment"] = svc.env_vars

        from registry.labels import build_service_labels

        spec["labels"] = build_service_labels(
            parent.intent.name,
            svc.name,
            intent_id=parent.id,
            framework=svc.framework,
            language=svc.language,
        )

        compose_services[svc.name] = spec

    doc = {
        "services": compose_services,
        "networks": {network: {"driver": "bridge"}},
    }
    return yaml.dump(doc, default_flow_style=False, sort_keys=False)


def plan_stack(ir: IntentIR) -> DryRunResult:
    """Generate per-service Dockerfiles and docker-compose.yaml."""
    result = DryRunResult()
    if not ir.stack or len(ir.stack.services) < 2:
        result.success = False
        result.warnings.append("STACK requires at least 2 services")
        return result

    planner = Planner()
    svc_map = {s.name: s for s in ir.stack.services}
    service_artifacts: dict[str, dict[str, str]] = {}

    result.add_log(f"Planning STACK application: {ir.intent.name}")
    result.add_log(f"Services: {', '.join(svc_map)}")

    for svc in ir.stack.services:
        result.add_log(f"  → service: {svc.name}")

        if svc.image:
            result.add_log(f"    ✓ pre-built image: {svc.image}")
            service_artifacts[svc.name] = {"image": svc.image}
            continue

        child = _service_ir(ir, svc)
        child_result = planner.dry_run(child)

        code = child_result.generated_code
        use_proxy = svc.host_port and svc.framework == "fastapi" and len(svc_map) > 1
        if use_proxy:
            code = _gateway_proxy_code(svc, svc_map)

        dockerfile = child_result.dockerfile
        if use_proxy and dockerfile and "httpx" not in dockerfile:
            dockerfile = dockerfile.replace(
                "RUN pip install --no-cache-dir ",
                "RUN pip install --no-cache-dir httpx ",
            )
        if svc.language == "node" and dockerfile:
            dockerfile = dockerfile.replace(
                "RUN npm install",
                "RUN npm init -y && npm install express",
            )

        service_artifacts[svc.name] = {
            "code": code,
            "dockerfile": dockerfile,
            "language": svc.language or "python",
        }
        result.add_log(f"    ✓ generated {svc.language} artifacts")

    result.compose_yaml = _build_compose(ir, service_artifacts)
    result.service_artifacts = service_artifacts
    result.add_log("docker-compose.yaml generated")
    result.add_log("STACK plan completed")

    gateway = next((s for s in ir.stack.services if s.host_port), ir.stack.services[0])
    result.add_log(f"Public entrypoint: {gateway.name} → host_port {gateway.host_port or gateway.port}")

    return result
