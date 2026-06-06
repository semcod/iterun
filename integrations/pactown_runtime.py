"""Execute iterun intents via pactown (universal sandbox) instead of raw Docker."""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ir.models import ActionType, IntentIR

from executor.models import ExecutionResult, ValidationResult
from executor.validation import filter_validation_endpoints

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


def _collect_endpoints(ir: IntentIR, base_url: str, extra: dict[str, str] | None = None) -> list[str]:
    endpoints: list[str] = []
    if ir.stack and ir.stack.services:
        for svc in ir.stack.services:
            if not svc.host_port and not (extra and svc.name in extra):
                continue
            if extra and svc.name in extra:
                base = extra[svc.name]
            else:
                base = f"http://localhost:{svc.host_port}"
            if base not in endpoints:
                endpoints.append(base)
            for action in svc.actions:
                if action.type == ActionType.API_EXPOSE and action.target:
                    url = f"{base.rstrip('/')}{action.target}"
                    if url not in endpoints:
                        endpoints.append(url)
    else:
        endpoints.append(base_url)
        for action in ir.implementation.actions:
            if action.type == ActionType.API_EXPOSE and action.target:
                url = f"{base_url.rstrip('/')}{action.target}"
                if url not in endpoints:
                    endpoints.append(url)
    return endpoints


def _validate_urls(endpoints: list[str], result: ExecutionResult, timeout: int = 10) -> ValidationResult:
    validation = ValidationResult()
    if not HTTPX_AVAILABLE:
        validation.success = True
        return validation
    for endpoint in filter_validation_endpoints(endpoints):
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.get(endpoint)
                ok = resp.status_code < 400
                validation.add_check(endpoint, resp.status_code, ok, None if ok else f"HTTP {resp.status_code}")
                result.add_log(f"  {'✓' if ok else '✗'} {endpoint} → {resp.status_code}")
        except Exception as e:
            validation.add_check(endpoint, 0, False, str(e))
            result.add_log(f"  ✗ {endpoint} → {e}")
    validation.success = len(validation.failed_endpoints) == 0
    return validation


def stop_pactown_for_intent(intent_name: str, workspace: str | Path | None = None) -> int:
    """Stop pactown ecosystem for intent (before verify retry)."""
    try:
        from pactown.orchestrator import Orchestrator
    except ImportError:
        return 0
    ws = Path(workspace) if workspace else Path.cwd()
    config_path = ws / "pactown.yaml"
    if not config_path.is_file():
        return 0
    try:
        orch = Orchestrator.from_file(config_path, verbose=False, dynamic_ports=True)
        orch.stop_all()
        return len(orch.config.services)
    except Exception:
        return 0


def execute_pactown(
    ir: IntentIR,
    workspace: str | Path,
    *,
    validate: bool = True,
    startup_wait: int = 3,
) -> ExecutionResult:
    """Run via pactown Orchestrator (STACK) or ServiceRunner (single service)."""
    result = ExecutionResult()
    ws = Path(workspace).resolve()
    start = time.time()

    try:
        from integrations.markpact_pack import pack_workspace
        from integrations.pactown_config import write_pactown_config

        pack_workspace(ws, ir, pack_services=True)
        write_pactown_config(ir, ws)
    except Exception as e:
        result.error = f"pack/config failed: {e}"
        result.add_log(result.error)
        result.execution_time = time.time() - start
        return result

    result.add_log(f"Pactown runtime: {ir.intent.name}")
    result.add_log(f"Workspace: {ws}")
    result.artifacts["stack.markpact.md"] = str(ws / "stack.markpact.md")
    result.artifacts["pactown.yaml"] = str(ws / "pactown.yaml")

    is_stack = bool(ir.stack and len(ir.stack.services) >= 2)
    service_urls: dict[str, str] = {}

    try:
        if is_stack:
            from pactown.orchestrator import Orchestrator

            config_path = ws / "pactown.yaml"
            orch = Orchestrator.from_file(config_path, verbose=False, dynamic_ports=True)
            if not orch.validate():
                result.error = "Invalid pactown.yaml"
                result.execution_time = time.time() - start
                return result
            orch.start_all(wait_for_health=True, parallel=True)
            result.container_id = f"pactown-{ir.intent.name}"
            for name in orch.config.services:
                url = orch.service_registry.get_url(name)
                if url:
                    service_urls[name] = url
            result.add_log(f"Pactown stack started: {', '.join(service_urls)}")
        else:
            from pactown.service_runner import ServiceRunner

            readme = ws / "stack.markpact.md"
            if not readme.is_file():
                readme = ws / "README.md"
            content = readme.read_text(encoding="utf-8")
            runner = ServiceRunner(sandbox_root=ws / ".pactown-sandboxes")

            async def _run():
                port = ir.environment.ports[0] if ir.environment.ports else 8000
                return await runner.run_from_content(
                    service_id=ir.intent.name,
                    content=content,
                    port=port,
                )

            run_result = asyncio.run(_run())
            if not run_result.success:
                result.error = run_result.message or "pactown run failed"
                result.add_log(result.error)
                result.execution_time = time.time() - start
                return result
            result.container_id = f"pactown-{ir.intent.name}"
            service_urls[ir.intent.name] = f"http://localhost:{run_result.port}"
            result.add_log(f"Pactown service on port {run_result.port}")

        gateway = None
        if is_stack and ir.stack:
            gateway = next((s for s in ir.stack.services if s.host_port), ir.stack.services[0])
        base = service_urls.get(gateway.name if gateway else ir.intent.name, next(iter(service_urls.values()), ""))
        result.endpoints = _collect_endpoints(ir, base, service_urls if is_stack else None)

        if validate and result.endpoints:
            result.add_log(f"Waiting {startup_wait}s for pactown startup...")
            time.sleep(startup_wait)
            result.validation = _validate_urls(result.endpoints, result)
            if result.validation.success:
                result.success = True
                result.add_log("✓ Pactown endpoints validated")
            else:
                result.add_log("✗ Pactown validation failed (use --verify for LLM repair)")
        else:
            result.success = True

        (ws / "pactown.urls.json").write_text(
            __import__("json").dumps(service_urls, indent=2),
            encoding="utf-8",
        )
        result.artifacts["pactown.urls.json"] = str(ws / "pactown.urls.json")

    except ImportError as e:
        result.error = "pactown not installed: pip install pactown or pip install -e '.[runtime]'"
        result.add_log(str(e))
    except Exception as e:
        result.error = str(e)
        result.add_log(f"ERROR: {e}")

    result.execution_time = time.time() - start
    return result
