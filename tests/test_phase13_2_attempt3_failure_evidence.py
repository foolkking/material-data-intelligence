from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase13/evidence/phase13_2_attempt3_seven_real_user_e2e"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def stable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def test_attempt3_failure_is_fresh_and_stops_at_first_p0() -> None:
    aggregate = load("seven_demo_aggregate.json")
    findings = load("release_finding_registry.json")
    result = load("demo_01_dataset_composition/demo_result.json")
    assert aggregate["freshExecutionStarted"] == 1
    assert aggregate["demosExecuted"] == 0
    assert aggregate["oldEvidenceReusedAsPass"] == 0
    assert result["status"] == "FAIL_PRODUCT_INTEGRATION"
    assert findings["releaseCriticalIntegrationDefects"] == 1
    assert findings["findings"][0]["findingId"] == "P13-R3-001"


def test_attempt3_failure_preserves_authority_and_no_injection() -> None:
    authority = load("current_authorities.json")
    injections = load("no_injection_audit.json")
    scientific = load("scientific_authority_nonchange.json")
    assert authority["factModelHash"] == "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
    assert authority["scopeBaselineHash"] == "eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94"
    assert all(value == 0 for value in injections.values())
    assert scientific["scientificBehaviorChanges"] == 0
    assert scientific["scientificDefects"] == 0


def test_attempt3_resource_gap_is_exact_and_has_no_fallback() -> None:
    audit = load("resource_identity_audit.json")
    job = load("demo_01_dataset_composition/job.json")
    assert audit["sqlDatasetNormalizedExportsPresent"] is False
    assert audit["runtimeResolvedProfile"] is False
    assert audit["latestFallback"] == audit["filenameFallback"] == audit["reparseFallback"] == 0
    assert job["terminalStatus"] == "failed"
    assert "Unknown input ref: profile" in job["error"]


def test_attempt3_manifest_is_complete_and_deterministic() -> None:
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
