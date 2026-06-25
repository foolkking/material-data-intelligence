from __future__ import annotations

import pytest

from mdi_adapters import ToolExecutionContext, ToolExecutionError, execute_tool_request
from mdi_schemas import ArtifactType, ToolExecutionRequest
from mdi_tool_registry import load_manifests


def make_context(tmp_path, object_store):
    return ToolExecutionContext(
        job_id="job_exec",
        project_id="project_exec",
        dataset_id="dataset_exec",
        tool_id="composition.ptable_heatmap",
        tool_version="0.1.0",
        adapter_version="0.1.0",
        registry_version="0.1.0",
        artifact_root=tmp_path / "artifacts",
        tool_call_id="call_exec",
        object_store=object_store,
    )


def make_request(**overrides):
    values = {
        "jobId": "job_exec",
        "stepId": "step_exec",
        "toolId": "composition.ptable_heatmap",
        "inputRefs": [{"refType": "normalized_object", "ref": "formulas", "objectType": "Composition"}],
        "params": {"title": "Executor path"},
        "artifactTypes": ["plotly_json", "summary_md", "recipe_json"],
    }
    values.update(overrides)
    return ToolExecutionRequest(**values)


def test_execute_tool_request_routes_through_registry_and_adapter(tmp_path):
    result = execute_tool_request(
        make_context(tmp_path, {"formulas": ["Si", "Fe2O3"]}),
        make_request(),
        registry=load_manifests(),
    )

    assert result.tool.toolId == "composition.ptable_heatmap"
    assert result.cache_hit is False
    assert result.cache_key.startswith("cache:tool_result:")
    assert {artifact.type for artifact in result.artifacts} == {
        ArtifactType.plotly_json,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }


def test_execute_tool_request_validates_registered_params_schema(tmp_path):
    request = make_request(params={"unknownParam": True})

    with pytest.raises(ToolExecutionError) as exc_info:
        execute_tool_request(make_context(tmp_path, {"formulas": ["Si"]}), request)

    assert exc_info.value.code == "TOOL_PARAM_INVALID"
    assert "Additional properties are not allowed" in exc_info.value.details["errors"][0]


def test_execute_tool_request_rejects_unregistered_tool(tmp_path):
    request = make_request(toolId="composition.not_registered")

    with pytest.raises(ToolExecutionError) as exc_info:
        execute_tool_request(make_context(tmp_path, {"formulas": ["Si"]}), request)

    assert exc_info.value.code == "TOOL_NOT_REGISTERED"


def test_execute_tool_request_uses_cache_when_available(tmp_path):
    cache = {}
    context = make_context(tmp_path, {"formulas": ["Si"]})
    request = make_request()

    first = execute_tool_request(context, request, cache=cache)
    second = execute_tool_request(context, request, cache=cache)

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert second.artifacts == first.artifacts

