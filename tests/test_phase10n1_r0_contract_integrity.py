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
    if "Phase 13-1 Reviewer Prompt" in tasks or "Phase 13-2 Reviewer Prompt" in tasks or "Phase 13-4 Targeted Final Product Polish" in tasks:
        blocks = re.findall(r"---TASK---.*?---END---", tasks, flags=re.DOTALL)
        active = [block for block in blocks if "状态：处理中" in block]
        assert len(blocks) == tasks.count("---TASK---") == tasks.count("---END---")
        assert len(active) <= 1 and (not active or active[0] == blocks[0])
        assert "Task: Phase 13-5" not in tasks
        return
    if not tasks.strip():
        return
    if "Phase 13-0 Reviewer Prompt" in tasks or "Phase 13-0 Reviewer Correction Prompt" in tasks:
        assert tasks.count("---TASK---") == tasks.count("---END---") == 1
        assert "状态：处理中" in tasks or "状态：已完成" in tasks
        assert "Phase 13-1 Reviewer Prompt" not in tasks
        return
    if "Phase 12-6 Reviewer Prompt" in tasks and "Phase 12-5 Reviewer Prompt" not in tasks:
        assert tasks.count("---TASK---") == 1
        assert tasks.count("---TASK---") == tasks.count("---END---")
        assert re.search(r"状态：(待处理|处理中|已完成)", tasks)
        return
    if "Phase 12-5 Reviewer Prompt" in tasks and "Phase 12-4 Reviewer Prompt" not in tasks:
        assert tasks.count("---TASK---") == 2
        assert tasks.count("---TASK---") == tasks.count("---END---")
        first, second = re.findall(r"---TASK---.*?---END---", tasks, flags=re.DOTALL)
        assert "Phase 12-5 Reviewer Prompt" in first and re.search(r"状态：(待处理|处理中|已完成)", first)
        assert "Phase 12-6 Reviewer Prompt" in second and "状态：待处理" in second
        return
    if "Phase 12-4 Reviewer Prompt" in tasks:
        assert tasks.count("---TASK---") == 3
        assert tasks.count("---TASK---") == tasks.count("---END---")
        first, second, third = re.findall(r"---TASK---.*?---END---", tasks, flags=re.DOTALL)
        assert "Phase 12-4 Reviewer Prompt" in first and ("状态：处理中" in first or "状态：已完成" in first)
        assert "Phase 12-5 Reviewer Prompt" in second and "状态：待处理" in second
        assert "Phase 12-6 Reviewer Prompt" in third and "状态：待处理" in third
        return
    if "Phase 12-3 Reviewer Prompt" in tasks and "Phase 12-2 Reviewer Prompt" not in tasks:
        assert tasks.count("---TASK---") == 1 and ("状态：处理中" in tasks or "状态：已完成" in tasks)
        return
    if "Phase 12-2 Reviewer Prompt" in tasks:
        assert tasks.count("---TASK---") == 2 and ("状态：处理中" in tasks or "状态：已完成" in tasks)
        assert "Phase 12-3 Reviewer Prompt" in tasks
        return
    if "Phase 12-0 Current UX Reality Audit" in tasks or "Phase 12-1 Design System 2.0" in tasks:
        assert tasks.count("---TASK---") == 1 and "状态：处理中" in tasks
        return
    if "Phase 11-4 Reviewer Prompt" in tasks:
        assert tasks.count("---TASK---") == 2 and "状态：处理中" in tasks
        assert "Phase 11-5 Reviewer Prompt" in tasks
        return
    if "Phase 11-5 Reviewer Prompt" in tasks:
        assert tasks.count("---TASK---") == 1 and "状态：处理中" in tasks
        return
    if "Phase 11-3 Reviewer Prompt" in tasks:
        assert tasks.count("---TASK---") == 1 and "状态：处理中" in tasks
        return
    assert tasks.count("---TASK---") == tasks.count("---END---")
    assert tasks.count("---TASK---") in {0, 1, 2, 3}
    if tasks.count("---TASK---") == 1:
        assert re.search(r"(?:Task:|任务：) Phase (?:10N-(?:1|2|3|4|5|6)|11-0) ", tasks)
        assert (
            "Status: IN_PROGRESS" in tasks
            or "Status: AUDIT_COMPLETE / AWAITING_IMPLEMENTATION_CI" in tasks
            or "Status: PASS / COMPLETE / AWAITING_QUEUE_ARCHIVE_COMMIT" in tasks
            or "Status: PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI" in tasks
            or "状态：处理中" in tasks
        )
    elif "Phase 11-1 Reviewer Prompt" not in tasks:
        assert "Phase 10N-1" not in tasks
    if "Phase 11-2 Reviewer Prompt" in tasks:
        assert tasks.count("---TASK---") == 2
        assert "状态：处理中" in tasks
        return
    if "Phase 11-1 Reviewer Prompt" in tasks:
        assert tasks.count("---TASK---") == 3
        assert "状态：处理中" in tasks
        return
    assert any(
        marker in tasks
        for marker in (
            "Phase 10N-2:\nREVIEWER_GATE / AWAITING REVIEWER PROMPT",
            "Phase 10N-2:\nIN_PROGRESS / AWAITING_IMPLEMENTATION",
            "Phase 10N-2:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT",
            "Phase 10N-2:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT\n\nPhase 10N-3:",
        )
    )


def test_checked_coordination_schema_is_strict_and_algorithm_specific() -> None:
    schema = json.loads((ROOT / "packages/schemas/json/phase10n1-coordination-contracts.schema.json").read_text(encoding="utf-8"))
    definitions = schema["$defs"]
    assert definitions["crystalnnParams"]["additionalProperties"] is False
    assert definitions["voronoinnParams"]["additionalProperties"] is False
    assert definitions["crystalnnArtifact"]["allOf"][1]["properties"]["artifactType"]["const"] == "structure.coordination_crystalnn"
    assert definitions["voronoinnArtifact"]["allOf"][1]["properties"]["artifactType"]["const"] == "structure.coordination_voronoinn"
    assert definitions["periodicImage"]["minItems"] == definitions["periodicImage"]["maxItems"] == 3
