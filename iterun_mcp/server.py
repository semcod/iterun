#!/usr/bin/env python3
"""
ITERUN MCP server — tools for LLM agents (schema, validate, generate, plan, pipeline).

Usage (from iterun repo root):
  pip install -e ".[mcp]"
  iterun-mcp
  python -m iterun_mcp.server
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.service import IterunService
from parser.dsl_parser import ParseError, ValidationError

try:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("iterun")
    _service = IterunService()

    @mcp.tool()
    def iterun_interfaces() -> str:
        """List available ITERUN integration surfaces (REST, CLI, SDK, MCP) and endpoints."""
        return json.dumps(_service.interfaces_info(), indent=2)

    @mcp.tool()
    def iterun_schema() -> str:
        """Return JSON Schema for ITERUN intent DSL."""
        return json.dumps(_service.schema(), indent=2)

    @mcp.tool()
    def iterun_validate_intent(yaml_content: str) -> str:
        """Validate intent YAML against schema and DSL parser."""
        return json.dumps(_service.validate_yaml(yaml_content), indent=2)

    @mcp.tool()
    def iterun_parse_yaml(yaml_content: str) -> str:
        """Parse intent YAML into IR JSON (supports STACK multi-service)."""
        try:
            ir = _service.parse(yaml_content)
            return json.dumps({"success": True, "intent": ir.to_dict()}, indent=2)
        except (ParseError, ValidationError) as e:
            return json.dumps({"success": False, "error": str(e)}, indent=2)

    @mcp.tool()
    def iterun_plan_yaml(yaml_content: str, output_dir: str | None = None) -> str:
        """Dry-run plan from YAML — generates Dockerfile(s) and docker-compose for STACK."""
        try:
            return json.dumps(
                _service.plan_yaml(yaml_content, output_dir=output_dir),
                indent=2,
            )
        except (ParseError, ValidationError) as e:
            return json.dumps({"success": False, "error": str(e)}, indent=2)

    @mcp.tool()
    def iterun_generate_intent(
        prompt: str,
        max_iterations: int = 5,
        model: str | None = None,
    ) -> str:
        """Generate intent YAML from natural language via LiteLLM with retry loop."""
        result = _service.generate(prompt, model=model, max_iterations=max_iterations)
        return json.dumps(result.to_dict(), indent=2)

    @mcp.tool()
    def iterun_run_pipeline(
        prompt: str,
        output_dir: str = "generated",
        execute: bool = False,
        verify: bool = False,
        max_iterations: int = 5,
        max_verify_iterations: int = 3,
        model: str | None = None,
    ) -> str:
        """Full pipeline: prompt → iterun.yaml → plan → optional Docker execute → optional verify."""
        result = _service.run_pipeline(
            prompt,
            output_dir=output_dir,
            execute=execute,
            verify=verify,
            max_iterations=max_iterations,
            max_verify_iterations=max_verify_iterations,
            model=model,
        )
        return json.dumps(result.to_dict(), indent=2)

    @mcp.tool()
    def iterun_registry_refresh(
        workspace: str = "generated",
        include_docker: bool = True,
    ) -> str:
        """Refresh service/artifact registry (iterun.registry.json, Backstage, OTel)."""
        return json.dumps(
            _service.registry_refresh(workspace, include_docker=include_docker),
            indent=2,
        )

    @mcp.tool()
    def iterun_registry_list(pattern: str = "examples/*/generated") -> str:
        """List registry summaries for workspace glob pattern."""
        return json.dumps({"registries": _service.registry_list(pattern)}, indent=2)

    @mcp.tool()
    def iterun_run_intent(
        prompt: str,
        output_dir: str = "generated",
        execute: bool = False,
        max_iterations: int = 5,
        model: str | None = None,
    ) -> str:
        """Deprecated alias for iterun_run_pipeline (without verify)."""
        return iterun_run_pipeline(
            prompt,
            output_dir=output_dir,
            execute=execute,
            verify=False,
            max_iterations=max_iterations,
            model=model,
        )

    def main():
        mcp.run()

except ImportError:

    def main():
        print(
            "MCP SDK not installed. From iterun repo root run:\n"
            "  pip install -e '.[mcp]'\n"
            "Or use CLI: iterun generate \"your prompt\"",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
