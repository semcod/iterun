"""Docker and docker-compose runtime operations."""

from __future__ import annotations

import shutil
import socket
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from config import get_config
from ir.models import ActionType

if TYPE_CHECKING:
    from ir.models import IntentIR

    from executor.models import ExecutionResult


def find_available_port(start_port: int = 8000) -> int:
    """Find an available port starting from start_port."""
    port = start_port
    max_attempts = 100

    for _ in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
                return port
        except OSError:
            port += 1

    return start_port + max_attempts


def stop_containers_for_intent(intent_name: str, prefix: str | None = None) -> int:
    """Stop all Docker containers whose name matches intent-{name}-*."""
    if not shutil.which("docker"):
        return 0
    cfg = get_config()
    name_prefix = prefix or cfg.container_prefix
    pattern = f"{name_prefix}-{intent_name}"
    proc = subprocess.run(
        ["docker", "ps", "-aq", "--filter", f"name={pattern}"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    stopped = 0
    for cid in proc.stdout.splitlines():
        cid = cid.strip()
        if not cid:
            continue
        subprocess.run(["docker", "rm", "-f", cid], capture_output=True, timeout=30)
        stopped += 1
    return stopped


def get_container_logs(workspace: Path, container_id: str, tail: int = 50) -> str:
    """Get logs from a container or docker compose project (STACK)."""
    compose_file = workspace / "docker-compose.yaml"
    is_compose_project = (
        compose_file.is_file()
        and container_id
        and (
            len(container_id) != 12
            or not all(c in "0123456789abcdef" for c in container_id.lower())
        )
    )
    try:
        if is_compose_project:
            result = subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(compose_file),
                    "-p",
                    container_id,
                    "logs",
                    "--tail",
                    str(tail),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
        else:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(tail), container_id],
                capture_output=True,
                text=True,
                timeout=30,
            )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error getting logs: {e}"


def patch_compose_host_ports(
    ir: IntentIR,
    compose_file: Path,
    result: ExecutionResult,
) -> None:
    """Rewrite compose port mappings when host_port is already taken."""
    data = yaml.safe_load(compose_file.read_text(encoding="utf-8")) or {}
    services = data.get("services") or {}
    for svc in ir.stack.services:
        if not svc.host_port or svc.name not in services:
            continue
        host_port = find_available_port(svc.host_port)
        if host_port != svc.host_port:
            result.add_log(
                f"Port {svc.host_port} in use — publishing {svc.name} on {host_port}"
            )
        services[svc.name]["ports"] = [f"{host_port}:{svc.port}"]
        svc.host_port = host_port
    compose_file.write_text(
        yaml.dump(data, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def execute_compose_stack(
    ir: IntentIR,
    workspace: Path,
    result: ExecutionResult,
    *,
    container_prefix: str,
) -> None:
    """Build and run multi-service STACK via docker compose."""
    compose_file = workspace / "docker-compose.yaml"
    project = f"{container_prefix}-{ir.intent.name}"

    result.add_log(f"STACK compose project: {project}")

    subprocess.run(
        ["docker", "compose", "-f", str(compose_file), "-p", project, "down"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    patch_compose_host_ports(ir, compose_file, result)

    proc = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            str(compose_file),
            "-p",
            project,
            "up",
            "-d",
            "--build",
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if proc.returncode != 0:
        result.error = f"docker compose up failed: {proc.stderr[-800:]}"
        result.add_log(result.error)
        return

    result.add_log("docker compose stack started")
    result.container_id = project

    for svc in ir.stack.services:
        if not svc.host_port:
            continue
        base = f"http://localhost:{svc.host_port}"
        if base not in result.endpoints:
            result.endpoints.append(base)
        for action in svc.actions:
            if action.type == ActionType.API_EXPOSE and action.target:
                url = f"{base.rstrip('/')}{action.target}"
                if url not in result.endpoints:
                    result.endpoints.append(url)


def execute_docker(
    ir: IntentIR,
    workspace: Path,
    result: ExecutionResult,
    *,
    container_prefix: str,
    container_port: int,
) -> None:
    """Build and run Docker container."""
    from registry.labels import build_service_labels

    image_name = f"{container_prefix}-{ir.intent.name}:latest"
    container_name = f"{container_prefix}-{ir.intent.name}-{ir.id}"

    requested_port = container_port
    if ir.environment.ports:
        requested_port = ir.environment.ports[0]

    host_port = find_available_port(requested_port)
    if host_port != requested_port:
        result.add_log(f"Port {requested_port} in use, using {host_port}")

    result.add_log(f"Building Docker image: {image_name}")

    build_result = subprocess.run(
        ["docker", "build", "-t", image_name, str(workspace)],
        capture_output=True,
        text=True,
        timeout=300,
    )

    if build_result.returncode != 0:
        result.error = f"Docker build failed: {build_result.stderr}"
        result.add_log(f"Build error: {build_result.stderr[:500]}")
        return

    result.add_log("Docker image built successfully")

    subprocess.run(
        ["docker", "rm", "-f", container_name],
        capture_output=True,
        timeout=30,
    )

    run_cmd = [
        "docker",
        "run",
        "-d",
        "--name",
        container_name,
        "-p",
        f"{host_port}:{container_port}",
    ]
    for key, value in build_service_labels(
        ir.intent.name,
        ir.intent.name,
        intent_id=ir.id,
        framework=ir.implementation.framework,
        language=ir.implementation.language,
    ).items():
        run_cmd.extend(["--label", f"{key}={value}"])

    for key, value in ir.environment.env_vars.items():
        run_cmd.extend(["-e", f"{key}={value}"])

    for port in ir.environment.ports:
        if port != container_port:
            extra_host_port = find_available_port(port)
            run_cmd.extend(["-p", f"{extra_host_port}:{port}"])

    run_cmd.append(image_name)

    result.add_log(f"Starting container: {container_name}")

    run_result = subprocess.run(
        run_cmd,
        capture_output=True,
        text=True,
        timeout=60,
    )

    if run_result.returncode != 0:
        result.error = f"Docker run failed: {run_result.stderr}"
        result.add_log(f"Run error: {run_result.stderr[:500]}")
        return

    result.container_id = run_result.stdout.strip()[:12]
    result.add_log(f"Container started: {result.container_id}")

    base_url = f"http://localhost:{host_port}"
    result.endpoints = [base_url]

    seen_paths: set[str] = set()
    for action in ir.implementation.actions:
        if action.type.value == "api.expose" and action.target:
            path = action.target
            if path not in seen_paths:
                seen_paths.add(path)
                result.endpoints.append(f"{base_url}{path}")
