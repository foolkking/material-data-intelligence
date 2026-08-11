from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_1_zero_gap_verification_closure"


def data(name: str):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def stable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def test_phase13_1_authorities_and_zero_gap_reconcile() -> None:
    assert data("fact_model_hash_verification.json")["status"] == "PASS"
    assert data("scope_baseline_hash_verification.json")["status"] == "PASS"
    assert data("phase12_baseline_verification.json")["status"] == "PASS"
    before = data("release_gap_registry_before.json")
    after = data("release_gap_registry_after.json")
    assert before == after
    assert after["releaseBlockers"] == after["releaseCriticalIntegrationGaps"] == after["unclassified"] == 0


def test_all_integration_seams_are_classified_without_gap() -> None:
    matrix = data("integration_seam_matrix.json")
    assert len(matrix["rows"]) >= 30
    assert len({row["seamId"] for row in matrix["rows"]}) == len(matrix["rows"])
    assert {row["status"] for row in matrix["rows"]} <= {"VERIFIED", "VERIFIED_WITH_EXPLICIT_LIMIT", "NOT_APPLICABLE", "GAP_FOUND"}
    assert not [row for row in matrix["rows"] if row["status"] == "GAP_FOUND"]
    assert all(row["implementationPath"] and row["testEvidence"] and row["exactIdentity"] for row in matrix["rows"])


def test_seven_demo_preflight_is_ready_but_not_executed() -> None:
    matrix = data("seven_demo_preflight_matrix.json")
    assert len(matrix["records"]) == matrix["expected"] == 7
    assert matrix["blocked"] == matrix["demosExecuted"] == matrix["passClaims"] == 0
    assert all(row["readiness"] in {"READY_FOR_REAL_USER_E2E", "READY_WITH_EXPLICIT_NONBLOCKING_LIMIT"} for row in matrix["records"])
    assert all(row["blockingReason"] is None and row["executed"] is False and row["passClaim"] is False for row in matrix["records"])


def test_fixture_registry_is_exact_and_release_safe() -> None:
    registry = data("fixture_integrity.json")
    assert registry["expected"] == registry["verified"] == 11
    assert registry["missing"] == registry["checksumMismatch"] == registry["externalDownloads"] == 0
    assert all(row["exists"] and row["actualChecksum"] == row["checksum"] and row["retentionSafe"] for row in registry["records"])


def test_registry_adapter_and_identity_boundaries() -> None:
    registry = data("registry_adapter_matrix.json")
    assert registry["liveRegistryCount"] == 62
    assert registry["registeredAdapterCount"] == 51
    assert registry["mappingOnlyOrUnavailableCount"] == 11
    assert registry["missing"] == 0
    identity = data("stale_identity_matrix.json")
    assert all(identity[key] == 0 for key in ["latestBinding", "fuzzyBinding", "filenameAuthority", "displayLabelAuthority", "arrayPositionAuthority"])


def test_no_injection_or_scientific_authority_mutation() -> None:
    injection = data("no_injection_revalidation.json")
    assert all(value == 0 for key, value in injection.items() if key != "status")
    assert injection["status"] == "PASS"
    science = data("scientific_authority_nonchange.json")
    assert science["RegistryBefore"] == science["RegistryAfter"] == 62
    assert science["DataProfileBefore"] == science["DataProfileAfter"] == "2.4"
    assert science["mutation"] == 0


def test_p13x1_acceptance_and_phase13_2_handoff() -> None:
    acceptance = data("phase13_acceptance_registry.json")
    assert acceptance["expected"] == acceptance["implemented"] == 8
    assert acceptance["missing"] == acceptance["extra"] == acceptance["duplicate"] == acceptance["conflicting"] == 0
    assert [row["acceptanceId"] for row in acceptance["records"]] == [f"P13X1-A{i:02d}" for i in range(1, 9)]
    assert all(row["status"] == "PASS" for row in acceptance["records"])
    handoff = data("phase13_2_entry_handoff.json")
    assert len(handoff["demoIds"]) == 7 and handoff["fixtureRecords"] == 11
    assert handoff["demosExecuted"] == 0 and handoff["executionAuthorized"] is False


def test_manifest_is_complete_and_hash_valid() -> None:
    manifest = data("manifest.json")
    assert manifest["missing"] == manifest["hashMismatch"] == manifest["unclassified"] == 0
    assert manifest["expectedFiles"] == len(manifest["entries"])
    for row in manifest["entries"]:
        path = OUT / row["path"]
        content = stable_bytes(path)
        assert len(content) == row["bytes"]
        assert hashlib.sha256(content).hexdigest() == row["sha256"]
