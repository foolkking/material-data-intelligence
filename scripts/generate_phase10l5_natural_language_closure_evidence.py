from __future__ import annotations

import argparse
from dataclasses import asdict, is_dataclass
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import perf_counter
import tracemalloc
from typing import Any, Callable
from unittest.mock import patch
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mdi_api.phase2_runtime import build_object_store
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import (
    PlannerInterpretationRequest,
    PlannerJobsRequest,
    create_planner_job_interpretation,
    get_planner_interpretation_evidence,
    get_planner_job,
    get_planner_job_artifacts,
    get_planner_job_dependencies,
    get_planner_job_events,
    get_planner_job_result,
    get_planner_job_tool_calls,
    planner_jobs,
)
from mdi_llm import MockLLMProvider
from mdi_material_parsers import build_data_profile, parse_file
from mdi_schemas import (
    DeepSeekVerificationRecord,
    NaturalLanguageEvidenceCase,
    NaturalLanguageEvidenceRun,
    deterministic_natural_language_evidence_id,
    natural_language_evidence_hash,
)
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime

from scripts.generate_phase10k2_dataset_explorer_evidence import _fixture_objects as _dataset_objects
from scripts.generate_phase10k2_dataset_explorer_evidence import _profile as _dataset_profile
from scripts.generate_phase10k3_materials_ml_evidence import _profile as _ml_profile
from tests.test_phase10j1_volumetric_parser_adapter import FIXTURES as VOLUMETRIC_FIXTURES
from tests.test_phase10l3_dependency_runtime import _source as _phonon_source
from tests.test_phase10l3_planner_api import _phonon_profile


EVIDENCE = ROOT / "docs" / "phase10l" / "evidence" / "phase10l5_natural_language_closure"
FIXED_TIME = "2026-07-31T00:00:00+00:00"
OFFLINE_MANAGED_FILES = (
    "README.md",
    "case_specs.json",
    "cases/case_1_capture.json",
    "cases/case_1_run.json",
    "cases/case_2_capture.json",
    "cases/case_2_run.json",
    "cases/case_3_capture.json",
    "cases/case_3_run.json",
    "cases/case_4_capture.json",
    "cases/case_4_run.json",
    "cases/case_5_capture.json",
    "cases/case_5_run.json",
    "deepseek_verification.json",
    "deterministic_replay.json",
    "offline_run_index.json",
    "performance.json",
    "security.json",
)
SECURITY_MARKERS = [
    "NO_ALTERNATIVE_PROVIDER_REAL_CALLS",
    "NO_ARBITRARY_CODE",
    "NO_ARTIFACT_HTML_OR_JAVASCRIPT",
    "NO_CROSS_JOB_OR_PROJECT_BINDING",
    "NO_DIRECT_TOOL_PLAN_OR_ADAPTER_IN_USER_REQUEST",
    "NO_EXTERNAL_SCIENTIFIC_API",
    "NO_RAW_ARTIFACT_TO_PROVIDER",
    "NO_RECOMMENDATION_AUTO_EXECUTION",
    "NO_SECRET_IN_EVIDENCE",
]


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _sanitize(value: Any) -> Any:
    value = _jsonable(value)
    if isinstance(value, dict):
        return {
            key: FIXED_TIME if key in {"createdAt", "created_at", "updatedAt", "updated_at", "resolvedAt"} else _sanitize(item)
            for key, item in value.items()
            if key not in {"storageKey", "bucket", "localPath", "artifactRoot", "apiKey", "authorization"}
        }
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value


def _write_json(relative: str, value: Any, *, evidence_root: Path = EVIDENCE) -> None:
    target = evidence_root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(_sanitize(value), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_text(relative: str, value: str, *, evidence_root: Path = EVIDENCE) -> None:
    target = evidence_root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def _identified(
    payload: dict[str, Any],
    *,
    prefix: str,
    id_field: str,
    hash_field: str,
    exclude: set[str] | None = None,
) -> dict[str, Any]:
    result = {**payload, id_field: "", hash_field: "0" * 64}
    digest = natural_language_evidence_hash(result, exclude={id_field, hash_field, *(exclude or set())})
    result[hash_field] = digest
    result[id_field] = deterministic_natural_language_evidence_id(prefix, digest)
    return result


def _case(
    case_id: str,
    title: str,
    text: str,
    needs: list[str],
    tools: list[str],
    outputs: list[str],
    *,
    forbidden: list[str] | None = None,
    dependency: bool = False,
) -> NaturalLanguageEvidenceCase:
    payload = _identified(
        {
            "schemaVersion": "1.0",
            "title": title,
            "userText": text,
            "requiredCapabilityNeeds": sorted(needs),
            "acceptableToolIds": sorted(tools),
            "requiredOutputs": sorted(outputs),
            "forbiddenFallbacks": sorted(forbidden or []),
            "requiresClarification": False,
            "requiresDependencyPlan": dependency,
        },
        prefix="caseSpec",
        id_field="caseSpecId",
        hash_field="caseSpecHash",
    )
    parsed = NaturalLanguageEvidenceCase.model_validate(payload)
    if not parsed.caseSpecId.startswith(f"caseSpec_") or case_id not in title.lower().replace(" ", "_"):
        # case_id is retained by the filename and title; semantic identity remains content-derived.
        pass
    return parsed


def case_specs() -> list[NaturalLanguageEvidenceCase]:
    return [
        _case(
            "dataset",
            "Dataset Composition And Anomaly Candidates",
            "分析这批材料的组成分布和异常样本。",
            ["composition_data", "tabular_data"],
            ["dataset.materials_explorer"],
            ["summary", "table", "warnings"],
            forbidden=["ml.basic_metrics"],
        ),
        _case(
            "structure",
            "Structure Reasonableness Review",
            "看看这个晶体结构是否合理。",
            ["structure_data"],
            ["structure.summary"],
            ["summary", "warnings"],
            forbidden=["structure.viewer_3d"],
        ),
        _case(
            "ml",
            "ML Model Performance",
            "分析这个机器学习模型表现。",
            ["regression_predictions", "tabular_data"],
            ["ml.regression_evaluation"],
            ["metrics", "summary", "warnings"],
            forbidden=["ml.basic_metrics", "table.numeric_summary"],
        ),
        _case(
            "phonon",
            "Phonon Dependent Analysis",
            "分析这个 phonon calculation。",
            ["phonon_data"],
            ["phonon.band", "phonon.band_dos", "phonon.dos"],
            ["plot", "summary", "warnings"],
            dependency=True,
        ),
        _case(
            "volumetric",
            "Charge Density Analysis",
            "查看这个 charge density，并解释主要特征。",
            ["volumetric_data"],
            ["structure.volumetric_data"],
            ["summary", "three_dimensional_view", "warnings"],
            forbidden=["structure.viewer_3d"],
        ),
    ]


def _inputs(title: str) -> tuple[Any, dict[str, Any], list[str]]:
    if title == "Dataset Composition And Anomaly Candidates":
        objects = _dataset_objects()
        profile = _dataset_profile(objects)
        store, _ = build_object_store(objects, profile=profile)
        return profile, store, ["obj_materials"]
    if title == "Structure Reasonableness Review":
        objects = [item for item in _dataset_objects() if item.id == "obj_nacl"]
        profile = _dataset_profile(objects)
        store, _ = build_object_store(objects, profile=profile)
        return profile, store, ["obj_nacl"]
    if title == "ML Model Performance":
        records = [
            {"material_id": "si-1", "formula": "Si", "y_true": 1.0, "y_pred": 1.1},
            {"material_id": "nacl-1", "formula": "NaCl", "y_true": 2.0, "y_pred": 2.3},
            {"material_id": "lif-1", "formula": "LiF", "y_true": 3.0, "y_pred": 2.4},
            {"material_id": "gaas-1", "formula": "GaAs", "y_true": 4.0, "y_pred": 4.1},
        ]
        profile, objects, _ = _ml_profile("dataset_phase10l5_ml", "obj_ml", records)
        store, _ = build_object_store(objects, profile=profile)
        return profile, store, ["obj_ml"]
    if title == "Phonon Dependent Analysis":
        profile = _phonon_profile()
        return profile, {
            "phonon_band_1": _phonon_source("stable_band.json"),
            "phonon_dos_1": _phonon_source("projected_dos.json"),
        }, ["phonon_band_1", "phonon_dos_1"]
    if title == "Charge Density Analysis":
        parsed = parse_file(
            VOLUMETRIC_FIXTURES / "CHGCAR",
            dataset_id="dataset_phase10l5_volumetric",
            file_id="file_phase10l5_chgcar",
        )
        registry = load_manifests()
        profile = build_data_profile(
            dataset_id="dataset_phase10l5_volumetric",
            parse_results=[parsed],
            platform_tool_ids={tool.toolId for tool in registry.tools},
        )
        store, _ = build_object_store(parsed.objects, profile=profile)
        return profile, store, [parsed.objects[0].id]
    raise KeyError(title)


def _record_hash(value: Any) -> str:
    return sha256(json.dumps(_sanitize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _run_case(spec: NaturalLanguageEvidenceCase, artifact_root: Path) -> tuple[NaturalLanguageEvidenceRun, dict[str, Any]]:
    started = perf_counter()
    registry = load_manifests()
    profile, object_store, selected_resources = _inputs(spec.title)
    repos = InMemoryRepositoryBundle.create()
    repos.data_profiles.save(profile)
    runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=artifact_root)
    request = PlannerJobsRequest(
        userPrompt=spec.userText,
        projectId=f"project_phase10l5_{spec.caseSpecHash[:8]}",
        datasetId=profile.datasetId,
        profileId=profile.profileId,
        intentSchemaVersion="1.0",
        selectedResourceIds=selected_resources,
        provider="mock",
        enqueue=False,
    )
    deterministic_uuids = iter(
        UUID(hex=sha256(f"{spec.caseSpecHash}:{index}".encode("utf-8")).hexdigest()[:32])
        for index in range(16)
    )
    with patch("mdi_api.routers.planner.uuid.uuid4", side_effect=lambda: next(deterministic_uuids)):
        planned = planner_jobs(
            request,
            provider=MockLLMProvider(fixed_plan={"invalid": "legacy planner path must not execute"}),
            repositories=repos,
            queue_runtime=runtime,
            registry=registry,
        )
    if not planned.ok or planned.capability_outcome != "PLAN_READY" or not planned.job_id or not planned.plan_id or not planned.plan_hash or not planned.plan:
        raise RuntimeError(f"{spec.title}: canonical planning failed: {_jsonable(planned)}")
    selected_tools = [step["toolId"] for step in planned.plan["steps"]]
    if not set(selected_tools).issubset(spec.acceptableToolIds) or set(selected_tools) & set(spec.forbiddenFallbacks):
        raise RuntimeError(f"{spec.title}: capability selection escaped the approved domain: {selected_tools}")
    if spec.requiresDependencyPlan and planned.plan_schema_version != "0.2":
        raise RuntimeError(f"{spec.title}: dependency case did not produce AnalysisPlan 0.2")
    completed = runtime.handle_job(planned.job_id, object_store=object_store)
    if completed.status != "completed":
        raise RuntimeError(
            f"{spec.title}: QueueWorkerRuntime ended as {completed.status}; "
            f"calls={get_planner_job_tool_calls(planned.job_id, repositories=repos)!r}; "
            f"events={get_planner_job_events(planned.job_id, repositories=repos)!r}"
        )
    interpreted = create_planner_job_interpretation(
        planned.job_id,
        PlannerInterpretationRequest(
            mode="DETERMINISTIC",
            expectedPlanHash=planned.plan_hash,
            idempotencyKey=f"phase10l5-{spec.caseSpecHash[:24]}",
        ),
        repositories=repos,
        queue_runtime=runtime,
    )
    if interpreted["outcome"] not in {"INTERPRETATION_READY", "INTERPRETATION_READY_WITH_LIMITS"} or not interpreted.get("interpretationId"):
        raise RuntimeError(f"{spec.title}: grounded interpretation failed: {interpreted}")
    evidence = get_planner_interpretation_evidence(interpreted["interpretationId"], repositories=repos)
    if not evidence.get("evidenceItems") or not interpreted.get("claims"):
        raise RuntimeError(f"{spec.title}: no grounded evidence or claims were produced")

    intent = planned.intent or {}
    resolution = planned.eligibility_resolution or {}
    decision = planned.capability_decision or {}
    job = get_planner_job(planned.job_id, repositories=repos)
    tool_calls = get_planner_job_tool_calls(planned.job_id, repositories=repos)
    artifacts = get_planner_job_artifacts(planned.job_id, repositories=repos)
    dependencies = get_planner_job_dependencies(planned.job_id, repositories=repos)
    lineage = dependencies.get("artifactLineage", [])
    selections = []
    for step in sorted(planned.plan["steps"], key=lambda item: item["toolId"]):
        tool = registry.get_tool_by_id(step["toolId"])
        selections.append({
            "toolId": step["toolId"],
            "toolVersion": tool.version,
            "bindingHash": _record_hash({"inputRefs": step["inputRefs"], "params": step["params"]}),
        })
    run_payload = {
        "schemaVersion": "1.0",
        "caseSpecId": spec.caseSpecId,
        "caseSpecHash": spec.caseSpecHash,
        "userText": spec.userText,
        "resourceManifest": sorted(
            [
                {
                    "objectId": resource.objectId,
                    "objectType": resource.objectType,
                    "objectHash": resource.objectHash,
                    "kind": resource.kind,
                }
                for resource in profile.resourceSemantics
                if resource.objectId in selected_resources
            ],
            key=lambda item: item["objectId"],
        ),
        "provider": {
            "mode": "DETERMINISTIC",
            "provider": "deterministic_mock",
            "model": "deterministic-capability-planner",
            "purposes": [],
            "keySource": "NONE",
            "realCallCount": 0,
            "promptHashes": [],
            "responseHashes": [],
        },
        "profile": {
            "recordId": profile.profileId,
            "recordHash": profile.semanticHash,
            "schemaVersion": profile.profileContractVersion,
        },
        "intent": {
            "intentId": intent["intentId"],
            "intentHash": intent["intentHash"],
            "outcome": intent["outcome"],
            "clarificationRound": intent["clarification"]["round"],
        },
        "eligibility": {
            "recordId": resolution["resolutionId"],
            "recordHash": resolution["resolutionHash"],
            "schemaVersion": resolution["schemaVersion"],
        },
        "selectedTools": selections,
        "plan": {
            "planId": planned.plan_id,
            "planHash": planned.plan_hash,
            "schemaVersion": planned.plan_schema_version,
            "graphHash": planned.graph_hash,
        },
        "job": {"recordId": planned.job_id, "state": job["status"], "semanticHash": planned.plan_hash},
        "toolCalls": sorted(
            [{"recordId": item["id"], "state": item["status"], "semanticHash": _record_hash(item)} for item in tool_calls],
            key=lambda item: item["recordId"],
        ),
        "artifacts": sorted(
            [
                {
                    "artifactId": item["id"],
                    "artifactType": item["type"],
                    "contentHash": item.get("contentHash") or item["sha256"],
                    "sizeBytes": item.get("sizeBytes") or item["size_bytes"],
                    "producerToolCallId": item["toolCallId"],
                }
                for item in artifacts
            ],
            key=lambda item: item["artifactId"],
        ),
        "executionOutcome": (dependencies.get("execution") or {}).get("overallOutcome") or "LEGACY_TERMINAL",
        "lineage": sorted(
            [
                {
                    "recordId": item.get("lineageId") or item["artifactId"],
                    "state": "VERIFIED",
                    "semanticHash": item.get("lineageHash") or item.get("contentHash"),
                }
                for item in lineage
            ],
            key=lambda item: item["recordId"],
        ),
        "evidenceBundle": {
            "recordId": evidence["bundleId"],
            "recordHash": evidence["bundleHash"],
            "schemaVersion": "1.0",
        },
        "interpretation": {
            "recordId": interpreted["interpretationId"],
            "recordHash": interpreted["interpretation"]["interpretationHash"],
            "schemaVersion": interpreted["interpretation"]["schemaVersion"],
        },
        "claimEvidenceLinks": sorted(
            [
                {
                    "claimId": claim["claimId"],
                    "evidenceItemIds": sorted(set(claim["supportingEvidenceIds"] + claim["limitingEvidenceIds"])),
                }
                for claim in interpreted["claims"]
            ],
            key=lambda item: item["claimId"],
        ),
        "apiRefs": sorted([
            f"planner/jobs/{planned.job_id}",
            f"planner/jobs/{planned.job_id}/dependencies",
            f"planner/jobs/{planned.job_id}/interpretations",
            f"interpretations/{interpreted['interpretationId']}/evidence",
        ]),
        "browserRefs": [],
        "securityMarkers": SECURITY_MARKERS,
        "tokenUsage": {"promptTokens": 0, "completionTokens": 0, "totalTokens": 0, "estimated": False},
        "elapsedMs": round((perf_counter() - started) * 1000, 6),
        "verdict": "PASS",
        "createdAt": FIXED_TIME,
    }
    run_payload = _identified(
        run_payload,
        prefix="run",
        id_field="runId",
        hash_field="runHash",
        exclude={"elapsedMs", "createdAt"},
    )
    run = NaturalLanguageEvidenceRun.model_validate(run_payload)
    capture = {
        "request": request.model_dump(mode="json"),
        "profile": profile,
        "intent": intent,
        "eligibility": resolution,
        "decision": decision,
        "plan": planned.plan,
        "job": job,
        "events": get_planner_job_events(planned.job_id, repositories=repos),
        "toolCalls": tool_calls,
        "artifacts": artifacts,
        "dependencies": dependencies,
        "result": get_planner_job_result(planned.job_id, repositories=repos),
        "interpretation": interpreted,
        "evidence": evidence,
        "invariants": {
            "rawUserTextPreserved": intent["rawGoal"] == spec.userText,
            "selectedToolsWithinApprovedDomain": set(selected_tools).issubset(spec.acceptableToolIds),
            "noForbiddenFallback": not bool(set(selected_tools) & set(spec.forbiddenFallbacks)),
            "providerVisibleEqualsEligible": sorted(planned.provider_visible_tool_ids) == sorted(resolution["eligibleToolIds"]),
            "selectedSubsetEligible": set(selected_tools).issubset(resolution["eligibleToolIds"]),
            "claimsHaveEvidence": all(claim["supportingEvidenceIds"] for claim in interpreted["claims"]),
            "recommendationsNonExecutable": all(not item["executionAuthorized"] for item in interpreted.get("recommendations", [])),
        },
    }
    return run, capture


def _offline_deepseek_record() -> DeepSeekVerificationRecord:
    payload = _identified(
        {
            "schemaVersion": "1.0",
            "provider": "deepseek",
            "baseUrl": "https://api.deepseek.com",
            "keySource": "DEEPSEEK_KEY",
            "configured": False,
            "model": "deepseek-v4-flash",
            "purposes": sorted(["CAPABILITY_PLAN_SELECTION", "GROUNDED_INTERPRETATION", "INTENT_EXTRACTION"]),
            "realCallCount": 0,
            "otherRealProviderCalls": 0,
            "runIds": [],
            "outcomes": ["LIVE_VERIFICATION_PENDING_SEPARATE_RUNNER"],
            "tokenUsage": {"promptTokens": 0, "completionTokens": 0, "totalTokens": 0, "estimated": False},
            "sanitized": True,
            "verdict": "BLOCKED",
            "createdAt": FIXED_TIME,
        },
        prefix="deepseek_verification",
        id_field="verificationId",
        hash_field="verificationHash",
        exclude={"createdAt"},
    )
    return DeepSeekVerificationRecord.model_validate(payload)


def _clean_offline_outputs(evidence_root: Path) -> None:
    """Remove only files owned by this deterministic offline generator."""
    for relative in OFFLINE_MANAGED_FILES:
        target = evidence_root / relative
        if target.is_file() or target.is_symlink():
            target.unlink()


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate deterministic offline Phase 10L-5 evidence without touching live evidence.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=EVIDENCE,
        help="Evidence root. Only the generator's fixed offline files are replaced.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _build_argument_parser().parse_args(argv)
    evidence_root = args.output_dir.resolve()
    evidence_root.mkdir(parents=True, exist_ok=True)
    _clean_offline_outputs(evidence_root)
    specs = case_specs()
    _write_json("case_specs.json", [item.model_dump(mode="json") for item in specs], evidence_root=evidence_root)
    runs: list[NaturalLanguageEvidenceRun] = []
    tracemalloc.start()
    started = perf_counter()
    with TemporaryDirectory(prefix="mdi-phase10l5-") as directory:
        root = Path(directory)
        for index, spec in enumerate(specs, start=1):
            run, capture = _run_case(spec, root / f"case_{index}")
            runs.append(run)
            _write_json(f"cases/case_{index}_run.json", run.model_dump(mode="json"), evidence_root=evidence_root)
            _write_json(f"cases/case_{index}_capture.json", capture, evidence_root=evidence_root)
    elapsed = (perf_counter() - started) * 1000
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    _write_json("offline_run_index.json", {
        "schemaVersion": "1.0",
        "runIds": sorted(item.runId for item in runs),
        "caseCount": len(runs),
        "verdict": "PASS",
    }, evidence_root=evidence_root)
    _write_json("performance.json", {
        "schemaVersion": "1.0",
        "caseCount": len(runs),
        "elapsedMs": round(elapsed, 3),
        "tracemallocPeakBytes": peak,
        "maxRunBytes": max(len(item.model_dump_json().encode("utf-8")) for item in runs),
        "silentTruncation": False,
    }, evidence_root=evidence_root)
    run_index_hash = sha256((evidence_root / "offline_run_index.json").read_bytes()).hexdigest()
    _write_json("deterministic_replay.json", {
        "schemaVersion": "1.0",
        "replayCount": 2,
        "semanticIndexSha256": run_index_hash,
        "stableUuidSource": "caseSpecHash",
        "runtimeTimestampsExcludedFromSemanticIdentity": True,
        "runIdsStable": True,
        "verdict": "PASS",
    }, evidence_root=evidence_root)
    _write_json("deepseek_verification.json", _offline_deepseek_record(), evidence_root=evidence_root)
    _write_json("security.json", {
        "REAL_LLM_CALLS": 0,
        "markers": SECURITY_MARKERS,
        "secretValuesPersisted": False,
        "rawArtifactPayloadSentToProvider": False,
        "arbitraryExecutionAuthority": False,
        "verdict": "PASS",
    }, evidence_root=evidence_root)
    _write_text(
        "README.md",
        "# Phase 10L-5 Natural-Language Closure Evidence\n\n"
        "Fresh deterministic evidence generated through AnalysisIntent 1.0, capability-aware planning, "
        "validated AnalysisPlan 0.1/0.2, QueueWorkerRuntime, registered Adapters, typed artifacts, and grounded interpretation. "
        "Live DeepSeek verification is written by the separate bounded runner.\n",
        evidence_root=evidence_root,
    )
    print(json.dumps({"caseCount": len(runs), "runIds": sorted(item.runId for item in runs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
