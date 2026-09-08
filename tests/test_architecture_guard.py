from __future__ import annotations

import ast
from pathlib import Path

from scripts.architecture_scan import (
    ImportEdge,
    is_forbidden_edge,
    public_symbols,
    strongly_connected_components,
)
from scripts.check_architecture_boundaries import build_guard_report


def test_canonical_architecture_guard_passes_current_canonical_scope() -> None:
    report = build_guard_report()

    assert report["status"] == "PASS"
    assert report["forbiddenEdges"] == []
    assert any(item["source"].endswith("providers.selection") for item in report["allowlistedEdges"])


def test_guard_rejects_canonical_to_compatibility() -> None:
    finding = is_forbidden_edge(
        ImportEdge(
            "mdi_api.application.projects.ports",
            "mdi_api.compatibility.projects",
            "fixture.py",
            1,
        )
    )

    assert finding == (
        "CANONICAL_TO_COMPATIBILITY",
        "canonical implementation may not import compatibility",
    )


def test_guard_rejects_canonical_to_legacy_facade() -> None:
    finding = is_forbidden_edge(
        ImportEdge(
            "mdi_api.transport.routers.planner",
            "mdi_api.repositories",
            "fixture.py",
            1,
        )
    )

    assert finding == (
        "CANONICAL_TO_COMPATIBILITY",
        "canonical implementation may not import a legacy facade",
    )


def test_guard_rejects_domain_transport_bootstrap_and_infrastructure_edges() -> None:
    cases = (
        ("mdi_api.domain.projects.policy", "mdi_api.routers.projects", "DOMAIN_TO_TRANSPORT"),
        ("mdi_api.domain.projects.policy", "mdi_api.bootstrap.composition", "DOMAIN_TO_BOOTSTRAP"),
        ("mdi_api.domain.projects.policy", "mdi_api.database", "DOMAIN_TO_CONCRETE_INFRASTRUCTURE"),
        ("mdi_api.application.projects.service", "fastapi", "APPLICATION_TO_TRANSPORT"),
        (
            "mdi_api.application.projects.service",
            "mdi_api.database",
            "APPLICATION_TO_CONCRETE_INFRASTRUCTURE",
        ),
    )

    for source, target, rule in cases:
        result = is_forbidden_edge(ImportEdge(source, target, "fixture.py", 1))
        assert result is not None
        assert result[0] == rule


def test_cycle_report_is_empty_for_current_canonical_modules() -> None:
    assert strongly_connected_components(()) == []


def test_public_symbol_census_is_static_and_sorted() -> None:
    path = Path("apps/api/mdi_api/application/projects/ports.py")
    symbols = public_symbols(path)

    assert symbols == sorted(symbols)
    assert "ProjectRepository" in symbols
    ast.parse(path.read_text(encoding="utf-8"))
