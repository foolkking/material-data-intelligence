from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert
from sqlalchemy.pool import StaticPool

from mdi_api.db import metadata, organizations, project_members, projects, sessions, users
from mdi_api.main import create_app
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.auth import CurrentUser, get_current_user
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.schemas import ScientificObjectKind, ScientificObjectRef, StorageRef
from mdi_api.scientific_objects.service import ScientificObjectService
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
