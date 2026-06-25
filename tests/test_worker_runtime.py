from __future__ import annotations

import pytest

from mdi_adapters import ToolExecutionContext
from mdi_schemas import JobStatus, ToolExecutionRequest
from mdi_workers import InMemoryJobStore, WorkerToolExecutionError, run_tool_call_job


def make_context(tmp_path, object_store):
    return ToolExecutionContext(
        job_id="job_worker",
        project_id="project_worker",
        dataset_id="dataset_worker",
        tool_id="composition.ptable_heatmap",
        tool_version="0.1.0",
        adapter_version="0.1.0",
        registry_version="0.1.0",
        artifact_root=tmp_path / "artifacts",
        tool_call_id="call_worker",
        object_store=object_store,
    )


def make_request(**overrides):
    values = {
        "jobId": "job_worker",
        "stepId": "step_worker",
        "toolId": "composition.ptable_heatmap",
        "inputRefs": [{"refType": "normalized_object", "ref": "formulas", "objectType": "Composition"}],
        "params": {"title": "Worker runtime"},
        "artifactTypes": ["plotly_json", "summary_md", "recipe_json"],
    }
    values.update(overrides)
    return ToolExecutionRequest(**values)


def test_worker_runtime_records_tool_call_and_artifact_events(tmp_path):
    store = InMemoryJobStore()
    result = run_tool_call_job(
        make_context(tmp_path, {"formulas": ["Si", "Fe2O3"]}),
        make_request(),
        store=store,
    )

    assert result.job.status == JobStatus.completed
    assert result.tool_call.status == "completed"
    assert len(result.tool_call.artifactIds) == 3
    assert [event.seq for event in result.job.events] == [1, 2, 3, 4, 5]
    assert [event.eventType for event in result.job.events] == [
        "tool.started",
        "artifact.ready",
        "artifact.ready",
        "artifact.ready",
        "tool.completed",
    ]
    assert all(event.jobId == "job_worker" for event in result.events)


def test_worker_runtime_records_failed_tool_call_and_redacts_secret_params(tmp_path):
    store = InMemoryJobStore()
    request = make_request(params={"api_key": "secret-value"})

    with pytest.raises(WorkerToolExecutionError) as exc_info:
        run_tool_call_job(make_context(tmp_path, {"formulas": ["Si"]}), request, store=store)

    job = exc_info.value.job
    tool_call = exc_info.value.tool_call
    assert job.status == JobStatus.failed
    assert tool_call.status == "failed"
    assert tool_call.params["api_key"] == "[REDACTED]"
    assert tool_call.error["code"] == "TOOL_PARAM_INVALID"
    assert [event.eventType for event in job.events] == ["tool.started", "tool.failed"]
    assert "secret-value" not in str(tool_call.model_dump())

