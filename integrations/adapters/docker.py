"""Docker adapter — enrich registry with running container state."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from integrations.adapters.filesystem import FilesystemAdapter
from registry.models import LifecyclePhase, RegistryManifest


class DockerAdapter(FilesystemAdapter):
    """Merge docker ps / compose state into registry manifest."""

    def collect(self, workspace: Path) -> RegistryManifest:
        manifest = super().collect(workspace)
        return self.enrich(manifest, workspace)

    def enrich(self, manifest: RegistryManifest, workspace: Path) -> RegistryManifest:
        running = _running_iterun_containers()
        if not running:
            return manifest

        services = manifest.spec.get("services") or []
        any_running = False
        for svc in services:
            name = svc.get("name", "")
            intent = manifest.metadata.name
            matches = [
                c
                for c in running
                if c.get("Labels", {}).get("dev.iterun.service") == name
                or c.get("Labels", {}).get("dev.iterun.intent") == intent
                or name in (c.get("Names") or [""])[0]
            ]
            if matches:
                any_running = True
                c = matches[0]
                svc["container_id"] = c.get("ID") or c.get("Id")
                svc["image"] = c.get("Image")
                labels = c.get("Labels") or {}
                svc.setdefault("labels", {}).update(
                    {k: v for k, v in labels.items() if k.startswith("dev.iterun.")}
                )
        manifest.spec["services"] = services

        if any_running and manifest.status.phase == LifecyclePhase.PLANNED:
            manifest.status.phase = LifecyclePhase.RUNNING
        return manifest


def _running_iterun_containers() -> list[dict]:
    try:
        proc = subprocess.run(
            ["docker", "ps", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode != 0:
            return []
        out = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return [
            c
            for c in out
            if "dev.iterun." in json.dumps(c.get("Labels") or {})
            or "intent-" in (c.get("Names") or [""])[0]
        ]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
