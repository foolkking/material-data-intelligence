from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mdi_adapters import ToolExecutionContext, VolumetricDataAdapter
from mdi_adapters.errors import ToolExecutionError
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import (
    decode_volumetric_payload,
    validate_volumetric_dataset,
    validate_volumetric_grid,
    validate_volumetric_manifest,
)
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import VolumetricParseError, detect_volumetric_format, parse_file, parse_volumetric_file
from mdi_schemas import DataProfile, MaterialObjectType, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10j" / "fixtures" / "volumetric_parser"
ARTIFACT_TYPES = [
    "volumetric_grid_json", "volumetric_payload_json", "volumetric_field_json",
    "volumetric_dataset_json", "volumetric_manifest_json", "volumetric_binary", "summary_md", "recipe_json",
]


def test_bounded_detection_and_format_mismatch(tmp_path: Path) -> None:
    assert detect_volumetric_format(FIXTURES / "CHGCAR") == "vasp_volumetric"
    assert detect_volumetric_format(FIXTURES / "orthogonal.cube") == "gaussian_cube"
    misleading = tmp_path / "CHGCAR"
    misleading.write_text("not volumetric\n", encoding="utf-8")
    with pytest.raises(VolumetricParseError) as error:
        detect_volumetric_format(misleading)
    assert error.value.code == "VOLUME_FORMAT_AMBIGUOUS"
    with pytest.raises(VolumetricParseError) as error:
        parse_volumetric_file(FIXTURES / "CHGCAR", source_format="gaussian_cube")
    assert error.value.code == "VOLUME_FORMAT_MISMATCH"


def test_vasp_source_order_normalization_and_electron_integral() -> None:
    parsed = parse_volumetric_file(FIXTURES / "CHGCAR")
    source = parsed.source
    assert source["shape"] == [2, 2, 2]
    assert source["endpoint_policy"] == "excluded"
    assert source["boundary_conditions"] == ["periodic"] * 3
    assert source["channels"][0]["values"] == [1.0, 5.0, 3.0, 7.0, 2.0, 6.0, 4.0, 8.0]
    voxel_volume = 1.0
    assert sum(source["channels"][0]["values"]) * voxel_volume == pytest.approx(36.0)
    assert parsed.report["source_order"] == "x_fastest_then_y_then_z"


@pytest.mark.parametrize(
    ("name", "quantity", "unit"),
    (("LOCPOT", "local_potential", "electronvolt"), ("ELFCAR", "electron_localization_function", "dimensionless"), ("PARCHG", "orbital_density", "electron/angstrom^3")),
)
def test_vasp_family_quantity_mapping(name: str, quantity: str, unit: str) -> None:
    channel = parse_volumetric_file(FIXTURES / name).source["channels"][0]
    assert channel["quantity"] == quantity
    assert channel["canonical_unit"] == unit


def test_collinear_and_noncollinear_channel_semantics() -> None:
    collinear = parse_volumetric_file(FIXTURES / "CHGCAR.collinear").source
    assert [item["spin_channel"] for item in collinear["channels"]] == ["total", "spin_difference"]
    noncollinear = parse_volumetric_file(FIXTURES / "CHGCAR.noncollinear").source
    assert [item["spin_channel"] for item in noncollinear["channels"]] == ["total", "magnetization_x", "magnetization_y", "magnetization_z"]
    augmentation = parse_volumetric_file(FIXTURES / "CHGCAR.augmentation")
    assert augmentation.source["warnings"] == ["VOLUME_VASP_AUGMENTATION_NOT_INCLUDED"]
    assert augmentation.report["augmentation_section_present"] is True


def test_cube_units_affine_steps_order_and_multi_orbital_rejection() -> None:
    cube = parse_volumetric_file(FIXTURES / "orthogonal.cube", quantity_hint="electron_density")
    assert cube.source["shape"] == [2, 2, 2]
    assert cube.source["boundary_conditions"] == ["non_periodic"] * 3
    assert cube.source["step_matrix"][0][0] == pytest.approx(0.529177210903)
    assert cube.source["channels"][0]["conversion_factor"] == pytest.approx(6.748334494600374)
    assert cube.source["channels"][0]["values"][7] == pytest.approx(47.23834146220262)
    affine = parse_volumetric_file(FIXTURES / "triclinic.cube").source
    assert affine["origin_cartesian"] == [0.1, 0.2, 0.3]
    assert affine["step_matrix"][1] == [0.2, 1.0, 0.0]
    with pytest.raises(VolumetricParseError) as error:
        parse_volumetric_file(FIXTURES / "multi_orbital.cube")
    assert error.value.code == "VOLUME_CUBE_MULTI_ORBITAL_UNSUPPORTED"


def test_malformed_numeric_caps_and_cancellation(tmp_path: Path) -> None:
    malformed = tmp_path / "CHGCAR"
    malformed.write_text((FIXTURES / "CHGCAR").read_text(encoding="utf-8").replace("64", "nan"), encoding="utf-8")
    with pytest.raises(VolumetricParseError) as error:
        parse_volumetric_file(malformed)
    assert error.value.code == "VOLUME_NUMERIC_NONFINITE"
    over = tmp_path / "over.cube"
    over.write_text("a\nb\n0 0 0 0\n513 1 0 0\n1 0 1 0\n1 0 0 1\n0\n", encoding="utf-8")
    with pytest.raises(VolumetricParseError) as error:
        parse_volumetric_file(over)
    assert error.value.code == "VOLUME_GRID_CAP_EXCEEDED"
    with pytest.raises(VolumetricParseError) as error:
        parse_volumetric_file(FIXTURES / "CHGCAR", cancel_check=lambda: True)
    assert error.value.code == "VOLUME_PARSE_CANCELLED"


def _context(root: Path, source: object) -> ToolExecutionContext:
    tool = load_manifests().get_tool_by_id("structure.volumetric_data")
    return ToolExecutionContext(
        job_id="job_volume", project_id="project_volume", dataset_id="dataset_volume",
        tool_id=tool.toolId, tool_version=tool.version, adapter_version="1.0.0",
        registry_version=load_manifests().version, artifact_root=root, tool_call_id="call_volume",
        object_store={"volumetric": source}, resource_limits=tool.resourceLimits,
    )


def _request(params: dict | None = None) -> ToolExecutionRequest:
    return ToolExecutionRequest(
        jobId="job_volume", stepId="step_001", toolId="structure.volumetric_data",
        inputRefs=[{"refType": "normalized_object", "ref": "volumetric", "objectType": "VolumetricData"}],
        params=params or {}, artifactTypes=ARTIFACT_TYPES,
    )


def _read(root: Path, artifacts: list, name: str) -> dict:
    item = next(artifact for artifact in artifacts if artifact.name == name)
    return json.loads((root / item.storageKey).read_text(encoding="utf-8"))


def test_parse_file_and_adapter_emit_valid_deterministic_binary_package(tmp_path: Path) -> None:
    normalized = parse_file(FIXTURES / "CHGCAR.collinear", dataset_id="dataset", file_id="file")
    assert normalized.parse_status == "success"
    assert normalized.objects[0].object_type == MaterialObjectType.VolumetricData
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first = VolumetricDataAdapter().execute(_context(first_root, normalized.objects[0]), _request())
    second = VolumetricDataAdapter().execute(_context(second_root, normalized.objects[0]), _request())
    assert len({item.id for item in first}) == len(first)
    assert [(item.name, item.contentHash) for item in first] == [(item.name, item.contentHash) for item in second]
    dataset = _read(first_root, first, "volumetric_dataset.json")
    manifest = _read(first_root, first, "volumetric_manifest.json")
    binaries = {item.name: (first_root / item.storageKey).read_bytes() for item in first if item.type.value == "volumetric_binary"}
    assert validate_volumetric_grid(dataset["grid"]).valid
    assert validate_volumetric_dataset(dataset, binaries).valid
    assert validate_volumetric_manifest(manifest, dataset=dataset, artifacts=binaries).valid
    assert len(dataset["fields"]) == 2
    for payload in dataset["payloads"]:
        assert len(decode_volumetric_payload(payload, binaries)) == 8
    assert all(item.metadata.provenance["rendererIncluded"] is False for item in first)


def test_adapter_vectorizes_noncollinear_and_rejects_unsafe_params(tmp_path: Path) -> None:
    source = parse_file(FIXTURES / "CHGCAR.noncollinear", dataset_id="dataset").objects[0]
    artifacts = VolumetricDataAdapter().execute(_context(tmp_path, source), _request())
    dataset = _read(tmp_path, artifacts, "volumetric_dataset.json")
    assert sorted((field["field_name"], field["stored_component_count"]) for field in dataset["fields"]) == [("magnetization_vector", 3), ("total", 1)]
    with pytest.raises(ToolExecutionError) as error:
        VolumetricDataAdapter().execute(_context(tmp_path / "bad", source), _request({"parser": "module.path"}))
    assert error.value.code == "TOOL_PARAM_INVALID"
    malicious = copy.deepcopy(source.payload)
    malicious["source_format"] = "https://example.invalid/parser"
    with pytest.raises(ToolExecutionError):
        VolumetricDataAdapter().execute(_context(tmp_path / "malicious", malicious), _request())
    cube = parse_file(FIXTURES / "orthogonal.cube", dataset_id="dataset").objects[0]
    cube_artifacts = VolumetricDataAdapter().execute(_context(tmp_path / "cube", cube), _request({"quantity_hint": "electron_density"}))
    cube_dataset = _read(tmp_path / "cube", cube_artifacts, "volumetric_dataset.json")
    cube_field = cube_dataset["fields"][0]
    assert cube_field["quantity"] == "electron_density"
    assert cube_field["unit"]["source_unit"] == "electron/bohr^3"
    assert cube_field["unit"]["conversion_applied"] is True


def _profile() -> DataProfile:
    return DataProfile.model_validate({
        "schemaVersion": "0.1", "profileId": "profile_volume", "datasetId": "dataset_volume",
        "version": "1", "datasetType": "volumetric", "objects": [{"id": "volumetric", "objectType": "VolumetricData"}],
        "qualityIssues": [], "recommendedTasks": [], "createdAt": "2026-07-18T00:00:00Z",
    })


def test_registry_planner_validator_and_runtime_flow(tmp_path: Path) -> None:
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.volumetric_data")
    assert tool.category.value == "parser"
    assert tool.inputSchema.inputOptions[0].requiredObjectTypes == [MaterialObjectType.VolumetricData]
    response = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt="Parse this CHGCAR into canonical volumetric artifacts.", dataset_id="dataset_volume", profile_id="profile_volume", tool_registry_version=registry.version),
        tools=registry.list_tools(), data_profile=_profile(),
    )
    assert response.raw_json and response.raw_json["steps"][0]["toolId"] == "structure.volumetric_data"
    assert validate_plan(response.raw_json, registry=registry).ok
    source = parse_file(FIXTURES / "CHGCAR", dataset_id="dataset_volume").objects[0]
    repos = InMemoryRepositoryBundle.create()
    runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=tmp_path / "runtime")
    created = planner_jobs(
        PlannerJobsRequest(userPrompt="Parse this CHGCAR into canonical volumetric artifacts.", projectId="project_volume", datasetId="dataset_volume", profileId="profile_volume", enqueue=True),
        provider=MockLLMProvider(fixed_plan=response.raw_json), repositories=repos, queue_runtime=runtime, registry=registry,
    )
    assert created.ok and created.job_id
    result = runtime.handle_job(created.job_id, object_store={"volumetric": source})
    assert result.status == "completed"
    assert repos.tool_calls.list_for_job(created.job_id)[0]["toolId"] == "structure.volumetric_data"
    assert any(item["name"] == "volumetric_manifest.json" for item in repos.artifacts.list_for_job(created.job_id))


@pytest.mark.parametrize("prompt", ["Render a charge density isosurface", "Run VASP to calculate charge density", "Show a volumetric 3D viewer", "Animate a phonon mode"])
def test_negative_planner_routing(prompt: str) -> None:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt=prompt, dataset_id="dataset_volume", profile_id="profile_volume", tool_registry_version=registry.version),
        tools=registry.list_tools(), data_profile=_profile(),
    )
    assert response.raw_json and response.raw_json["steps"][0]["toolId"] != "structure.volumetric_data"
