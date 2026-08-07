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
    "N1-A01": "BASELINE_AUTHORITY_ACCEPTANCE_AND_EXACT_CONTRACT_CLOSURE",
    "N1-A02": "DATAPROFILE_REGISTRY_PARAMETER_AND_ARTIFACT_CONTRACTS",
    "N1-A03": "CRYSTALNN_COORDINATION_EXECUTION",
    "N1-A04": "VORONOINN_COORDINATION_EXECUTION",
    "N1-A05": "EXACT_STRUCTURE_SITE_NEIGHBOR_PERIODIC_IMAGE_IDENTITY_AND_DETERMINISM",
    "N1-A06": "ELIGIBILITY_PLANNER_PLANVALIDATOR_RUNTIME_PERSISTENCE_AND_NO_FALLBACK",
    "N1-A07": "WORKSPACE_STRUCTURE_VIEWER_SELECTION_AND_INSPECTOR_INTEGRATION",
    "N1-A08": "GROUNDED_INTERPRETATION_REPORT_RECIPE_AND_SCIENTIFIC_WORDING",
    "N1-A09": "REFERENCES_TOLERANCES_PERFORMANCE_ACCESSIBILITY_SECURITY_AND_SERVICE_EVIDENCE",
    "N1-A10": "THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_N2_REVIEWER_GATE",
}


def _registry(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    marker = "## Canonical Phase 10N-1 Acceptance Registry"
    assert text.count(marker) == 1
    section = text.split(marker, 1)[1].split("\n## ", 1)[0]
    entries = re.findall(r"`(N1-A\d{2}) ([A-Z0-9_]+)`", section)
    assert len(entries) == len(set(item[0] for item in entries))
    assert not re.search(r"N1-A\d{2}\s+(?:through|to)\s+N1-A\d{2}", section, re.IGNORECASE)
    return dict(entries)


def test_exact_n1_acceptance_registry_is_identical_in_four_canonical_docs() -> None:
    for path in DOCS:
        assert _registry(path) == EXPECTED


def test_r0_exact_scope_and_queue_admission_are_closed() -> None:
    scope = (ROOT / "docs/phase10n/phase10n1_coordination_scope.md").read_text(encoding="utf-8")
    for marker in (
        "structure.coordination_crystalnn@0.1.0",
        "structure.coordination_voronoinn@0.1.0",
        "pymatgen 2026.5.4",
        "pymatgen-core 2026.5.18",
        "phase10n1.crystalnn_coordination.v1",
        "phase10n1.voronoinn_coordination.v1",
        "profileContractVersion",
        "DataProfile 2.0 remains readable",
        "no comparison Tool",
        "0007_phase10m1_workspace_domain",
    ):
        assert marker in scope
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    assert tasks.count("---TASK---") == tasks.count("---END---")
    assert tasks.count("---TASK---") in {0, 1}
    if tasks.count("---TASK---") == 1:
        assert "Phase 10N-1" in tasks and "Status: IN_PROGRESS" in tasks
    else:
        assert "Phase 10N-1" not in tasks
    assert "Phase 10N-2:\nREVIEWER_GATE / AWAITING REVIEWER PROMPT" in tasks


def test_checked_coordination_schema_is_strict_and_algorithm_specific() -> None:
    schema = json.loads((ROOT / "packages/schemas/json/phase10n1-coordination-contracts.schema.json").read_text(encoding="utf-8"))
    definitions = schema["$defs"]
    assert definitions["crystalnnParams"]["additionalProperties"] is False
    assert definitions["voronoinnParams"]["additionalProperties"] is False
    assert definitions["crystalnnArtifact"]["allOf"][1]["properties"]["artifactType"]["const"] == "structure.coordination_crystalnn"
    assert definitions["voronoinnArtifact"]["allOf"][1]["properties"]["artifactType"]["const"] == "structure.coordination_voronoinn"
    assert definitions["periodicImage"]["minItems"] == definitions["periodicImage"]["maxItems"] == 3
