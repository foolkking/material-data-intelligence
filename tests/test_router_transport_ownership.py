from __future__ import annotations

import importlib

import pytest


ROUTERS = (
    "agent2",
    "auth",
    "datasets",
    "health",
    "observability",
    "planner",
    "planner_providers",
    "platform_admin",
    "project_history",
    "projects",
    "report_compositions",
    "research",
    "scientific_reports",
    "secrets",
    "secured_planner",
    "secured_runtime",
    "tools",
    "workspaces",
)


@pytest.mark.parametrize("name", ROUTERS)
def test_legacy_router_module_is_canonical_transport_module(name: str) -> None:
    legacy = importlib.import_module(f"mdi_api.routers.{name}")
    canonical = importlib.import_module(f"mdi_api.transport.routers.{name}")

    assert legacy is canonical
