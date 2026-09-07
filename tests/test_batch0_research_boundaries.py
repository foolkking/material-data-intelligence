from __future__ import annotations

import ast
from pathlib import Path

from mdi_api.application.research.ports import ResearchActorContext
from mdi_api.routers.agent2 import _research_actor
from mdi_api.routers.auth import CurrentUser


_ROOT = Path(__file__).resolve().parents[1]
_CANONICAL_RESEARCH_MODULES = (
    "apps/api/mdi_api/research_agent/service.py",
    "apps/api/mdi_api/research_agent/execution/dispatcher.py",
    "apps/api/mdi_api/research_agent/llm/structured_client.py",
    "apps/api/mdi_api/research_agent/orchestration/processor.py",
    "apps/api/mdi_api/research_agent/orchestration/router.py",
    "apps/api/mdi_api/research_agent/planning/planner.py",
    "apps/api/mdi_api/research_agent/planning/processor.py",
)
_FORBIDDEN_PREFIXES = (
    "fastapi",
    "sqlalchemy",
    "mdi_api.config",
    "mdi_api.database",
    "mdi_api.db",
    "mdi_api.routers",
    "mdi_api.unit_of_work",
)


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_canonical_research_application_imports_are_transport_and_infrastructure_neutral():
    violations: dict[str, list[str]] = {}
    for relative_path in _CANONICAL_RESEARCH_MODULES:
        imports = _imports(_ROOT / relative_path)
        forbidden = sorted(
            imported
            for imported in imports
            if imported.startswith(_FORBIDDEN_PREFIXES)
        )
        if forbidden:
            violations[relative_path] = forbidden
    assert violations == {}


def test_http_current_user_is_projected_to_minimal_research_actor_context():
    current_user = CurrentUser(
        id="research-user",
        email="research@example.invalid",
        displayName="Research User",
        roles=["researcher"],
        platformRole="PLATFORM_ADMIN",
    )

    actor = _research_actor(current_user)

    assert actor == ResearchActorContext(id="research-user")
    assert not hasattr(actor, "email")
    assert not hasattr(actor, "roles")
    assert not hasattr(actor, "platformRole")
