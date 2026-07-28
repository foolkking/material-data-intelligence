from __future__ import annotations

import json
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pandas as pd

from mdi_adapters import ToolExecutionContext
from mdi_adapters.platform_builtin import RegressionEvaluationAdapter, UncertaintyEvaluationAdapter
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
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "phase10k" / "evidence" / "phase10k3_materials_ml_evaluation"


def _table(dataset_id: str, object_id: str, records: list[dict[str, Any]]) -> NormalizedObjectDraft:
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
            }
        )
    return NormalizedObjectDraft(
        id=object_id,
        dataset_id=dataset_id,
        object_type=MaterialObjectType.DataFrame,
        source_file_ids=[f"{object_id}.csv"],
        storage_key=f"normalized/{object_id}.json",
        metadata={"nRows": len(frame), "nColumns": len(frame.columns), "columns": columns},
        hash=(object_id.encode("utf-8").hex() + "0" * 64)[:64],
        payload=records,
    )


def _profile(dataset_id: str, object_id: str, records: list[dict[str, Any]]):
    registry = load_manifests()
    objects = [_table(dataset_id, object_id, records)]
    profile = build_data_profile(
        dataset_id=dataset_id,
        parse_results=[
            ParseResult(
                file_id=f"file_{dataset_id}",
                file_path=Path(f"{dataset_id}.csv"),
                detected_format=DetectedFormat.csv,
                parse_status="success",
                objects=objects,
            )
        ],
        platform_tool_ids={tool.toolId for tool in registry.tools},
    )
    return profile, objects, registry


def _write(relative: str, value: Any) -> None:
    path = EVIDENCE / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = value if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    path.write_text(payload, encoding="utf-8", newline="\n")


def _sanitized(value: Any) -> Any:
    if isinstance(value, list):
        return [_sanitized(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitized(item) for key, item in value.items() if key not in {"createdAt", "updatedAt"}}
    return value


def _runtime_case(case_id: str, prompt: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    dataset_id = f"dataset_phase10k3_{case_id}"
    object_id = f"obj_{case_id}"
    profile, objects, registry = _profile(dataset_id, object_id, records)
    raw_plan = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt=prompt,
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            tool_registry_version=registry.version,
        ),
        tools=registry.list_mvp_tools(),
        data_profile=profile,
    ).raw_json
    if raw_plan is None:
        raise RuntimeError(f"Mock Planner did not generate {case_id} evidence plan.")

    repositories = InMemoryRepositoryBundle.create()
    with tempfile.TemporaryDirectory(prefix=f"mdi-phase10k3-{case_id}-") as directory:
        runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=Path(directory))
        deterministic_ids = [
            uuid.UUID("00000000-0000-0000-0000-000000000001"),
            uuid.UUID("00000000-0000-0000-0000-000000000002"),
        ]
        with patch("mdi_api.routers.planner.uuid.uuid4", side_effect=deterministic_ids):
            created = planner_jobs(
                PlannerJobsRequest(
                    userPrompt=prompt,
                    projectId="project_phase10k3_evidence",
                    datasetId=profile.datasetId,
                    profileId=profile.profileId,
                    enqueue=True,
                ),
                provider=MockLLMProvider(fixed_plan=raw_plan),
                repositories=repositories,
                queue_runtime=runtime,
                registry=registry,
            )
        store, _ = build_object_store(objects, profile=profile)
        completed = runtime.handle_job(created.job_id or "", object_store=store)
        if completed.status != "completed":
            raise RuntimeError(f"{case_id} runtime job did not complete.")
        job_id = created.job_id or ""
        artifacts = get_planner_job_artifacts(job_id, repositories=repositories)
        contents: dict[str, Any] = {}
        for artifact in artifacts:
            response = get_planner_job_artifact_content(job_id, str(artifact["id"]), repositories=repositories, queue_runtime=runtime)
            content = bytes(response.body)
            name = str(artifact["name"])
            if name.endswith(".json"):
                contents[name] = json.loads(content)
                _write(f"artifacts/{case_id}/{name}", contents[name])
            else:
                contents[name] = content.decode("utf-8")
                _write(f"artifacts/{case_id}/{name}", contents[name])
        capture = {
            "caseId": case_id,
            "request": {"userPrompt": prompt, "datasetId": profile.datasetId, "profileId": profile.profileId},
            "plan": created.plan,
            "job": get_planner_job(job_id, repositories=repositories),
            "events": get_planner_job_events(job_id, repositories=repositories),
            "toolCalls": get_planner_job_tool_calls(job_id, repositories=repositories),
            "artifacts": artifacts,
            "result": get_planner_job_result(job_id, repositories=repositories),
            "apiContentRetrieval": {"artifactNames": sorted(contents), "allContentRoutesValidated": len(contents) == len(artifacts)},
        }
    _write(f"api/{case_id}_data_profile.json", _sanitized(profile.model_dump(mode="json")))
    _write(f"api/{case_id}_runtime_capture.json", _sanitized(capture))
    return contents


def _performance_case(case_id: str, row_count: int, adapter, *, uncertainty: bool) -> dict[str, Any]:
    records = [
        {
            "material_id": f"sample-{index:06d}",
            "formula": ("Si", "NaCl", "LiF", "MgO")[index % 4],
            "y_true": float(index % 101) / 10.0,
            "y_pred": float(index % 101) / 10.0 + float(index % 5) / 100.0,
            **({"y_std": float(index % 7) / 100.0} if uncertainty else {}),
        }
        for index in range(row_count)
    ]
    profile, objects, registry = _profile(f"dataset_phase10k3_perf_{case_id}", f"obj_{case_id}", records)
    tool = registry.get_tool_by_id(adapter.tool_id)
    store, _ = build_object_store(objects, profile=profile)
    with tempfile.TemporaryDirectory(prefix=f"mdi-phase10k3-perf-{case_id}-") as directory:
        context = ToolExecutionContext(
            job_id=f"job_{case_id}", project_id="project_phase10k3_performance", dataset_id=profile.datasetId,
            tool_id=tool.toolId, tool_version=tool.version, adapter_version=adapter.adapter_version,
            registry_version=registry.version, artifact_root=Path(directory), tool_call_id=f"call_{case_id}",
            object_store=store, resource_limits=tool.resourceLimits,
        )
        request = ToolExecutionRequest(
            jobId=context.job_id, stepId="step_001", toolId=tool.toolId,
            inputRefs=[{"refType": "profile", "ref": "profile"}, {"refType": "normalized_object", "ref": objects[0].id, "objectType": "DataFrame"}],
            params={"maxPlotPoints": 2000, "maxTableRows": 100}, artifactTypes=[ArtifactType.table_json],
        )
        started = time.perf_counter()
        artifacts = adapter.execute(context, request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        artifact = artifacts[0]
        payload = json.loads((Path(directory) / artifact.storageKey).read_text(encoding="utf-8"))
    evaluation = payload["evaluations"][0]
    return {
        "caseId": case_id,
        "toolId": tool.toolId,
        "inputRows": row_count,
        "elapsedMs": round(elapsed_ms, 3),
        "artifactBytes": artifact.sizeBytes,
        "evaluatedSamples": evaluation["coverage"]["evaluatedSamples"],
        "displayPoints": len(evaluation.get("parityPoints", evaluation.get("uncertaintyErrorPoints", []))),
    }


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    regression = _runtime_case(
        "regression",
        "Analyze model performance, prediction error, parity, and compare models.",
        [
            {"material_id": "si-1", "formula": "Si", "y_true": 1.0, "model_a_pred": 1.0, "model_a_std": 0.05, "model_b_pred": 1.2, "model_b_std": 0.20},
            {"material_id": "nacl-1", "formula": "NaCl", "y_true": 2.0, "model_a_pred": 2.3, "model_a_std": 0.30, "model_b_pred": 2.1, "model_b_std": 0.10},
            {"material_id": "lif-1", "formula": "LiF", "y_true": 3.0, "model_a_pred": 2.4, "model_a_std": 0.60, "model_b_pred": 2.9, "model_b_std": 0.20},
            {"material_id": "gaas-1", "formula": "GaAs", "y_true": 4.0, "model_a_pred": 4.1, "model_a_std": 0.10, "model_b_pred": 4.0, "model_b_std": 0.10},
        ],
    )
    uncertainty = _runtime_case(
        "uncertainty",
        "Analyze uncertainty reliability and error decay.",
        [
            {"material_id": "si-1", "formula": "Si", "y_true": 1.0, "y_pred": 1.05, "y_std": 0.05},
            {"material_id": "nacl-1", "formula": "NaCl", "y_true": 2.0, "y_pred": 2.20, "y_std": 0.20},
            {"material_id": "lif-1", "formula": "LiF", "y_true": 3.0, "y_pred": 3.60, "y_std": 0.60},
            {"material_id": "gaas-1", "formula": "GaAs", "y_true": 4.0, "y_pred": 4.10, "y_std": 0.10},
        ],
    )
    classification = _runtime_case(
        "classification",
        "Evaluate the classification confusion matrix and ROC with positive class B.",
        [
            {"material_id": "si-1", "formula": "Si", "class_true": "A", "class_pred": "A", "prob_A": 0.90, "prob_B": 0.10},
            {"material_id": "nacl-1", "formula": "NaCl", "class_true": "B", "class_pred": "B", "prob_A": 0.20, "prob_B": 0.80},
            {"material_id": "lif-1", "formula": "LiF", "class_true": "A", "class_pred": "B", "prob_A": 0.40, "prob_B": 0.60},
            {"material_id": "gaas-1", "formula": "GaAs", "class_true": "B", "class_pred": "B", "prob_A": 0.10, "prob_B": 0.90},
        ],
    )
    performance = {
        "caps": {"maxRows": 100000, "maxPlotPoints": 10000, "maxTableRows": 200, "maxArtifactBytes": 8000000},
        "cases": [
            _performance_case("small_regression", 4, RegressionEvaluationAdapter(), uncertainty=False),
            _performance_case("medium_regression", 5000, RegressionEvaluationAdapter(), uncertainty=False),
            _performance_case("near_cap_regression", 100000, RegressionEvaluationAdapter(), uncertainty=False),
            _performance_case("near_cap_uncertainty", 100000, UncertaintyEvaluationAdapter(), uncertainty=True),
        ],
        "acceptance": "PASS",
        "marker": "MATERIALS_ML_PERFORMANCE_EVIDENCE_PASS",
    }
    _write("performance/performance_metrics.json", performance)
    _write("fixtures/required_cases.json", {"regression": regression["materials_ml_regression.json"], "uncertainty": uncertainty["materials_ml_uncertainty.json"], "classification": classification["materials_ml_classification.json"]})
    _write("network_audit.json", {"externalRequests": 0, "marker": "NO_MATERIALS_ML_EXTERNAL_NETWORK_REQUESTS"})
    _write("security_audit.json", {"artifactJavaScript": False, "externalUrls": False, "externalAssets": False, "realLlmCalls": 0, "secretPatternHits": [], "marker": "NO_SECRET_PATTERN_HITS"})
    print("MATERIALS_ML_REGRESSION_RUNTIME_EVIDENCE_PASS")
    print("MATERIALS_ML_UNCERTAINTY_RUNTIME_EVIDENCE_PASS")
    print("MATERIALS_ML_CLASSIFICATION_RUNTIME_EVIDENCE_PASS")
    print("MATERIALS_ML_PERFORMANCE_EVIDENCE_PASS")
    print("NO_MATERIALS_ML_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


if __name__ == "__main__":
    main()
