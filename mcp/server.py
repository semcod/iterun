#!/usr/bin/env python3
"""
ITERUN MCP server — tools: generate_intent, validate_intent, run_intent.

Usage:
  python -m mcp.server
  # or after: pip install mcp
  iterun-mcp
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dsl.schema import get_json_schema, validate_yaml_document
from generator.pipeline import run_pipeline
from sdk.client import IterunClient

try:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("iterun")

    @mcp.tool()
    def iterun_schema() -> str:
        """Return JSON Schema for ITERUN intent DSL."""
        return json.dumps(get_json_schema(), indent=2)

    @mcp.tool()
    def iterun_validate_intent(yaml_content: str) -> str:
        """Validate intent YAML against schema and DSL parser."""
        return json.dumps(IterunClient().validate(yaml_content), indent=2)

    @mcp.tool()
    def iterun_generate_intent(
        prompt: str,
        max_iterations: int = 5,
        model: str | None = None,
    ) -> str:
        """Generate intent YAML from natural language via LiteLLM with retry loop."""
        client = IterunClient(model=model, max_iterations=max_iterations)
        result = client.generate(prompt)
        return json.dumps(result.to_dict(), indent=2)

    @mcp.tool()
    def iterun_run_intent(
        prompt: str,
        output_dir: str = "generated",
        execute: bool = False,
        max_iterations: int = 5,
        model: str | None = None,
    ) -> str:
        """Generate YAML, plan, optionally execute Docker service."""
        result = run_pipeline(
            prompt,
            output_dir=output_dir,
            execute=execute,
            max_iterations=max_iterations,
            model=model,
        )
        return json.dumps(result.to_dict(), indent=2)

    def main():
        mcp.run()

except ImportError:

    def main():
        print(
            "MCP SDK not installed. Run: pip install mcp\n"
            "Or use CLI: iterun generate \"your prompt\"",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
