from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10m/evidence/phase10m6_workspace_recovery_closure"
ACCEPTANCE = {
    "M6-A01": "EXPLICIT_WORKSPACE_SAVE_AND_CONCURRENCY",
    "M6-A02": "DETERMINISTIC_RELOAD_AND_LAYOUT_RESTORATION",
    "M6-A03": "DEEP_LINK_REFRESH_AND_HISTORY_NAVIGATION",
    "M6-A04": "JOB_SOURCE_PARTIAL_AND_HISTORICAL_RECOVERY",
    "M6-A05": "REPORT_RECIPE_RECOVERY_AND_DRAFT_HONESTY",
    "M6-A06": "USER_FACING_STATES_LONG_CONTENT_AND_TERMINOLOGY",
    "M6-A07": "RESPONSIVE_MOBILE_AND_ACCESSIBILITY_CLOSURE",
    "M6-A08": "PERFORMANCE_SECURITY_EVIDENCE_AND_VERIFIED_LIFECYCLE",
}


def _json(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_phase10m6_acceptance_browser_and_recovery_invariants() -> None:
    mapping = _json("acceptance_mapping.json")
    assert mapping["expected"] == mapping["implemented"] == 8
    assert mapping["missing"] == mapping["extra"] == mapping["duplicate"] == 0
    assert {item["id"]: item["requirement"] for item in mapping["items"]} == ACCEPTANCE

    matrix = _json("browser_matrix.json")
    assert set(matrix) == {"chromium", "firefox", "webkit"}
    for item in matrix.values():
        assert item["explicitSave"] is item["conflictLocalEditsPreserved"] is True
        assert item["confirmedServerReload"] is item["backForwardRestored"] is True
        assert item["reloadHiddenWrites"] == item["initialArtifactPayloadRequests"] == 0
        assert item["reportPreviewWebglContexts"] == 0
        assert item["finalizedPairReloaded"] is True
        assert item["overflow"] == {"body": 0, "root": 0}
        assert item["consoleErrors"] == item["pageErrors"] == item["failedResponses"] == []
        assert item["externalRequests"] == []
        assert item["browserVersion"]

    mobile = _json("browser_mobile.json")
    assert mobile["viewport"] == [390, 844]
    assert mobile["minTouchTarget"] >= 44
    assert mobile["overflow"] == {"body": 0, "root": 0}
    assert mobile["focusRestored"] is True
    assert mobile["reportPreviewWebglContexts"] == 0

    save = _json("save_api_capture.json")
    assert save["noOpPatchRequests"] == save["noOpRevisionGrowth"] == 0
    conflict = _json("save_conflict_capture.json")
    assert conflict["silentOverwrite"] == conflict["automaticMerge"] == 0
    reload_capture = _json("reload_capture.json")
    assert reload_capture["hiddenWrites"] == 0


def test_phase10m6_manifest_security_and_deepseek_policy() -> None:
    manifest = _json("manifest.json")
    assert manifest["schemaVersion"] == "phase10m6.evidence_manifest.v1"
    entries = manifest["entries"]
    assert entries == sorted(entries, key=lambda item: item["path"])
    actual = {
        item.relative_to(EVIDENCE).as_posix()
        for item in EVIDENCE.rglob("*")
        if item.is_file() and item.name != "manifest.json"
    }
    assert {item["path"] for item in entries} == actual
    for entry in entries:
        raw = (EVIDENCE / entry["path"]).read_bytes()
        hashed = raw if entry["hashMode"] == "raw_binary" else raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        assert len(raw) == entry["bytes"]
        assert sha256(hashed).hexdigest() == entry["sha256"]

    security = (EVIDENCE / "security_summary.md").read_text(encoding="utf-8")
    for marker in (
        "NO_WORKSPACE_RECOVERY_ARBITRARY_CODE_EXECUTION",
        "NO_WORKSPACE_RECOVERY_ARTIFACT_JAVASCRIPT",
        "NO_WORKSPACE_RECOVERY_CROSS_PROJECT_ACCESS",
        "NO_WORKSPACE_RECOVERY_STALE_IDENTITY_REBINDING",
        "NO_WORKSPACE_RECOVERY_CHECKSUM_BYPASS",
        "NO_WORKSPACE_RECOVERY_AUTOMATIC_RERUN",
        "NO_WORKSPACE_RECOVERY_PLAN_CREATION",
        "NO_WORKSPACE_RECOVERY_JOB_CREATION",
        "NO_WORKSPACE_RECOVERY_QUEUE_AUTHORITY",
        "NO_LOCALSTORAGE_CANONICAL_BACKUP",
        "NO_SECRET_PATTERN_HITS",
        "DEEPSEEK_POLICY_REGRESSION",
    ):
        assert f"{marker} = PASS" in security
    assert "NEW_LLM_CALL_SITES = 0" in security
    assert "REAL_LLM_CALLS = 0" in security

    evidence_text = "\n".join(
        item.read_text(encoding="utf-8", errors="ignore")
        for item in EVIDENCE.rglob("*")
        if item.is_file() and item.suffix.lower() in {".txt", ".json", ".md"}
    )
    assert "DEEPSEEK_KEY=" not in evidence_text
    assert "Authorization:" not in evidence_text
    assert not re.search(r"[A-Za-z]:\\Users\\", evidence_text)
    assert "/home/runner/" not in evidence_text


def test_phase10m6_required_inventory_acceptance_authorities_and_screenshots() -> None:
    required = {
        "baseline.txt", "git_history.txt", "task_state.txt", "entry_gate.md",
        "state_ownership_inventory.md", "save_api_capture.json", "save_success_capture.json",
        "save_conflict_capture.json", "revision_cap_capture.json", "reload_capture.json",
        "deep_link_capture.json", "back_forward_capture.json", "running_job_recovery_capture.json",
        "partial_recovery_capture.json", "stale_source_capture.json", "missing_artifact_capture.json",
        "historical_job_capture.json", "report_recipe_recovery_capture.json", "draft_loss_behavior.md",
        "performance.json", "request_cancellation.json", "webgl_lifecycle.json",
        "accessibility_summary.md", "security_summary.md", "network_summary.json",
        "console_summary.json", "browser_matrix.md", "mobile_metrics.json",
        "service_backed_summary.md", "manifest.json",
    }
    assert required.issubset({item.name for item in EVIDENCE.iterdir()})
    for name in ("chromium_report.png", "firefox_report.png", "webkit_report.png", "mobile_report.png"):
        assert (EVIDENCE / "screenshots" / name).stat().st_size > 10_000

    authority_documents = [
        (ROOT / "docs/phase10m/phase10m_implementation_backlog.md").read_text(encoding="utf-8"),
        (ROOT / "docs/phase10m/phase10m_acceptance_and_test_plan.md").read_text(encoding="utf-8"),
        (ROOT / "docs/phase10m/phase10m_execution_manifest.md").read_text(encoding="utf-8"),
    ]
    for acceptance_id, requirement in ACCEPTANCE.items():
        assert all(acceptance_id in document and requirement in document for document in authority_documents)

    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    assert tasks.count("---TASK---") == tasks.count("---END---")
    assert tasks.count("---TASK---") in {0, 1}
    if "# Phase 10M-6" in tasks:
        assert "Phase 10M-6" in tasks
        assert all(acceptance_id in tasks for acceptance_id in ACCEPTANCE)
    elif "Task: Phase 10N-3" in tasks or "任务：Phase 10N-3" in tasks:
        assert "Phase 10N-4:\nREVIEWER_GATE / AWAITING REVIEWER PROMPT" in tasks
    elif "Task: Phase 10N-2" in tasks or "任务：Phase 10N-2" in tasks:
        assert "Phase 10N-3:\nREVIEWER_GATE / AWAITING REVIEWER PROMPT" in tasks
    elif "---TASK---" in tasks and "Phase 10N-1" not in tasks:
        assert "# Phase 10M-7" in tasks
    elif "Phase 10N-1" in tasks:
        assert tasks.count("Phase 10N-1") >= 1
    assert "---TASK---\nPhase 10N" not in tasks


def test_phase10m6_document_links_resolve() -> None:
    referenced = (
        "phase10m6_entry_audit.md", "phase10m6_state_ownership.md",
        "phase10m6_save_and_concurrency.md", "phase10m6_reload_and_layout_restoration.md",
        "phase10m6_deep_link_and_history.md", "phase10m6_job_and_source_recovery.md",
        "phase10m6_report_recipe_recovery.md", "phase10m6_responsive_mobile_accessibility.md",
        "phase10m6_performance_and_lifecycle.md", "phase10m6_security_and_compatibility.md",
        "phase10m6_acceptance_evidence_map.md", "phase10m6_next_scope.md",
    )
    phase_root = ROOT / "docs/phase10m"
    phase_readme = (phase_root / "README.md").read_text(encoding="utf-8")
    docs_index = (ROOT / "docs/index.md").read_text(encoding="utf-8")
    for name in referenced:
        assert (phase_root / name).is_file()
        assert name in phase_readme
        assert f"phase10m/{name}" in docs_index
