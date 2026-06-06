"""Pydantic request/response models for the web API."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class DSLInput(BaseModel):
    content: str


class IterationInput(BaseModel):
    changes: dict[str, Any]
    source: str = "web"


class ExecutionRequest(BaseModel):
    workspace: Optional[str] = None


class GenerateRequest(BaseModel):
    prompt: str
    max_iterations: int = 5
    model: Optional[str] = None


class GenerateAndRunRequest(BaseModel):
    prompt: str
    output_dir: Optional[str] = None
    execute: bool = False
    verify: bool = False
    max_iterations: int = 5
    max_verify_iterations: int = 3
    model: Optional[str] = None


class PlanYAMLRequest(BaseModel):
    content: str
    output_dir: Optional[str] = None


class RegistryRefreshRequest(BaseModel):
    workspace: str = "generated"
    include_docker: bool = True


class ValidateYAMLRequest(BaseModel):
    content: str


class AICompletionRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096


class AISuggestRequest(BaseModel):
    focus: Optional[str] = None


class AIChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
