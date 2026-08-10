from __future__ import annotations

import hashlib
import json
from pathlib import Path

from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase11/evidence/phase11_5_scientific_validation_closure"
TEXT_SUFFIXES = {".json", ".md", ".txt", ".yaml", ".yml"}


def read(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def semantic_sha(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def test_final_closure_baseline_is_sealed() -> None:
    baseline = read("phase11_final_baseline.json")
    registry = load_manifests()
    assert len(registry.tools) == 62
    assert baseline["registryCount"] == 62
    assert baseline["dataProfile"] == "2.4"
    assert baseline["migrationHead"] == "0007_phase10m1_workspace_domain"
    assert baseline["phase11Status"] == "COMPLETE / REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS"
    assert baseline["scientificValidationReleaseCandidate"] == "PASS"
    assert baseline["initialReleaseComplete"] == "NO"
    assert baseline["finalProductReleaseReady"] == "NO"
    assert len(baseline["scientificValidationBaselineHash"]) == 64


def test_final_inputs_and_evidence_counts_are_inherited() -> None:
    handoff = read("phase11_4_handoff_snapshot.json")
    assert handoff["registryRows"] == 62
    assert handoff["inputRows"] == 14
    assert handoff["exampleRows"] == 55
    assert handoff["p0Gaps"] == 0
    assert handoff["v4Promotions"] == 0
    assert handoff["numericCrossPlatformClaims"] == 0
    golden = read("phase11_golden_suite_index.json")
    assert golden["benchmarkCount"] == 12
    assert golden["passCount"] == 8
    assert golden["notApplicableCount"] == 4
    assert golden["failCount"] == 0


def test_acceptance_registry_is_exact() -> None:
    registry = read("acceptance_registry.json")
    assert registry["expected"] == 12
    assert registry["implemented"] == 12
    assert registry["missing"] == 0
    assert registry["extra"] == 0
    assert registry["duplicate"] == 0
    assert registry["conflicting"] == 0
    assert registry["shorthand"] == 0
    assert [entry["id"] for entry in registry["entries"]] == [
        f"P11V5-A{index:02d}" for index in range(1, 13)
    ]
    assert all(entry["status"] == "PASS" for entry in registry["entries"])


def test_final_manifest_is_complete_and_semantically_hashed() -> None:
    manifest = read("manifest.json")
    assert manifest["files"]
    for item in manifest["files"]:
        path = EVIDENCE / item["path"]
        assert path.is_file()
        assert semantic_sha(path) == item["sha256"]


def test_phase12_is_read_only_and_no_new_authority() -> None:
    handoff = read("phase12_scientific_authority_handoff.json")
    assert handoff["readOnly"] is True
    assert handoff["phase12TaskCreated"] is False
    assert read("phase11_remaining_gaps.json")["newGaps"] == 0
    assert read("phase11_reference_registry_index.json")["newSources"] == 0
