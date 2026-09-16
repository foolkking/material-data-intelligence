from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
from types import SimpleNamespace
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert
from sqlalchemy.pool import StaticPool

from mdi_api.db import metadata, organizations, project_members, projects, sessions, users
from mdi_api.agent2_errors import ScientificResultSnapshotNotFound
from mdi_api.artifact_storage import LocalFileArtifactStorage
from mdi_api.main import create_app
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor
from mdi_api.research_agent.registry_validation import build_default_agent2_registries
from mdi_api.routers.agent2 import (
    _http_error,
    _research_progress_response_kind,
    research_turn_correlation_payload,
)
from mdi_api.routers.auth import CurrentUser, get_current_user
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.schemas import (
    ScientificObjectKind,
    ScientificObjectRef,
    StorageRef,
)
from mdi_api.scientific_objects.service import ScientificObjectService
from mdi_api.scientific_results.schemas import ScientificResultBundle
from mdi_api.unit_of_work import RepositoryFactory


@pytest.fixture
def api(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    owner = CurrentUser(id="owner", email="owner@example.invalid", displayName="Owner", roles=[])
    viewer = CurrentUser(id="viewer", email="viewer@example.invalid", displayName="Viewer", roles=[])
    stranger = CurrentUser(id="stranger", email="stranger@example.invalid", displayName="Stranger", roles=[])
    with engine.begin() as connection:
        connection.execute(insert(users), [
            {"id": item.id, "email": item.email, "display_name": item.displayName, "is_active": True}
            for item in (owner, viewer, stranger)
        ])
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(insert(projects), [
            {"id": "project", "organization_id": "org", "name": "Project", "created_by": owner.id},
            {"id": "other", "organization_id": "org", "name": "Other", "created_by": owner.id},
        ])
        connection.execute(insert(project_members), {"project_id": "project", "user_id": viewer.id, "role": "viewer"})
        connection.execute(insert(sessions), [
            {"id": "session", "project_id": "project", "mode": "project", "status": "active", "created_by": owner.id},
            {"id": "other-session", "project_id": "other", "mode": "project", "status": "active", "created_by": owner.id},
        ])
    factory = RepositoryFactory(engine)
    turn_service = ResearchTurnService(factory)
    object_service = ScientificObjectService(factory, build_default_object_type_registry())
    monkeypatch.setattr("mdi_api.routers.agent2.get_research_turn_service", lambda: turn_service)
    monkeypatch.setattr("mdi_api.routers.agent2.get_scientific_object_service", lambda: object_service)
    monkeypatch.setattr("mdi_api.routers.agent2.create_repository_factory", lambda: factory)
    monkeypatch.setattr(
        "mdi_api.routers.scientific_reports.create_repository_factory",
        lambda: factory,
    )
    monkeypatch.setattr(
        "mdi_api.routers.project_history.create_engine_from_settings",
        lambda _settings: engine,
    )
    app = create_app()
    active_user = {"value": owner}
    app.dependency_overrides[get_current_user] = lambda: active_user["value"]
    return TestClient(app), active_user, owner, viewer, stranger, object_service


def create_ref(service: ScientificObjectService, project_id: str) -> ScientificObjectRef:
    logical = service.create_object(
        project_id=project_id, kind=ScientificObjectKind.STRUCTURE,
        object_type="structure.crystal", display_name=f"Structure {project_id}", created_by_user_id="owner",
    )
    version = service.create_version(
        logical["id"], object_type="structure.crystal", object_schema_version="1.0",
        source_resource_refs=[{"scope": "system_fixture", "resource_id": project_id}],
        parent_object_version_refs=[],
        normalized_payload_ref=StorageRef(storage_backend="minio", object_key=f"{project_id}.json", checksum="abc"),
        content_hash=f"content-{project_id}", semantic_hash=f"semantic-{project_id}", canonical_metadata={},
        created_by_user_id="owner",
    )
    return ScientificObjectRef(
        object_id=logical["id"], version_id=version["id"], project_id=project_id,
        object_type="structure.crystal", display_name=logical["display_name"],
    )


def test_missing_result_reference_is_normalized_to_not_found() -> None:
    error = _http_error(ScientificResultSnapshotNotFound("missing-result"))
    assert error.status_code == 404
    assert error.detail == "请求的 Agent 2.0 资源不存在。"


def test_create_get_list_and_cancel_turn(api):
    client, _active, _owner, _viewer, _stranger, _objects = api
    created = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={"message": "Inspect the current structure"},
    )
    assert created.status_code == 202
    payload = created.json()
    assert payload["status"] == "RECEIVED"
    assert payload["user_message"] == {
        "id": payload["user_message"]["id"], "role": "USER", "content": "Inspect the current structure",
    }
    turn_id = payload["turn_id"]
    detail = client.get(f"/api/research/turns/{turn_id}")
    assert detail.status_code == 200
    assert detail.json()["messages"][0]["role"] == "USER"
    assert detail.json()["action"] is None and detail.json()["result_available"] is False
    listed = client.get("/api/projects/project/research/sessions/session/turns?limit=10")
    assert [item["sequence_no"] for item in listed.json()["items"]] == [1]
    canceled = client.post(f"/api/research/turns/{turn_id}/cancel")
    assert canceled.status_code == 200 and canceled.json()["status"] == "CANCELED"
    terminal = client.post(f"/api/research/turns/{turn_id}/cancel")
    assert terminal.status_code == 409 and terminal.json()["detail"]["code"] == "TURN_TERMINAL"


def test_research_turn_correlation_is_bounded_authorized_and_secret_free(api):
    client, active, _owner, _viewer, stranger, _objects = api
    created = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={"message": "Trace the persisted research lineage"},
    )
    turn_id = created.json()["turn_id"]

    empty = client.get(f"/api/research/turns/{turn_id}/correlation")
    assert empty.status_code == 200
    payload = empty.json()
    assert {key: value for key, value in payload.items() if key != "lifecycle"} == {
        "contract_version": "1.0",
        "project_id": "project",
        "research_session_id": "session",
        "research_turn_id": turn_id,
        "job": None,
        "tool_calls": [],
        "tool_calls_truncated": False,
        "scientific_result": None,
        "report": None,
        "integrity_warnings": [],
    }
    assert payload["lifecycle"]["stage"]["name"] == "RECEIVED"
    assert payload["lifecycle"]["stage"]["owner"] == "orchestration"

    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/correlation").status_code == 403


def test_research_turn_correlation_projects_exact_bounded_lineage():
    turn_id = uuid4()
    result_snapshot_id = uuid4()
    result_id = uuid4()
    report_snapshot_id = uuid4()
    calls = [
        {
            "id": f"call-{index:02d}",
            "stepId": f"step-{index:02d}",
            "status": "completed",
            "params": {"secret": "must-not-leak"},
        }
        for index in range(65)
    ]

    class Jobs:
        @staticmethod
        def get(job_id):
            assert job_id == "job-exact"
            return {"id": job_id, "status": "completed", "createdBy": "internal"}

    class ToolCalls:
        @staticmethod
        def list_for_job(job_id):
            assert job_id == "job-exact"
            return calls

    class Results:
        @staticmethod
        def get_latest_for_turn(requested_turn_id):
            assert requested_turn_id == turn_id
            return {
                "id": result_snapshot_id,
                "project_id": "project",
                "research_turn_id": turn_id,
                "job_id": "job-exact",
                "execution_status": "SUCCESS",
                "bundle_json": {"result_id": str(result_id)},
            }

    class Reports:
        @staticmethod
        def get_for_turn(requested_turn_id):
            assert requested_turn_id == turn_id
            return {
                "id": report_snapshot_id,
                "report_id": "report-exact",
                "project_id": "project",
                "research_turn_id": turn_id,
                "scientific_result_snapshot_id": result_snapshot_id,
                "grounding_status": "VALID",
            }

    session = SimpleNamespace(
        repositories=SimpleNamespace(jobs=Jobs(), tool_calls=ToolCalls()),
        agent2=SimpleNamespace(
            scientific_result_snapshots=Results(),
            scientific_reports=Reports(),
        ),
    )
    payload = research_turn_correlation_payload(
        session,
        {
            "id": turn_id,
            "project_id": "project",
            "research_session_id": "session",
            "job_id": "job-exact",
        },
    )

    assert payload["research_turn_id"] == str(turn_id)
    assert payload["job"] == {"job_id": "job-exact", "status": "completed"}
    assert len(payload["tool_calls"]) == 64
    assert payload["tool_calls_truncated"] is True
    assert payload["tool_calls"][0] == {
        "tool_call_id": "call-00",
        "step_id": "step-00",
        "status": "completed",
    }
    assert payload["scientific_result"] == {
        "result_snapshot_id": str(result_snapshot_id),
        "result_id": str(result_id),
        "execution_status": "SUCCESS",
        "job_id": "job-exact",
    }
    assert payload["report"] == {
        "report_id": "report-exact",
        "report_snapshot_id": str(report_snapshot_id),
        "grounding_status": "VALID",
    }
    assert payload["integrity_warnings"] == []
    serialized = str(payload)
    assert "must-not-leak" not in serialized
    assert "storage_key" not in serialized
    assert "provider_request_id" not in serialized


def test_context_manifest_endpoint_returns_bounded_manifest_and_enforces_project_access(api):
    client, active, _owner, _viewer, stranger, objects = api
    created = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={"message": "Use the selected structure context"},
    )
    assert created.status_code == 202
    turn_id = UUID(created.json()["turn_id"])
    with objects.repository_factory.unit_of_work() as unit:
        unit.agent2.research_turn_events.append_turn_event({
            "id": uuid4(),
            "turn_id": turn_id,
            "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id),
            "event_type": "CONTEXT_RESOLVED",
            "payload_json": {
                "context_manifest": {
                    "manifest_id": "manifest-test",
                    "operation": "ORCHESTRATOR",
                    "project_id": "project",
                    "research_turn_id": str(turn_id),
                    "included_items": [{
                        "item_id": "item-1",
                        "kind": "SCIENTIFIC_SELECTION",
                        "authority_class": "SCIENTIFIC_DATA",
                        "server_side_source_identity": "scientific-object:project",
                        "provider_opaque_ref": "opaque:item-1",
                        "inclusion_reason": "explicit UI selection",
                        "selection_mode": "UI_SELECTION",
                        "authorization_checked": True,
                        "content_fingerprint": "f" * 64,
                        "estimated_tokens": 12,
                        "exact_object_id": "object-1",
                        "exact_object_version_id": "version-1",
                    }],
                    "excluded_items": [],
                    "estimated_input_tokens": 12,
                    "input_budget": 12000,
                    "reserved_output_tokens": 2000,
                    "repair_margin": 500,
                    "compaction_state": "NONE",
                    "truncation_state": "NONE",
                    "context_fingerprint": "c" * 64,
                    "created_at": "2026-08-28T00:00:00Z",
                },
            },
        })

    response = client.get(f"/api/research/turns/{turn_id}/context-manifest")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["turn_id"] == str(turn_id)
    assert payload["manifest"]["manifest_id"] == "manifest-test"
    assert payload["manifest"]["included_items"][0]["exact_object_version_id"] == "version-1"
    assert "provider_prompt" not in payload["manifest"]
    assert payload["manifests"][0]["operation"] == "ORCHESTRATOR"
    assert payload["manifests"][0]["manifest"]["manifest_id"] == "manifest-test"

    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/context-manifest").status_code == 403


def test_context_manifest_endpoint_projects_legacy_context_snapshot(api):
    client, _active, _owner, _viewer, _stranger, objects = api
    created = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={"message": "Reopen historical context"},
    )
    assert created.status_code == 202
    turn_id = UUID(created.json()["turn_id"])
    snapshot_id = uuid4()
    with objects.repository_factory.unit_of_work() as unit:
        unit.agent2.research_context_snapshots.add({
            "id": snapshot_id,
            "project_id": "project",
            "research_session_id": "session",
            "research_turn_id": turn_id,
            "snapshot_schema_version": "2.0",
            "active_scope_refs_json": [{
                "object_id": str(uuid4()),
                "version_id": str(uuid4()),
                "project_id": "project",
                "object_type": "materials.table",
                "display_name": "Dataset",
            }],
            "selection_refs_json": [],
            "scientific_selections_json": [{
                "object_ref": {
                    "object_id": str(uuid4()),
                    "version_id": str(uuid4()),
                    "project_id": "project",
                    "object_type": "materials.table",
                    "display_name": "Dataset",
                },
                "viewer_id": "materials.table",
                "selection_type": "DATASET_SAMPLE",
                "semantic_locator": {"sample_ref": "mat-2"},
                "display_label": "mat-2",
            }],
            "resolved_references_json": [],
            "referenced_result_refs_json": [str(uuid4())],
            "relevant_finding_refs_json": [],
            "effective_constraints_json": [{"name": "band_gap", "operator": ">", "value": 2}],
            "research_goal": "Inspect the selected sample",
            "unresolved_questions_json": [],
            "context_fingerprint": "a" * 64,
            "compiler_version": "legacy.context-compiler/1.0",
        })
        unit.agent2.research_turn_events.append_turn_event({
            "id": uuid4(),
            "turn_id": turn_id,
            "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id),
            "event_type": "CONTEXT_RESOLVED",
            "payload_json": {"status": "ORCHESTRATING", "context_snapshot_id": str(snapshot_id)},
        })

    response = client.get(f"/api/research/turns/{turn_id}/context-manifest")
    assert response.status_code == 200, response.text
    manifest = response.json()["manifest"]
    assert manifest["context_manifest_id"]
    assert manifest["policy_version"] == "agent2.context-compat/1.0"
    assert manifest["research_turn_id"] == str(turn_id)
    assert any(item["kind"] == "SCIENTIFIC_SELECTION" for item in manifest["included_items"])
    assert any(item["kind"] == "USER_CONSTRAINT" for item in manifest["included_items"])
    assert any(item["kind"] == "RESEARCH_GOAL" for item in manifest["included_items"])
    assert all("provider_prompt" not in item for item in manifest["included_items"])


def test_concurrent_create_turn_api_allocates_unique_ordered_sequences(api):
    client, _active, _owner, _viewer, _stranger, _objects = api

    def create(index: int):
        return client.post(
            "/api/projects/project/research/sessions/session/turns",
            json={"message": f"Concurrent question {index}"},
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        responses = list(pool.map(create, range(12)))
    assert all(response.status_code == 202 for response in responses)
    assert sorted(response.json()["sequence_no"] for response in responses) == list(range(1, 13))
    first_page = client.get("/api/projects/project/research/sessions/session/turns?limit=5").json()
    second_page = client.get(
        f"/api/projects/project/research/sessions/session/turns?limit=5&cursor={first_page['next_cursor']}"
    ).json()
    assert [item["sequence_no"] for item in first_page["items"]] == [1, 2, 3, 4, 5]
    assert [item["sequence_no"] for item in second_page["items"]] == [6, 7, 8, 9, 10]


def test_create_turn_rejects_empty_session_mismatch_and_read_only_user(api):
    client, active, owner, viewer, _stranger, _objects = api
    assert client.post("/api/projects/project/research/sessions/session/turns", json={"message": "  "}).status_code == 422
    assert client.post("/api/projects/project/research/sessions/other-session/turns", json={"message": "Wrong scope"}).status_code == 404
    active["value"] = viewer
    assert client.post("/api/projects/project/research/sessions/session/turns", json={"message": "Read only"}).status_code == 403
    active["value"] = owner


def test_ui_context_is_reauthorized_and_historical_version_is_not_upgraded(api):
    client, _active, _owner, _viewer, _stranger, objects = api
    ref = create_ref(objects, "project")
    accepted = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={"message": "Use this exact version", "ui_context": {"active_object_refs": [ref.model_dump(mode="json")], "selection_refs": []}},
    )
    assert accepted.status_code == 202
    outside = create_ref(objects, "other")
    rejected = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={"message": "Cross project", "ui_context": {"active_object_refs": [outside.model_dump(mode="json")], "selection_refs": []}},
    )
    assert rejected.status_code == 403


def test_get_turn_and_scientific_object_are_project_isolated(api):
    client, active, owner, viewer, stranger, objects = api
    turn = client.post("/api/projects/project/research/sessions/session/turns", json={"message": "Private"}).json()
    ref = create_ref(objects, "project")
    active["value"] = viewer
    assert client.get(f"/api/research/turns/{turn['turn_id']}").status_code == 200
    assert client.get(f"/api/scientific-objects/{ref.object_id}").status_code == 200
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn['turn_id']}").status_code == 403
    assert client.get(f"/api/scientific-objects/{ref.object_id}").status_code == 403
    assert client.get("/api/projects/project/scientific-objects").status_code == 403
    active["value"] = owner


def test_exact_turn_and_object_routes_fail_closed_for_foreign_user(api):
    """Exercise the high-value exact-id read/write boundaries as one matrix.

    Each request starts from a persisted project-owned Turn/Object.  The
    stranger must receive the same authorization denial before any route can
    disclose status, metadata, version content, or trigger a mutation.
    """
    client, active, owner, _viewer, stranger, objects = api
    turn = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={"message": "Authorization matrix"},
    ).json()
    ref = create_ref(objects, "project")
    turn_id = turn["turn_id"]
    object_id = str(ref.object_id)
    version_id = str(ref.version_id)

    route_cases = [
        ("get", f"/api/research/turns/{turn_id}"),
        ("get", f"/api/research/turns/{turn_id}/context-manifest"),
        ("get", f"/api/research/turns/{turn_id}/correlation"),
        ("post", f"/api/research/turns/{turn_id}/cancel"),
        ("post", f"/api/research/turns/{turn_id}/dispatch"),
        ("get", f"/api/research/turns/{turn_id}/progress"),
        ("get", f"/api/research/turns/{turn_id}/result"),
        ("post", f"/api/research/turns/{turn_id}/project-result"),
        ("post", f"/api/research/turns/{turn_id}/interpret"),
        ("get", f"/api/research/turns/{turn_id}/interpretation"),
        ("post", f"/api/research/turns/{turn_id}/report"),
        ("get", f"/api/research/turns/{turn_id}/report"),
        ("get", f"/api/research/turns/{turn_id}/report-status"),
        ("get", f"/api/research/turns/{turn_id}/events"),
        ("get", "/projects/project/history"),
        ("get", f"/api/scientific-objects/{object_id}"),
        ("get", f"/api/scientific-objects/{object_id}/dependency-impact"),
        ("patch", f"/api/scientific-objects/{object_id}", {"display_name": "泄漏"}),
        ("get", f"/api/scientific-objects/{object_id}/versions"),
        ("post", f"/api/scientific-objects/{object_id}/versions", {
            "dataset_id": "foreign-attempt",
            "resource_id": "foreign-attempt",
        }),
        ("get", f"/api/scientific-objects/{object_id}/versions/{version_id}"),
        ("post", f"/api/scientific-objects/{object_id}/versions/{version_id}/query", {
            "filters": [],
            "limit": 1,
        }),
        ("get", f"/api/scientific-objects/{object_id}/versions/{version_id}/viewer"),
        ("get", f"/api/scientific-objects/{object_id}/relationships"),
    ]

    active["value"] = stranger
    try:
        for case in route_cases:
            method, path, *payload = case
            kwargs = {"json": payload[0]} if payload else {}
            response = getattr(client, method)(path, **kwargs)
            assert response.status_code == 403, (
                f"{method.upper()} {path} leaked or bypassed authorization: "
                f"{response.status_code} {response.text}"
            )
            assert "泄漏" not in response.text
            assert turn_id not in response.text
            assert object_id not in response.text
            assert version_id not in response.text
    finally:
        active["value"] = owner


def test_scientific_object_read_api_lists_exact_versions_and_relationships(api):
    client, _active, _owner, _viewer, _stranger, objects = api
    left = create_ref(objects, "project")
    right = create_ref(objects, "project")
    objects.create_relationship(
        project_id="project", source_version_id=left.version_id,
        target_version_id=right.version_id, relation_type="companion_of",
    )
    listing = client.get("/api/projects/project/scientific-objects?kind=STRUCTURE&search=structure&limit=10")
    assert listing.status_code == 200 and len(listing.json()["items"]) == 2
    versions = client.get(f"/api/scientific-objects/{left.object_id}/versions")
    assert versions.status_code == 200 and versions.json()["items"][0]["id"] == str(left.version_id)
    exact = client.get(f"/api/scientific-objects/{left.object_id}/versions/{left.version_id}")
    assert exact.status_code == 200 and exact.json()["content_hash"] == "content-project"
    relationships = client.get(f"/api/scientific-objects/{left.object_id}/relationships")
    assert relationships.status_code == 200 and relationships.json()["items"][0]["relation_type"] == "companion_of"
    impact = client.get(f"/api/scientific-objects/{left.object_id}/dependency-impact")
    assert impact.status_code == 200
    assert impact.json()["entity"] == "scientific_object"
    assert impact.json()["impact"]["scientificSnapshotMutated"] is False
    assert {item["kind"] for item in impact.json()["dependencies"]} >= {
        "scientific_object_versions",
        "scientific_object_relationships",
    }
    assert all(
        item["href"]
        == f"/projects/project/data?object={left.object_id}"
        for item in impact.json()["dependencies"]
        if item["kind"]
        in {"scientific_object_versions", "scientific_object_relationships"}
    )


def test_scientific_object_metadata_update_is_authorized_and_version_stable(api):
    client, active, owner, viewer, _stranger, objects = api
    ref = create_ref(objects, "project")

    renamed = client.patch(
        f"/api/scientific-objects/{ref.object_id}",
        json={"display_name": "Renamed"},
    )
    assert renamed.status_code == 200
    assert renamed.json()["display_name"] == "Renamed"
    assert renamed.json()["current_version_id"] == str(ref.version_id)

    archived = client.patch(
        f"/api/scientific-objects/{ref.object_id}",
        json={"archived": True},
    )
    assert archived.status_code == 200
    assert archived.json()["lifecycle_status"] == "ARCHIVED"
    assert archived.json()["current_version_id"] == str(ref.version_id)

    active["value"] = viewer
    assert client.patch(
        f"/api/scientific-objects/{ref.object_id}",
        json={"display_name": "Unauthorized"},
    ).status_code == 403
    active["value"] = owner

    restored = client.patch(
        f"/api/scientific-objects/{ref.object_id}",
        json={"archived": False},
    )
    assert restored.status_code == 200
    assert restored.json()["lifecycle_status"] == "ACTIVE"
    assert restored.json()["archived_at"] is None
    assert client.get(f"/api/scientific-objects/{ref.object_id}/versions/{ref.version_id}").json()["content_hash"] == "content-project"

    trashed = client.patch(
        f"/api/scientific-objects/{ref.object_id}",
        json={"lifecycle": "TRASHED"},
    )
    assert trashed.status_code == 200
    assert trashed.json()["lifecycle_status"] == "TRASHED"
    assert trashed.json()["pre_trash_lifecycle_status"] == "ACTIVE"
    listing = client.get("/api/projects/project/scientific-objects?lifecycle_status=TRASHED")
    assert listing.status_code == 200
    assert any(item["id"] == str(ref.object_id) for item in listing.json()["items"])

    restored_from_trash = client.patch(
        f"/api/scientific-objects/{ref.object_id}",
        json={"lifecycle": "ACTIVE"},
    )
    assert restored_from_trash.status_code == 200
    assert restored_from_trash.json()["lifecycle_status"] == "ACTIVE"
    assert restored_from_trash.json()["pre_trash_lifecycle_status"] is None


def test_scientific_object_bulk_lifecycle_is_atomic_authorized_and_version_stable(api):
    client, active, owner, viewer, _stranger, objects = api
    left = create_ref(objects, "project")
    right = create_ref(objects, "project")

    archived = client.post(
        "/api/projects/project/scientific-objects/bulk",
        json={
            "object_ids": [str(left.object_id), str(right.object_id)],
            "lifecycle": "ARCHIVED",
        },
    )
    assert archived.status_code == 200
    assert archived.json()["count"] == 2
    assert {item["lifecycle_status"] for item in archived.json()["items"]} == {"ARCHIVED"}
    assert {item["current_version_id"] for item in archived.json()["items"]} == {
        str(left.version_id),
        str(right.version_id),
    }
    assert objects.list_versions(left.object_id)[0]["content_hash"] == "content-project"
    assert objects.list_versions(right.object_id)[0]["content_hash"] == "content-project"

    active["value"] = viewer
    assert client.post(
        "/api/projects/project/scientific-objects/bulk",
        json={"object_ids": [str(left.object_id)], "lifecycle": "ACTIVE"},
    ).status_code == 403
    active["value"] = owner

    outside = create_ref(objects, "other")
    rejected = client.post(
        "/api/projects/project/scientific-objects/bulk",
        json={
            "object_ids": [str(left.object_id), str(outside.object_id)],
            "lifecycle": "ACTIVE",
        },
    )
    assert rejected.status_code == 403
    assert objects.get_object(left.object_id)["lifecycle_status"] == "ARCHIVED"

    restored = client.post(
        "/api/projects/project/scientific-objects/bulk",
        json={
            "object_ids": [str(left.object_id), str(right.object_id)],
            "lifecycle": "ACTIVE",
        },
    )
    assert restored.status_code == 200
    assert {item["lifecycle_status"] for item in restored.json()["items"]} == {"ACTIVE"}


def _persist_profiled_structure(objects, storage, *, dataset_id: str, resource_id: str, revision: int):
    prefix = f"projects/project/datasets/{dataset_id}/normalized/{resource_id}"
    payload = {
        "@module": "pymatgen.core.structure",
        "@class": "Structure",
        "charge": 0,
        "lattice": {"matrix": [[5.4 + revision / 10, 0, 0], [0, 5.4 + revision / 10, 0], [0, 0, 5.4 + revision / 10]]},
        "properties": {},
        "sites": [],
    }
    stored = storage.put_json(f"{prefix}/structure.json", payload)
    metadata_ref = storage.put_json(
        f"{prefix}/metadata.json",
        {
            "objectId": resource_id,
            "contentHash": stored.sha256,
            "metadata": {"formula": "Si", "periodicity": "periodic", "revision": revision},
            "provenance": {"objectType": "Structure"},
        },
    )
    with objects.repository_factory.session() as session:
        session.repositories.datasets.save({
            "id": dataset_id,
            "projectId": "project",
            "name": f"Profiled structure {revision}",
            "status": "profile_ready",
            "createdBy": "owner",
            "metadata": {
                "normalizedExports": [{
                    "objectId": resource_id,
                    "storageKey": stored.storage_key,
                    "metadataKey": metadata_ref.storage_key,
                    "objectHash": f"{revision:064x}",
                    "contentHash": stored.sha256,
                }],
            },
        })
        session.repositories.data_profiles.save({
            "schemaVersion": "0.1",
            "profileId": f"profile-{dataset_id}",
            "datasetId": dataset_id,
            "version": "2",
            "profileContractVersion": "2.1",
            "semanticHash": f"{revision + 10:064x}",
            "objects": [{
                "objectId": resource_id,
                "objectHash": f"{revision:064x}",
                "objectType": "Structure",
            }],
            "resourceSemantics": [{
                "objectId": resource_id,
                "objectHash": f"{revision:064x}",
                "objectType": "Structure",
                "facts": {"formula": "Si", "periodicity": "periodic", "siteCount": 2},
            }],
            "coordinationReadiness": {
                "contractVersion": "1.0",
                "status": "READY",
                "structures": [{
                    "objectId": resource_id,
                    "objectHash": f"{revision:064x}",
                    "latticeStatus": "VALID",
                    "siteCount": 2,
                    "coordinationInputStatus": "READY",
                    "speciesOccupancyStatus": "ORDERED_FULL_OCCUPANCY",
                }],
            },
        })


def _persist_profiled_resource(
    objects,
    storage,
    *,
    dataset_id: str,
    resource_id: str,
    resource_type: str,
    semantic_hash: str,
):
    prefix = f"projects/project/datasets/{dataset_id}/normalized/{resource_id}"
    stored = storage.put_json(
        f"{prefix}/scientific.json",
        {"schemaVersion": "test.scientific_resource.v1", "resourceId": resource_id},
    )
    metadata_ref = storage.put_json(
        f"{prefix}/metadata.json",
        {
            "objectId": resource_id,
            "contentHash": stored.sha256,
            "metadata": {"source": "typed-import"},
            "provenance": {"objectType": resource_type},
        },
    )
    with objects.repository_factory.session() as session:
        session.repositories.datasets.save({
            "id": dataset_id,
            "projectId": "project",
            "name": f"Profiled {resource_type}",
            "status": "profile_ready",
            "createdBy": "owner",
            "metadata": {
                "normalizedExports": [{
                    "objectId": resource_id,
                    "storageKey": stored.storage_key,
                    "metadataKey": metadata_ref.storage_key,
                    "objectHash": semantic_hash,
                    "contentHash": stored.sha256,
                }],
            },
        })
        session.repositories.data_profiles.save({
            "schemaVersion": "0.1",
            "profileId": f"profile-{dataset_id}",
            "datasetId": dataset_id,
            "version": "2",
            "profileContractVersion": "2.1",
            "semanticHash": hashlib.sha256(dataset_id.encode("utf-8")).hexdigest(),
            "objects": [{
                "objectId": resource_id,
                "objectHash": semantic_hash,
                "objectType": resource_type,
            }],
            "resourceSemantics": [{
                "objectId": resource_id,
                "objectHash": semantic_hash,
                "objectType": resource_type,
                "facts": {"source": "typed-import"},
            }],
        })


@pytest.mark.parametrize(
    ("resource_type", "expected_object_type"),
    [
        ("PhononBand", "phonon.band_structure"),
        ("PhononDos", "phonon.dos"),
    ],
)
def test_scientific_object_admission_accepts_profiled_phonon_resources(
    api,
    monkeypatch,
    tmp_path,
    resource_type,
    expected_object_type,
):
    client, _active, _owner, _viewer, _stranger, objects = api
    storage = LocalFileArtifactStorage(tmp_path)
    monkeypatch.setattr(
        "mdi_api.routers.agent2.create_artifact_storage_from_settings",
        lambda _settings: storage,
    )
    resource_id = f"resource-{resource_type.lower()}"
    dataset_id = f"dataset-{resource_type.lower()}"
    semantic_hash = hashlib.sha256(resource_id.encode("utf-8")).hexdigest()
    _persist_profiled_resource(
        objects,
        storage,
        dataset_id=dataset_id,
        resource_id=resource_id,
        resource_type=resource_type,
        semantic_hash=semantic_hash,
    )

    response = client.post(
        "/api/projects/project/scientific-objects",
        json={"dataset_id": dataset_id, "resource_id": resource_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["object"]["kind"] == "PHONON"
    assert body["object"]["object_type"] == expected_object_type
    assert body["version"]["semantic_hash"] == semantic_hash
    assert body["version"]["source_resource_refs_json"] == [{
        "project_id": "project",
        "dataset_id": dataset_id,
        "resource_id": resource_id,
    }]


def test_scientific_object_admission_reuses_the_exact_profiled_resource(
    api,
    monkeypatch,
    tmp_path,
):
    client, _active, _owner, _viewer, _stranger, objects = api
    storage = LocalFileArtifactStorage(tmp_path)
    monkeypatch.setattr(
        "mdi_api.routers.agent2.create_artifact_storage_from_settings",
        lambda _settings: storage,
    )
    dataset_id = "dataset-trajectory-idempotent"
    resource_id = "resource-trajectory-idempotent"
    semantic_hash = hashlib.sha256(resource_id.encode("utf-8")).hexdigest()
    _persist_profiled_resource(
        objects,
        storage,
        dataset_id=dataset_id,
        resource_id=resource_id,
        resource_type="Trajectory",
        semantic_hash=semantic_hash,
    )

    first = client.post(
        "/api/projects/project/scientific-objects",
        json={"dataset_id": dataset_id, "resource_id": resource_id},
    )
    second = client.post(
        "/api/projects/project/scientific-objects",
        json={"dataset_id": dataset_id, "resource_id": resource_id},
    )

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert second.json()["object"]["id"] == first.json()["object"]["id"]
    assert second.json()["version"]["id"] == first.json()["version"]["id"]
    admitted = objects.list_project_objects(
        "project",
        object_type="trajectory.atomic",
        limit=50,
    )
    assert [str(item["id"]) for item in admitted] == [first.json()["object"]["id"]]
    assert len(objects.list_versions(UUID(first.json()["object"]["id"]))) == 1


def test_scientific_object_admission_keeps_unregistered_resource_types_fail_closed(
    api,
    monkeypatch,
    tmp_path,
):
    client, _active, _owner, _viewer, _stranger, objects = api
    storage = LocalFileArtifactStorage(tmp_path)
    monkeypatch.setattr(
        "mdi_api.routers.agent2.create_artifact_storage_from_settings",
        lambda _settings: storage,
    )
    _persist_profiled_resource(
        objects,
        storage,
        dataset_id="dataset-unsupported",
        resource_id="resource-unsupported",
        resource_type="UnregisteredScientificPayload",
        semantic_hash=hashlib.sha256(b"resource-unsupported").hexdigest(),
    )

    response = client.post(
        "/api/projects/project/scientific-objects",
        json={
            "dataset_id": "dataset-unsupported",
            "resource_id": "resource-unsupported",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "persisted scientific resource type is not admitted to ScientificObject authority"
    )


def test_scientific_object_admission_and_version_creation_use_profiled_resources(api, monkeypatch, tmp_path):
    client, active, owner, viewer, _stranger, objects = api
    storage = LocalFileArtifactStorage(tmp_path)
    monkeypatch.setattr("mdi_api.routers.agent2.create_artifact_storage_from_settings", lambda _settings: storage)
    _persist_profiled_structure(objects, storage, dataset_id="dataset-v1", resource_id="structure-v1", revision=1)
    admitted = client.post(
        "/api/projects/project/scientific-objects",
        json={"dataset_id": "dataset-v1", "resource_id": "structure-v1", "display_name": "Versioned structure"},
    )
    assert admitted.status_code == 200
    logical = admitted.json()["object"]
    v1 = admitted.json()["version"]
    assert logical["current_version_id"] == v1["id"]
    assert v1["source_resource_refs_json"] == [{
        "project_id": "project", "dataset_id": "dataset-v1", "resource_id": "structure-v1",
    }]
    assert v1["semantic_profile_ref_json"]["contractVersion"] == "2.1"
    assert v1["canonical_metadata_json"]["coordinationInputStatus"] == "READY"

    _persist_profiled_structure(objects, storage, dataset_id="dataset-v2", resource_id="structure-v2", revision=2)
    response = client.post(
        f"/api/scientific-objects/{logical['id']}/versions",
        json={"dataset_id": "dataset-v2", "resource_id": "structure-v2"},
    )
    assert response.status_code == 200
    v2 = response.json()
    assert v2["version_no"] == 2
    assert v2["scientific_object_id"] == logical["id"]
    refreshed = client.get(f"/api/scientific-objects/{logical['id']}").json()
    assert refreshed["current_version_id"] == v2["id"]
    assert client.get(
        f"/api/scientific-objects/{logical['id']}/versions/{v1['id']}"
    ).json()["content_hash"] == v1["content_hash"]

    active["value"] = viewer
    denied = client.post(
        f"/api/scientific-objects/{logical['id']}/versions",
        json={"dataset_id": "dataset-v2", "resource_id": "structure-v2"},
    )
    assert denied.status_code == 403
    active["value"] = owner


def test_scientific_dataset_query_is_bounded_and_project_authorized(api, monkeypatch, tmp_path):
    client, active, owner, _viewer, stranger, objects = api
    storage = LocalFileArtifactStorage(tmp_path)
    payload = [
        {"sample_id": "s-1", "formula": "Si", "band_gap": 0.0},
        {"sample_id": "s-2", "formula": "SiO2", "band_gap": 1.2},
        {"sample_id": "s-3", "formula": "Ge", "band_gap": 0.7},
    ]
    stored = storage.put_json("project/query.json", payload)
    logical = objects.create_object(
        project_id="project",
        kind=ScientificObjectKind.DATASET,
        object_type="materials.dataset",
        display_name="Query dataset",
        created_by_user_id=owner.id,
    )
    version = objects.create_version(
        logical["id"],
        object_type="materials.dataset",
        object_schema_version="1.0",
        source_resource_refs=[{"scope": "system_fixture", "resource_id": "api-query"}],
        parent_object_version_refs=[],
        normalized_payload_ref=StorageRef(
            storage_backend="local",
            object_key=stored.storage_key,
            checksum=stored.sha256,
            media_type="application/json",
            byte_size=stored.size_bytes,
        ),
        content_hash=stored.sha256,
        semantic_hash=stored.sha256,
        canonical_metadata={"row_count": 3, "sample_identity": "sample_id"},
        created_by_user_id=owner.id,
    )
    monkeypatch.setattr("mdi_api.routers.agent2.create_artifact_storage_from_settings", lambda _settings: storage)
    response = client.post(
        f"/api/scientific-objects/{logical['id']}/versions/{version['id']}/query",
        json={
            "filters": [{"column": "band_gap", "operator": "gt", "value": 0}],
            "sort_by": "band_gap",
            "descending": True,
            "columns": ["sample_id", "formula"],
            "limit": 2,
        },
    )
    assert response.status_code == 200
    assert [item["_stable_id"] for item in response.json()["items"]] == ["s-2", "s-3"]
    active["value"] = stranger
    assert client.post(
        f"/api/scientific-objects/{logical['id']}/versions/{version['id']}/query",
        json={"limit": 1},
    ).status_code == 403
    active["value"] = owner


def test_sse_orders_events_reconnects_without_duplicates_and_checks_authority(api):
    client, active, owner, _viewer, stranger, _objects = api
    turn = client.post("/api/projects/project/research/sessions/session/turns", json={"message": "Stream"}).json()
    client.post(f"/api/research/turns/{turn['turn_id']}/cancel")
    stream = client.get(f"/api/research/turns/{turn['turn_id']}/events")
    assert stream.status_code == 200
    assert stream.text.count("event: turn.accepted") == 1
    assert stream.text.count("event: turn.canceled") == 1
    assert stream.text.index("id: 1") < stream.text.index("id: 2")
    replay = client.get(f"/api/research/turns/{turn['turn_id']}/events", headers={"Last-Event-ID": "1"})
    assert "turn.accepted" not in replay.text and replay.text.count("turn.canceled") == 2  # event name + JSON type
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn['turn_id']}/events").status_code == 403
    active["value"] = owner


def test_phase2_sse_projects_product_events_without_internal_provider_details(api):
    client, _active, _owner, _viewer, _stranger, objects = api
    ref = create_ref(objects, "project")
    created = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={
            "message": "What is RDF?",
            "ui_context": {"active_object_refs": [ref.model_dump(mode="json")], "selection_refs": []},
        },
    ).json()

    class AnswerClient:
        async def generate_structured(self, **_kwargs: Any) -> StructuredLLMResult:
            return StructuredLLMResult(
                provider="fake-internal-provider",
                model="fixture-model",
                parsed={
                    "contract_version": "1.0",
                    "action": "ANSWER",
                    "assistant_message": "RDF describes the distribution of pair distances.",
                    "research_objective": None,
                    "selected_scope_ref_keys": [],
                    "scientific_requirements": [],
                    "reusable_result_ref_keys": [],
                    "clarification": None,
                    "confidence": "HIGH",
                },
                latency_ms=1,
                usage={"input_tokens": 1},
                prompt_version="research-orchestrator/1.0",
            )

    result = asyncio.run(AgentTurnProcessor(
        repository_factory=objects.repository_factory,
        registries=build_default_agent2_registries(),
        llm_client=AnswerClient(),
    ).process(UUID(created["turn_id"])))
    assert result.status == "ANSWERED"
    detail = client.get(f"/api/research/turns/{created['turn_id']}").json()
    assert detail["orchestration"] == {"decision_available": True, "action_dispatch_status": "COMPLETED"}
    serialized = str(detail)
    assert "fake-internal-provider" not in serialized
    assert "fixture-model" not in serialized
    assert "input_tokens" not in serialized

    stream = client.get(f"/api/research/turns/{created['turn_id']}/events")
    event_names = [line.removeprefix("event: ") for line in stream.text.splitlines() if line.startswith("event: ")]
    assert event_names == [
        "turn.accepted",
        "context.resolving",
        "context.ready",
        "assistant.preparing",
        "turn.status.changed",
        "assistant.message",
        "turn.answered",
    ]
    assert "fake-internal-provider" not in stream.text

    progress = client.get(f"/api/research/turns/{created['turn_id']}/progress")
    assert progress.status_code == 200
    assert progress.json()["response_kind"] == "CONVERSATIONAL"


@pytest.mark.parametrize(
    ("turn", "decision", "expected"),
    [
        (
            {"status": "ANSWERED", "action_type": "QUERY_DATA"},
            {"decision_json": {"reusable_result_ref_keys": []}},
            "DATA_QUERY",
        ),
        (
            {"status": "ANSWERED", "action_type": "ANSWER"},
            {"decision_json": {"reusable_result_ref_keys": []}},
            "CONVERSATIONAL",
        ),
        (
            {"status": "ANSWERED", "action_type": "ANSWER"},
            {"decision_json": {"reusable_result_ref_keys": ["result_1"]}},
            "RESULT_REUSE",
        ),
        (
            {"status": "COMPLETED", "action_type": "ANALYZE"},
            {"decision_json": {"reusable_result_ref_keys": ["result_1"]}},
            None,
        ),
    ],
)
def test_research_progress_response_kind_is_server_authoritative(
    turn: dict[str, Any],
    decision: dict[str, Any],
    expected: str | None,
):
    assert _research_progress_response_kind(turn, decision) == expected


def test_phase4_progress_and_dispatch_are_project_authorized(api):
    client, active, owner, _viewer, stranger, _objects = api
    turn = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={"message": "Prepare an analysis"},
    ).json()
    progress = client.get(f"/api/research/turns/{turn['turn_id']}/progress")
    assert progress.status_code == 200
    assert progress.json() == {
        "contract_version": "1.0",
        "turn_id": turn["turn_id"],
        "status": "RECEIVED",
        "response_kind": None,
        "plan_title": None,
        "steps": [],
        "active_step_ids": [],
        "completed_step_count": 0,
        "total_step_count": 0,
        "incremental_outputs": [],
        "warnings": [],
        "execution_outcome": None,
        "result_projection_pending": False,
    }
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn['turn_id']}/progress").status_code == 403
    assert client.post(f"/api/research/turns/{turn['turn_id']}/dispatch").status_code == 403
    active["value"] = owner


def test_progress_projects_interpretation_retry_without_hiding_preserved_result(api):
    client, _active, _owner, _viewer, _stranger, objects = api
    created = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={"message": "Interpret the completed scientific result"},
    ).json()
    turn_id = UUID(created["turn_id"])
    with objects.repository_factory.unit_of_work() as unit:
        current = unit.agent2.research_turns.get(turn_id)
        unit.agent2.research_turns.compare_and_set_status(
            turn_id,
            expected_status=str(current["status"]),
            expected_version=int(current["row_version"]),
            target_status="INTERPRETING",
        )
        for event_type, payload in (
            ("INTERPRETATION_STARTED", {"status": "INTERPRETING"}),
            (
                "INTERPRETATION_RETRY_SCHEDULED",
                {
                    "error_code": "DEEPSEEK_RATE_LIMITED",
                    "retry_delay_seconds": 0.31,
                    "preserved_result": True,
                },
            ),
        ):
            unit.agent2.research_turn_events.append_turn_event(
                {
                    "id": uuid4(),
                    "turn_id": turn_id,
                    "sequence_no": unit.agent2.research_turn_events.next_sequence_no(
                        turn_id
                    ),
                    "event_type": event_type,
                    "payload_json": payload,
                }
            )

    response = client.get(f"/api/research/turns/{turn_id}/progress")

    assert response.status_code == 200
    assert response.json()["status"] == "INTERPRETING"
    assert response.json()["warnings"] == [
        {
            "code": "INTERPRETATION_RETRYING",
            "message": (
                "解释服务暂时繁忙，正在按有界策略重试；"
                "已完成的科学结果仍然保留。"
            ),
        }
    ]


def test_research_progress_exposes_bounded_strategy_without_hidden_reasoning(api):
    client, _active, _owner, _viewer, _stranger, objects = api
    turn = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={"message": "Explain the transport behavior autonomously"},
    ).json()
    turn_id = UUID(turn["turn_id"])
    with objects.repository_factory.unit_of_work() as unit:
        for event_type, payload in (
            (
                "AUTONOMY_CYCLE_CREATED",
                {
                    "mode": "BOUNDED_AUTONOMOUS",
                    "cycle_index": 2,
                    "research_objective": "Explain the transport behavior",
                    "policy_version": "bounded-autonomy/1.0",
                },
            ),
            (
                "AUTONOMY_ASSESSMENT_RECORDED",
                {
                    "assessment": {
                        "outcome": "CONTINUE_WITH_ANALYSIS",
                        "strategy_decision": {
                            "action": "TEST_HYPOTHESIS",
                            "reasoning": "must not be exposed",
                        },
                        "strategy_summary": {
                            "evidence_state_fingerprint": "a" * 64,
                            "evidence_strength": "WELL_SUPPORTED",
                            "question_count": 2,
                            "resolved_question_count": 1,
                            "open_question_count": 1,
                            "evidence_gap_count": 1,
                            "hypothesis_count": 1,
                            "unresolved_contradiction_count": 0,
                            "questions": [
                                {
                                    "question_id": "q-transport",
                                    "question_type": "QUANTIFY",
                                    "statement": "Is diffusion elevated?",
                                    "status": "RESOLVED",
                                    "evidence_result_ids": [],
                                    "evidence_gap_ids": [],
                                },
                                {
                                    "question_id": "q-structure",
                                    "question_type": "EXPLAIN",
                                    "statement": "Does local structure explain transport?",
                                    "status": "OPEN",
                                    "evidence_result_ids": [],
                                    "evidence_gap_ids": ["gap-structure"],
                                },
                            ],
                            "evidence_gaps": [
                                {
                                    "gap_id": "gap-structure",
                                    "question_id": "q-structure",
                                    "gap_type": "STRUCTURAL_CONTEXT_MISSING",
                                    "statement": "Local structural evidence is missing.",
                                    "evidence_value": "HIGH",
                                    "required_result_types": [],
                                    "satisfied_by_result_ids": [],
                                }
                            ],
                            "hypotheses": [
                                {
                                    "hypothesis_id": "hypothesis-constraint",
                                    "question_id": "q-structure",
                                    "statement": "Weaker local constraint may accompany diffusion.",
                                    "status": "PROPOSED",
                                    "supporting_result_ids": [],
                                    "contradicting_result_ids": [],
                                    "testable_predictions": [],
                                    "known_assumptions": [],
                                }
                            ],
                            "current_question": {
                                "question_id": "q-structure",
                                "statement": "Does local structure explain transport?",
                            },
                            "active_evidence_gap": {
                                "gap_id": "gap-structure",
                                "statement": "Local structural evidence is missing.",
                            },
                            "active_hypothesis": {
                                "hypothesis_id": "hypothesis-constraint",
                                "statement": "Weaker local constraint may accompany diffusion.",
                                "status": "PROPOSED",
                            },
                        },
                    }
                },
            ),
        ):
            unit.agent2.research_turn_events.append_turn_event({
                "id": uuid4(),
                "turn_id": turn_id,
                "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id),
                "event_type": event_type,
                "payload_json": payload,
            })

    response = client.get(f"/api/research/turns/{turn_id}/progress")
    assert response.status_code == 200
    autonomy = response.json()["autonomy"]
    assert autonomy["enabled"] is True
    assert autonomy["cycle_index"] == 2
    assert autonomy["decision"]["strategy"]["action"] == "TEST_HYPOTHESIS"
    assert (
        autonomy["decision"]["strategy"]["current_question"]["statement"]
        == "Does local structure explain transport?"
    )
    assert autonomy["decision"]["strategy"]["questions"][0]["status"] == "RESOLVED"
    assert (
        autonomy["decision"]["strategy"]["evidence_gaps"][0]["gap_type"]
        == "STRUCTURAL_CONTEXT_MISSING"
    )
    assert (
        autonomy["decision"]["strategy"]["hypotheses"][0]["status"]
        == "PROPOSED"
    )
    assert "reasoning" not in str(autonomy)


def test_terminal_history_progress_uses_read_only_fallback_when_legacy_plan_payload_is_missing(api, monkeypatch):
    client, _active, _owner, _viewer, _stranger, objects = api
    turn = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={"message": "Open a historical result"},
    ).json()
    turn_id = UUID(turn["turn_id"])
    with objects.repository_factory.unit_of_work() as unit:
        current = unit.agent2.research_turns.get(turn_id)
        unit.agent2.research_turns.compare_and_set_status(
            turn_id,
            expected_status=str(current["status"]),
            expected_version=int(current["row_version"]),
            target_status="COMPLETED",
        )
        unit.agent2.research_turns.attach_job(turn_id, "legacy-result-job")

    def missing_legacy_plan(_self, _job_id):
        raise ValueError("AnalysisPlan record is missing analysis_plan_json")

    monkeypatch.setattr(
        "mdi_api.routers.agent2.ResearchExecutionSupervisor.sync_for_job",
        missing_legacy_plan,
    )
    response = client.get(f"/api/research/turns/{turn_id}/progress")
    assert response.status_code == 200
    assert response.json() == {
        "contract_version": "1.0",
        "turn_id": str(turn_id),
        "status": "COMPLETED",
        "response_kind": "SCIENTIFIC_EXECUTION",
        "plan_title": "Historical completed analysis",
        "steps": [],
        "active_step_ids": [],
        "completed_step_count": 0,
        "total_step_count": 0,
        "incremental_outputs": [],
        "warnings": ["HISTORICAL_ANALYSIS_PLAN_PAYLOAD_UNAVAILABLE"],
        "execution_outcome": "SUCCESS",
        "result_projection_pending": False,
    }


def test_agent2_result_projection_exposes_bounded_facts_and_exact_sources(api):
    client, active, _owner, _viewer, stranger, objects = api
    ref = create_ref(objects, "project")
    scientific_selection = {
        "contract_version": "1.0",
        "object_ref": ref.model_dump(mode="json"),
        "viewer_id": "materials.table",
        "selection_type": "DATASET_SAMPLE",
        "semantic_locator": {"sample_ref": "mat-2"},
        "display_label": "mat-2",
    }
    turn = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={"message": "Read the exact scientific result"},
    ).json()
    turn_id = UUID(turn["turn_id"])
    bundle = ScientificResultBundle.model_validate({
        "schema_version": "1.0",
        "result_id": str(uuid4()),
        "project_id": "project",
        "research_session_id": "session",
        "research_turn_id": str(turn_id),
        "research_question": "Read the exact scientific result",
        "source_object_refs": [ref.model_dump(mode="json")],
        "execution_status": "SUCCESS",
        "relevance_status": "CURRENT",
        "result_items": [],
        "facts": [{
            "fact_id": "structure.site_count",
            "predicate": "structure.site_count",
            "subject_ref": "structure",
            "value": 2,
            "unit": None,
            "source": {"scientific_object_ref": ref.model_dump(mode="json")},
        }],
        "figures": [],
        "tables": [],
        "output_object_refs": [],
        "evidence": [],
        "methods": [],
        "limitations": [],
        "warnings": [],
        "provenance": {},
        "projection_version": "agent2.result/1.0",
    })
    with objects.repository_factory.unit_of_work() as unit:
        unit.agent2.research_context_snapshots.add({
            "id": uuid4(),
            "project_id": "project",
            "research_session_id": "session",
            "research_turn_id": turn_id,
            "snapshot_schema_version": "1.1",
            "active_scope_refs_json": [],
            "selection_refs_json": [],
            "scientific_selections_json": [scientific_selection],
            "resolved_references_json": [],
            "referenced_result_refs_json": [],
            "relevant_finding_refs_json": [],
            "effective_constraints_json": [],
            "research_goal": None,
            "unresolved_questions_json": [],
            "context_fingerprint": "presentation-api-test",
            "compiler_version": "test",
        })
        current = unit.agent2.research_turns.get(turn_id)
        unit.agent2.research_turns.compare_and_set_status(
            turn_id,
            expected_status=str(current["status"]),
            expected_version=int(current["row_version"]),
            target_status="COMPLETED",
        )
        unit.agent2.scientific_result_snapshots.add({
            "id": uuid4(),
            "project_id": "project",
            "research_turn_id": turn_id,
            "job_id": None,
            "schema_version": bundle.schema_version,
            "projection_version": bundle.projection_version,
            "execution_status": bundle.execution_status.value,
            "relevance_status": bundle.relevance_status.value,
            "source_fingerprint": "presentation-api-test",
            "bundle_json": bundle.model_dump(mode="json"),
        })

    response = client.get(f"/api/research/turns/{turn_id}/result")
    assert response.status_code == 200
    payload = response.json()
    assert payload["result_id"] == str(bundle.result_id)
    assert payload["result_snapshot_id"]
    assert payload["result_snapshot_id"] != str(bundle.result_id)
    assert payload["source_object_refs"][0] == {
        **ref.model_dump(mode="json"),
        "version_no": 1,
    }
    assert payload["facts"] == [bundle.facts[0].model_dump(mode="json")]
    assert payload["evidence"] == []
    assert payload["artifacts"] == []
    assert payload["scientific_selections"][0]["semantic_locator"] == {"sample_ref": "mat-2"}

    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/result").status_code == 403


def test_phase4_sse_reconnect_does_not_repeat_execution_events(api):
    client, _active, _owner, _viewer, _stranger, objects = api
    turn = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={"message": "Stream execution"},
    ).json()
    turn_id = UUID(turn["turn_id"])
    with objects.repository_factory.unit_of_work() as unit:
        for event_type, payload in (
            ("JOB_STARTED", {"status": "RUNNING"}),
            ("EXECUTION_STEP_STARTED", {"step_id": "step_1", "label": "正在计算径向分布函数"}),
            ("EXECUTION_OUTPUT_AVAILABLE", {"step_id": "step_1", "label": "径向分布函数输出已生成"}),
        ):
            unit.agent2.research_turn_events.append_turn_event({
                "id": uuid4(),
                "turn_id": turn_id,
                "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id),
                "event_type": event_type,
                "payload_json": payload,
            })
    first = client.get(f"/api/research/turns/{turn['turn_id']}/events")
    assert "event: analysis.started" in first.text
    assert "event: analysis.step.started" in first.text
    assert "event: analysis.output.available" in first.text
    replay = client.get(
        f"/api/research/turns/{turn['turn_id']}/events",
        headers={"Last-Event-ID": "2"},
    )
    assert "analysis.started" not in replay.text
    assert "analysis.step.started" in replay.text
    assert "analysis.output.available" in replay.text
