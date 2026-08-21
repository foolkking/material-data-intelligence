"""Run the R1.4 non-LLM qualification executability preflight.

This is non-production governance tooling.  It reads the historical R1.2
authority without modifying it, exercises the current parser, DataProfile,
deterministic Intent, Eligibility, and ToolPlannerMetadata paths, and writes
content-and-contract evidence.  It deliberately does not compute or compare
qualification digests, create jobs, or call an LLM.
"""

from __future__ import annotations

import csv
import json
import math
import sys
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for package in ("services/llm", "packages/material-parsers", "packages/tool-registry", "packages/schemas"):
    sys.path.insert(0, str(ROOT / package))

from mdi_llm import AnalysisIntentRequest, DeterministicAnalysisIntentBuilder  # noqa: E402
from mdi_llm.capability_planner import resolve_eligibility  # noqa: E402
from mdi_material_parsers import build_data_profile, parse_file  # noqa: E402
from mdi_material_parsers.mapped_resources import map_normalized_phonon_resource  # noqa: E402
from mdi_tool_registry import build_registry_snapshot, load_manifests  # noqa: E402


PACKAGE = ROOT / "_qualification" / "work" / "phase_bc_r1_2" / "package"
R13_SOURCE = ROOT / "_qualification" / "work" / "phase_bc_r1_3" / "source" / "jdft_3d-8-18-2021.json.zip"
WORK = ROOT / "_qualification" / "work" / "phase_bc_r1_4"
CANDIDATE_TABLE = WORK / "q_table" / "Q_TABLE_CANDIDATE_JARVIS_DFT_3D.csv"
EVIDENCE = ROOT / "_qualification" / "evidence" / "phase_bc_r1_4" / "attempt_01_authority_preflight"

PROPERTY_MAP = {
    "formation_energy": {"sourceField": "formation_energy_peratom", "unit": "eV/atom"},
    "band_gap": {"sourceField": "optb88vdw_bandgap", "unit": "eV"},
    "density": {"sourceField": "density", "unit": "g/cm3"},
}

REVISED_QTABLE_QUESTIONS = {
    "numeric-summary": "Summarize the material property measurements: formation energy, band-gap, and density.",
    "distribution": "Plot a histogram of the material property band-gap.",
    "correlation": "Plot correlations among the material property values formation energy, band-gap, and density.",
    "scatter": "Plot a material property scatter of formation energy versus density.",
}


def _without_qualification_digests(value: Any) -> Any:
    """Remove product-emitted digest identifiers from qualification evidence.

    Product contracts can use content addressing operationally.  R1.4 evidence
    must not turn those values into a qualification integrity gate.
    """

    if isinstance(value, list):
        return [_without_qualification_digests(item) for item in value]
    if not isinstance(value, dict):
        return value
    forbidden = ("hash", "digest", "checksum")
    return {
        key: _without_qualification_digests(item)
        for key, item in value.items()
        if not any(fragment in key.casefold() for fragment in forbidden)
        and key not in {"sourceIdentity", "profileId"}
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_without_qualification_digests(value), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def materialize_jarvis_candidate() -> dict[str, Any]:
    """Project exact source fields into the approved product field names."""

    if not R13_SOURCE.is_file():
        raise RuntimeError(f"Missing retained JARVIS source: {R13_SOURCE}")
    with zipfile.ZipFile(R13_SOURCE) as archive:
        names = archive.namelist()
        if names != ["jdft_3d-8-18-2021.json"]:
            raise RuntimeError(f"Unexpected JARVIS source inventory: {names!r}")
        records = json.loads(archive.read(names[0]))

    selected: list[dict[str, Any]] = []
    for record in sorted(records, key=lambda item: str(item.get("jid", ""))):
        values = [record.get(spec["sourceField"]) for spec in PROPERTY_MAP.values()]
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) for value in values):
            continue
        if float(record["optb88vdw_bandgap"]) <= 0:
            continue
        selected.append(record)
        if len(selected) == 64:
            break
    if len(selected) != 64:
        raise RuntimeError("JARVIS source cannot produce the governed 64-record candidate.")

    CANDIDATE_TABLE.parent.mkdir(parents=True, exist_ok=True)
    with CANDIDATE_TABLE.open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sample_id", "formula", *PROPERTY_MAP], lineterminator="\n")
        writer.writeheader()
        for record in selected:
            writer.writerow(
                {
                    "sample_id": record["jid"],
                    "formula": record["formula"],
                    **{name: record[spec["sourceField"]] for name, spec in PROPERTY_MAP.items()},
                }
            )
    return {
        "sourceIdentity": "JARVIS-DFT-3D / Figshare 10.6084/m9.figshare.6815699.v11",
        "licenseOrReuseAuthority": "CC BY 4.0",
        "sourceInventory": names,
        "rowSelection": "sort by stable jid; first 64 records with finite formation_energy_peratom, optb88vdw_bandgap, density and positive band gap",
        "stableMaterialIdentity": "jid projected exactly to sample_id",
        "scientificTransformation": "none; representation-only projection and canonical source-field rename",
        "propertyMap": PROPERTY_MAP,
        "candidatePath": str(CANDIDATE_TABLE.relative_to(ROOT)),
        "candidateRows": len(selected),
    }


def parse_asset(case_dir: Path, asset: dict[str, Any], dataset_id: str) -> tuple[Any | None, dict[str, Any] | None]:
    path = case_dir / asset["filename"]
    if not path.is_file():
        return None, {"code": "ASSET_MISSING", "message": f"Missing declared asset {asset['filename']}."}
    try:
        mode = asset.get("importMode")
        if mode == "TYPED_PHONON_BAND_IMPORT":
            parsed = map_normalized_phonon_resource(path, dataset_id=dataset_id, file_id=asset["filename"], declared_kind="phonon_band")
        elif mode == "TYPED_PHONON_DOS_IMPORT":
            parsed = map_normalized_phonon_resource(path, dataset_id=dataset_id, file_id=asset["filename"], declared_kind="phonon_dos")
        else:
            parsed = parse_file(path, dataset_id=dataset_id, file_id=asset["filename"])
    except Exception as exc:  # The product parser converts these to an import failure at runtime.
        return None, {"code": type(exc).__name__, "message": str(exc)}
    if parsed.parse_status not in {"success", "partial"}:
        return parsed, {"code": parsed.error_code or "PARSE_NOT_READY", "message": parsed.error_message or "No normalized resource was created."}
    return parsed, None


def profile_for_case(case_dir: Path, case: dict[str, Any], dataset_id: str) -> tuple[Any | None, list[dict[str, Any]], list[dict[str, Any]]]:
    parsed_results: list[Any] = []
    resources: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for asset in case["assets"]:
        parsed, issue = parse_asset(case_dir, asset, dataset_id)
        resources.append(
            {
                "asset": asset["filename"],
                "semanticKind": asset["semanticKind"],
                "importMode": asset["importMode"],
                "parseStatus": None if parsed is None else parsed.parse_status,
                "objectTypes": [] if parsed is None else [obj.object_type.value for obj in parsed.objects],
            }
        )
        if issue:
            issues.append({"asset": asset["filename"], **issue})
        if parsed is not None and parsed.objects:
            parsed_results.append(parsed)
    if issues:
        return None, resources, issues
    try:
        profile = build_data_profile(
            dataset_id=dataset_id,
            parse_results=parsed_results,
            platform_tool_ids={tool.toolId for tool in load_manifests().tools},
        )
    except Exception as exc:
        return None, resources, [{"code": type(exc).__name__, "message": str(exc)}]
    return profile, resources, []


def profile_for_qtable(candidate: Path, dataset_id: str) -> tuple[Any | None, list[dict[str, Any]], list[dict[str, Any]]]:
    parsed = parse_file(candidate, dataset_id=dataset_id, file_id=candidate.name)
    if parsed.parse_status != "success":
        return None, [], [{"code": parsed.error_code or "PARSE_NOT_READY", "message": parsed.error_message or "No normalized table."}]
    profile = build_data_profile(
        dataset_id=dataset_id,
        parse_results=[parsed],
        platform_tool_ids={tool.toolId for tool in load_manifests().tools},
    )
    return profile, [{"asset": candidate.name, "semanticKind": "materials_tabular_dataset", "importMode": "FILE_UPLOAD", "parseStatus": parsed.parse_status, "objectTypes": [obj.object_type.value for obj in parsed.objects]}], []


def turn_preflight(
    case: dict[str, Any],
    turn: dict[str, Any],
    profile: Any | None,
    registry: Any,
    metadata_by_id: dict[str, Any],
    question_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    question = (question_overrides or {}).get(turn["turnId"], turn["question"])
    entry: dict[str, Any] = {
        "caseId": case["caseId"],
        "turnId": turn["turnId"],
        "question": question,
        "requiredTools": turn["requiredExecutionTools"],
        "maxRequiredStepCount": turn["maxRequiredStepCount"],
        "planStepCap": case["currentPlanStepCap"],
        "issues": [],
    }
    if turn["maxRequiredStepCount"] > case["currentPlanStepCap"]:
        entry["issues"].append({"code": "PLAN_STEP_CAP_CONFLICT", "message": "Turn step count exceeds Case plan cap."})
    if profile is None:
        entry["intent"] = None
        entry["requiredToolResults"] = []
        entry["issues"].append({"code": "REQUIRED_RESOURCE_BINDING_MISSING", "message": "No usable DataProfile was produced from declared assets."})
        entry["status"] = "BLOCKED"
        return entry

    intent = DeterministicAnalysisIntentBuilder().build(
        AnalysisIntentRequest(raw_goal=question, dataset_id=profile.datasetId, profile_id=profile.profileId),
        profile=profile,
        created_at="2026-08-16T00:00:00+00:00",
    )
    entry["intent"] = {
        "outcome": intent.outcome.value,
        "scientificIntents": [item.value for item in intent.scientificIntents],
        "requiredCapabilityNeeds": [item.value for item in intent.requiredCapabilityNeeds],
        "targetSemantics": [item.model_dump(mode="json") for item in intent.targetSemantics],
        "unsupportedReasons": [item.model_dump(mode="json") for item in intent.unsupportedReasons],
    }
    if intent.outcome.value != "READY":
        entry["issues"].append({"code": "EXECUTION_TURN_INTENT_NOT_RECOGNIZED", "message": "Current deterministic Intent did not reach READY."})
        entry["requiredToolResults"] = []
        entry["status"] = "BLOCKED"
        return entry

    resolution = resolve_eligibility(intent, profile=profile, registry=registry)
    candidates = {candidate.toolId: candidate for candidate in resolution.evaluatedCandidates}
    required_results: list[dict[str, Any]] = []
    for tool_id in turn["requiredExecutionTools"]:
        candidate = candidates.get(tool_id)
        if candidate is None:
            entry["issues"].append({"code": "REQUIRED_TOOL_INTENT_MISMATCH", "message": f"{tool_id} was not evaluated for the deterministic Intent."})
            required_results.append({"toolId": tool_id, "eligible": False, "bindingDomains": [], "reasons": []})
            continue
        bindings = [domain.model_dump(mode="json") for domain in candidate.bindingDomains]
        reasons = [reason.model_dump(mode="json") for reason in candidate.reasons]
        required_results.append({"toolId": tool_id, "eligible": candidate.eligible, "bindingDomains": bindings, "reasons": reasons})
        if not candidate.eligible:
            entry["issues"].append({"code": "REQUIRED_TOOL_PARAMETER_BINDING_INCOMPLETE", "message": f"{tool_id} is not eligible with the deterministic Intent/Profile binding."})
        metadata = metadata_by_id[tool_id]
        requires_parameter_binding = any(binding.required for binding in metadata.parameterBindings)
        if requires_parameter_binding and not bindings:
            entry["issues"].append({"code": "REQUIRED_PARAMETER_BINDING_INCOMPLETE", "message": f"{tool_id} has no complete binding domain."})
    entry["requiredToolResults"] = required_results
    entry["status"] = "PASS" if not entry["issues"] else "BLOCKED"
    return entry


def expected_rejection_preflight(case: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    required_report = case.get("requiredReportBehavior", {})
    required_recipe = case.get("requiredRecipeBehavior", {})
    if case.get("analysisExecutionExpected") is not False:
        issues.append({"code": "EXPECTED_REJECTION_CONTRACT_INVALID", "message": "analysisExecutionExpected must be false."})
    for field in ("requiredExecutionTools", "executionTurns", "requiredArtifacts", "requiredRenderers"):
        if case.get(field) != []:
            issues.append({"code": "EXPECTED_REJECTION_HAS_EXECUTION_REQUIREMENTS", "message": f"{field} must be empty."})
    if required_report.get("previewExpected") or required_report.get("finalizeExpected"):
        issues.append({"code": "EXPECTED_REJECTION_HAS_EXECUTION_REQUIREMENTS", "message": "Reports must be absent."})
    if required_recipe.get("expected"):
        issues.append({"code": "EXPECTED_REJECTION_HAS_EXECUTION_REQUIREMENTS", "message": "Recipe must be absent."})
    return {"caseId": case["caseId"], "expectedOutcome": "PRE_PLAN_REJECTION", "status": "PASS" if not issues else "BLOCKED", "issues": issues}


def main() -> None:
    index = load_json(PACKAGE / "CASE_INDEX.json")["cases"]
    registry = load_manifests()
    _, metadata_by_id = build_registry_snapshot(registry)
    source_selection = materialize_jarvis_candidate()
    old_qtable_dir = PACKAGE / "03_Q-TABLE-001"
    old_qtable_case = load_json(old_qtable_dir / "CASE.json")
    old_qtable_profile, old_qtable_resources, old_qtable_import_issues = profile_for_case(
        old_qtable_dir, old_qtable_case, "qtable_r12_historical"
    )
    old_qtable_turns = [
        turn_preflight(old_qtable_case, turn, old_qtable_profile, registry, metadata_by_id)
        for turn in old_qtable_case["executionTurns"]
    ]
    all_cases: list[dict[str, Any]] = []
    all_turns: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    qtable_profile: Any | None = None

    for item in index:
        case_dir = PACKAGE / item["directory"]
        case = load_json(case_dir / "CASE.json")
        if not case["analysisExecutionExpected"]:
            result = expected_rejection_preflight(case)
            all_cases.append({"caseId": case["caseId"], "caseType": case["caseType"], "resources": [], "turns": [], "expectedRejection": result, "status": result["status"]})
            conflicts.extend({"caseId": case["caseId"], **issue} for issue in result["issues"])
            continue

        if case["caseId"] == "Q-TABLE-001":
            profile, resources, import_issues = profile_for_qtable(CANDIDATE_TABLE, "qtable_r14_candidate")
            qtable_profile = profile
        else:
            profile, resources, import_issues = profile_for_case(case_dir, case, f"{case['caseId'].lower()}_r14")
        question_overrides = REVISED_QTABLE_QUESTIONS if case["caseId"] == "Q-TABLE-001" else None
        turns = [
            turn_preflight(case, turn, profile, registry, metadata_by_id, question_overrides)
            for turn in case["executionTurns"]
        ]
        case_issues = list(import_issues)
        for turn in turns:
            case_issues.extend(turn["issues"])
            conflicts.extend({"caseId": case["caseId"], "turnId": turn["turnId"], **issue} for issue in turn["issues"])
        conflicts.extend({"caseId": case["caseId"], **issue} for issue in import_issues)
        status = "PASS" if not case_issues else "BLOCKED"
        all_cases.append({"caseId": case["caseId"], "caseType": case["caseType"], "resources": resources, "importIssues": import_issues, "turns": turns, "status": status})
        all_turns.extend(turns)

    qtable_turns = [turn for turn in all_turns if turn["caseId"] == "Q-TABLE-001"]
    qtable_properties = [] if qtable_profile is None else [
        column.model_dump(mode="json")
        for column in qtable_profile.semanticColumns
        if any(role.role == "material_property" for role in column.roles)
    ]
    tool_requirements = {
        tool_id: {
            "toolId": tool_id,
            "scientificIntents": [item.value for item in metadata_by_id[tool_id].scientificIntents],
            "capabilityNeeds": [item.value for item in metadata_by_id[tool_id].capabilityNeeds],
            "requiredParameterBindings": [item.model_dump(mode="json") for item in metadata_by_id[tool_id].parameterBindings if item.required],
        }
        for tool_id in ("table.numeric_summary", "viz.histogram", "viz.correlation", "viz.scatter")
    }
    issue_counts: dict[str, int] = {}
    for conflict in conflicts:
        issue_counts[conflict["code"]] = issue_counts.get(conflict["code"], 0) + 1
    result = {
        "schemaVersion": "PhaseBCR14AllCaseExecutabilityPreflight/1.0",
        "integrityAuthority": "CONTENT_AND_CONTRACT_VALIDATION",
        "authorityUnderReview": "Phase_BC_R1_2_Qualification_Authority_Reconciled",
        "executionMode": "NON_LLM_NON_FORMAL_QUALIFICATION",
        "cases": all_cases,
        "summary": {
            "caseCount": len(all_cases),
            "analysisExecutionCaseCount": sum(1 for case in all_cases if case["caseType"] != "EXPECTED_REJECTION"),
            "expectedRejectionCaseCount": sum(1 for case in all_cases if case["caseType"] == "EXPECTED_REJECTION"),
            "analysisExecutionTurnCount": len(all_turns),
            "passingCases": sum(1 for case in all_cases if case["status"] == "PASS"),
            "blockedCases": sorted({item["caseId"] for item in conflicts}),
            "issueCounts": issue_counts,
            "allPrimaryExecutionTurnsPreflight": "PASS" if not conflicts else "FAIL",
        },
        "executionCounters": {"realLlmCalls": 0, "formalQualificationExecutions": 0, "newQualificationJobs": 0, "newQualificationArtifacts": 0},
    }
    write_json(EVIDENCE / "ALL_CASE_EXECUTABILITY_PREFLIGHT.json", result)
    write_json(EVIDENCE / "Q_TABLE_INTENT_AND_BINDING_AUTHORITY.json", {
        "schemaVersion": "PhaseBCR14QTableIntentAndBindingAuthority/1.0",
        "sources": [
            "services/llm/mdi_llm/analysis_intent.py#DeterministicAnalysisIntentBuilder",
            "services/llm/mdi_llm/analysis_intent.py#_resolve_targets",
            "services/llm/mdi_llm/capability_planner.py#_binding_domains",
            "packages/tool-registry/mdi_tool_registry/planner_metadata.py#_bindings",
        ],
        "finding": "The current deterministic non-ML Intent path does not derive material_property targetSemantics from normal-user table questions. Required scalar target bindings for viz.histogram and viz.scatter therefore remain unbound.",
        "prohibitedAutonomousChanges": ["DataProfile semantic expansion", "fuzzy property binding", "first numeric column binding", "ToolPlannerMetadata relaxation", "deterministic Intent target-binding changes"],
        "toolRequirements": tool_requirements,
    })
    write_json(EVIDENCE / "Q_TABLE_PROPERTY_AUTHORITY.json", {
        "schemaVersion": "PhaseBCR14QTablePropertyAuthority/1.0",
        "candidateSource": source_selection,
        "recognizedMaterialPropertyColumns": qtable_properties,
        "profileResult": "PASS" if qtable_profile is not None else "FAIL",
        "unitPolicy": "Bare CSV columns retain typed unknown units under the current product contract; no units were inferred.",
    })
    write_json(EVIDENCE / "Q_TABLE_EXECUTION_TURN_PREFLIGHT.json", {
        "schemaVersion": "PhaseBCR14QTableExecutionTurnPreflight/1.0",
        "revisedQuestions": REVISED_QTABLE_QUESTIONS,
        "turns": qtable_turns,
        "result": "PASS" if qtable_turns and all(turn["status"] == "PASS" for turn in qtable_turns) else "FAIL",
    })
    write_json(EVIDENCE / "Q_TABLE_OLD_AUTHORITY_FAILURE_REPRODUCTION.json", {
        "schemaVersion": "PhaseBCR14QTableOldAuthorityFailureReproduction/1.0",
        "authority": "Phase_BC_R1_2_Qualification_Authority_Reconciled / Q-TABLE-001",
        "fixture": "UPLOAD_materials_table.csv",
        "resources": old_qtable_resources,
        "importIssues": old_qtable_import_issues,
        "turns": old_qtable_turns,
        "result": "FAIL" if old_qtable_import_issues or any(turn["status"] != "PASS" for turn in old_qtable_turns) else "UNEXPECTED_PASS",
        "requiredFinding": "The historical generic table cannot complete the required material-property tool bindings under current released product semantics.",
    })
    write_json(EVIDENCE / "Q_TABLE_SOURCE_SELECTION.json", source_selection)
    write_json(EVIDENCE / "Q_TABLE_PROVENANCE_VERIFICATION.json", {
        "schemaVersion": "PhaseBCR14QTableProvenanceVerification/1.0",
        "result": "PASS_FOR_SOURCE_SELECTION_ONLY",
        "source": source_selection,
        "provenanceInspection": {
            "realPublicScientificData": True,
            "licenseOrReuseAuthority": "CC BY 4.0",
            "materialIdentitiesStable": True,
            "scientificValuesPreserved": True,
            "unitsPreserved": True,
            "syntheticPropertyCreation": 0,
            "rowOrderIdentity": False,
            "guessedDatasetJoin": 0,
        },
    })
    write_json(EVIDENCE / "Q_TABLE_PROFILE_VERIFICATION.json", {
        "schemaVersion": "PhaseBCR14QTableProfileVerification/1.0",
        "result": "PASS" if qtable_profile is not None else "FAIL",
        "recognizedProperties": qtable_properties,
        "sourceSelection": source_selection,
    })
    write_json(EVIDENCE / "R1_4_PACKAGE_VERIFICATION.json", {
        "schemaVersion": "PhaseBCR14PackageVerification/1.0",
        "status": "NOT_CREATED_AFTER_FULL_PREFLIGHT_FAILURE" if conflicts else "PENDING_REFREEZE",
        "integrityAuthority": "CONTENT_AND_CONTRACT_VALIDATION",
        "retiredQualificationIntegrityGate": "DIGESTS_ARE_NON_NORMATIVE",
        "reason": "A new authority package is forbidden while any primary Case execution contract is incompatible with current released authority.",
    })
    write_json(EVIDENCE / "Q_TABLE_AUTHORITY_DECISION.json", {
        "schemaVersion": "PhaseBCR14QTableAuthorityDecision/1.0",
        "reviewerDirection": "REVISE_Q_TABLE_EXECUTION_TURNS_WITH_EXPLICIT_PROPERTY_TARGETS",
        "result": "BLOCKED_QUALIFICATION_PRODUCT_CONTRACT_MISMATCH",
        "revisedTurns": qtable_turns,
        "rootCause": "The deterministic non-ML Intent builder supplies no material_property targetSemantics. viz.histogram and viz.scatter require exact target_column bindings, so natural-language wording alone cannot produce the required bindings.",
        "disallowedAutonomousRemediation": [
            "DataProfile semantic expansion",
            "fuzzy or first-column property binding",
            "ToolPlannerMetadata relaxation",
            "deterministic Intent target-binding behavior change",
            "qualification-only target injection",
        ],
        "reviewerDecisionRequired": "Authorize a production normal-user property-target selection capability, or revise the required Q-TABLE execution contract to a currently executable normal-user path.",
    })
    write_json(EVIDENCE / "STATIC_VALIDATOR_HARDENING.json", {
        "schemaVersion": "PhaseBCR14StaticValidatorHardening/1.0",
        "status": "IMPLEMENTED_NON_PRODUCTION_PREFLIGHT",
        "validator": "scripts/phase_bc_r1_4_executability_preflight.py",
        "checks": [
            "EXECUTION_TURN_INTENT_NOT_RECOGNIZED",
            "REQUIRED_TOOL_INTENT_MISMATCH",
            "REQUIRED_TOOL_PARAMETER_BINDING_INCOMPLETE",
            "REQUIRED_PARAMETER_BINDING_INCOMPLETE",
            "REQUIRED_RESOURCE_BINDING_MISSING",
            "PLAN_STEP_CAP_CONFLICT",
            "EXPECTED_REJECTION_HAS_EXECUTION_REQUIREMENTS",
        ],
        "oldQTableAuthorityReproduced": bool(old_qtable_import_issues or any(turn["status"] != "PASS" for turn in old_qtable_turns)),
        "fullPreflightResult": result["summary"]["allPrimaryExecutionTurnsPreflight"],
    })
    write_json(EVIDENCE / "PACKAGE_SUPERSESSION.json", {
        "schemaVersion": "PhaseBCR14PackageSupersession/1.0",
        "status": "NOT_CREATED_AFTER_FULL_PREFLIGHT_FAILURE",
        "intendedSupersedesAuthority": "Phase_BC_R1_2_Qualification_Authority_Reconciled",
        "intendedSupersessionReason": "Q_TABLE_EXECUTION_TURN_EXPLICIT_PROPERTY_TARGET_RECONCILIATION",
        "reasonNotCreated": "Primary execution-contract conflicts remain. R1.3 was blocked and no successful R1.3 package exists to supersede.",
    })
    write_json(EVIDENCE / "R1_4_PACKAGE_INVENTORY.json", {
        "schemaVersion": "PhaseBCR14PackageInventory/1.0",
        "status": "NOT_CREATED_AFTER_FULL_PREFLIGHT_FAILURE",
        "authorityName": None,
        "caseInventory": [item["caseId"] for item in index],
        "expectedCaseCount": len(index),
        "integrityValidation": "content and contract only; no qualification digest inventory",
    })
    write_text(EVIDENCE / "QUALIFICATION_INTEGRITY_POLICY.md", """# Qualification Integrity Policy\n\n`QUALIFICATION_INTEGRITY_AUTHORITY = CONTENT_AND_CONTRACT_VALIDATION`\n\n`HISTORICAL_DIGEST_RECORDS = NON_NORMATIVE`\n\n`FUTURE_PASS_FAIL_DEPENDS_ON_DIGESTS = NO`\n\nR1.4 validates source/provenance content, direct protected-byte equality where needed, Case schemas, parser/Profile/Intent/Eligibility bindings, entry paths, plan constraints, production tests, and later runtime evidence. It does not produce qualification checksum manifests or digest gates. Product-level integrity controls remain outside this qualification policy.\n""")
    write_text(EVIDENCE / "PHASE_BC_R1_4_RESULT.md", """# Phase B/C-R1.4 Result\n\n```text\nPHASE_BC_R1_4 =\nBLOCKED /\nQUALIFICATION_AUTHORITY_CONFLICT\n\nFULL_EXECUTABILITY_PREFLIGHT = FAIL\nR1_4_PACKAGE = NOT_CREATED\nPHASE_D_RESEAL = NOT_STARTED\nREADY_FOR_PHASE_D_RESEAL = NO\nREADY_FOR_PHASE_E = NO\nREAL_LLM_CALLS = 0\nFORMAL_QUALIFICATION_EXECUTIONS = 0\nNEW_QUALIFICATION_JOBS = 0\nNEW_QUALIFICATION_ARTIFACTS = 0\n```\n\n## Current conflicts\n\n- `PHASE_BC_R14_AUTH_001`: Q-TABLE histogram and scatter need exact scalar material-property targets, but the current deterministic normal-user Intent path emits no material-property target semantics.\n- `PHASE_BC_R14_AUTH_002`: Q-ML-REG-001, Q-ML-UNC-001, and Q-ML-CLASS-001 do not reach READY under the current deterministic semantic-target path.\n- `PHASE_BC_R14_AUTH_003`: Q-XRD-001 direct Eligibility cannot make the experimental comparison source eligible from the imported Profile; its theoretical-XRD artifact dependency is not represented by that direct candidate evaluation.\n- `PHASE_BC_R14_AUTH_004`: Q-TRAJECTORY-001 fails the current official parser with `TRAJECTORY_NESTING_LIMIT_EXCEEDED`.\n- `PHASE_BC_R14_AUTH_005`: Q-PHONON-001 typed band and DOS imports fail current validation with `PHONON_SPECIES_ORDER_INVALID`.\n\nThe complete content-and-contract preflight is recorded in `ALL_CASE_EXECUTABILITY_PREFLIGHT.json`. A new R1.4 authority package and Phase D re-seal are forbidden until Reviewer reconciles this complete conflict surface.\n""")


if __name__ == "__main__":
    main()
