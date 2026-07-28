from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

from mdi_artifact_core import content_hash
from jsonschema import Draft202012Validator

from mdi_adapters import CompositionSpaceAdapter, ToolExecutionContext, ToolExecutionError
from mdi_api.phase2_runtime import build_object_store
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import NormalizedObjectDraft, ParseResult, build_data_profile
from mdi_material_parsers.models import DetectedFormat
from mdi_schemas import ArtifactType, DataProfile, MaterialObjectType, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


def _table_object(
    dataset_id: str,
    object_id: str,
    records: list[dict[str, object]],
    *,
    units: dict[str, str] | None = None,
) -> NormalizedObjectDraft:
    frame = pd.DataFrame(records)
    columns: list[dict[str, object]] = []
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
                "unit": (units or {}).get(str(name)),
                "finiteCount": int(finite.notna().sum()) if finite is not None else None,
            }
        )
    payload_text = json.dumps(records, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return NormalizedObjectDraft(
        id=object_id,
        dataset_id=dataset_id,
        object_type=MaterialObjectType.DataFrame,
        source_file_ids=[f"{object_id}.csv"],
        storage_key=f"normalized/{object_id}.json",
        metadata={"nRows": len(frame), "nColumns": len(frame.columns), "columns": columns},
        hash=hashlib.sha256(payload_text.encode("utf-8")).hexdigest(),
        payload=records,
    )


def _profile_and_objects(
    dataset_id: str,
    tables: list[tuple[str, list[dict[str, object]], dict[str, str] | None]],
) -> tuple[DataProfile, list[NormalizedObjectDraft]]:
    objects = [
        _table_object(dataset_id, object_id, records, units=units)
        for object_id, records, units in tables
    ]
    result = ParseResult(
        file_id=f"file_{dataset_id}",
        file_path=Path(f"{dataset_id}.json"),
        detected_format=DetectedFormat.json_limited,
        parse_status="success",
        objects=objects,
    )
    registry = load_manifests()
    profile = build_data_profile(
        dataset_id=dataset_id,
        parse_results=[result],
        platform_tool_ids={tool.toolId for tool in registry.tools},
    )
    return profile, objects


def _single_table_profile(
    dataset_id: str,
    records: list[dict[str, object]],
    *,
    units: dict[str, str] | None = None,
    object_id: str = "obj_compositions",
) -> tuple[DataProfile, list[NormalizedObjectDraft]]:
    return _profile_and_objects(dataset_id, [(object_id, records, units)])


def _execute(
    tmp_path: Path,
    profile: DataProfile,
    objects: list[NormalizedObjectDraft],
    *,
    params: dict[str, object] | None = None,
    table_object_ids: list[str] | None = None,
    ml_artifact: dict[str, object] | None = None,
    resource_limits: dict[str, int] | None = None,
    artifact_types: list[ArtifactType] | None = None,
) -> tuple[dict[str, Any], list[Any]]:
    registry = load_manifests()
    tool = registry.get_tool_by_id("dataset.composition_space")
    store, refs = build_object_store(objects, profile=profile)
    selected_ids = table_object_ids or [str((params or {}).get("tableObjectId") or refs["dataset_table"])]
    input_refs: list[dict[str, object]] = [{"refType": "profile", "ref": "profile"}]
    for object_id in selected_ids:
        input_refs.append(
            {"refType": "normalized_object", "ref": object_id, "objectType": "DataFrame"}
        )
    if ml_artifact is not None:
        store["ml_artifact"] = ml_artifact
        input_refs.append({"refType": "artifact", "ref": "ml_artifact"})

    context = ToolExecutionContext(
        job_id="job_10k4",
        project_id="project_10k4",
        dataset_id=profile.datasetId,
        tool_id=tool.toolId,
        tool_version=tool.version,
        adapter_version=CompositionSpaceAdapter.adapter_version,
        registry_version=registry.version,
        artifact_root=tmp_path,
        tool_call_id="call_10k4_composition_space",
        object_store=store,
        resource_limits={**tool.resourceLimits, **(resource_limits or {})},
    )
    request = ToolExecutionRequest(
        jobId="job_10k4",
        stepId="step_001",
        toolId=tool.toolId,
        inputRefs=input_refs,
        params={
            "tableObjectId": selected_ids[0],
            "comparisonMode": "none",
            "projectionDimensions": 2,
            "clusteringEnabled": False,
            **(params or {}),
        },
        artifactTypes=artifact_types
        or [
            ArtifactType.table_json,
            ArtifactType.plotly_json,
            ArtifactType.summary_md,
            ArtifactType.recipe_json,
        ],
    )
    artifacts = CompositionSpaceAdapter().execute(context, request)
    product = next(item for item in artifacts if item.name == "composition_space.json")
    payload = json.loads((tmp_path / product.storageKey).read_text(encoding="utf-8"))
    return payload, artifacts


def _representative_records(*, with_ids: bool = True) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [
        {"formula": "C", "band_gap": 0.0},
        {"formula": "O2", "band_gap": 1.0},
        {"formula": "NaCl", "band_gap": 5.6},
        {"formula": "SiO2", "band_gap": 8.9},
        {"formula": "LiF", "band_gap": 13.6},
        {"formula": "GaAs", "band_gap": 1.42},
    ]
    if with_ids:
        for index, row in enumerate(rows, start=1):
            row["material_id"] = f"m{index}"
    return rows


def test_registry_contract_is_strict_profile_bound_and_bounded() -> None:
    registry = load_manifests()
    tool = registry.get_tool_by_id("dataset.composition_space")

    assert tool.domain.value == "dataset"
    assert tool.adapter == "CompositionSpaceAdapter"
    assert tool.outputSchema.displayTarget.value == "composition"
    assert set(tool.artifactTypes) == {
        ArtifactType.table_json,
        ArtifactType.plotly_json,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }
    assert "Profile 2.0" in tool.inputSchema.inputOptions[0].description
    assert "Phase 10K-3 artifact" in tool.inputSchema.inputOptions[0].description
    assert tool.paramsSchema["additionalProperties"] is False
    assert tool.paramsSchema["properties"]["projectionDimensions"] == {"const": 2}
    assert tool.paramsSchema["properties"]["nClusters"] == {
        "type": "integer",
        "minimum": 2,
        "maximum": 12,
    }
    assert tool.resourceLimits == {
        "maxRows": 100000,
        "maxAnalyzedSamples": 20000,
        "maxElements": 118,
        "maxClusters": 12,
        "maxPlotPoints": 10000,
        "maxOutlierRows": 200,
        "maxColorProperties": 16,
        "maxWarnings": 128,
        "maxArtifactBytes": 16000000,
    }
    assert tool.defaultTimeoutSec == 120
    assert tool.maxTimeoutSec == 300

    validator = Draft202012Validator(tool.paramsSchema)
    for invalid in (
        {"remoteUrl": "https://invalid.example"},
        {"projectionDimensions": 3},
        {"nClusters": 13},
        {"tolerance": 0},
        {"maxPlotPoints": 10001},
    ):
        assert list(validator.iter_errors(invalid)), invalid


def test_profile_bound_atomic_number_basis_and_normalized_fractions(tmp_path: Path) -> None:
    profile, objects = _single_table_profile(
        "basis",
        _representative_records(),
        units={"band_gap": "eV"},
    )
    payload, _ = _execute(tmp_path, profile, objects)

    representation = payload["featureRepresentation"]
    assert representation["type"] == "normalized_atomic_fraction"
    assert representation["basisOrder"] == "atomic_number_ascending"
    assert representation["elementBasis"] == ["Li", "C", "O", "F", "Na", "Si", "Cl", "Ga", "As"]
    assert representation["fractionalOccupancySupported"] is True
    points = {point["sampleRef"]: point for point in payload["points"]}
    assert points["m3"]["elementFractions"] == {"Na": 0.5, "Cl": 0.5}
    assert points["m4"]["elementFractions"] == pytest.approx({"Si": 1 / 3, "O": 2 / 3})
    assert all(sum(point["elementFractions"].values()) == pytest.approx(1.0) for point in points.values())
    assert payload["semantics"]["roleInferenceRepeated"] is False
    assert payload["semantics"]["sampleIdentityPreserved"] is True


def test_center_only_pca_sign_explained_variance_and_replay_are_deterministic(tmp_path: Path) -> None:
    profile, objects = _single_table_profile("pca_replay", _representative_records())
    first, _ = _execute(tmp_path / "first", profile, objects)
    second, _ = _execute(tmp_path / "second", profile, objects)

    assert first == second
    projection = first["projection"]
    assert projection["method"] == "PCA"
    assert projection["centering"] is True
    assert projection["scaling"] == "none"
    assert projection["solver"] == "sklearn_full_svd"
    assert projection["signConvention"] == "largest_absolute_loading_is_positive"
    assert projection["rank"] >= 2
    assert 0 < projection["cumulativeExplainedVarianceRatio"] <= 1.0 + 1e-12
    assert sum(projection["explainedVarianceRatio"]) == pytest.approx(
        projection["cumulativeExplainedVarianceRatio"]
    )
    for component in projection["components"]:
        pivot = int(np.argmax(np.abs(component)))
        assert component[pivot] >= 0

    basis = first["featureRepresentation"]["elementBasis"]
    matrix = np.asarray(
        [[point["elementFractions"].get(element, 0.0) for element in basis] for point in first["points"]]
    )
    assert projection["mean"] == pytest.approx(np.mean(matrix, axis=0).tolist())


def test_pca_rejects_insufficient_sample_count_and_rank(tmp_path: Path) -> None:
    too_small, too_small_objects = _single_table_profile(
        "too_small",
        [{"formula": "Si"}, {"formula": "NaCl"}],
    )
    with pytest.raises(ToolExecutionError) as sample_error:
        _execute(tmp_path / "small", too_small, too_small_objects)
    assert sample_error.value.code == "TOOL_INPUT_INVALID"
    assert sample_error.value.details["errorType"] == "insufficient_valid_samples"

    rank_one, rank_one_objects = _single_table_profile(
        "rank_one",
        [{"formula": "Si"}, {"formula": "Ge"}, {"formula": "SiGe"}, {"formula": "Si2Ge"}],
    )
    with pytest.raises(ToolExecutionError) as rank_error:
        _execute(tmp_path / "rank", rank_one, rank_one_objects)
    assert rank_error.value.code == "TOOL_INPUT_INVALID"
    assert rank_error.value.details == {
        "errorType": "insufficient_projection_rank",
        "rank": 1,
        "requiredRank": 2,
    }


def test_kmeans_uses_original_feature_space_and_stable_centroid_labels(tmp_path: Path) -> None:
    records = [
        {"material_id": "li1", "formula": "LiF"},
        {"material_id": "li2", "formula": "Li2F"},
        {"material_id": "li3", "formula": "LiF2"},
        {"material_id": "na1", "formula": "NaCl"},
        {"material_id": "na2", "formula": "Na2Cl"},
        {"material_id": "na3", "formula": "NaCl2"},
    ]
    profile, objects = _single_table_profile("kmeans", records)
    params = {
        "clusteringEnabled": True,
        "nClusters": 2,
        "randomState": 17,
        "nInit": 20,
        "maxIterations": 300,
        "tolerance": 0.0001,
    }
    first, _ = _execute(tmp_path / "first", profile, objects, params=params)
    second, _ = _execute(tmp_path / "second", profile, objects, params=params)

    assert first == second
    clustering = first["clustering"]
    assert clustering["status"] == "READY"
    assert clustering["method"] == "kmeans_lloyd"
    assert clustering["featureSpace"] == "normalized_atomic_fraction"
    assert clustering["parameters"] == {
        "nClusters": 2,
        "randomState": 17,
        "nInit": 20,
        "maxIterations": 300,
        "tolerance": 0.0001,
        "labelOrdering": "centroid_lexicographic",
    }
    labels = {point["sampleRef"]: point["cluster"] for point in first["points"]}
    assert len({labels[key] for key in ("li1", "li2", "li3")}) == 1
    assert len({labels[key] for key in ("na1", "na2", "na3")}) == 1
    assert labels["li1"] != labels["na1"]
    assert [cluster["cluster"] for cluster in clustering["clusters"]] == [0, 1]
    assert clustering["scientificAuthority"] == "descriptive_composition_clusters_not_material_families"


def test_invalid_formula_accounting_is_explicit_and_not_silent(tmp_path: Path) -> None:
    records = _representative_records()[:4] + [
        {"material_id": "bad1", "formula": "not-a-formula", "band_gap": 1.0},
        {"material_id": "bad2", "formula": None, "band_gap": 2.0},
    ]
    profile, objects = _single_table_profile("invalid_formulas", records)
    payload, _ = _execute(tmp_path, profile, objects)

    coverage = payload["coverage"]
    assert coverage["selectedRows"] == 6
    assert coverage["validCompositionSamples"] == 4
    assert coverage["invalidCompositionSamples"] == 2
    assert coverage["silentDrops"] is False
    assert coverage["invalidExamplesTruncated"] is False
    assert {(item["objectId"], item["rowIndex"]) for item in coverage["invalidExamples"]} == {
        ("obj_compositions", 4),
        ("obj_compositions", 5),
    }


def test_profile_formula_binding_and_profiled_resource_membership_are_required(tmp_path: Path) -> None:
    missing_formula, missing_formula_objects = _single_table_profile(
        "missing_formula_semantics",
        [
            {"material_id": "m1", "formula_text": "Si"},
            {"material_id": "m2", "formula_text": "NaCl"},
            {"material_id": "m3", "formula_text": "LiF"},
        ],
    )
    with pytest.raises(ToolExecutionError) as missing:
        _execute(tmp_path / "missing", missing_formula, missing_formula_objects)
    assert missing.value.details["errorType"] == "missing_formula_semantics"

    profile, objects = _single_table_profile("profile_membership", _representative_records())
    unprofiled = _table_object(
        profile.datasetId,
        "obj_unprofiled",
        _representative_records(),
    )
    with pytest.raises(ToolExecutionError) as unknown:
        _execute(
            tmp_path / "unprofiled",
            profile,
            [*objects, unprofiled],
            table_object_ids=["obj_unprofiled"],
            params={"tableObjectId": "obj_unprofiled"},
        )
    assert unknown.value.details == {
        "errorType": "object_not_profiled",
        "objectIds": ["obj_unprofiled"],
    }


def test_explicit_and_fallback_sample_identity_are_stable(tmp_path: Path) -> None:
    explicit_profile, explicit_objects = _single_table_profile("explicit_identity", _representative_records())
    explicit, _ = _execute(tmp_path / "explicit", explicit_profile, explicit_objects)
    assert [point["sampleRef"] for point in explicit["points"]] == [f"m{index}" for index in range(1, 7)]
    assert {point["identitySource"] for point in explicit["points"]} == {"explicit_column"}

    fallback_profile, fallback_objects = _single_table_profile(
        "fallback_identity",
        _representative_records(with_ids=False),
    )
    first, _ = _execute(tmp_path / "fallback_first", fallback_profile, fallback_objects)
    second, _ = _execute(tmp_path / "fallback_second", fallback_profile, fallback_objects)
    assert [point["sampleRef"] for point in first["points"]] == [
        point["sampleRef"] for point in second["points"]
    ]
    assert len({point["sampleRef"] for point in first["points"]}) == 6
    assert {point["identitySource"] for point in first["points"]} == {
        "dataset_version_object_hash_row_index"
    }


def test_group_and_resource_comparison_use_explicit_shared_projection(tmp_path: Path) -> None:
    group_records = _representative_records()
    for index, row in enumerate(group_records):
        row["split"] = "train" if index < 3 else "test"
    group_profile, group_objects = _single_table_profile("group_comparison", group_records)
    grouped, _ = _execute(
        tmp_path / "group",
        group_profile,
        group_objects,
        params={
            "comparisonMode": "group",
            "groupColumn": "split",
            "groupA": "train",
            "groupB": "test",
        },
    )
    assert grouped["comparison"] == {
        "status": "READY",
        "mode": "group",
        "groups": [
            {
                "group": "test",
                "sampleCount": 3,
                "featureCentroid": grouped["comparison"]["groups"][0]["featureCentroid"],
            },
            {
                "group": "train",
                "sampleCount": 3,
                "featureCentroid": grouped["comparison"]["groups"][1]["featureCentroid"],
            },
        ],
        "projectionPolicy": "exploratory_combined_projection",
        "sharedElementBasis": True,
        "sharedPcaFit": True,
        "trainingSafetyClaimed": False,
    }
    assert {point["group"] for point in grouped["points"]} == {"train", "test"}

    profile, objects = _profile_and_objects(
        "resource_comparison",
        [
            (
                "obj_train",
                [
                    {"material_id": "t1", "formula": "LiF"},
                    {"material_id": "t2", "formula": "Li2F"},
                    {"material_id": "t3", "formula": "SiO2"},
                ],
                None,
            ),
            (
                "obj_test",
                [
                    {"material_id": "h1", "formula": "NaCl"},
                    {"material_id": "h2", "formula": "Na2Cl"},
                    {"material_id": "h3", "formula": "GaAs"},
                ],
                None,
            ),
        ],
    )
    resources, _ = _execute(
        tmp_path / "resources",
        profile,
        objects,
        table_object_ids=["obj_train", "obj_test"],
        params={
            "comparisonMode": "resources",
            "leftObjectId": "obj_train",
            "rightObjectId": "obj_test",
        },
    )
    assert resources["comparison"]["mode"] == "resources"
    assert [item["group"] for item in resources["comparison"]["groups"]] == ["obj_test", "obj_train"]
    assert all(point["group"] in {"obj_train", "obj_test"} for point in resources["points"])


def test_property_and_explicit_k3_ml_coloring_preserve_backend_values(tmp_path: Path) -> None:
    records = _representative_records()
    records[0]["y_true"] = 0.0
    records[0]["y_pred"] = 1.0
    profile, objects = _single_table_profile(
        "coloring",
        records,
        units={"band_gap": "eV"},
    )
    resource_bindings = [
        {"objectId": item.objectId, "objectHash": item.objectHash, "objectType": item.objectType}
        for item in sorted(profile.resourceSemantics, key=lambda item: item.objectId)
    ]
    ml_artifact = {
        "schemaVersion": "phase10k3.materials_ml_regression.v1",
        "artifactType": "ml.regression_evaluation",
        "dataset": {
            "datasetId": profile.datasetId,
            "datasetVersion": profile.version,
            "profileId": profile.profileId,
            "profileContractVersion": profile.profileContractVersion,
            "semanticHash": profile.semanticHash,
            "datasetContentHash": content_hash(resource_bindings),
            "resourceBindings": resource_bindings,
        },
        "security": {
            "artifactJavaScript": False,
            "externalUrls": False,
            "externalAssets": False,
            "executableContent": False,
        },
        "evaluations": [
            {
                "taskId": "regression:default",
                "unit": "eV",
                "highErrorSamples": [
                    {
                        "objectId": "obj_compositions",
                        "sampleRef": "m1",
                        "sampleKey": "obj_compositions:m1",
                        "rowIndex": 0,
                        "absoluteError": 99.0,
                        "residual": -12.5,
                    }
                ],
            }
        ],
    }
    payload, _ = _execute(
        tmp_path,
        profile,
        objects,
        ml_artifact=ml_artifact,
        params={"colorBy": "ml:regression:default:absolute_error"},
    )

    options = {item["id"]: item for item in payload["coloring"]["available"]}
    assert options["property:band_gap"] == {
        "id": "property:band_gap",
        "kind": "continuous",
        "label": "band_gap",
        "unit": "eV",
        "source": "material_data_profile_2_material_property",
    }
    assert options["ml:regression:default:absolute_error"]["source"] == "phase10k3_sample_bound_artifact"
    assert options["ml:regression:default:absolute_error"]["unit"] == "eV"
    assert options["ml:regression:default:absolute_error"]["coverage"] == {
        "totalSamples": 6,
        "matchedSamples": 1,
        "missingSamples": 5,
    }
    point = next(item for item in payload["points"] if item["sampleRef"] == "m1")
    assert point["propertyValues"]["band_gap"] == 0.0
    assert point["mlValues"] == {
        "regression:default:absolute_error": 99.0,
        "regression:default:residual": -12.5,
    }
    assert point["mlValues"]["regression:default:absolute_error"] != abs(
        float(records[0]["y_pred"]) - float(records[0]["y_true"])
    )
    assert payload["upstreamMlBindings"][0]["schemaVersion"] == (
        "phase10k3.materials_ml_regression.v1"
    )
    assert payload["upstreamMlBindings"][0]["contentHash"]


def test_k3_ml_binding_rejects_stale_foreign_and_unknown_artifacts(tmp_path: Path) -> None:
    profile, objects = _single_table_profile("binding", _representative_records())
    resource_bindings = [
        {"objectId": item.objectId, "objectHash": item.objectHash, "objectType": item.objectType}
        for item in sorted(profile.resourceSemantics, key=lambda item: item.objectId)
    ]
    base_artifact = {
        "schemaVersion": "phase10k3.materials_ml_regression.v1",
        "artifactType": "ml.regression_evaluation",
        "dataset": {
            "datasetId": profile.datasetId,
            "datasetVersion": profile.version,
            "profileId": profile.profileId,
            "profileContractVersion": profile.profileContractVersion,
            "semanticHash": profile.semanticHash,
            "datasetContentHash": content_hash(resource_bindings),
            "resourceBindings": resource_bindings,
        },
        "security": {
            "artifactJavaScript": False,
            "externalUrls": False,
            "externalAssets": False,
            "executableContent": False,
        },
        "evaluations": [],
    }

    for field, stale_value in (
        ("datasetId", "foreign_dataset"),
        ("datasetVersion", "stale_version"),
        ("profileId", "stale_profile"),
        ("profileContractVersion", "1.0"),
        ("semanticHash", "stale_semantics"),
        ("datasetContentHash", "stale_content"),
        ("resourceBindings", []),
    ):
        stale = json.loads(json.dumps(base_artifact))
        stale["dataset"][field] = stale_value
        with pytest.raises(ToolExecutionError) as mismatch:
            _execute(tmp_path / field, profile, objects, ml_artifact=stale)
        assert mismatch.value.details == {
            "errorType": "ml_artifact_binding_mismatch",
            "fields": [field],
        }

    missing = json.loads(json.dumps(base_artifact))
    del missing["dataset"]
    with pytest.raises(ToolExecutionError) as missing_binding:
        _execute(tmp_path / "missing", profile, objects, ml_artifact=missing)
    assert missing_binding.value.details["errorType"] == "ml_artifact_binding_missing"

    unknown = json.loads(json.dumps(base_artifact))
    unknown["schemaVersion"] = "phase10k3.materials_ml_regression.v2"
    with pytest.raises(ToolExecutionError) as unsupported:
        _execute(tmp_path / "unknown", profile, objects, ml_artifact=unknown)
    assert unsupported.value.details["errorType"] == "unsupported_input"

    inconsistent_identity = json.loads(json.dumps(base_artifact))
    inconsistent_identity["evaluations"] = [
        {
            "taskId": "regression:default",
            "highErrorSamples": [
                {
                    "objectId": "obj_compositions",
                    "sampleRef": "m1",
                    "sampleKey": "obj_compositions:another_sample",
                    "rowIndex": 0,
                    "absoluteError": 1.0,
                }
            ],
        }
    ]
    with pytest.raises(ToolExecutionError) as sample_identity:
        _execute(
            tmp_path / "sample_identity",
            profile,
            objects,
            ml_artifact=inconsistent_identity,
        )
    assert sample_identity.value.details["errorType"] == (
        "ml_artifact_sample_identity_mismatch"
    )


def test_caps_secret_params_and_unavailable_color_sources_are_typed(tmp_path: Path) -> None:
    profile, objects = _single_table_profile("security", _representative_records())

    with pytest.raises(ToolExecutionError) as row_cap:
        _execute(
            tmp_path / "row_cap",
            profile,
            objects,
            resource_limits={"maxRows": 5},
        )
    assert row_cap.value.code == "TOOL_RESOURCE_LIMIT"
    assert row_cap.value.details == {"rows": 6, "maxRows": 5}

    with pytest.raises(ToolExecutionError) as analyzed_cap:
        _execute(
            tmp_path / "analysis_cap",
            profile,
            objects,
            resource_limits={"maxAnalyzedSamples": 5},
        )
    assert analyzed_cap.value.code == "TOOL_RESOURCE_LIMIT"
    assert analyzed_cap.value.details["validSamples"] == 6

    with pytest.raises(ToolExecutionError) as element_cap:
        _execute(
            tmp_path / "element_cap",
            profile,
            objects,
            resource_limits={"maxElements": 4},
        )
    assert element_cap.value.code == "TOOL_RESOURCE_LIMIT"
    assert element_cap.value.details == {"elementCount": 9, "maxElements": 4}

    with pytest.raises(ToolExecutionError) as cluster_cap:
        _execute(
            tmp_path / "cluster_cap",
            profile,
            objects,
            params={"clusteringEnabled": True, "nClusters": 7},
        )
    assert cluster_cap.value.details["errorType"] == "invalid_cluster_count"

    with pytest.raises(ToolExecutionError) as missing_ml:
        _execute(
            tmp_path / "missing_ml",
            profile,
            objects,
            params={"colorBy": "ml:regression:default:absolute_error"},
        )
    assert missing_ml.value.details["errorType"] in {"color_source_unavailable", "missing_ml_artifact"}

    with pytest.raises(ToolExecutionError) as secret:
        _execute(
            tmp_path / "secret",
            profile,
            objects,
            params={"apiKey": "do-not-record"},
        )
    assert secret.value.code == "TOOL_PARAM_INVALID"
    assert secret.value.details == {"param": "apiKey"}

    malicious_ml = {
        "schemaVersion": "phase10k3.materials_ml_regression.v1",
        "security": {
            "artifactJavaScript": False,
            "externalUrls": True,
            "externalAssets": False,
            "executableContent": False,
        },
        "evaluations": [],
    }
    with pytest.raises(ToolExecutionError) as artifact_security:
        _execute(
            tmp_path / "malicious_artifact",
            profile,
            objects,
            ml_artifact=malicious_ml,
        )
    assert artifact_security.value.details["errorType"] == "unsupported_input"


def test_group_comparison_enforces_raw_row_cap_before_filtering(tmp_path: Path) -> None:
    records = _representative_records()
    for row, split in zip(records, ["train", "test", "test", "test", "other", "other"], strict=True):
        row["split"] = split
    profile, objects = _single_table_profile("group_row_cap", records)

    with pytest.raises(ToolExecutionError) as row_cap:
        _execute(
            tmp_path,
            profile,
            objects,
            params={
                "comparisonMode": "group",
                "groupColumn": "split",
                "groupA": "train",
                "groupB": "test",
            },
            resource_limits={"maxRows": 5},
        )

    assert row_cap.value.code == "TOOL_RESOURCE_LIMIT"
    assert row_cap.value.details == {"rows": 6, "maxRows": 5}


def test_planner_route_and_plan_validator_enforce_explicit_profile_binding(tmp_path: Path) -> None:
    profile, objects = _single_table_profile("planner", _representative_records())
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt="Show the composition space and cluster compositions.",
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
    assert step["toolId"] == "dataset.composition_space"
    assert step["inputRefs"] == [
        {"refType": "profile", "ref": "profile"},
        {
            "refType": "normalized_object",
            "ref": objects[0].id,
            "objectType": "DataFrame",
            "fieldRole": "composition_samples",
        },
    ]
    assert step["params"] == {
        "tableObjectId": objects[0].id,
        "comparisonMode": "none",
        "projectionDimensions": 2,
        "clusteringEnabled": True,
        "nClusters": 3,
        "randomState": 0,
        "nInit": 10,
        "maxIterations": 300,
        "tolerance": 0.0001,
        "maxPlotPoints": 5000,
        "maxOutlierRows": 50,
    }
    assert validate_plan(plan, registry=registry).ok

    invalid = json.loads(json.dumps(plan))
    invalid["steps"][0]["params"]["remoteUrl"] = "https://invalid.example"
    validation = validate_plan(invalid, registry=registry)
    assert not validation.ok
    assert any(error.code == "PARAMS_SCHEMA_INVALID" for error in validation.errors)


def test_queue_runtime_emits_direct_product_artifact_names(tmp_path: Path) -> None:
    profile, objects = _single_table_profile("runtime", _representative_records())
    registry = load_manifests()
    raw_plan = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt="Build a composition PCA for this materials dataset.",
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            tool_registry_version=registry.version,
        ),
        tools=registry.list_mvp_tools(),
        data_profile=profile,
    ).raw_json
    assert raw_plan is not None
    repositories = InMemoryRepositoryBundle.create()
    runtime = QueueWorkerRuntime(
        repositories=repositories,
        registry=registry,
        artifact_root=tmp_path / "runtime",
    )
    created = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Build a composition PCA for this materials dataset.",
            projectId="project_10k4",
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
    assert [call["toolId"] for call in repositories.tool_calls.list_for_job(created.job_id or "")] == [
        "dataset.composition_space"
    ]
    artifacts = repositories.artifacts.list_for_job(created.job_id or "")
    assert {item["name"] for item in artifacts} == {
        "composition_space.json",
        "composition_space_plot.json",
        "summary.md",
        "recipe.json",
    }
