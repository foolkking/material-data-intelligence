from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_2_seven_real_user_e2e"


def load(name: str):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def stable(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def test_release_critical_findings_are_preserved_not_fixed() -> None:
    registry = load("release_finding_registry.json")
    assert registry["releaseCriticalIntegrationDefects"] == 3
    assert registry["scientificDefects"] == registry["securityDefects"] == registry["unclassified"] == 0
    assert [item["findingId"] for item in registry["findings"]] == ["P13-RF-001", "P13-RF-002", "P13-RF-003", "P13-RF-004"]
    assert all(item["fixed"] is False for item in registry["findings"])


def test_historical_profile_version_gate_conflict_is_preserved_and_superseded() -> None:
    source = (ROOT / "apps/api/mdi_api/routers/planner.py").read_text(encoding="utf-8")
    assert 'profile.profileContractVersion not in {"2.0", "2.1"}' not in source
    assert "is_supported_data_profile_contract_version(profile.profileContractVersion)" in source
    probe = load("planner_entry_probe.json")["records"]
    by_id = {item["demoId"]: item for item in probe}
    assert by_id["P13-DEMO-04"]["profileContractVersion"] == "2.3"
    assert by_id["P13-DEMO-07"]["profileContractVersion"] == "2.4"
    assert by_id["P13-DEMO-04"]["plannerOutcomes"][0]["errorCode"] == "PROFILE_2_REQUIRED"
    assert by_id["P13-DEMO-07"]["plannerOutcomes"][0]["errorCode"] == "PROFILE_2_REQUIRED"


def test_no_demo_execution_or_injection_is_claimed() -> None:
    assert load("manifest.json")["demosExecuted"] == 0
    injection = load("no_injection_audit.json")
    assert all(value == 0 for key, value in injection.items() if key != "status")
    for directory in sorted(path for path in OUT.iterdir() if path.is_dir()):
        result = json.loads((directory / "demo_result.json").read_text(encoding="utf-8"))
        assert result["demoPassClaim"] is False
        assert result["status"] == "NOT_EXECUTED_DUE_RELEASE_CRITICAL_INTEGRATION_DEFECT"


def test_blocked_acceptance_and_nonexecuted_audits_are_explicit() -> None:
    acceptance = load("acceptance_results.json")
    assert acceptance["expected"] == acceptance["blocked"] == 8
    assert acceptance["passed"] == 0
    assert acceptance["acceptanceIds"] == [f"P13X2-A{index:02d}" for index in range(1, 9)]
    assert load("api_request_response_audit.json")["requests"] == 0
    assert load("cross_project_isolation.json")["newAuthorityClaim"] is False
    summary = (OUT / "test_summary.txt").read_text(encoding="utf-8")
    assert "BACKEND=1339 passed, 50 skipped" in summary
    assert "FRONTEND=455 passed" in summary


def test_blocker_evidence_manifest_is_cross_platform_stable() -> None:
    manifest = load("manifest.json")
    assert manifest["missing"] == manifest["hashMismatch"] == manifest["unclassified"] == 0
    for item in manifest["entries"]:
        content = stable(OUT / item["path"])
        assert len(content) == item["bytes"]
        assert hashlib.sha256(content).hexdigest() == item["sha256"]
