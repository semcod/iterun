"""Tests for registry and integration adapters."""

from __future__ import annotations

import json

import pytest

from integrations.adapters.backstage import BackstageExporter
from integrations.adapters.opentelemetry import OpenTelemetryExporter
from integrations.bridges.pipeline import refresh_registry
from registry.catalog import RegistryCatalog
from registry.discover import discover_workspace

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

STACK_YAML = """INTENT:
  name: shop-stack
  goal: Multi-service shop

STACK:
  services:
    api-gateway:
      language: python
      framework: fastapi
      port: 8000
      host_port: 18080
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


def _seed_workspace(tmp_path, yaml_content: str, *, session: dict | None = None):
    from config import PACKAGE_FILENAME

    (tmp_path / PACKAGE_FILENAME).write_text(yaml_content, encoding="utf-8")
    (tmp_path / "intract.yaml").write_text("require: []\n", encoding="utf-8")
    if session:
        (tmp_path / "session.json").write_text(json.dumps(session), encoding="utf-8")


def test_discover_single_service(tmp_path):
    _seed_workspace(
        tmp_path,
        SIMPLE_YAML,
        session={"success": True, "execution": {"endpoints": ["http://localhost:8000"]}},
    )
    m = discover_workspace(tmp_path)
    assert m.metadata.name == "ping-api"
    assert m.spec["deployment"] == "single"
    assert len(m.spec["services"]) == 1
    assert m.spec["services"][0]["urls"] == ["http://localhost:8000"]
    assert any(a["name"] == "iterun.yaml" for a in m.spec["artifacts"])


def test_discover_stack(tmp_path):
    _seed_workspace(tmp_path, STACK_YAML)
    (tmp_path / "docker-compose.yaml").write_text("services: {}\n", encoding="utf-8")
    (tmp_path / "stack.urls.json").write_text(
        '{"api-gateway": "http://localhost:18081"}',
        encoding="utf-8",
    )
    m = discover_workspace(tmp_path)
    assert m.metadata.is_stack is True
    assert m.spec["deployment"] == "stack"
    gateway = next(s for s in m.spec["services"] if s["name"] == "api-gateway")
    assert gateway["urls"] == ["http://localhost:18081"]


def test_refresh_registry_exports(tmp_path):
    _seed_workspace(tmp_path, SIMPLE_YAML)
    result = refresh_registry(tmp_path, include_docker=False)
    assert (tmp_path / "iterun.registry.json").is_file()
    assert (tmp_path / "catalog").is_dir()
    assert (tmp_path / "otel.resources.json").is_file()
    assert "registry" in result["written"]


def test_backstage_exporter(tmp_path):
    _seed_workspace(tmp_path, STACK_YAML)
    m = discover_workspace(tmp_path)
    written = BackstageExporter().export(m, tmp_path)
    assert "system" in written
    assert (tmp_path / "catalog" / "component-api-gateway.yaml").is_file()


def test_otel_exporter(tmp_path):
    _seed_workspace(tmp_path, SIMPLE_YAML)
    m = discover_workspace(tmp_path)
    written = OpenTelemetryExporter().export(m, tmp_path)
    data = json.loads((tmp_path / "otel.resources.json").read_text(encoding="utf-8"))
    assert data["resources"][0]["resource"]["attributes"]["service.name"] == "ping-api"


def test_catalog_refresh(tmp_path):
    _seed_workspace(tmp_path, SIMPLE_YAML)
    cat = RegistryCatalog(tmp_path)
    path = cat.refresh()
    assert path.name == "iterun.registry.json"
    loaded = cat.load()
    assert loaded is not None
    assert loaded.metadata.name == "ping-api"


@pytest.mark.anyio
async def test_rest_registry_endpoints(tmp_path):
    from httpx import ASGITransport, AsyncClient
    from web.app import app

    _seed_workspace(tmp_path, SIMPLE_YAML)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/registry", params={"workspace": str(tmp_path)})
        assert r.status_code == 200
        assert r.json()["metadata"]["name"] == "ping-api"

        r = await ac.post(
            "/api/registry/refresh",
            json={"workspace": str(tmp_path), "include_docker": False},
        )
        assert r.status_code == 200
        assert "written" in r.json()
