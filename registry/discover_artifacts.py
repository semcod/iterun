"""Artifact discovery for iterun workspaces."""

from __future__ import annotations

import hashlib
from pathlib import Path

from config import PACKAGE_FILENAME
from registry.models import ArtifactRecord, ArtifactRole

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


def sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def discover_artifacts(workspace: Path) -> list[ArtifactRecord]:
    """Scan workspace for known and generated artifacts."""
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
                checksum_sha256=sha256_file(path),
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
                        checksum_sha256=sha256_file(child),
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
                    checksum_sha256=sha256_file(path),
                )
            )
    return records
