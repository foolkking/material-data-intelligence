from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from mdi_api.main import create_app
from mdi_api.repositories import InMemoryRepositoryBundle, compute_plan_hash
from mdi_api.routers import planner
from mdi_api.workspaces import WorkspaceDomainError, WorkspaceProjectionService
from mdi_llm import DeterministicAnalysisIntentBuilder, MockLLMProvider, plan_capabilities
from mdi_tool_registry import load_manifests

from tests.test_phase10l1_analysis_intent import _profile, _request


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
    assert "artifact_1" in serialized
    assert "private/object/store/key" not in serialized
    assert "must-not-copy" not in serialized

    with pytest.raises(WorkspaceDomainError) as conflict:
        service.project_job(
            source_job_id="job_m1",
            created_by="user_local",
            title="Conflicting title",
        )
    assert conflict.value.code == "WORKSPACE_CREATE_CONFLICT"


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
