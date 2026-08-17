from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import zipfile

from tests.evidence_inventory_contract import assert_readable_evidence_inventory
from tests.task_queue_contract import assert_current_task_queue


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_6_final_archive_presentation"
FINAL = ROOT / "docs/phase13/final"
ARTIFACTS = ROOT / ".artifacts/phase13_6"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_release_candidate_authority_contract_is_readable() -> None:
    seal = load(OUT / "release_candidate_seal.json")
    assert seal["registry"] == 62 and seal["dataProfile"] == "2.4"
    assert seal["analysisIntent"] == seal["eligibilityResolution"] == "1.0"
    assert seal["analysisPlanVersions"] == ["0.1", "0.2"]
    assert seal["migrationHead"] == "0007_phase10m1_workspace_domain"
    assert seal["maxWorkspacePanels"] == 32 and seal["maxLayoutRevisions"] == 128
    assert seal["inputSupport"] == {
        "typedPhononBandImport": "SUPPORTED_WITH_LIMITS",
        "typedPhononDosImport": "SUPPORTED_WITH_LIMITS",
        "genericPhononYamlJson": "MAPPING_ONLY",
    }


def test_phase13_6_recorded_no_production_surface_changes() -> None:
    record = load(OUT / "production_surface_hash_before_after.json")
    assert record["unchanged"] is True and record["productionCodeChanges"] == 0
    assert record["before"]["roots"] == record["after"]["roots"]
    assert record["before"]["fileCount"] == record["after"]["fileCount"] > 200


def test_initial_release_manifest_is_structurally_readable() -> None:
    manifest = load(FINAL / "initial_release_manifest.json")
    assert manifest["schemaVersion"] == "InitialReleaseManifest/1.0"
    assert manifest["releaseStatus"] == "RELEASE_CANDIDATE_ACCEPTED_PENDING_PHASE13_6_LIFECYCLE"
    determinism = load(OUT / "initial_release_manifest_determinism.json")
    assert determinism["status"] == "PASS"
    assert manifest["KnownLimitationIds"] and manifest["Phase13LifecycleRefs"]


def test_claims_limitations_timeline_and_evidence_index_are_complete() -> None:
    claims = load(OUT / "final_claim_matrix.json")
    assert claims["unsupportedClaims"] == 0 and len(claims["claims"]) >= 8
    limits = load(OUT / "known_limitations_final.json")
    assert limits["count"] == 8 and limits["withoutDisclosure"] == limits["newUnapproved"] == 0
    assert set(limits["linkage"].values()) == {f"LIM-{index:03d}" for index in range(1, 9)}
    history = load(OUT / "phase13_forensic_timeline.json")
    assert len(history["records"]) == 19 and history["historyRewritten"] is False
    failed = next(row for row in history["records"] if row["phase"] == "Phase13-4")["failedCandidate"]
    assert failed["sha"] == "34f7cb7cea3db351edff0d3b39ff7fe39cd7e192" and failed["ciRun"] == 31713598663
    index = load(OUT / "final_evidence_index.json")
    assert index["missingEvidenceRootRefs"] == index["brokenEvidenceManifestRefs"] == 0


def test_presentation_assets_exist_and_have_no_science_authority() -> None:
    presentation = load(FINAL / "presentation/presentation_manifest.json")
    provenance = load(OUT / "presentation_screenshot_provenance.json")
    assert len(presentation["slides"]) == 12
    assert presentation["pptx"] == presentation["pdf"] == "NOT_REQUIRED"
    assert presentation["presentationScientificAuthority"] == "NONE"
    assert provenance["assetCount"] == len(provenance["records"]) == 5
    for row in provenance["records"]:
        path = FINAL / "presentation" / row["asset"]
        assert path.is_file() and path.stat().st_size > 0
        assert row["scientificAuthority"] == "NONE"


def test_archive_is_readable_sanitized_and_path_safe() -> None:
    archive = ARTIFACTS / "material-data-intelligence-initial-release.zip"
    if not archive.is_file():
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/generate_phase13_6_final_archive.py")],
            cwd=ROOT,
            check=True,
        )
    determinism = load(OUT / "archive_determinism.json")
    check = load(OUT / "archive_extract_self_check.json")
    assert determinism["status"] == "PASS" and determinism["archiveEntryCount"] > 30
    assert check["status"] == "PASS"
    assert check["manifestMissingFiles"] == check["manifestExtraFiles"] == 0
    assert check["absolutePathHits"] == check["pathTraversalEntries"] == check["symlinks"] == 0
    assert check["brokenInternalLinks"] == 0
    assert check["privatePathHits"] == check["secretPatternHits"] == []
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
        assert package.testzip() is None
    assert names == sorted(names)
    assert all(name.startswith("initial-release/") and ".." not in Path(name).parts for name in names)
    assert all("node_modules" not in name and "/.git/" not in name and "/.venv/" not in name for name in names)


def test_evidence_manifest_and_queue_governance() -> None:
    manifest = load(OUT / "manifest.json")
    paths = assert_readable_evidence_inventory(OUT, manifest)
    assert {"final_closure_decision.json", "failed_candidates.json", "final_evidence_index.json"}.issubset(paths)
    assert_current_task_queue(ROOT)
    decision = load(OUT / "final_closure_decision.json")
    assert decision["overall"] == "PASS_WITH_EXISTING_EXPLICIT_LIMIT"
    assert decision["initialReleaseComplete"] is False
    assert decision["newReleaseCriticalDefects"] == decision["newScientificDefects"] == 0
    failed = load(OUT / "failed_candidates.json")
    assert len(failed["candidates"]) == 2
    assert all(row["rootCause"] and row["failedJob"] for row in failed["candidates"])
    assert failed["candidates"][1]["classification"] == "CI_EVIDENCE_PORTABILITY / SANITIZATION_SELF_MATCH"
