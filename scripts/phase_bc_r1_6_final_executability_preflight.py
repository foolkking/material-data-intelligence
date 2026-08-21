"""Run the final R1.6 content-and-contract executability preflight.

The preflight uses the frozen R1.6 package itself.  It does not call a real
provider, enqueue work, or create qualification runtime records.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for package in (
    "services/llm",
    "packages/material-parsers",
    "packages/tool-registry",
    "packages/schemas",
    "packages/artifact-core",
    "packages/adapters",
):
    sys.path.insert(0, str(ROOT / package))

from mdi_llm import AnalysisIntentRequest, DeterministicAnalysisIntentBuilder, MockLLMProvider, OpenAICompatibleProvider  # noqa: E402
from mdi_llm.capability_planner import plan_capabilities, resolve_eligibility  # noqa: E402
from mdi_tool_registry import build_artifact_compatibility_matrix, build_registry_snapshot, load_manifests  # noqa: E402
from mdi_tool_registry.dependency_ports import build_artifact_port_inventory  # noqa: E402
from mdi_tool_registry.plan_validator import validate_plan  # noqa: E402
from phase_bc_r1_6_executability_preflight import (  # noqa: E402
    expected_rejection_preflight,
    load_json,
    profile_for_case,
    write_json,
)


PACKAGE = ROOT / "_qualification" / "work" / "phase_bc_r1_6" / "authority_package"
HISTORICAL_R12 = ROOT / "_qualification" / "work" / "phase_bc_r1_2" / "package"
EVIDENCE = ROOT / "_qualification" / "evidence" / "phase_bc_r1_6" / "attempt_02_final_package_preflight"


def exact_provider(required_tools: list[str]) -> OpenAICompatibleProvider:
    def transport(**kwargs: object) -> dict[str, object]:
        context = json.loads(kwargs["messages"][-1]["content"])
        return {
            "choices": [{
                "message": {"content": json.dumps({
                    "schemaVersion": "1.0",
                    "resolutionId": context["eligibleCandidates"]["resolutionId"],
                    "selectedToolIds": required_tools,
                }, separators=(",", ":"))},
                "finish_reason": "stop",
            }]
        }
    return OpenAICompatibleProvider(transport=transport)


def turn_preflight(case: dict[str, Any], turn: dict[str, Any], profile: Any, registry: Any, metadata_by_id: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    question = turn["question"]
    entry: dict[str, Any] = {
        "caseId": case["caseId"],
        "turnId": turn["turnId"],
        "question": question,
        "requiredTools": turn["requiredExecutionTools"],
        "maxRequiredStepCount": turn["maxRequiredStepCount"],
        "planStepCap": case["currentPlanStepCap"],
        "issues": issues,
    }
    if turn["maxRequiredStepCount"] > case["currentPlanStepCap"]:
        issues.append({"code": "PLAN_STEP_CAP_CONFLICT", "message": "Turn exceeds its Case Plan step cap."})
    if len(set(turn["requiredExecutionTools"])) > turn["maxRequiredStepCount"]:
        issues.append({"code": "PLAN_STEP_CAP_CONFLICT", "message": "Required Tool set exceeds the turn cap."})
    if set(turn["requiredExecutionTools"]) & set(case.get("forbiddenExecutionTools", [])):
        issues.append({"code": "FORBIDDEN_TOOL_REQUIRED_AS_SUBSTITUTE", "message": "A required Tool is also forbidden by the Case."})
    selected_resource_ids = tuple(sorted(item.objectId for item in profile.resourceSemantics))
    intent = DeterministicAnalysisIntentBuilder().build(
        AnalysisIntentRequest(raw_goal=question, dataset_id=profile.datasetId, profile_id=profile.profileId, selected_resource_ids=selected_resource_ids),
        profile=profile,
        created_at="2026-08-16T00:00:00+00:00",
    )
    entry["intent"] = {
        "schemaVersion": intent.schemaVersion,
        "outcome": intent.outcome.value,
        "scientificIntents": [item.value for item in intent.scientificIntents],
        "requiredCapabilityNeeds": [item.value for item in intent.requiredCapabilityNeeds],
        "targetSemantics": [item.model_dump(mode="json") for item in intent.targetSemantics],
        "unsupportedReasons": [item.model_dump(mode="json") for item in intent.unsupportedReasons],
    }
    if intent.outcome.value != "READY":
        issues.append({"code": "EXECUTION_TURN_INTENT_NOT_RECOGNIZED", "message": "Current deterministic Intent did not reach READY."})
        entry["status"] = "BLOCKED"
        return entry

    resolution = resolve_eligibility(intent, profile=profile, registry=registry)
    candidates = {candidate.toolId: candidate for candidate in resolution.evaluatedCandidates}
    tool_results: list[dict[str, Any]] = []
    for tool_id in turn["requiredExecutionTools"]:
        candidate = candidates.get(tool_id)
        if candidate is None:
            issues.append({"code": "REQUIRED_TOOL_INTENT_MISMATCH", "message": f"{tool_id} was not evaluated."})
            continue
        bindings = [domain.model_dump(mode="json") for domain in candidate.bindingDomains]
        tool_results.append({"toolId": tool_id, "eligible": candidate.eligible, "bindingDomains": bindings, "reasons": [reason.model_dump(mode="json") for reason in candidate.reasons]})
        if not candidate.eligible:
            issues.append({"code": "REQUIRED_PARAMETER_BINDING_INCOMPLETE", "message": f"{tool_id} is not eligible with this exact Intent/Profile."})
        if any(binding.required for binding in metadata_by_id[tool_id].parameterBindings) and not bindings:
            issues.append({"code": "REQUIRED_PARAMETER_BINDING_INCOMPLETE", "message": f"{tool_id} has no complete binding domain."})
    entry["requiredToolResults"] = tool_results

    required_ids = sorted(set(turn["requiredExecutionTools"]))
    ports = build_artifact_port_inventory(registry)
    matrix = build_artifact_compatibility_matrix(registry, selected_tool_ids=required_ids)
    compatible_consumers = {pair.consumerToolId for pair in matrix.pairs if pair.compatible}
    required_dependency_consumers = {
        tool_id for tool_id in required_ids if ports[tool_id].inputPorts
    }
    unresolved_dependencies = sorted(required_dependency_consumers - compatible_consumers)
    entry["dependencyPreflight"] = {
        "requiredToolIds": required_ids,
        "requiredConsumerTools": sorted(required_dependency_consumers),
        "compatibleProducerConsumerPairs": [
            {
                "producerToolId": pair.producerToolId,
                "producerOutputPort": pair.producerOutputPort,
                "consumerToolId": pair.consumerToolId,
                "consumerInputPort": pair.consumerInputPort,
                "artifactContractVersion": pair.artifactContractVersion,
            }
            for pair in matrix.pairs
            if pair.compatible
        ],
        "unresolvedConsumerTools": unresolved_dependencies,
    }
    if unresolved_dependencies:
        issues.append({"code": "PLANNED_ARTIFACT_DEPENDENCY_CONFLICT", "message": "A required artifact consumer lacks a compatible required producer."})

    exact_selection_required = case["caseId"] == "Q-TABLE-001"
    provider = exact_provider(turn["requiredExecutionTools"]) if exact_selection_required else MockLLMProvider()
    planning = plan_capabilities(intent, profile=profile, registry=registry, provider=provider)
    plan = planning.plan
    validation = validate_plan(plan.model_dump(mode="json"), registry=registry) if plan is not None else None
    selected = [] if planning.decision is None else [selection.toolId for selection in planning.decision.selections]
    entry["planPreflight"] = {
        "outcome": planning.outcome.value,
        "selectedTools": selected,
        "schemaVersion": None if plan is None else plan.schemaVersion,
        "stepCount": 0 if plan is None else len(plan.steps),
        "validationOk": bool(validation and validation.ok),
        "validationErrors": [] if validation is None else [error.code for error in validation.errors],
        "decisionDiagnostics": [] if planning.decision is None else [diagnostic.code for diagnostic in planning.decision.diagnostics],
        "selectionPolicy": "EXACT_REQUIRED_TOOL_SELECTION" if exact_selection_required else "SCHEMA_AND_PLAN_CONTRACT_PROBE",
    }
    if planning.outcome.value != "PLAN_READY" or validation is None or not validation.ok:
        issues.append({"code": "PLAN_PREFLIGHT_INVALID", "message": "Exact required-tool selection did not yield a valid non-executing Plan."})
    elif exact_selection_required and selected != turn["requiredExecutionTools"]:
        issues.append({"code": "REQUIRED_TOOL_SELECTION_MISMATCH", "message": "Planner selection differs from Case requiredExecutionTools."})
    elif len(plan.steps) > case["currentPlanStepCap"]:
        issues.append({"code": "PLAN_STEP_CAP_CONFLICT", "message": "Plan exceeds current Case cap."})
    entry["status"] = "PASS" if not issues else "BLOCKED"
    return entry


def historical_qtable_failure(registry: Any, metadata_by_id: dict[str, Any]) -> list[dict[str, Any]]:
    case_dir = HISTORICAL_R12 / "03_Q-TABLE-001"
    case = load_json(case_dir / "CASE.json")
    profile, _, issues = profile_for_case(case_dir, case, "historical_qtable_r12")
    if issues or profile is None:
        return [{"code": "HISTORICAL_PROFILE_NOT_READY", "details": issues}]
    entries: list[dict[str, Any]] = []
    for turn in case["executionTurns"]:
        entry = turn_preflight(case, turn, profile, registry, metadata_by_id)
        entries.append({"turnId": turn["turnId"], "status": entry["status"], "issues": entry["issues"]})
    return entries


def main() -> None:
    index = load_json(PACKAGE / "CASE_INDEX.json")["cases"]
    registry = load_manifests()
    _, metadata_by_id = build_registry_snapshot(registry)
    cases: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    turns: list[dict[str, Any]] = []
    for item in index:
        case_dir = PACKAGE / item["directory"]
        case = load_json(case_dir / "CASE.json")
        if not case["analysisExecutionExpected"]:
            rejection = expected_rejection_preflight(case)
            cases.append({"caseId": case["caseId"], "caseType": case["caseType"], "status": rejection["status"], "turns": [], "expectedRejection": rejection})
            conflicts.extend({"caseId": case["caseId"], **issue} for issue in rejection["issues"])
            continue
        profile, resources, import_issues = profile_for_case(case_dir, case, f"r16_{case['caseId'].lower()}")
        case_turns: list[dict[str, Any]] = []
        case_issues = list(import_issues)
        if profile is not None:
            for turn in case["executionTurns"]:
                entry = turn_preflight(case, turn, profile, registry, metadata_by_id)
                case_turns.append(entry)
                turns.append(entry)
                case_issues.extend(entry["issues"])
                conflicts.extend({"caseId": case["caseId"], "turnId": turn["turnId"], **issue} for issue in entry["issues"])
        else:
            conflicts.extend({"caseId": case["caseId"], **issue} for issue in import_issues)
        cases.append({"caseId": case["caseId"], "caseType": case["caseType"], "status": "PASS" if not case_issues else "BLOCKED", "resources": resources, "importIssues": import_issues, "turns": case_turns})
    summary = {
        "caseCount": len(cases),
        "analysisExecutionCaseCount": sum(1 for case in cases if case["caseType"] != "EXPECTED_REJECTION"),
        "expectedRejectionCaseCount": sum(1 for case in cases if case["caseType"] == "EXPECTED_REJECTION"),
        "analysisExecutionTurnCount": len(turns),
        "passingCases": sum(1 for case in cases if case["status"] == "PASS"),
        "blockedCases": sorted({issue["caseId"] for issue in conflicts}),
        "issueCounts": {code: sum(1 for issue in conflicts if issue["code"] == code) for code in sorted({issue["code"] for issue in conflicts})},
        "allPrimaryExecutionTurnsPreflight": "PASS" if not conflicts else "FAIL",
    }
    result = {
        "schemaVersion": "PhaseBCR16AllCaseExecutabilityPreflight/4.0",
        "authorityUnderReview": "Phase_BC_R1_6_Qualification_Authority_Reconciled",
        "integrityAuthority": "CONTENT_AND_CONTRACT_VALIDATION",
        "executionMode": "NON_LLM_NON_FORMAL_QUALIFICATION",
        "cases": cases,
        "summary": summary,
        "executionCounters": {"realLlmCalls": 0, "formalQualificationExecutions": 0, "newQualificationJobs": 0, "newQualificationArtifacts": 0},
    }
    write_json(EVIDENCE / "ALL_CASE_EXECUTABILITY_PREFLIGHT.json", result)
    qtable = next(case for case in cases if case["caseId"] == "Q-TABLE-001")
    write_json(EVIDENCE / "Q_TABLE_EXECUTION_TURN_PREFLIGHT.json", {"caseId": "Q-TABLE-001", "result": qtable["status"], "turns": qtable["turns"]})
    write_json(EVIDENCE / "Q_TABLE_OLD_AUTHORITY_FAILURE_REPRODUCTION.json", {
        "historicalAuthority": "Phase_BC_R1_2_Qualification_Authority_Reconciled",
        "caseId": "Q-TABLE-001",
        "turns": historical_qtable_failure(registry, metadata_by_id),
        "purpose": "Reproduces the old content/contract failure without using a checksum identity.",
    })
    write_json(EVIDENCE / "PREFLIGHT_MODEL_RESULT.json", {
        "modelVersion": "4.0",
        "sourceBindings": "Actual R1.6 Case assets parsed into current DataProfile.",
        "plannedOutputBindings": "Exact required-tool Plans are constructed and schema-validated without execution.",
        "runtimeOnlyBindings": "Future Job, ToolCall, Artifact, and storage IDs are not pre-Plan requirements.",
        "exactSelectionPolicy": "The bounded fake provider selects the Case-declared required tools; current Planner binding and Plan validation decide whether that selection is legal.",
        "summary": summary,
    })
    print(json.dumps(summary, indent=2))
    if conflicts:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
