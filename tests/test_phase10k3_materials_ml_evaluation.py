from __future__ import annotations

import json
from pathlib import Path

import pytest

from mdi_adapters import (
    ClassificationEvaluationAdapter,
    RegressionEvaluationAdapter,
    ToolExecutionContext,
    ToolExecutionError,
    UncertaintyEvaluationAdapter,
)
from mdi_adapters.platform_builtin import binary_roc_pr, regression_metric_values
from mdi_api.phase2_runtime import build_object_store
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import build_data_profile, parse_file
from mdi_schemas import ArtifactType, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


def _profiled_csv(tmp_path: Path, text: str, *, dataset_id: str):
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / f"{dataset_id}.csv"
    path.write_text(text, encoding="utf-8")
    parsed = parse_file(path, dataset_id=dataset_id, file_id=f"file_{dataset_id}")
    assert parsed.parse_status == "success"
    registry = load_manifests()
    profile = build_data_profile(
        dataset_id=dataset_id,
        parse_results=[parsed],
        platform_tool_ids={tool.toolId for tool in registry.tools},
    )
    return profile, parsed.objects


def _execute(
    tmp_path: Path,
    adapter,
    profile,
    objects,
    *,
    params: dict | None = None,
    resource_limits: dict | None = None,
):
    registry = load_manifests()
    tool = registry.get_tool_by_id(adapter.tool_id)
    store, _ = build_object_store(objects, profile=profile)
    object_id = objects[0].id
    context = ToolExecutionContext(
        job_id="job_10k3",
        project_id="project_10k3",
        dataset_id=profile.datasetId,
        tool_id=tool.toolId,
        tool_version=tool.version,
        adapter_version=adapter.adapter_version,
        registry_version=registry.version,
        artifact_root=tmp_path,
        tool_call_id=f"call_{tool.toolId.replace('.', '_')}",
        object_store=store,
        resource_limits={**tool.resourceLimits, **(resource_limits or {})},
    )
    request = ToolExecutionRequest(
        jobId="job_10k3",
        stepId="step_001",
        toolId=tool.toolId,
        inputRefs=[
            {"refType": "profile", "ref": "profile"},
            {"refType": "normalized_object", "ref": object_id, "objectType": "DataFrame"},
        ],
        params=params or {},
        artifactTypes=[ArtifactType.table_json, ArtifactType.summary_md, ArtifactType.recipe_json],
    )
    artifacts = adapter.execute(context, request)
    product = next(item for item in artifacts if item.type == ArtifactType.table_json)
    payload = json.loads((tmp_path / product.storageKey).read_text(encoding="utf-8"))
    return payload, artifacts


def test_metric_definitions_handle_constant_target_and_curve_bounding() -> None:
    metrics = regression_metric_values([2.0, 2.0], [1.0, 3.0])
    assert metrics["mae"] == 1.0
    assert metrics["rmse"] == 1.0
    assert metrics["meanSignedError"] == 0.0
    assert metrics["r2"] is None
    assert metrics["r2Status"] == "undefined_constant_target"

    curves = binary_roc_pr([False, False, True, True], [0.1, 0.2, 0.8, 0.9], max_points=2)
    assert curves["status"] == "READY"
    assert curves["roc"]["auc"] == 1.0
    assert curves["precisionRecall"]["averagePrecision"] == 1.0
    assert len(curves["roc"]["points"]) == 2


def test_regression_product_uses_profile_groups_and_material_identity(tmp_path: Path) -> None:
    profile, objects = _profiled_csv(
        tmp_path,
        "material_id,formula,y_true,model_a_pred,model_a_std,model_b_pred,model_b_std\n"
        "s1,Si,1.0,1.1,0.10,0.9,0.20\n"
        "s2,NaCl,2.0,2.3,0.30,2.1,0.10\n"
        "s3,LiF,3.0,2.5,0.50,2.9,0.20\n"
        "s4,Si,4.0,4.2,0.20,4.1,0.10\n"
        "s5,NaCl,5.0,,0.60,4.8,0.30\n",
        dataset_id="regression_results",
    )
    payload, artifacts = _execute(tmp_path / "out", RegressionEvaluationAdapter(), profile, objects)

    assert payload["schemaVersion"] == "phase10k3.materials_ml_regression.v1"
    assert payload["semantics"]["roleInferenceRepeated"] is False
    assert payload["residualConvention"] == "prediction_minus_target"
    assert len(payload["evaluations"]) == 2
    first = next(item for item in payload["evaluations"] if item["predictionColumn"] == "model_a_pred")
    assert first["coverage"] == {
        "totalSamples": 5,
        "evaluatedSamples": 4,
        "targetMissing": 0,
        "predictionMissing": 1,
        "nonFiniteOrInvalid": 0,
        "excludedSamples": 1,
    }
    assert first["highErrorSamples"][0]["sampleRef"] == "s3"
    assert first["highErrorSamples"][0]["sampleKey"] == f"{objects[0].id}:s3"
    assert first["highErrorSamples"][0]["chemicalSystem"] == "F-Li"
    assert payload["dataset"]["datasetContentHash"]
    assert payload["dataset"]["resourceBindings"] == [
        {
            "objectId": objects[0].id,
            "objectType": "DataFrame",
            "objectHash": payload["dataset"]["resourceBindings"][0]["objectHash"],
        }
    ]
    assert {item["group"] for item in first["chemistryConditioned"]["byElement"]} >= {"Si", "Na", "Cl"}
    assert payload["modelComparisons"][0]["policy"] == "common_valid_samples"
    assert payload["modelComparisons"][0]["commonSampleCount"] == 4
    assert {item.name for item in artifacts} == {"materials_ml_regression.json", "summary.md", "recipe.json"}


def test_uncertainty_product_has_explicit_association_and_retention_policy(tmp_path: Path) -> None:
    profile, objects = _profiled_csv(
        tmp_path,
        "material_id,formula,y_true,y_pred,y_std\n"
        "s1,Si,1.0,1.05,0.05\n"
        "s2,NaCl,2.0,2.20,0.20\n"
        "s3,LiF,3.0,3.60,0.60\n"
        "s4,GaAs,4.0,4.10,0.10\n",
        dataset_id="uncertainty_results",
    )
    payload, _ = _execute(
        tmp_path / "out",
        UncertaintyEvaluationAdapter(),
        profile,
        objects,
        params={"uncertaintyBins": 2},
    )

    evaluation = payload["evaluations"][0]
    assert payload["schemaVersion"] == "phase10k3.materials_ml_uncertainty.v1"
    assert evaluation["uncertaintyKind"] == "source_defined_uncertainty"
    assert evaluation["reliability"]["method"] == "equal_count_mean_uncertainty_vs_mean_absolute_error"
    assert len(evaluation["reliability"]["bins"]) == 2
    assert evaluation["errorDecay"]["method"] == "retain_lowest_uncertainty_first"
    assert evaluation["highUncertaintySamples"][0]["sampleRef"] == "s3"
    assert evaluation["highUncertaintySamples"][0]["sampleKey"] == f"{objects[0].id}:s3"
    assert evaluation["warnings"] == ["UNCERTAINTY_DIAGNOSTIC_NOT_CALIBRATION_AUTHORITY"]


def test_classification_product_preserves_class_labels_and_binary_curves(tmp_path: Path) -> None:
    profile, objects = _profiled_csv(
        tmp_path,
        "material_id,formula,class_true,class_pred,prob_A,prob_B\n"
        "s1,Si,A,A,0.90,0.10\n"
        "s2,NaCl,B,B,0.20,0.80\n"
        "s3,LiF,A,B,0.40,0.60\n"
        "s4,GaAs,B,B,0.10,0.90\n",
        dataset_id="classification_results",
    )
    payload, artifacts = _execute(
        tmp_path / "out",
        ClassificationEvaluationAdapter(),
        profile,
        objects,
        params={"positiveClass": "B"},
    )

    evaluation = payload["evaluations"][0]
    assert payload["schemaVersion"] == "phase10k3.materials_ml_classification.v1"
    assert evaluation["metrics"]["confusionMatrix"] == {
        "normalization": "raw_counts",
        "labels": ["A", "B"],
        "values": [[1, 1], [0, 2]],
    }
    assert evaluation["metrics"]["accuracy"] == 0.75
    assert evaluation["curves"]["status"] == "READY"
    assert evaluation["curves"]["positiveClass"] == "B"
    assert evaluation["sampleRows"][0]["probabilities"] == {"A": 0.9, "B": 0.1}
    assert evaluation["misclassifiedSamples"][0]["sampleRef"] == "s3"
    assert evaluation["misclassifiedSamples"][0]["sampleKey"] == f"{objects[0].id}:s3"
    assert {item.name for item in artifacts} == {"materials_ml_classification.json", "summary.md", "recipe.json"}


def test_registry_contracts_are_strict_profile_bound_and_bounded() -> None:
    registry = load_manifests()
    for tool_id in (
        "ml.regression_evaluation",
        "ml.uncertainty_evaluation",
        "ml.classification_evaluation",
    ):
        tool = registry.get_tool_by_id(tool_id)
        assert tool.paramsSchema["additionalProperties"] is False
        assert tool.resourceLimits["maxRows"] == 100000
        assert tool.resourceLimits["maxArtifactBytes"] == 8000000
        assert "Profile 2.0" in tool.inputSchema.inputOptions[0].description
        assert tool.adapter.endswith("EvaluationAdapter")


def test_profile_readiness_becomes_available_only_for_registered_products(tmp_path: Path) -> None:
    profile, _ = _profiled_csv(
        tmp_path,
        "material_id,y_true,y_pred,y_std\ns1,1.0,1.1,0.1\n",
        dataset_id="readiness",
    )
    readiness = {item.capability: item for item in profile.analysisReadiness}
    assert readiness["regression_evaluation"].platformStatus == "AVAILABLE"
    assert readiness["uncertainty_evaluation"].platformStatus == "AVAILABLE"
    assert readiness["classification_evaluation"].dataStatus == "MISSING_REQUIRED_DATA"
    assert readiness["classification_evaluation"].platformStatus == "AVAILABLE"


def test_typed_semantic_unit_uncertainty_and_cap_failures(tmp_path: Path) -> None:
    ambiguous_profile, ambiguous_objects = _profiled_csv(
        tmp_path / "ambiguous",
        "material_id,y_true,target,y_pred\ns1,1.0,1.0,1.1\n",
        dataset_id="ambiguous",
    )
    with pytest.raises(ToolExecutionError) as ambiguous:
        _execute(tmp_path / "ambiguous_out", RegressionEvaluationAdapter(), ambiguous_profile, ambiguous_objects)
    assert ambiguous.value.details["errorType"] == "ambiguous_semantic_binding"

    profile, objects = _profiled_csv(
        tmp_path / "unit",
        "material_id,y_true,y_pred\ns1,1.0,1.1\ns2,2.0,2.1\n",
        dataset_id="units",
    )
    for column in profile.semanticColumns:
        if column.column == "y_true":
            column.unit = "eV"
        if column.column == "y_pred":
            column.unit = "meV"
    with pytest.raises(ToolExecutionError) as units:
        _execute(tmp_path / "unit_out", RegressionEvaluationAdapter(), profile, objects)
    assert units.value.details["errorType"] == "incompatible_units"

    negative_profile, negative_objects = _profiled_csv(
        tmp_path / "negative",
        "material_id,y_true,y_pred,y_std\ns1,1.0,1.1,-0.1\ns2,2.0,2.2,0.2\n",
        dataset_id="negative_uncertainty",
    )
    with pytest.raises(ToolExecutionError) as uncertainty:
        _execute(tmp_path / "negative_out", UncertaintyEvaluationAdapter(), negative_profile, negative_objects)
    assert uncertainty.value.details["errorType"] == "invalid_uncertainty"

    with pytest.raises(ToolExecutionError) as cap:
        _execute(
            tmp_path / "cap_out",
            RegressionEvaluationAdapter(),
            profile,
            objects,
            resource_limits={"maxRows": 1},
        )
    assert cap.value.code == "TOOL_RESOURCE_LIMIT"
    assert cap.value.details["maxRows"] == 1


def test_classification_missing_probability_multiclass_and_unknown_positive_policy(tmp_path: Path) -> None:
    no_probability_profile, no_probability_objects = _profiled_csv(
        tmp_path / "no_probability",
        "material_id,class_true,class_pred\ns1,A,A\ns2,B,B\n",
        dataset_id="classification_no_probability",
    )
    payload, _ = _execute(
        tmp_path / "no_probability_out",
        ClassificationEvaluationAdapter(),
        no_probability_profile,
        no_probability_objects,
        params={"positiveClass": "b"},
    )
    assert payload["evaluations"][0]["curves"]["status"] == "UNAVAILABLE_CLASS_PROBABILITY_MISSING"

    multiclass_profile, multiclass_objects = _profiled_csv(
        tmp_path / "multiclass",
        "material_id,class_true,class_pred,prob_A,prob_B,prob_C\n"
        "s1,A,A,0.8,0.1,0.1\ns2,B,B,0.1,0.8,0.1\ns3,C,B,0.1,0.6,0.3\n",
        dataset_id="classification_multiclass",
    )
    multiclass, _ = _execute(
        tmp_path / "multiclass_out",
        ClassificationEvaluationAdapter(),
        multiclass_profile,
        multiclass_objects,
    )
    assert multiclass["evaluations"][0]["curves"]["status"] == "UNAVAILABLE_MULTICLASS_DEFERRED"
    assert {item["class"] for item in multiclass["evaluations"][0]["metrics"]["perClass"]} == {"A", "B", "C"}

    binary_profile, binary_objects = _profiled_csv(
        tmp_path / "unknown_positive",
        "material_id,class_true,class_pred,prob_A,prob_B\ns1,A,A,0.9,0.1\ns2,B,B,0.2,0.8\n",
        dataset_id="classification_unknown_positive",
    )
    with pytest.raises(ToolExecutionError) as positive:
        _execute(
            tmp_path / "unknown_positive_out",
            ClassificationEvaluationAdapter(),
            binary_profile,
            binary_objects,
            params={"positiveClass": "c"},
        )
    assert positive.value.details["errorType"] == "unknown_positive_class"


def test_classification_rejects_ambiguous_case_folded_positive_class(tmp_path: Path) -> None:
    profile, objects = _profiled_csv(
        tmp_path / "case_ambiguous",
        "material_id,class_true,class_pred\n"
        "s1,AA,AA\n"
        "s2,aa,aa\n",
        dataset_id="classification_case_ambiguous",
    )
    with pytest.raises(ToolExecutionError) as positive:
        _execute(
            tmp_path / "case_ambiguous_out",
            ClassificationEvaluationAdapter(),
            profile,
            objects,
            params={"positiveClass": "Aa"},
        )
    assert positive.value.details["errorType"] == "ambiguous_positive_class"


def test_payload_replay_is_deterministic_and_plot_sampling_does_not_change_metrics(tmp_path: Path) -> None:
    rows = "".join(f"s{index},Si,{index},{index + (index % 3) * 0.1}\n" for index in range(30))
    profile, objects = _profiled_csv(
        tmp_path,
        f"material_id,formula,y_true,y_pred\n{rows}",
        dataset_id="deterministic_regression",
    )
    first, _ = _execute(
        tmp_path / "first",
        RegressionEvaluationAdapter(),
        profile,
        objects,
        params={"maxPlotPoints": 10},
    )
    second, _ = _execute(
        tmp_path / "second",
        RegressionEvaluationAdapter(),
        profile,
        objects,
        params={"maxPlotPoints": 10},
    )
    assert first == second
    evaluation = first["evaluations"][0]
    assert evaluation["metrics"]["sampleCount"] == 30
    assert len(evaluation["parityPoints"]) == 10
    assert evaluation["visualizationSampling"] == {
        "policy": "deterministic_even_index",
        "sourceCount": 30,
        "displayCount": 10,
    }


@pytest.mark.parametrize(
    ("prompt", "expected_tool"),
    [
        ("Analyze model performance and prediction error.", "ml.regression_evaluation"),
        ("Analyze uncertainty reliability and error decay.", "ml.uncertainty_evaluation"),
    ],
)
def test_planner_routes_profile_bound_regression_products(
    tmp_path: Path,
    prompt: str,
    expected_tool: str,
) -> None:
    profile, objects = _profiled_csv(
        tmp_path,
        "material_id,formula,y_true,y_pred,y_std\ns1,Si,1.0,1.1,0.1\ns2,NaCl,2.0,2.2,0.2\n",
        dataset_id=f"planner_{expected_tool.rsplit('.', 1)[-1]}",
    )
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
    plan = response.raw_json
    assert plan is not None
    step = plan["steps"][0]
    assert step["toolId"] == expected_tool
    assert step["inputRefs"] == [
        {"refType": "profile", "ref": "profile"},
        {
            "refType": "normalized_object",
            "ref": objects[0].id,
            "objectType": "DataFrame",
            "fieldRole": "ml_result_table",
        },
    ]
    assert validate_plan(plan, registry=registry).ok


def test_planner_routes_classification_with_explicit_positive_class(tmp_path: Path) -> None:
    profile, _ = _profiled_csv(
        tmp_path,
        "material_id,class_true,class_pred,prob_A,prob_B\ns1,A,A,0.9,0.1\ns2,B,B,0.2,0.8\n",
        dataset_id="planner_classification",
    )
    registry = load_manifests()
    plan = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt="Show the classification confusion matrix and ROC with positive class B.",
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            tool_registry_version=registry.version,
        ),
        tools=registry.list_mvp_tools(),
        data_profile=profile,
    ).raw_json
    assert plan is not None
    assert plan["steps"][0]["toolId"] == "ml.classification_evaluation"
    assert plan["steps"][0]["params"]["positiveClass"] == "b"
    assert validate_plan(plan, registry=registry).ok

    invalid = json.loads(json.dumps(plan))
    invalid["steps"][0]["params"]["remoteUrl"] = "https://invalid.example"
    validation = validate_plan(invalid, registry=registry)
    assert not validation.ok
    assert any(error.code == "PARAMS_SCHEMA_INVALID" for error in validation.errors)


def test_planner_does_not_fall_back_to_basic_metrics_for_ambiguous_profile(tmp_path: Path) -> None:
    profile, _ = _profiled_csv(
        tmp_path,
        "material_id,formula,y_true,target,y_pred\ns1,Si,1.0,1.0,1.1\ns2,NaCl,2.0,2.0,2.2\n",
        dataset_id="planner_ambiguous_regression",
    )
    registry = load_manifests()
    plan = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt="Analyze model performance and prediction error.",
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            tool_registry_version=registry.version,
        ),
        tools=registry.list_mvp_tools(),
        data_profile=profile,
    ).raw_json
    assert plan is not None
    assert plan["steps"][0]["toolId"] == "dataset.materials_explorer"
    assert "ambiguous" in plan["steps"][0]["purpose"].lower()
    assert validate_plan(plan, registry=registry).ok


def test_persisted_regression_plan_executes_through_queue_runtime(tmp_path: Path) -> None:
    profile, objects = _profiled_csv(
        tmp_path,
        "material_id,formula,y_true,y_pred\ns1,Si,1.0,1.1\ns2,NaCl,2.0,2.2\n",
        dataset_id="runtime_regression",
    )
    registry = load_manifests()
    raw_plan = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt="Analyze model performance and prediction error.",
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            tool_registry_version=registry.version,
        ),
        tools=registry.list_mvp_tools(),
        data_profile=profile,
    ).raw_json
    assert raw_plan is not None
    repositories = InMemoryRepositoryBundle.create()
    runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=tmp_path / "runtime")
    created = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Analyze model performance and prediction error.",
            projectId="project_10k3",
            datasetId=profile.datasetId,
            profileId=profile.profileId,
            enqueue=True,
        ),
        provider=MockLLMProvider(fixed_plan=raw_plan),
        repositories=repositories,
        queue_runtime=runtime,
        registry=registry,
    )
    assert created.ok
    store, _ = build_object_store(objects, profile=profile)
    worker = runtime.handle_job(created.job_id or "", object_store=store)
    assert worker.status == "completed"
    calls = repositories.tool_calls.list_for_job(created.job_id or "")
    artifacts = repositories.artifacts.list_for_job(created.job_id or "")
    assert [call["toolId"] for call in calls] == ["ml.regression_evaluation"]
    assert {item["name"] for item in artifacts} >= {
        "materials_ml_regression.json",
        "summary.md",
        "recipe.json",
    }
