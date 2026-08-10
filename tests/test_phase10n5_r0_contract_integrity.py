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


def test_n5_queue_state_remains_compatible_through_n6_archive() -> None:
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    if not tasks.strip():
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
    if "Phase 11-2 Reviewer Prompt" in tasks:
        assert tasks.count("---TASK---") == 2
        return
    if "Phase 11-1 Reviewer Prompt" in tasks:
        assert tasks.count("---TASK---") == 3
        return
    if "Task: Phase 11-0" in tasks:
        assert tasks.count("---TASK---") == 1
        assert "Phase 10N-6:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
    elif "Task: Phase 10N-6" in tasks or "任务：Phase 10N-6" in tasks:
        assert tasks.count("---TASK---") == 1
        assert "Phase 10N-5:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
    elif "Task: Phase 10N-5" in tasks:
        assert tasks.count("---TASK---") == 1
        assert (
            "Status: IN_PROGRESS" in tasks
            or "Status: PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI" in tasks
        )
    else:
        assert tasks.count("---TASK---") == 0
        assert "Phase 10N-5:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
        assert (
            "Phase 10N-6:\nREVIEWER_GATE / AWAITING REVIEWER PROMPT" in tasks
            or (
                "Phase 10N-6:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
                and (
                    "Phase 11:\nREVIEWER_GATE / AWAITING REVIEWER PROMPT" in tasks
                    or "Phase 11:\nIN_PROGRESS / GOVERNANCE_SEALED" in tasks
                )
            )
        )
    assert tasks.count("Task: Phase 10N-6") <= 1


def test_n5_ci_requires_browser_and_service_closure() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "--n5-electronic-only" in workflow
    assert "tests/integration/test_phase10n5_electronic_service_backed.py" in workflow
    assert "test_phase10n5_postgres_redis_minio_band_dos_closure" in workflow
    threshold = re.search(r'if \[ "\$\{PASSED:-0\}" -lt (\d+) \]; then', workflow)
    assert threshold and int(threshold.group(1)) >= 47
