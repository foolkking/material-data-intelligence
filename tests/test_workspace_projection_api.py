from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from mdi_api.main import create_app
from mdi_api.repositories import InMemoryRepositoryBundle, compute_plan_hash
from mdi_api.routers import planner
from mdi_api.workspaces import WorkspaceDomainError, WorkspaceProjectionService
from mdi_api.application.workspaces.projection import (
    WorkspaceProjectionService as CanonicalWorkspaceProjectionService,
)
from mdi_api.domain.workspaces import (
    WorkspaceDomainError as CanonicalWorkspaceDomainError,
)
from mdi_llm import DeterministicAnalysisIntentBuilder, MockLLMProvider, plan_capabilities
from mdi_tool_registry import load_manifests
from mdi_schemas.workspace import workspace_semantic_hash

from tests.test_analysis_intent import _profile, _request


def test_legacy_workspace_exports_preserve_canonical_identity() -> None:
    assert WorkspaceProjectionService is CanonicalWorkspaceProjectionService
    assert WorkspaceDomainError is CanonicalWorkspaceDomainError


def _seed_modern(repos: InMemoryRepositoryBundle, *, job_id: str = "job_m1") -> None:
    resources = [
        {
            "objectId": "phonon_band_1",
            "objectType": "PhononBand",
            "objectHash": "b" * 64,
            "kind": "phonon",
            "capabilities": ["phonon"],
        },
        {
            "objectId": "phonon_dos_1",
            "objectType": "PhononDos",
            "objectHash": "c" * 64,
            "kind": "phonon",
            "capabilities": ["phonon"],
        },
    ]
    profile = _profile(resources=resources)
    intent = DeterministicAnalysisIntentBuilder().build(
        _request(
            "Create a combined phonon band and density of states product.",
            selected_resource_ids=("phonon_band_1", "phonon_dos_1"),
        ),
        profile=profile,
    )
    capability = plan_capabilities(
        intent,
        profile=profile,
        registry=load_manifests(),
        provider=MockLLMProvider(),
    )
    assert capability.plan is not None and capability.plan.schemaVersion == "0.2"
    plan_id = f"plan_{job_id}"
    plan_hash = compute_plan_hash(capability.plan)

    repos.projects.save(
        {"projectId": "project_1", "name": "Project", "createdBy": "user_local"}
    )
    repos.datasets.save(
        {
            "datasetId": profile.datasetId,
            "projectId": "project_1",
            "name": "Phonons",
            "createdBy": "user_local",
        }
    )
    repos.data_profiles.save(profile)
    repos.analysis_intents.save_intent(
        {
            "projectId": "project_1",
            "analysisIntent": intent.model_dump(mode="json"),
            "createdBy": "user_local",
        }
    )
    repos.capability_planning.save_resolution(
        {
            "eligibilityResolution": capability.resolution.model_dump(mode="json"),
            "createdBy": "user_local",
        }
    )
    repos.capability_planning.save_decision(
        {
            "capabilityDecision": capability.decision.model_dump(mode="json"),
            "createdBy": "user_local",
        }
    )
    repos.analysis_plans.save_plan(
        {
            "id": plan_id,
            "projectId": "project_1",
            "datasetId": profile.datasetId,
            "profileId": profile.profileId,
            "analysisPlan": capability.plan.model_dump(mode="json"),
            "planHash": plan_hash,
            "planSource": "capability_planner",
            "createdBy": "user_local",
        }
    )
    repos.jobs.save(
        {
            "id": job_id,
            "projectId": "project_1",
            "datasetId": profile.datasetId,
            "planId": plan_id,
            "status": "completed",
            "createdBy": "user_local",
        }
    )
    repos.analysis_intents.attach_execution(intent.intentId, plan_id, job_id)
    repos.capability_planning.attach_execution(
        capability.decision.decisionId,
        intent.intentId,
        plan_id,
        job_id,
    )


def _seed_legacy(repos: InMemoryRepositoryBundle, *, job_id: str = "job_legacy") -> None:
    repos.projects.save(
        {"projectId": "project_1", "name": "Project", "createdBy": "user_local"}
    )
    repos.datasets.save(
        {
            "datasetId": "dataset_1",
            "projectId": "project_1",
            "name": "Legacy",
            "createdBy": "user_local",
        }
    )
    repos.jobs.save(
        {
            "id": job_id,
            "projectId": "project_1",
            "datasetId": "dataset_1",
            "status": "completed",
            "createdBy": "user_local",
        }
    )


def test_modern_projection_is_exact_idempotent_and_metadata_only() -> None:
    repos = InMemoryRepositoryBundle.create()
    _seed_modern(repos)
    repos.artifacts.save(
        {
            "id": "artifact_1",
            "projectId": "project_1",
            "datasetId": "dataset_1",
            "jobId": "job_m1",
            "toolCallId": "call_1",
            "type": "phonon_band_json",
            "name": "ignored-name.json",
            "storageKey": "private/object/store/key",
            "sizeBytes": 12,
            "contentType": "application/json",
            "contentHash": "d" * 64,
            "sha256": "d" * 64,
            "metadata": {"provenance": {}, "rawPayload": "must-not-copy"},
        }
    )
    service = WorkspaceProjectionService(repos)

    first, created = service.project_job(
        source_job_id="job_m1", created_by="user_local", title="Phonon workspace"
    )
    second, replay_created = service.project_job(
        source_job_id="job_m1", created_by="user_local", title="Phonon workspace"
    )

    workspace = first.body["workspace"]
    serialized = json.dumps(first.body, sort_keys=True)
    assert created is True and replay_created is False
    assert workspace["projectedStatus"] == "COMPLETE"
    assert workspace["readOnly"] is False
    assert workspace["planSchemaVersion"] == "0.2"
    assert workspace["datasetVersion"] == "dataset_version_2"
    assert first.etag == second.etag
    assert len(repos.workspaces.list_by_project("project_1")) == 1
    assert "artifact_1" not in serialized
    assert len(repos.artifacts.list_for_job("job_m1")) == 1
    assert "private/object/store/key" not in serialized
    assert "must-not-copy" not in serialized
    panels = first.body["panels"]
    overview = next(item for item in panels if item["panelKind"] == "OVERVIEW")
    result_panel = next(item for item in panels if item["panelKind"] == "SCIENTIFIC_RESULT")
    assert result_panel["title"] == "Scientific results"
    assert not any(ref["kind"] == "ARTIFACT" for ref in result_panel["sourceRefs"])
    assert len(overview["acceptedSelectionKinds"]) == 20
    assert overview["emittedSelectionKinds"] == []
    assert result_panel["emittedSelectionKinds"] == [
        "DATASET_SAMPLE",
        "MATERIAL_OBJECT",
        "ARTIFACT",
        "LOCAL_ENVIRONMENT",
        "COORDINATION_POLYHEDRON",
        "POLYHEDRON_VERTEX",
        "POLYHEDRON_FACE",
        "EXPERIMENTAL_XRD_PEAK",
        "THEORETICAL_XRD_PEAK",
        "XRD_MATCH",
    ]
    assert result_panel["acceptedSelectionKinds"] == [
        "DATASET_SAMPLE",
        "MATERIAL_OBJECT",
        "STRUCTURE",
        "PERIODIC_SITE",
        "TRAJECTORY_ATOM",
        "TRAJECTORY_FRAME",
        "LOCAL_ENVIRONMENT",
        "COORDINATION_POLYHEDRON",
        "POLYHEDRON_VERTEX",
        "POLYHEDRON_FACE",
        "EXPERIMENTAL_XRD_PEAK",
        "THEORETICAL_XRD_PEAK",
        "XRD_MATCH",
        "PHONON_Q_POINT",
        "PHONON_BRANCH",
        "RECIPROCAL_POINT",
        "VOLUMETRIC_FIELD",
        "ARTIFACT",
    ]

    with pytest.raises(WorkspaceDomainError) as conflict:
        service.project_job(
            source_job_id="job_m1",
            created_by="user_local",
            title="Conflicting title",
        )
    assert conflict.value.code == "WORKSPACE_CREATE_CONFLICT"


def test_many_artifacts_project_to_one_exact_job_results_surface() -> None:
    repos = InMemoryRepositoryBundle.create()
    _seed_modern(repos)
    for index in range(40):
        checksum = f"{index:064x}"
        repos.artifacts.save(
            {
                "id": f"artifact_{index:02d}",
                "projectId": "project_1",
                "datasetId": "dataset_1",
                "jobId": "job_m1",
                "toolCallId": f"call_{index:02d}",
                "type": "phonon_band_json" if index % 2 == 0 else "table_json",
                "version": "1.0",
                "name": f"display-{39 - index}.json",
                "storageKey": f"private/{index}",
                "sizeBytes": 12,
                "contentType": "application/json",
                "contentHash": checksum,
                "sha256": checksum,
                "metadata": {"provenance": {}},
            }
        )

    first, created = WorkspaceProjectionService(repos).project_job(
        source_job_id="job_m1", created_by="user_local"
    )
    assert created is True
    result_panels = [
        item for item in first.body["panels"]
        if item["panelKind"] == "SCIENTIFIC_RESULT"
    ]
    assert len(result_panels) == 1
    assert len(first.body["panels"]) == 7
    assert len(repos.artifacts.list_for_job("job_m1")) == 40
    assert result_panels[0]["rendererContract"] == "workspace.artifact-metadata/1.0"
    assert [ref["kind"] for ref in result_panels[0]["sourceRefs"]].count("JOB") == 1

    replay, replay_created = WorkspaceProjectionService(repos).project_job(
        source_job_id="job_m1", created_by="user_local"
    )
    assert replay_created is False
    assert replay.body["workspace"]["workspaceId"] == first.body["workspace"]["workspaceId"]
    assert replay.body["workspace"]["panelIds"] == first.body["workspace"]["panelIds"]


def test_historical_empty_panel_declarations_are_read_projected_without_write() -> None:
    repos = InMemoryRepositoryBundle.create()
    _seed_modern(repos)
    repos.artifacts.save(
        {
            "id": "artifact_historical",
            "projectId": "project_1",
            "datasetId": "dataset_1",
            "jobId": "job_m1",
            "toolCallId": "call_historical",
            "type": "phonon_band_json",
            "name": "phonon_band.json",
            "storageKey": "artifact/historical",
            "sizeBytes": 12,
            "contentType": "application/json",
            "contentHash": "e" * 64,
            "sha256": "e" * 64,
            "metadata": {"provenance": {}},
        }
    )
    service = WorkspaceProjectionService(repos)
    created, _ = service.project_job(source_job_id="job_m1", created_by="user_local")
    workspace_id = created.body["workspace"]["workspaceId"]
    result = next(item for item in created.body["panels"] if item["panelKind"] == "SCIENTIFIC_RESULT")

    historical = {**result, "acceptedSelectionKinds": [], "emittedSelectionKinds": [], "contractProvenance": "phase10m1.workspace_projection.v1"}
    historical["panelStateHash"] = workspace_semantic_hash({key: value for key, value in historical.items() if key != "panelStateHash"})
    row = repos.workspaces.panels[(workspace_id, result["panelId"])]
    row["accepted_selection_kinds_json"] = []
    row["source_refs_json"]["emittedSelectionKinds"] = []
    row["source_refs_json"]["contractProvenance"] = historical["contractProvenance"]
    row["panel_state_hash"] = historical["panelStateHash"]

    projected = service.get_snapshot(workspace_id)
    projected_result = next(item for item in projected.body["panels"] if item["panelKind"] == "SCIENTIFIC_RESULT")
    assert projected_result["emittedSelectionKinds"] == [
        "DATASET_SAMPLE",
        "MATERIAL_OBJECT",
        "ARTIFACT",
        "LOCAL_ENVIRONMENT",
        "COORDINATION_POLYHEDRON",
        "POLYHEDRON_VERTEX",
        "POLYHEDRON_FACE",
        "EXPERIMENTAL_XRD_PEAK",
        "THEORETICAL_XRD_PEAK",
        "XRD_MATCH",
    ]
    assert projected_result["contractProvenance"] == "phase10m3.selection_registry.v1"
    persisted = repos.workspaces.get_panel(workspace_id, result["panelId"], project_id="project_1")
    assert persisted["acceptedSelectionKinds"] == []
    assert persisted["emittedSelectionKinds"] == []
    assert persisted["contractProvenance"] == "phase10m1.workspace_projection.v1"


def test_projection_states_cover_legacy_partial_stale_and_missing_sources() -> None:
    legacy = InMemoryRepositoryBundle.create()
    _seed_legacy(legacy)
    service = WorkspaceProjectionService(legacy)
    snapshot, _ = service.project_job(source_job_id="job_legacy", created_by="user_local")
    assert snapshot.body["workspace"]["projectedStatus"] == "LEGACY_READ_ONLY"
    assert snapshot.body["workspace"]["readOnly"] is True

    modern = InMemoryRepositoryBundle.create()
    _seed_modern(modern)
    modern.jobs.records["job_m1"]["status"] = "partial_success"
    partial, _ = WorkspaceProjectionService(modern).project_job(
        source_job_id="job_m1", created_by="user_local"
    )
    assert partial.body["workspace"]["projectedStatus"] == "PARTIAL_RESULTS"

    modern.data_profiles.records["profile_1"]["datasetId"] = "dataset_foreign"
    stale = WorkspaceProjectionService(modern).get_snapshot(
        partial.body["workspace"]["workspaceId"]
    )
    assert stale.body["workspace"]["projectedStatus"] == "STALE"
    assert stale.body["workspace"]["readOnly"] is True

    del modern.jobs.records["job_m1"]
    missing = WorkspaceProjectionService(modern).get_snapshot(
        partial.body["workspace"]["workspaceId"]
    )
    assert missing.body["workspace"]["projectedStatus"] == "SOURCE_MISSING"
    assert missing.body["workspace"]["readOnly"] is True


def test_projection_uses_profile_version_when_sample_identity_is_not_applicable() -> None:
    repos = InMemoryRepositoryBundle.create()
    _seed_modern(repos)
    profile = repos.data_profiles.records["profile_1"]
    profile["sampleIdentity"] = None
    profile["version"] = "2"
    resolution = next(iter(repos.capability_planning.resolutions.values()))
    resolution["eligibilityResolution"]["datasetVersion"] = "2"

    current, _ = WorkspaceProjectionService(repos).project_job(
        source_job_id="job_m1", created_by="user_local"
    )
    assert current.body["workspace"]["projectedStatus"] == "COMPLETE"
    assert current.body["workspace"]["datasetVersion"] == "2"

    workspace_id = current.body["workspace"]["workspaceId"]
    stored = repos.workspaces.workspaces[workspace_id]
    stored["dataset_version"] = None
    stored["source_reference_hash"] = workspace_semantic_hash(
        {
            "schemaVersion": stored["schema_version"],
            "workspaceId": stored["workspace_id"],
            "projectId": stored["project_id"],
            "sourceJobId": stored["source_job_id"],
            "datasetId": stored["dataset_id"],
            "datasetVersion": None,
            "profileId": stored["profile_id"],
            "profileSemanticHash": stored["profile_semantic_hash"],
            "intentId": stored["intent_id"],
            "intentSemanticHash": stored["intent_semantic_hash"],
            "planId": stored["plan_id"],
            "planHash": stored["plan_hash"],
            "planSchemaVersion": stored["plan_schema_version"],
        }
    )
    stale_snapshot = WorkspaceProjectionService(repos).get_snapshot(workspace_id)
    assert stale_snapshot.body["workspace"]["projectedStatus"] == "STALE"
    assert stale_snapshot.body["workspace"]["warnings"][-1]["code"] == "WORKSPACE_SOURCE_IDENTITY_STALE"

    stored["dataset_version"] = "2"
    stored["source_reference_hash"] = current.body["workspace"]["sourceReferenceHash"]
    profile["version"] = "3"
    stale = WorkspaceProjectionService(repos).get_snapshot(
        workspace_id
    )
    assert stale.body["workspace"]["projectedStatus"] == "STALE"
    assert stale.body["workspace"]["readOnly"] is True


def test_job_list_and_workspace_get_never_create_hidden_projection() -> None:
    repos = InMemoryRepositoryBundle.create()
    _seed_legacy(repos)
    service = WorkspaceProjectionService(repos)

    jobs = service.list_analysis_jobs(project_id="project_1", limit=10, cursor=None)
    assert jobs["items"][0]["workspaceExists"] is False
    assert repos.workspaces.list_by_project("project_1") == []
    with pytest.raises(WorkspaceDomainError) as missing:
        service.get_snapshot("workspace_missing")
    assert missing.value.code == "WORKSPACE_NOT_FOUND"
    assert repos.workspaces.list_by_project("project_1") == []


def test_global_task_feed_is_bounded_and_stably_ordered() -> None:
    repos = InMemoryRepositoryBundle.create()
    _seed_legacy(repos, job_id="job_a")
    repos.jobs.records["job_a"]["createdAt"] = "2026-09-01T00:00:00Z"
    repos.jobs.records["job_a"]["updatedAt"] = "2026-09-01T00:00:00Z"
    for job_id in ("job_b", "job_c"):
        repos.jobs.save(
            {
                "id": job_id,
                "projectId": "project_1",
                "datasetId": "dataset_1",
                "status": "completed",
                "createdBy": "user_local",
                "createdAt": "2026-09-01T00:00:00Z",
                "updatedAt": "2026-09-01T00:00:00Z",
            }
        )
    service = WorkspaceProjectionService(repos)
    projects = (
        {
            "id": "project_1",
            "projectId": "project_1",
            "name": "Project",
            "role": "owner",
            "status": "active",
        },
    )

    first = service.list_task_feed(projects=projects, limit=1, cursor=None)
    assert [item["jobId"] for item in first["items"]] == ["job_c"]
    assert len(first["nextCursor"]) == 64
    assert first["truncated"] is True
    assert first["projectCount"] == 1

    second = service.list_task_feed(
        projects=projects,
        limit=1,
        cursor=first["nextCursor"],
    )
    assert [item["jobId"] for item in second["items"]] == ["job_b"]
    assert len(second["nextCursor"]) == 64
    assert second["nextCursor"] != first["nextCursor"]
    with pytest.raises(WorkspaceDomainError) as invalid:
        service.list_task_feed(projects=projects, limit=1, cursor="missing")
    assert invalid.value.code == "CURSOR_INVALID"


def test_modern_identity_chain_and_unsupported_artifact_are_projected_safely() -> None:
    incomplete = InMemoryRepositoryBundle.create()
    _seed_modern(incomplete)
    incomplete.capability_planning.executions.clear()
    legacy, _ = WorkspaceProjectionService(incomplete).project_job(
        source_job_id="job_m1", created_by="user_local"
    )
    assert legacy.body["workspace"]["projectedStatus"] == "LEGACY_READ_ONLY"
    assert legacy.body["workspace"]["readOnly"] is True

    tampered = InMemoryRepositoryBundle.create()
    _seed_modern(tampered)
    decision = next(iter(tampered.capability_planning.decisions.values()))
    decision["capabilityDecision"]["resolutionHash"] = "e" * 64
    stale, _ = WorkspaceProjectionService(tampered).project_job(
        source_job_id="job_m1", created_by="user_local"
    )
    assert stale.body["workspace"]["projectedStatus"] == "STALE"
    assert stale.body["workspace"]["readOnly"] is True

    html = InMemoryRepositoryBundle.create()
    _seed_modern(html)
    html.artifacts.save(
        {
            "id": "artifact_html",
            "projectId": "project_1",
            "datasetId": "dataset_1",
            "jobId": "job_m1",
            "toolCallId": "call_html",
            "type": "report_html",
            "name": "untrusted.html",
            "storageKey": "private/html/object",
            "sizeBytes": 32,
            "contentType": "text/html",
            "contentHash": "f" * 64,
            "sha256": "f" * 64,
            "metadata": {"provenance": {}},
        }
    )
    inert, _ = WorkspaceProjectionService(html).project_job(
        source_job_id="job_m1", created_by="user_local"
    )
    panel = next(
        item for item in inert.body["panels"] if item["panelKind"] == "SCIENTIFIC_RESULT"
    )
    assert panel["state"] == "CONTRACT_UNSUPPORTED"
    assert panel["rendererContract"] == "workspace.inert-fallback/1.0"
    serialized = json.dumps(inert.body, sort_keys=True)
    assert "private/html/object" not in serialized
    assert "<html" not in serialized.lower()


@pytest.fixture
def workspace_api() -> tuple[TestClient, InMemoryRepositoryBundle]:
    planner.reset_planner_runtime()
    repos = planner._IN_MEMORY_REPOSITORIES
    _seed_modern(repos)
    client = TestClient(create_app())
    try:
        yield client, repos
    finally:
        client.close()
        planner.reset_planner_runtime()


def test_workspace_api_create_get_patch_panels_history_and_concurrency(
    workspace_api: tuple[TestClient, InMemoryRepositoryBundle],
) -> None:
    client, repos = workspace_api
    assert client.get("/projects/project_1/analysis-jobs").status_code == 200
    assert repos.workspaces.list_by_project("project_1") == []

    created = client.post(
        "/workspaces",
        headers={"Idempotency-Key": "workspace-create-1"},
        json={"sourceJobId": "job_m1", "title": "Initial title"},
    )
    assert created.status_code == 201
    workspace_id = created.json()["workspace"]["workspaceId"]
    etag = created.headers["etag"]
    replay = client.post(
        "/workspaces",
        headers={"Idempotency-Key": "workspace-create-1"},
        json={"sourceJobId": "job_m1", "title": "Initial title"},
    )
    assert replay.status_code == 200
    assert replay.headers["x-idempotent-replay"] == "true"
    assert replay.json()["workspace"]["workspaceId"] == workspace_id

    unchanged = client.get(
        f"/workspaces/{workspace_id}", headers={"If-None-Match": etag}
    )
    assert unchanged.status_code == 304
    patched = client.patch(
        f"/workspaces/{workspace_id}",
        headers={"If-Match": etag},
        json={"title": "Updated title"},
    )
    assert patched.status_code == 200
    assert patched.json()["workspace"]["revision"] == 1
    assert patched.json()["workspace"]["title"] == "Updated title"
    assert client.patch(
        f"/workspaces/{workspace_id}",
        headers={"If-Match": etag},
        json={"title": "Stale write"},
    ).status_code == 412
    panels = client.get(f"/workspaces/{workspace_id}/panels")
    history = client.get(f"/workspaces/{workspace_id}/layout-revisions")
    exact = client.get(f"/workspaces/{workspace_id}/layout-revisions/1")
    assert panels.status_code == history.status_code == exact.status_code == 200
    assert len(panels.json()["items"]) == len(created.json()["panels"])
    assert [item["revision"] for item in history.json()["items"]] == [0, 1]
    assert exact.json()["revision"] == 1


def test_global_task_feed_api_is_authorized_paginated_and_cross_project_safe(
    workspace_api: tuple[TestClient, InMemoryRepositoryBundle],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from mdi_api.routers import secured_runtime

    client, repos = workspace_api
    repos.projects.save(
        {
            "projectId": "project_hidden",
            "name": "Hidden",
            "createdBy": "another_user",
        }
    )
    repos.jobs.save(
        {
            "id": "job_hidden",
            "projectId": "project_hidden",
            "datasetId": "dataset_hidden",
            "status": "completed",
            "createdBy": "another_user",
        }
    )
    repos.jobs.save(
        {
            "id": "job_second",
            "projectId": "project_1",
            "datasetId": "dataset_1",
            "status": "completed",
            "createdBy": "user_local",
        }
    )
    monkeypatch.setattr(
        secured_runtime,
        "list_projects_secured",
        lambda _current_user: [
            {
                "id": "project_1",
                "projectId": "project_1",
                "name": "Project",
                "role": "owner",
                "status": "active",
            }
        ],
    )

    first = client.get("/api/tasks/feed", params={"limit": 1})
    assert first.status_code == 200
    payload = first.json()
    assert payload["schemaVersion"] == "ProductTaskFeed/1.0"
    assert payload["projectCount"] == 1
    assert payload["truncated"] is True
    assert len(payload["items"]) == 1
    assert len(payload["nextCursor"]) == 64
    assert payload["items"][0]["projectId"] == "project_1"
    assert payload["items"][0]["projectName"] == "Project"
    assert payload["items"][0]["jobId"] != "job_hidden"

    second = client.get(
        "/api/tasks/feed",
        params={"limit": 1, "cursor": payload["nextCursor"]},
    )
    assert second.status_code == 200
    assert second.json()["items"][0]["projectId"] == "project_1"
    assert second.json()["items"][0]["jobId"] != payload["items"][0]["jobId"]
    assert client.get(
        "/api/tasks/feed",
        params={"limit": 1, "cursor": "missing"},
    ).status_code == 400


def test_workspace_api_rejects_unsafe_conflicts_and_cross_project_access(
    workspace_api: tuple[TestClient, InMemoryRepositoryBundle],
) -> None:
    client, repos = workspace_api
    assert client.get("/workspaces/workspace_missing").status_code == 404
    assert client.post("/workspaces", json={"sourceJobId": "job_m1"}).status_code == 400
    duplicate = client.post(
        "/workspaces",
        headers={
            "Idempotency-Key": "duplicate-json",
            "Content-Type": "application/json",
        },
        content='{"sourceJobId":"job_m1","sourceJobId":"job_m1"}',
    )
    assert duplicate.status_code == 400
    unsafe = client.post(
        "/workspaces",
        headers={"Idempotency-Key": "unsafe-title"},
        json={"sourceJobId": "job_m1", "title": "<script>alert(1)</script>"},
    )
    assert unsafe.status_code == 422

    created = client.post(
        "/workspaces",
        headers={"Idempotency-Key": "workspace-create-2"},
        json={"sourceJobId": "job_m1"},
    )
    workspace_id = created.json()["workspace"]["workspaceId"]
    immutable = client.patch(
        f"/workspaces/{workspace_id}",
        headers={"If-Match": created.headers["etag"]},
        json={"sourceJobId": "job_other"},
    )
    assert immutable.status_code == 422
    malformed = client.patch(
        f"/workspaces/{workspace_id}",
        headers={"If-Match": "not-an-etag"},
        json={"title": "No"},
    )
    assert malformed.status_code == 400

    repos.projects.save(
        {"projectId": "project_foreign", "name": "Other", "createdBy": "other_user"}
    )
    repos.jobs.save(
        {
            "id": "job_foreign",
            "projectId": "project_foreign",
            "status": "completed",
            "createdBy": "other_user",
        }
    )
    foreign = client.post(
        "/workspaces",
        headers={"Idempotency-Key": "foreign-job"},
        json={"sourceJobId": "job_foreign"},
    )
    assert foreign.status_code == 403
    assert "Traceback" not in foreign.text and "E:\\" not in foreign.text


def test_grounded_evidence_projection_preserves_exact_bundle_and_artifact_refs(
    tmp_path,
) -> None:
    from mdi_api.routers.planner import (
        PlannerInterpretationRequest,
        create_planner_job_interpretation,
    )
    from tests.test_api_persistence import _seed_api_source

    repos, runtime, plan_hash = _seed_api_source(tmp_path / "m4-evidence")
    created = create_planner_job_interpretation(
        "job_l4_api",
        PlannerInterpretationRequest(
            mode="DETERMINISTIC",
            expectedPlanHash=plan_hash,
            idempotencyKey="m4-workspace-evidence",
        ),
        repositories=repos,
        queue_runtime=runtime,
    )
    assert created["outcome"] == "INTERPRETATION_READY"
    repos.projects.save(
        {"projectId": "project_l4_api", "name": "L4 source", "createdBy": "user_local"}
    )
    repos.datasets.save(
        {
            "datasetId": "dataset_l4_api",
            "projectId": "project_l4_api",
            "name": "L4 dataset",
            "createdBy": "user_local",
        }
    )

    snapshot, projected = WorkspaceProjectionService(repos).project_job(
        source_job_id="job_l4_api",
        created_by="user_local",
        title="Grounded evidence workspace",
    )

    assert projected is True
    evidence_panel = next(
        panel for panel in snapshot.body["panels"] if panel["panelKind"] == "EVIDENCE"
    )
    findings_panel = next(
        panel for panel in snapshot.body["panels"] if panel["panelKind"] == "FINDINGS"
    )
    bundle_refs = [
        ref for ref in evidence_panel["sourceRefs"] if ref["kind"] == "EVIDENCE_BUNDLE"
    ]
    artifact_refs = [
        ref for ref in evidence_panel["sourceRefs"] if ref["kind"] == "ARTIFACT"
    ]
    assert len(bundle_refs) == 1
    assert bundle_refs[0]["sourceId"] == created["bundleId"]
    assert bundle_refs[0]["sourceHash"] == created["bundleHash"]
    assert bundle_refs[0]["projectId"] == "project_l4_api"
    assert bundle_refs[0]["jobId"] == "job_l4_api"
    assert artifact_refs
    assert all(ref["sourceHash"] and ref["jobId"] == "job_l4_api" for ref in artifact_refs)
    assert findings_panel["evidenceRefs"] == [created["bundleId"]]
    assert evidence_panel["evidenceRefs"] == [created["bundleId"]]
    assert set(evidence_panel["provenanceRefs"]) == {ref["sourceId"] for ref in artifact_refs}
    serialized = json.dumps(snapshot.body, sort_keys=True)
    assert "storageKey" not in serialized and "rawPayload" not in serialized
