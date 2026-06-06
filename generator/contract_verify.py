"""Verify deployed service against intent contract (TestQL + HTTP probes)."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from contracts.api_actions import parse_api_actions
from contracts.expectations import load_and_check_expectations
from generator.intract_manifest import write_intract_manifest
from generator.testql_scenario import write_testql_scenario


@dataclass
class VerifyResult:
    success: bool
    errors: list[str] = field(default_factory=list)
    testql_ran: bool = False
    testql_passed: bool = False
    testql_output: str = ""
    probes: list[dict[str, Any]] = field(default_factory=list)
    service_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "errors": self.errors,
            "testql_ran": self.testql_ran,
            "testql_passed": self.testql_passed,
            "testql_output": self.testql_output[-4000:],
            "probes": self.probes,
            "service_url": self.service_url,
        }


def _probe_path(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "1", path)


def discover_service_url(intent_name: str, fallback_endpoints: list[str] | None = None) -> str | None:
    if fallback_endpoints:
        from urllib.parse import urlparse

        for url in fallback_endpoints:
            parsed = urlparse(url)
            if parsed.scheme and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}"

    if not shutil.which("docker"):
        return fallback_endpoints[0].rstrip("/") if fallback_endpoints else None

    pattern = f"intent-{intent_name}"
    # STACK compose project name matches executor _execute_compose_stack
    proc = subprocess.run(
        ["docker", "ps", "--filter", f"name={pattern}", "--format", "{{.Ports}}"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    for line in proc.stdout.splitlines():
        match = re.search(r":(\d+)->", line)
        if match:
            return f"http://localhost:{match.group(1)}"
    return fallback_endpoints[0].rstrip("/") if fallback_endpoints else None


def readiness_paths(intent_data: dict[str, Any] | None) -> list[str]:
    """Paths to probe until the deployed service responds."""
    if intent_data:
        get_paths = [
            _probe_path(path)
            for method, path in parse_api_actions(intent_data)
            if method == "GET"
        ]
        if get_paths:
            return get_paths
    return ["/ping", "/health", "/live", "/ready", "/"]


def _endpoint_responding(base_url: str, path: str) -> bool:
    url = f"{base_url.rstrip('/')}{path}"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            return resp.status < 500
    except urllib.error.HTTPError as exc:
        # 404 still means the HTTP server is up (wrong path, not connection refused)
        return exc.code < 500
    except Exception:
        return False


def wait_for_service(
    base_url: str,
    attempts: int = 30,
    paths: list[str] | None = None,
    intent_data: dict[str, Any] | None = None,
) -> bool:
    probes = paths or readiness_paths(intent_data)
    for _ in range(attempts):
        for path in probes:
            if _endpoint_responding(base_url, path):
                return True
        time.sleep(1)
    return False


def _http_probe(base_url: str, method: str, path: str) -> tuple[bool, str, int]:
    url = f"{base_url.rstrip('/')}{path}"
    req = urllib.request.Request(url, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="replace")[:300]
            ok = resp.status < 400
            if ok and "status" in body and '"ok"' not in body and '"status"' in body:
                try:
                    data = json.loads(body)
                    if data.get("status") not in (None, "ok"):
                        return False, f"unexpected body status={data.get('status')}", resp.status
                except json.JSONDecodeError:
                    pass
            return ok, body, resp.status
    except urllib.error.HTTPError as exc:
        return False, str(exc), exc.code
    except Exception as exc:
        return False, str(exc), 0


def run_testql(scenario_path: Path, base_url: str, timeout_ms: int = 30000) -> tuple[bool, str]:
    if not shutil.which("testql"):
        return False, "testql not installed (pip install testql)"

    proc = subprocess.run(
        [
            "testql", "run", str(scenario_path),
            "--url", base_url,
            "--output", "console",
            "--timeout", str(timeout_ms),
            "--quiet",
        ],
        capture_output=True,
        text=True,
        timeout=max(60, timeout_ms // 1000 + 30),
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, output


def write_contract_artifacts(
    workspace: Path,
    intent_path: Path,
    *,
    prompt: str | None = None,
) -> dict[str, Path]:
    written: dict[str, Path] = {}
    written["intract.yaml"] = write_intract_manifest(
        intent_path, workspace / "intract.yaml", prompt=prompt
    )
    written["service.testql.toon.yaml"] = write_testql_scenario(
        intent_path, workspace / "service.testql.toon.yaml"
    )
    return written


def _run_testql_checks(result: VerifyResult, scenario: Path, base_url: str) -> None:
    if not shutil.which("testql") or not scenario.is_file():
        return
    result.testql_ran = True
    passed, output = run_testql(scenario, base_url)
    result.testql_output = output
    result.testql_passed = passed
    if passed:
        return
    result.errors.append("TestQL contract verification failed")
    for line in output.splitlines():
        if "failed" in line.lower() or "✗" in line or "FAIL" in line:
            result.errors.append(line.strip())


def _run_http_probes(result: VerifyResult, data: dict[str, Any], base_url: str) -> None:
    for method, path in parse_api_actions(data):
        probe = _probe_path(path)
        ok, detail, status = _http_probe(base_url, method, probe)
        result.probes.append({"method": method, "path": probe, "status": status, "ok": ok})
        if not ok:
            result.errors.append(f"HTTP {method} {probe} failed: {detail} (status={status})")


def _write_verify_result(ws: Path, result: VerifyResult) -> VerifyResult:
    result.success = len(result.errors) == 0
    (ws / "verify.result.json").write_text(
        json.dumps(result.to_dict(), indent=2),
        encoding="utf-8",
    )
    return result


def verify_contract(
    workspace: Path | str,
    intent_path: Path | str,
    *,
    prompt: str | None = None,
    service_url: str | None = None,
    execution_endpoints: list[str] | None = None,
) -> VerifyResult:
    ws = Path(workspace)
    intent = Path(intent_path)
    result = VerifyResult(success=False)

    data = yaml.safe_load(intent.read_text(encoding="utf-8")) or {}
    intent_name = str((data.get("INTENT") or {}).get("name", "service"))
    write_contract_artifacts(ws, intent, prompt=prompt)

    base_url = service_url or discover_service_url(intent_name, execution_endpoints)
    if not base_url:
        result.errors.append("Could not discover service URL (docker ps / execution endpoints)")
        return _write_verify_result(ws, result)

    result.service_url = base_url
    if not wait_for_service(base_url, intent_data=data):
        result.errors.append(f"Service not ready at {base_url}")
        return _write_verify_result(ws, result)

    _run_testql_checks(result, ws / "service.testql.toon.yaml", base_url)
    _run_http_probes(result, data, base_url)
    result.errors.extend(load_and_check_expectations(ws, intent, base_url))
    return _write_verify_result(ws, result)
