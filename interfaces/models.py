"""Shared request/response models for REST, SDK, and MCP."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ValidateYAMLRequest(BaseModel):
    content: str


class GenerateRequest(BaseModel):
    prompt: str
    max_iterations: int = 5
    model: Optional[str] = None


class PipelineRequest(BaseModel):
    prompt: str
    output_dir: Optional[str] = "generated"
    execute: bool = False
    verify: bool = False
    max_iterations: int = 5
    max_verify_iterations: int = 3
    model: Optional[str] = None


class PlanYAMLRequest(BaseModel):
    content: str
    output_dir: Optional[str] = None


class ParseRequest(BaseModel):
    content: str


class ExecuteRequest(BaseModel):
    workspace: Optional[str] = None
    validate: bool = True
    auto_fix: bool = True


class InterfacesInfo(BaseModel):
    """Available integration surfaces."""

    rest_base: str = "/api"
    cli: str = "iterun"
    mcp_server: str = "iterun-mcp / python -m iterun_mcp.server"
    sdk: str = "from sdk import IterunClient"
    surfaces: list[dict[str, Any]] = Field(default_factory=list)
