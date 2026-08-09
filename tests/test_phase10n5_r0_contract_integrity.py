from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def test_n5_r0_acceptance_registry_is_exact() -> None:
    text = (ROOT / "docs/phase10n/phase10n_acceptance_and_test_plan.md").read_text(encoding="utf-8")
    section = text.split("## Canonical Phase 10N-5 Acceptance Registry", 1)[1]
    definitions = re.findall(r"^\| (N5-A\d{2}) \| ([A-Z0-9_]+) \|", section, re.MULTILINE)
    assert [item[0] for item in definitions] == [f"N5-A{i:02d}" for i in range(1, 11)]
    assert len(set(definitions)) == 10
    assert "expected = 10; implemented = 10; missing = 0; extra = 0" in section


def test_n5_r0_exact_authority_and_boundaries_are_frozen() -> None:
    scope = (ROOT / "docs/phase10n/phase10n5_electronic_band_dos_scope.md").read_text(encoding="utf-8")
    lock = (ROOT / "docs/phase10n/phase10n_execution_lock.md").read_text(encoding="utf-8")
    assert "electronic.band_structure@0.1.0" in scope
    assert "electronic.dos@0.1.0" in scope
    assert "there is no combined scientific Artifact" in scope
    assert "pymatgen 2026.5.4" in scope
    assert "DataProfile evolves additively from 2.3 to 2.4" in scope
    assert "Combined Band+DOS Tool/Adapter/scientific-authority count is zero" in lock
    assert "0007_phase10m1_workspace_domain" in lock


def test_n5_r0_required_contract_documents_exist_without_critical_tbd() -> None:
    required = [
        "phase10n5_electronic_resource_contract.md",
        "phase10n5_band_structure_contract.md",
        "phase10n5_band_gap_classification_contract.md",
        "phase10n5_dos_projection_contract.md",
        "phase10n5_identity_units_provenance.md",
        "phase10n5_artifact_contracts.md",
        "phase10n5_registry_profile_planner_integration.md",
        "phase10n5_workspace_selection_interpretation.md",
        "phase10n5_reference_tolerance_evidence.md",
        "phase10n5_performance_security_accessibility.md",
        "phase10n5_acceptance_evidence_map.md",
        "phase10n6_next_scope.md",
    ]
    contents = []
    for name in required:
        path = ROOT / "docs/phase10n" / name
        assert path.is_file(), name
        contents.append(path.read_text(encoding="utf-8"))
    assert not re.search(r"\b(?:TBD|TO BE DETERMINED)\b", "\n".join(contents), re.IGNORECASE)
    next_scope = contents[-1]
    assert "REVIEWER_GATE" in next_scope and "NOT QUEUED" in next_scope and "NOT EXECUTABLE" in next_scope


def test_n5_is_the_only_active_task_and_n6_is_absent() -> None:
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    assert tasks.count("---TASK---") == 1
    assert tasks.count("---END---") == 1
    assert "Task: Phase 10N-5" in tasks
    assert "Status: IN_PROGRESS" in tasks
    assert "Task: Phase 10N-6" not in tasks


def test_n5_ci_requires_browser_and_service_closure() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "--n5-electronic-only" in workflow
    assert "tests/integration/test_phase10n5_electronic_service_backed.py" in workflow
    assert "test_phase10n5_postgres_redis_minio_band_dos_closure" in workflow
    threshold = re.search(r'if \[ "\$\{PASSED:-0\}" -lt (\d+) \]; then', workflow)
    assert threshold and int(threshold.group(1)) >= 47
