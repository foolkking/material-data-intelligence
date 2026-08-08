from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    ROOT / "docs/phase10n/phase10n_acceptance_and_test_plan.md",
    ROOT / "docs/phase10n/phase10n_implementation_backlog.md",
    ROOT / "docs/phase10n/phase10n_execution_lock.md",
    ROOT / "docs/phase10n/phase10n_execution_manifest.md",
]
EXPECTED = {
    "N2-A01": "BASELINE_N1_AUTHORITY_AND_EXACT_CONTRACT_CLOSURE",
    "N2-A02": "N1_COORDINATION_ARTIFACT_DEPENDENCY_AND_NO_RECOMPUTATION",
    "N2-A03": "LOCAL_ENVIRONMENT_GEOMETRY_CLASSIFICATION",
    "N2-A04": "COORDINATION_POLYHEDRON_GEOMETRY_AND_DISTORTION",
    "N2-A05": "EXACT_SITE_NEIGHBOR_POLYHEDRON_IDENTITY_AND_DETERMINISM",
    "N2-A06": "PROFILE_ELIGIBILITY_PLANNER_PLAN_DEPENDENCY_RUNTIME_AND_PERSISTENCE",
    "N2-A07": "WORKSPACE_STRUCTURE_VIEWER_SELECTION_AND_INSPECTOR_INTEGRATION",
    "N2-A08": "GROUNDED_INTERPRETATION_REPORT_RECIPE_AND_SCIENTIFIC_WORDING",
    "N2-A09": "REFERENCES_TOLERANCES_PERFORMANCE_ACCESSIBILITY_SECURITY_AND_SERVICE_EVIDENCE",
    "N2-A10": "THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_N3_REVIEWER_GATE",
}


def _registry(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    marker = "## Canonical Phase 10N-2 Acceptance Registry"
    assert text.count(marker) == 1
    section = text.split(marker, 1)[1].split("\n## ", 1)[0]
    entries = re.findall(r"`(N2-A\d{2}) ([A-Z0-9_]+)`", section)
    assert len(entries) == len(set(item[0] for item in entries))
    assert not re.search(r"N2-A\d{2}\s+(?:through|to)\s+N2-A\d{2}", section, re.IGNORECASE)
    return dict(entries)


def test_exact_n2_acceptance_registry_is_identical_in_four_canonical_docs() -> None:
    for path in DOCS:
        assert _registry(path) == EXPECTED


def test_n2_r0_scope_is_exact_and_bounded() -> None:
    scope = (ROOT / "docs/phase10n/phase10n2_local_environment_polyhedra_scope.md").read_text(encoding="utf-8")
    for marker in (
        "structure.local_environment_polyhedra@0.1.0",
        "Registry count advances from 55 to 56",
        "phase10n2.local_environment_polyhedra.v1",
        "mdi.angular_spectrum_reference_match@1.0.0",
        "scipy.spatial.ConvexHull",
        "DataProfile remains 2.1",
        "neighbor search, CrystalNN, VoronoiNN or ChemEnv coordination discovery",
        "No dependency, API family, table,",
    ):
        assert marker in scope
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    task_count = tasks.count("---TASK---")
    assert task_count == tasks.count("---END---")
    if task_count:
        assert task_count == 1
        assert "Phase 10N-2 Local Environment + Coordination Polyhedra" in tasks
        assert "Phase 10N-3:\nREVIEWER_GATE / AWAITING REVIEWER PROMPT" in tasks
    else:
        assert "Phase 10N-2:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks


def test_checked_n2_schema_is_strict_single_family_and_exact_n1_bound() -> None:
    schema = json.loads((ROOT / "packages/schemas/json/phase10n2-local-environment-polyhedra.schema.json").read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert schema["properties"]["artifactType"]["const"] == "structure.local_environment_polyhedra"
    assert schema["properties"]["schema_version"]["const"] == "phase10n2.local_environment_polyhedra.v1"
    assert schema["$defs"]["params"]["additionalProperties"] is False
    assert schema["$defs"]["sourceCoordination"]["properties"]["contractVersion"]["enum"] == [
        "phase10n1.crystalnn_coordination.v1",
        "phase10n1.voronoinn_coordination.v1",
    ]
    assert schema["$defs"]["periodicImage"]["minItems"] == schema["$defs"]["periodicImage"]["maxItems"] == 3
