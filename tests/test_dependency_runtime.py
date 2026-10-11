from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from mdi_api.repositories import InMemoryRepositoryBundle, compute_plan_hash
from mdi_api.routers.planner import get_planner_job, get_planner_job_dependencies
from mdi_schemas import AnalysisPlanV02, AnalysisPlanV03, DataProfile, compute_dependency_graph_hash, make_dependency_binding
from mdi_tool_registry import load_manifests, validate_dependency_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
PHONON_FIXTURES = ROOT / "tests" / "fixtures" / "phonon_contract"


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


def _multi_plan_and_store():
    from mdi_workers.source_resources import register_runtime_source_resource
    from mdi_schemas import dependency_semantic_hash
    band_id, dos_id = "11111111-1111-4111-8111-111111111111", "22222222-2222-4222-8222-222222222222"
    draft = _plan().model_dump(mode="json")
    draft.update(schemaVersion="0.3", datasetId="dataset_band", profileId="profile_band",
        sourceContexts=[{"datasetId": "dataset_band", "profileId": "profile_band"}, {"datasetId": "dataset_dos", "profileId": "profile_dos"}],
        sourceVersions=[{"objectId": band_id, "versionId": band_id, "datasetId": "dataset_band", "objectType": "PhononBand"},
                        {"objectId": dos_id, "versionId": dos_id, "datasetId": "dataset_dos", "objectType": "PhononDos"}])
    store = {}
    for suffix, source_id, object_type, fixture in [("band", band_id, "PhononBand", "stable_band.json"), ("dos", dos_id, "PhononDos", "projected_dos.json")]:
        data = _source(fixture)
        register_runtime_source_resource(store, object_id=source_id, object_type=object_type,
            object_hash=dependency_semantic_hash(data), dataset_id=f"dataset_{suffix}", value=data)
        profile = DataProfile(profileId=f"profile_{suffix}", datasetId=f"dataset_{suffix}", datasetType="structure", version="1.0", createdAt="2026-10-06T00:00:00Z")
        register_runtime_source_resource(store, object_id=f"profile:profile_{suffix}", object_type="DataProfile",
            object_hash=f"profile_{suffix}", dataset_id=f"dataset_{suffix}", value=profile)
    for step in draft["steps"]:
        ids = []
        for input_ref in step["inputRefs"]:
            input_ref["ref"] = band_id if input_ref["ref"] == "source_band" else dos_id
            ids.append(input_ref["ref"])
        step["output"]["sourceObjectVersionIds"] = ids or [band_id, dos_id]
    return AnalysisPlanV03.model_validate(draft), store


def test_cross_dataset_dependency_outputs_keep_all_sources_without_false_dataset_ownership(tmp_path):
    plan, store = _multi_plan_and_store()
    repos, job_id, plan_hash = _seed(plan)
    runtime = QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path / "adapter")
    result = runtime.handle_job(job_id, object_store=store)
    assert result.status == "completed", repos.job_events.list_for_job(job_id)
    assert result.plan_hash == plan_hash
    artifacts = repos.artifacts.list_for_job(job_id)
    lineages = repos.dependency_execution.list_lineage_for_job(job_id)
    combined = next(item for item in lineages if item["producerToolId"] == "phonon.band_dos")
    assert combined["datasetId"] is None and combined["profileId"] is None
    assert len(combined["sourceVersions"]) == 2 and len(combined["upstreamArtifactIds"]) == 2
    assert next(item for item in artifacts if item["type"] == "phonon_band_dos_json")["datasetId"] is None
    assert {item["datasetId"] for item in lineages if item["producerStepId"] != "step_combined"} == {"dataset_band", "dataset_dos"}
    details = get_planner_job_dependencies(job_id, repositories=repos)
    assert details["planSchemaVersion"] == "0.3"
    assert details["execution"]["outcome"] == "ALL_SUCCEEDED"
    assert len(details["bindingResolutions"]) == 2
    assert len(details["plannedBindingRecords"]) == 2
    assert runtime.handle_job(job_id, object_store=store).status == "completed"
    assert len(repos.tool_calls.list_for_job(job_id)) == 3
    assert len(repos.artifacts.list_for_job(job_id)) == 3


@pytest.mark.parametrize("wrong_source", [False, True])
def test_cross_dataset_msd_reuse_verifies_persisted_sources_before_diffusion(tmp_path, wrong_source):
    from mdi_tool_registry import build_artifact_port_inventory
    plan, store = _multi_plan_and_store()
    draft = plan.model_dump(mode="json")
    for source in draft["sourceVersions"]:
        source["objectType"] = "Trajectory"
    ids = [item["versionId"] for item in draft["sourceVersions"]]
    draft.update(dependencyBindings=[], graphHash=compute_dependency_graph_hash([]), expectedArtifacts=[], steps=[
        {**_step(f"diffuse_{i}", "trajectory.diffusion", refs=[{"refType": "artifact", "ref": f"prior_msd_{i}", "fieldRole": "msd_artifact", "objectType": "Trajectory"}], artifacts=["table_json"]),
         "params": {"fit_start_time_ps": 1.0, "fit_end_time_ps": 8.0, "minimum_fit_points": 5, "minimum_fit_duration_ps": 1.0, "minimum_r_squared": 0.9},
         "output": {"artifactTypes": ["table_json"], "sourceObjectVersionIds": [ids[1-i] if wrong_source else source_id]}}
        for i, source_id in enumerate(ids)])
    plan = AnalysisPlanV03.model_validate(draft)
    repos, job_id, _ = _seed(plan)
    runtime = QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path / "adapter")
    for i, source in enumerate(plan.sourceVersions):
        source_context = next(item for item in plan.sourceContexts if item.datasetId == source.datasetId)
        producer = AnalysisPlanV02.model_validate({"schemaVersion": "0.2", "goal": "Saved MSD", "datasetId": source.datasetId,
            "profileId": source_context.profileId, "toolRegistryVersion": runtime.registry.version, "graphHash": compute_dependency_graph_hash([]),
            "steps": [{**_step("msd", "trajectory.msd", refs=[{"refType": "normalized_object", "ref": str(source.versionId), "objectType": "Trajectory"}], artifacts=["table_json"]),
                       "output": {"sourceObjectVersionIds": [str(source.versionId)]}}]})
        producer_record = repos.analysis_plans.save_plan({"id": f"prior_plan_{i}", "projectId": "project_l3_runtime", "analysisPlan": producer.model_dump(mode="json")})
        producer_job = {"id": f"prior_job_{i}", "projectId": "project_l3_runtime", "datasetId": source.datasetId}
        payload = {"artifactType": "trajectory.msd", "schema_version": "phase10n4.trajectory_msd.v1",
            "trajectory": {"resourceId": "sha256:" + str(i+1)*64, "trajectoryHash": "sha256:" + str(i+1)*64,
                           "contractVersion": "phase10g.trajectory.v1", "frameCount": 20, "atomCount": 4},
            "parameterHash": "2"*64, "lagTimesPs": [float(v) for v in range(1, 9)],
            "totalMsdAngstrom2": [0.6*(i+1)*v for v in range(1, 9)],
            "directionalMsdAngstrom2": {axis: [0.2*(i+1)*v for v in range(1, 9)] for axis in ["x", "y", "z"]},
            "originCounts": list(range(20, 12, -1))}
        stored = runtime.artifact_storage.put_bytes(f"prior/msd_{i}.json", json.dumps(payload).encode(), content_type="application/json")
        artifact = repos.artifacts.save({"id": f"prior_msd_{i}", "projectId": "project_l3_runtime", "datasetId": source.datasetId,
            "jobId": producer_job["id"], "toolCallId": f"prior_call_{i}", "type": "table_json", "name": "MSD",
            "storageKey": stored.storage_key, "sizeBytes": stored.size_bytes, "contentType": stored.content_type,
            "contentHash": stored.sha256, "sha256": stored.sha256,
            "metadata": {"provenance": {"schemaVersion": "phase10n4.trajectory_msd.v1"}}})
        lineage = runtime._artifact_lineage(repos, job=producer_job, plan=producer, plan_record=producer_record,
            step=producer.steps[0], artifact=artifact, upstream=[], ports=build_artifact_port_inventory(runtime.registry))
        repos.dependency_execution.save_lineage(lineage)
    # Only profiles are needed; the stored MSD values are the scientific inputs.
    store = {key: value for key, value in store.items() if key.startswith("profile:") or key == "__mdi_source_resources__"}
    result = runtime.handle_job(job_id, object_store=store)
    if wrong_source:
        assert result.status == "failed"
        assert repos.tool_calls.list_for_job(job_id) == []
        return
    assert result.status == "completed", repos.job_events.list_for_job(job_id)
    assert [item["toolId"] for item in repos.tool_calls.list_for_job(job_id)] == ["trajectory.diffusion"]*2
    produced = repos.artifacts.list_for_job(job_id)
    assert len(produced) == 2
    for i, artifact in enumerate(produced):
        output = runtime.artifact_storage.get_json(artifact["storageKey"])
        assert output["sourceMsd"]["artifactId"] == f"prior_msd_{i}"
        assert output["runtimeDiagnostics"]["msdRecomputation"] is False
        lineage = repos.dependency_execution.get_lineage_for_artifact(artifact["id"])
        assert lineage["upstreamArtifactIds"] == [f"prior_msd_{i}"]


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


def test_two_step_artifact_ready_is_observable_before_terminal_event(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Observe the real artifact-ready contract without adding a delay."""
    base = _plan()
    two_step = base.model_copy(update={
        "steps": [item for item in base.steps if item.stepId in {"step_band", "step_dos"}],
        "expectedArtifacts": [item for item in base.expectedArtifacts if item.fromStepId in {"step_band", "step_dos"}],
        "dependencyBindings": [],
        "graphHash": compute_dependency_graph_hash([]),
    })
    repos, job_id, _ = _seed(two_step)
    runtime = QueueWorkerRuntime(
        repositories=repos,
        registry=load_manifests(),
        artifact_root=tmp_path / "adapter",
    )
    original_append = repos.job_events.append_event
    observations: list[dict[str, Any]] = []

    def observe(event_job_id: str, *, event_type: str, **kwargs: Any) -> Any:
        result = original_append(event_job_id, event_type=event_type, **kwargs)
        if event_job_id != job_id:
            return result
        if event_type == "artifact.ready":
            artifact_id = str((kwargs.get("payload") or {}).get("artifactId") or "")
            observations.append({
                "event": event_type,
                "artifactPersisted": any(str(item.get("id")) == artifact_id for item in repos.artifacts.list_for_job(job_id)),
                "jobStatusAtEvent": repos.jobs.get(job_id).get("status"),
            })
        elif event_type == "dependency.execution_completed":
            observations.append({"event": event_type, "jobStatusAtEvent": repos.jobs.get(job_id).get("status")})
        return result

    monkeypatch.setattr(repos.job_events, "append_event", observe)
    result = runtime.handle_job(job_id, object_store=_object_store())

    assert result.status == "completed"
    assert [item["event"] for item in observations] == [
        "artifact.ready", "artifact.ready", "dependency.execution_completed",
    ]
    assert all(item["artifactPersisted"] for item in observations[:2])
    assert all(item["jobStatusAtEvent"] != "completed" for item in observations[:2])
    assert observations[-1]["jobStatusAtEvent"] == "completed"
    assert len(repos.artifacts.list_for_job(job_id)) == 2


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


def test_persisted_msd_artifact_is_reused_cross_run_without_recomputation(
    tmp_path: Path,
) -> None:
    """An autonomous diffusion cycle may reuse the exact durable MSD output."""

    artifact_id = "artifact_prior_msd"
    plan = AnalysisPlanV02.model_validate(
        {
            "schemaVersion": "0.2",
            "goal": "Estimate diffusion from an existing exact MSD Result.",
            "datasetId": "dataset_l3_runtime",
            "profileId": "profile_l3_runtime",
            "toolRegistryVersion": load_manifests().version,
            "assumptions": [],
            "warnings": [],
            "steps": [
                _step(
                    "step_diffusion",
                    "trajectory.diffusion",
                    refs=[
                        {
                            "refType": "artifact",
                            "ref": artifact_id,
                            "fieldRole": "msd_artifact",
                            "objectType": "Trajectory",
                        }
                    ],
                    artifacts=["table_json"],
                )
                | {
                    "params": {
                        "fit_start_time_ps": 1.0,
                        "fit_end_time_ps": 8.0,
                        "minimum_fit_points": 5,
                        "minimum_fit_duration_ps": 1.0,
                        "minimum_r_squared": 0.9,
                    }
                }
            ],
            "expectedArtifacts": [
                {
                    "name": "trajectory_diffusion.json",
                    "type": "table_json",
                    "fromStepId": "step_diffusion",
                }
            ],
            "graphHash": compute_dependency_graph_hash([]),
            "dependencyBindings": [],
        }
    )
    registry = load_manifests()
    validation = validate_dependency_plan(plan, registry=registry)
    assert validation.ok

    repos, job_id, _plan_hash = _seed(plan)
    runtime = QueueWorkerRuntime(
        repositories=repos,
        registry=registry,
        artifact_root=tmp_path / "adapter",
    )
    msd_payload = {
        "artifactType": "trajectory.msd",
        "schema_version": "phase10n4.trajectory_msd.v1",
        "trajectory": {
            "resourceId": "sha256:" + "1" * 64,
            "trajectoryHash": "sha256:" + "1" * 64,
            "contractVersion": "phase10g.trajectory.v1",
            "frameCount": 20,
            "atomCount": 4,
        },
        "parameterHash": "2" * 64,
        "lagTimesPs": [float(value) for value in range(1, 9)],
        "totalMsdAngstrom2": [0.6 * value for value in range(1, 9)],
        "directionalMsdAngstrom2": {
            axis: [0.2 * value for value in range(1, 9)]
            for axis in ("x", "y", "z")
        },
        "originCounts": list(range(20, 12, -1)),
    }
    encoded = json.dumps(msd_payload, sort_keys=True).encode("utf-8")
    stored = runtime.artifact_storage.put_bytes(
        "prior/msd.json",
        encoded,
        content_type="application/json",
    )
    repos.artifacts.save(
        {
            "id": artifact_id,
            "projectId": "project_l3_runtime",
            "datasetId": plan.datasetId,
            "jobId": "job_prior_msd",
            "toolCallId": "call_prior_msd",
            "type": "table_json",
            "name": "Persisted MSD",
            "version": "1",
            "storageKey": stored.storage_key,
            "storageProvider": stored.storage_provider,
            "sizeBytes": stored.size_bytes,
            "contentType": stored.content_type,
            "contentHash": stored.sha256,
            "sha256": stored.sha256,
            "metadata": {
                "createdAt": "2026-09-10T00:00:00Z",
                "provenance": {
                    "schemaVersion": "phase10n4.trajectory_msd.v1",
                },
            },
        }
    )

    result = runtime.handle_job(job_id, object_store={})

    assert result.status == "completed"
    calls = repos.tool_calls.list_for_job(job_id)
    assert [(item["stepId"], item["toolId"]) for item in calls] == [
        ("step_diffusion", "trajectory.diffusion")
    ]
    assert not any(item["toolId"] == "trajectory.msd" for item in calls)
    produced = repos.artifacts.list_for_job(job_id)
    assert len(produced) == 1
    payload = runtime.artifact_storage.get_json(produced[0]["storageKey"])
    assert payload["sourceMsd"]["artifactId"] == artifact_id
    assert payload["runtimeDiagnostics"]["msdRecomputation"] is False
