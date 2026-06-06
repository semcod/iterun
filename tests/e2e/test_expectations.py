"""Tests for expectations.yaml contract checks."""

import yaml

from generator.expectations import check_expectations

INTENT_MINIMAL = """
INTENT:
  name: user-api
IMPLEMENTATION:
  framework: fastapi
  actions:
    - api.expose GET /ping
"""

EXPECTATIONS_FULL = """
name: user-api
framework: fastapi
endpoints:
  - method: GET
    path: /ping
    status: 200
  - method: GET
    path: /health
    status: 200
  - method: GET
    path: /users
    status: 200
"""


def test_check_expectations_missing_endpoints():
    intent = yaml.safe_load(INTENT_MINIMAL)
    exp = yaml.safe_load(EXPECTATIONS_FULL)
    errors = check_expectations(intent, exp, base_url=None)
    assert any("missing in iterun.yaml" in e for e in errors)
    assert any("/health" in e for e in errors)
    assert any("/users" in e for e in errors)


def test_check_expectations_framework_mismatch():
    intent = yaml.safe_load(INTENT_MINIMAL)
    exp = yaml.safe_load("framework: flask\nendpoints: []")
    errors = check_expectations(intent, exp)
    assert any("framework" in e for e in errors)
