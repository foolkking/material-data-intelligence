from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from pymatgen.core import Lattice, Structure

from mdi_adapters import ToolExecutionContext, ToolExecutionError
from mdi_adapters.platform_builtin import DatasetMaterialsExplorerAdapter
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
    object_id: str,
    records: list[dict[str, object]],
    *,
    units: dict[str, str] | None = None,
) -> NormalizedObjectDraft:
    frame = pd.DataFrame(records)
    columns = []
    for name in frame.columns:
        series = frame[name]
        numeric = pd.api.types.is_numeric_dtype(series)
        values = pd.to_numeric(series, errors="coerce") if numeric else series
        columns.append(
            {
                "name": str(name),
                "dtype": "number" if numeric else "string",
                "missingCount": int(series.isna().sum()),
                "uniqueCount": int(series.nunique(dropna=True)),
                "unit": (units or {}).get(str(name)),
                "finiteCount": int(values.notna().sum()) if numeric else None,
            }
        )
    return NormalizedObjectDraft(
        id=object_id,
        dataset_id="dataset_10k2",
        object_type=MaterialObjectType.DataFrame,
        source_file_ids=[f"{object_id}.csv"],
        storage_key=f"normalized/{object_id}.json",
        metadata={"nRows": len(frame), "nColumns": len(frame.columns), "columns": columns},
        hash=(object_id.encode("utf-8").hex() + "0" * 64)[:64],
        payload=records,
    )


def _structure_object(object_id: str, structure: Structure, *, content_hash: str | None = None) -> NormalizedObjectDraft:
    return NormalizedObjectDraft(
        id=object_id,
        dataset_id="dataset_10k2",
        object_type=MaterialObjectType.Structure,
        source_file_ids=[f"{object_id}.cif"],
        storage_key=f"normalized/{object_id}.json",
        metadata={
            "formula": structure.composition.reduced_formula,
            "chemicalSystem": structure.composition.chemical_system,
            "elements": sorted(str(element) for element in structure.composition.elements),
            "nAtoms": len(structure),
            "periodicity": "periodic",
        },
        hash=content_hash or (object_id.encode("utf-8").hex() + "1" * 64)[:64],
        payload=structure.as_dict(),
    )


def _profile_and_objects(
    *,
    include_second_table: bool = False,
    holdout_band_gap_unit: str = "eV",
) -> tuple[DataProfile, list[NormalizedObjectDraft]]:
    primary = _table_object(
        "obj_materials",
        [
            {"material_id": "m1", "formula": "Si", "band_gap": 1.1, "density": 2.33, "split": "train"},
            {"material_id": "m2", "formula": "NaCl", "band_gap": 5.6, "density": 2.16, "split": "train"},
            {"material_id": "m3", "formula": "Si", "band_gap": 1.3, "density": None, "split": "test"},
            {"material_id": "m4", "formula": "not-a-formula", "band_gap": 20.0, "density": 2.5, "split": "test"},
        ],
        units={"band_gap": "eV", "density": "g/cm^3"},
    )
    si = Structure(Lattice.cubic(5.43), ["Si", "Si"], [[0, 0, 0], [0.25, 0.25, 0.25]])
    structure_a = _structure_object("obj_si_a", si, content_hash="a" * 64)
    structure_b = _structure_object("obj_si_b", si, content_hash="a" * 64)
    objects = [primary, structure_a, structure_b]
    if include_second_table:
        objects.append(
            _table_object(
                "obj_holdout",
                [
                    {"material_id": "h1", "formula": "LiF", "band_gap": 11.0, "density": 2.64},
                    {"material_id": "h2", "formula": "NaCl", "band_gap": 5.8, "density": 2.2},
                ],
                units={"band_gap": holdout_band_gap_unit, "density": "g/cm^3"},
            )
        )
    result = ParseResult(
        file_id="file_dataset",
        file_path=Path("dataset.json"),
        detected_format=DetectedFormat.json_limited,
        parse_status="success",
        objects=objects,
    )
    registry = load_manifests()
    profile = build_data_profile(
        dataset_id="dataset_10k2",
        parse_results=[result],
        platform_tool_ids={tool.toolId for tool in registry.tools},
    )
    return profile, objects


def _execute(
    tmp_path: Path,
    profile: DataProfile,
    objects: list[NormalizedObjectDraft],
    *,
    params: dict[str, object] | None = None,
) -> tuple[dict[str, object], list[object]]:
    registry = load_manifests()
    tool = registry.get_tool_by_id("dataset.materials_explorer")
    store, refs = build_object_store(objects, profile=profile)
    primary_id = str((params or {}).get("tableObjectId") or refs.get("dataset_table") or "")
    input_refs = [{"refType": "profile", "ref": "profile"}]
    if primary_id:
        input_refs.append({"refType": "normalized_object", "ref": primary_id, "objectType": "DataFrame"})
    if (params or {}).get("comparisonMode") == "resources":
        right_id = str((params or {})["rightObjectId"])
        if right_id != primary_id and right_id in store:
            input_refs.append({"refType": "normalized_object", "ref": right_id, "objectType": "DataFrame"})
    if "structure_resources" in store:
        input_refs.append({"refType": "normalized_object", "ref": "structure_resources", "objectType": "Structure"})
    context = ToolExecutionContext(
        job_id="job_10k2",
        project_id="project_10k2",
        dataset_id=profile.datasetId,
        tool_id=tool.toolId,
        tool_version=tool.version,
        adapter_version="0.1.0",
        registry_version=registry.version,
        artifact_root=tmp_path,
        tool_call_id="call_10k2",
        object_store=store,
        resource_limits=tool.resourceLimits,
    )
    request = ToolExecutionRequest(
        jobId="job_10k2",
        stepId="step_001",
        toolId=tool.toolId,
        inputRefs=input_refs,
        params={"comparisonMode": "none", "tableObjectId": primary_id, **(params or {})},
        artifactTypes=["table_json", "quality_issues_json", "summary_md", "recipe_json"],
    )
    artifacts = DatasetMaterialsExplorerAdapter().execute(context, request)
    primary = next(item for item in artifacts if item.name == "dataset_materials_explorer.json")
    payload = json.loads((tmp_path / primary.storageKey).read_text(encoding="utf-8"))
    return payload, artifacts


def test_registry_contract_is_product_level_strict_and_bounded() -> None:
    registry = load_manifests()
    tool = registry.get_tool_by_id("dataset.materials_explorer")
    assert tool.domain.value == "dataset"
    assert tool.adapter == "DatasetMaterialsExplorerAdapter"
    assert tool.outputSchema.displayTarget.value == "overview"
    assert tool.paramsSchema["additionalProperties"] is False
    assert set(tool.paramsSchema["properties"]) >= {
        "comparisonMode",
        "groupColumn",
        "leftObjectId",
        "rightObjectId",
        "maxProperties",
        "maxTableRows",
    }
    assert tool.resourceLimits == {
        "maxRows": 100000,
        "maxColumns": 512,
        "maxProperties": 64,
        "maxCategories": 256,
        "maxTableRows": 200,
        "maxHistogramBins": 100,
        "maxStructures": 256,
        "maxAtomsPerStructure": 5000,
        "maxWarnings": 128,
        "maxArtifactBytes": 8000000,
    }


def test_materials_explorer_builds_coherent_profile_bound_product(tmp_path: Path) -> None:
    profile, objects = _profile_and_objects()
    payload, artifacts = _execute(tmp_path, profile, objects, params={"tableObjectId": "obj_materials"})

    assert payload["schemaVersion"] == "phase10k2.dataset_materials_explorer.v1"
    assert payload["dataset"]["semanticHash"] == profile.semanticHash
    assert len(payload["dataset"]["datasetContentHash"]) == 64
    assert {item["objectId"] for item in payload["dataset"]["resourceBindings"]} == {
        "obj_materials",
        "obj_si_a",
        "obj_si_b",
    }
    assert payload["semantics"]["roleInferenceRepeated"] is False
    assert payload["overview"] == {
        "sampleCount": 4,
        "tableCount": 1,
        "structureCount": 2,
        "formulaCoverage": {"total": 4, "nonNull": 4, "valid": 3, "invalid": 1},
        "propertyCount": 2,
        "availableAnalyses": payload["overview"]["availableAnalyses"],
        "unavailableAnalyses": payload["overview"]["unavailableAnalyses"],
    }
    elements = {item["element"]: item for item in payload["composition"]["elements"]}
    assert elements["Si"]["materialsContainingElement"] == 2
    assert elements["Na"]["materialsContainingElement"] == 1
    assert payload["composition"]["duplicateReducedFormulaGroups"][0]["reducedFormula"] == "Si"
    assert payload["structures"]["structureCount"] == 2
    assert payload["structures"]["exactStructureDuplicateGroups"][0]["objectIds"] == ["obj_si_a", "obj_si_b"]
    assert {item["column"] for item in payload["properties"]["properties"]} == {"band_gap", "density"}
    assert next(item for item in payload["properties"]["properties"] if item["column"] == "band_gap")["unit"] == "eV"
    assert payload["quality"]["invalidFormulaCount"] == 1
    assert payload["quality"]["nearDuplicateAnalysis"] == "NOT_IMPLEMENTED_BY_DESIGN"
    assert [item["sampleRef"] for item in payload["sampleIndex"]] == ["m1", "m2", "m3", "m4"]
    assert [item["sampleKey"] for item in payload["sampleIndex"]] == [
        "obj_materials:m1",
        "obj_materials:m2",
        "obj_materials:m3",
        "obj_materials:m4",
    ]
    assert {item.name for item in artifacts} == {
        "dataset_materials_explorer.json",
        "dataset_quality.json",
        "summary.md",
        "recipe.json",
    }


def test_group_comparison_is_explicit_and_never_uses_row_order(tmp_path: Path) -> None:
    profile, objects = _profile_and_objects()
    payload, _ = _execute(
        tmp_path,
        profile,
        objects,
        params={
            "tableObjectId": "obj_materials",
            "comparisonMode": "group",
            "groupColumn": "split",
            "groupA": "train",
            "groupB": "test",
        },
    )
    comparison = payload["comparison"]
    assert comparison["status"] == "READY"
    assert comparison["binding"] == {"groupColumn": "split", "groupA": "train", "groupB": "test"}
    assert comparison["sampleCounts"] == {"train": 2, "test": 2}
    assert comparison["semantics"] == "explicitly bound groups/resources; no row-order inference"

    with pytest.raises(ToolExecutionError) as exc_info:
        _execute(
            tmp_path / "invalid",
            profile,
            objects,
            params={"comparisonMode": "group", "groupColumn": "split", "groupA": "train", "groupB": "train"},
        )
    assert exc_info.value.details["errorType"] == "comparison_groups_invalid"


def test_resource_comparison_uses_two_profiled_tables(tmp_path: Path) -> None:
    profile, objects = _profile_and_objects(include_second_table=True)
    payload, _ = _execute(
        tmp_path,
        profile,
        objects,
        params={
            "tableObjectId": "obj_materials",
            "comparisonMode": "resources",
            "leftObjectId": "obj_materials",
            "rightObjectId": "obj_holdout",
        },
    )
    comparison = payload["comparison"]
    assert comparison["mode"] == "resources"
    assert comparison["sampleCounts"] == {"obj_materials": 4, "obj_holdout": 2}
    assert comparison["elementOverlap"]["shared"] == ["Cl", "Na"]
    assert comparison["elementOverlap"]["rightOnly"] == ["F", "Li"]
    assert all(item["comparable"] for item in comparison["propertyComparison"])


def test_partial_empty_and_formula_only_datasets_have_typed_states(tmp_path: Path) -> None:
    registry = load_manifests()
    for case_id, records in (
        ("empty", []),
        ("formula_only", [{"material_id": "m1", "formula": "Si"}, {"material_id": "m2", "formula": "bad formula"}]),
    ):
        objects = [_table_object(f"obj_{case_id}", records)]
        profile = build_data_profile(
            dataset_id="dataset_10k2",
            parse_results=[
                ParseResult(
                    file_id=f"file_{case_id}",
                    file_path=Path(f"{case_id}.json"),
                    detected_format=DetectedFormat.json_limited,
                    parse_status="success",
                    objects=objects,
                )
            ],
            platform_tool_ids={tool.toolId for tool in registry.tools},
        )
        payload, _ = _execute(
            tmp_path / case_id,
            profile,
            objects,
            params={"tableObjectId": f"obj_{case_id}"},
        )
        assert payload["structures"]["status"] == "UNAVAILABLE"
        assert payload["properties"]["status"] == "UNAVAILABLE"
        assert payload["comparison"] == {"status": "NOT_REQUESTED", "mode": "none"}
    assert payload["composition"]["coverage"] == {"total": 2, "nonNull": 2, "valid": 1, "invalid": 1}


def test_nonfinite_values_duplicates_and_category_truncation_are_explicit(tmp_path: Path) -> None:
    records = [
        {"material_id": "duplicate", "formula": "LiF", "band_gap": 10.0},
        {"material_id": "duplicate", "formula": "NaCl", "band_gap": float("inf")},
        {"material_id": "third", "formula": "MgO", "band_gap": None},
    ]
    objects = [_table_object("obj_quality", records, units={"band_gap": "eV"})]
    registry = load_manifests()
    profile = build_data_profile(
        dataset_id="dataset_10k2",
        parse_results=[
            ParseResult(
                file_id="file_quality",
                file_path=Path("quality.json"),
                detected_format=DetectedFormat.json_limited,
                parse_status="success",
                objects=objects,
            )
        ],
        platform_tool_ids={tool.toolId for tool in registry.tools},
    )
    payload, _ = _execute(
        tmp_path,
        profile,
        objects,
        params={"tableObjectId": "obj_quality", "maxCategories": 2},
    )
    assert payload["quality"]["duplicateSampleIdentityValues"] == [
        {"column": "material_id", "value": "duplicate", "count": 2}
    ]
    prop = next(item for item in payload["properties"]["properties"] if item["column"] == "band_gap")
    assert prop["count"] == 1
    assert prop["missingCount"] == 1
    assert prop["nonFiniteCount"] == 1
    assert len(payload["composition"]["chemicalSystems"]) == 2
    assert "DATASET_COMPOSITION_CATEGORY_CAP_APPLIED" in payload["warnings"]


def test_invalid_comparison_bindings_and_mixed_units_are_typed(tmp_path: Path) -> None:
    profile, objects = _profile_and_objects(include_second_table=True, holdout_band_gap_unit="meV")
    payload, _ = _execute(
        tmp_path / "mixed_units",
        profile,
        objects,
        params={
            "tableObjectId": "obj_materials",
            "comparisonMode": "resources",
            "leftObjectId": "obj_materials",
            "rightObjectId": "obj_holdout",
        },
    )
    band_gap = next(item for item in payload["comparison"]["propertyComparison"] if item["column"] == "band_gap")
    assert band_gap["comparable"] is False
    assert band_gap["unit"] is None
    assert "DATASET_COMPARISON_UNIT_MISMATCH:band_gap" in payload["warnings"]

    with pytest.raises(ToolExecutionError) as missing_resource:
        _execute(
            tmp_path / "missing_resource",
            profile,
            objects,
            params={
                "tableObjectId": "obj_materials",
                "comparisonMode": "resources",
                "leftObjectId": "obj_materials",
                "rightObjectId": "obj_missing",
            },
        )
    assert missing_resource.value.code == "TOOL_INPUT_INVALID"
    assert missing_resource.value.details["errorType"] == "comparison_resources_invalid"

    with pytest.raises(ToolExecutionError) as empty_group:
        _execute(
            tmp_path / "empty_group",
            profile,
            objects,
            params={
                "tableObjectId": "obj_materials",
                "comparisonMode": "group",
                "groupColumn": "split",
                "groupA": "train",
                "groupB": "validation",
            },
        )
    assert empty_group.value.details["errorType"] == "comparison_group_empty"


def test_fallback_sample_identity_and_resource_caps_are_deterministic(tmp_path: Path) -> None:
    profile, objects = _profile_and_objects()
    profile.sampleIdentity.policy = "object_hash_row_index"
    profile.sampleIdentity.explicitColumn = None
    first, _ = _execute(tmp_path / "first", profile, objects)
    second, _ = _execute(tmp_path / "second", profile, objects)
    assert first["sampleIndex"] == second["sampleIndex"]
    assert first["sampleIndex"][0]["sampleRef"].startswith("dataset_10k2@2:")
    assert first["sampleIndex"][0]["sampleKey"] == (
        f"obj_materials:{first['sampleIndex'][0]['sampleRef']}"
    )

    tool = load_manifests().get_tool_by_id("dataset.materials_explorer")
    store, _ = build_object_store(objects, profile=profile)
    context = ToolExecutionContext(
        job_id="job_cap",
        project_id="project_10k2",
        dataset_id=profile.datasetId,
        tool_id=tool.toolId,
        tool_version=tool.version,
        adapter_version="0.1.0",
        registry_version="0.1.0",
        artifact_root=tmp_path / "cap",
        object_store=store,
        resource_limits={**tool.resourceLimits, "maxRows": 2},
    )
    with pytest.raises(ToolExecutionError) as exc_info:
        DatasetMaterialsExplorerAdapter().execute(
            context,
            ToolExecutionRequest(
                jobId="job_cap",
                stepId="step_cap",
                toolId=tool.toolId,
                inputRefs=[
                    {"refType": "profile", "ref": "profile"},
                    {"refType": "normalized_object", "ref": "obj_materials", "objectType": "DataFrame"},
                ],
                params={"comparisonMode": "none", "tableObjectId": "obj_materials"},
                artifactTypes=["table_json"],
            ),
        )
    assert exc_info.value.code == "TOOL_RESOURCE_LIMIT"
    assert exc_info.value.details["maxRows"] == 2


def test_planner_and_plan_validator_use_current_profile_object_ids() -> None:
    profile, _ = _profile_and_objects()
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt="Explore this materials dataset composition and properties.",
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            tool_registry_version=registry.version,
        ),
        tools=registry.list_mvp_tools(),
        data_profile=profile,
    )
    plan = response.raw_json
    assert plan is not None
    assert plan["steps"][0]["toolId"] == "dataset.materials_explorer"
    assert plan["steps"][0]["inputRefs"][:2] == [
        {"refType": "profile", "ref": "profile"},
        {"refType": "normalized_object", "ref": "obj_materials", "objectType": "DataFrame", "fieldRole": "primary_table"},
    ]
    assert validate_plan(plan, registry=registry).ok

    invalid = json.loads(json.dumps(plan))
    invalid["steps"][0]["params"]["remoteUrl"] = "https://invalid.example"
    validation = validate_plan(invalid, registry=registry)
    assert not validation.ok
    assert any(error.code == "PARAMS_SCHEMA_INVALID" for error in validation.errors)


def test_persisted_plan_executes_one_dataset_product_through_queue_runtime(tmp_path: Path) -> None:
    profile, objects = _profile_and_objects()
    registry = load_manifests()
    raw_plan = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt="Analyze this batch of materials with the dataset materials explorer.",
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
            userPrompt="Analyze this batch of materials with the dataset materials explorer.",
            projectId="project_10k2",
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
    assert [call["toolId"] for call in calls] == ["dataset.materials_explorer"]
    assert {item["name"] for item in artifacts} >= {
        "dataset_materials_explorer.json",
        "dataset_quality.json",
        "summary.md",
        "recipe.json",
    }


def test_outputs_are_inert_and_do_not_embed_executable_or_remote_content(tmp_path: Path) -> None:
    profile, objects = _profile_and_objects()
    _, artifacts = _execute(tmp_path, profile, objects)
    combined = "\n".join(
        (tmp_path / item.storageKey).read_text(encoding="utf-8")
        for item in artifacts
        if item.type != ArtifactType.preview_png
    ).lower()
    for marker in ("<script", "javascript:", "https://", "http://", "<iframe", "eval(", "function("):
        assert marker not in combined
