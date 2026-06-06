"""Discover artifacts and services from an iterun workspace."""

from __future__ import annotations

from pathlib import Path

from registry.discover_artifacts import discover_artifacts
from registry.discover_io import intent_from_workspace, load_session, load_stack_urls, phase_from_session
from registry.discover_services import build_single_service, build_stack_services
from registry.models import DeploymentKind, RegistryManifest, RegistryMetadata, RegistryStatus


def discover_workspace(workspace: str | Path) -> RegistryManifest:
    """Build registry manifest by scanning workspace artifacts."""
    ws = Path(workspace).resolve()
    session = load_session(ws)
    intent_doc = intent_from_workspace(ws) or {}
    intent_section = intent_doc.get("INTENT") or intent_doc.get("intent") or {}
    intent_name = intent_section.get("name") or ws.name
    intent_id = intent_section.get("id") or (session or {}).get("generate", {}).get("ir", {}).get("id")

    stack_section = intent_doc.get("STACK") or {}
    stack_services = (stack_section.get("services") or {}) if isinstance(stack_section, dict) else {}
    is_stack = bool(stack_services) or (ws / "docker-compose.yaml").is_file()
    deployment = DeploymentKind.STACK if is_stack else DeploymentKind.SINGLE

    stack_urls = load_stack_urls(ws)
    execution = (session or {}).get("execution") or {}
    endpoints: list[str] = list(execution.get("endpoints") or [])
    container_id = execution.get("container_id")

    if is_stack and stack_services:
        services = build_stack_services(
            intent_name=intent_name,
            intent_id=intent_id,
            stack_services=stack_services,
            stack_urls=stack_urls,
            container_id=container_id,
            workspace=ws,
        )
    else:
        services = build_single_service(
            intent_name=intent_name,
            intent_id=intent_id,
            intent_doc=intent_doc,
            endpoints=endpoints,
            container_id=container_id,
            workspace=ws,
        )

    artifacts = discover_artifacts(ws)
    phase = phase_from_session(session)

    prompt_path = ws / "prompt.txt"
    prompt = (session or {}).get("prompt") or (
        prompt_path.read_text(encoding="utf-8") if prompt_path.is_file() else None
    )

    return RegistryManifest(
        metadata=RegistryMetadata(
            name=intent_name,
            intent_id=intent_id,
            workspace=str(ws),
            prompt=prompt,
            is_stack=is_stack,
        ),
        spec={
            "deployment": deployment.value,
            "services": [s.model_dump(mode="json") for s in services],
            "artifacts": [a.model_dump(mode="json") for a in artifacts],
        },
        status=RegistryStatus(
            phase=phase,
            success=session.get("success") if session else None,
            session_path=str(ws / "session.json") if (ws / "session.json").is_file() else None,
            verification=(session or {}).get("verification"),
            endpoints=endpoints,
        ),
    )
