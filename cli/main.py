#!/usr/bin/env python3
"""ITERUN: Command Line Interface — argparse entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.dispatch import dispatch_command
from cli.shell import CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ITERUN: DSL-based intent execution system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Start interactive shell
  %(prog)s plan myintent.yaml        # Run dry-run on file
  %(prog)s new my-api                # Create new intent
  %(prog)s execute myintent.yaml     # Plan, approve and execute
  %(prog)s generate "REST API" -o out/  # LLM → iterun.yaml
  %(prog)s schema                    # JSON Schema for intent DSL
  %(prog)s registry -o generated/    # Refresh service/artifact registry
        """,
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="shell",
        choices=[
            "shell",
            "new",
            "plan",
            "execute",
            "parse",
            "generate",
            "validate",
            "schema",
            "registry",
        ],
        help="Command to run",
    )
    parser.add_argument("file", nargs="?", help="DSL file path or intent name")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--goal", "-g", help="Goal for new intent")
    parser.add_argument("--workspace", "-w", help="Workspace directory for execution")
    parser.add_argument("--output-dir", "-o", help="Directory for generated plan artifacts")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output (for scripts)")
    parser.add_argument("--prompt", "-p", help="Natural language prompt (generate command)")
    parser.add_argument("--max-iterations", type=int, default=5, help="LLM validate-retry limit")
    parser.add_argument("--model", "-m", help="LiteLLM model name")
    parser.add_argument("--run", action="store_true", help="Plan after generate (generate command)")
    parser.add_argument("--execute", action="store_true", help="Execute after generate (generate command)")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="TestQL contract verify after execute; retry on failure",
    )
    parser.add_argument(
        "--max-verify-iterations",
        type=int,
        default=3,
        help="Regenerate+redeploy attempts when --verify fails",
    )
    parser.add_argument(
        "--runtime",
        choices=["docker", "pactown"],
        default=None,
        help="Execution runtime (default: ITERUN_RUNTIME or docker)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.runtime:
        import os

        from config import reload_config

        os.environ["ITERUN_RUNTIME"] = args.runtime
        reload_config()

    cli = CLI(no_color=args.no_color, quiet=args.quiet)
    dispatch_command(args, cli)


if __name__ == "__main__":
    main()
