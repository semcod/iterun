"""Bridge: pipeline / session → registry refresh."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from integrations.adapters.backstage import BackstageExporter
from integrations.adapters.docker import DockerAdapter
from integrations.adapters.opentelemetry import OpenTelemetryExporter
from registry.catalog import RegistryCatalog

if TYPE_CHECKING:
    from generator.pipeline import PipelineResult


def refresh_registry(
    workspace: str | Path,
    *,
    include_docker: bool = True,
    export_backstage: bool = True,
    export_otel: bool = True,
) -> dict[str, Any]:
    """Discover workspace, write iterun.registry.json, optional standard exports."""
    ws = Path(workspace)
    adapter = DockerAdapter() if include_docker else None
    manifest = adapter.collect(ws) if adapter else RegistryCatalog(ws).discover()

    registry_path = RegistryCatalog(ws).write(manifest)
    exports: dict[str, Any] = {"registry": str(registry_path)}

    if export_backstage:
        exports["backstage"] = BackstageExporter().export(manifest, ws)
    if export_otel:
        exports["otel"] = OpenTelemetryExporter().export(manifest, ws)

    return {
        "manifest": manifest.to_dict(),
        "written": exports,
    }


def refresh_registry_from_pipeline(
    workspace: str | Path,
    result: PipelineResult | None = None,
) -> dict[str, Any]:
    """Called after pipeline finalize — uses docker state when executed."""
    include_docker = bool(result and result.execution)
    return refresh_registry(workspace, include_docker=include_docker)
