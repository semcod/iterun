#!/usr/bin/env python3
"""Verify generated intent + live service match expectations.yaml (from prompt)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _map_expectation_errors(raw_errors: list[str]) -> list[str]:
    mapped: list[str] = []
    for err in raw_errors:
        if err.startswith("expectations name:"):
            mapped.append(err.replace("expectations name:", "intent name:", 1))
        elif err.startswith("expectations framework:"):
            mapped.append(err.replace("expectations framework:", "framework:", 1))
        elif err.startswith("expectations missing in iterun.yaml:"):
            mapped.append(err.replace("expectations missing in iterun.yaml:", "missing in iterun.yaml:", 1))
        elif err.startswith("expectations HTTP "):
            mapped.append(err.replace("expectations HTTP ", "HTTP ", 1))
        elif err.startswith("expectations JSON"):
            mapped.append(err.replace("expectations JSON", "HTTP", 1))
        elif err.startswith("expectations response missing"):
            mapped.append(err.replace("expectations response missing", "HTTP", 1))
        else:
            mapped.append(err)
    return mapped


def verify(
    expectations_path: Path,
    intent_path: Path,
    base_url: str | None,
) -> list[str]:
    from contracts.expectations import check_expectations

    expectations = _load_yaml(expectations_path)
    intent_data = _load_yaml(intent_path)
    return _map_expectation_errors(check_expectations(intent_data, expectations, base_url))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expectations", type=Path)
    parser.add_argument("intent", type=Path)
    parser.add_argument("--url", default=None, help="Live service base URL")
    args = parser.parse_args()

    errors = verify(args.expectations, args.intent, args.url)
    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        sys.exit(1)
    print("OK expectations verified")


if __name__ == "__main__":
    main()
