from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from mdi_api.repositories import InMemoryRepositoryBundle, compute_plan_hash
from mdi_api.routers.planner import get_planner_job, get_planner_job_dependencies
from mdi_schemas import AnalysisPlanV02, compute_dependency_graph_hash, make_dependency_binding
from mdi_tool_registry import load_manifests, validate_dependency_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
PHONON_FIXTURES = ROOT / "docs" / "phase10h" / "fixtures" / "phonon_contract"


def _source(name: str) -> dict[str, Any]:
    return json.loads((PHONON_FIXTURES / name).read_text(encoding="utf-8"))


def _step(
    step_id: str,
    tool_id: str,
    *,
    refs: list[dict[str, Any]],
    artifacts: list[str],
) -> dict[str, Any]:
    return {
        "stepId": step_id,
        "toolId": tool_id,
        "purpose": f"Execute {tool_id}",
        "reason": "Phase 10L-3 real registered Adapter execution fixture.",
        "inputRefs": refs,
        "params": {},
        "output": {"artifactTypes": artifacts, "displayTarget": "result"},
    }


def _plan(*, include_independent: bool = False) -> AnalysisPlanV02:
    band_binding = make_dependency_binding(
        producerStepId="step_band",
        producerOutputPort="canonical-band",
        consumerStepId="step_combined",
        consumerInputPort="band",
        artifactKind="phonon_band_json",
        artifactContractVersion="phase10h.phonon_band.v1",
        mediaType="application/json",
        cardinality="EXACTLY_ONE",
    )
    dos_binding = make_dependency_binding(
        producerStepId="step_dos",
        producerOutputPort="canonical-dos",
        consumerStepId="step_combined",
        consumerInputPort="dos",
        artifactKind="phonon_dos_json",
        artifactContractVersion="phase10h.phonon_dos.v1",
        mediaType="application/json",
        cardinality="EXACTLY_ONE",
    )
    steps = [
        _step(
            "step_combined",
            "phonon.band_dos",
            refs=[],
            artifacts=["phonon_band_dos_json"],
        ),
        _step(
            "step_dos",
            "phonon.dos",
            refs=[{"refType": "normalized_object", "ref": "source_dos", "objectType": "PhononDos"}],
            artifacts=["phonon_dos_json"],
        ),
        _step(
            "step_band",
            "phonon.band",
            refs=[{"refType": "normalized_object", "ref": "source_band", "objectType": "PhononBand"}],
            artifacts=["phonon_band_json"],
        ),
    ]
    if include_independent:
        steps.insert(
            1,
            _step(
                "step_independent",
                "composition.summary",
                refs=[{"refType": "normalized_object", "ref": "formulas", "objectType": "Composition"}],
                artifacts=["table_json"],
            ),
        )
    bindings = [band_binding, dos_binding]
    return AnalysisPlanV02.model_validate(
        {
            "schemaVersion": "0.2",
            "goal": "Build an exact phonon band and DOS linked product.",
            "datasetId": "dataset_l3_runtime",
            "profileId": "profile_l3_runtime",
            "toolRegistryVersion": load_manifests().version,
            "assumptions": [],
            "warnings": [],
            "steps": steps,
            "expectedArtifacts": [
                {"name": "phonon_band.json", "type": "phonon_band_json", "fromStepId": "step_band"},
                {"name": "phonon_dos.json", "type": "phonon_dos_json", "fromStepId": "step_dos"},
                {
                    "name": "phonon_band_dos.json",
                    "type": "phonon_band_dos_json",
                    "fromStepId": "step_combined",
                },
            ],
            "graphHash": compute_dependency_graph_hash(bindings),
            "dependencyBindings": [item.model_dump(mode="json") for item in bindings],
        }
    )


def _seed(plan: AnalysisPlanV02) -> tuple[InMemoryRepositoryBundle, str, str]:
    repos = InMemoryRepositoryBundle.create()
    project_id = "project_l3_runtime"
    job_id = "job_l3_runtime"
    plan_id = "plan_l3_runtime"
    repos.projects.save({"id": project_id, "name": "Phase 10L-3 runtime"})
    repos.datasets.save({"id": plan.datasetId, "projectId": project_id, "name": "Typed phonon sources"})
    plan_hash = compute_plan_hash(plan)
    repos.analysis_plans.save_plan(
        {
            "id": plan_id,
            "projectId": project_id,
            "datasetId": plan.datasetId,
            "profileId": plan.profileId,
            "planSource": "capability_planner",
            "plannerProvider": "mock",
            "analysisPlan": plan.model_dump(mode="json"),
            "planHash": plan_hash,
            "createdBy": "phase10l3_test",
        }
    )
    repos.dependency_execution.save_plan_bindings(
        plan_id,
        plan_hash,
        plan.graphHash,
        plan.dependencyBindings,
    )
    repos.jobs.save(
        {
            "id": job_id,
            "projectId": project_id,
            "datasetId": plan.datasetId,
            "planId": plan_id,
            "status": "created",
            "kind": "analysis",
            "createdBy": "phase10l3_test",
        }
    )
    repos.analysis_plans.attach_plan_to_job(plan_id, job_id)
    return repos, job_id, plan_hash


def _object_store(*, bad_band: bool = False) -> dict[str, Any]:
    return {
        "source_band": {} if bad_band else _source("stable_band.json"),
        "source_dos": _source("projected_dos.json"),
        "formulas": ["Si", "Fe2O3"],
    }


def test_real_registered_dependency_chain_executes_topologically_and_replays_idempotently(tmp_path: Path) -> None:
    registry = load_manifests()
    plan = _plan()
    validation = validate_dependency_plan(plan, registry=registry)
    assert validation.ok
    assert validation.topological_order == ["step_band", "step_dos", "step_combined"]
    assert [step.stepId for step in plan.steps][0] == "step_combined"

    repos, job_id, plan_hash = _seed(plan)
    runtime = QueueWorkerRuntime(
        repositories=repos,
        registry=registry,
        artifact_root=tmp_path / "adapter",
    )
    result = runtime.handle_job(job_id, object_store=_object_store())

    assert result.status == "completed"
    assert result.plan_hash == plan_hash
    calls = repos.tool_calls.list_for_job(job_id)
    assert [(item["stepId"], item["toolId"], item["status"]) for item in calls] == [
        ("step_band", "phonon.band", "completed"),
        ("step_dos", "phonon.dos", "completed"),
        ("step_combined", "phonon.band_dos", "completed"),
    ]
    artifacts = repos.artifacts.list_for_job(job_id)
    assert [item["type"] for item in artifacts] == [
        "phonon_band_json",
        "phonon_dos_json",
        "phonon_band_dos_json",
    ]
    resolutions = repos.dependency_execution.list_binding_resolutions(job_id)
    assert len(resolutions) == 2
    assert {item["validationOutcome"] for item in resolutions} == {"RESOLVED"}
    assert all(item["resolvedArtifactInputRef"]["materializedObjectRef"].startswith("resolved:binding_") for item in resolutions)
    execution = repos.dependency_execution.get_execution_for_job(job_id)
    assert execution["outcome"] == "ALL_SUCCEEDED"
    assert execution["topologicalOrder"] == validation.topological_order
    lineages = repos.dependency_execution.list_lineage_for_job(job_id)
    assert len(lineages) == 3
    combined = next(item for item in lineages if item["producerToolId"] == "phonon.band_dos")
    assert combined["outputPort"] == "combined-band-dos"
    assert len(combined["upstreamArtifactIds"]) == 2
    assert len(combined["bindingIds"]) == 2
    api_dependencies = get_planner_job_dependencies(job_id, repositories=repos)
    assert api_dependencies["planSchemaVersion"] == "0.2"
    assert api_dependencies["graphHash"] == plan.graphHash
    assert api_dependencies["topologicalOrder"] == validation.topological_order
    assert api_dependencies["execution"]["outcome"] == "ALL_SUCCEEDED"
    assert len(api_dependencies["bindingResolutions"]) == 2
    assert len(api_dependencies["artifactLineage"]) == 3
    assert get_planner_job(job_id, repositories=repos)["dependencyExecutionSummary"]["outcome"] == "ALL_SUCCEEDED"

    counts = (len(calls), len(artifacts), len(lineages), len(repos.job_events.list_for_job(job_id)))
    replay = runtime.handle_job(job_id, object_store=_object_store())
    assert replay.status == "completed"
    assert counts == (
        len(repos.tool_calls.list_for_job(job_id)),
        len(repos.artifacts.list_for_job(job_id)),
        len(repos.dependency_execution.list_lineage_for_job(job_id)),
        len(repos.job_events.list_for_job(job_id)),
    )


def test_producer_failure_blocks_consumer_but_independent_real_adapter_continues(tmp_path: Path) -> None:
    plan = _plan(include_independent=True)
    repos, job_id, _ = _seed(plan)
    runtime = QueueWorkerRuntime(
        repositories=repos,
        registry=load_manifests(),
        artifact_root=tmp_path / "adapter",
    )
    result = runtime.handle_job(job_id, object_store=_object_store(bad_band=True))

    assert result.status == "partial_success"
    calls = repos.tool_calls.list_for_job(job_id)
    by_step = {item["stepId"]: item for item in calls}
    assert by_step["step_band"]["status"] == "failed"
    assert by_step["step_dos"]["status"] == "completed"
    assert by_step["step_independent"]["status"] == "completed"
    assert "step_combined" not in by_step
    execution = repos.dependency_execution.get_execution_for_job(job_id)
    states = {item["stepId"]: item for item in execution["steps"]}
    assert states["step_combined"]["state"] == "BLOCKED_DEPENDENCY"
    assert states["step_combined"]["blockedByStepIds"] == ["step_band"]
    assert execution["outcome"] == "PARTIAL_RESULTS"
    assert repos.artifacts.list_for_job(job_id)

    counts = (len(calls), len(repos.artifacts.list_for_job(job_id)), len(repos.job_events.list_for_job(job_id)))
    replay = runtime.handle_job(job_id, object_store=_object_store(bad_band=True))
    assert replay.status == "partial_success"
    assert counts == (
        len(repos.tool_calls.list_for_job(job_id)),
        len(repos.artifacts.list_for_job(job_id)),
        len(repos.job_events.list_for_job(job_id)),
    )


def test_consumer_failure_retains_upstream_artifacts_and_terminal_replay_is_idempotent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = _plan()
    repos, job_id, _ = _seed(plan)
    runtime = QueueWorkerRuntime(
        repositories=repos,
        registry=load_manifests(),
        artifact_root=tmp_path / "adapter",
    )
    original = runtime._execute_tool

    def fail_consumer(request: Any, context: Any, *, object_store: Any) -> Any:
        if request.toolId == "phonon.band_dos":
            raise RuntimeError("typed consumer failure fixture")
        return original(request, context, object_store=object_store)

    monkeypatch.setattr(runtime, "_execute_tool", fail_consumer)
    result = runtime.handle_job(job_id, object_store=_object_store())

    assert result.status == "partial_success"
    execution = repos.dependency_execution.get_execution_for_job(job_id)
    assert execution["outcome"] == "PARTIAL_RESULTS"
    states = {item["stepId"]: item["state"] for item in execution["steps"]}
    assert states == {
        "step_band": "SUCCEEDED",
        "step_dos": "SUCCEEDED",
        "step_combined": "FAILED",
    }
    artifacts = repos.artifacts.list_for_job(job_id)
    assert {item["type"] for item in artifacts} == {"phonon_band_json", "phonon_dos_json"}
    assert len(repos.dependency_execution.list_binding_resolutions(job_id)) == 2

    counts = (len(repos.tool_calls.list_for_job(job_id)), len(artifacts), len(repos.job_events.list_for_job(job_id)))
    replay = runtime.handle_job(job_id, object_store=_object_store())
    assert replay.status == "partial_success"
    assert counts == (
        len(repos.tool_calls.list_for_job(job_id)),
        len(repos.artifacts.list_for_job(job_id)),
        len(repos.job_events.list_for_job(job_id)),
    )


def test_tampered_artifact_bytes_fail_checksum_before_consumer_adapter_invocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = _plan()
    repos, job_id, _ = _seed(plan)
    runtime = QueueWorkerRuntime(
        repositories=repos,
        registry=load_manifests(),
        artifact_root=tmp_path / "adapter",
    )
    original_get_bytes = runtime.artifact_storage.get_bytes
    reads = 0

    def tampered_get_bytes(storage_key: str) -> bytes:
        nonlocal reads
        reads += 1
        content = original_get_bytes(storage_key)
        return b"tampered-artifact-bytes" if reads == 1 else content

    monkeypatch.setattr(runtime.artifact_storage, "get_bytes", tampered_get_bytes)
    result = runtime.handle_job(job_id, object_store=_object_store())

    assert result.status == "partial_success"
    assert reads >= 1
    assert "step_combined" not in {item["stepId"] for item in repos.tool_calls.list_for_job(job_id)}
    failures = repos.dependency_execution.list_binding_resolutions(job_id)
    assert any(
        item["validationOutcome"] == "CHECKSUM_MISMATCH" and item["errorCode"] == "CHECKSUM_MISMATCH"
        for item in failures
    )
    execution = repos.dependency_execution.get_execution_for_job(job_id)
    combined = next(item for item in execution["steps"] if item["stepId"] == "step_combined")
    assert combined["state"] == "FAILED"
    assert combined["errorCode"] == "CHECKSUM_MISMATCH"
