"""Discover artifacts and services from an iterun workspace."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from config import PACKAGE_FILENAME
from registry.labels import build_otel_resource, build_service_labels
from registry.models import (
    ArtifactRecord,
    ArtifactRole,
    DeploymentKind,
    LifecyclePhase,
    RegistryManifest,
    RegistryMetadata,
    RegistryStatus,
    ServiceRecord,
)

KNOWN_ARTIFACTS: list[tuple[str, ArtifactRole, str, str | None]] = [
    (PACKAGE_FILENAME, ArtifactRole.INTENT, "application/x-yaml", "iterun-dsl"),
    ("intract.yaml", ArtifactRole.CONTRACT, "application/x-yaml", "intract"),
    ("service.testql.toon.yaml", ArtifactRole.TEST, "application/x-yaml", "testql"),
    ("session.json", ArtifactRole.SESSION, "application/json", None),
    ("execution.json", ArtifactRole.SESSION, "application/json", None),
    ("plan.result.json", ArtifactRole.PLAN, "application/json", None),
    ("verify.rounds.json", ArtifactRole.TEST, "application/json", None),
    ("docker-compose.yaml", ArtifactRole.RUNTIME, "application/x-yaml", "compose-spec"),
    ("Dockerfile", ArtifactRole.RUNTIME, "text/plain", "dockerfile"),
    ("stack.urls.json", ArtifactRole.RUNTIME, "application/json", None),
    ("openapi.yaml", ArtifactRole.CONTRACT, "application/x-yaml", "openapi"),
    ("container.log", ArtifactRole.SESSION, "text/plain", None),
    ("prompt.txt", ArtifactRole.SESSION, "text/plain", None),
]


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _discover_artifacts(workspace: Path) -> list[ArtifactRecord]:
    records: list[ArtifactRecord] = []
    seen: set[str] = set()

    for rel, role, mime, standard in KNOWN_ARTIFACTS:
        path = workspace / rel
        if not path.is_file():
            continue
        seen.add(rel)
        records.append(
            ArtifactRecord(
                name=rel,
                path=str(path),
                kind="file",
                role=role,
                mime_type=mime,
                standard=standard,
                size_bytes=path.stat().st_size,
                checksum_sha256=_sha256(path),
            )
        )

    services_dir = workspace / "services"
    if services_dir.is_dir():
        for svc_dir in sorted(services_dir.iterdir()):
            if not svc_dir.is_dir():
                continue
            for child in svc_dir.rglob("*"):
                if not child.is_file():
                    continue
                rel = str(child.relative_to(workspace))
                if rel in seen:
                    continue
                seen.add(rel)
                records.append(
                    ArtifactRecord(
                        name=rel,
                        path=str(child),
                        kind="file",
                        role=ArtifactRole.RUNTIME,
                        mime_type="text/plain",
                        size_bytes=child.stat().st_size,
                        checksum_sha256=_sha256(child),
                        labels={"iterun.service": svc_dir.name},
                    )
                )

    for app in ("app.py", "app.js"):
        path = workspace / app
        if path.is_file() and app not in seen:
            records.append(
                ArtifactRecord(
                    name=app,
                    path=str(path),
                    kind="file",
                    role=ArtifactRole.RUNTIME,
                    mime_type="text/plain",
                    size_bytes=path.stat().st_size,
                    checksum_sha256=_sha256(path),
                )
            )
    return records


def _load_session(workspace: Path) -> dict[str, Any] | None:
    path = workspace / "session.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _load_stack_urls(workspace: Path) -> dict[str, str]:
    path = workspace / "stack.urls.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _intent_from_workspace(workspace: Path) -> dict[str, Any] | None:
    for name in (PACKAGE_FILENAME, "intent.yaml"):
        path = workspace / name
        if path.is_file():
            try:
                return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                return None
    plan = workspace / "plan.result.json"
    if plan.is_file():
        try:
            data = json.loads(plan.read_text(encoding="utf-8"))
            return data.get("intent") or {}
        except (json.JSONDecodeError, OSError):
            pass
    return None


def _phase_from_session(session: dict[str, Any] | None) -> LifecyclePhase:
    if not session:
        return LifecyclePhase.PLANNED
    verification = session.get("verification") or {}
    if verification.get("success"):
        return LifecyclePhase.VERIFIED
    if session.get("success"):
        if session.get("execution"):
            return LifecyclePhase.RUNNING
        return LifecyclePhase.PLANNED
    if session.get("error"):
        return LifecyclePhase.FAILED
    return LifecyclePhase.PLANNED


def discover_workspace(workspace: str | Path) -> RegistryManifest:
    """Build registry manifest by scanning workspace artifacts."""
    ws = Path(workspace).resolve()
    session = _load_session(ws)
    intent_doc = _intent_from_workspace(ws) or {}
    intent_section = intent_doc.get("INTENT") or intent_doc.get("intent") or {}
    intent_name = intent_section.get("name") or ws.name
    intent_id = intent_section.get("id") or (session or {}).get("generate", {}).get("ir", {}).get("id")

    stack_section = intent_doc.get("STACK") or {}
    stack_services = (stack_section.get("services") or {}) if isinstance(stack_section, dict) else {}
    is_stack = bool(stack_services) or (ws / "docker-compose.yaml").is_file()
    deployment = DeploymentKind.STACK if is_stack else DeploymentKind.SINGLE

    stack_urls = _load_stack_urls(ws)
    execution = (session or {}).get("execution") or {}
    endpoints: list[str] = list(execution.get("endpoints") or [])
    container_id = execution.get("container_id")

    services: list[ServiceRecord] = []

    if is_stack and stack_services:
        for svc_name, svc_def in stack_services.items():
            if not isinstance(svc_def, dict):
                svc_def = {}
            url = stack_urls.get(svc_name)
            urls = [url] if url else []
            if not urls and svc_def.get("host_port"):
                urls = [f"http://localhost:{svc_def['host_port']}"]
            health = []
            for action in svc_def.get("actions") or []:
                if isinstance(action, str) and "GET" in action:
                    parts = action.split()
                    if len(parts) >= 2:
                        health.append(parts[-1])
            labels = build_service_labels(
                intent_name,
                svc_name,
                intent_id=intent_id,
                framework=svc_def.get("framework"),
                language=svc_def.get("language"),
            )
            services.append(
                ServiceRecord(
                    name=svc_name,
                    urls=urls,
                    health_paths=health[:3],
                    framework=svc_def.get("framework"),
                    language=svc_def.get("language"),
                    port=svc_def.get("port"),
                    host_port=svc_def.get("host_port"),
                    image=svc_def.get("image"),
                    depends_on=list(svc_def.get("depends_on") or []),
                    container_id=container_id if svc_def.get("host_port") else None,
                    labels=labels,
                    otel=build_otel_resource(
                        intent_name, svc_name, workspace=str(ws), urls=urls
                    ),
                )
            )
    else:
        impl = intent_doc.get("IMPLEMENTATION") or intent_doc.get("implementation") or {}
        urls = endpoints[:1] if endpoints else []
        labels = build_service_labels(
            intent_name,
            intent_name,
            intent_id=intent_id,
            framework=impl.get("framework") if isinstance(impl, dict) else None,
            language=impl.get("language") if isinstance(impl, dict) else None,
        )
        services.append(
            ServiceRecord(
                name=intent_name,
                urls=urls,
                framework=impl.get("framework") if isinstance(impl, dict) else None,
                language=impl.get("language") if isinstance(impl, dict) else None,
                container_id=container_id,
                labels=labels,
                otel=build_otel_resource(intent_name, intent_name, workspace=str(ws), urls=urls),
            )
        )

    artifacts = _discover_artifacts(ws)
    phase = _phase_from_session(session)

    return RegistryManifest(
        metadata=RegistryMetadata(
            name=intent_name,
            intent_id=intent_id,
            workspace=str(ws),
            prompt=(session or {}).get("prompt") or (ws / "prompt.txt").read_text(encoding="utf-8")
            if (ws / "prompt.txt").is_file()
            else None,
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
