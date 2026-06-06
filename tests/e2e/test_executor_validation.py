"""Executor endpoint validation helpers."""

from executor.runner import _filter_validation_endpoints


def test_filter_validation_endpoints_skips_bare_root_when_routes_exist():
    endpoints = [
        "http://localhost:18081",
        "http://localhost:18081/ping",
        "http://localhost:18081/users",
    ]
    filtered = _filter_validation_endpoints(endpoints)
    assert "http://localhost:18081" not in filtered
    assert "http://localhost:18081/ping" in filtered
    assert "http://localhost:18081/users" in filtered


def test_filter_validation_endpoints_keeps_root_when_only_base():
    endpoints = ["http://localhost:8000"]
    assert _filter_validation_endpoints(endpoints) == endpoints
