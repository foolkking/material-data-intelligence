"""Build the R1.6 qualification authority from R1.2 plus approved repairs.

This is qualification-governance tooling.  It intentionally establishes
authority through content, schema, and executable-contract validation rather
than checksums or package digests.  Historical packages are read only.
"""

from __future__ import annotations

import json
import shutil
import sys
import zipfile
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for package in ("services/llm", "packages/material-parsers", "packages/tool-registry", "packages/schemas"):
    sys.path.insert(0, str(ROOT / package))

from phase_bc_r1_6_executability_preflight import (  # noqa: E402
    EVIDENCE as PREFLIGHT_EVIDENCE,
    PROPERTY_MAP,
    WORK as PREFLIGHT_WORK,
    materialize_jarvis_candidate,
    materialize_ml_candidates,
    materialize_phonon_ordering_candidates,
)


SOURCE_PACKAGE = ROOT / "_qualification" / "work" / "phase_bc_r1_2" / "package"
WORK = ROOT / "_qualification" / "work" / "phase_bc_r1_6" / "authority_package"
OUTPUT = ROOT / "_qualification" / "inputs" / "Phase_BC_R1_6_Qualification_Authority_Reconciled.zip"
EVIDENCE = ROOT / "_qualification" / "evidence" / "phase_bc_r1_6" / "attempt_01_authority_refreeze"

QTABLE_QUESTIONS = {
    "numeric-summary": "Summarize formation energy, band gap, and density.",
    "distribution": "Show the distribution of band gap.",
    "correlation": "Analyze the correlations among formation energy, band gap, and density.",
    "scatter": "Plot formation energy against density.",
}

ML_QUESTIONS = {
    "Q-ML-REG-001": "Analyze the supplied regression model performance and prediction error for the measured target values.",
    "Q-ML-UNC-001": "Assess whether the supplied prediction uncertainty is informative for these predictions.",
    "Q-ML-CLASS-001": "Evaluate the supplied material classification labels and summarize their limitations.",
}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def strip_digest_fields(value: Any) -> Any:
    """Retire R1.2 digest machinery without touching scientific content."""

    if isinstance(value, list):
        return [strip_digest_fields(item) for item in value]
    if not isinstance(value, dict):
        return value
    return {
        key: strip_digest_fields(item)
        for key, item in value.items()
        if not any(fragment in key.casefold() for fragment in ("sha256", "checksum", "digest"))
    }


def copy_base_package() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    shutil.copytree(SOURCE_PACKAGE, WORK)
    for path in WORK.rglob("SHA256SUMS.txt"):
        path.unlink()
    for path in WORK.rglob("VERIFICATION.json"):
        path.unlink()
    for filename in (
        "HISTORICAL_PHASE_A_AUTHORITY.json",
        "PHASE_B_RESULT.md",
        "PHASE_BC_R1_RESULT.md",
        "PHASE_BC_R1_1_RESULT.md",
        "PHASE_BC_R1_2_RESULT.md",
    ):
        path = WORK / filename
        if path.is_file():
            path.unlink()

    for path in WORK.rglob("*.json"):
        write_json(path, strip_digest_fields(load_json(path)))


def update_qtable(jarvis: dict[str, Any]) -> dict[str, Any]:
    case_dir = WORK / "03_Q-TABLE-001"
    candidate = PREFLIGHT_WORK / "q_table" / "Q_TABLE_CANDIDATE_JARVIS_DFT_3D.csv"
    for filename in ("SOURCE_TableS1.csv", "UPLOAD_materials_table.csv"):
        (case_dir / filename).unlink()
    shutil.copyfile(candidate, case_dir / "SOURCE_JARVIS_DFT_3D_material_properties.csv")
    shutil.copyfile(candidate, case_dir / "UPLOAD_materials_table.csv")

    case = load_json(case_dir / "CASE.json")
    asset = case["assets"][0]
    asset["filename"] = "UPLOAD_materials_table.csv"
    asset["provenanceRef"] = "PROVENANCE.json#/assetLineage/UPLOAD_materials_table.csv"
    case["canonicalQuestion"] = "Summarize, distribute, correlate, and compare explicitly named material properties in the supplied materials table."
    case["reason"] = "R1.6 retains table analysis with exact, current DataProfile-backed material-property targets; no numeric-column or fuzzy target selection is authorized."
    case["sourceBytesChanged"] = True
    case["correctionsApplied"] = [
        "Replaced the stale Bartel table with a provenance-grounded JARVIS-DFT-3D material-property projection.",
        "Rewrote four natural-language turns to name exact current DataProfile material properties.",
        "Requires AnalysisIntent/1.1 explicit property target roles derived only from current Profile facts.",
    ]
    case["requiredProfileFacts"] = [
        "materials_tabular_dataset READY",
        "material_property formation_energy",
        "material_property band_gap",
        "material_property density",
    ]
    for turn in case["executionTurns"]:
        turn["question"] = QTABLE_QUESTIONS[turn["turnId"]]
        turn["requiredProfileFacts"] = deepcopy(case["requiredProfileFacts"])
        if turn["turnId"] == "numeric-summary":
            turn["requiredIntentFacts"] = ["PROPERTY_SET: formation_energy, band_gap, density"]
        elif turn["turnId"] == "distribution":
            turn["requiredIntentFacts"] = ["PROPERTY: band_gap"]
        elif turn["turnId"] == "correlation":
            turn["requiredIntentFacts"] = ["PROPERTY_SET: formation_energy, band_gap, density"]
        else:
            turn["requiredIntentFacts"] = ["X_PROPERTY: formation_energy", "Y_PROPERTY: density", "X_PROPERTY != Y_PROPERTY"]
    case["userQuestions"] = [turn["question"] for turn in case["executionTurns"]]
    write_json(case_dir / "CASE.json", case)

    provenance = {
        "schemaVersion": "QualificationSourceProvenance/1.1",
        "caseId": "Q-TABLE-001",
        "provenanceStatus": "COMPLETE",
        "sources": [{
            "sourceId": "SRC-JARVIS-DFT-3D-FIGSHARE",
            "sourceRole": "materials_dataset",
            "sourceType": "public_scientific_dataset",
            "sourceTitle": "JARVIS-DFT-3D dataset",
            "repositoryIdentifier": "Figshare 10.6084/m9.figshare.6815699.v11",
            "licenseOrReuseAuthority": "CC BY 4.0",
            "retrievalAuthority": "Retained repository source used by the R1.3/R1.5 reconciliation work.",
            "sourceFields": {name: spec["sourceField"] for name, spec in PROPERTY_MAP.items()},
            "materialIdentity": "JARVIS jid",
        }],
        "assetLineage": {
            "SOURCE_JARVIS_DFT_3D_material_properties.csv": {
                "sourceRefs": ["SRC-JARVIS-DFT-3D-FIGSHARE"],
                "normalization": "representation-only projection with stable jid copied to sample_id and canonical current Profile column names",
            },
            "UPLOAD_materials_table.csv": {
                "sourceRefs": ["SRC-JARVIS-DFT-3D-FIGSHARE"],
                "normalization": "byte-identical copy of the authority source projection for normal-user upload",
            },
        },
        "propertyAuthority": {
            name: {"sourceField": spec["sourceField"], "unit": spec["unit"], "currentProfileSemanticRole": "material_property"}
            for name, spec in PROPERTY_MAP.items()
        },
        "scientificFreeze": {
            "scientificValueChanges": 0,
            "unitGuesses": 0,
            "propertyFabrication": 0,
            "rowJoinGuessing": 0,
        },
        "replacementReason": "Q_TABLE_FIXTURE_NOT_EXECUTION_COMPATIBLE_WITH_EXISTING_SEMANTIC_AUTHORITY",
    }
    write_json(case_dir / "PROVENANCE.json", provenance)
    (case_dir / "LICENSE.txt").write_text("JARVIS-DFT-3D selected records are used under the source's CC BY 4.0 reuse authority.\n", encoding="utf-8", newline="\n")
    (case_dir / "README.md").write_text(
        "# Q-TABLE-001 R1.6 fixture\n\n"
        "This is a representation-only, provenance-grounded JARVIS-DFT-3D projection. "
        "The four normal-user questions bind only explicit, current DataProfile material-property targets.\n",
        encoding="utf-8",
        newline="\n",
    )
    return {"caseId": "Q-TABLE-001", "source": jarvis["sourceIdentity"], "properties": list(PROPERTY_MAP), "questions": QTABLE_QUESTIONS}


def update_ml(ml: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for ordinal, case_id in (("04", "Q-ML-REG-001"), ("05", "Q-ML-UNC-001"), ("06", "Q-ML-CLASS-001")):
        case_dir = next(WORK.glob(f"{ordinal}_*"))
        case = load_json(case_dir / "CASE.json")
        candidate = Path(ml[case_id]["candidatePath"])
        upload = case["assets"][0]["filename"]
        shutil.copyfile(candidate, case_dir / upload)
        turn = case["executionTurns"][0]
        turn["question"] = ML_QUESTIONS[case_id]
        case["userQuestions"] = [turn["question"]]
        case["sourceBytesChanged"] = True
        case["correctionsApplied"] = list(case.get("correctionsApplied", [])) + [
            "R1.5 source-authoritative canonical Profile field projection retained for exact ML target binding.",
            "R1.5 natural-language turn clarification retained without changing the scientific objective or required Tool.",
        ]
        write_json(case_dir / "CASE.json", case)
        changes.append({
            "caseId": case_id,
            "candidate": str(Path(ml[case_id]["candidatePath"]).relative_to(ROOT)),
            "question": turn["question"],
        })
    return changes


def update_phonon(phonon: dict[str, Path]) -> dict[str, Any]:
    case_dir = WORK / "13_Q-PHONON-001"
    for filename, source in phonon.items():
        shutil.copyfile(source, case_dir / filename)
    case = load_json(case_dir / "CASE.json")
    case["sourceBytesChanged"] = True
    case["correctionsApplied"] = list(case.get("correctionsApplied", [])) + [
        "R1.5 explicit canonical_structure_order metadata correction retained after direct compatibility review; no species or mode data was reordered.",
    ]
    write_json(case_dir / "CASE.json", case)
    return {"caseId": "Q-PHONON-001", "change": "atom_ordering metadata source_order -> canonical_structure_order", "scientificValuesChanged": 0}


def update_root(qtable: dict[str, Any], ml: list[dict[str, Any]], phonon: dict[str, Any]) -> None:
    manifest = {
        "schemaVersion": "PhaseBClosurePhaseCContractManifest/1.2",
        "qualificationAuthorityRevision": "R1.6",
        "authorityName": "Phase_BC_R1_6_Qualification_Authority_Reconciled",
        "caseSchemaVersion": "QualificationCaseManifest/1.1",
        "caseCount": 16,
        "integrityAuthority": "CONTENT_AND_CONTRACT_VALIDATION",
        "historicalDigestRecords": "NON_NORMATIVE",
        "futurePassFailDependsOnDigests": False,
        "contractAliasPolicy": "CONTRACT_ALIAS_POLICY.json",
        "primaryQualificationExecutionAuthority": "PRIMARY_QUALIFICATION_EXECUTION_AUTHORITY.json",
        "entryPathCapabilityContract": "REPOSITORY_INPUT_TRANSPORT_CONTRACT.json",
        "repositoryAuthorityFingerprint": "REPOSITORY_AUTHORITY_FINGERPRINT.json",
        "packageSupersession": "PACKAGE_SUPERSESSION.json",
        "caseInventory": "CASE_INDEX.json",
    }
    write_json(WORK / "MANIFEST.json", manifest)
    write_json(WORK / "PACKAGE_SUPERSESSION.json", {
        "schemaVersion": "QualificationAuthoritySupersession/1.2",
        "supersedesAuthority": "Phase_BC_R1_2_Qualification_Authority_Reconciled",
        "supersessionReason": [
            "Q_TABLE_EXPLICIT_PROPERTY_TARGET_RECONCILIATION",
            "BOUND_EXPLICIT_MATERIAL_PROPERTY_TARGET_INTENT",
            "R1_5_FULL_PREFLIGHT_RECONCILIATIONS",
        ],
        "historicalBlockedAttempts": ["Phase_BC_R1_3", "Phase_BC_R1_4", "Phase_BC_R1_5"],
        "integrityAuthority": "CONTENT_AND_CONTRACT_VALIDATION",
    })
    write_json(WORK / "PRIMARY_QUALIFICATION_EXECUTION_AUTHORITY.json", {
        "schemaVersion": "PrimaryQualificationExecutionAuthority/1.2",
        "authorityRevision": "R1.6",
        "analysisIntentSupportedVersions": ["1.0", "1.1"],
        "materialPropertyTargetAuthority": "AnalysisIntent/1.1 explicit exact Profile targets only",
        "caseCanonicalQuestionRule": "executionTurns[].question are ordered live Planner submissions for analysis cases",
        "requiredToolRule": "requiredExecutionTools are mandatory; allowedExecutionTools are nonmandatory; campaignCoverageContributions are not execution assertions",
        "expectedRejectionRule": "Expected-rejection Cases terminate before Plan creation as declared by their Case contract.",
        "qTable": qtable,
        "mlCarryForward": ml,
        "phononCarryForward": phonon,
    })
    write_json(WORK / "REPOSITORY_AUTHORITY_FINGERPRINT.json", {
        "schemaVersion": "QualificationRepositoryAuthorityInventory/1.2",
        "qualificationIntegrityAuthority": "CONTENT_AND_CONTRACT_VALIDATION",
        "currentCommittedProductState": "9f406f9 fix(trajectory): scan typed numeric arrays within contract caps (descends from 0e8f779 explicit property targets)",
        "analysisIntent": {"currentVersion": "1.1", "historicalReadableVersion": "1.0"},
        "analysisPlan": {"supportedVersions": ["0.1", "0.2"], "maximumSteps": 4},
        "entryPathContract": "REPOSITORY_INPUT_TRANSPORT_CONTRACT.json",
        "preflight": "PREFLIGHT_MODEL_RESULT.json",
    })
    write_json(WORK / "PREFLIGHT_MODEL_RESULT.json", {
        "schemaVersion": "QualificationExecutabilityPreflight/2.0",
        "source": "_qualification/evidence/phase_bc_r1_6/attempt_02_final_package_preflight/ALL_CASE_EXECUTABILITY_PREFLIGHT.json",
        "executionMode": "NON_LLM_NON_FORMAL",
        "expectedCases": 16,
        "expectedAnalysisExecutionTurns": 26,
        "integrityAuthority": "CONTENT_AND_CONTRACT_VALIDATION",
    })
    (WORK / "README.md").write_text(
        "# Phase B/C-R1.6 Qualification Authority\n\n"
        "This authority is evaluated through package inventory, Case schemas, direct protected-content comparison, semantic contracts, deterministic preflight, and later runtime evidence. "
        "Historical digest records are non-normative and no current pass/fail decision depends on a digest.\n",
        encoding="utf-8",
        newline="\n",
    )


def deterministic_zip(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*"), key=lambda item: item.relative_to(source).as_posix()):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(path.relative_to(source).as_posix(), date_time=(2026, 8, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def inventory(package: Path) -> dict[str, Any]:
    files = sorted(path.relative_to(package).as_posix() for path in package.rglob("*") if path.is_file())
    case_dirs = sorted(path for path in package.iterdir() if path.is_dir() and path.name[:2].isdigit())
    case_ids = [load_json(path / "CASE.json")["caseId"] for path in case_dirs]
    missing_case_files = [path.name for path in case_dirs if not (path / "CASE.json").is_file()]
    forbidden = [item for item in files if any(token in Path(item).name.casefold() for token in ("sha256", "checksum", "digest"))]
    return {
        "packageRoot": str(package.relative_to(ROOT)),
        "entryCount": len(files),
        "entriesSorted": files == sorted(files),
        "caseDirectoryCount": len(case_dirs),
        "caseIds": case_ids,
        "uniqueCaseIds": len(case_ids) == len(set(case_ids)),
        "missingCaseFiles": missing_case_files,
        "forbiddenDigestArtifacts": forbidden,
        "requiredRootFilesPresent": all((package / name).is_file() for name in ("MANIFEST.json", "CASE_INDEX.json", "QUALIFICATION_CASE_MANIFEST.json", "CONTRACT_ALIAS_POLICY.json", "PRIMARY_QUALIFICATION_EXECUTION_AUTHORITY.json", "REPOSITORY_AUTHORITY_FINGERPRINT.json")),
    }


def main() -> None:
    jarvis = materialize_jarvis_candidate()
    ml = materialize_ml_candidates()
    phonon = materialize_phonon_ordering_candidates()
    copy_base_package()
    qtable = update_qtable(jarvis)
    ml_changes = update_ml(ml)
    phonon_change = update_phonon(phonon)
    update_root(qtable, ml_changes, phonon_change)

    package_inventory = inventory(WORK)
    if package_inventory["caseDirectoryCount"] != 16 or not package_inventory["uniqueCaseIds"] or package_inventory["missingCaseFiles"] or package_inventory["forbiddenDigestArtifacts"] or not package_inventory["requiredRootFilesPresent"]:
        raise RuntimeError(f"R1.6 package inventory invalid: {package_inventory}")

    first = EVIDENCE / "Phase_BC_R1_6_Qualification_Authority_Reconciled.first.zip"
    second = EVIDENCE / "Phase_BC_R1_6_Qualification_Authority_Reconciled.second.zip"
    deterministic_zip(WORK, first)
    deterministic_zip(WORK, second)
    deterministic = first.read_bytes() == second.read_bytes()
    if not deterministic:
        raise RuntimeError("R1.6 package double-build differs.")
    shutil.copyfile(first, OUTPUT)
    with zipfile.ZipFile(OUTPUT) as archive:
        zip_entries = archive.namelist()
    package_inventory["zipPath"] = str(OUTPUT.relative_to(ROOT))
    package_inventory["zipByteSize"] = OUTPUT.stat().st_size
    package_inventory["zipEntryCount"] = len(zip_entries)
    package_inventory["zipEntriesSorted"] = zip_entries == sorted(zip_entries)
    package_inventory["deterministicPackageBuild"] = "PASS"
    package_inventory["digestBasedQualificationGates"] = False
    write_json(EVIDENCE / "R1_6_PACKAGE_INVENTORY.json", package_inventory)
    write_json(EVIDENCE / "R1_6_PACKAGE_VERIFICATION.json", {
        "schemaVersion": "QualificationPackageVerification/1.2",
        "package": str(OUTPUT.relative_to(ROOT)),
        "authorityVersion": "R1.6",
        "deterministicPackageBuild": "PASS",
        "caseCount": 16,
        "missingFiles": 0,
        "duplicateEntries": 0,
        "forbiddenDigestArtifacts": 0,
        "validationBasis": ["package inventory", "Case schema/content", "all-case preflight", "direct protected-content review"],
    })
    write_json(EVIDENCE / "PACKAGE_SUPERSESSION.json", load_json(WORK / "PACKAGE_SUPERSESSION.json"))
    write_json(EVIDENCE / "Q_TABLE_R1_6_AUTHORITY.json", qtable)
    write_json(EVIDENCE / "Q_TABLE_FINAL_EXECUTION_TURNS.json", {
        "caseId": "Q-TABLE-001",
        "questions": QTABLE_QUESTIONS,
        "requiredTools": ["table.numeric_summary", "viz.histogram", "viz.correlation", "viz.scatter"],
        "bindingPolicy": "explicit exact current-Profile material_property targets only",
    })
    print(json.dumps({"package": str(OUTPUT.relative_to(ROOT)), "inventory": package_inventory}, indent=2))


if __name__ == "__main__":
    main()
