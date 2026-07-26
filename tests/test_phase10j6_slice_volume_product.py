from __future__ import annotations

import pytest

from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests


def _profile() -> DataProfile:
    return DataProfile.model_validate({
        "schemaVersion": "0.1", "profileId": "profile_slice_volume", "datasetId": "dataset_slice_volume",
        "version": "1", "datasetType": "volumetric",
        "objects": [{"id": "volumetric", "objectType": "VolumetricData"}],
        "qualityIssues": [], "recommendedTasks": [], "createdAt": "2026-07-25T00:00:00Z",
    })


def _tool_for(prompt: str) -> str:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt=prompt, dataset_id="dataset_slice_volume", profile_id="profile_slice_volume", tool_registry_version=registry.version),
        tools=registry.list_tools(), data_profile=_profile(),
    )
    assert response.raw_json
    return str(response.raw_json["steps"][0]["toolId"])


@pytest.mark.parametrize("prompt", [
    "显示这个 CHGCAR 在晶格 c 方向的切片",
    "查看这个体数据在 fractional 0.5 位置的截面",
    "显示 LOCPOT 的二维晶格切片",
    "Show a slice through this volumetric field",
    "Display the plane at fractional coordinate 0.5",
    "直接体绘制这个电荷密度",
    "用 volume rendering 显示这个 CUBE",
    "显示 ELF 的体绘制",
    "Render this volumetric field directly",
    "Open the 3D volume view",
])
def test_slice_and_direct_volume_intents_reuse_canonical_volumetric_tool(prompt: str) -> None:
    assert _tool_for(prompt) == "structure.volumetric_data"


@pytest.mark.parametrize("prompt", [
    "生成任意曲面切片",
    "自动分割电子云",
    "做 Bader 分析",
    "计算真空能级",
    "重构波函数并显示复相位",
    "Apply an arbitrary Python volume filter",
    "Run VASP and render on a remote GPU",
    "Show a curved slice through the field",
])
def test_unsupported_calculation_segmentation_and_arbitrary_slice_intents_do_not_route(prompt: str) -> None:
    assert _tool_for(prompt) != "structure.volumetric_data"


def test_slice_volume_plan_keeps_backend_artifacts_inert_and_unchanged() -> None:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt="Render this volumetric field directly", dataset_id="dataset_slice_volume", profile_id="profile_slice_volume", tool_registry_version=registry.version),
        tools=registry.list_tools(), data_profile=_profile(),
    )
    assert response.raw_json
    step = response.raw_json["steps"][0]
    assert step["toolId"] == "structure.volumetric_data"
    assert step["constraints"] == {"noExternalNetwork": True}
    assert "volumetric_dataset_json" in step["output"]["artifactTypes"]
    assert "volumetric_manifest_json" in step["output"]["artifactTypes"]
    assert all("shader" not in item.lower() and "renderer" not in item.lower() for item in step["output"]["artifactTypes"])
