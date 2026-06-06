"""Backstage Software Catalog exporter (catalog-info.yaml per service)."""

from __future__ import annotations

from pathlib import Path

import yaml

from integrations.adapters.base import RegistryExporter
from registry.models import BACKSTAGE_CATALOG_DIR, RegistryManifest


class BackstageExporter(RegistryExporter):
    """Export iterun services as Backstage Component entities."""

    def export(self, manifest: RegistryManifest, workspace: Path) -> dict[str, str]:
        ws = Path(workspace)
        catalog_dir = ws / BACKSTAGE_CATALOG_DIR
        catalog_dir.mkdir(parents=True, exist_ok=True)
        written: dict[str, str] = {}

        system_name = manifest.metadata.name
        system_path = catalog_dir / f"system-{system_name}.yaml"
        system_path.write_text(
            yaml.dump(
                {
                    "apiVersion": "backstage.io/v1alpha1",
                    "kind": "System",
                    "metadata": {
                        "name": system_name,
                        "description": f"ITERUN generated system ({manifest.spec.get('deployment')})",
                        "labels": {"iterun.dev/managed": "true"},
                    },
                    "spec": {"owner": "iterun"},
                },
                default_flow_style=False,
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        written["system"] = str(system_path)

        for svc in manifest.spec.get("services") or []:
            name = svc.get("name", "service")
            comp_path = catalog_dir / f"component-{name}.yaml"
            comp_path.write_text(
                yaml.dump(
                    {
                        "apiVersion": "backstage.io/v1alpha1",
                        "kind": "Component",
                        "metadata": {
                            "name": name,
                            "description": f"ITERUN service in {system_name}",
                            "labels": svc.get("labels") or {},
                            "annotations": {
                                "iterun.dev/workspace": manifest.metadata.workspace,
                                "iterun.dev/urls": ",".join(svc.get("urls") or []),
                            },
                        },
                        "spec": {
                            "type": "service",
                            "lifecycle": svc.get("lifecycle", "experimental"),
                            "owner": svc.get("owner", "iterun"),
                            "system": system_name,
                        },
                    },
                    default_flow_style=False,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            written[f"component-{name}"] = str(comp_path)

        return written
