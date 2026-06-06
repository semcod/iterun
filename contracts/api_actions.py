"""Parse api.expose actions from iterun.yaml dicts."""

from __future__ import annotations

import re
from typing import Any


def _parse_action_strings(actions: list[Any]) -> list[tuple[str, str]]:
    parsed: list[tuple[str, str]] = []
    for action in actions:
        if not isinstance(action, str):
            continue
        match = re.match(
            r"api\.expose\s+(GET|POST|PUT|PATCH|DELETE)\s+(\S+)",
            action.strip(),
            re.IGNORECASE,
        )
        if match:
            parsed.append((match.group(1).upper(), match.group(2)))
    return parsed


def parse_api_actions(intent_data: dict[str, Any]) -> list[tuple[str, str]]:
    parsed = _parse_action_strings(
        (intent_data.get("IMPLEMENTATION", {}) or {}).get("actions", []) or []
    )
    stack = intent_data.get("STACK") or {}
    for _name, svc in (stack.get("services") or {}).items():
        if not isinstance(svc, dict):
            continue
        if not svc.get("host_port"):
            continue
        parsed.extend(_parse_action_strings(svc.get("actions", []) or []))
    return parsed
