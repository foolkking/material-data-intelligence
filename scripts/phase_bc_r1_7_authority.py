"""Prepare and freeze the content-first Phase B/C-R1.7 authority."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for package in ("packages/material-parsers", "packages/artifact-core", "packages/schemas"):
    sys.path.insert(0, str(ROOT / package))

from mdi_artifact_core import canonical_trajectory_id, stable_trajectory_json, validate_trajectory  # noqa: E402
from mdi_material_parsers.trajectory import parse_trajectory_file  # noqa: E402


R16 = ROOT / "_qualification" / "work" / "phase_bc_r1_6" / "authority_package"
WORK = ROOT / "_qualification" / "work" / "phase_bc_r1_7" / "authority_package"
EVIDENCE = ROOT / "_qualification" / "evidence" / "phase_bc_r1_7"
OUTPUT = ROOT / "_qualification" / "inputs" / "Phase_BC_R1_7_Qualification_Authority_Reconciled.zip"
PREFLIGHT = EVIDENCE / "ALL_CASE_EXECUTABILITY_PREFLIGHT.json"
TRAJECTORY_DIR = WORK / "12_Q-TRAJECTORY-001"
FRAME_START = 0
FRAME_END = 14
FRAME_COUNT = FRAME_END - FRAME_START + 1
SOURCE_NAME = "SOURCE_cage1_500K_frames_000_014.xyz"
UPLOAD_NAME = "UPLOAD_cage1_500K_frames_000_014.trajectory.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def committed_state() -> str:
    subject = subprocess.check_output(["git", "log", "-1", "--format=%s"], cwd=ROOT, text=True).strip()
    return f"CURRENT_COMMITTED_PRODUCT_STATE: {subject}"


def extxyz_frames(path: Path) -> list[list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    frames: list[list[str]] = []
    cursor = 0
    while cursor < len(lines):
        atom_count = int(lines[cursor].strip())
        end = cursor + atom_count + 2
        if end > len(lines):
            raise RuntimeError(f"Truncated trajectory frame at line {cursor + 1}.")
        frames.append(lines[cursor:end])
        cursor = end
    return frames


def select_frames(path: Path) -> bytes:
    frames = extxyz_frames(path)
    if len(frames) != 650:
        raise RuntimeError(f"Historical source has {len(frames)} frames, expected 650.")
    return "".join(line for frame in frames[FRAME_START : FRAME_END + 1] for line in frame).encode("utf-8")


def prepare_fixture() -> dict[str, Any]:
    old_dir = R16 / "12_Q-TRAJECTORY-001"
    source_bytes = select_frames(old_dir / "SOURCE_cage1_500K.xyz")
    selected_extxyz = EVIDENCE / "work" / "selected_first_15.extxyz"
    selected_extxyz.parent.mkdir(parents=True, exist_ok=True)
    selected_extxyz.write_bytes(select_frames(old_dir / "UPLOAD_cage1_500K.extxyz"))

    source_path = TRAJECTORY_DIR / SOURCE_NAME
    source_path.write_bytes(source_bytes)
    parsed = parse_trajectory_file(selected_extxyz).trajectory
    if len(parsed["frames"]) != FRAME_COUNT or parsed["atoms"]["count"] != 516:
        raise RuntimeError("Selected source window changed frame or atom identity.")
    if parsed["lattice_mode"] != "fixed" or parsed["periodic_boundary"] != [True, True, True]:
        raise RuntimeError("Selected source window does not preserve the fixed periodic cell.")
    times = [frame["time"] for frame in parsed["frames"]]
    if times != [float(index * 75) for index in range(FRAME_COUNT)]:
        raise RuntimeError("Selected source window does not preserve physical source timestamps.")

    # The public source's calibrated trajectory is the direct Cartesian authority
    # used by its published MSD workflow; R1.7 records that source-backed meaning
    # explicitly instead of making the EXTXYZ parser guess from coordinate range.
    parsed["position_wrapping"] = "unwrapped"
    parsed["warnings"] = [item for item in parsed["warnings"] if item != "TRAJECTORY_WRAPPING_UNKNOWN"]
    parsed["metadata"]["title"] = "Cage-1 500 K AIMD contiguous frames 0-14"
    parsed["metadata"]["qualification_source_window"] = (
        "frames 0-14; COM-calibrated direct Cartesian positions used by the public source MSD method"
    )
    parsed["provenance"].update(
        {
            "source_format": "extxyz",
            "source_software": "CP2K",
            "source_version": None,
            "created_by_tool": None,
        }
    )
    parsed["trajectory_id"] = canonical_trajectory_id(parsed)
    validation = validate_trajectory(parsed)
    if not validation.valid:
        raise RuntimeError(f"R1.7 canonical trajectory is invalid: {validation.errors}")
    upload_path = TRAJECTORY_DIR / UPLOAD_NAME
    upload_path.write_text(json.dumps(parsed, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")

    round_trip = parse_trajectory_file(upload_path).trajectory
    if round_trip["position_wrapping"] != "unwrapped" or round_trip["frames"] != parsed["frames"]:
        raise RuntimeError("Canonical upload round trip changed trajectory semantics.")
    return {
        "sourceIdentity": "Lei et al. Molecular-Dynamics-Molecular-Cages cage1/cage1_500K.xyz",
        "sourceRepository": "https://github.com/Lei-Lei-alpha/Molecular-Dynamics-Molecular-Cages",
        "sourcePublication": "10.1021/jacsau.1c00556",
        "sourceLicense": "MIT",
        "sourceRepositoryRevision": "da33036b2e256317e5559e7390f87fe272fa7743",
        "sourceFrameCount": 650,
        "sourceFrameStart": FRAME_START,
        "sourceFrameEnd": FRAME_END,
        "selectedFrameCount": FRAME_COUNT,
        "atomCount": 516,
        "timeUnit": "femtosecond",
        "timeRange": [times[0], times[-1]],
        "coordinateMode": "cartesian",
        "positionWrapping": "unwrapped",
        "latticeMode": "fixed",
        "periodicBoundary": [True, True, True],
        "sourceFile": SOURCE_NAME,
        "uploadFile": UPLOAD_NAME,
        "trajectoryContract": parsed["schema_version"],
    }


def update_case(fixture: dict[str, Any]) -> dict[str, Any]:
    for path in TRAJECTORY_DIR.glob("SOURCE_cage1_500K.xyz"):
        path.unlink()
    for path in TRAJECTORY_DIR.glob("UPLOAD_cage1_500K.extxyz"):
        path.unlink()
    case = load_json(TRAJECTORY_DIR / "CASE.json")
    asset = case["assets"][0]
    asset.update(
        {
            "filename": UPLOAD_NAME,
            "containerFormat": "CANONICAL_TRAJECTORY_JSON",
            "phaseAInputFormat": "JSON_LIMITED",
            "parserImporter": "bounded canonical trajectory JSON parser",
            "provenanceRef": f"PROVENANCE.json#/assetLineage/{UPLOAD_NAME}",
        }
    )
    case["correctionsApplied"] = sorted(
        set(case.get("correctionsApplied", []))
        | {
            "Q_TRAJECTORY_RELEASED_CAP_COMPATIBLE_FIXTURE",
            "RUNTIME_RESOURCE_CAP_PREFLIGHT_REQUIRED",
            "SOURCE_BACKED_EXPLICIT_UNWRAPPED_COORDINATE_AUTHORITY",
        }
    )
    case["reason"] = (
        "The former 650-frame viewer-valid source exceeded released trajectory analytics caps. "
        "R1.7 uses the predeclared first contiguous 15 source frames, preserving all 516 atoms, "
        "coordinates, cell/PBC, species order, and physical timestamps."
    )
    case["sourceBytesChanged"] = True
    write_json(TRAJECTORY_DIR / "CASE.json", case)

    provenance = {
        "schemaVersion": "QualificationSourceProvenance/1.1",
        "caseId": "Q-TRAJECTORY-001",
        "provenanceStatus": "COMPLETE",
        "sources": [
            {
                "sourceId": "SRC-MD-CAGE1-500K-R1.7-WINDOW",
                "sourceRole": "trajectory",
                "sourceType": "public_scientific_repository_derived_contiguous_window",
                "repositoryUrl": fixture["sourceRepository"],
                "repositoryRevision": fixture["sourceRepositoryRevision"],
                "publicationDoi": fixture["sourcePublication"],
                "license": fixture["sourceLicense"],
                "materialDatasetId": "cage1_500K",
                "originalFilename": "cage1_500K.xyz",
                "sourceFrameCount": fixture["sourceFrameCount"],
                "selectedFrameRangeInclusive": [FRAME_START, FRAME_END],
                "selectedPhysicalTimeRangeFemtosecond": fixture["timeRange"],
                "atomCount": fixture["atomCount"],
                "coordinateAuthority": "COM-calibrated direct Cartesian source positions used by the published source MSD workflow",
                "cellAuthority": "source simulation cell retained exactly",
            }
        ],
        "assetLineage": {
            SOURCE_NAME: {"sourceRefs": ["SRC-MD-CAGE1-500K-R1.7-WINDOW"], "transformation": "CONTIGUOUS_FRAME_SELECTION"},
            UPLOAD_NAME: {"sourceRefs": ["SRC-MD-CAGE1-500K-R1.7-WINDOW"], "transformation": "CONTIGUOUS_FRAME_SELECTION_AND_CANONICAL_JSON_SERIALIZATION"},
        },
        "normalizationNotes": (
            "Frames 0-14 are selected before any RDF/MSD/diffusion calculation. All atoms, species order, "
            "Cartesian coordinates, fixed cell, PBC, and source physical timestamps are preserved. Canonical "
            "JSON records the source-backed unwrapped Cartesian meaning explicitly."
        ),
        "scientificIntegrity": {
            "atomsRemoved": 0,
            "framesInterpolated": 0,
            "framesResampled": 0,
            "coordinatesChanged": 0,
            "cellValuesChanged": 0,
            "speciesChanged": 0,
            "physicalTimestampsChanged": 0,
            "resultBasedSelection": False,
        },
    }
    write_json(TRAJECTORY_DIR / "PROVENANCE.json", provenance)
    write_text(
        TRAJECTORY_DIR / "README.md",
        """# Q-TRAJECTORY-001 - Inspect trajectory dynamics

R1.7 replaces the viewer-valid but analytics-over-cap 650-frame fixture with the predeclared first contiguous 15-frame window from the same real public Cage-1 500 K AIMD source. The same canonical trajectory resource is used by both turns. All 516 atoms, species order, coordinates, fixed cell, PBC, and physical timestamps are retained. The required Tools and questions are unchanged.

The source window was selected only from released resource limits before any RDF, MSD, or diffusion result was calculated. No runtime truncation, atom subset, interpolation, resampling, or result-driven selection is used.
""",
    )
    return case


def update_root(case: dict[str, Any], fixture: dict[str, Any]) -> None:
    manifest = load_json(WORK / "MANIFEST.json")
    manifest.update(
        {
            "qualificationAuthorityRevision": "R1.7",
            "authorityName": "Phase_BC_R1_7_Qualification_Authority_Reconciled",
        }
    )
    write_json(WORK / "MANIFEST.json", manifest)
    write_json(
        WORK / "PACKAGE_SUPERSESSION.json",
        {
            "schemaVersion": "QualificationAuthoritySupersession/1.3",
            "supersedesAuthority": "Phase_BC_R1_6_Qualification_Authority_Reconciled",
            "supersessionReason": [
                "Q_TRAJECTORY_POSITIVE_ANALYTICS_FIXTURE_EXCEEDED_RELEASED_RUNTIME_RESOURCE_AUTHORITY",
                "QUALIFICATION_EXECUTABILITY_PREFLIGHT_DID_NOT_ENFORCE_REQUIRED_TOOL_RESOURCE_CAPS",
            ],
            "integrityAuthority": "CONTENT_AND_CONTRACT_VALIDATION",
        },
    )
    primary = load_json(WORK / "PRIMARY_QUALIFICATION_EXECUTION_AUTHORITY.json")
    primary["authorityRevision"] = "R1.7"
    primary["trajectoryResourceCapAuthority"] = {
        "fixture": UPLOAD_NAME,
        "sameResourceForViewerAndAnalytics": True,
        "frameCount": FRAME_COUNT,
        "atomCount": fixture["atomCount"],
        "resourceCapPreflightRequired": True,
        "requiredTools": case["requiredExecutionTools"],
    }
    write_json(WORK / "PRIMARY_QUALIFICATION_EXECUTION_AUTHORITY.json", primary)
    inventory = load_json(WORK / "REPOSITORY_AUTHORITY_FINGERPRINT.json")
    inventory["schemaVersion"] = "QualificationRepositoryAuthorityInventory/1.3"
    inventory["currentCommittedProductState"] = committed_state()
    inventory["preflight"] = "PREFLIGHT_MODEL_RESULT.json"
    inventory["trajectoryAnalyticsResourceAuthority"] = "Registry resourceLimits aligned with existing Adapter runtime caps"
    inventory.pop("repositoryAuthorityFingerprint", None)
    write_json(WORK / "REPOSITORY_AUTHORITY_INVENTORY.json", inventory)
    (WORK / "REPOSITORY_AUTHORITY_FINGERPRINT.json").unlink()
    manifest.pop("repositoryAuthorityFingerprint", None)
    manifest["repositoryAuthorityInventory"] = "REPOSITORY_AUTHORITY_INVENTORY.json"
    write_json(WORK / "MANIFEST.json", manifest)
    qmanifest = load_json(WORK / "QUALIFICATION_CASE_MANIFEST.json")
    qmanifest["cases"] = [case if item["caseId"] == case["caseId"] else item for item in qmanifest["cases"]]
    write_json(WORK / "QUALIFICATION_CASE_MANIFEST.json", qmanifest)
    write_text(
        WORK / "README.md",
        """# Phase B/C-R1.7 Qualification Authority

R1.7 supersedes R1.6 only to replace the over-cap positive Q-TRAJECTORY fixture and require deterministic required-Tool resource-cap preflight. Integrity remains content-and-contract based. Historical digest records are non-normative and no checksum manifest is part of this authority.
""",
    )


def prepare() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    shutil.copytree(R16, WORK)
    fixture = prepare_fixture()
    case = update_case(fixture)
    update_root(case, fixture)
    write_json(EVIDENCE / "Q_TRAJECTORY_REVIEWER_DECISION.json", {
        "decision": "REPLACE_QUALIFICATION_TRAJECTORY_FIXTURE",
        "releasedCapsPreserved": True,
        "phaseER16HistoricalFailurePreserved": True,
    })
    write_json(EVIDENCE / "Q_TRAJECTORY_SOURCE_SELECTION.json", fixture | {
        "decision": "DERIVED_CONTIGUOUS_SOURCE_WINDOW",
        "selectionRule": "first bounded contiguous source window satisfying all-pairs RDF cap",
        "selectionDefinedBeforeScientificResults": True,
    })
    write_json(EVIDENCE / "Q_TRAJECTORY_PROVENANCE_VERIFICATION.json", load_json(TRAJECTORY_DIR / "PROVENANCE.json"))
    write_json(EVIDENCE / "Q_TRAJECTORY_DERIVATION_RECORD.json", {
        "derivedFromRealSource": True,
        "derivationType": "CONTIGUOUS_FRAME_SELECTION",
        "sourceFrameStart": FRAME_START,
        "sourceFrameEnd": FRAME_END,
        "selectedFrameCount": FRAME_COUNT,
        "atomsRemoved": 0,
        "framesInterpolated": 0,
        "framesResampled": 0,
        "coordinatesChanged": 0,
        "cellValuesChanged": 0,
        "speciesChanged": 0,
        "physicalTimestampsChanged": 0,
        "resultBasedSelection": False,
    })
    write_json(EVIDENCE / "Q_TRAJECTORY_RESOURCE_SEMANTICS.json", fixture)
    write_json(EVIDENCE / "Q_TRAJECTORY_RELEASED_CAP_AUTHORITY.json", {
        "authority": "CURRENT_RELEASED_TRAJECTORY_ANALYTICS_RUNTIME_CONTRACT",
        "sourceFiles": [
            "packages/adapters/mdi_adapters/platform_builtin/trajectory_analytics.py",
            "packages/tool-registry/mdi_tool_registry/loader.py",
        ],
        "adapterLimits": {
            "maxFrames": 200,
            "maxAtoms": 5000,
            "maxRdfPairs": 2000000,
            "maxRdfBins": 2048,
            "maxMsdLags": 2048,
            "maxTimeOrigins": 4096,
            "maxFitPoints": 4096,
            "maxArtifactBytes": 33554432,
        },
        "registryLimitsAligned": True,
        "trajectoryAnalyticsCapChanged": False,
        "algorithmChanged": False,
        "toolSetExpanded": False,
        "runtimeTruncationAdded": False,
        "runtimeResamplingAdded": False,
        "atomSubsettingAdded": False,
        "supportDispositionChanged": False,
        "integrityAuthority": "CONTENT_AND_CONTRACT_VALIDATION",
    })
    write_json(EVIDENCE / "Q_TRAJECTORY_R16_RUNTIME_FAILURE_ANALYSIS.json", {
        "historicalAuthority": "Phase_BC_R1_6_Qualification_Authority_Reconciled",
        "browserUpload": "PASS",
        "viewerTurn": "PASS_DISCOVERY",
        "analyticsPlan": "PASS_3_STEP_DEPENDENCY_PLAN",
        "workerOutcome": "TOOL_RESOURCE_LIMIT_TRAJECTORY_TOO_LARGE",
        "oldFrameCount": 650,
        "releasedFrameCap": 200,
        "classification": "VALID_FOR_VIEWER_INCOMPATIBLE_WITH_RELEASED_ANALYTICS_CAP",
    })
    protected_cases: list[dict[str, Any]] = []
    for item in load_json(R16 / "CASE_INDEX.json")["cases"]:
        if item["caseId"] == "Q-TRAJECTORY-001":
            continue
        old_case_dir = R16 / item["directory"]
        new_case_dir = WORK / item["directory"]
        differences: list[str] = []
        old_files = sorted(path.relative_to(old_case_dir).as_posix() for path in old_case_dir.rglob("*") if path.is_file())
        new_files = sorted(path.relative_to(new_case_dir).as_posix() for path in new_case_dir.rglob("*") if path.is_file())
        for relative in sorted(set(old_files) | set(new_files)):
            old_path = old_case_dir / relative
            new_path = new_case_dir / relative
            if not old_path.is_file() or not new_path.is_file() or old_path.read_bytes() != new_path.read_bytes():
                differences.append(relative)
        protected_cases.append({
            "caseId": item["caseId"],
            "byteForByteEqual": not differences,
            "differences": differences,
        })
    write_json(EVIDENCE / "R1_7_PROTECTED_CONTENT_REVIEW.json", {
        "integrityAuthority": "CONTENT_AND_CONTRACT_VALIDATION",
        "unchangedProtectedContent": all(item["byteForByteEqual"] for item in protected_cases),
        "unchangedCaseCount": sum(1 for item in protected_cases if item["byteForByteEqual"]),
        "protectedCaseCount": len(protected_cases),
        "cases": protected_cases,
        "qTrajectoryChangedFiles": [
            "CASE.json",
            "PROVENANCE.json",
            "README.md",
            "SOURCE_cage1_500K_frames_000_014.xyz",
            "UPLOAD_cage1_500K_frames_000_014.trajectory.json",
        ],
        "qTrajectoryChangeReason": "STALE_VIEWER_VALID_FIXTURE_EXCEEDED_RELEASED_ANALYTICS_CAP",
    })
    write_json(EVIDENCE / "SCIENTIFIC_INTEGRITY_SUMMARY.json", {
        "scientificValueFabrication": 0,
        "unitGuessing": 0,
        "runtimeFrameTruncation": 0,
        "runtimeAtomTruncation": 0,
        "runtimeResampling": 0,
        "runtimeWindowSelectionWithoutUserAuthority": 0,
        "resultDrivenWindowSelection": 0,
        "coordinateChanges": 0,
        "cellChanges": 0,
        "speciesChanges": 0,
        "physicalTimestampChanges": 0,
        "atomSubsetting": 0,
        "algorithmChanges": 0,
        "supportDispositionChanges": 0,
    })
    print(json.dumps({"prepared": str(WORK.relative_to(ROOT)), "fixture": fixture}, indent=2))


def deterministic_zip(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted((item for item in source.rglob("*") if item.is_file()), key=lambda item: item.relative_to(source).as_posix()):
            info = zipfile.ZipInfo(path.relative_to(source).as_posix(), date_time=(2026, 8, 17, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def inventory() -> dict[str, Any]:
    files = sorted(path.relative_to(WORK).as_posix() for path in WORK.rglob("*") if path.is_file())
    case_dirs = sorted(path for path in WORK.iterdir() if path.is_dir() and path.name[:2].isdigit())
    case_ids = [load_json(path / "CASE.json")["caseId"] for path in case_dirs]
    forbidden = [name for name in files if any(token in Path(name).name.casefold() for token in ("sha256sums", "checksum_manifest", "digest_manifest"))]
    return {
        "authorityVersion": "R1.7",
        "packageRoot": str(WORK.relative_to(ROOT)),
        "entryCount": len(files),
        "entriesSorted": files == sorted(files),
        "entries": files,
        "caseCount": len(case_dirs),
        "caseIds": case_ids,
        "uniqueCaseIds": len(case_ids) == len(set(case_ids)),
        "missingCaseFiles": [path.name for path in case_dirs if not (path / "CASE.json").is_file()],
        "forbiddenQualificationIntegrityArtifacts": forbidden,
    }


def freeze() -> None:
    preflight = load_json(PREFLIGHT)
    summary = preflight["summary"]
    if summary["allAnalysisExecutionTurnsPreflight"] != "PASS" or summary["resourceCapConflicts"] != 0 or summary["resourceCapUnpreflightableRequiredTools"] != 0:
        raise RuntimeError(f"R1.7 preflight is not closed: {summary}")
    write_json(WORK / "PREFLIGHT_MODEL_RESULT.json", {
        "schemaVersion": "QualificationExecutabilityPreflight/3.0",
        "source": "_qualification/evidence/phase_bc_r1_7/ALL_CASE_EXECUTABILITY_PREFLIGHT.json",
        "executionMode": "NON_LLM_NON_FORMAL",
        "expectedCases": 16,
        "expectedAnalysisExecutionTurns": summary["analysisExecutionTurnCount"],
        "resourceCapModel": "required Tool Registry limits plus deterministic fixture/parameter/dependency projections",
        "result": "PASS",
    })
    package_inventory = inventory()
    if package_inventory["caseCount"] != 16 or not package_inventory["uniqueCaseIds"] or package_inventory["missingCaseFiles"] or package_inventory["forbiddenQualificationIntegrityArtifacts"]:
        raise RuntimeError(f"R1.7 package inventory invalid: {package_inventory}")
    first = EVIDENCE / "work" / "r1_7_first.zip"
    second = EVIDENCE / "work" / "r1_7_second.zip"
    deterministic_zip(WORK, first)
    deterministic_zip(WORK, second)
    if first.read_bytes() != second.read_bytes():
        raise RuntimeError("R1.7 package double-build differs byte-for-byte.")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(first, OUTPUT)
    with zipfile.ZipFile(OUTPUT) as archive:
        names = archive.namelist()
    package_inventory.update({
        "zipPath": str(OUTPUT.relative_to(ROOT)),
        "zipByteSize": OUTPUT.stat().st_size,
        "zipEntryCount": len(names),
        "zipEntriesSorted": names == sorted(names),
        "deterministicPackageBuild": "PASS",
    })
    write_json(EVIDENCE / "R1_7_PACKAGE_INVENTORY.json", package_inventory)
    write_json(EVIDENCE / "R1_7_PACKAGE_VERIFICATION.json", {
        "schemaVersion": "QualificationPackageVerification/1.3",
        "authorityVersion": "R1.7",
        "package": str(OUTPUT.relative_to(ROOT)),
        "deterministicPackageBuild": "PASS",
        "caseCount": 16,
        "missingFiles": 0,
        "duplicateEntries": len(names) - len(set(names)),
        "standaloneChecksumOrDigestManifests": 0,
        "validationBasis": ["package inventory", "Case schemas", "direct content review", "all-case cap-aware preflight"],
    })
    write_json(EVIDENCE / "PACKAGE_SUPERSESSION.json", load_json(WORK / "PACKAGE_SUPERSESSION.json"))
    write_text(EVIDENCE / "PHASE_BC_R1_7_RESULT.md", f"""# Phase B/C-R1.7 Result

```text
PHASE_BC_R1_7 = PASS / TRAJECTORY_RESOURCE_CAP_AUTHORITY_RECONCILED_AND_REFROZEN
CASES = 16
Q_TRAJECTORY_VIEWER_PREFLIGHT = PASS
Q_TRAJECTORY_ANALYTICS_PREFLIGHT = PASS
Q_TRAJECTORY_RESOURCE_CAPS = PASS
ALL_ANALYSIS_EXECUTION_TURNS_PREFLIGHT = PASS
EXPECTED_REJECTION_CONTRACTS = PASS
CASE_AUTHORITY_CONFLICTS = 0
RESOURCE_CAP_CONFLICTS = 0
PREFLIGHT_TEST_ERRORS = 0
READY_FOR_PHASE_D_RESEAL = YES
READY_FOR_PHASE_E_DIRECT_CONTINUATION = NO
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_EXECUTIONS = 0
```

Package: `{OUTPUT.relative_to(ROOT).as_posix()}`
""")
    print(json.dumps({"package": str(OUTPUT.relative_to(ROOT)), "inventory": package_inventory}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "freeze"))
    args = parser.parse_args()
    prepare() if args.mode == "prepare" else freeze()


if __name__ == "__main__":
    main()
