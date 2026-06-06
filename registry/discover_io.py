"""Workspace I/O helpers for registry discovery."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from config import PACKAGE_FILENAME
from registry.models import LifecyclePhase


def load_session(workspace: Path) -> dict[str, Any] | None:
    path = workspace / "session.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def load_stack_urls(workspace: Path) -> dict[str, str]:
    path = workspace / "stack.urls.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def intent_from_workspace(workspace: Path) -> dict[str, Any] | None:
    for name in (PACKAGE_FILENAME, "intent.yaml"):
        path = workspace / name
        if path.is_file():
            try:
                return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                return None
    plan = workspace / "plan.result.json"
    if plan.is_file():
        try:
            data = json.loads(plan.read_text(encoding="utf-8"))
            return data.get("intent") or {}
        except (json.JSONDecodeError, OSError):
            pass
    return None


def phase_from_session(session: dict[str, Any] | None) -> LifecyclePhase:
    if not session:
        return LifecyclePhase.PLANNED
    verification = session.get("verification") or {}
    if verification.get("success"):
        return LifecyclePhase.VERIFIED
    if session.get("success"):
        if session.get("execution"):
            return LifecyclePhase.RUNNING
        return LifecyclePhase.PLANNED
    if session.get("error"):
        return LifecyclePhase.FAILED
    return LifecyclePhase.PLANNED
