"""Registry catalog — load, save, index workspaces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from registry.discover import discover_workspace
from registry.models import REGISTRY_FILENAME, RegistryManifest


class RegistryCatalog:
    """Workspace-scoped service and artifact registry."""

    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()

    @property
    def registry_path(self) -> Path:
        return self.workspace / REGISTRY_FILENAME

    def discover(self) -> RegistryManifest:
        return discover_workspace(self.workspace)

    def load(self) -> RegistryManifest | None:
        if not self.registry_path.is_file():
            return None
        data = json.loads(self.registry_path.read_text(encoding="utf-8"))
        return RegistryManifest.model_validate(data)

    def refresh(self) -> Path:
        manifest = self.discover()
        return self.write(manifest)

    def write(self, manifest: RegistryManifest | None = None) -> Path:
        manifest = manifest or self.discover()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(
            json.dumps(manifest.to_dict(), indent=2),
            encoding="utf-8",
        )
        return self.registry_path

    def summary(self) -> dict[str, Any]:
        m = self.load() or self.discover()
        return {
            "name": m.metadata.name,
            "workspace": m.metadata.workspace,
            "deployment": m.spec.get("deployment"),
            "phase": m.status.phase.value,
            "success": m.status.success,
            "services": len(m.spec.get("services") or []),
            "artifacts": len(m.spec.get("artifacts") or []),
            "endpoints": m.status.endpoints,
        }


def discover_glob(pattern: str) -> list[dict[str, Any]]:
    """Discover multiple workspaces (e.g. examples/*/generated)."""
    root = Path(".")
    results: list[dict[str, Any]] = []
    for path in sorted(root.glob(pattern)):
        if not path.is_dir():
            continue
        if not (path / REGISTRY_FILENAME).is_file() and not (path / "iterun.yaml").is_file():
            if not (path / "plan.result.json").is_file() and not (path / "docker-compose.yaml").is_file():
                continue
        cat = RegistryCatalog(path)
        results.append(cat.summary())
    return results
