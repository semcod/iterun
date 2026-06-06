"""Execute iterun intents via pactown (universal sandbox) instead of raw Docker."""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

from ir.models import ActionType, IntentIR

from executor.models import ExecutionResult, ValidationResult
from executor.validation import filter_validation_endpoints

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


def _append_action_urls(endpoints: list[str], base: str, actions) -> None:
    for action in actions:
        if action.type != ActionType.API_EXPOSE or not action.target:
            continue
        url = f"{base.rstrip('/')}{action.target}"
        if url not in endpoints:
            endpoints.append(url)


def _collect_stack_endpoints(ir: IntentIR, extra: dict[str, str] | None) -> list[str]:
    endpoints: list[str] = []
    for svc in ir.stack.services:
        if not svc.host_port and not (extra and svc.name in extra):
            continue
        base = extra[svc.name] if extra and svc.name in extra else f"http://localhost:{svc.host_port}"
        if base not in endpoints:
            endpoints.append(base)
        _append_action_urls(endpoints, base, svc.actions)
    return endpoints


def _collect_single_endpoints(ir: IntentIR, base_url: str) -> list[str]:
    endpoints = [base_url]
    _append_action_urls(endpoints, base_url, ir.implementation.actions)
    return endpoints


def _collect_endpoints(ir: IntentIR, base_url: str, extra: dict[str, str] | None = None) -> list[str]:
    if ir.stack and ir.stack.services:
        return _collect_stack_endpoints(ir, extra)
    return _collect_single_endpoints(ir, base_url)


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


def _prepare_pactown_workspace(ir: IntentIR, ws: Path, result: ExecutionResult) -> bool:
    try:
        from integrations.markpact_pack import pack_workspace
        from integrations.pactown_config import write_pactown_config

        pack_workspace(ws, ir, pack_services=True)
        write_pactown_config(ir, ws)
    except Exception as e:
        result.error = f"pack/config failed: {e}"
        result.add_log(result.error)
        return False
    result.add_log(f"Pactown runtime: {ir.intent.name}")
    result.add_log(f"Workspace: {ws}")
    result.artifacts["stack.markpact.md"] = str(ws / "stack.markpact.md")
    result.artifacts["pactown.yaml"] = str(ws / "pactown.yaml")
    return True


def _start_pactown_stack(ws: Path, ir: IntentIR, result: ExecutionResult) -> dict[str, str]:
    from pactown.orchestrator import Orchestrator

    orch = Orchestrator.from_file(ws / "pactown.yaml", verbose=False, dynamic_ports=True)
    if not orch.validate():
        result.error = "Invalid pactown.yaml"
        return {}
    orch.start_all(wait_for_health=True, parallel=True)
    result.container_id = f"pactown-{ir.intent.name}"
    urls = {
        name: url
        for name in orch.config.services
        if (url := orch.service_registry.get_url(name))
    }
    result.add_log(f"Pactown stack started: {', '.join(urls)}")
    return urls


def _start_pactown_single(ws: Path, ir: IntentIR, result: ExecutionResult) -> dict[str, str]:
    from pactown.service_runner import ServiceRunner

    readme = ws / "stack.markpact.md"
    if not readme.is_file():
        readme = ws / "README.md"
    runner = ServiceRunner(sandbox_root=ws / ".pactown-sandboxes")
    port = ir.environment.ports[0] if ir.environment.ports else 8000

    async def _run():
        return await runner.run_from_content(
            service_id=ir.intent.name,
            content=readme.read_text(encoding="utf-8"),
            port=port,
        )

    run_result = asyncio.run(_run())
    if not run_result.success:
        result.error = run_result.message or "pactown run failed"
        result.add_log(result.error)
        return {}
    result.container_id = f"pactown-{ir.intent.name}"
    result.add_log(f"Pactown service on port {run_result.port}")
    return {ir.intent.name: f"http://localhost:{run_result.port}"}


def _finalize_pactown(
    ir: IntentIR,
    ws: Path,
    result: ExecutionResult,
    service_urls: dict[str, str],
    *,
    is_stack: bool,
    validate: bool,
    startup_wait: int,
) -> None:
    gateway = None
    if is_stack and ir.stack:
        gateway = next((s for s in ir.stack.services if s.host_port), ir.stack.services[0])
    base = service_urls.get(
        gateway.name if gateway else ir.intent.name,
        next(iter(service_urls.values()), ""),
    )
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
    if not _prepare_pactown_workspace(ir, ws, result):
        result.execution_time = time.time() - start
        return result

    is_stack = bool(ir.stack and len(ir.stack.services) >= 2)
    try:
        service_urls = (
            _start_pactown_stack(ws, ir, result)
            if is_stack
            else _start_pactown_single(ws, ir, result)
        )
        if result.error or not service_urls:
            result.execution_time = time.time() - start
            return result
        _finalize_pactown(
            ir, ws, result, service_urls, is_stack=is_stack, validate=validate, startup_wait=startup_wait
        )
    except ImportError as e:
        result.error = "pactown not installed: pip install pactown or pip install -e '.[runtime]'"
        result.add_log(str(e))
    except Exception as e:
        result.error = str(e)
        result.add_log(f"ERROR: {e}")

    result.execution_time = time.time() - start
    return result
