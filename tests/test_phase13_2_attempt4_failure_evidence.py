from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase13/evidence/phase13_2_attempt4_seven_real_user_e2e"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def stable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def test_attempt4_stops_on_fresh_demo1_product_defects() -> None:
    aggregate = load("seven_demo_aggregate.json")
    result = load("demo_01_dataset_composition/demo_result.json")
    findings = load("release_finding_registry.json")
    assert aggregate["freshExecutionsStarted"] == 1
    assert aggregate["fullDemosExecuted"] == 0
    assert aggregate["oldEvidenceReusedAsPass"] == 0
    assert result["status"] == "FAIL_PRODUCT_INTEGRATION"
    assert result["findingIds"] == ["P13-R4-001", "P13-R4-002"]
    assert findings["releaseCriticalIntegrationDefects"] == 2
    assert {item["findingId"] for item in findings["findings"]} == {
        "P13-R4-001",
        "P13-R4-002",
    }


def test_attempt4_records_exact_capability_and_workspace_failures() -> None:
    plan = load("demo_01_dataset_composition/analysis_plan.json")
    calls = load("demo_01_dataset_composition/tool_calls.json")
    artifacts = load("demo_01_dataset_composition/artifact_manifest.json")
    workspace = load("demo_01_dataset_composition/workspace.json")
    report = load("demo_01_dataset_composition/report.json")
    assert plan["plannedTools"] == ["dataset.materials_explorer"]
    assert calls["missingRequiredTool"] == "dataset.composition_space"
    assert artifacts["missingRequiredType"] == "plotly_json"
    assert workspace["projectedStatus"] == "LEGACY_READ_ONLY"
    assert workspace["readOnly"] is True
    assert report["realUserFinalizeEnabled"] is False
    assert report["diagnosticApiFinalizeExcludedFromPass"] is True


def test_attempt4_preserves_frozen_authority_and_no_injection() -> None:
    authority = load("current_authorities.json")
    hashes = load("hash_verification.json")
    injection = load("no_injection_audit.json")
    assert authority["factModelHash"] == "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
    assert authority["scopeBaselineHash"] == "eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94"
    assert authority["registry"] == 62
    assert hashes["factModelImpact"] == hashes["scopeImpact"] == "NO"
    assert all(value == 0 for value in injection.values())


def test_attempt4_p13x2_and_downstream_are_not_overclaimed() -> None:
    acceptance = load("p13x2_acceptance.json")
    aggregate = load("negative_path_aggregate.json")
    browser = load("browser_matrix.json")
    assert acceptance["acceptance"] == "0/8"
    assert acceptance["passed"] == 0
    assert aggregate["status"] == "NOT_EXECUTED_AFTER_P0_STOP"
    assert all(value == "NOT_EXECUTED_AFTER_P0_STOP" for value in browser.values())


def test_attempt4_manifest_is_complete_and_deterministic() -> None:
    manifest = load("manifest.json")
    assert manifest["missing"] == manifest["hashMismatch"] == manifest["unclassified"] == 0
    listed = {item["path"] for item in manifest["entries"]}
    actual = {
        path.relative_to(EVIDENCE).as_posix()
        for path in EVIDENCE.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    assert listed == actual
    for item in manifest["entries"]:
        content = stable_bytes(EVIDENCE / item["path"])
        assert hashlib.sha256(content).hexdigest() == item["sha256"]
        assert len(content) == item["bytes"]
