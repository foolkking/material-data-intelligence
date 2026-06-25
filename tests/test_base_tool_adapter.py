from __future__ import annotations

from typing import Any

import pytest

from mdi_adapters import BaseToolAdapter, ToolExecutionContext, ToolExecutionError
from mdi_artifact_core import ArtifactPayload
from mdi_schemas import Artifact, ArtifactType, ToolExecutionRequest


class DummyAdapter(BaseToolAdapter):
    tool_id = "composition.ptable_heatmap"

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[str] = []

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> dict[str, Any]:
        self.calls.append("prepare")
        return {"value": self._resolved_inputs[0]}

    def run(self, prepared: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        self.calls.append("run")
        return prepared

    def export(self, result: dict[str, Any], artifact_types: list[ArtifactType]) -> list[Artifact]:
        self.calls.append("export")
        return self.export_payloads(
            [
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=f"value={result['value']}",
                    media_type="text/markdown",
                )
            ],
            provenance={"dummy": True},
        )


class BrokenAdapter(DummyAdapter):
    def run(self, prepared: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("boom")


def make_context(tmp_path, object_store):
    return ToolExecutionContext(
        job_id="job_test",
        project_id="project_test",
        dataset_id="dataset_test",
        tool_id="composition.ptable_heatmap",
        tool_version="0.1.0",
        adapter_version="0.1.0",
        registry_version="0.1.0",
        artifact_root=tmp_path,
        tool_call_id="call_test",
        object_store=object_store,
    )


def test_lifecycle_is_called_and_exports_artifact(tmp_path):
    adapter = DummyAdapter()
    request = ToolExecutionRequest(
        jobId="job_test",
        stepId="step_test",
        toolId="composition.ptable_heatmap",
        inputRefs=[{"refType": "normalized_object", "ref": "input_1"}],
        params={},
        artifactTypes=["summary_md"],
    )

    artifacts = adapter.execute(make_context(tmp_path, {"input_1": "ok"}), request)

    assert adapter.calls == ["prepare", "run", "export"]
    assert len(artifacts) == 1
    assert artifacts[0].type == ArtifactType.summary_md
    assert (tmp_path / artifacts[0].storageKey).exists()


def test_errors_are_standardized(tmp_path):
    request = ToolExecutionRequest(
        jobId="job_test",
        stepId="step_test",
        toolId="composition.ptable_heatmap",
        inputRefs=[{"refType": "normalized_object", "ref": "input_1"}],
        params={},
        artifactTypes=["summary_md"],
    )

    with pytest.raises(ToolExecutionError) as exc_info:
        BrokenAdapter().execute(make_context(tmp_path, {"input_1": "ok"}), request)

    assert exc_info.value.code == "TOOL_RUNTIME_ERROR"
    assert exc_info.value.to_dict()["message"] == "boom"


def test_secret_like_params_are_rejected(tmp_path):
    request = ToolExecutionRequest(
        jobId="job_test",
        stepId="step_test",
        toolId="composition.ptable_heatmap",
        inputRefs=[{"refType": "normalized_object", "ref": "input_1"}],
        params={"api_key": "do-not-log"},
        artifactTypes=["summary_md"],
    )

    with pytest.raises(ToolExecutionError) as exc_info:
        DummyAdapter().execute(make_context(tmp_path, {"input_1": "ok"}), request)

    assert exc_info.value.code == "TOOL_PARAM_INVALID"

