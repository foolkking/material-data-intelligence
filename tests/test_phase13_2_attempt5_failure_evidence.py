from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase13/evidence/phase13_2_attempt5_seven_real_user_e2e"


def load(name: str):
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_attempt5_failure_is_honest_and_stops_after_new_p0() -> None:
    aggregate = load("seven_demo_aggregate.json")
    assert aggregate["freshDemosStarted"] == 5
    assert aggregate["fullDemosExecuted"] == 3
    assert aggregate["oldEvidenceReusedAsPass"] == 0
    assert aggregate["statuses"]["P13-DEMO-04"] == "FAIL_PRODUCT_INTEGRATION"
    assert aggregate["statuses"]["P13-DEMO-05"] == "FAIL_PRODUCT_INTEGRATION"
    assert aggregate["statuses"]["P13-DEMO-06"] == "NOT_EXECUTED_AFTER_P0_STOP"


def test_attempt5_findings_preserve_nonchange_boundaries() -> None:
    registry = load("release_finding_registry.json")
    assert registry["releaseCriticalIntegrationDefects"] == 2
    assert registry["scientificDefects"] == registry["securityDefects"] == 0
    assert {item["findingId"] for item in registry["findings"]} == {"P13-R5-001", "P13-R5-002"}
    assert all(item["productionCodeChanged"] is False for item in registry["findings"])


def test_attempt5_successful_fresh_demos_have_ui_report_recipe_pairs() -> None:
    for index in (1, 2, 3):
        assert load(f"demo_{index:02d}/demo_result.json")["status"] == "PASS"
        assert load(f"demo_{index:02d}/report.json")["uiFinalize"] is True
        assert load(f"demo_{index:02d}/recipe.json")["executionAuthorized"] is False
        assert load(f"demo_{index:02d}/durable_source_manifest.json")["identityExact"] is True


def test_attempt5_manifest_covers_every_retained_evidence_file() -> None:
    manifest = load("manifest.json")
    actual = sorted(path.relative_to(EVIDENCE).as_posix() for path in EVIDENCE.rglob("*") if path.is_file() and path.name != "manifest.json")
    recorded = sorted(item["path"] for item in manifest["entries"])
    assert recorded == actual
    assert manifest["missing"] == manifest["hashMismatch"] == 0
