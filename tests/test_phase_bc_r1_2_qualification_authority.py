from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import zipfile

import pytest


pytestmark = pytest.mark.qualification


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from mdi_material_parsers import parse_file  # noqa: E402
from validate_phase_bc_r1_qualification_authority import validate_package  # noqa: E402


INPUTS = ROOT / "_qualification" / "inputs"
R11 = INPUTS / "Phase_BC_R1_1_Qualification_Authority_Reconciled.zip"
R12 = INPUTS / "Phase_BC_R1_2_Qualification_Authority_Reconciled.zip"
R11_SHA256 = "bf1198f0281119af6b0485518ace053d99e827d0ed3d31d077ddf94ed8d4f87f"
PACKAGE = ROOT / "_qualification" / "work" / "phase_bc_r1_2" / "package"
EVIDENCE = ROOT / "_qualification" / "evidence" / "phase_d_r2_1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def case_dir(root: Path, case_id: str) -> Path:
    return next(root.glob(f"*_{case_id}/CASE.json")).parent


def test_r12_is_deterministic_distinct_and_preserves_r11() -> None:
    verification = load_json(EVIDENCE / "R1_2_PACKAGE_VERIFICATION.json")
    assert sha256(R11) == R11_SHA256
    assert sha256(R12) == verification["sha256"]
    assert verification["sha256"] != R11_SHA256
    assert verification["deterministicBuild1Sha256"] == verification["deterministicBuild2Sha256"]
    assert verification["entriesSorted"] is True
    assert verification["rootHashMismatches"] == 0
    assert verification["caseHashMismatches"] == 0
    assert verification["missingFiles"] == 0


def test_r12_is_historical_after_current_authority_supersession() -> None:
    result = validate_package(PACKAGE)
    assert result["status"] == "FAIL"
    assert result["caseCount"] == 16
    assert result["issueCounts"] == {"REPOSITORY_AUTHORITY_FINGERPRINT_DRIFT": 1}
    assert result["issues"][0]["caseId"] == "PACKAGE"
    audit = load_json(EVIDENCE / "ALL_CASE_ENTRY_PATH_AUDIT.json")
    assert audit["caseCount"] == 16
    assert audit["allPrimaryCaseEntryPathsExecutionCompatible"] is True
    assert all(case["executionCompatible"] for case in audit["cases"])


def test_r11_xrd_is_rejected_by_current_cuka_validator() -> None:
    historical = ROOT / "_qualification" / "work" / "phase_bc_r1_1" / "package"
    result = validate_package(historical)
    assert result["status"] == "FAIL"
    assert result["issueCounts"]["XRD_WAVELENGTH_INCOMPATIBILITY"] == 1


def test_qxrd_uses_real_cuka_resource_without_old_value_transformation() -> None:
    directory = case_dir(PACKAGE, "Q-XRD-001")
    case = load_json(directory / "CASE.json")
    resource = load_json(directory / "UPLOAD_experimental_xrd.json")
    provenance = load_json(directory / "PROVENANCE.json")
    assert case["xrdAuthority"] == {
        "arbitraryWavelengthSupport": False,
        "experimentalWavelengthAngstrom": 1.54184,
        "radiation": "CuKa",
        "theoreticalTool": "structure.xrd@0.1.0",
        "theoreticalWavelengthAngstrom": 1.54184,
        "wavelengthGuessingAuthorized": False,
        "wavelengthMatchRequired": True,
        "wavelengthReprojectionAuthorized": False,
    }
    assert resource["wavelength"] == {"unit": "angstrom", "value": 1.54184}
    assert len(resource["twoTheta"]) == len(resource["intensity"]) == 1493
    assert provenance["scientificFreeze"] == {
        "old19373DataRelabeled": 0,
        "oldXrdIntensitySyntheticTransformation": 0,
        "oldXrdTwoThetaReprojected": 0,
        "unitGuesses": 0,
        "wavelengthReprojection": 0,
    }
    parsed = parse_file(directory / "UPLOAD_experimental_xrd.json", dataset_id="dataset_r12_xrd")
    assert parsed.parse_status == "success"
    assert parsed.objects[0].metadata["experimentalXrd"]["wavelength"]["value"] == 1.54184


def test_fifteen_unrevised_case_directories_are_byte_identical() -> None:
    r11_root = ROOT / "_qualification" / "work" / "phase_bc_r1_2" / "historical_r1_1_source"
    old_cases = {load_json(path)["caseId"]: path.parent for path in r11_root.glob("*/CASE.json")}
    new_cases = {load_json(path)["caseId"]: path.parent for path in PACKAGE.glob("*/CASE.json")}
    assert set(old_cases) == set(new_cases)
    for case_id in sorted(set(old_cases) - {"Q-XRD-001"}):
        old_files = {path.relative_to(old_cases[case_id]).as_posix(): path.read_bytes() for path in old_cases[case_id].rglob("*") if path.is_file()}
        new_files = {path.relative_to(new_cases[case_id]).as_posix(): path.read_bytes() for path in new_cases[case_id].rglob("*") if path.is_file()}
        assert old_files == new_files


def test_root_and_case_hash_manifests_have_complete_coverage() -> None:
    roots = [PACKAGE, *[path.parent for path in PACKAGE.glob("*/CASE.json")]]
    for root in roots:
        manifest = root / "SHA256SUMS.txt"
        entries = {}
        for line in manifest.read_text(encoding="utf-8").splitlines():
            expected, relative = line.split("  ", 1)
            assert relative not in entries
            entries[relative] = expected
            assert sha256(root / relative) == expected
        expected_paths = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and path != manifest
        }
        assert set(entries) == expected_paths


def test_package_protected_lineage_and_layout() -> None:
    supersession = load_json(PACKAGE / "PACKAGE_SUPERSESSION.json")
    assert supersession["supersedesPackageSha256"] == R11_SHA256
    assert supersession["historicalPackageMutated"] is False
    with zipfile.ZipFile(R12) as archive:
        assert archive.namelist() == sorted(archive.namelist())
        assert "REPOSITORY_INPUT_TRANSPORT_CONTRACT.json" in archive.namelist()
        assert len(archive.namelist()) == 138
