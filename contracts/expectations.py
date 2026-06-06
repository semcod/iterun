"""Check iterun.yaml + live HTTP against expectations.yaml (prompt contract)."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml

from contracts.api_actions import parse_api_actions


def _probe_path(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "1", path)


def _http_probe(base_url: str, method: str, path: str) -> tuple[bool, str, int]:
    url = f"{base_url.rstrip('/')}{path}"
    req = urllib.request.Request(url, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return True, resp.read().decode("utf-8", errors="replace")[:300], resp.status
    except urllib.error.HTTPError as exc:
        return False, str(exc), exc.code
    except Exception as exc:
        return False, str(exc), 0


def _check_metadata(intent_data: dict[str, Any], expectations: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_name = expectations.get("name")
    actual_name = (intent_data.get("INTENT") or {}).get("name")
    if expected_name and actual_name != expected_name:
        errors.append(f"expectations name: want {expected_name!r}, got {actual_name!r}")

    expected_fw = expectations.get("framework")
    actual_fw = (intent_data.get("IMPLEMENTATION") or {}).get("framework")
    if expected_fw and actual_fw != expected_fw:
        errors.append(f"expectations framework: want {expected_fw!r}, got {actual_fw!r}")
    return errors


def _check_declared_endpoints(intent_data: dict[str, Any], expectations: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    parsed = {(m, p) for m, p in parse_api_actions(intent_data)}
    for endpoint in expectations.get("endpoints", []) or []:
        key = (endpoint["method"].upper(), endpoint["path"])
        if key not in parsed:
            errors.append(f"expectations missing in iterun.yaml: {key[0]} {key[1]}")
    return errors


def _check_endpoint_response(endpoint: dict[str, Any], data: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    for field in endpoint.get("json_fields", []) or []:
        if field not in data:
            errors.append(f"expectations JSON field missing: {field} on {path}")
    for needle in endpoint.get("body_contains", []) or []:
        if needle not in json.dumps(data):
            errors.append(f"expectations response missing {needle!r} on {path}")
    return errors


def _check_live_endpoint(base_url: str, endpoint: dict[str, Any]) -> list[str]:
    method = endpoint["method"].upper()
    path = _probe_path(endpoint["path"])
    expected_status = int(endpoint.get("status", 200))
    ok, detail, status = _http_probe(base_url, method, path)
    if not ok or status != expected_status:
        return [
            f"expectations HTTP {method} {path}: want {expected_status}, got {status} ({detail})"
        ]
    try:
        data = json.loads(detail)
    except json.JSONDecodeError:
        return [f"expectations JSON parse failed on {path}"]
    return _check_endpoint_response(endpoint, data, path)


def check_expectations(
    intent_data: dict[str, Any],
    expectations: dict[str, Any],
    base_url: str | None = None,
) -> list[str]:
    errors = _check_metadata(intent_data, expectations)
    errors.extend(_check_declared_endpoints(intent_data, expectations))
    if base_url:
        for endpoint in expectations.get("endpoints", []) or []:
            errors.extend(_check_live_endpoint(base_url, endpoint))
    return errors


def load_and_check_expectations(
    workspace: Path | str,
    intent_path: Path | str,
    base_url: str | None = None,
) -> list[str]:
    ws = Path(workspace)
    exp_file = ws / "expectations.yaml"
    if not exp_file.is_file():
        return []
    intent_data = yaml.safe_load(Path(intent_path).read_text(encoding="utf-8")) or {}
    expectations = yaml.safe_load(exp_file.read_text(encoding="utf-8")) or {}
    return check_expectations(intent_data, expectations, base_url)
