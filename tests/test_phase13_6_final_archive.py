from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_6_final_archive_presentation"
FINAL = ROOT / "docs/phase13/final"
ARTIFACTS = ROOT / ".artifacts/phase13_6"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_release_candidate_and_frozen_authorities_are_exact() -> None:
    seal = load(OUT / "release_candidate_seal.json")
    assert seal["entryGitSha"] == "bde200acbe4e0d761d6c7a8338fbe68870fa82d6"
    assert seal["factModelHash"] == "92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a"
    assert seal["scopeBaselineHash"] == "bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba"
    assert seal["phase12ProductBaselineHash"] == "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4"
    assert seal["reproManifestHash"] == "931d6214cb11dbcad628f5b33ea97e043bbfeb54fbccc2f8c87cffebad9537e2"
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


def test_production_surface_is_frozen_and_phase13_6_is_nonproduction() -> None:
    record = load(OUT / "production_surface_hash_before_after.json")
    assert record["before"] == record["after"]
    assert record["unchanged"] is True and record["productionCodeChanges"] == 0
    assert record["before"]["fileCount"] > 200
    assert len(record["before"]["semanticHash"]) == 64


def test_initial_release_manifest_is_pending_and_deterministic() -> None:
    manifest = load(FINAL / "initial_release_manifest.json")
    assert manifest["schemaVersion"] == "InitialReleaseManifest/1.0"
    assert manifest["releaseStatus"] == "RELEASE_CANDIDATE_ACCEPTED_PENDING_PHASE13_6_LIFECYCLE"
    semantic = {key: value for key, value in manifest.items() if key not in {"semanticHash", "generatedAt"}}
    actual = hashlib.sha256(
        json.dumps(semantic, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert manifest["semanticHash"] == actual
    determinism = load(OUT / "initial_release_manifest_determinism.json")
    assert determinism["run1"] == determinism["run2"] == determinism["linux"] == determinism["windows"] == actual


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


def test_presentation_assets_have_exact_provenance_and_no_science_authority() -> None:
    presentation = load(FINAL / "presentation/presentation_manifest.json")
    provenance = load(OUT / "presentation_screenshot_provenance.json")
    assert len(presentation["slides"]) == 12
    assert presentation["pptx"] == presentation["pdf"] == "NOT_REQUIRED"
    assert presentation["presentationScientificAuthority"] == "NONE"
    assert provenance["assetCount"] == len(provenance["records"]) == 5
    for row in provenance["records"]:
        path = FINAL / "presentation" / row["asset"]
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
        assert row["scientificAuthority"] == "NONE"


def test_archive_is_deterministic_sanitized_and_self_verifying() -> None:
    archive = ARTIFACTS / "material-data-intelligence-initial-release.zip"
    if not archive.is_file():
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/generate_phase13_6_final_archive.py")],
            cwd=ROOT,
            check=True,
        )
    determinism = load(OUT / "archive_determinism.json")
    check = load(OUT / "archive_extract_self_check.json")
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == determinism["build1Sha256"] == determinism["build2Sha256"]
    assert determinism["status"] == "PASS" and determinism["archiveEntryCount"] > 30
    assert check["status"] == "PASS"
    assert check["manifestMissingFiles"] == check["manifestExtraFiles"] == 0
    assert check["manifestHashMismatches"] == check["manifestByteSizeMismatches"] == 0
    assert check["privatePathHits"] == check["secretPatternHits"] == []
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
    assert names == sorted(names)
    assert all(name.startswith("initial-release/") and ".." not in Path(name).parts for name in names)
    assert all("node_modules" not in name and "/.git/" not in name and "/.venv/" not in name for name in names)


def test_evidence_manifest_and_queue_governance() -> None:
    manifest = load(OUT / "manifest.json")
    assert manifest["missingFiles"] == manifest["hashMismatches"] == 0
    for row in manifest["entries"]:
        payload = (OUT / row["path"]).read_bytes()
        assert len(payload) == row["bytes"]
        assert hashlib.sha256(payload).hexdigest() == row["sha256"]
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    assert "Phase 13-6 - Final Archive + Presentation Package" in tasks
    assert "## Phase 14" not in tasks
    decision = load(OUT / "final_closure_decision.json")
    assert decision["overall"] == "PASS_WITH_EXISTING_EXPLICIT_LIMIT"
    assert decision["lifecycleStatus"] == "PENDING_IMPLEMENTATION_EXACT_SHA_CI"
    assert decision["initialReleaseComplete"] is False
    failed = load(OUT / "failed_candidates.json")
    assert [row["candidateSha"] for row in failed["candidates"]] == [
        "ad0c98f4e469bb9215cd651ad6ed791527faf01c",
        "f7388b8ef402826d9a0f978c6c43f800449da5f3",
    ]
    assert failed["candidates"][0]["correctedSha"] == "f7388b8ef402826d9a0f978c6c43f800449da5f3"
    assert failed["candidates"][1]["classification"] == "CI_EVIDENCE_PORTABILITY / SANITIZATION_SELF_MATCH"
    assert failed["candidates"][1]["correctedSha"] == "PENDING_CORRECTED_IMPLEMENTATION_COMMIT"
