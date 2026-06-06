"""Registry models — Backstage-inspired catalog + OCI/OTel metadata."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


REGISTRY_API_VERSION = "iterun.dev/v1"
REGISTRY_FILENAME = "iterun.registry.json"
BACKSTAGE_CATALOG_DIR = "catalog"


class DeploymentKind(str, Enum):
    SINGLE = "single"
    STACK = "stack"


class LifecyclePhase(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    VERIFIED = "verified"
    FAILED = "failed"
    STOPPED = "stopped"


class ArtifactRole(str, Enum):
    INTENT = "intent"
    CONTRACT = "contract"
    TEST = "test"
    PLAN = "plan"
    SESSION = "session"
    RUNTIME = "runtime"
    SBOM = "sbom"


class ArtifactRecord(BaseModel):
    """Tracked file or logical artifact (aligns with SPDX/CycloneDX component refs)."""

    name: str
    path: str
    kind: str
    role: ArtifactRole
    mime_type: str | None = None
    standard: str | None = None
    size_bytes: int | None = None
    checksum_sha256: str | None = None
    labels: dict[str, str] = Field(default_factory=dict)


class ServiceRecord(BaseModel):
    """Runnable unit — maps to Backstage Component + OTel service.name."""

    name: str
    type: str = "service"
    owner: str = "iterun"
    lifecycle: str = "experimental"
    urls: list[str] = Field(default_factory=list)
    health_paths: list[str] = Field(default_factory=list)
    framework: str | None = None
    language: str | None = None
    port: int | None = None
    host_port: int | None = None
    container_id: str | None = None
    image: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    labels: dict[str, str] = Field(default_factory=dict)
    otel: dict[str, Any] = Field(default_factory=dict)


class RegistryMetadata(BaseModel):
    name: str
    intent_id: str | None = None
    workspace: str
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    prompt: str | None = None
    is_stack: bool = False


class RegistryStatus(BaseModel):
    phase: LifecyclePhase = LifecyclePhase.PLANNED
    success: bool | None = None
    session_path: str | None = None
    verification: dict[str, Any] | None = None
    endpoints: list[str] = Field(default_factory=list)


class RegistryManifest(BaseModel):
    """Canonical iterun registry document (JSON, machine-readable)."""

    api_version: str = REGISTRY_API_VERSION
    kind: str = "Registry"
    metadata: RegistryMetadata
    spec: dict[str, Any] = Field(default_factory=dict)
    status: RegistryStatus = Field(default_factory=RegistryStatus)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json", by_alias=False)
