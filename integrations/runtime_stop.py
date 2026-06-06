"""Stop running workloads before verify retry (docker or pactown)."""

from __future__ import annotations

from pathlib import Path

from config import get_config
from executor.docker_ops import stop_containers_for_intent


def stop_runtime_for_intent(
    intent_name: str,
    workspace: str | Path | None = None,
    *,
    runtime: str | None = None,
) -> int:
    rt = (runtime or get_config().runtime).lower()
    if rt == "pactown":
        from integrations.pactown_runtime import stop_pactown_for_intent

        return stop_pactown_for_intent(intent_name, workspace)
    return stop_containers_for_intent(intent_name)
