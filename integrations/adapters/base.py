"""Adapter protocol for registry integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from registry.models import RegistryManifest


class RegistryAdapter(ABC):
    """Collect or export registry data from an external system."""

    @abstractmethod
    def collect(self, workspace: Path) -> RegistryManifest:
        """Build registry manifest from workspace (+ optional live state)."""

    def enrich(self, manifest: RegistryManifest, workspace: Path) -> RegistryManifest:
        """Optionally merge live runtime data into manifest."""
        return manifest


class RegistryExporter(ABC):
    """Export registry to industry-standard formats."""

    @abstractmethod
    def export(self, manifest: RegistryManifest, workspace: Path) -> dict[str, str]:
        """Return mapping format → written path."""
