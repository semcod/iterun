"""
ITERUN Intent DSL — schema, JSON Schema export, LLM system prompt.
"""

from __future__ import annotations

import json
import re
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator



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
        default_factory=list,
        description='DSL action strings, e.g. "api.expose GET /ping"',
    )


class StackServiceSection(BaseModel):
    language: Literal["python", "node"] | None = None
    framework: Literal["fastapi", "flask", "express"] | None = None
    image: str | None = Field(default=None, description="Pre-built image (redis, postgres, …)")
    base_image: str | None = None
    port: int = 8000
    host_port: int | None = Field(default=None, description="Publish to host (gateway/frontend)")
    depends_on: list[str] = Field(default_factory=list)
    env_vars: dict[str, str] = Field(default_factory=dict)
    actions: list[str] = Field(default_factory=list)


class StackSection(BaseModel):
    network: str = "app-net"
    services: dict[str, StackServiceSection] = Field(
        ...,
        min_length=2,
        description="Named services — each gets its own Dockerfile (unless image:)",
    )


class ExecutionSection(BaseModel):
    mode: Literal["dry-run", "transactional"] = "dry-run"


class IntentDSLDocument(BaseModel):
    """Canonical structure for LLM-generated intent YAML."""

    INTENT: IntentSection
    ENVIRONMENT: EnvironmentSection = Field(default_factory=EnvironmentSection)
    IMPLEMENTATION: ImplementationSection | None = None
    STACK: StackSection | None = None
    EXECUTION: ExecutionSection = Field(default_factory=ExecutionSection)

    @field_validator("STACK")
    @classmethod
    def stack_services_named(cls, v: StackSection | None) -> StackSection | None:
        if v is None:
            return v
        for name in v.services:
            if not re.match(r"^[a-z][a-z0-9-]*$", name):
                raise ValueError(f"STACK service name must be kebab-case: {name!r}")
        return v


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

EXAMPLE_STACK_YAML = """INTENT:
  name: shop-stack
  goal: Multi-service shop with API gateway, users, and catalog

STACK:
  network: shop-net
  services:
    api-gateway:
      language: python
      framework: fastapi
      base_image: python:3.12-slim
      port: 8000
      host_port: 18080
      depends_on: [users-service, catalog-service]
      actions:
        - api.expose GET /ping
        - api.expose GET /health
        - api.expose GET /users
        - api.expose GET /products
    users-service:
      language: python
      framework: fastapi
      port: 8000
      actions:
        - api.expose GET /health
        - api.expose GET /users
    catalog-service:
      language: node
      framework: express
      base_image: node:20-slim
      port: 8000
      actions:
        - api.expose GET /health
        - api.expose GET /products

EXECUTION:
  mode: transactional
"""

ACTION_TYPES_DOC = """
Allowed action types (string format: TYPE [METHOD] TARGET):
  - api.expose METHOD /path          — HTTP endpoint (METHOD: GET|POST|PUT|DELETE|PATCH)
  - db.create table_name
  - db.add_column table column type
  - shell.exec command
  - rest.call METHOD url             — upstream URL (use service hostname in STACK)
  - file.create path

Framework rules:
  - fastapi, flask → language must be python
  - express → language must be node, base_image node:20-slim

Multi-service (STACK):
  - Use STACK.services when the prompt asks for multiple connected containers / microservices.
  - Each service gets its own Dockerfile under services/<name>/ (unless image: is set).
  - Internal services communicate via Docker network hostnames (service name as hostname).
  - Set host_port only on the public entrypoint (gateway, frontend).
  - depends_on lists other service names in the same STACK.
"""


def get_json_schema() -> dict[str, Any]:
    return IntentDSLDocument.model_json_schema()


def document_to_yaml(doc: IntentDSLDocument) -> str:
    payload = doc.model_dump(exclude_none=True)
    return yaml.dump(payload, default_flow_style=False, sort_keys=False, allow_unicode=True)


def validate_yaml_document(yaml_content: str) -> tuple[IntentDSLDocument | None, list[str]]:
    """Validate YAML against Pydantic schema (DSL parse is done separately)."""
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

    if doc.STACK is None and (doc.IMPLEMENTATION is None or not doc.IMPLEMENTATION.actions):
        errors.append("Provide IMPLEMENTATION.actions or STACK.services (min 2 services)")

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
2. REST APIs: include GET /ping and GET /health unless the prompt specifies different health paths (/live, /ready).
3. Include every HTTP endpoint explicitly mentioned in the user prompt (method + path).
4. If the prompt contradicts itself on framework (e.g. "Flask" then "must be FastAPI"), follow the strongest constraint.
5. actions use string format exactly as documented (not nested objects).
6. Use port 8000 inside containers; language must match framework (python↔fastapi/flask, node↔express).
7. EXECUTION.mode is dry-run unless transactional deployment is explicitly requested.
8. Multiple connected Docker services → use STACK (not a single IMPLEMENTATION). Gateway aggregates routes.

Single-service example:
{EXAMPLE_YAML}

Multi-service example:
{EXAMPLE_STACK_YAML}"""
