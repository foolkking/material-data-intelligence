from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10m/evidence/phase10m7_workspace_integration_closure"


def _json(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_phase10m7_evidence_manifest_and_required_inventory() -> None:
    required = {
        "baseline.txt", "git_history.txt", "task_state.txt", "entry_gate.md", "acceptance_source_extraction.md",
        "acceptance_reconciliation.md", "acceptance_registry_diff.md", "authority_map.md",
        "identity_continuity.md", "scenario_matrix.md", "api_matrix.md",
        "service_backed_summary.md", "browser_matrix.md", "mobile_metrics.json",
        "accessibility_summary.md", "performance.json", "webgl_lifecycle.json",
        "scientific_integrity.md", "security_summary.md", "known_limitations.md",
        "acceptance_mapping.json", "test_summary.txt", "manifest.json",
    }
    assert required.issubset({item.name for item in EVIDENCE.iterdir()})
    manifest = _json("manifest.json")
    assert manifest["schemaVersion"] == "phase10m7.evidence_manifest.v1"
    entries = manifest["entries"]
    assert entries == sorted(entries, key=lambda item: item["path"])
    actual = {item.relative_to(EVIDENCE).as_posix() for item in EVIDENCE.rglob("*") if item.is_file() and item.name != "manifest.json"}
    assert {item["path"] for item in entries} == actual
    for entry in entries:
        raw = (EVIDENCE / entry["path"]).read_bytes()
        hashed = raw if entry["hashMode"] == "raw_binary" else raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        assert len(raw) == entry["bytes"]
        assert sha256(hashed).hexdigest() == entry["sha256"]


def test_phase10m7_browser_mobile_performance_and_security_closure() -> None:
    closure = _json("browser_closure.json")
    assert all(closure["currentRun"].values())
    assert closure["unexpectedConsoleErrors"] == closure["unexpectedPageErrors"] == 0
    assert closure["unexpectedFailedResponses"] == closure["unapprovedExternalRequests"] == 0
    assert closure["initialHeavyArtifactPayloadRequests"] == 0
    assert closure["inactiveHeavyArtifactPayloadRequests"] == 0
    assert closure["reportPreviewWebglContexts"] == 0
    mobile = _json("mobile_metrics.json")
    assert mobile["viewport"] == [390, 844]
    assert mobile["horizontalOverflow"] == {"body": 0, "root": 0}
    assert mobile["minimumTouchTargetCssPx"] >= 44
    performance = _json("performance.json")
    for marker in (
        "INITIAL_HEAVY_ARTIFACT_PAYLOAD_REQUESTS", "INACTIVE_HEAVY_ARTIFACT_PAYLOAD_REQUESTS",
        "ADJACENT_HEAVY_PANEL_PREFETCH", "STALE_RESPONSE_STATE_COMMITS", "REPORT_PREVIEW_WEBGL_CONTEXTS",
    ):
        assert performance[marker] == 0
    assert performance["MAX_ACTIVE_HEAVY_VIEWERS"] == 1

    security = (EVIDENCE / "security_summary.md").read_text(encoding="utf-8")
    for marker in (
        "NO_WORKSPACE_ARBITRARY_CODE_EXECUTION", "NO_ARTIFACT_JAVASCRIPT_EXECUTION",
        "NO_CROSS_PROJECT_ACCESS", "NO_CROSS_WORKSPACE_ACCESS", "NO_CHECKSUM_BYPASS",
        "NO_RECOVERY_JOB_CREATION", "NO_RECOVERY_QUEUE_AUTHORITY", "NO_PROVIDER_FALLBACK",
        "NO_SECRET_PATTERN_HITS",
    ):
        assert f"{marker} = PASS" in security
    assert "NEW_LLM_CALL_SITES = 0" in security
    assert "M7_NEW_REAL_LLM_CALLS = 0" in security


def test_phase10m7_acceptance_identity_and_sanitization() -> None:
    acceptance = _json("acceptance_mapping.json")
    assert acceptance["expected"] == acceptance["implemented"] == 8
    assert acceptance["missing"] == acceptance["extra"] == 0
    assert acceptance["duplicateCanonicalRegistryEntries"] == 0
    assert acceptance["conflictingDefinitions"] == 0
    assert acceptance["canonicalRegistryShorthandEntries"] == 0
    assert [item["id"] for item in acceptance["items"]] == [f"M7-A0{index}" for index in range(1, 9)]
    identity = (EVIDENCE / "identity_continuity.md").read_text(encoding="utf-8")
    for value in ("deepseek", "plan_f51417c7f8a11af44c512ec7", "job_7fb4e1d2b9db58a02d1e56ac", "0.2"):
        assert value in identity
    evidence_text = "\n".join(
        item.read_text(encoding="utf-8", errors="ignore")
        for item in EVIDENCE.rglob("*")
        if item.is_file() and item.suffix.lower() in {".txt", ".json", ".md"}
    )
    assert "DEEPSEEK_KEY=" not in evidence_text
    assert "Authorization:" not in evidence_text
    assert not re.search(r"[A-Za-z]:\\Users\\", evidence_text)
    assert "/home/runner/" not in evidence_text


def test_phase10m7_screenshots_and_api_routes_are_current() -> None:
    for name in ("chromium_report.png", "firefox_report.png", "webkit_report.png", "mobile_report.png"):
        assert (EVIDENCE / "screenshots" / name).stat().st_size > 10_000
    api = (EVIDENCE / "api_matrix.md").read_text(encoding="utf-8")
    router = (ROOT / "apps/api/mdi_api/main.py").read_text(encoding="utf-8")
    for route in (
        "/planner/intents", "/planner/jobs", "/workspaces/{workspace_id}",
        "/workspaces/{workspace_id}/report-compositions/preview",
        "/workspaces/{workspace_id}/report-compositions/{report_id}/recipe",
    ):
        assert route in api and route in router


def test_phase10m7_document_links_and_phase10n_gate() -> None:
    names = (
        "phase10m7_entry_audit.md", "phase10m7_acceptance_reconciliation.md",
        "phase10m7_integration_scenario_matrix.md", "phase10m7_api_service_closure.md",
        "phase10m7_browser_mobile_accessibility.md", "phase10m7_performance_lifecycle_security.md",
        "phase10m7_acceptance_evidence_map.md", "phase10m_final_capability_matrix.md",
        "phase10m_final_known_limitations.md", "phase10m_completion.md", "phase10n0_next_scope.md",
    )
    phase_root = ROOT / "docs/phase10m"
    readme = (phase_root / "README.md").read_text(encoding="utf-8")
    index = (ROOT / "docs/index.md").read_text(encoding="utf-8")
    for name in names:
        assert (phase_root / name).is_file()
        assert name in readme
        assert f"phase10m/{name}" in index
    next_scope = (phase_root / "phase10n0_next_scope.md").read_text(encoding="utf-8")
    assert "REVIEWER_GATE" in next_scope
    assert "NOT QUEUED" in next_scope
    assert "NOT EXECUTABLE" in next_scope
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    task_count = tasks.count("---TASK---")
    assert task_count == tasks.count("---END---")
    assert task_count in {0, 1}
    if task_count and "Task: Phase 10N-2" in tasks:
        assert "Phase 10N-3:\nREVIEWER_GATE / AWAITING REVIEWER PROMPT" in tasks
    elif task_count and "Phase 10N-1" not in tasks:
        assert "# Phase 10M-7" in tasks
    elif task_count:
        assert "Phase 10N-1 CrystalNN / VoronoiNN Coordination" in tasks
    else:
        assert "# Phase 10M-7" not in tasks
    assert (
        "Phase 10N-2:\nREVIEWER_GATE / AWAITING REVIEWER PROMPT" in tasks
        or "Task: Phase 10N-2" in tasks
        or "Phase 10N-2:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
    )
    task_blocks = re.findall(r"(?ms)^---TASK---\n.*?^---END---$", tasks)
    assert len(task_blocks) == task_count
    assert all(
        "Phase 10N-1 CrystalNN / VoronoiNN Coordination" in block
        or "Phase 10N-2 Local Environment + Coordination Polyhedra" in block
        for block in task_blocks
    )
