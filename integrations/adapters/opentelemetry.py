"""OpenTelemetry resource export (lightweight, no OTLP SDK)."""

from __future__ import annotations

import json
from pathlib import Path

from integrations.adapters.base import RegistryExporter
from registry.models import RegistryManifest


class OpenTelemetryExporter(RegistryExporter):
    """Write OTel resource descriptors for generated services."""

    def export(self, manifest: RegistryManifest, workspace: Path) -> dict[str, str]:
        ws = Path(workspace)
        out_path = ws / "otel.resources.json"
        resources = []
        for svc in manifest.spec.get("services") or []:
            otel = svc.get("otel") or {}
            if otel:
                resources.append(otel)
        payload = {
            "schemaUrl": "https://opentelemetry.io/schemas/1.26.0",
            "resources": resources,
        }
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return {"otel": str(out_path)}
