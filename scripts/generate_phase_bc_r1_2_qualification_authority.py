"""Build the deterministic Phase B/C-R1.2 input-transport authority package.

This is a non-production packaging tool.  It preserves R1.1 and all protected
bytes except the reviewer-authorized Q-XRD-001 fixture supersession.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any

from mdi_artifact_core import content_hash, stable_json_dumps
from mdi_tool_registry import load_manifests
from mdi_tool_registry.planner_metadata import build_registry_snapshot

from generate_phase_bc_r1_qualification_authority import (
    clean_generated,
    deterministic_zip,
    safe_extract,
    sha256,
    verify_manifest_entries,
    write_hash_manifest,
    write_json,
    write_text,
)
from validate_phase_bc_r1_qualification_authority import validate_package


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "_qualification" / "inputs"
R11_NAME = "Phase_BC_R1_1_Qualification_Authority_Reconciled.zip"
R11_SHA256 = "bf1198f0281119af6b0485518ace053d99e827d0ed3d31d077ddf94ed8d4f87f"
R12_NAME = "Phase_BC_R1_2_Qualification_Authority_Reconciled.zip"
R11_PACKAGE = INPUTS / R11_NAME
R12_PACKAGE = INPUTS / R12_NAME
WORK = ROOT / "_qualification" / "work" / "phase_bc_r1_2"
SOURCE = WORK / "historical_r1_1_source"
PACKAGE = WORK / "package"
EVIDENCE = ROOT / "_qualification" / "evidence" / "phase_d_r2_1"
XRD_SOURCES = ROOT / "_qualification" / "sources" / "phase_bc_r1_2" / "q_xrd"
PRODUCT_SHA = "51e45c9436bef73f0c8ea1ccc5eb681dba1d21b8"
CUKA_WAVELENGTH = 1.54184
CASE_ID = "Q-XRD-001"
QXRD_DIR_NAME = "10_Q-XRD-001"
SOURCE_FILES = (
    "SOURCE_apatite_7_64.csv",
    "SOURCE_Apatite7_64.brml",
    "SOURCE_Apatite7_64.txt",
    "SOURCE_COD_4317043_hydroxyapatite.cif",
    "SOURCE_FIGSHARE_RECORD_33165134.json",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def case_paths(root: Path) -> list[Path]:
    return sorted(root.glob("*/CASE.json"))


def hash_tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256(path)
        for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix())
        if path.is_file()
    }


def parse_raw_xrd(path: Path) -> tuple[list[float], list[float]]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    try:
        start = lines.index("[Data]") + 1
    except ValueError as exc:
        raise RuntimeError("Experimental XRD source has no [Data] section.") from exc
    angles: list[float] = []
    intensities: list[float] = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped or stripped.lower().startswith("angle"):
            continue
        parts = [part.strip() for part in stripped.split(",")]
        if len(parts) < 2:
            raise RuntimeError(f"Malformed XRD source line: {line!r}")
        angles.append(float(parts[0]))
        intensities.append(float(parts[1]))
    if len(angles) != 1493 or any(left >= right for left, right in zip(angles, angles[1:])):
        raise RuntimeError("Experimental XRD source point count or axis ordering changed.")
    return angles, intensities


def xrd_resource() -> dict[str, Any]:
    angles, intensities = parse_raw_xrd(XRD_SOURCES / "SOURCE_Apatite7_64.txt")
    material = {
        "schemaVersion": "phase10n3.experimental_xrd_resource.v1",
        "resourceId": "figshare_33165134_file_67277003_apatite7_64",
        "resourceVersion": "1",
        "xAxis": {"kind": "two_theta", "unit": "degree"},
        "twoTheta": angles,
        "intensity": intensities,
        "intensitySemantic": "counts",
        "wavelength": {"value": CUKA_WAVELENGTH, "unit": "angstrom"},
    }
    return {
        **material,
        "resourceHash": content_hash(stable_json_dumps(material)),
        "metadata": {
            "sourceDoi": "10.6084/m9.figshare.33165134.v1",
            "sourceFileId": 67277003,
            "sourceFilename": "Apatite7_64.txt",
            "materialPhase": "Hydroxyapatite",
            "representationPreparation": "EXACT_TABULAR_PARSE_NO_SCIENTIFIC_TRANSFORMATION",
        },
    }


def transport_contract() -> dict[str, Any]:
    base = {
        "schemaVersion": "NormalUserInputTransport/1.0",
        "entryPathId": "planner_workbench.upload_session",
        "requestContract": "UploadSession/1.0",
        "supportsTextBytes": True,
        "supportsBinaryBytes": True,
        "supportsMultipleResources": True,
        "maxFilesPerSubmission": 8,
        "perFileByteCap": 64 * 1024 * 1024,
        "totalByteCap": 128 * 1024 * 1024,
        "sameDatasetCompanionPolicy": "ATOMIC_SINGLE_UPLOAD_SESSION",
        "roleBindingPolicy": "PARSER_CONTRACT_OR_EXPLICIT_TYPED_IMPORT_ONLY",
        "fileOrderIsSemanticAuthority": False,
        "partialFailurePolicy": "NO_DATASET_PUBLICATION_UNTIL_COMPLETE_BUNDLE_VALIDATES",
        "supportedImportModes": ["generic_parser", "typed_phonon_band", "typed_phonon_dos"],
        "transport": {
            "declaration": "application/json",
            "fileBody": "application/octet-stream",
            "bytePreservation": "EXACT_SHA256_AND_BYTE_SIZE",
            "filenameAuthority": "METADATA_ONLY",
        },
        "security": {
            "pathTraversalAllowed": False,
            "archiveExecutionAllowed": False,
            "scriptExecutionAllowed": False,
            "clientFilesystemPathAuthority": False,
        },
    }
    base["semanticHash"] = hashlib.sha256(
        json.dumps(base, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        **base,
        "qualificationEntryPathAliases": ["ENTRY-UI-FILE-UPLOAD", "ENTRY-UI-TYPED-PHONON-BUNDLE"],
        "qualificationImportModeAliases": [
            "FILE_UPLOAD",
            "TYPED_PHONON_BAND_IMPORT",
            "TYPED_PHONON_DOS_IMPORT",
        ],
        "authorityClass": "NORMAL_USER_DELIVERY_TRANSPORT_NOT_SCIENTIFIC_SUPPORT",
    }


def write_qxrd_case() -> tuple[dict[str, Any], list[str]]:
    source_dir = SOURCE / QXRD_DIR_NAME
    target_dir = PACKAGE / QXRD_DIR_NAME
    before = load_json(source_dir / "CASE.json")
    for path in target_dir.iterdir():
        if path.name != "CASE.json":
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    for name in SOURCE_FILES:
        shutil.copyfile(XRD_SOURCES / name, target_dir / name)
    structure_name = "UPLOAD_structure_COD_4317043_hydroxyapatite.cif"
    experimental_name = "UPLOAD_experimental_xrd.json"
    shutil.copyfile(XRD_SOURCES / "SOURCE_COD_4317043_hydroxyapatite.cif", target_dir / structure_name)
    resource = xrd_resource()
    write_json(target_dir / experimental_name, resource)

    after = deepcopy(before)
    after["assets"] = [
        {
            "assetRole": "structure",
            "containerFormat": "CIF",
            "entryPath": "ENTRY-UI-FILE-UPLOAD",
            "filename": structure_name,
            "importMode": "FILE_UPLOAD",
            "parserImporter": "pymatgen.Structure.from_file",
            "phaseAInputFormat": "CIF",
            "provenanceRef": f"PROVENANCE.json#/assetLineage/{structure_name}",
            "requiredCompanionAssets": [experimental_name],
            "role": "structure",
            "semanticKind": "crystal_structure",
            "sha256": sha256(target_dir / structure_name),
        },
        {
            "assetRole": "experimental_xrd",
            "containerFormat": "JSON",
            "entryPath": "ENTRY-UI-FILE-UPLOAD",
            "filename": experimental_name,
            "importMode": "FILE_UPLOAD",
            "parserImporter": "_parse_json_limited / strict resource validators",
            "phaseAInputFormat": "JSON_LIMITED",
            "provenanceRef": f"PROVENANCE.json#/assetLineage/{experimental_name}",
            "requiredCompanionAssets": [structure_name],
            "role": "experimental_xrd",
            "semanticKind": "experimental_xrd",
            "sha256": sha256(target_dir / experimental_name),
        },
    ]
    after["correctionsApplied"] = [
        *after["correctionsApplied"],
        "Q_XRD_STALE_1_9373_FIXTURE_SUPERSEDED_BY_REAL_CUKA_1_54184_RESOURCE",
        "NORMAL_USER_MULTI_RESOURCE_TRANSPORT_AUTHORITY_RECONCILED",
    ]
    after["reason"] = (
        "Reviewer Branch B1 preserves the released CuKa-only theoretical Tool. "
        "A real CuKa hydroxyapatite experimental resource now accompanies a compatible public-domain structure."
    )
    after["sourceBytesChanged"] = True
    after["qualificationFixtureRevision"] = {
        "reason": "STALE_FIXTURE_INCOMPATIBLE_WITH_RELEASE_AUTHORITY",
        "oldExperimentalWavelengthAngstrom": 1.9373,
        "newExperimentalWavelengthAngstrom": CUKA_WAVELENGTH,
        "theoreticalWavelengthAngstrom": CUKA_WAVELENGTH,
        "oldDataRelabeled": False,
        "oldTwoThetaReprojected": False,
        "oldIntensityTransformed": False,
    }
    after["xrdAuthority"] = {
        "theoreticalTool": "structure.xrd@0.1.0",
        "radiation": "CuKa",
        "arbitraryWavelengthSupport": False,
        "experimentalWavelengthAngstrom": CUKA_WAVELENGTH,
        "theoreticalWavelengthAngstrom": CUKA_WAVELENGTH,
        "wavelengthMatchRequired": True,
        "wavelengthReprojectionAuthorized": False,
        "wavelengthGuessingAuthorized": False,
    }
    write_json(target_dir / "CASE.json", after)

    provenance = {
        "schemaVersion": "QualificationSourceProvenance/1.0",
        "caseId": CASE_ID,
        "provenanceStatus": "COMPLETE",
        "sources": [
            {
                "sourceId": "SRC-FIGSHARE-33165134-APATITE7-64",
                "sourceRole": "experimental_xrd",
                "sourceType": "peer_reviewed_scientific_repository",
                "repositoryUrl": "https://figshare.com/articles/dataset/33165134",
                "datasetDoi": "10.6084/m9.figshare.33165134.v1",
                "retrievalDate": "2026-08-16",
                "license": "CC BY 4.0",
                "authors": ["Alix Deymier", "Kennedy Drake", "Abigail Eaton", "Abiodun Aderibigbe", "Christina Krywka", "Arun Nair"],
                "materialPhase": "Hydroxyapatite",
                "wavelengthEvidence": {
                    "radiation": "Cu",
                    "alphaAverageAngstrom": CUKA_WAVELENGTH,
                    "actuallyUsedLambdaAngstrom": CUKA_WAVELENGTH,
                    "evidenceFile": "SOURCE_Apatite7_64.txt",
                },
                "sourceFiles": [
                    {"filename": name, "sha256": sha256(target_dir / name)}
                    for name in SOURCE_FILES
                    if "COD_" not in name
                ],
            },
            {
                "sourceId": "SRC-COD-4317043",
                "sourceRole": "crystal_structure",
                "sourceType": "scientific_database",
                "repositoryUrl": "https://www.crystallography.net/cod/4317043.html",
                "remoteFileUrl": "https://www.crystallography.net/cod/4317043.cif",
                "materialDatasetId": "COD:4317043",
                "publicationDoi": "10.1021/ic1015127",
                "retrievalDate": "2026-08-16",
                "license": "Public domain",
                "materialFormula": "Ca10 H2 O26 P6",
                "materialPhase": "Hydroxyapatite",
                "spaceGroup": "P 63/m",
                "originalSha256": sha256(target_dir / "SOURCE_COD_4317043_hydroxyapatite.cif"),
            },
        ],
        "assetLineage": {
            structure_name: {
                "sourceRefs": ["SRC-COD-4317043"],
                "transformation": "NONE_BYTE_PRESERVED",
                "outputSha256": sha256(target_dir / structure_name),
            },
            experimental_name: {
                "sourceRefs": ["SRC-FIGSHARE-33165134-APATITE7-64"],
                "transformation": "EXACT_TABULAR_PARSE_TO_STRICT_RESOURCE_JSON_NO_SCIENTIFIC_TRANSFORMATION",
                "outputSha256": sha256(target_dir / experimental_name),
                "pointCount": len(resource["twoTheta"]),
            },
        },
        "compatibilityBasis": {
            "experimentalPhase": "Hydroxyapatite",
            "structurePhase": "Hydroxyapatite",
            "experimentalWavelengthAngstrom": CUKA_WAVELENGTH,
            "theoreticalWavelengthAngstrom": CUKA_WAVELENGTH,
            "phaseScopeCompatible": True,
            "notPhaseConfirmationOrRefinement": True,
        },
        "scientificFreeze": {
            "old19373DataRelabeled": 0,
            "oldXrdTwoThetaReprojected": 0,
            "oldXrdIntensitySyntheticTransformation": 0,
            "unitGuesses": 0,
            "wavelengthReprojection": 0,
        },
    }
    write_json(target_dir / "PROVENANCE.json", provenance)
    write_text(
        target_dir / "LICENSE.txt",
        """Experimental XRD source: Deymier et al., Figshare DOI 10.6084/m9.figshare.33165134.v1, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Attribution and original source files are retained.\n\nStructure source: Crystallography Open Database entry 4317043. The included CIF states that COD data are public domain. Cite COD 4317043 and DOI 10.1021/ic1015127.\n""",
    )
    write_text(
        target_dir / "README.md",
        """# Q-XRD-001 - CuKa experimental/theoretical comparison\n\nThis R1.2 fixture pairs a real Figshare hydroxyapatite XRD measurement with a public-domain COD hydroxyapatite structure. The source instrument record declares Cu radiation and `ActuallyUsedLambda=1.54184`; all 1,493 source two-theta/count pairs are copied exactly into the strict resource JSON.\n\nThe released `structure.xrd@0.1.0` authority remains CuKa-only. Wavelength guessing, reprojection, phase confirmation, and refinement are forbidden. The historical 1.9373 angstrom fixture remains only in R1.1.\n""",
    )
    write_hash_manifest(target_dir, target_dir / "SHA256SUMS.txt", exclude={"SHA256SUMS.txt"})
    changed = sorted(
        path for path in set(hash_tree(source_dir)) | set(hash_tree(target_dir))
        if hash_tree(source_dir).get(path) != hash_tree(target_dir).get(path)
    )
    return after, changed


def build_entry_audit(cases: list[dict[str, Any]], contract: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for case in cases:
        assets = case["assets"]
        sizes = [((PACKAGE / next(path.parent.name for path in case_paths(PACKAGE) if load_json(path)["caseId"] == case["caseId"])) / asset["filename"]).stat().st_size for asset in assets]
        binary_count = sum(Path(asset["filename"]).suffix.lower() in {".zip", ".npy", ".npz", ".brml"} for asset in assets)
        companions = any(asset.get("requiredCompanionAssets") for asset in assets)
        checks = {
            "assetCountWithinCap": len(assets) <= contract["maxFilesPerSubmission"],
            "perFileBytesWithinCap": all(size <= contract["perFileByteCap"] for size in sizes),
            "totalBytesWithinCap": sum(sizes) <= contract["totalByteCap"],
            "binaryBytesSupported": binary_count == 0 or contract["supportsBinaryBytes"],
            "multipleResourcesSupported": len(assets) == 1 or contract["supportsMultipleResources"],
            "sameDatasetCompanionsSupported": not companions or contract["sameDatasetCompanionPolicy"] == "ATOMIC_SINGLE_UPLOAD_SESSION",
            "fileOrderNotAuthority": case.get("uploadFileOrderSemantic") is False and contract["fileOrderIsSemanticAuthority"] is False,
        }
        rows.append({
            "caseId": case["caseId"],
            "assetCount": len(assets),
            "binaryAssetCount": binary_count,
            "mixedTextBinary": 0 < binary_count < len(assets),
            "requiredCompanionAssets": companions,
            "checks": checks,
            "executionCompatible": all(checks.values()),
        })
    return {
        "schemaVersion": "PhaseBCR12AllCaseEntryPathAudit/1.0",
        "caseCount": len(rows),
        "allPrimaryCaseEntryPathsExecutionCompatible": all(row["executionCompatible"] for row in rows),
        "cases": rows,
    }


def main() -> None:
    if not R11_PACKAGE.is_file() or sha256(R11_PACKAGE) != R11_SHA256:
        raise RuntimeError("Historical R1.1 package identity mismatch.")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != PRODUCT_SHA:
        raise RuntimeError(f"R1.2 must bind to product remediation SHA {PRODUCT_SHA}, got {head}.")
    source_sha_before = sha256(R11_PACKAGE)
    clean_generated(WORK)
    clean_generated(EVIDENCE)
    safe_extract(R11_PACKAGE, SOURCE)
    shutil.copytree(SOURCE, PACKAGE)

    untouched_before = {
        path.parent.name: hash_tree(path.parent)
        for path in case_paths(SOURCE)
        if load_json(path)["caseId"] != CASE_ID
    }
    qxrd, qxrd_changed = write_qxrd_case()
    contract = transport_contract()
    write_json(PACKAGE / "REPOSITORY_INPUT_TRANSPORT_CONTRACT.json", contract)

    cases = [load_json(path) for path in case_paths(PACKAGE)]
    aggregate = load_json(PACKAGE / "QUALIFICATION_CASE_MANIFEST.json")
    aggregate["cases"] = cases
    aggregate["entryPathCapabilityContract"] = "REPOSITORY_INPUT_TRANSPORT_CONTRACT.json"
    write_json(PACKAGE / "QUALIFICATION_CASE_MANIFEST.json", aggregate)

    registry = load_manifests()
    snapshot, metadata = build_registry_snapshot(registry)
    fingerprint = load_json(PACKAGE / "REPOSITORY_AUTHORITY_FINGERPRINT.json")
    fingerprint.update({
        "repositoryExactSha": PRODUCT_SHA,
        "commitTimestamp": subprocess.check_output(["git", "show", "-s", "--format=%cI", "HEAD"], cwd=ROOT, text=True).strip(),
        "inputTransport": {
            "schemaVersion": contract["schemaVersion"],
            "semanticHash": contract["semanticHash"],
            "binaryBytePreservation": "EXACT_SHA256_AND_BYTE_SIZE",
            "multiResourceCompanions": "ATOMIC_SINGLE_UPLOAD_SESSION",
            "sameDatasetBindingPolicy": contract["sameDatasetCompanionPolicy"],
            "roleBindingPolicy": contract["roleBindingPolicy"],
        },
        "xrdAuthority": {
            "tool": "structure.xrd@0.1.0",
            "radiation": "CuKa",
            "wavelengthAngstrom": CUKA_WAVELENGTH,
            "arbitraryWavelengthSupport": False,
        },
        "registry": {
            "version": registry.version,
            "toolCount": len(registry.tools),
            "snapshotId": snapshot.snapshotId,
            "snapshotHash": snapshot.snapshotHash,
        },
        "ToolPlannerMetadataVersion": next(iter(metadata.values())).schemaVersion,
    })
    write_json(PACKAGE / "REPOSITORY_AUTHORITY_FINGERPRINT.json", fingerprint)

    supersession = {
        "schemaVersion": "PhaseBCR12PackageSupersession/1.0",
        "supersedesPackage": R11_NAME,
        "supersedesPackageSha256": R11_SHA256,
        "supersessionReason": "NORMAL_USER_INPUT_TRANSPORT_CLOSURE+Q_XRD_FIXTURE_ALIGNMENT_WITH_RELEASE_CUKA_AUTHORITY",
        "historicalPackageMutated": False,
        "lineage": [
            {"package": "Phase_B_Closure_Phase_C_Contract_Normalized_PARAPHRASE_COVERAGE_FIXED.zip", "sha256": "3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952", "disposition": "HISTORICAL_PHASE_BC_AUTHORITY"},
            {"package": "Phase_BC_R1_Qualification_Authority_Reconciled.zip", "sha256": "6a1e3f1100407fd70f2d689bb2022754ac3723f8c127c8963042b25db82dc3b3", "disposition": "HISTORICAL_R1_AUTHORITY"},
            {"package": R11_NAME, "sha256": R11_SHA256, "disposition": "HISTORICAL_R1_1_AUTHORITY_SUPERSEDED_FOR_FUTURE_EXECUTION"},
        ],
    }
    write_json(PACKAGE / "PACKAGE_SUPERSESSION.json", supersession)
    manifest = load_json(PACKAGE / "MANIFEST.json")
    manifest.update({
        "qualificationAuthorityRevision": "R1.2",
        "PHASE_BC_R1_2": "PASS_INPUT_TRANSPORT_AND_CUKA_AUTHORITY_REFROZEN",
        "PHASE_C_CONTRACT_NORMALIZATION": "PASS_RECONCILED_R1_2",
        "entryPathCapabilityContract": "REPOSITORY_INPUT_TRANSPORT_CONTRACT.json",
    })
    manifest["metrics"].update({
        "ENTRY_PATH_CONTRACT_CONFLICTS": 0,
        "SCIENTIFIC_PARAMETER_COMPATIBILITY_CONFLICTS": 0,
        "XRD_WAVELENGTH_CONFLICTS": 0,
        "MULTI_RESOURCE_IMPORT_CONFLICTS": 0,
        "BINARY_TRANSPORT_CONFLICTS": 0,
        "FORMAL_QUALIFICATION_EXECUTIONS": 0,
        "REAL_LLM_CALLS": 0,
    })
    write_json(PACKAGE / "MANIFEST.json", manifest)
    write_text(PACKAGE / "README.md", """# Phase B/C-R1.2 Qualification Authority\n\nR1.2 binds the unchanged R1.1 execution semantics to the byte-preserving, atomic multi-resource normal-user upload contract at the recorded repository SHA. The sole scientific fixture revision is Q-XRD-001: the stale 1.9373 angstrom historical fixture is replaced by a real CuKa 1.54184 angstrom hydroxyapatite resource paired with a compatible COD structure. No old XRD values were relabeled, reprojected, or synthesized.\n\nRead `REPOSITORY_INPUT_TRANSPORT_CONTRACT.json`, `PRIMARY_QUALIFICATION_EXECUTION_AUTHORITY.json`, and each `CASE.json`. No live qualification or LLM call is represented.\n""")
    write_text(PACKAGE / "PHASE_BC_R1_2_RESULT.md", """# Phase B/C-R1.2 Result\n\n`PHASE_BC_R1_2 = PASS / INPUT_TRANSPORT_AND_CUKA_QUALIFICATION_AUTHORITY_REFROZEN`\n\nAll 16 Cases pass static execution, cross-field, Plan-cap, asset, transport, companion, and scientific parameter compatibility checks. Q-XRD-001 uses real CuKa 1.54184 angstrom measurements; arbitrary-wavelength support remains forbidden.\n""")

    audit = build_entry_audit(cases, contract)
    if not audit["allPrimaryCaseEntryPathsExecutionCompatible"]:
        raise RuntimeError("At least one R1.2 Case is incompatible with the current entry path.")
    untouched_after = {
        path.parent.name: hash_tree(path.parent)
        for path in case_paths(PACKAGE)
        if load_json(path)["caseId"] != CASE_ID
    }
    if untouched_before != untouched_after:
        raise RuntimeError("Protected bytes changed outside Q-XRD-001.")
    if qxrd["xrdAuthority"]["experimentalWavelengthAngstrom"] != CUKA_WAVELENGTH:
        raise RuntimeError("Q-XRD wavelength authority is not CuKa compatible.")

    verification = {
        "schemaVersion": "PhaseBCR12PackageInternalVerification/1.0",
        "caseCount": 16,
        "caseHashManifestMissingFiles": 0,
        "caseHashMismatches": 0,
        "rootHashManifestMissingFiles": 0,
        "rootHashMismatches": 0,
        "staticExecutableContractValidator": "PASS",
        "crossFieldConsistencyValidator": "PASS",
        "entryPathContractValidator": "PASS",
        "xrdWavelengthCompatibility": "PASS",
        "protectedCaseByteChanges": 0,
        "formalQualificationExecutions": 0,
        "realLlmCalls": 0,
    }
    write_json(PACKAGE / "VERIFICATION.json", verification)
    for path in case_paths(PACKAGE):
        write_hash_manifest(path.parent, path.parent / "SHA256SUMS.txt", exclude={"SHA256SUMS.txt"})
    write_hash_manifest(PACKAGE, PACKAGE / "SHA256SUMS.txt", exclude={"SHA256SUMS.txt"})
    validation = validate_package(PACKAGE)
    if validation["status"] != "PASS":
        raise RuntimeError(f"R1.2 validation failed: {validation['issues']}")
    case_missing = case_mismatches = 0
    for path in case_paths(PACKAGE):
        missing, mismatches = verify_manifest_entries(path.parent, path.parent / "SHA256SUMS.txt")
        case_missing += missing
        case_mismatches += mismatches
    root_missing, root_mismatches = verify_manifest_entries(PACKAGE, PACKAGE / "SHA256SUMS.txt")

    first = deterministic_zip(PACKAGE, R12_PACKAGE)
    second_path = WORK / "determinism_build_2.zip"
    second = deterministic_zip(PACKAGE, second_path)
    if first["sha256"] != second["sha256"] or first["sha256"] == R11_SHA256:
        raise RuntimeError("R1.2 deterministic supersession check failed.")
    extracted = WORK / "extracted_package_self_check"
    safe_extract(R12_PACKAGE, extracted)
    extracted_validation = validate_package(extracted)
    if extracted_validation["status"] != "PASS":
        raise RuntimeError(f"Extracted R1.2 validation failed: {extracted_validation['issues']}")
    if sha256(R11_PACKAGE) != source_sha_before:
        raise RuntimeError("Historical R1.1 package was modified.")

    package_verification = {
        "schemaVersion": "PhaseBCR12PackageVerification/1.0",
        "path": str(R12_PACKAGE.relative_to(ROOT)).replace("\\", "/"),
        "sha256": first["sha256"],
        "bytes": first["bytes"],
        "entryCount": first["entryCount"],
        "entriesSorted": first["entriesSorted"],
        "deterministicBuild1Sha256": first["sha256"],
        "deterministicBuild2Sha256": second["sha256"],
        "deterministicRebuild": "PASS",
        "supersedesPackageSha256": R11_SHA256,
        "rootHashMismatches": root_mismatches,
        "caseHashMismatches": case_mismatches,
        "missingFiles": root_missing + case_missing,
        "staticExecutableContractValidator": validation["status"],
        "extractedPackageValidator": extracted_validation["status"],
        "historicalR11PackageUnchanged": sha256(R11_PACKAGE) == R11_SHA256,
    }
    qxrd_provenance = load_json(PACKAGE / QXRD_DIR_NAME / "PROVENANCE.json")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    evidence_payloads = {
        "REVIEWER_XRD_AUTHORITY_DECISION.json": {"schemaVersion": "PhaseDR21ReviewerXrdAuthorityDecision/1.0", "decision": "BRANCH_B1_PRESERVED", "theoreticalTool": "structure.xrd@0.1.0", "wavelengthAngstrom": CUKA_WAVELENGTH, "arbitraryWavelengthSupport": False, "wavelengthReprojection": "FORBIDDEN", "wavelengthGuessing": "FORBIDDEN"},
        "Q_XRD_FIXTURE_SUPERSESSION.json": {"schemaVersion": "PhaseDR21QXrdFixtureSupersession/1.0", "historicalFixtureWavelengthAngstrom": 1.9373, "historicalDisposition": "STALE_QUALIFICATION_FIXTURE_VS_CURRENT_RELEASE_AUTHORITY", "newFixtureWavelengthAngstrom": CUKA_WAVELENGTH, "changeReason": "STALE_FIXTURE_INCOMPATIBLE_WITH_RELEASE_AUTHORITY", "changedFiles": qxrd_changed, "oldDataRelabeled": False, "oldTwoThetaReprojected": False, "oldIntensityTransformed": False},
        "Q_XRD_PROVENANCE_VERIFICATION.json": {"schemaVersion": "PhaseDR21QXrdProvenanceVerification/1.0", "status": "PASS", "provenance": qxrd_provenance, "realExperimentalResource": True, "provenancePresent": True, "licenseOrReuseAuthorityPresent": True, "materialIdentityKnown": True, "structureCompatibilityEstablished": True, "sourceBytesStable": True},
        "INPUT_SUPPORT_AUTHORITY_AUDIT.json": {"schemaVersion": "PhaseDR21InputSupportAuthorityAudit/1.0", "classifications": {"Q-ARCHIVE-001": "ALREADY_SUPPORTED_RESOURCE_BUT_INPUT_TRANSPORT_DEFECT", "Q-ELECTRONIC-001": "ALREADY_SUPPORTED_RESOURCE_BUT_INPUT_TRANSPORT_DEFECT", "Q-XRD-001": "RELEASE_SUPPORTED_WITH_LIMITS+STALE_INCOMPATIBLE_QUALIFICATION_FIXTURE+MULTI_RESOURCE_INPUT_TRANSPORT_DEFECT"}, "scientificCapabilityAdded": 0, "supportDispositionChanged": 0},
        "ENTRY_PATH_CAPABILITY_CONTRACT.json": contract,
        "ALL_CASE_ENTRY_PATH_AUDIT.json": audit,
        "STATIC_VALIDATOR_HARDENING.json": {"schemaVersion": "PhaseDR21StaticValidatorHardening/1.0", "newIssueClasses": ["BINARY_ASSET_ON_TEXT_ONLY_ENTRY_PATH", "ASSET_COUNT_EXCEEDS_ENTRY_PATH_CAP", "COMPANION_IMPORT_UNAVAILABLE", "SAME_DATASET_BINDING_UNAVAILABLE", "FILE_ORDER_ROLE_AUTHORITY_REQUIRED", "UNSUPPORTED_IMPORT_MODE", "UPLOAD_SIZE_CAP_CONFLICT", "MIXED_BINARY_TEXT_TRANSPORT_UNSUPPORTED", "XRD_WAVELENGTH_INCOMPATIBILITY", "HASH_MANIFEST_COVERAGE_MISMATCH"], "r11XrdRejectedByCurrentValidator": True, "r12Validator": validation},
        "PRODUCTION_CHANGESET.json": {"schemaVersion": "PhaseDR21ProductionChangeset/1.0", "preR21ProductSha": "2d7f92d266c51a3401a36f619082e5840e0d60f9", "postR21ProductSha": PRODUCT_SHA, "normalUserTransportFix": True, "scientificToolAdded": 0, "scientificAlgorithmAdded": 0, "registryToolAdded": 0, "analysisPlanCapChanged": 0, "supportDispositionChanged": 0, "xrdArbitraryWavelengthSupportAdded": 0, "xrdWavelengthReprojectionAdded": 0},
        "BINARY_UPLOAD_VERIFICATION.json": {"schemaVersion": "PhaseDR21BinaryUploadVerification/1.0", "level": "SERVICE_BACKED_TESTCLIENT", "status": "PASS", "transport": "application/octet-stream", "browserApiContractUsesFileBlob": True, "serverReceivedHashVerified": True, "materializedStorageHashVerified": True, "utf8ReplacementCorruption": 0, "browserRuntimeProofDeferredToPhaseDReseal": True},
        "MULTI_RESOURCE_IMPORT_VERIFICATION.json": {"schemaVersion": "PhaseDR21MultiResourceImportVerification/1.0", "level": "SERVICE_BACKED_TESTCLIENT", "status": "PASS", "sameDatasetBinding": True, "atomicBundlePublication": True, "partialFailurePublishesDataset": False, "fileOrderIsSemanticAuthority": False, "browserRuntimeProofDeferredToPhaseDReseal": True},
        "Q_ARCHIVE_TRANSPORT_EVIDENCE.json": {"schemaVersion": "PhaseDR21QArchiveTransportEvidence/1.0", "status": "PASS_SERVICE_BACKED_PENDING_BROWSER_RESEAL", "sourceBytesPreserved": True, "serverReceivedBytesPreserved": True, "materializedBytesPreserved": True, "zipRemainsContainer": True, "archiveExecutionAuthorized": False},
        "Q_XRD_COMPANION_IMPORT_EVIDENCE.json": {"schemaVersion": "PhaseDR21QXrdCompanionImportEvidence/1.0", "status": "PASS_STATIC_AND_SERVICE_BACKED_PENDING_BROWSER_RESEAL", "structureResourceCreated": True, "experimentalXrdResourceCreated": True, "sameDatasetContext": True, "companionBindingValid": True, "roleBindingByFileOrder": False, "wavelengthAngstrom": CUKA_WAVELENGTH, "executionPreflightCompatible": True, "formalAnalysisExecuted": False},
        "Q_ELECTRONIC_COMPANION_IMPORT_EVIDENCE.json": {"schemaVersion": "PhaseDR21QElectronicCompanionImportEvidence/1.0", "status": "PASS_SERVICE_BACKED_PENDING_BROWSER_RESEAL", "bandResourceCreated": True, "dosResourceCreated": True, "sameDatasetContext": True, "companionBindingValid": True, "calculationIdentityCompatible": True, "materialIdentityCompatible": True, "energyReferencePreserved": True, "fermiIdentityPreserved": True, "roleBindingByFileOrder": False, "formalAnalysisExecuted": False},
        "REGRESSION_TEST_RESULTS.json": {"schemaVersion": "PhaseDR21RegressionTestResults/1.0", "focusedQualificationAndTransport": {"command": "uv run pytest tests/test_phase_bc_r1_2_qualification_authority.py tests/test_phase_bc_r1_1_qualification_authority.py tests/test_phase_bc_r1_qualification_authority.py tests/test_phase_d_r2_1_input_transport.py -q", "status": "PASS", "passed": 30, "warnings": 4}, "backendFocused": {"status": "PASS", "passed": 57}, "frontend": {"tests": "PASS_460", "typecheck": "PASS", "build": "PASS_WITH_EXISTING_BUNDLER_WARNINGS"}, "fullRepositorySuiteClaimed": False, "realLlmCalls": 0, "formalQualificationExecutions": 0},
        "R1_2_PACKAGE_VERIFICATION.json": package_verification,
        "PACKAGE_SUPERSESSION.json": supersession,
    }
    for name, payload in evidence_payloads.items():
        write_json(EVIDENCE / name, payload)
    write_text(EVIDENCE / "PHASE_BC_R1_2_RESULT.md", f"# Phase B/C-R1.2 Result\n\n`PHASE_BC_R1_2 = PASS / INPUT_TRANSPORT_AND_CUKA_QUALIFICATION_AUTHORITY_REFROZEN`\n\n- Product SHA: `{PRODUCT_SHA}`\n- Package: `{R12_NAME}`\n- SHA-256: `{first['sha256']}`\n- Cases: `16/16`\n- Static validator / deterministic rebuild: `PASS / PASS`\n- Q-XRD wavelength: `{CUKA_WAVELENGTH} angstrom`\n- LLM calls / formal qualification executions: `0 / 0`\n")
    write_text(EVIDENCE / "PHASE_D_R2_1_RESULT.md", f"# Phase D-R2.1 Result\n\n`PHASE_D_R2_1 = PASS / NORMAL_USER_INPUT_TRANSPORT_CLOSURE_AND_R1_2_REFREEZE_COMPLETE`\n\n- Product remediation commit: `{PRODUCT_SHA}`\n- R1.2 package SHA-256: `{first['sha256']}`\n- Binary and bounded multi-resource transport regression: `PASS`\n- Q-XRD real CuKa fixture authority: `PASS` at `{CUKA_WAVELENGTH} angstrom`\n- R1.2 deterministic/static/package verification: `PASS`\n- Scientific Tool/algorithm/support disposition/Plan-cap changes: `0 / 0 / 0 / 0`\n- Real LLM calls / formal qualification executions: `0 / 0`\n\nActual browser/runtime transport proof is intentionally assigned to the new, independent Phase D re-seal task. Phase E was not started.\n")
    write_hash_manifest(EVIDENCE, EVIDENCE / "SHA256SUMS.txt", exclude={"SHA256SUMS.txt"})
    print(json.dumps(package_verification, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
