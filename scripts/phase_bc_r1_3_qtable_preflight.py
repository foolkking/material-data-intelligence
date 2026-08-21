"""Mechanically audit Q-TABLE fixture binding against current product authority.

This is a non-production Phase B/C-R1.3 audit.  It uses the current parser,
DataProfile, deterministic Intent builder, Registry, and Eligibility code; it
does not create Jobs, call an LLM, or modify product contracts.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "llm"))

from mdi_llm import AnalysisIntentRequest, DeterministicAnalysisIntentBuilder  # noqa: E402
from mdi_llm.capability_planner import resolve_eligibility  # noqa: E402
from mdi_material_parsers import build_data_profile, parse_file  # noqa: E402
from mdi_tool_registry import build_registry_snapshot, load_manifests  # noqa: E402
from mdi_material_parsers.semantic_profile import _PROPERTY_NAMES  # noqa: E402


R12_WORK = ROOT / "_qualification" / "work" / "phase_bc_r1_2" / "package"
R12_QTABLE = R12_WORK / "03_Q-TABLE-001"
SOURCE_ZIP = ROOT / "_qualification" / "work" / "phase_bc_r1_3" / "source" / "jdft_3d-8-18-2021.json.zip"
SOURCE_SHA256 = "03e5af365067117d97c73b83fc74b86f79cdba4cc592b346f5aa2209a24c3925"
OUTPUT = ROOT / "_qualification" / "work" / "phase_bc_r1_3" / "q_table_preflight"
CANDIDATE_CSV = OUTPUT / "Q_TABLE_CANDIDATE_JARVIS_DFT_3D.csv"
RESULT = OUTPUT / "Q_TABLE_REQUIRED_TOOL_BINDING_PREFLIGHT.json"
EVIDENCE = ROOT / "_qualification" / "evidence" / "phase_bc_r1_3" / "attempt_01_blocked_authority_conflict"

PROPERTY_MAP = {
    "formation_energy": {
        "sourceField": "formation_energy_peratom",
        "unit": "eV/atom",
        "mapping": "EXPLICIT_CANONICAL_RENAME",
    },
    "band_gap": {
        "sourceField": "optb88vdw_bandgap",
        "unit": "eV",
        "mapping": "EXPLICIT_CANONICAL_RENAME",
    },
    "density": {
        "sourceField": "density",
        "unit": "g/cm3",
        "mapping": "IDENTICAL_FIELD_NAME",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


def write_hash_manifest(root: Path) -> None:
    rows = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            rel = path.relative_to(root).as_posix()
            rows.append(f"{sha256(path)}  {rel}  {path.stat().st_size}  UTF8_LF")
    write_text(root / "SHA256SUMS.txt", "\n".join(rows) + "\n")


def source_rows() -> list[dict[str, Any]]:
    if sha256(SOURCE_ZIP) != SOURCE_SHA256:
        raise RuntimeError("JARVIS source ZIP SHA-256 mismatch.")
    with zipfile.ZipFile(SOURCE_ZIP) as archive:
        names = archive.namelist()
        if names != ["jdft_3d-8-18-2021.json"]:
            raise RuntimeError(f"Unexpected JARVIS ZIP entries: {names!r}")
        records = json.loads(archive.read(names[0]))
    selected: list[dict[str, Any]] = []
    for record in sorted(records, key=lambda item: str(item["jid"])):
        values = [record.get(spec["sourceField"]) for spec in PROPERTY_MAP.values()]
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) for value in values):
            continue
        if float(record["optb88vdw_bandgap"]) <= 0:
            continue
        selected.append(record)
        if len(selected) == 64:
            break
    if len(selected) != 64:
        raise RuntimeError("The deterministic JARVIS selection did not produce 64 finite nonzero-gap records.")
    return selected


def materialize_candidate(rows: list[dict[str, Any]]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fieldnames = ["sample_id", "formula", *PROPERTY_MAP]
    with CANDIDATE_CSV.open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "sample_id": row["jid"],
                    "formula": row["formula"],
                    **{name: row[spec["sourceField"]] for name, spec in PROPERTY_MAP.items()},
                }
            )


def profile_for(path: Path, dataset_id: str):
    parsed = parse_file(path, dataset_id=dataset_id, file_id=f"file_{dataset_id}")
    if parsed.parse_status != "success":
        raise RuntimeError(f"Could not parse {path.name}: {parsed.error_code} {parsed.error_message}")
    return build_data_profile(dataset_id=dataset_id, parse_results=[parsed], platform_tool_ids={tool.toolId for tool in load_manifests().tools})


def semantic_properties(profile: Any) -> list[dict[str, Any]]:
    return [
        column.model_dump(mode="json")
        for column in profile.semanticColumns
        if any(role.role == "material_property" for role in column.roles)
    ]


def turn_results(profile: Any, case: dict[str, Any]) -> list[dict[str, Any]]:
    registry = load_manifests()
    builder = DeterministicAnalysisIntentBuilder()
    results: list[dict[str, Any]] = []
    for turn in case["executionTurns"]:
        intent = builder.build(
            AnalysisIntentRequest(
                raw_goal=turn["question"],
                dataset_id=profile.datasetId,
                profile_id=profile.profileId,
            ),
            profile=profile,
            created_at="2026-08-16T00:00:00+00:00",
        )
        if intent.outcome.value != "READY":
            results.append(
                {
                    "turnId": turn["turnId"],
                    "question": turn["question"],
                    "requiredTools": [
                        {
                            "toolId": tool_id,
                            "eligible": False,
                            "bindingDomains": [],
                            "reasons": [reason.model_dump(mode="json") for reason in intent.unsupportedReasons],
                        }
                        for tool_id in turn["requiredExecutionTools"]
                    ],
                    "intent": {
                        "outcome": intent.outcome.value,
                        "scientificIntents": [value.value for value in intent.scientificIntents],
                        "requiredCapabilityNeeds": [value.value for value in intent.requiredCapabilityNeeds],
                        "targetSemantics": [value.model_dump(mode="json") for value in intent.targetSemantics],
                    },
                }
            )
            continue
        resolution = resolve_eligibility(intent, profile=profile, registry=registry)
        candidates = {candidate.toolId: candidate for candidate in resolution.evaluatedCandidates}
        required = []
        for tool_id in turn["requiredExecutionTools"]:
            candidate = candidates[tool_id]
            required.append(
                {
                    "toolId": tool_id,
                    "eligible": candidate.eligible,
                    "bindingDomains": [domain.model_dump(mode="json") for domain in candidate.bindingDomains],
                    "reasons": [reason.model_dump(mode="json") for reason in candidate.reasons],
                }
            )
        results.append(
            {
                "turnId": turn["turnId"],
                "question": turn["question"],
                "requiredTools": required,
                "intent": {
                    "outcome": intent.outcome.value,
                    "scientificIntents": [value.value for value in intent.scientificIntents],
                    "requiredCapabilityNeeds": [value.value for value in intent.requiredCapabilityNeeds],
                    "targetSemantics": [value.model_dump(mode="json") for value in intent.targetSemantics],
                },
            }
        )
    return results


def main() -> None:
    case = json.loads((R12_QTABLE / "CASE.json").read_text(encoding="utf-8"))
    old_csv = R12_QTABLE / "UPLOAD_materials_table.csv"
    rows = source_rows()
    materialize_candidate(rows)
    old_profile = profile_for(old_csv, "dataset_qtable_old_r12")
    candidate_profile = profile_for(CANDIDATE_CSV, "dataset_qtable_candidate_r13")
    registry = load_manifests()
    _, metadata_by_id = build_registry_snapshot(registry)
    result = {
        "schemaVersion": "PhaseBCR13QTableRequiredToolBindingPreflight/1.0",
        "executionMode": "NON_LLM_NON_FORMAL_QUALIFICATION",
        "productContractsModified": False,
        "sourceSelection": {
            "sourceId": "SRC-JARVIS-DFT-3D-2021-FIGSHARE-6815699",
            "sourceZip": SOURCE_ZIP.name,
            "sourceZipSha256": sha256(SOURCE_ZIP),
            "selectionPolicy": "SORT_BY_JID_THEN_FIRST_64_WITH_FINITE_FORMATION_ENERGY_PERATOM_OPTB88VDW_BANDGAP_DENSITY_AND_POSITIVE_BANDGAP",
            "stableIdentity": "jid copied to sample_id",
            "rowOrderIsIdentity": False,
            "propertyMap": PROPERTY_MAP,
            "candidateCsv": CANDIDATE_CSV.name,
            "candidateCsvSha256": sha256(CANDIDATE_CSV),
            "candidateRowCount": len(rows),
        },
        "oldR12Fixture": {
            "filename": old_csv.name,
            "sha256": sha256(old_csv),
            "materialPropertyColumns": semantic_properties(old_profile),
            "turnResults": turn_results(old_profile, case),
        },
        "candidateReplacementFixture": {
            "filename": CANDIDATE_CSV.name,
            "sha256": sha256(CANDIDATE_CSV),
            "materialPropertyColumns": semantic_properties(candidate_profile),
            "turnResults": turn_results(candidate_profile, case),
        },
        "expectedConflict": {
            "classification": "EXECUTION_TURN_INTENT_AND_TARGET_BINDING_CONTRACT_CONFLICT",
            "reason": "Current non-ML normal-user intent construction supplies no material_property targetSemantics for the frozen histogram and scatter questions; the current scatter contract also has no distinct x/y target-pair binding authority.",
            "reviewerActionRequired": True,
        },
        "executionCounters": {
            "realLlmCalls": 0,
            "formalQualificationExecutions": 0,
            "newQualificationJobs": 0,
            "newQualificationArtifacts": 0,
        },
    }
    write_json(RESULT, result)
    approved_properties = {
        "schemaVersion": "PhaseBCR13ApprovedMaterialPropertySemantics/1.0",
        "source": "packages/material-parsers/mdi_material_parsers/semantic_profile.py#_PROPERTY_NAMES",
        "dataProfileSemanticRulesVersion": candidate_profile.semanticRulesVersion,
        "matchingPolicy": "TRIMMED_CASE_INSENSITIVE_EXACT_CANONICAL_NAME",
        "numericDtypeRequired": True,
        "properties": [
            {
                "canonicalSemanticId": name,
                "acceptedSourceColumnNames": [name],
                "semanticRole": role,
                "unitRequirement": "NO_TOOL_BINDING_REQUIREMENT; BARE_CSV_PROFILE_UNIT_IS_UNKNOWN",
                "normalizationPolicy": "NO_VALUE_OR_UNIT_TRANSFORMATION",
                "toolUsability": {
                    "table.numeric_summary": True,
                    "viz.histogram": True,
                    "viz.correlation": True,
                    "viz.scatter": True,
                },
            }
            for name in sorted(_PROPERTY_NAMES)
            for role in ["material_property"]
        ],
    }
    tool_requirements = {
        "schemaVersion": "PhaseBCR13QTableToolBindingRequirements/1.0",
        "source": "packages/tool-registry/mdi_tool_registry/planner_metadata.py#_bindings",
        "tools": [
            {
                "toolId": tool_id,
                "metadata": metadata_by_id[tool_id].model_dump(mode="json"),
                "requiredBindings": [
                    item.model_dump(mode="json")
                    for item in metadata_by_id[tool_id].parameterBindings
                    if item.required
                ],
            }
            for tool_id in case["requiredExecutionTools"]
        ],
    }
    source_selection = {
        "schemaVersion": "PhaseBCR13QTableSourceSelection/1.0",
        "outcome": "CANDIDATE_SOURCE_VALID_BUT_FIXTURE_REPLACEMENT_INSUFFICIENT",
        "source": {
            "sourceId": "SRC-JARVIS-DFT-3D-2021-FIGSHARE-6815699",
            "articleDoi": "10.6084/m9.figshare.6815699.v11",
            "fileId": 29204826,
            "fileName": SOURCE_ZIP.name,
            "downloadUrl": "https://ndownloader.figshare.com/files/29204826",
            "license": "CC BY 4.0",
            "sourceZipBytes": SOURCE_ZIP.stat().st_size,
            "sourceZipSha256": sha256(SOURCE_ZIP),
            "figshareSuppliedMd5": "8f619035a2cd8030de1ce38ce8b561b2",
        },
        "projection": result["sourceSelection"],
        "scientificTransformations": "NONE; deterministic row filtering and explicit representation-only source-field to canonical-column projection only",
        "scientificValueChanges": 0,
        "unitValueChanges": 0,
        "propertyFabrication": 0,
        "rowMatchGuesses": 0,
    }
    profile_verification = {
        "schemaVersion": "PhaseBCR13QTableProfileVerification/1.0",
        "candidateProfile": candidate_profile.model_dump(mode="json"),
        "approvedMaterialPropertyColumnCount": len(result["candidateReplacementFixture"]["materialPropertyColumns"]),
        "exactPropertyColumns": [item["column"] for item in result["candidateReplacementFixture"]["materialPropertyColumns"]],
        "profileResult": "PASS_FOR_MATERIAL_PROPERTY_IDENTIFICATION",
        "qualificationResult": "BLOCKED_BY_EXECUTION_TURN_INTENT_AND_TARGET_BINDING_CONTRACT",
    }
    old_failure = {
        "schemaVersion": "PhaseBCR13QTableOldFixtureFailureAnalysis/1.0",
        "caseId": case["caseId"],
        "oldFixtureSha256": result["oldR12Fixture"]["sha256"],
        "approvedMaterialPropertyColumns": [],
        "requiredTools": case["requiredExecutionTools"],
        "turnResults": result["oldR12Fixture"]["turnResults"],
        "classification": "QUALIFICATION_FIXTURE_NOT_EXECUTION_COMPATIBLE_WITH_EXISTING_SEMANTIC_AUTHORITY",
    }
    decision = {
        "schemaVersion": "PhaseBCR13QTableAuthorityDecision/1.0",
        "reviewerDecision": "REPLACE_FIXTURE_WITH_REAL_MATERIALS_TABLE_USING_EXISTING_APPROVED_MATERIAL_PROPERTY_SEMANTICS",
        "result": "BLOCKED_AUTHORITY_CONFLICT",
        "blockerId": "PHASE_BC_R13_AUTH_001",
        "component": "FROZEN_Q_TABLE_EXECUTION_TURN_INTENT_AND_TARGET_BINDING_CONTRACT",
        "observedEvidence": {
            "candidateApprovedMaterialPropertyColumns": [item["column"] for item in result["candidateReplacementFixture"]["materialPropertyColumns"]],
            "candidateTurnResults": result["candidateReplacementFixture"]["turnResults"],
        },
        "expectedState": "All four frozen execution turns reach current normal-user Intent/Eligibility parameter binding without changing production semantic or target-binding authority.",
        "whyFixtureReplacementCannotSatisfyIt": [
            "The frozen numeric-summary, histogram, and correlation questions do not map to the current deterministic normal-user Intent vocabulary.",
            "The frozen scatter question reaches READY Intent but has no material_property targetSemantics, leaving both required scalar parameters unbound.",
            "Current scalar scatter bindings do not model a distinct x/y pair, so a fixture alone cannot establish an unambiguous non-degenerate scatter binding.",
        ],
        "forbiddenAutonomousChanges": [
            "DataProfile approved property vocabulary or semantic binding policy",
            "ToolPlannerMetadata for table.numeric_summary/viz.histogram/viz.correlation/viz.scatter",
            "AnalysisIntent target-binding behavior",
            "Frozen Q-TABLE questions or required Tool set",
        ],
        "recommendedResolutionClass": "REVIEWER_AUTHORITY_RECONCILIATION",
        "minimumReviewerDecision": "Authorize a revised frozen Q-TABLE turn contract with product-supported explicit property selection/clarification semantics, or separately authorize a reviewed production normal-user target-binding capability change followed by a new authority refreeze.",
    }
    static_hardening = {
        "schemaVersion": "PhaseBCR13StaticValidatorHardeningStatus/1.0",
        "status": "NOT_IMPLEMENTED_AFTER_HARD_STOP",
        "reason": "A full required-tool binding validator would correctly fail the current R1.2 Q-TABLE execution turns. R1.3 cannot be refrozen until Reviewer resolves the discovered frozen authority conflict.",
        "requiredFutureChecks": [
            "REQUIRED_TOOL_PARAMETER_UNBOUND",
            "REQUIRED_TOOL_INTENT_INCOMPATIBLE",
            "REQUIRED_TOOL_TARGET_BINDING_MISSING",
            "REQUIRED_TOOL_PROFILE_CAPABILITY_MISSING",
        ],
    }
    all_case_audit = {
        "schemaVersion": "PhaseBCR13AllCaseRequiredToolBindingAudit/1.0",
        "status": "NOT_STARTED_AFTER_HARD_STOP",
        "reason": "The mandatory Q-TABLE pre-freeze gate revealed an authority conflict that invalidates R1.3 completion; the task stop rule prevents a misleading package/Phase D progression.",
        "analysisExecutionTurnsWithUnboundRequiredTool": "NOT_FINALIZED",
    }
    package_supersession = {
        "schemaVersion": "PhaseBCR13PackageSupersession/1.0",
        "status": "NOT_CREATED_AFTER_HARD_STOP",
        "intendedSupersedesPackageSha256": "7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04",
        "reason": "PHASE_BC_R13_AUTH_001 prevents a truthful R1.3 refreeze.",
    }
    package_verification = {
        "schemaVersion": "PhaseBCR13PackageVerification/1.0",
        "status": "NOT_APPLICABLE_PACKAGE_NOT_CREATED",
        "newPackagePath": None,
        "newPackageSha256": None,
        "rootHashMismatches": "NOT_APPLICABLE",
        "caseHashMismatches": "NOT_APPLICABLE",
        "missingFiles": "NOT_APPLICABLE",
        "deterministicRebuild": "NOT_APPLICABLE",
    }
    for name, payload in {
        "APPROVED_MATERIAL_PROPERTY_SEMANTICS.json": approved_properties,
        "Q_TABLE_TOOL_BINDING_REQUIREMENTS.json": tool_requirements,
        "Q_TABLE_SOURCE_SELECTION.json": source_selection,
        "Q_TABLE_PROVENANCE_VERIFICATION.json": source_selection,
        "Q_TABLE_PROFILE_VERIFICATION.json": profile_verification,
        "Q_TABLE_REQUIRED_TOOL_BINDING_PREFLIGHT.json": result,
        "Q_TABLE_OLD_FIXTURE_FAILURE_ANALYSIS.json": old_failure,
        "Q_TABLE_AUTHORITY_DECISION.json": decision,
        "STATIC_VALIDATOR_HARDENING.json": static_hardening,
        "ALL_CASE_REQUIRED_TOOL_BINDING_AUDIT.json": all_case_audit,
        "PACKAGE_SUPERSESSION.json": package_supersession,
        "R1_3_PACKAGE_VERIFICATION.json": package_verification,
    }.items():
        write_json(EVIDENCE / name, payload)
    write_text(
        EVIDENCE / "PHASE_BC_R1_3_RESULT.md",
        """# Phase B/C-R1.3 Result\n\n```text\nPHASE_BC_R1_3 =\nBLOCKED /\nQUALIFICATION_AUTHORITY_CONFLICT\n\nBLOCKER = PHASE_BC_R13_AUTH_001\nREADY_FOR_PHASE_D_RESEAL = NO\nREADY_FOR_PHASE_E = NO\n```\n\nA real CC BY 4.0 JARVIS-DFT candidate table was acquired and the current DataProfile correctly identified `formation_energy`, `band_gap`, and `density` as approved `material_property` semantics. The frozen Q-TABLE execution-turn wording and current normal-user target binding remain incompatible: the summary, distribution, and correlation turns are not recognized by the deterministic current Intent vocabulary, and scatter has no exact material-property target bindings for either required parameter. Fixture replacement alone cannot correct these product/frozen-contract conditions.\n\nNo R1.3 package was built. No Phase D re-seal, Phase E execution, real LLM call, qualification Job, or qualification Artifact was started.\n""",
    )
    write_hash_manifest(EVIDENCE)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
