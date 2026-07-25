from __future__ import annotations

import json
from pathlib import Path

import pytest

from mdi_adapters import ToolExecutionContext, VolumetricDataAdapter
from mdi_artifact_core import decode_volumetric_payload, validate_volumetric_dataset, validate_volumetric_manifest
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import VolumetricParseError, parse_file, parse_volumetric_file
from mdi_schemas import DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10j" / "fixtures" / "volumetric_parser"
ARTIFACT_TYPES = [
    "volumetric_grid_json", "volumetric_payload_json", "volumetric_field_json",
    "volumetric_dataset_json", "volumetric_manifest_json", "volumetric_binary",
    "summary_md", "recipe_json", "volumetric_structure_overlay_json",
]


def _context(root: Path, source: object) -> ToolExecutionContext:
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.volumetric_data")
    return ToolExecutionContext(
        job_id="job_elf_orbital", project_id="project_elf_orbital", dataset_id="dataset_elf_orbital",
        tool_id=tool.toolId, tool_version=tool.version, adapter_version="1.0.0",
        registry_version=registry.version, artifact_root=root, tool_call_id="call_elf_orbital",
        object_store={"volumetric": source}, resource_limits=tool.resourceLimits,
    )


def _request(quantity_hint: str = "auto") -> ToolExecutionRequest:
    return ToolExecutionRequest(
        jobId="job_elf_orbital", stepId="step_001", toolId="structure.volumetric_data",
        inputRefs=[{"refType": "normalized_object", "ref": "volumetric", "objectType": "VolumetricData"}],
        params={"quantity_hint": quantity_hint}, artifactTypes=ARTIFACT_TYPES,
    )


def _content(root: Path, artifacts: list, name: str) -> bytes:
    artifact = next(item for item in artifacts if item.name == name)
    return (root / artifact.storageKey).read_bytes()


def _json(root: Path, artifacts: list, name: str) -> dict:
    return json.loads(_content(root, artifacts, name))


@pytest.mark.parametrize(
    ("source_name", "quantity", "unit", "integral_semantics"),
    [
        ("ELFCAR", "electron_localization_function", "dimensionless", "not_physically_interpreted"),
        ("PARCHG", "orbital_density", "electron/angstrom^3", "electron_count"),
    ],
)
def test_runtime_artifact_semantics_are_source_native_and_canonical(
    tmp_path: Path, source_name: str, quantity: str, unit: str, integral_semantics: str,
) -> None:
    source = parse_file(FIXTURES / source_name, dataset_id="dataset_elf_orbital").objects[0]
    root = tmp_path / source_name.lower()
    artifacts = VolumetricDataAdapter().execute(_context(root, source), _request())
    dataset = _json(root, artifacts, "volumetric_dataset.json")
    manifest = _json(root, artifacts, "volumetric_manifest.json")
    binaries = {item.name: _content(root, artifacts, item.name) for item in artifacts if item.type.value == "volumetric_binary"}
    field = dataset["fields"][0]

    assert validate_volumetric_dataset(dataset, binaries).valid
    assert validate_volumetric_manifest(manifest, dataset=dataset, artifacts=binaries).valid
    assert field["quantity"] == quantity
    assert field["unit"]["canonical_unit"] == unit
    assert field["normalization_semantics"] == "source_native"
    assert field["integral_semantics"] == integral_semantics
    assert field["value_kind"] == "real" and field["field_rank"] == "scalar"
    assert field["provenance"]["source_sha256"] == source.payload["source_sha256"]
    assert all(value == pytest.approx(expected) for value, expected in zip(
        decode_volumetric_payload(dataset["payloads"][0], binaries),
        source.payload["channels"][0]["values"], strict=True,
    ))
    recipe = _json(root, artifacts, "recipe.json")
    product = recipe["scientificContract"]["elfOrbitalFields"][0]
    assert product["sourceValuesModified"] is False
    assert product["identityCompleteness"] == ("unavailable" if quantity == "orbital_density" else "not_applicable")
    summary = _content(root, artifacts, "summary.md").decode()
    assert ("not bond" in summary.lower()) if quantity == "electron_localization_function" else ("source-defined partial density" in summary)


def test_elf_and_parchg_source_values_and_integrals_remain_exact() -> None:
    elf = parse_volumetric_file(FIXTURES / "ELFCAR").source["channels"][0]
    parchg = parse_volumetric_file(FIXTURES / "PARCHG").source["channels"][0]
    assert min(elf["values"]) == 0 and max(elf["values"]) == 1
    assert sum(elf["values"]) == pytest.approx(3.1)
    assert min(parchg["values"]) == pytest.approx(0.5)
    assert max(parchg["values"]) == pytest.approx(4.0)
    assert sum(parchg["values"]) == pytest.approx(18.0)


def test_cube_requires_explicit_orbital_quantity_and_rejects_multi_orbital() -> None:
    generic = parse_volumetric_file(FIXTURES / "orthogonal.cube")
    explicit = parse_volumetric_file(FIXTURES / "orthogonal.cube", quantity_hint="orbital_density")
    assert generic.source["channels"][0]["quantity"] == "generic_scalar"
    assert explicit.source["channels"][0]["quantity"] == "orbital_density"
    assert explicit.source["channels"][0]["normalization_semantics"] == "source_native"
    with pytest.raises(VolumetricParseError) as error:
        parse_volumetric_file(FIXTURES / "multi_orbital.cube", quantity_hint="orbital_density")
    assert error.value.code == "VOLUME_CUBE_MULTI_ORBITAL_UNSUPPORTED"


def _profile() -> DataProfile:
    return DataProfile.model_validate({
        "schemaVersion": "0.1", "profileId": "profile_elf_orbital", "datasetId": "dataset_elf_orbital",
        "version": "1", "datasetType": "volumetric",
        "objects": [{"id": "volumetric", "objectType": "VolumetricData"}],
        "qualityIssues": [], "recommendedTasks": [], "createdAt": "2026-07-24T00:00:00Z",
    })


@pytest.mark.parametrize("prompt", [
    "显示这个 ELFCAR 的 ELF 等值面", "查看电子局域函数", "Visualize the ELF from this ELFCAR",
    "Show an ELF isosurface at 0.7", "显示这个 PARCHG 的部分电荷密度",
    "可视化这个轨道密度 CUBE", "Show the orbital-density isosurface",
])
def test_precise_elf_orbital_product_prompts_use_existing_tool(prompt: str) -> None:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt=prompt, dataset_id="dataset_elf_orbital", profile_id="profile_elf_orbital", tool_registry_version=registry.version),
        tools=registry.list_tools(), data_profile=_profile(),
    )
    assert response.raw_json and response.raw_json["steps"][0]["toolId"] == "structure.volumetric_data"


@pytest.mark.parametrize("prompt", [
    "Show the HOMO", "Display the LUMO", "Calculate ELF basins", "Find lone pairs from ELF",
    "Reconstruct the wavefunction", "Combine two orbitals", "计算轨道占据数", "生成轨道",
])
def test_unsupported_identity_calculation_and_topology_prompts_do_not_route(prompt: str) -> None:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt=prompt, dataset_id="dataset_elf_orbital", profile_id="profile_elf_orbital", tool_registry_version=registry.version),
        tools=registry.list_tools(), data_profile=_profile(),
    )
    assert response.raw_json and response.raw_json["steps"][0]["toolId"] != "structure.volumetric_data"
