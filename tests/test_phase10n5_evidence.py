from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10n/evidence/phase10n5_electronic_band_dos"


def test_n5_acceptance_registry_and_tool_inventory_are_exact() -> None:
    text = (ROOT / "docs/phase10n/phase10n_acceptance_and_test_plan.md").read_text(encoding="utf-8")
    section = text.split("## Canonical Phase 10N-5 Acceptance Registry", 1)[1]
    definitions = re.findall(r"^\| (N5-A\d{2}) \| ([A-Z0-9_]+) \|", section, re.MULTILINE)
    assert [item[0] for item in definitions[:10]] == [f"N5-A{i:02d}" for i in range(1, 11)]
    assert len({item[0] for item in definitions[:10]}) == 10
    registry = load_manifests()
    assert len(registry.tools) == 62
    assert [item.toolId for item in registry.tools if item.toolId.startswith("electronic.")] == ["electronic.band_structure", "electronic.dos"]


def test_n5_evidence_inventory_and_manifest_integrity() -> None:
    required = {"baseline.txt", "entry_gate.md", "electronic_resource_authority_audit.md", "n5_r0_contract_closure.md", "n5_acceptance_registry.md", "n5_decision_traceability.md", "band_contract.md", "band_parameters.json", "band_gap_algorithm.md", "band_reference_results.json", "dos_contract.md", "dos_parameters.json", "dos_reference_results.json", "projection_completeness_cases.json", "band_dos_compatibility_cases.json", "profile_eligibility_cases.json", "planner_cases.json", "plan_cases.json", "runtime_cases.json", "workspace_selection.json", "interpretation.json", "report_recipe.json", "performance.json", "plot_lifecycle.json", "accessibility.md", "security.md", "docs_link_check.txt", "secret_scan.txt", "manifest.json", "electronic_resource_contracts/band.json", "electronic_resource_contracts/dos.json", "artifact_contract_samples/band.json", "artifact_contract_samples/dos.json", "service_backed/status.md", "browser/matrix.json", "screenshots/README.md"}
    assert all((EVIDENCE / path).is_file() for path in required)
    manifest = json.loads((EVIDENCE / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == "phase10n5.evidence_manifest.v1"
    assert manifest["registryCount"] == 62 and manifest["realLlmCalls"] == 0 and manifest["newLlmCallSites"] == 0
    assert "DOCS_LINK_CHECK = PASS" in (EVIDENCE / "docs_link_check.txt").read_text(encoding="utf-8")
    assert "NO_SECRET_PATTERN_HITS = PASS" in (EVIDENCE / "secret_scan.txt").read_text(encoding="utf-8")
    for entry in manifest["entries"]:
        canonical = (EVIDENCE / entry["path"]).read_bytes().replace(b"\r\n", b"\n")
        assert sha256(canonical).hexdigest() == entry["sha256"] and len(canonical) == entry["bytes"]


def test_n5_reference_results_preserve_source_only_boundaries() -> None:
    band = json.loads((EVIDENCE / "band_reference_results.json").read_text(encoding="utf-8"))
    dos = json.loads((EVIDENCE / "dos_reference_results.json").read_text(encoding="utf-8"))
    compatibility = json.loads((EVIDENCE / "band_dos_compatibility_cases.json").read_text(encoding="utf-8"))
    runtime = json.loads((EVIDENCE / "runtime_cases.json").read_text(encoding="utf-8"))
    assert band["gap"]["valueEv"] == 0.6 and band["gap"]["directness"] == "INDIRECT"
    assert dos["totalDos"] and compatibility["compatible"]["valid"] is True
    assert compatibility["sourceMismatch"]["errors"] == ["BAND_DOS_SOURCE_MISMATCH"]
    assert runtime["dft"] is False and runtime["frontendScientificAuthority"] is False


def test_n5_queue_has_one_active_task_and_no_n6_task() -> None:
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    if "Phase 13-1 Reviewer Prompt" in tasks or "Phase 13-2 Reviewer Prompt" in tasks:
        blocks = re.findall(r"---TASK---.*?---END---", tasks, flags=re.DOTALL)
        active = [block for block in blocks if "状态：处理中" in block]
        assert len(blocks) == tasks.count("---TASK---") == tasks.count("---END---")
        assert len(active) <= 1 and (not active or active[0] == blocks[0])
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
    else:
        assert tasks.count("---TASK---") == 0
        assert "Phase 10N-5:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
    assert tasks.count("Task: Phase 10N-6") + tasks.count("任务：Phase 10N-6") <= 1
