from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10n/evidence/phase10n3_experimental_xrd_comparison_peak_matching"
DOCS = [ROOT / f"docs/phase10n/{name}" for name in (
    "phase10n_acceptance_and_test_plan.md", "phase10n_implementation_backlog.md",
    "phase10n_execution_lock.md", "phase10n_execution_manifest.md",
)]
EXPECTED = {
    "N3-A01": "BASELINE_THEORETICAL_XRD_AUTHORITY_AND_EXACT_CONTRACT_CLOSURE",
    "N3-A02": "EXPERIMENTAL_XRD_RESOURCE_PROFILE_UNITS_AND_SEMANTIC_VALIDATION",
    "N3-A03": "EXPERIMENTAL_PEAK_DETECTION_AND_DETERMINISTIC_NORMALIZATION",
    "N3-A04": "THEORETICAL_PEAK_BINDING_AND_BOUNDED_ONE_TO_ONE_PEAK_MATCHING",
    "N3-A05": "EXACT_PEAK_IDENTITY_RESIDUALS_COVERAGE_AND_DETERMINISM",
    "N3-A06": "ELIGIBILITY_PLANNER_PLANVALIDATOR_DEPENDENCY_RUNTIME_AND_PERSISTENCE",
    "N3-A07": "WORKSPACE_XRD_OVERLAY_SELECTION_TABLES_AND_INSPECTOR",
    "N3-A08": "GROUNDED_INTERPRETATION_REPORT_RECIPE_AND_SCIENTIFIC_CLAIM_BOUNDARY",
    "N3-A09": "REFERENCES_TOLERANCES_PERFORMANCE_ACCESSIBILITY_SECURITY_AND_SERVICE_EVIDENCE",
    "N3-A10": "THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_N4_REVIEWER_GATE",
}


def test_exact_n3_registry_is_identical_in_four_canonical_docs() -> None:
    for path in DOCS:
        text = path.read_text(encoding="utf-8")
        marker = "## Canonical Phase 10N-3 Acceptance Registry"
        assert text.count(marker) == 1
        section = text.split(marker, 1)[1].split("\n## ", 1)[0]
        entries = re.findall(r"`(N3-A\d{2}) ([A-Z0-9_]+)`", section)
        assert dict(entries) == EXPECTED
        assert len(entries) == len(set(item[0] for item in entries)) == 10
        assert not re.search(r"N3-A\d{2}\s+(?:through|to)\s+N3-A\d{2}", section, re.IGNORECASE)


def test_n3_evidence_manifest_is_complete_hashed_and_inert() -> None:
    manifest = json.loads((EVIDENCE / "manifest.json").read_text(encoding="utf-8"))
    entries = manifest["entries"]
    actual = {item.relative_to(EVIDENCE).as_posix() for item in EVIDENCE.rglob("*") if item.is_file() and item.name != "manifest.json"}
    assert {item["path"] for item in entries} == actual
    assert len(entries) == len(actual) == len({item["path"] for item in entries})
    for entry in entries:
        raw = (EVIDENCE / entry["path"]).read_bytes()
        normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        assert entry["bytes"] == len(raw)
        assert entry["sha256"] == sha256(normalized).hexdigest()
    assert manifest["missingEntries"] == manifest["duplicateEntries"] == manifest["secretEntries"] == 0
    text = "\n".join((EVIDENCE / entry["path"]).read_text(encoding="utf-8", errors="ignore") for entry in entries)
    assert "Authorization:" not in text and "DEEPSEEK_KEY=" not in text
    assert not re.search(r"[A-Za-z]:\\Users\\", text)


def test_n3_ci_registers_browser_and_zero_skip_service_closure() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "--n3-experimental-xrd-only" in workflow
    assert "test_phase10n3_experimental_xrd_service_backed.py" in workflow
    assert "test_phase10n3_postgres_redis_minio_theoretical_xrd_comparison_closure" in workflow
    threshold = re.search(r'if \[ "\$\{PASSED:-0\}" -lt (\d+) \]; then', workflow)
    assert threshold and int(threshold.group(1)) >= 45


def test_n3_task_and_n4_gate_are_exact() -> None:
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    if not tasks.strip():
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
    task_count = tasks.count("---TASK---")
    assert task_count == tasks.count("---END---")
    if task_count == 2 and "Phase 11-2 Reviewer Prompt" in tasks:
        assert "状态：处理中" in tasks
        return
    if task_count == 3 and "Phase 11-1 Reviewer Prompt" in tasks:
        assert "状态：处理中" in tasks
        return
    if task_count and "Task: Phase 11-0" in tasks:
        assert "Phase 10N-3:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
        assert "Phase 10N-4:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
        assert "Phase 10N-5:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
        assert "Phase 10N-6:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
    elif task_count and ("Task: Phase 10N-6" in tasks or "任务：Phase 10N-6" in tasks):
        assert "Phase 10N-3:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
        assert "Phase 10N-4:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
        assert "Phase 10N-5:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
    elif task_count and "Task: Phase 10N-5" in tasks:
        assert "Phase 10N-3:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
        assert "Phase 10N-4:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
    elif task_count and "Task: Phase 10N-4" not in tasks:
        assert task_count in {1, 3}
        assert "Phase 10N-3 Experimental XRD Comparison + Peak Matching" in tasks
    else:
        assert "Phase 10N-3:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
    if task_count and "Task: Phase 11-0" not in tasks and "Task: Phase 10N-5" not in tasks and "Task: Phase 10N-6" not in tasks:
        assert "Task: Phase 10N-4 Trajectory RDF / MSD / Diffusion" in tasks
    else:
        assert "Phase 10N-4:\nREVIEWER_GATE / AWAITING REVIEWER PROMPT" in tasks or "Phase 10N-4:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
