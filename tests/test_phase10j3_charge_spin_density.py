from __future__ import annotations

import json
from pathlib import Path

import pytest

from mdi_adapters import ToolExecutionContext, VolumetricDataAdapter
from mdi_artifact_core import decode_volumetric_payload, validate_volumetric_dataset
from mdi_material_parsers import parse_file
from mdi_schemas import ToolExecutionRequest
from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10j" / "fixtures" / "volumetric_parser"
ARTIFACT_TYPES = [
    "volumetric_grid_json", "volumetric_payload_json", "volumetric_field_json",
    "volumetric_dataset_json", "volumetric_manifest_json", "volumetric_binary",
    "summary_md", "recipe_json",
]


def _execute(root: Path, fixture: str, params: dict | None = None):
    source = parse_file(FIXTURES / fixture, dataset_id="dataset").objects[0]
    tool = load_manifests().get_tool_by_id("structure.volumetric_data")
    context = ToolExecutionContext(
        job_id="job", project_id="project", dataset_id="dataset", tool_id=tool.toolId,
        tool_version=tool.version, adapter_version="1.1.0", registry_version=load_manifests().version,
        artifact_root=root, tool_call_id="call", object_store={"volumetric": source},
        resource_limits=tool.resourceLimits,
    )
    request = ToolExecutionRequest(
        jobId="job", stepId="step", toolId=tool.toolId,
        inputRefs=[{"refType": "normalized_object", "ref": "volumetric", "objectType": "VolumetricData"}],
        params=params or {}, artifactTypes=ARTIFACT_TYPES,
    )
    artifacts = VolumetricDataAdapter().execute(context, request)
    dataset_artifact = next(item for item in artifacts if item.name == "volumetric_dataset.json")
    dataset = json.loads((root / dataset_artifact.storageKey).read_text(encoding="utf-8"))
    binaries = {item.name: (root / item.storageKey).read_bytes() for item in artifacts if item.type.value == "volumetric_binary"}
    return artifacts, dataset, binaries


def test_collinear_spin_derivation_is_deterministic_and_replayable(tmp_path: Path) -> None:
    first, dataset, binaries = _execute(tmp_path / "first", "CHGCAR.collinear")
    second, replay, replay_binaries = _execute(tmp_path / "second", "CHGCAR.collinear")
    assert [(item.name, item.contentHash) for item in first] == [(item.name, item.contentHash) for item in second]
    assert dataset == replay
    assert binaries == replay_binaries
    assert validate_volumetric_dataset(dataset, binaries).valid

    payloads = {item["payload_id"]: item for item in dataset["payloads"]}
    fields = {item["field_name"]: item for item in dataset["fields"]}
    values = {name: decode_volumetric_payload(payloads[field["payload_id"]], binaries) for name, field in fields.items()}
    assert values["spin_up"] == pytest.approx([(total + spin) / 2 for total, spin in zip(values["total"], values["spin_difference"], strict=True)])
    assert values["spin_down"] == pytest.approx([(total - spin) / 2 for total, spin in zip(values["total"], values["spin_difference"], strict=True)])
    assert fields["spin_up"]["statistics"]["stored_components"][0]["integral"] == pytest.approx(20.25)
    assert fields["spin_down"]["statistics"]["stored_components"][0]["integral"] == pytest.approx(15.75)
    assert fields["spin_up"]["spin"]["channel"] == "spin_up"
    assert "COLLINEAR_SPIN_UP_V1" in fields["spin_up"]["provenance"]["transformations"][-1]["detail"]
    assert [item["kind"] for item in dataset["relationships"]] == [
        "spin_difference_equals_up_minus_down", "total_equals_up_plus_down",
    ]
    assert all(item["status"] == "validated" and item["residual"] == 0 for item in dataset["relationships"])


def test_nonspin_augmentation_and_signed_charge_remain_source_explicit(tmp_path: Path) -> None:
    _, augmentation, _ = _execute(tmp_path / "augmentation", "CHGCAR.augmentation")
    assert [field["field_name"] for field in augmentation["fields"]] == ["total"]
    assert augmentation["warnings"] == ["VOLUME_VASP_AUGMENTATION_NOT_INCLUDED"]

    _, signed, _ = _execute(tmp_path / "signed", "orthogonal.cube", {"quantity_hint": "charge_density"})
    field = signed["fields"][0]
    assert field["quantity"] == "charge_density"
    assert field["unit"]["canonical_unit"] == "elementary_charge/angstrom^3"
    assert field["integral_semantics"] == "elementary_charge"
    assert field["spin"] is None
    assert signed["relationships"] == []
