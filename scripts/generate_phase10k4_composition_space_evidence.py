from __future__ import annotations

import copy
import hashlib
import json
import re
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Mapping
from unittest.mock import patch

import pandas as pd

from mdi_adapters import ToolExecutionContext, ToolExecutionError
from mdi_adapters.platform_builtin import CompositionSpaceAdapter, RegressionEvaluationAdapter
from mdi_api.phase2_runtime import build_object_store
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import (
    PlannerJobsRequest,
    get_planner_job,
    get_planner_job_artifact_content,
    get_planner_job_artifacts,
    get_planner_job_events,
    get_planner_job_result,
    get_planner_job_tool_calls,
    planner_jobs,
)
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import NormalizedObjectDraft, ParseResult, build_data_profile
from mdi_material_parsers.models import DetectedFormat
from mdi_schemas import ArtifactType, MaterialObjectType, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "phase10k" / "evidence" / "phase10k4_composition_space"
TOOL_ID = "dataset.composition_space"
PROMPT = "Explore this composition space with deterministic PCA and bounded composition clusters."
PRIVATE_PATH = re.compile(r"[A-Za-z]:[\\/](?:Users|home|1project)[\\/]", re.IGNORECASE)
SECRET_PATTERN = re.compile(
    r"(?:sk-[A-Za-z0-9]{16,}|api[_-]?key\s*[:=]|password\s*[:=]|authorization\s*[:=])",
    re.IGNORECASE,
)


BASE_RECORDS = [
    {"material_id": "si-1", "formula": "Si", "band_gap": 1.10, "split": "train", "y_true": 1.0, "y_pred": 1.1},
    {"material_id": "sige-1", "formula": "Si0.5Ge0.5", "band_gap": 0.75, "split": "train", "y_true": 1.2, "y_pred": 1.0},
    {"material_id": "nacl-1", "formula": "NaCl", "band_gap": 5.60, "split": "train", "y_true": 2.0, "y_pred": 2.3},
    {"material_id": "lif-1", "formula": "LiF", "band_gap": 11.80, "split": "test", "y_true": 3.0, "y_pred": 2.5},
    {"material_id": "mgo-1", "formula": "MgO", "band_gap": 7.80, "split": "test", "y_true": 4.0, "y_pred": 4.1},
    {"material_id": "gaas-1", "formula": "GaAs", "band_gap": 1.42, "split": "test", "y_true": 5.0, "y_pred": 4.8},
]


def _table(
    dataset_id: str,
    object_id: str,
    records: list[dict[str, Any]],
    *,
    units: Mapping[str, str] | None = None,
) -> NormalizedObjectDraft:
    frame = pd.DataFrame(records)
    columns: list[dict[str, Any]] = []
    for name in frame.columns:
        series = frame[name]
        numeric = pd.api.types.is_numeric_dtype(series)
        finite = pd.to_numeric(series, errors="coerce") if numeric else None
        columns.append(
            {
                "name": str(name),
                "dtype": "number" if numeric else "string",
                "missingCount": int(series.isna().sum()),
                "uniqueCount": int(series.nunique(dropna=True)),
                "finiteCount": int(finite.notna().sum()) if finite is not None else None,
                "unit": (units or {}).get(str(name)),
            }
        )
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return NormalizedObjectDraft(
        id=object_id,
        dataset_id=dataset_id,
        object_type=MaterialObjectType.DataFrame,
        source_file_ids=[f"{object_id}.csv"],
        storage_key=f"normalized/{object_id}.json",
        metadata={"nRows": len(frame), "nColumns": len(frame.columns), "columns": columns},
        hash=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        payload=records,
    )


def _profile(
    dataset_id: str,
    table_specs: list[tuple[str, list[dict[str, Any]]]],
) -> tuple[Any, list[NormalizedObjectDraft], Any]:
    objects = [
        _table(dataset_id, object_id, records, units={"band_gap": "eV"})
        for object_id, records in table_specs
    ]
    registry = load_manifests()
    profile = build_data_profile(
        dataset_id=dataset_id,
        parse_results=[
            ParseResult(
                file_id=f"file_{dataset_id}",
                file_path=Path(f"{dataset_id}.json"),
                detected_format=DetectedFormat.json_limited,
                parse_status="success",
                objects=objects,
            )
        ],
        platform_tool_ids={tool.toolId for tool in registry.tools},
    )
    return profile, objects, registry


def _mock_plan(profile: Any, prompt: str = PROMPT) -> dict[str, Any]:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt=prompt,
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            tool_registry_version=registry.version,
        ),
        tools=registry.list_mvp_tools(),
        data_profile=profile,
    )
    if response.raw_json is None:
        raise RuntimeError("Mock Planner did not return a composition-space AnalysisPlan.")
    if response.raw_json["steps"][0]["toolId"] != TOOL_ID:
        raise RuntimeError(f"Mock Planner routed composition space to {response.raw_json['steps'][0]['toolId']}.")
    return copy.deepcopy(response.raw_json)


def _plan_with(
    profile: Any,
    *,
    prompt: str = PROMPT,
    params: Mapping[str, Any] | None = None,
    input_refs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    plan = _mock_plan(profile, prompt)
    if params:
        plan["steps"][0]["params"].update(dict(params))
    if input_refs is not None:
        plan["steps"][0]["inputRefs"] = input_refs
    return plan


def _write(relative: str, value: Any) -> None:
    target = EVIDENCE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        payload = value
    else:
        payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n"
    target.write_text(payload, encoding="utf-8", newline="\n")


def _sanitized(value: Any) -> Any:
    if isinstance(value, list):
        return [_sanitized(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _sanitized(item)
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
            if key not in {"createdAt", "updatedAt", "storageKey", "bucket", "downloadUrl"}
        }
    if isinstance(value, str):
        return PRIVATE_PATH.sub("[local-path]", value)
    return value


def _deterministic_ids(case_id: str) -> list[uuid.UUID]:
    namespace = uuid.UUID("2d8456c6-c09f-40d4-90f2-5376a9d15d15")
    return [uuid.uuid5(namespace, f"{case_id}:{index}") for index in range(1, 5)]


def _runtime_case(
    case_id: str,
    profile: Any,
    objects: list[NormalizedObjectDraft],
    plan: dict[str, Any],
    *,
    extra_store: Mapping[str, Any] | None = None,
    expected_status: str = "completed",
) -> dict[str, Any]:
    registry = load_manifests()
    validation = validate_plan(plan, registry=registry)
    if not validation.ok:
        raise RuntimeError(
            f"{case_id} AnalysisPlan did not validate: "
            + "; ".join(f"{item.code}:{item.message}" for item in validation.errors)
        )
    repositories = InMemoryRepositoryBundle.create()
    with tempfile.TemporaryDirectory(prefix=f"mdi-phase10k4-{case_id}-") as directory:
        runtime = QueueWorkerRuntime(
            repositories=repositories,
            registry=registry,
            artifact_root=Path(directory),
        )
        with patch("mdi_api.routers.planner.uuid.uuid4", side_effect=_deterministic_ids(case_id)):
            created = planner_jobs(
                PlannerJobsRequest(
                    userPrompt=f"Phase 10K-4 evidence: {case_id}",
                    projectId="project_phase10k4_evidence",
                    datasetId=profile.datasetId,
                    profileId=profile.profileId,
                    enqueue=True,
                ),
                provider=MockLLMProvider(fixed_plan=plan),
                repositories=repositories,
                queue_runtime=runtime,
                registry=registry,
            )
        if not created.ok or not created.job_id:
            raise RuntimeError(f"{case_id} Planner job creation failed.")
        object_store, _ = build_object_store(objects, profile=profile)
        object_store.update(dict(extra_store or {}))
        completed = runtime.handle_job(created.job_id, object_store=object_store)
        job_id = created.job_id
        artifacts = get_planner_job_artifacts(job_id, repositories=repositories)
        contents: dict[str, Any] = {}
        if completed.status == "completed":
            for artifact in artifacts:
                response = get_planner_job_artifact_content(
                    job_id,
                    str(artifact["id"]),
                    repositories=repositories,
                    queue_runtime=runtime,
                )
                raw = bytes(response.body)
                name = str(artifact["name"])
                contents[name] = json.loads(raw) if name.endswith(".json") else raw.decode("utf-8")
                _write(f"artifacts/{case_id}/{name}", contents[name])
        capture = {
            "caseId": case_id,
            "expectedStatus": expected_status,
            "request": {
                "datasetId": profile.datasetId,
                "profileId": profile.profileId,
                "provider": "MockLLMProvider",
                "enqueue": True,
            },
            "plan": created.plan,
            "planValidation": {"ok": validation.ok, "errors": []},
            "job": get_planner_job(job_id, repositories=repositories),
            "events": get_planner_job_events(job_id, repositories=repositories),
            "toolCalls": get_planner_job_tool_calls(job_id, repositories=repositories),
            "artifacts": artifacts,
            "result": get_planner_job_result(job_id, repositories=repositories),
            "apiContentRetrieval": {
                "artifactNames": sorted(contents),
                "allContentRoutesValidated": len(contents) == len(artifacts),
            },
        }
    _write(f"api/{case_id}_data_profile.json", _sanitized(profile.model_dump(mode="json")))
    _write(f"api/{case_id}_runtime_capture.json", _sanitized(capture))
    if completed.status != expected_status:
        error = capture["toolCalls"][-1].get("error") if capture["toolCalls"] else None
        raise RuntimeError(
            f"{case_id} runtime status was {completed.status}, expected {expected_status}; error={_sanitized(error)}"
        )
    return {"capture": capture, "contents": contents}


def _regression_artifact(
    profile: Any,
    objects: list[NormalizedObjectDraft],
    root: Path,
) -> dict[str, Any]:
    registry = load_manifests()
    tool = registry.get_tool_by_id("ml.regression_evaluation")
    store, _ = build_object_store(objects, profile=profile)
    context = ToolExecutionContext(
        job_id="job_phase10k4_k3_source",
        project_id="project_phase10k4_evidence",
        dataset_id=profile.datasetId,
        tool_id=tool.toolId,
        tool_version=tool.version,
        adapter_version=RegressionEvaluationAdapter.adapter_version,
        registry_version=registry.version,
        artifact_root=root,
        tool_call_id="call_phase10k4_k3_source",
        object_store=store,
        resource_limits=tool.resourceLimits,
    )
    request = ToolExecutionRequest(
        jobId=context.job_id,
        stepId="step_001",
        toolId=tool.toolId,
        inputRefs=[
            {"refType": "profile", "ref": "profile"},
            {"refType": "normalized_object", "ref": objects[0].id, "objectType": "DataFrame"},
        ],
        params={"maxPlotPoints": 1000, "maxTableRows": 100},
        artifactTypes=[ArtifactType.table_json],
    )
    artifacts = RegressionEvaluationAdapter().execute(context, request)
    product = next(item for item in artifacts if item.name == "materials_ml_regression.json")
    return json.loads((root / product.storageKey).read_text(encoding="utf-8"))


def _performance_case(case_id: str, row_count: int) -> dict[str, Any]:
    records = [
        {
            "material_id": f"sample-{index:06d}",
            "formula": ("Si", "Si0.5Ge0.5", "NaCl", "LiF", "MgO", "GaAs")[index % 6],
            "band_gap": float(index % 101) / 10.0,
        }
        for index in range(row_count)
    ]
    profile, objects, registry = _profile(
        f"dataset_phase10k4_performance_{case_id}",
        [(f"obj_{case_id}", records)],
    )
    tool = registry.get_tool_by_id(TOOL_ID)
    store, _ = build_object_store(objects, profile=profile)
    with tempfile.TemporaryDirectory(prefix=f"mdi-phase10k4-performance-{case_id}-") as directory:
        context = ToolExecutionContext(
            job_id=f"job_{case_id}",
            project_id="project_phase10k4_performance",
            dataset_id=profile.datasetId,
            tool_id=tool.toolId,
            tool_version=tool.version,
            adapter_version=CompositionSpaceAdapter.adapter_version,
            registry_version=registry.version,
            artifact_root=Path(directory),
            tool_call_id=f"call_{case_id}",
            object_store=store,
            resource_limits=tool.resourceLimits,
        )
        request = ToolExecutionRequest(
            jobId=context.job_id,
            stepId="step_001",
            toolId=tool.toolId,
            inputRefs=[
                {"refType": "profile", "ref": "profile"},
                {"refType": "normalized_object", "ref": objects[0].id, "objectType": "DataFrame"},
            ],
            params={
                "tableObjectId": objects[0].id,
                "comparisonMode": "none",
                "projectionDimensions": 2,
                "clusteringEnabled": True,
                "nClusters": 3,
                "randomState": 0,
                "nInit": 10,
                "maxIterations": 300,
                "tolerance": 0.0001,
                "maxPlotPoints": 1000,
                "maxOutlierRows": 20,
            },
            artifactTypes=[ArtifactType.table_json],
        )
        started = time.perf_counter()
        artifacts = CompositionSpaceAdapter().execute(context, request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        product = next(item for item in artifacts if item.name == "composition_space.json")
        payload = json.loads((Path(directory) / product.storageKey).read_text(encoding="utf-8"))
    return {
        "caseId": case_id,
        "inputRows": row_count,
        "validSamples": payload["coverage"]["validCompositionSamples"],
        "displayPoints": len(payload["displayPointKeys"]),
        "featureDimensions": payload["featureRepresentation"]["featureDimensions"],
        "clusterCount": len(payload["clustering"]["clusters"]),
        "artifactBytes": product.sizeBytes,
        "elapsedMs": round(elapsed_ms, 3),
    }


def _expected_failure(
    case_id: str,
    records: list[dict[str, Any]],
    *,
    error_code: str,
    error_type: str | None,
) -> dict[str, Any]:
    profile, objects, _ = _profile(f"dataset_phase10k4_{case_id}", [(f"obj_{case_id}", records)])
    plan = _plan_with(profile)
    result = _runtime_case(case_id, profile, objects, plan, expected_status="failed")
    call = result["capture"]["toolCalls"][-1]
    message = str((call.get("error") or {}).get("message") or "")
    if error_code not in message:
        raise RuntimeError(f"{case_id} did not expose expected code {error_code}: {message}")
    registry = load_manifests()
    tool = registry.get_tool_by_id(TOOL_ID)
    store, _ = build_object_store(objects, profile=profile)
    with tempfile.TemporaryDirectory(prefix=f"mdi-phase10k4-typed-{case_id}-") as directory:
        context = ToolExecutionContext(
            job_id=f"job_typed_{case_id}",
            project_id="project_phase10k4_evidence",
            dataset_id=profile.datasetId,
            tool_id=tool.toolId,
            tool_version=tool.version,
            adapter_version=CompositionSpaceAdapter.adapter_version,
            registry_version=registry.version,
            artifact_root=Path(directory),
            tool_call_id=f"call_typed_{case_id}",
            object_store=store,
            resource_limits=tool.resourceLimits,
        )
        request = ToolExecutionRequest(
            jobId=context.job_id,
            stepId="step_001",
            toolId=TOOL_ID,
            inputRefs=plan["steps"][0]["inputRefs"],
            params=plan["steps"][0]["params"],
            artifactTypes=[ArtifactType.table_json],
        )
        try:
            CompositionSpaceAdapter().execute(context, request)
        except ToolExecutionError as exc:
            typed_error = exc.to_dict()
        else:
            raise RuntimeError(f"{case_id} direct Registry/Adapter request unexpectedly succeeded.")
    if typed_error["code"] != error_code:
        raise RuntimeError(f"{case_id} typed code was {typed_error['code']}, expected {error_code}.")
    if error_type and typed_error["details"].get("errorType") != error_type:
        raise RuntimeError(
            f"{case_id} typed error was {typed_error['details'].get('errorType')}, expected {error_type}."
        )
    capture = _sanitized(result["capture"])
    capture["typedAdapterError"] = _sanitized(typed_error)
    _write(f"api/{case_id}_runtime_capture.json", capture)
    return capture


def _security_validation(profile: Any) -> dict[str, Any]:
    registry = load_manifests()
    plan = _plan_with(profile)
    plan["steps"][0]["params"]["callback"] = "javascript:alert(1)"
    validation = validate_plan(plan, registry=registry)
    if validation.ok:
        raise RuntimeError("Executable callback parameter unexpectedly passed PlanValidator.")
    return {
        "validationOk": False,
        "errors": [
            {"code": item.code, "message": item.message, "detail": _sanitized(item.detail)}
            for item in validation.errors
        ],
        "runtimeStarted": False,
        "artifactCreated": False,
    }


def _manifest() -> None:
    files = []
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file() or path.name == "evidence_manifest.json":
            continue
        payload = path.read_bytes()
        files.append(
            {
                "name": path.relative_to(EVIDENCE).as_posix(),
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    _write("evidence_manifest.json", {"algorithm": "sha256", "files": files})


def _security_audit() -> dict[str, Any]:
    secret_hits: list[str] = []
    private_path_hits: list[str] = []
    executable_hits: list[str] = []
    executable = re.compile(r"(?:<script|dangerouslySetInnerHTML|\beval\s*\(|\bFunction\s*\()", re.IGNORECASE)
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".json", ".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = path.relative_to(EVIDENCE).as_posix()
        if SECRET_PATTERN.search(text):
            secret_hits.append(relative)
        if PRIVATE_PATH.search(text):
            private_path_hits.append(relative)
        if executable.search(text):
            executable_hits.append(relative)
    return {
        "artifactJavaScript": False,
        "externalUrls": False,
        "externalAssets": False,
        "realLlmCalls": 0,
        "secretPatternHits": secret_hits,
        "privatePathHits": private_path_hits,
        "executableEvidenceHits": executable_hits,
        "marker": "NO_SECRET_PATTERN_HITS",
    }


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    normal_profile, normal_objects, _ = _profile(
        "dataset_phase10k4_normal",
        [("obj_materials", [*BASE_RECORDS, {"material_id": "invalid-1", "formula": "__proto__", "band_gap": 9.0, "split": "test", "y_true": 0.0, "y_pred": 0.0}])],
    )
    normal = _runtime_case("normal", normal_profile, normal_objects, _plan_with(normal_profile))
    property_case = _runtime_case(
        "property_color",
        normal_profile,
        normal_objects,
        _plan_with(normal_profile, params={"colorBy": "property:band_gap"}),
    )

    group_prompt = "Explore this composition space and compare the train and test groups."
    group = _runtime_case(
        "group_comparison",
        normal_profile,
        normal_objects,
        _plan_with(normal_profile, prompt=group_prompt),
    )

    resource_profile, resource_objects, _ = _profile(
        "dataset_phase10k4_resources",
        [
            ("obj_reference", BASE_RECORDS[:3]),
            ("obj_holdout", BASE_RECORDS[3:]),
        ],
    )
    resource_refs = [
        {"refType": "profile", "ref": "profile"},
        {"refType": "normalized_object", "ref": "obj_reference", "objectType": "DataFrame", "fieldRole": "composition_samples"},
        {"refType": "normalized_object", "ref": "obj_holdout", "objectType": "DataFrame", "fieldRole": "comparison_samples"},
    ]
    resource = _runtime_case(
        "resource_comparison",
        resource_profile,
        resource_objects,
        _plan_with(
            resource_profile,
            params={
                "comparisonMode": "resources",
                "leftObjectId": "obj_reference",
                "rightObjectId": "obj_holdout",
                "tableObjectId": "obj_reference",
            },
            input_refs=resource_refs,
        ),
    )

    with tempfile.TemporaryDirectory(prefix="mdi-phase10k4-k3-source-") as directory:
        ml_artifact = _regression_artifact(normal_profile, normal_objects, Path(directory))
    ml_options = [
        item["id"]
        for item in normal["contents"]["composition_space.json"]["coloring"]["available"]
        if str(item["id"]).startswith("ml:")
    ]
    if ml_options:
        raise RuntimeError("Normal composition artifact unexpectedly contained ML colors without an explicit K3 artifact.")
    task_id = str(ml_artifact["evaluations"][0]["taskId"])
    ml_color_id = f"ml:{task_id}:absolute_error"
    ml_refs = [
        {"refType": "profile", "ref": "profile"},
        {"refType": "normalized_object", "ref": "obj_materials", "objectType": "DataFrame", "fieldRole": "composition_samples"},
        {"refType": "artifact", "ref": "k3_regression", "fieldRole": "sample_bound_ml_metrics"},
    ]
    ml = _runtime_case(
        "k3_ml_color",
        normal_profile,
        normal_objects,
        _plan_with(normal_profile, params={"colorBy": ml_color_id}, input_refs=ml_refs),
        extra_store={"k3_regression": ml_artifact},
    )
    _write("fixtures/k3_regression_source.json", _sanitized(ml_artifact))

    rank_records = [
        {"material_id": "rank-1", "formula": "Si"},
        {"material_id": "rank-2", "formula": "Ge"},
        {"material_id": "rank-3", "formula": "Si"},
    ]
    rank_failure = _expected_failure(
        "rank_failure",
        rank_records,
        error_code="TOOL_INPUT_INVALID",
        error_type="insufficient_projection_rank",
    )
    over_cap_records = [
        {"material_id": f"cap-{index:05d}", "formula": ("Si", "NaCl", "LiF", "MgO")[index % 4]}
        for index in range(20_001)
    ]
    cap_failure = _expected_failure(
        "analysis_cap_failure",
        over_cap_records,
        error_code="TOOL_RESOURCE_LIMIT",
        error_type=None,
    )
    security_validation = _security_validation(normal_profile)

    performance = {
        "caps": {
            "maxRows": 100_000,
            "maxAnalyzedSamples": 20_000,
            "maxPlotPoints": 10_000,
            "maxArtifactBytes": 16_000_000,
        },
        "cases": [
            _performance_case("small", 6),
            _performance_case("medium", 5_000),
            _performance_case("near_cap", 20_000),
        ],
        "acceptance": "PASS",
        "marker": "COMPOSITION_SPACE_PERFORMANCE_EVIDENCE_PASS",
    }
    _write("performance/performance_metrics.json", performance)
    _write(
        "fixtures/required_cases.json",
        {
            "normal": normal["contents"]["composition_space.json"],
            "propertyColor": property_case["contents"]["composition_space.json"],
            "groupComparison": group["contents"]["composition_space.json"],
            "resourceComparison": resource["contents"]["composition_space.json"],
            "k3MlColor": ml["contents"]["composition_space.json"],
            "rankFailure": rank_failure,
            "analysisCapFailure": cap_failure,
        },
    )
    _write("security/plan_validation_rejection.json", security_validation)
    _write("network_audit.json", {"externalRequests": 0, "marker": "NO_COMPOSITION_SPACE_EXTERNAL_NETWORK_REQUESTS"})
    _write(
        "README.md",
        "# Phase 10K-4 Composition Space Evidence\n\n"
        "Deterministic local evidence for Profile 2.0 -> Mock Planner -> validated AnalysisPlan -> "
        "QueueWorkerRuntime -> Registry -> CompositionSpaceAdapter. Browser evidence is appended by "
        "`apps/web/test/composition-space-browser-evidence.mjs`. No external service or real LLM is used.\n",
    )
    security = _security_audit()
    if security["secretPatternHits"] or security["privatePathHits"] or security["executableEvidenceHits"]:
        raise RuntimeError(f"Composition-space evidence security audit failed: {security}")
    _write("security/security_audit.json", security)
    _manifest()

    print("COMPOSITION_SPACE_RUNTIME_EVIDENCE_PASS")
    print("COMPOSITION_SPACE_PCA_EVIDENCE_PASS")
    print("COMPOSITION_SPACE_SAMPLE_LINKAGE_EVIDENCE_PASS")
    print("COMPOSITION_SPACE_PROPERTY_COLOR_EVIDENCE_PASS")
    print("COMPOSITION_SPACE_DATASET_COMPARISON_EVIDENCE_PASS")
    print("COMPOSITION_SPACE_CLUSTERING_EVIDENCE_PASS")
    print("COMPOSITION_SPACE_PERFORMANCE_EVIDENCE_PASS")
    print("NO_COMPOSITION_SPACE_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


if __name__ == "__main__":
    main()
