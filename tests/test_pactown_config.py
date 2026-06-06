"""Tests for pactown/markpact integration helpers."""

from __future__ import annotations

import yaml

from integrations.pactown_config import build_pactown_config, write_pactown_config
from parser import parse_dsl

STACK_YAML = """INTENT:
  name: shop-stack
  goal: Shop stack

STACK:
  network: shop-net
  services:
    api-gateway:
      language: python
      framework: fastapi
      port: 8000
      host_port: 18080
      depends_on: [users-service]
      actions:
        - api.expose GET /ping
    users-service:
      language: python
      framework: fastapi
      port: 8000
      actions:
        - api.expose GET /health

EXECUTION:
  mode: transactional
"""


def test_build_pactown_config_stack():
    ir = parse_dsl(STACK_YAML)
    cfg = build_pactown_config(ir, "/tmp/generated")
    assert cfg["name"] == "shop-stack"
    assert "api-gateway" in cfg["services"]
    assert cfg["services"]["api-gateway"]["depends_on"] == [{"name": "users-service"}]
    assert cfg["services"]["api-gateway"]["health_check"] == "/ping"


def test_write_pactown_config(tmp_path):
    ir = parse_dsl(STACK_YAML)
    path = write_pactown_config(ir, tmp_path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data["services"]["users-service"]["readme"] == "services/users-service/README.md"
