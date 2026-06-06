"""Service record builders for registry discovery."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from registry.labels import build_otel_resource, build_service_labels
from registry.models import ServiceRecord


def build_stack_services(
    *,
    intent_name: str,
    intent_id: str | None,
    stack_services: dict[str, Any],
    stack_urls: dict[str, str],
    container_id: str | None,
    workspace: Path,
) -> list[ServiceRecord]:
    """Build service records for a multi-service STACK."""
    services: list[ServiceRecord] = []

    for svc_name, svc_def in stack_services.items():
        if not isinstance(svc_def, dict):
            svc_def = {}
        url = stack_urls.get(svc_name)
        urls = [url] if url else []
        if not urls and svc_def.get("host_port"):
            urls = [f"http://localhost:{svc_def['host_port']}"]
        health: list[str] = []
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
                    intent_name, svc_name, workspace=str(workspace), urls=urls
                ),
            )
        )
    return services


def build_single_service(
    *,
    intent_name: str,
    intent_id: str | None,
    intent_doc: dict[str, Any],
    endpoints: list[str],
    container_id: str | None,
    workspace: Path,
) -> list[ServiceRecord]:
    """Build service record for a single-service intent."""
    impl = intent_doc.get("IMPLEMENTATION") or intent_doc.get("implementation") or {}
    urls = endpoints[:1] if endpoints else []
    labels = build_service_labels(
        intent_name,
        intent_name,
        intent_id=intent_id,
        framework=impl.get("framework") if isinstance(impl, dict) else None,
        language=impl.get("language") if isinstance(impl, dict) else None,
    )
    return [
        ServiceRecord(
            name=intent_name,
            urls=urls,
            framework=impl.get("framework") if isinstance(impl, dict) else None,
            language=impl.get("language") if isinstance(impl, dict) else None,
            container_id=container_id,
            labels=labels,
            otel=build_otel_resource(
                intent_name, intent_name, workspace=str(workspace), urls=urls
            ),
        )
    ]
