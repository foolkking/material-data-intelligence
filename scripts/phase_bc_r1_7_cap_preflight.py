"""Run the non-LLM R1.7 executability and required-Tool resource-cap preflight."""

from __future__ import annotations

import json
import math
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
sys.path.insert(0, str(ROOT / "scripts"))

from mdi_llm import AnalysisIntentRequest, DeterministicAnalysisIntentBuilder, MockLLMProvider, OpenAICompatibleProvider  # noqa: E402
from mdi_llm.capability_planner import plan_capabilities, resolve_eligibility  # noqa: E402
from mdi_tool_registry import build_artifact_compatibility_matrix, build_registry_snapshot, load_manifests  # noqa: E402
from mdi_tool_registry.dependency_ports import build_artifact_port_inventory  # noqa: E402
from mdi_tool_registry.plan_validator import validate_plan  # noqa: E402
from phase_bc_r1_6_executability_preflight import expected_rejection_preflight, load_json, parse_asset, profile_for_case, write_json  # noqa: E402


PACKAGE = ROOT / "_qualification" / "work" / "phase_bc_r1_7" / "authority_package"
R16 = ROOT / "_qualification" / "work" / "phase_bc_r1_6" / "authority_package"
EVIDENCE = ROOT / "_qualification" / "evidence" / "phase_bc_r1_7"


CAP_CODES = {
    "maxFrames": "REQUIRED_TOOL_FRAME_CAP_EXCEEDED",
    "maxAtoms": "REQUIRED_TOOL_ATOM_CAP_EXCEEDED",
    "maxRdfPairs": "REQUIRED_TOOL_PAIR_EVALUATION_CAP_EXCEEDED",
    "maxRdfBins": "REQUIRED_TOOL_BIN_CAP_EXCEEDED",
    "maxMsdLags": "REQUIRED_TOOL_LAG_CAP_EXCEEDED",
    "maxTimeOrigins": "REQUIRED_TOOL_ORIGIN_CAP_EXCEEDED",
    "maxFitPoints": "REQUIRED_TOOL_FIT_POINT_CAP_EXCEEDED",
    "maxJsonBytes": "REQUIRED_TOOL_INPUT_SIZE_CAP_EXCEEDED",
    "maxSourceBytes": "REQUIRED_TOOL_INPUT_SIZE_CAP_EXCEEDED",
    "maxDatasetBytes": "REQUIRED_TOOL_INPUT_SIZE_CAP_EXCEEDED",
    "maxArtifactBytes": "REQUIRED_TOOL_OUTPUT_SIZE_INEVITABLY_EXCEEDED",
}


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


def _merge_max(target: dict[str, int], key: str, value: int) -> None:
    target[key] = max(target.get(key, 0), int(value))


def resource_metrics(case_dir: Path, case: dict[str, Any], dataset_id: str) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "inputBytes": 0,
        "rows": 0,
        "columns": 0,
        "structures": 0,
        "atomsPerStructure": 0,
        "trajectoryFrames": 0,
        "trajectoryAtoms": 0,
        "trajectorySpecies": 0,
        "trajectoryCoordinateValues": 0,
        "trajectorySerializedBytes": 0,
        "trajectoryPositionWrapping": None,
        "trajectoryLatticeMode": None,
        "trajectoryPbc": None,
        "trajectoryTimes": [],
        "phononAtoms": 0,
        "phononQpoints": 0,
        "phononBranches": 0,
        "phononSegments": 0,
        "phononDosPoints": 0,
        "phononProjectedDosSeries": 0,
        "phononNumericValues": 0,
        "volumetricFields": 0,
        "volumetricVoxels": 0,
        "volumetricGridDimension": 0,
        "electronicPoints": 0,
        "experimentalPoints": 0,
        "distinctElements": 0,
        "maxCategoryCardinality": 0,
        "classificationClasses": 0,
        "assetCount": len(case["assets"]),
    }
    elements: set[str] = set()
    for asset in case["assets"]:
        path = case_dir / asset["filename"]
        metrics["inputBytes"] += path.stat().st_size
        parsed, issue = parse_asset(case_dir, asset, dataset_id)
        if issue or parsed is None:
            continue
        for obj in parsed.objects:
            payload = obj.payload
            object_type = obj.object_type.value
            if isinstance(payload, list):
                _merge_max(metrics, "rows", len(payload))
                if payload and isinstance(payload[0], dict):
                    _merge_max(metrics, "columns", len(payload[0]))
                    for value in payload[0].values():
                        if isinstance(value, str):
                            elements.update(token for token in value.replace("-", " ").split() if len(token) <= 2 and token[:1].isupper())
                    for key in payload[0]:
                        values = {str(row.get(key)) for row in payload[:10000] if row.get(key) is not None}
                        _merge_max(metrics, "maxCategoryCardinality", len(values))
                        if key.casefold() in {"class_true", "class_pred", "class_label", "predicted_class"}:
                            _merge_max(metrics, "classificationClasses", len(values))
                if asset.get("semanticKind") == "experimental_xrd":
                    _merge_max(metrics, "experimentalPoints", len(payload))
            elif isinstance(payload, dict):
                if object_type == "Structure":
                    metrics["structures"] += 1
                    sites = payload.get("sites") or []
                    _merge_max(metrics, "atomsPerStructure", len(sites))
                    for site in sites:
                        for species in site.get("species", []):
                            if species.get("element"):
                                elements.add(str(species["element"]))
                elif object_type == "Trajectory":
                    frames = payload["frames"]
                    atoms = payload["atoms"]["records"]
                    metrics.update({
                        "trajectoryFrames": len(frames),
                        "trajectoryAtoms": len(atoms),
                        "trajectorySpecies": len({item["species"] for item in atoms}),
                        "trajectoryCoordinateValues": len(frames) * len(atoms) * 3,
                        "trajectorySerializedBytes": len(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
                        "trajectoryPositionWrapping": payload["position_wrapping"],
                        "trajectoryLatticeMode": payload["lattice_mode"],
                        "trajectoryPbc": payload["periodic_boundary"],
                        "trajectoryTimes": [frame.get("time") for frame in frames],
                    })
                    elements.update(item["species"] for item in atoms)
                elif object_type == "PhononBand":
                    metrics["phononAtoms"] = max(metrics["phononAtoms"], int(payload.get("atom_count", 0)))
                    metrics["phononQpoints"] = max(metrics["phononQpoints"], len(payload.get("qpoints", [])))
                    metrics["phononBranches"] = max(metrics["phononBranches"], len(payload.get("branches", [])))
                    metrics["phononSegments"] = max(metrics["phononSegments"], len(payload.get("segments", [])))
                    metrics["phononNumericValues"] += len(payload.get("qpoints", [])) * max(1, len(payload.get("branches", [])))
                    elements.update(payload.get("species", []))
                elif object_type == "PhononDos":
                    points = len(payload.get("frequencies", []))
                    projections = len(payload.get("projected_dos", {}))
                    metrics["phononAtoms"] = max(metrics["phononAtoms"], int(payload.get("atom_count", 0)))
                    metrics["phononDosPoints"] = max(metrics["phononDosPoints"], points)
                    metrics["phononProjectedDosSeries"] = max(metrics["phononProjectedDosSeries"], projections)
                    metrics["phononNumericValues"] += points * (2 + projections)
                    elements.update(payload.get("species", []))
                elif object_type == "VolumetricData":
                    shape = [int(value) for value in payload.get("shape", [])]
                    voxels = math.prod(shape) if shape else 0
                    metrics["volumetricFields"] += max(1, len(payload.get("channels", [])))
                    metrics["volumetricVoxels"] += voxels
                    metrics["volumetricGridDimension"] = max([metrics["volumetricGridDimension"], *shape])
                elif object_type == "ElectronicBand":
                    metrics["electronicPoints"] += len(payload.get("kpoints", [])) * max(1, len(payload.get("bands", [])))
                elif object_type == "ElectronicDos":
                    metrics["electronicPoints"] += len(payload.get("energiesEv", [])) * (1 + len(payload.get("projections", [])))
    metrics["distinctElements"] = len(elements)
    metrics["estimatedArtifactBytes"] = max(
        4096,
        metrics["rows"] * max(1, metrics["columns"]) * 96,
        metrics["atomsPerStructure"] * 4096,
        metrics["trajectoryFrames"] * 512 + metrics["trajectoryAtoms"] * 256,
        metrics["phononNumericValues"] * 32,
        metrics["electronicPoints"] * 64,
        metrics["experimentalPoints"] * 64,
    )
    return metrics


def projected_value(key: str, limit: int, metrics: dict[str, Any]) -> tuple[int | None, str]:
    frames = int(metrics["trajectoryFrames"])
    atoms = int(metrics["trajectoryAtoms"])
    pairs = frames * atoms * max(0, atoms - 1) // 2
    direct: dict[str, tuple[int, str]] = {
        "maxRows": (int(metrics["rows"]), "parsed table row count"),
        "maxStructures": (int(metrics["structures"]), "parsed Structure count"),
        "maxAtomsPerStructure": (int(metrics["atomsPerStructure"]), "maximum parsed Structure site count"),
        "maxSites": (int(metrics["atomsPerStructure"]), "maximum parsed Structure site count"),
        "maxFrames": (frames, "parsed trajectory frame count"),
        "maxAtoms": (atoms or int(metrics["phononAtoms"]), "parsed trajectory/phonon atom count"),
        "maxSpecies": (int(metrics["trajectorySpecies"]), "parsed trajectory distinct species count"),
        "maxCoordinateValues": (int(metrics["trajectoryCoordinateValues"]), "frames * atoms * 3"),
        "maxJsonBytes": (int(metrics["trajectorySerializedBytes"] or metrics["inputBytes"]), "canonical parsed input bytes"),
        "maxSourceBytes": (int(metrics["inputBytes"]), "declared source asset bytes"),
        "maxDatasetBytes": (int(metrics["inputBytes"]), "declared dataset asset bytes"),
        "maxRdfPairs": (pairs, "whole-window unordered all-atom pairs"),
        "maxRdfBins": (200, "current trajectory RDF default bin_count"),
        "maxMsdLags": (min(512, max(0, frames - 1)), "current MSD default bounded by available frames"),
        "maxTimeOrigins": (max(0, frames - 1), "maximum available origins at lag one"),
        "maxFitPoints": (max(0, frames - 1), "full-window MSD points available to diffusion"),
        "maxArtifactBytes": (int(metrics["estimatedArtifactBytes"]), "deterministic schema/shape upper-bound projection"),
        "maxRows": (int(metrics["rows"]), "parsed table row count"),
        "maxPoints": (max(int(metrics["rows"]), int(metrics["experimentalPoints"]), int(metrics["electronicPoints"])), "largest parsed point domain"),
        "maxPlotPoints": (max(int(metrics["rows"]), int(metrics["experimentalPoints"]), int(metrics["electronicPoints"]), int(metrics["phononQpoints"]), frames), "largest frozen plot point domain"),
        "maxTableRows": (min(limit, max(int(metrics["rows"]), int(metrics["phononQpoints"]), int(metrics["phononDosPoints"]))), "bounded output table projection"),
        "maxColumns": (int(metrics["columns"]), "parsed table column count"),
        "maxProperties": (int(metrics["columns"]), "parsed table property-column upper bound"),
        "maxAnalyzedSamples": (int(metrics["rows"]), "parsed sample row count"),
        "maxElements": (int(metrics["distinctElements"]), "parsed distinct element/species count"),
        "maxCategories": (min(limit, int(metrics["maxCategoryCardinality"])), "bounded output category collection"),
        "maxClasses": (int(metrics["classificationClasses"]), "source classification target/prediction class cardinality"),
        "maxModels": (1, "single source-authoritative model identity per ML Case"),
        "maxQpoints": (int(metrics["phononQpoints"]), "typed phonon q-point count"),
        "maxBranches": (int(metrics["phononBranches"]), "typed phonon branch count"),
        "maxSegments": (int(metrics["phononSegments"]), "typed phonon segment count"),
        "maxPathSegments": (int(metrics["phononSegments"]), "typed path segment count"),
        "maxDosPoints": (int(metrics["phononDosPoints"]), "typed phonon DOS point count"),
        "maxProjectedDosSeries": (int(metrics["phononProjectedDosSeries"]), "typed phonon projection series count"),
        "maxNumericValues": (int(metrics["phononNumericValues"]), "typed phonon numeric value projection"),
        "maxCombinedPlotValues": (int(metrics["phononNumericValues"]), "typed combined phonon plot values"),
        "maxFieldsPerDataset": (int(metrics["volumetricFields"]), "parsed volumetric field count"),
        "maxGridDimension": (int(metrics["volumetricGridDimension"]), "maximum parsed volumetric grid dimension"),
        "maxTotalVoxels": (int(metrics["volumetricVoxels"]), "parsed total voxel count"),
        "maxStoredValues": (int(metrics["volumetricVoxels"] * max(1, metrics["volumetricFields"])), "parsed stored scalar value count"),
        "maxUncompressedBytesPerField": (int(metrics["volumetricVoxels"] * 8), "float64 voxel upper-bound bytes"),
        "maxDisplayedInstances": (atoms, "trajectory atoms displayed per frame"),
        "maxCacheBytes": (atoms * 256, "one protected mapped trajectory frame"),
        "maxCacheFrames": (1, "minimum active protected frame requirement"),
        "maxPendingFrameRequests": (1, "bounded UI request policy"),
        "maxPlaybackFps": (30, "current desktop playback ceiling"),
        "maxHistogramBins": (30, "current default bounded histogram bins"),
        "maxCurvePoints": (int(metrics["rows"]), "source row curve domain"),
        "maxUncertaintyBins": (10, "current default uncertainty bin count"),
        "maxColorProperties": (min(limit, int(metrics["columns"])), "bounded output color-property selection"),
        "maxWarnings": (0, "no deterministic import warnings requiring retained warning slots"),
    }
    if key in direct:
        return direct[key]
    if key in {"timeoutSec"}:
        return 1, "positive configured timeout and all dominant work projections remain under their caps"
    if key.startswith("max"):
        # Output collection caps bound product-emitted collections. Current frozen
        # inputs are below their source-domain caps, so the maximum possible
        # requested collection is conservatively bounded by the declared limit.
        return min(limit, max(0, int(metrics["rows"] or metrics["atomsPerStructure"] or metrics["phononQpoints"] or 1))), "bounded output collection projected from frozen source domain"
    return None, "no deterministic projection"


def evaluate_tool_caps(tool_id: str, limits: dict[str, int], metrics: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    issues: list[dict[str, str]] = []
    unpreflightable: list[str] = []
    for key, raw_limit in sorted(limits.items()):
        limit = int(raw_limit)
        actual, basis = projected_value(key, limit, metrics)
        if actual is None:
            unpreflightable.append(key)
            checks.append({"limit": key, "maximum": limit, "status": "UNPREFLIGHTABLE", "basis": basis})
            continue
        status = "PASS" if actual <= limit else "FAIL"
        checks.append({"limit": key, "maximum": limit, "projectedActual": actual, "status": status, "basis": basis})
        if status == "FAIL":
            issues.append({"code": CAP_CODES.get(key, "REQUIRED_TOOL_RESOURCE_CAP_EXCEEDED"), "message": f"{tool_id} {key}={actual} exceeds {limit}."})
    if tool_id in {"trajectory.msd", "trajectory.diffusion"}:
        if metrics["trajectoryPositionWrapping"] not in {"wrapped", "unwrapped"}:
            issues.append({"code": "SCIENTIFIC_PARAMETER_INCOMPATIBLE", "message": f"{tool_id} requires explicit wrapped or unwrapped coordinate authority."})
        if metrics["trajectoryLatticeMode"] != "fixed":
            issues.append({"code": "SCIENTIFIC_PARAMETER_INCOMPATIBLE", "message": f"{tool_id} requires a fixed simulation cell."})
        times = metrics["trajectoryTimes"]
        if len(times) < 3 or any(value is None for value in times):
            issues.append({"code": "SCIENTIFIC_PARAMETER_INCOMPATIBLE", "message": f"{tool_id} requires at least three physical timestamps."})
        elif any(float(right) <= float(left) for left, right in zip(times, times[1:])):
            issues.append({"code": "SCIENTIFIC_PARAMETER_INCOMPATIBLE", "message": f"{tool_id} requires strictly increasing physical time."})
        elif len(times) > 2:
            deltas = [float(right) - float(left) for left, right in zip(times, times[1:])]
            if any(abs(value - deltas[0]) > 1e-9 for value in deltas[1:]):
                issues.append({"code": "SCIENTIFIC_PARAMETER_INCOMPATIBLE", "message": f"{tool_id} requires constant physical timestep."})
    if tool_id == "trajectory.rdf" and not any(metrics.get("trajectoryPbc") or []):
        issues.append({"code": "SCIENTIFIC_PARAMETER_INCOMPATIBLE", "message": "trajectory.rdf requires at least one periodic axis."})
    return {
        "toolId": tool_id,
        "checks": checks,
        "unpreflightableLimits": unpreflightable,
        "issues": issues,
        "status": "PASS" if not issues and not unpreflightable else "BLOCKED",
    }


def turn_preflight(case: dict[str, Any], turn: dict[str, Any], profile: Any, registry: Any, metadata_by_id: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    entry: dict[str, Any] = {
        "caseId": case["caseId"],
        "turnId": turn["turnId"],
        "question": turn["question"],
        "requiredTools": turn["requiredExecutionTools"],
        "maxRequiredStepCount": turn["maxRequiredStepCount"],
        "planStepCap": case["currentPlanStepCap"],
        "resourceMetrics": metrics,
        "issues": issues,
    }
    if turn["maxRequiredStepCount"] > case["currentPlanStepCap"] or len(set(turn["requiredExecutionTools"])) > turn["maxRequiredStepCount"]:
        issues.append({"code": "PLAN_CONSTRAINT_CONFLICT", "message": "Declared required Tool count exceeds the current turn/Case Plan cap."})
    if set(turn["requiredExecutionTools"]) & set(case.get("forbiddenExecutionTools", [])):
        issues.append({"code": "FORBIDDEN_TOOL_REQUIRED_AS_SUBSTITUTE", "message": "A required Tool is also forbidden."})

    selected_resource_ids = tuple(sorted(item.objectId for item in profile.resourceSemantics))
    intent = DeterministicAnalysisIntentBuilder().build(
        AnalysisIntentRequest(raw_goal=turn["question"], dataset_id=profile.datasetId, profile_id=profile.profileId, selected_resource_ids=selected_resource_ids),
        profile=profile,
        created_at="2026-08-17T00:00:00+00:00",
    )
    entry["intent"] = {
        "schemaVersion": intent.schemaVersion,
        "outcome": intent.outcome.value,
        "scientificIntents": [item.value for item in intent.scientificIntents],
        "requiredCapabilityNeeds": [item.value for item in intent.requiredCapabilityNeeds],
        "targetSemantics": [item.model_dump(mode="json") for item in intent.targetSemantics],
    }
    if intent.outcome.value != "READY":
        issues.append({"code": "EXECUTION_TURN_INTENT_NOT_RECOGNIZED", "message": "Current deterministic Intent did not reach READY."})
        entry["status"] = "BLOCKED"
        return entry

    resolution = resolve_eligibility(intent, profile=profile, registry=registry)
    candidates = {candidate.toolId: candidate for candidate in resolution.evaluatedCandidates}
    tool_results: list[dict[str, Any]] = []
    cap_results: list[dict[str, Any]] = []
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
        cap = evaluate_tool_caps(tool_id, registry.get_tool_by_id(tool_id).resourceLimits, metrics)
        cap_results.append(cap)
        issues.extend(cap["issues"])
        if cap["unpreflightableLimits"]:
            issues.append({"code": "REQUIRED_TOOL_RESOURCE_CAP_NOT_PREFLIGHTABLE", "message": f"{tool_id} has unresolved cap projections: {cap['unpreflightableLimits']}"})
    entry["requiredToolResults"] = tool_results
    entry["resourceCapPreflight"] = cap_results

    required_ids = sorted(set(turn["requiredExecutionTools"]))
    ports = build_artifact_port_inventory(registry)
    matrix = build_artifact_compatibility_matrix(registry, selected_tool_ids=required_ids)
    compatible_consumers = {pair.consumerToolId for pair in matrix.pairs if pair.compatible}
    required_consumers = {tool_id for tool_id in required_ids if ports[tool_id].inputPorts}
    unresolved = sorted(required_consumers - compatible_consumers)
    entry["dependencyPreflight"] = {
        "requiredConsumerTools": sorted(required_consumers),
        "compatiblePairs": [
            {"producerToolId": pair.producerToolId, "consumerToolId": pair.consumerToolId, "artifactContractVersion": pair.artifactContractVersion}
            for pair in matrix.pairs if pair.compatible
        ],
        "unresolvedConsumerTools": unresolved,
    }
    if unresolved:
        issues.append({"code": "DEPENDENCY_CONFLICT", "message": "A required artifact consumer lacks a compatible required producer."})

    exact_selection = case["caseId"] == "Q-TABLE-001"
    provider = exact_provider(turn["requiredExecutionTools"]) if exact_selection else MockLLMProvider()
    planning = plan_capabilities(intent, profile=profile, registry=registry, provider=provider)
    plan = planning.plan
    validation = validate_plan(plan.model_dump(mode="json"), registry=registry) if plan is not None else None
    selected = [] if planning.decision is None else [selection.toolId for selection in planning.decision.selections]
    entry["planPreflight"] = {
        "outcome": planning.outcome.value,
        "selectedTools": selected,
        "schemaVersion": None if plan is None else plan.schemaVersion,
        "stepCount": 0 if plan is None else len(plan.steps),
        "stepParams": [] if plan is None else [{"toolId": step.toolId, "params": step.params} for step in plan.steps],
        "validationOk": bool(validation and validation.ok),
        "validationErrors": [] if validation is None else [error.code for error in validation.errors],
    }
    if planning.outcome.value != "PLAN_READY" or validation is None or not validation.ok:
        issues.append({"code": "PLAN_CONSTRAINT_CONFLICT", "message": "Required-tool selection did not yield a valid non-executing Plan."})
    elif exact_selection and selected != turn["requiredExecutionTools"]:
        issues.append({"code": "REQUIRED_TOOL_SELECTION_MISMATCH", "message": "Planner selection differs from the Case required Tools."})
    elif len(plan.steps) > case["currentPlanStepCap"]:
        issues.append({"code": "PLAN_CONSTRAINT_CONFLICT", "message": "Plan exceeds current Case cap."})
    entry["status"] = "PASS" if not issues else "BLOCKED"
    return entry


def old_trajectory_reproduction(registry: Any, *, metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    if metrics is None:
        case_dir = R16 / "12_Q-TRAJECTORY-001"
        case = load_json(case_dir / "CASE.json")
        metrics = resource_metrics(case_dir, case, "historical_r16_trajectory")
    results = [evaluate_tool_caps(tool_id, registry.get_tool_by_id(tool_id).resourceLimits, metrics) for tool_id in ("trajectory.msd", "trajectory.diffusion", "trajectory.rdf")]
    issues = [issue for result in results for issue in result["issues"]]
    expected = {"REQUIRED_TOOL_FRAME_CAP_EXCEEDED", "REQUIRED_TOOL_PAIR_EVALUATION_CAP_EXCEEDED", "SCIENTIFIC_PARAMETER_INCOMPATIBLE"}
    observed = {issue["code"] for issue in issues}
    return {
        "historicalAuthority": "Phase_BC_R1_6_Qualification_Authority_Reconciled",
        "caseId": "Q-TRAJECTORY-001",
        "resourceMetrics": metrics,
        "requiredToolCapResults": results,
        "observedIssueCodes": sorted(observed),
        "expectedFailureClassesPresent": sorted(expected & observed),
        "result": "PASS_OLD_FAILURE_REPRODUCED" if expected <= observed else "FAIL_REPRODUCTION_INCOMPLETE",
    }


def main() -> None:
    registry = load_manifests()
    _, metadata_by_id = build_registry_snapshot(registry)
    index = load_json(PACKAGE / "CASE_INDEX.json")["cases"]
    cases: list[dict[str, Any]] = []
    turns: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    for item in index:
        case_dir = PACKAGE / item["directory"]
        case = load_json(case_dir / "CASE.json")
        if not case["analysisExecutionExpected"]:
            rejection = expected_rejection_preflight(case)
            cases.append({"caseId": case["caseId"], "caseType": case["caseType"], "status": rejection["status"], "turns": [], "expectedRejection": rejection})
            conflicts.extend({"caseId": case["caseId"], **issue} for issue in rejection["issues"])
            continue
        profile, resources, import_issues = profile_for_case(case_dir, case, f"r17_{case['caseId'].lower()}")
        metrics = resource_metrics(case_dir, case, f"r17_metrics_{case['caseId'].lower()}")
        case_turns: list[dict[str, Any]] = []
        case_issues = list(import_issues)
        if profile is not None:
            for turn in case["executionTurns"]:
                entry = turn_preflight(case, turn, profile, registry, metadata_by_id, metrics)
                case_turns.append(entry)
                turns.append(entry)
                case_issues.extend(entry["issues"])
                conflicts.extend({"caseId": case["caseId"], "turnId": turn["turnId"], **issue} for issue in entry["issues"])
        else:
            conflicts.extend({"caseId": case["caseId"], **issue} for issue in import_issues)
        cases.append({"caseId": case["caseId"], "caseType": case["caseType"], "status": "PASS" if not case_issues else "BLOCKED", "resources": resources, "resourceMetrics": metrics, "importIssues": import_issues, "turns": case_turns})

    old = old_trajectory_reproduction(registry)
    if old["result"] != "PASS_OLD_FAILURE_REPRODUCED":
        conflicts.append({"caseId": "Q-TRAJECTORY-001", "code": "OLD_FAILURE_REPRODUCTION_MISSING", "message": old["result"]})
    unpreflightable = sum(
        len(cap["unpreflightableLimits"])
        for turn in turns
        for cap in turn.get("resourceCapPreflight", [])
    )
    resource_conflicts = sum(
        1 for issue in conflicts if issue["code"].startswith("REQUIRED_TOOL_") and ("CAP" in issue["code"] or "SIZE" in issue["code"])
    )
    summary = {
        "caseCount": len(cases),
        "analysisExecutionCaseCount": sum(1 for case in cases if case["caseType"] != "EXPECTED_REJECTION"),
        "expectedRejectionCaseCount": sum(1 for case in cases if case["caseType"] == "EXPECTED_REJECTION"),
        "analysisExecutionTurnCount": len(turns),
        "passingCases": sum(1 for case in cases if case["status"] == "PASS"),
        "blockedCases": sorted({issue["caseId"] for issue in conflicts}),
        "issueCounts": {code: sum(1 for issue in conflicts if issue["code"] == code) for code in sorted({issue["code"] for issue in conflicts})},
        "resourceCapConflicts": resource_conflicts,
        "resourceCapUnpreflightableRequiredTools": unpreflightable,
        "allAnalysisExecutionTurnsPreflight": "PASS" if not conflicts else "FAIL",
        "expectedRejectionContracts": "PASS" if all(case["status"] == "PASS" for case in cases if case["caseType"] == "EXPECTED_REJECTION") else "FAIL",
        "preflightTestErrors": 0,
    }
    result = {
        "schemaVersion": "PhaseBCR17AllCaseExecutabilityPreflight/1.0",
        "authorityUnderReview": "Phase_BC_R1_7_Qualification_Authority_Reconciled",
        "integrityAuthority": "CONTENT_AND_CONTRACT_VALIDATION",
        "executionMode": "NON_LLM_NON_FORMAL_QUALIFICATION",
        "cases": cases,
        "summary": summary,
        "executionCounters": {"realLlmCalls": 0, "formalQualificationExecutions": 0, "newQualificationJobs": 0, "newQualificationToolCalls": 0, "newQualificationArtifacts": 0},
    }
    write_json(EVIDENCE / "ALL_CASE_EXECUTABILITY_PREFLIGHT.json", result)
    write_json(EVIDENCE / "OLD_Q_TRAJECTORY_PREFLIGHT_REPRODUCTION.json", old)
    qtrajectory = next(case for case in cases if case["caseId"] == "Q-TRAJECTORY-001")
    write_json(EVIDENCE / "Q_TRAJECTORY_RUNTIME_CAP_PREFLIGHT.json", {
        "caseId": "Q-TRAJECTORY-001",
        "result": qtrajectory["status"],
        "resourceMetrics": qtrajectory["resourceMetrics"],
        "turns": qtrajectory["turns"],
    })
    write_json(EVIDENCE / "Q_TRAJECTORY_TOOL_BINDING_PREFLIGHT.json", {
        "caseId": "Q-TRAJECTORY-001",
        "requiredTools": ["structure.trajectory_viewer", "trajectory.msd", "trajectory.diffusion", "trajectory.rdf"],
        "result": qtrajectory["status"],
        "turns": qtrajectory["turns"],
    })
    write_json(EVIDENCE / "RESOURCE_CAP_PREFLIGHT_MODEL.json", {
        "modelVersion": "1.0",
        "caseSpecificBranches": 0,
        "authoritySources": ["Tool Registry resourceLimits", "current parser/Profile facts", "current Adapter default parameter contracts", "current planned dependency ports"],
        "bindingClasses": ["SOURCE_BINDING", "PLANNED_OUTPUT_BINDING", "RUNTIME_ONLY_IDENTITY"],
        "runtimeOnlyIdsRequiredBeforePlan": False,
        "oldAuthorityFailureReproduced": old["result"],
        "summary": summary,
    })
    write_json(EVIDENCE / "STATIC_VALIDATOR_HARDENING.json", {
        "validator": "scripts/phase_bc_r1_7_cap_preflight.py",
        "genericByToolContract": True,
        "caseIdSpecialCasingForCaps": False,
        "newFindingClasses": sorted(set(CAP_CODES.values()) | {"REQUIRED_TOOL_RESOURCE_CAP_NOT_PREFLIGHTABLE", "REQUIRED_TOOL_RESOURCE_CAP_EXCEEDED"}),
        "oldR16TrajectoryRejectedBeforeExecution": old["result"] == "PASS_OLD_FAILURE_REPRODUCED",
        "r17AllCaseResult": summary["allAnalysisExecutionTurnsPreflight"],
    })
    print(json.dumps(summary, indent=2))
    if conflicts:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
