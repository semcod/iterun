"""
ITERUN Intent DSL — schema, JSON Schema export, LLM system prompt.
"""

from __future__ import annotations

import json
import re
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator

from parser.dsl_parser import DSLParser, ParseError, ValidationError, parse_dsl


class IntentSection(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="kebab-case identifier, e.g. user-api",
    )
    goal: str = Field(..., min_length=3, max_length=500)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("name")
    @classmethod
    def name_kebab(cls, v: str) -> str:
        if not re.match(r"^[a-z][a-z0-9-]*$", v):
            raise ValueError("name must be kebab-case (lowercase, digits, hyphens)")
        return v


class EnvironmentSection(BaseModel):
    runtime: Literal["docker", "kubernetes", "local"] = "docker"
    base_image: str = "python:3.12-slim"
    ports: list[int] = Field(default_factory=lambda: [8000])
    env_vars: dict[str, str] = Field(default_factory=dict)


class ImplementationSection(BaseModel):
    language: Literal["python", "node"] = "python"
    framework: Literal["fastapi", "flask", "express"] | None = "fastapi"
    actions: list[str] = Field(
        ...,
        min_length=1,
        description='DSL action strings, e.g. "api.expose GET /ping"',
    )


class ExecutionSection(BaseModel):
    mode: Literal["dry-run", "transactional"] = "dry-run"


class IntentDSLDocument(BaseModel):
    """Canonical structure for LLM-generated intent YAML."""

    INTENT: IntentSection
    ENVIRONMENT: EnvironmentSection = Field(default_factory=EnvironmentSection)
    IMPLEMENTATION: ImplementationSection
    EXECUTION: ExecutionSection = Field(default_factory=ExecutionSection)


EXAMPLE_YAML = """INTENT:
  name: user-api
  goal: Create a REST API for user management
  description: Simple CRUD API for users

ENVIRONMENT:
  runtime: docker
  base_image: python:3.12-slim
  ports:
    - 8000

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
    - api.expose GET /health
    - api.expose GET /users
    - api.expose POST /users
    - api.expose GET /users/{id}
    - api.expose PUT /users/{id}
    - api.expose DELETE /users/{id}

EXECUTION:
  mode: dry-run
"""

ACTION_TYPES_DOC = """
Allowed action types (string format: TYPE [METHOD] TARGET):
  - api.expose METHOD /path          — HTTP endpoint (METHOD: GET|POST|PUT|DELETE|PATCH)
  - db.create table_name
  - db.add_column table column type
  - shell.exec command
  - rest.call METHOD url
  - file.create path

Framework rules:
  - fastapi, flask → language must be python
  - express → language must be node, base_image node:20-slim
"""


def get_json_schema() -> dict[str, Any]:
    return IntentDSLDocument.model_json_schema()


def document_to_yaml(doc: IntentDSLDocument) -> str:
    payload = doc.model_dump(exclude_none=True)
    return yaml.dump(payload, default_flow_style=False, sort_keys=False, allow_unicode=True)


def validate_yaml_document(yaml_content: str) -> tuple[IntentDSLDocument | None, list[str]]:
    """Validate YAML against Pydantic schema and DSL parser."""
    errors: list[str] = []

    try:
        data = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        return None, [f"Invalid YAML syntax: {e}"]

    if not isinstance(data, dict):
        return None, ["Root must be a YAML mapping"]

    try:
        doc = IntentDSLDocument.model_validate(data)
    except Exception as e:
        errors.append(f"Schema validation: {e}")
        return None, errors

    try:
        parse_dsl(yaml_content)
    except ParseError as e:
        errors.append(f"DSL parse: {e}")
    except ValidationError as e:
        errors.extend(e.errors)

    if errors:
        return doc, errors
    return doc, []


def get_system_prompt() -> str:
    schema_json = json.dumps(get_json_schema(), indent=2)
    return f"""You are an expert ITERUN intent DSL generator.

Output ONLY valid YAML (no markdown fences, no commentary) matching this JSON Schema:

{schema_json}

{ACTION_TYPES_DOC}

Rules:
1. INTENT.name and INTENT.goal are required.
2. REST APIs: include GET /ping and GET /health, use framework fastapi for Python.
3. actions use string format exactly as documented (not nested objects).
4. Use port 8000 for HTTP services.
5. EXECUTION.mode is dry-run unless transactional deployment is explicitly requested.

Example:
{EXAMPLE_YAML}"""
