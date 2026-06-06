"""Standard labels for Docker/OCI and compose (monitoring-friendly)."""

from __future__ import annotations

from typing import Any

OCI = "org.opencontainers.image"
ITERUN = "dev.iterun"


def build_service_labels(
    intent_name: str,
    service_name: str,
    *,
    intent_id: str | None = None,
    framework: str | None = None,
    language: str | None = None,
) -> dict[str, str]:
    """OCI Image Spec + iterun labels for Docker/Compose."""
    labels = {
        f"{OCI}.title": service_name,
        f"{OCI}.vendor": "iterun",
        f"{ITERUN}.intent": intent_name,
        f"{ITERUN}.service": service_name,
        f"{ITERUN}.managed-by": "iterun",
    }
    if intent_id:
        labels[f"{ITERUN}.intent-id"] = intent_id
    if framework:
        labels[f"{ITERUN}.framework"] = framework
    if language:
        labels[f"{ITERUN}.language"] = language
    return labels


def build_otel_resource(
    intent_name: str,
    service_name: str,
    *,
    workspace: str | None = None,
    urls: list[str] | None = None,
) -> dict[str, Any]:
    """OpenTelemetry resource descriptor (no SDK required)."""
    attrs: dict[str, Any] = {
        "service.name": service_name,
        "service.namespace": intent_name,
        "deployment.environment": "iterun-generated",
    }
    if workspace:
        attrs["iterun.workspace"] = workspace
    if urls:
        attrs["iterun.urls"] = urls
    return {"resource": {"attributes": attrs}}
