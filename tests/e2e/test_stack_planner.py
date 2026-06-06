"""Tests for multi-service STACK planning."""

from pathlib import Path

import yaml

from parser import parse_dsl
from planner.plan import plan_intent
from planner.stack_artifacts import write_stack_artifacts

SHOP_STACK = """
INTENT:
  name: shop-stack
  goal: Shop with gateway, users, and catalog

STACK:
  network: shop-net
  services:
    api-gateway:
      language: python
      framework: fastapi
      port: 8000
      host_port: 28080
      depends_on: [users-service, catalog-service]
      actions:
        - api.expose GET /ping
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
        - api.expose GET /products

EXECUTION:
  mode: transactional
"""


def test_parse_stack_ir():
    ir = parse_dsl(SHOP_STACK)
    assert ir.stack is not None
    assert len(ir.stack.services) == 3
    names = {s.name for s in ir.stack.services}
    assert names == {"api-gateway", "users-service", "catalog-service"}


def test_plan_stack_compose_and_services():
    ir = parse_dsl(SHOP_STACK)
    result = plan_intent(ir)
    assert result.compose_yaml
    assert "api-gateway" in result.compose_yaml
    assert "users-service" in result.compose_yaml
    assert "28080:8000" in result.compose_yaml
    assert "api-gateway" in result.service_artifacts
    assert "users-service" in result.service_artifacts
    assert "catalog-service" in result.service_artifacts
    assert "httpx" in result.service_artifacts["api-gateway"]["dockerfile"]


def test_write_stack_artifacts(tmp_path: Path):
    ir = parse_dsl(SHOP_STACK)
    result = plan_intent(ir)
    written = write_stack_artifacts(tmp_path, ir, result)
    assert (tmp_path / "docker-compose.yaml").is_file()
    assert (tmp_path / "services/api-gateway/Dockerfile").is_file()
    assert (tmp_path / "services/api-gateway/app.py").is_file()
    assert (tmp_path / "services/catalog-service/app.js").is_file()
    assert "docker-compose.yaml" in written


def test_intract_parse_stack_actions():
    from generator.intract_manifest import parse_api_actions

    data = yaml.safe_load(SHOP_STACK)
    actions = parse_api_actions(data)
    paths = {p for _m, p in actions}
    assert "/ping" in paths
    assert "/users" in paths
    assert "/products" in paths
