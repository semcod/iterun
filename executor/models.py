"""Execution result types shared across executor and integrations."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class ExecutionError(Exception):
    """Raised when execution fails."""

    pass


class ValidationResult:
    """Result of post-execution validation."""

    def __init__(self) -> None:
        self.success: bool = False
        self.checks: list[dict[str, Any]] = []
        self.failed_endpoints: list[str] = []
        self.errors: list[str] = []
        self.suggestions: list[str] = []

    def add_check(self, endpoint: str, status: int, ok: bool, error: str | None = None) -> None:
        self.checks.append(
            {"endpoint": endpoint, "status": status, "ok": ok, "error": error}
        )
        if not ok:
            self.failed_endpoints.append(endpoint)
            if error:
                self.errors.append(f"{endpoint}: {error}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "checks": self.checks,
            "failed_endpoints": self.failed_endpoints,
            "errors": self.errors,
            "suggestions": self.suggestions,
        }


class ExecutionResult:
    """Result of intent execution."""

    def __init__(self) -> None:
        self.success: bool = False
        self.logs: list[str] = []
        self.artifacts: dict[str, str] = {}
        self.container_id: str | None = None
        self.endpoints: list[str] = []
        self.error: str | None = None
        self.execution_time: float = 0.0
        self.validation: ValidationResult | None = None
        self.auto_fix_applied: bool = False
        self.fix_iterations: int = 0

    def add_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "logs": self.logs,
            "artifacts": self.artifacts,
            "container_id": self.container_id,
            "endpoints": self.endpoints,
            "error": self.error,
            "execution_time": self.execution_time,
            "validation": self.validation.to_dict() if self.validation else None,
            "auto_fix_applied": self.auto_fix_applied,
            "fix_iterations": self.fix_iterations,
        }
