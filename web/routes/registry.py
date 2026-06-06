"""Registry and service discovery API routes."""

from __future__ import annotations

from fastapi import APIRouter

from web.schemas import RegistryRefreshRequest

router = APIRouter(tags=["registry"])

_service = None


def _get_service():
    global _service
    if _service is None:
        from interfaces.service import IterunService

        _service = IterunService()
    return _service


@router.get("/api/health")
async def health():
    return {"status": "ok", "service": "iterun"}


@router.get("/api/interfaces")
async def list_interfaces():
    return _get_service().interfaces_info()


@router.get("/api/registry")
async def get_registry(workspace: str = "generated"):
    return _get_service().registry_get(workspace)


@router.post("/api/registry/refresh")
async def refresh_registry_api(data: RegistryRefreshRequest):
    return _get_service().registry_refresh(
        data.workspace,
        include_docker=data.include_docker,
    )


@router.get("/api/registry/list")
async def list_registries(pattern: str = "examples/*/generated"):
    return {"registries": _get_service().registry_list(pattern)}
