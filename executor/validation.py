"""Endpoint validation and auto-fix helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from executor.models import ExecutionResult, ValidationResult

if TYPE_CHECKING:
    from ir.models import IntentIR

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


def filter_validation_endpoints(endpoints: list[str]) -> list[str]:
    """Drop bare base URLs when explicit routes exist on the same host (404 on / is OK)."""
    by_host: dict[str, list[str]] = {}
    for endpoint in endpoints:
        parsed = urlparse(endpoint)
        base = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path or "/"
        by_host.setdefault(base, []).append(path)

    filtered: list[str] = []
    for endpoint in endpoints:
        parsed = urlparse(endpoint)
        base = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path or "/"
        if path in ("/", ""):
            explicit = [p for p in by_host.get(base, []) if p not in ("/", "")]
            if explicit:
                continue
        filtered.append(endpoint)
    return filtered


def validate_endpoints(
    endpoints: list[str],
    result: ExecutionResult,
    *,
    timeout: int = 10,
) -> ValidationResult:
    """Validate that endpoints are responding correctly."""
    validation = ValidationResult()

    if not HTTPX_AVAILABLE:
        validation.success = True
        result.add_log("httpx not available, skipping validation")
        return validation

    checked: set[str] = set()

    for endpoint in endpoints:
        if endpoint in checked:
            continue
        checked.add(endpoint)

        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(endpoint)

                if response.status_code < 400:
                    validation.add_check(endpoint, response.status_code, True)
                    result.add_log(f"  ✓ {endpoint} → {response.status_code}")
                else:
                    validation.add_check(
                        endpoint,
                        response.status_code,
                        False,
                        f"HTTP {response.status_code}",
                    )
                    result.add_log(f"  ✗ {endpoint} → {response.status_code}")

        except httpx.ConnectError:
            validation.add_check(endpoint, 0, False, "Connection refused")
            result.add_log(f"  ✗ {endpoint} → Connection refused")
            validation.suggestions.append(
                "Container may still be starting or crashed. Check 'docker logs'"
            )

        except httpx.TimeoutException:
            validation.add_check(endpoint, 0, False, "Timeout")
            result.add_log(f"  ✗ {endpoint} → Timeout")
            validation.suggestions.append("Endpoint is taking too long to respond")

        except Exception as e:
            validation.add_check(endpoint, 0, False, str(e))
            result.add_log(f"  ✗ {endpoint} → {e}")

    validation.success = len(validation.failed_endpoints) == 0

    if not validation.success:
        if any("Connection refused" in e for e in validation.errors):
            validation.suggestions.append(
                "Check if the application is listening on the correct port"
            )
            validation.suggestions.append(
                "Verify Dockerfile EXPOSE matches application port"
            )

        if any("404" in str(c.get("status")) for c in validation.checks):
            validation.suggestions.append(
                "Some routes may not be registered correctly"
            )

    return validation


def add_main_block(ir: IntentIR, container_port: int) -> str:
    """Add missing __main__ block to generated code."""
    code = ir.generated_code

    if ir.implementation.framework == "fastapi":
        if "if __name__" not in code:
            code += f"""

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port={container_port})
"""
    elif ir.implementation.framework == "flask":
        if "if __name__" not in code:
            code += f"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port={container_port})
"""
    elif ir.implementation.framework == "express":
        if "app.listen" not in code:
            code += f"""

app.listen({container_port}, '0.0.0.0', () => {{
    console.log('Server running on port {container_port}');
}});
"""

    return code


def attempt_auto_fix(
    ir: IntentIR,
    result: ExecutionResult,
    validation: ValidationResult,
    *,
    container_port: int,
) -> bool:
    """Attempt to fix issues found during validation."""
    fixes_applied: list[str] = []

    for error in validation.errors:
        if "Connection refused" in error:
            if ir.generated_code and "if __name__" not in ir.generated_code:
                ir.generated_code = add_main_block(ir, container_port)
                fixes_applied.append("Added __main__ block")

            if ir.implementation.framework == "fastapi":
                if f"port={container_port}" not in ir.generated_code:
                    ir.generated_code = ir.generated_code.replace(
                        'uvicorn.run(app, host="0.0.0.0")',
                        f'uvicorn.run(app, host="0.0.0.0", port={container_port})',
                    )
                    fixes_applied.append(f"Fixed port to {container_port}")

        if "500" in error and "try:" not in ir.generated_code:
            fixes_applied.append("Consider adding try/except blocks")

    if fixes_applied:
        result.add_log(f"Applied fixes: {', '.join(fixes_applied)}")
        ir.add_iteration(
            {
                "auto_fix": True,
                "fixes": fixes_applied,
                "validation_errors": validation.errors,
            },
            source="auto_fix",
        )
        return True

    return False
