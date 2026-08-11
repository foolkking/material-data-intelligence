from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase13/evidence/phase13_2_seven_real_user_e2e_rerun"


def data(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def stable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def test_rerun_preserves_attempt_chain_and_current_baselines() -> None:
    chain = data("attempt_chain.json")
    baseline = data("baseline_verification.json")
    assert chain["attempt1"].startswith("FAILED_HISTORICAL")
    assert chain["remediation"] == "PHASE13_1_FIX_FORWARD_PASS"
    assert chain["attempt2"] == "FAILED_RERUN_PREFLIGHT_REVIEWER_ACTION_REQUIRED"
    assert chain["oldEvidenceReusedAsPass"] == 0
    assert baseline["factModelHash"] == "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
    assert baseline["scopeBaselineHash"] == "caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4"
    assert baseline["scopeDrift"] == 0


def test_runtime_preflight_records_all_seven_and_three_release_defects() -> None:
    preflight = data("runtime_preflight.json")
    findings = data("release_finding_registry.json")
    records = {item["demoId"]: item for item in preflight["records"]}
    assert preflight["freshExecutions"] == 7
    assert len(records) == 7
    assert records["P13-DEMO-03"]["workerStatus"] == "partial_success"
    assert records["P13-DEMO-05"]["workerStatus"] == "partial_success"
    assert records["P13-DEMO-07"]["workerStatus"] == "failed"
    assert findings["releaseCriticalIntegrationDefects"] == 3
    assert {item["findingId"] for item in findings["findings"]} == {"P13-RR-001", "P13-RR-002", "P13-RR-003"}
    assert all(item["status"] == "OPEN_REVIEWER_ACTION_REQUIRED" for item in findings["findings"])


def test_failed_rerun_makes_no_demo_or_acceptance_pass_claim() -> None:
    demos = data("demo_execution_aggregate.json")
    acceptance = data("acceptance_results.json")
    browser = data("browser_matrix.json")
    assert demos["phase13_2DemosExecuted"] == 0
    assert demos["demoPassOrExplicitLimit"] == "0/7"
    assert acceptance["passed"] == 0 and acceptance["status"].startswith("FAILED_RERUN")
    assert browser["mockWorkspaceReleaseAuthority"] is False


def test_no_injection_and_scientific_authority_are_unchanged() -> None:
    injection = data("no_injection_audit.json")
    science = data("scientific_authority_nonchange.json")
    assert injection["status"] == "PASS"
    assert all(value == 0 for key, value in injection.items() if key.startswith("handcrafted"))
    assert science["RegistryBefore"] == science["RegistryAfter"] == 62
    assert science["DataProfile"] == "2.4"
    assert science["scientificBehaviorChanges"] == 0
    assert science["scientificDefects"] == 0


def test_rerun_failure_manifest_is_complete_and_hash_valid() -> None:
    manifest = data("manifest.json")
    assert manifest["missing"] == manifest["hashMismatch"] == manifest["unclassified"] == 0
    assert manifest["phaseStatus"] == "FAILED_RERUN"
    for entry in manifest["entries"]:
        path = EVIDENCE / entry["path"]
        assert path.is_file()
        assert hashlib.sha256(stable_bytes(path)).hexdigest() == entry["sha256"]
