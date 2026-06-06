"""Tests for unified API layer (interfaces, SDK, REST helpers)."""

from __future__ import annotations

import pytest

from interfaces.service import IterunService
from sdk import IterunClient

STACK_YAML = """INTENT:
  name: shop-stack
  goal: Multi-service shop API

STACK:
  services:
    api-gateway:
      language: python
      framework: fastapi
      port: 8000
      actions:
        - api.expose GET /ping
    users-service:
      language: python
      framework: fastapi
      port: 8000
      actions:
        - api.expose GET /users

EXECUTION:
  mode: transactional
"""

SIMPLE_YAML = """INTENT:
  name: ping-api
  goal: Ping endpoint

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping

EXECUTION:
  mode: auto
"""


def test_interfaces_info_lists_surfaces():
    info = IterunService.interfaces_info()
    ids = {s["id"] for s in info["surfaces"]}
    assert {"rest", "cli", "sdk", "mcp", "pipeline"} <= ids
    assert "iterun_run_pipeline" in info["mcp_tools"]


def test_validate_yaml_detects_stack():
    svc = IterunService()
    out = svc.validate_yaml(STACK_YAML)
    assert out["valid"] is True
    assert out["is_stack"] is True


def test_plan_yaml_stack_compose(tmp_path):
    svc = IterunService()
    result = svc.plan_yaml(STACK_YAML, output_dir=tmp_path)
    assert result["success"] is True
    assert result["plan"]["is_stack"] is True
    assert "docker-compose.yaml" in result["artifacts"]
    assert (tmp_path / "docker-compose.yaml").exists()


def test_plan_yaml_single_service(tmp_path):
    svc = IterunService()
    result = svc.plan_yaml(SIMPLE_YAML, output_dir=tmp_path)
    assert result["success"] is True
    assert result["plan"]["is_stack"] is False
    assert (tmp_path / "Dockerfile").exists()


def test_sdk_local_interfaces_and_plan():
    client = IterunClient()
    assert client.health()["status"] == "ok"
    plan = client.plan_yaml(SIMPLE_YAML)
    assert plan["success"] is True


@pytest.mark.anyio
async def test_rest_health_and_interfaces():
    from httpx import ASGITransport, AsyncClient
    from web.app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

        r = await ac.get("/api/interfaces")
        assert r.status_code == 200
        assert "mcp_tools" in r.json()

        r = await ac.post(
            "/api/intents/plan-yaml",
            json={"content": SIMPLE_YAML},
        )
        assert r.status_code == 200
        assert r.json()["success"] is True
