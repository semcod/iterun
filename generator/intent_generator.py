"""
LLM intent YAML generator with validate-and-retry loop (LiteLLM).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import yaml

from ai_gateway.gateway import AIGateway, get_gateway
from dsl.schema import (
    EXAMPLE_YAML,
    IntentDSLDocument,
    get_system_prompt,
    validate_yaml_document,
)
from ir.models import IntentIR
from parser.dsl_parser import parse_dsl


@dataclass
class GenerateAttempt:
    iteration: int
    yaml_content: str | None
    errors: list[str] = field(default_factory=list)
    llm_error: str | None = None
    model: str | None = None
    tokens: int = 0
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "iteration": self.iteration,
            "yaml_content": self.yaml_content,
            "errors": self.errors,
            "llm_error": self.llm_error,
            "model": self.model,
            "tokens": self.tokens,
            "timestamp": self.timestamp,
        }


@dataclass
class GenerateResult:
    success: bool
    prompt: str
    yaml_content: str | None = None
    ir: IntentIR | None = None
    attempts: list[GenerateAttempt] = field(default_factory=list)
    iterations: int = 0
    model: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "prompt": self.prompt,
            "yaml_content": self.yaml_content,
            "ir": self.ir.to_dict() if self.ir else None,
            "attempts": [a.to_dict() for a in self.attempts],
            "iterations": self.iterations,
            "model": self.model,
            "error": self.error,
        }


_FENCE_RE = re.compile(
    r"```(?:ya?ml)?\s*\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)


def extract_yaml_from_llm(content: str) -> str:
    """Strip markdown fences and leading prose from LLM output."""
    text = (content or "").strip()
    match = _FENCE_RE.search(text)
    if match:
        return match.group(1).strip()
    if text.startswith("INTENT:"):
        return text
    # Drop lines before INTENT:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("INTENT:"):
            return "\n".join(lines[i:]).strip()
    return text


def _fallback_yaml(prompt: str) -> str:
    """Deterministic fallback when LLM unavailable (tests / offline)."""
    name = "generated-api"
    lower = prompt.lower()
    if "user" in lower:
        name = "user-api"
    elif "flask" in lower:
        return EXAMPLE_YAML.replace("fastapi", "flask").replace("user-api", "flask-api")
    elif "express" in lower or "node" in lower:
        return """INTENT:
  name: express-api
  goal: {goal}

ENVIRONMENT:
  runtime: docker
  base_image: node:20-slim
  ports:
    - 8000

IMPLEMENTATION:
  language: node
  framework: express
  actions:
    - api.expose GET /
    - api.expose GET /health

EXECUTION:
  mode: dry-run
""".replace("{goal}", prompt[:200])
    return EXAMPLE_YAML.replace("Create a REST API for user management", prompt[:200]).replace(
        "user-api", name
    )


def _build_user_prompt(
    user_prompt: str,
    *,
    previous_yaml: str | None = None,
    errors: list[str] | None = None,
) -> str:
    if not previous_yaml:
        return f"Generate ITERUN intent YAML for:\n\n{user_prompt}"
    err_text = "\n".join(f"- {e}" for e in (errors or []))
    return f"""Fix the ITERUN intent YAML. Previous output failed validation.

Original request:
{user_prompt}

Validation errors:
{err_text}

Previous YAML:
{previous_yaml}

Output corrected YAML only (no markdown)."""


class IntentGenerator:
    """Generate intent YAML via LiteLLM with validate-and-retry."""

    def __init__(
        self,
        gateway: AIGateway | None = None,
        model: str | None = None,
        max_iterations: int = 5,
        temperature: float = 0.2,
    ):
        self.gateway = gateway or get_gateway()
        self.model = model
        self.max_iterations = max_iterations
        self.temperature = temperature
        self.system_prompt = get_system_prompt()

    def generate(self, prompt: str) -> GenerateResult:
        result = GenerateResult(success=False, prompt=prompt)
        previous_yaml: str | None = None
        previous_errors: list[str] = []

        for iteration in range(1, self.max_iterations + 1):
            attempt = GenerateAttempt(iteration=iteration, yaml_content=None)
            user_msg = _build_user_prompt(
                prompt,
                previous_yaml=previous_yaml,
                errors=previous_errors if iteration > 1 else None,
            )

            response = self.gateway.complete(
                user_msg,
                model=self.model,
                system_prompt=self.system_prompt,
                temperature=self.temperature,
            )

            if not response.get("success"):
                attempt.llm_error = response.get("error", "LLM request failed")
                result.attempts.append(attempt)
                result.error = attempt.llm_error
                return result

            attempt.model = response.get("model")
            result.model = attempt.model
            if response.get("usage"):
                attempt.tokens = response["usage"].get("total_tokens", 0)

            raw = response.get("content") or ""
            if response.get("mock") or raw.startswith("[MOCK]"):
                raw = _fallback_yaml(prompt)

            yaml_content = extract_yaml_from_llm(raw)
            attempt.yaml_content = yaml_content
            doc, errors = validate_yaml_document(yaml_content)
            attempt.errors = errors
            result.attempts.append(attempt)

            if not errors and doc is not None:
                try:
                    ir = parse_dsl(yaml_content)
                except Exception as e:
                    previous_yaml = yaml_content
                    previous_errors = [str(e)]
                    continue

                result.success = True
                result.yaml_content = yaml_content
                result.ir = ir
                result.iterations = iteration
                return result

            previous_yaml = yaml_content
            previous_errors = errors

        result.iterations = self.max_iterations
        result.error = (
            f"Failed after {self.max_iterations} iterations: "
            + "; ".join(previous_errors[:5])
        )
        result.yaml_content = previous_yaml
        return result
