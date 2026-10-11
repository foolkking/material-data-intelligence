from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
from types import SimpleNamespace
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert, update
from sqlalchemy.pool import StaticPool

from mdi_api.db import metadata, organizations, project_members, projects, research_turns, sessions, users
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


@pytest.mark.parametrize("status", ["INTERPRETING", "RESULT_PENDING", "RESULT_READY"])
def test_cancel_interpretation_authorizes_writer_and_keeps_result_stages(api, status):
    from mdi_api.routers.agent2 import get_research_turn_service

    client, active, owner, viewer, _stranger, _objects = api
    created = client.post("/api/projects/project/research/sessions/session/turns", json={"message": "Explain"}).json()
    turn_id = UUID(created["turn_id"])
    factory = get_research_turn_service().repository_factory
    with factory.unit_of_work() as unit:
        unit.connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status=status))
    active["value"] = viewer
    assert client.post(f"/api/research/turns/{turn_id}/cancel").status_code == 403
    active["value"] = owner
    response = client.post(f"/api/research/turns/{turn_id}/cancel")
    assert response.status_code == (200 if status == "INTERPRETING" else 409)
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == ("CANCELED" if status == "INTERPRETING" else status)


@pytest.mark.parametrize("provider", ["personal", "platform:shared"])
def test_autonomous_child_inherits_parent_model_identity(api, provider):
    from sqlalchemy import update
    from mdi_api.db import messages
    from mdi_api.routers.agent2 import get_research_turn_service
    from mdi_api.research_agent.schemas import ResearchTurnUIContext
    client, *_ = api
    created = client.post("/api/projects/project/research/sessions/session/turns", json={"message": "Analyze"}).json()
    assert client.post(f"/api/research/turns/{created['turn_id']}/cancel").status_code == 200
    service = get_research_turn_service()
    choice = {"user_id": "owner", "provider": provider, "model": "Vendor/Exact-ID", "thinking_mode": "standard"}
    with service.repository_factory.unit_of_work() as unit:
        unit.connection.execute(update(messages).where(messages.c.id == created["user_message"]["id"]).values(payload_json={"_model_selection": choice}))
    child = service.receive_autonomous_turn(project_id="project", session_id="session", parent_turn_id=UUID(created["turn_id"]), message="Continue analysis", ui_context=ResearchTurnUIContext(), autonomy={"assessment_signature": "model-lineage-test", "cycle_index": 2})
    with service.repository_factory.session() as unit:
        message = unit.agent2.research_turns.get_message(child.user_message.id)
    assert message["payload_json"]["_model_selection"] == choice
    assert "api_key" not in str(message["payload_json"])


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


def _context_result_link_fixture(api, *, source_project="project", source_session="session", item_patch=None, manifest_patch=None, bundle_patch=None):
    client, _active, _owner, _viewer, _stranger, objects = api
    source = client.post(f"/api/projects/{source_project}/research/sessions/{source_session}/turns", json={"message": "Original saved scientific result"}).json()
    source_id = UUID(source["turn_id"])
    snapshot_id = uuid4()
    with objects.repository_factory.unit_of_work() as unit:
        snapshot = unit.agent2.scientific_result_snapshots.add({
            "id": snapshot_id, "project_id": source_project, "research_turn_id": source_id, "job_id": None,
            "schema_version": "1.0", "projection_version": "agent2.result/1.0", "execution_status": "SUCCESS",
            "relevance_status": "CURRENT", "source_fingerprint": str(snapshot_id),
            "bundle_json": {"result_id": str(uuid4()), "project_id": source_project, "research_turn_id": str(source_id),
                "private_fixture_value": "not-navigation-data", **(bundle_patch or {})},
        })
    current = client.post("/api/projects/project/research/sessions/session/turns", json={"message": "Explain the saved result without recomputing"}).json()
    turn_id = UUID(current["turn_id"])
    manifest = {
        "context_manifest_id": str(uuid4()), "operation": "ORCHESTRATOR", "project_id": "project",
        "research_session_id": "session", "research_turn_id": str(turn_id), "input_state": "ACTUAL",
        "included_items": [{"item_id": "result_1", "kind": "SCIENTIFIC_RESULT", "authorization_checked": True,
            "server_side_source_identity": str(snapshot_id), "result_ref": str(snapshot_id), "provider_opaque_ref": "result_1",
            **(item_patch or {})}],
        "excluded_items": [], "serialized_input": {"research_context": {"results": [{"ref_key": "result_1", "summary": "Saved RDF"}]}},
        **(manifest_patch or {}),
    }
    with objects.repository_factory.unit_of_work() as unit:
        unit.agent2.research_turn_events.append_turn_event({
            "id": uuid4(), "turn_id": turn_id,
            "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id),
            "event_type": "CONTEXT_RESOLVED", "payload_json": {"context_manifest": manifest},
        })
    return turn_id, snapshot, manifest


def test_context_result_link_uses_the_saved_source_session_and_preserves_the_model_input(api):
    client, active, _owner, viewer, stranger, objects = api
    with objects.repository_factory.unit_of_work() as unit:
        unit.connection.execute(insert(sessions), {"id": "source-session", "project_id": "project", "mode": "project", "status": "active", "created_by": "owner"})
    turn_id, snapshot, manifest = _context_result_link_fixture(api, source_session="source-session")
    path = f"/api/research/turns/{turn_id}/context-manifest"
    active["value"] = viewer
    response = client.get(path)
    assert response.status_code == 200, response.text
    assert response.json()["result_sources"] == [{
        "result_snapshot_id": str(snapshot["id"]), "project_id": "project",
        "research_session_id": "source-session", "research_turn_id": str(snapshot["research_turn_id"]),
    }]
    assert response.json()["manifest"] == manifest
    assert response.json()["manifests"][0]["manifest"] == manifest
    assert "not-navigation-data" not in response.text
    with objects.repository_factory.session() as unit:
        event = next(item for item in unit.agent2.research_turn_events.list_for_turn(turn_id) if item["event_type"] == "CONTEXT_RESOLVED")
        assert event["payload_json"]["context_manifest"] == manifest
        assert unit.agent2.scientific_result_snapshots.get(snapshot["id"]) == snapshot
    active["value"] = stranger
    assert client.get(path).status_code == 403


def _context_navigation_item(item_id, ref):
    return {
        "id": item_id, "result_type": "structure.rdf", "role": "PRIMARY", "title": "structure.rdf result",
        "artifact_ids": [f"private-artifact-{item_id}"], "scientific_object_refs": [ref.model_dump(mode="json")],
        "fact_refs": [f"private-fact-{item_id}"], "evidence_refs": [f"private-evidence-{item_id}"],
    }


def test_context_navigation_metadata_keeps_exact_material_items_without_changing_or_expanding_model_input(api):
    client, _active, _owner, _viewer, _stranger, objects = api
    refs = {name: create_ref(objects, "project").model_copy(update={"display_name": f"{name}.cif"}) for name in ("Si", "Cu", "NaCl")}
    items = [_context_navigation_item(name, refs[name]) for name in ("NaCl", "Cu", "Si")]
    turn_id, snapshot, manifest = _context_result_link_fixture(api,
        item_patch={"serialized_representation": {"result_item_ids": ["Si", "Cu", "NaCl"]}},
        manifest_patch={"operation": "INTERPRETER", "serialized_input": {"result": {"result_items": [
            {"id": name, "result_type": "structure.rdf"} for name in ("Si", "Cu", "NaCl")
        ]}}},
        bundle_patch={"result_items": items, "facts": [{"value": "private-numeric-data"}]},
    )
    response = client.get(f"/api/research/turns/{turn_id}/context-manifest")
    assert response.status_code == 200, response.text
    payload = response.json()
    location = payload["result_sources"][0]
    assert location["result_snapshot_id"] == str(snapshot["id"])
    assert location["research_turn_id"] == str(snapshot["research_turn_id"])
    assert {item["id"]: item["scientific_object_refs"] for item in location["result_items"]} == {
        name: [ref.model_dump(mode="json")] for name, ref in refs.items()
    }
    assert all(set(item) == {"id", "title", "result_type", "scientific_object_refs"} for item in location["result_items"])
    assert "private-" not in response.text
    assert "not-navigation-data" not in response.text
    assert payload["manifest"] == manifest
    assert payload["manifests"][0]["manifest"] == manifest
    with objects.repository_factory.session() as unit:
        event = next(item for item in unit.agent2.research_turn_events.list_for_turn(turn_id) if item["event_type"] == "CONTEXT_RESOLVED")
        assert event["payload_json"]["context_manifest"] == manifest
        assert unit.agent2.scientific_result_snapshots.get(snapshot["id"]) == snapshot


@pytest.mark.parametrize("invalid", ["duplicate", "foreign-source", "malformed", "extra-field"])
def test_context_navigation_omits_invalid_materials_without_guessing_or_discarding_other_items(api, invalid):
    objects = api[-1]
    valid = _context_navigation_item("Si", create_ref(objects, "project"))
    bad = _context_navigation_item("Cu", create_ref(objects, "project"))
    items = [bad, valid]
    if invalid == "duplicate":
        items.append({**bad, "result_type": "electronic.band"})
    elif invalid == "foreign-source":
        bad["scientific_object_refs"][0]["project_id"] = "other"
    elif invalid == "malformed":
        bad["scientific_object_refs"][0]["version_id"] = "missing-version"
    else:
        bad["untrusted_value"] = "private-extra-data"
    turn_id, _snapshot, manifest = _context_result_link_fixture(api, bundle_patch={"result_items": items})
    response = api[0].get(f"/api/research/turns/{turn_id}/context-manifest")
    assert response.status_code == 200, response.text
    assert [item["id"] for item in response.json()["result_sources"][0]["result_items"]] == ["Si"]
    assert response.json()["manifest"] == manifest
    assert "private-" not in response.text


@pytest.mark.parametrize("mismatch", [{"project_id": "other"}, {"research_turn_id": str(UUID(int=1))}])
def test_context_navigation_does_not_use_items_from_a_misbound_bundle(api, mismatch):
    item = _context_navigation_item("Si", create_ref(api[-1], "project"))
    turn_id, _snapshot, manifest = _context_result_link_fixture(api, bundle_patch={"result_items": [item], **mismatch})
    response = api[0].get(f"/api/research/turns/{turn_id}/context-manifest")
    assert response.status_code == 200, response.text
    assert "result_items" not in response.json()["result_sources"][0]
    assert response.json()["manifest"] == manifest


@pytest.mark.parametrize("item_patch", [
    {"authorization_checked": False}, {"kind": "SCIENTIFIC_FINDING"},
    {"server_side_source_identity": "another-result"}, {"result_ref": "not-a-snapshot-id"},
    {"result_ref": "11111111-1111-4111-8111-111111111111", "server_side_source_identity": "11111111-1111-4111-8111-111111111111"},
])
def test_context_result_links_do_not_guess_missing_or_unverified_sources(api, item_patch):
    turn_id, _snapshot, manifest = _context_result_link_fixture(api, item_patch=item_patch)
    response = api[0].get(f"/api/research/turns/{turn_id}/context-manifest")
    assert response.status_code == 200
    assert response.json()["result_sources"] == []
    assert response.json()["manifest"] == manifest


@pytest.mark.parametrize("manifest_patch", [{"project_id": "other"}, {"research_session_id": "other-session"}, {"research_turn_id": str(UUID(int=1))}])
def test_context_result_links_reject_foreign_manifest_identity(api, manifest_patch):
    turn_id, _snapshot, _manifest = _context_result_link_fixture(api, manifest_patch=manifest_patch)
    assert api[0].get(f"/api/research/turns/{turn_id}/context-manifest").json()["result_sources"] == []


def test_context_result_links_never_cross_the_current_project(api):
    turn_id, _snapshot, _manifest = _context_result_link_fixture(api, source_project="other", source_session="other-session")
    assert api[0].get(f"/api/research/turns/{turn_id}/context-manifest").json()["result_sources"] == []


def test_context_result_links_do_not_open_a_newer_snapshot_for_an_older_citation(api):
    from datetime import timedelta
    turn_id, snapshot, manifest = _context_result_link_fixture(api)
    with api[-1].repository_factory.unit_of_work() as unit:
        unit.agent2.scientific_result_snapshots.add({
            **snapshot, "id": uuid4(), "source_fingerprint": "newer-projection",
            "created_at": snapshot["created_at"] + timedelta(seconds=1),
        })
    response = api[0].get(f"/api/research/turns/{turn_id}/context-manifest")
    assert response.status_code == 200
    assert response.json()["result_sources"] == []
    assert response.json()["manifest"] == manifest


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


def test_explicit_result_action_exposes_only_actual_interpreter_context(api):
    client, active, _owner, _viewer, stranger, objects = api
    created = client.post("/api/projects/project/research/sessions/session/turns", json={
        "message": "重新解释", "requested_action": "INTERPRET_RESULT",
        "ui_context": {"explicit_result_ids": [str(uuid4())]},
    }).json()
    turn_id = UUID(created["turn_id"])
    with objects.repository_factory.unit_of_work() as unit:
        unit.agent2.research_turn_events.append_turn_event({
            "id": uuid4(), "turn_id": turn_id,
            "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id),
            "event_type": "CONTEXT_RESOLVED", "payload_json": {"requested_action": "INTERPRET_RESULT"},
        })
    path = f"/api/research/turns/{turn_id}/context-manifest"
    assert client.get(path).status_code == 409
    actual = {"context_manifest_id": str(uuid4()), "operation": "INTERPRETER", "input_state": "ACTUAL", "serialized_input": {"user_question": "重新解释"}}
    with objects.repository_factory.unit_of_work() as unit:
        unit.agent2.research_turn_events.append_turn_event({
            "id": uuid4(), "turn_id": turn_id,
            "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id),
            "event_type": "CONTEXT_MANIFEST_RECORDED", "payload_json": {"context_manifest": actual},
        })
    response = client.get(path)
    assert response.status_code == 200
    assert response.json()["manifest"] == actual
    assert [item["operation"] for item in response.json()["manifests"]] == ["INTERPRETER"]
    active["value"] = stranger
    assert client.get(path).status_code == 403


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


def test_create_turn_replays_same_admission_key_after_lost_response(api):
    client, _active, _owner, _viewer, _stranger, _objects = api
    payload = {
        "message": "A request whose response may be lost during API restart",
        "admission_key": "m4-01-api-restart-api",
    }

    first = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json=payload,
    )
    replay = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json=payload,
    )

    assert first.status_code == replay.status_code == 202
    assert first.json()["turn_id"] == replay.json()["turn_id"]
    assert first.json()["user_message"]["id"] == replay.json()["user_message"]["id"]
    assert replay.json()["idempotent_replay"] is True

    conflict = client.post(
        "/api/projects/project/research/sessions/session/turns",
        json={**payload, "message": "not the admitted request"},
    )
    assert conflict.status_code == 409
    assert conflict.json()["detail"]["code"] == "RESEARCH_TURN_ADMISSION_CONFLICT"


def test_create_turn_rejects_empty_session_mismatch_and_read_only_user(api):
    client, active, owner, viewer, _stranger, _objects = api
    assert client.post("/api/projects/project/research/sessions/session/turns", json={"message": "  "}).status_code == 422
    assert client.post("/api/projects/project/research/sessions/other-session/turns", json={"message": "Wrong scope"}).status_code == 404
    active["value"] = viewer
    assert client.post("/api/projects/project/research/sessions/session/turns", json={"message": "Read only"}).status_code == 403
    active["value"] = owner


@pytest.mark.parametrize("context,action,mode", [
    (None, "INTERPRET_RESULT", "STANDARD"),
    ({"explicit_result_ids": []}, "INTERPRET_RESULT", "STANDARD"),
    ({"explicit_result_ids": [str(uuid4()), str(uuid4())]}, "INTERPRET_RESULT", "STANDARD"),
    ({"explicit_result_ids": [str(uuid4())]}, "ANALYZE", "STANDARD"),
    ({"explicit_result_ids": [str(uuid4())]}, "INTERPRET_RESULT", "BOUNDED_AUTONOMOUS"),
])
def test_explicit_action_requires_one_result_and_cannot_start_analysis(api, context, action, mode):
    client, *_ = api
    response = client.post("/api/projects/project/research/sessions/session/turns", json={
        "message": "重新解释", "requested_action": action, "ui_context": context, "autonomy_mode": mode,
    })
    assert response.status_code == 422
    assert client.get("/api/projects/project/research/sessions/session/turns").json()["items"] == []


def test_explicit_action_is_durable_and_has_distinct_admission_identity(api, monkeypatch):
    client, _active, owner, _viewer, _stranger, objects = api
    from mdi_api import user_models
    choice = {"provider": "personal", "model": "qwen3.8-27b", "thinking_mode": "standard"}
    monkeypatch.setattr(user_models, "validate_user_selection", lambda user_id, value: value if user_id == owner.id else None)
    payload = {
        "message": "重新解释", "admission_key": "explicit-action", "requested_action": "INTERPRET_RESULT",
        "ui_context": {"explicit_result_ids": [str(uuid4())]}, "model_selection": choice,
    }
    path = "/api/projects/project/research/sessions/session/turns"
    first = client.post(path, json=payload)
    replay = client.post(path, json=payload)
    assert first.status_code == replay.status_code == 202
    assert first.json()["turn_id"] == replay.json()["turn_id"] and replay.json()["idempotent_replay"]
    assert client.post(path, json={**payload, "requested_action": None}).status_code == 409
    with objects.repository_factory.session() as session:
        message = session.agent2.research_turns.get_message(first.json()["user_message"]["id"])
        assert message["payload_json"]["requested_action"] == "INTERPRET_RESULT"
        assert message["payload_json"]["_model_selection"] == choice
    # Omission and explicit null preserve pre-existing request fingerprints.
    ordinary = {**payload, "requested_action": None, "admission_key": "ordinary-action"}
    assert client.post(path, json=ordinary).status_code == 202
    ordinary.pop("requested_action")
    assert client.post(path, json=ordinary).json()["idempotent_replay"]


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
    payload: dict | None = None,
):
    prefix = f"projects/project/datasets/{dataset_id}/normalized/{resource_id}"
    stored = storage.put_json(
        f"{prefix}/scientific.json",
        payload
        or {
            "schemaVersion": "test.scientific_resource.v1",
            "resourceId": resource_id,
        },
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


def test_scientific_object_admission_uses_registered_trajectory_size_bound(
    api,
    monkeypatch,
    tmp_path,
):
    from mdi_artifact_core import DEFAULT_TRAJECTORY_CAPS

    client, _active, _owner, _viewer, _stranger, objects = api
    storage = LocalFileArtifactStorage(tmp_path)
    monkeypatch.setattr(
        "mdi_api.routers.agent2.create_artifact_storage_from_settings",
        lambda _settings: storage,
    )
    dataset_id = "dataset-large-trajectory"
    resource_id = "resource-large-trajectory"
    semantic_hash = hashlib.sha256(resource_id.encode("utf-8")).hexdigest()
    _persist_profiled_resource(
        objects,
        storage,
        dataset_id=dataset_id,
        resource_id=resource_id,
        resource_type="Trajectory",
        semantic_hash=semantic_hash,
        payload={
            "schemaVersion": "test.large_trajectory.v1",
            "resourceId": resource_id,
            "padding": "x" * (17 * 1024 * 1024),
        },
    )

    response = client.post(
        "/api/projects/project/scientific-objects",
        json={"dataset_id": dataset_id, "resource_id": resource_id},
    )

    assert response.status_code == 200, response.text
    assert response.json()["object"]["object_type"] == "trajectory.atomic"
    version = response.json()["version"]
    assert (
        version["normalized_payload_ref_json"]["byte_size"]
        > 16 * 1024 * 1024
    )
    assert (
        version["normalized_payload_ref_json"]["byte_size"]
        < DEFAULT_TRAJECTORY_CAPS["max_json_bytes"]
    )


def test_scientific_object_admission_returns_typed_error_for_bounded_read(
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
    dataset_id = "dataset-over-limit-trajectory"
    resource_id = "resource-over-limit-trajectory"
    semantic_hash = hashlib.sha256(resource_id.encode("utf-8")).hexdigest()
    _persist_profiled_resource(
        objects,
        storage,
        dataset_id=dataset_id,
        resource_id=resource_id,
        resource_type="Trajectory",
        semantic_hash=semantic_hash,
    )
    original = storage.get_bytes_bounded

    def reject_payload(key: str, *, max_bytes: int) -> bytes:
        if key.endswith("/scientific.json"):
            raise ValueError("Artifact exceeds the bounded read limit")
        return original(key, max_bytes=max_bytes)

    monkeypatch.setattr(storage, "get_bytes_bounded", reject_payload)

    response = client.post(
        "/api/projects/project/scientific-objects",
        json={"dataset_id": dataset_id, "resource_id": resource_id},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "persisted scientific resource exceeds its registered bounded size"
    )
    assert objects.list_project_objects(
        "project",
        object_type="trajectory.atomic",
        limit=50,
    ) == []


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


def test_answer_stream_reconnects_by_sequence_and_hides_canceled_drafts(api):
    from mdi_api.routers.agent2 import get_research_turn_service
    from mdi_api.research_agent.orchestration.answer_stream import ResearchAnswerPublisher

    client, active, owner, _viewer, stranger, _objects = api
    turn = client.post("/api/projects/project/research/sessions/session/turns", json={"message": "解释材料。"}).json()
    turn_id = UUID(turn["turn_id"])
    factory = get_research_turn_service().repository_factory
    with factory.unit_of_work() as unit:
        unit.connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status="ORCHESTRATING"))
        row = unit.agent2.research_turns.get(turn_id)
    publisher = ResearchAnswerPublisher(factory, row)
    publisher.feed('{"action":"ANSWER","assistant_message":"这是一条正在生成的公开回答，尚未完成。')
    stream_url = f"/api/research/turns/{turn_id}/answer-stream"
    response = client.get(stream_url, params={"follow": "false"})
    assert response.status_code == 200 and "event: answer.delta" in response.text
    assert "no-store" in response.headers["cache-control"]
    assert "no-transform" in response.headers["cache-control"]
    sequence = response.text.split("id: ", 1)[1].split("\n", 1)[0]
    replay = client.get(stream_url, params={"follow": "false"}, headers={"Last-Event-ID": sequence})
    assert "answer.delta" not in replay.text
    active["value"] = stranger
    assert client.get(stream_url).status_code == 403
    active["value"] = owner
    assert client.get(stream_url, headers={"Last-Event-ID": "-1"}).status_code == 422
    assert client.post(f"/api/research/turns/{turn_id}/cancel").status_code == 200
    stopped = client.get(stream_url)
    assert "event: answer.stopped" in stopped.text and "answer.delta" not in stopped.text
    assert "公开回答" not in stopped.text


def test_completed_answer_stream_returns_only_the_saved_authoritative_message(api):
    from mdi_api.routers.agent2 import get_research_turn_service
    from mdi_api.research_agent.llm.schemas import StructuredLLMResult
    from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor
    from mdi_api.research_agent.registry_validation import build_default_agent2_registries

    client, _active, _owner, _viewer, _stranger, _objects = api
    turn = client.post("/api/projects/project/research/sessions/session/turns", json={"message": "解释 RDF。"}).json()
    turn_id = UUID(turn["turn_id"])

    class Provider:
        async def generate_structured(self, **kwargs):
            kwargs["request_context"]["on_answer_delta"]('{"action":"ANSWER","assistant_message":"这是一条在提交之前的草稿回答。')
            return StructuredLLMResult(provider="fake", model="fixture", latency_ms=1, repair_attempted=False, prompt_version="test", parsed={
                "contract_version": "1.0", "action": "ANSWER", "assistant_message": "**RDF** 描述原子对距离的分布。", "research_objective": None,
                "selected_scope_ref_keys": [], "scientific_requirements": [], "reusable_result_ref_keys": [], "clarification": None, "confidence": "HIGH",
            })

    target = AgentTurnProcessor(repository_factory=get_research_turn_service().repository_factory, registries=build_default_agent2_registries(), llm_client=Provider())
    assert asyncio.run(target.process(turn_id)).status == "ANSWERED"
    response = client.get(f"/api/research/turns/{turn_id}/answer-stream")
    assert "event: answer.completed" in response.text and "answer.delta" not in response.text
    frame = __import__("json").loads(response.text.split("data: ", 1)[1])
    assert frame["text"] == "**RDF** 描述原子对距离的分布。" and frame["message_id"]
    assert frame["status"] == "ANSWERED" and "草稿回答" not in response.text

    other = client.post("/api/projects/project/research/sessions/session/turns", json={"message": "同一会话的另一个问题。"}).json()
    with get_research_turn_service().repository_factory.unit_of_work() as unit:
        unit.connection.execute(update(research_turns).where(research_turns.c.id == UUID(other["turn_id"])).values(
            status="ANSWERED", assistant_final_message_id=frame["message_id"],
        ))
    mismatched = client.get(f"/api/research/turns/{other['turn_id']}/answer-stream")
    assert "answer.completed" not in mismatched.text and "RDF" not in mismatched.text


@pytest.mark.parametrize("markdown", [False, True])
@pytest.mark.parametrize("case", [
    "valid", "reused-source", "ungrounded", "missing-interpretation",
    "wrong-turn", "wrong-snapshot", "other-project", "invalid-bundle",
    "legacy-binding", "invalid-snapshot-id", "missing-snapshot",
    "snapshot-other-project", "invalid-output", "partial",
])
def test_scientific_answer_stream_and_session_share_grounded_markdown(api, monkeypatch, markdown, case):
    from datetime import datetime, timezone
    import json

    client, active, _owner, viewer, stranger, objects = api
    factory = objects.repository_factory
    monkeypatch.setattr("mdi_api.routers.research.create_engine_from_settings", lambda _settings: factory.engine)
    ref = create_ref(objects, "project")
    turn = client.post("/api/projects/project/research/sessions/session/turns", json={"message": "解释保存的 RDF。"}).json()
    turn_id = UUID(turn["turn_id"])
    source_turn_id = turn_id
    if case in {"reused-source", "wrong-turn"}:
        other = client.post("/api/projects/project/research/sessions/session/turns", json={"message": "独立来源问题。"}).json()
        source_turn_id = UUID(other["turn_id"])
    snapshot_id, interpretation_id = uuid4(), uuid4()
    bundle = ScientificResultBundle(
        schema_version="1.0", result_id=uuid4(), project_id="project", research_session_id="session",
        research_turn_id=source_turn_id, research_question="解释 RDF", source_object_refs=[ref],
        execution_status="PARTIAL" if case == "partial" else "SUCCESS",
        relevance_status="CURRENT", projection_version="agent2.result/1.0",
        result_items=[{"id": "rdf.item", "result_type": "rdf_curve", "role": "PRIMARY", "title": "RDF",
                       "artifact_ids": ["artifact-rdf"], "scientific_object_refs": [ref],
                       "fact_refs": ["rdf.first_peak"], "evidence_refs": ["evidence.rdf"]}],
        facts=[{"fact_id": "rdf.first_peak", "predicate": "rdf.first_peak_position", "subject_ref": "structure:v1",
                "value": 2.5, "unit": "angstrom", "source": {"artifact_id": "artifact-rdf", "artifact_locator": "/firstPeak"}}],
        evidence=[{"evidence_id": "evidence.rdf", "evidence_type": "structured_summary",
                   "artifact_id": "artifact-rdf", "artifact_locator": "/summary"}],
        figures=[], tables=[], output_object_refs=[], methods=[], limitations=[], warnings=[],
        provenance={"artifact_ids": ["artifact-rdf"]},
    )
    interpretation = {
        "contract_version": "1.0", "title": "RDF 解释", "answer_lead": "该方法非常准确，但结果没有这种证据。",
        "primary_findings": [{"finding_id": "finding-1", "statement": "第一峰位于 9.9 angstrom。" if case == "ungrounded" else "第一峰位于 2.5 angstrom。",
                              "importance": "HIGH", "confidence": "HIGH", "fact_refs": ["rdf.first_peak"],
                              "evidence_refs": ["evidence.rdf"], "result_item_refs": ["rdf.item"]}],
        "supporting_findings": [], "limitations": ["未来源的方法常识。"], "primary_result_refs": ["rdf.item"],
        "supporting_result_refs": [], "follow_up_suggestions": [],
    }
    message_id = f"scientific-message-{turn_id}"
    with factory.unit_of_work() as unit:
        snapshot = unit.agent2.scientific_result_snapshots.add({
            "id": snapshot_id, "project_id": "other" if case == "snapshot-other-project" else "project",
            "research_turn_id": source_turn_id, "job_id": None,
            "schema_version": "1.0", "projection_version": bundle.projection_version,
            "execution_status": bundle.execution_status.value,
            "relevance_status": "CURRENT", "source_fingerprint": str(snapshot_id),
            "bundle_json": {"invalid": True} if case == "invalid-bundle" else bundle.model_dump(mode="json"),
        })
        record = None
        if case != "missing-interpretation":
            record = unit.agent2.interpretations.add({
                "id": interpretation_id, "research_turn_id": source_turn_id if case == "wrong-turn" else turn_id,
                "project_id": "other" if case == "other-project" else "project",
                "result_snapshot_id": uuid4() if case == "missing-snapshot" else snapshot_id,
                "contract_version": "1.0", "prompt_version": "fixture", "provider": "fixture", "model": "fixture",
                "repair_attempted": False, "input_fingerprint": str(interpretation_id), "grounding_status": "VALID",
                "output_json": ["invalid"] if case == "invalid-output" else {"interpretation": interpretation},
            })
        saved = unit.agent2.research_turns.add_message({
            "id": message_id, "session_id": "session", "role": "agent",
            "content_summary": "未经当前校验的旧原文：绝对准确，峰位为 9.9 angstrom。",
            "payload_json": {"source": "agent2_scientific_interpreter", "messageKind": "ASSISTANT_FINAL",
                             "turnId": str(turn_id), "interpretationId": str(interpretation_id),
                             **({} if case == "legacy-binding" else {
                                 "sourceResultSnapshotId": "" if case == "invalid-snapshot-id" else str(
                                     uuid4() if case == "wrong-snapshot" else snapshot_id
                                 ),
                             }),
                             **({"responseFormat": "markdown"} if markdown else {})},
            "created_at": datetime.now(timezone.utc),
        })
        unit.connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
            status="PARTIAL" if case == "partial" else "COMPLETED", assistant_final_message_id=message_id,
        ))

    active["value"] = viewer
    response = client.get(f"/api/research/turns/{turn_id}/answer-stream")
    assert response.status_code == 200 and "event: answer.completed" in response.text
    frame = json.loads(response.text.split("data: ", 1)[1])
    session_response = client.get("/research-sessions/session")
    assert session_response.status_code == 200
    projected = next(item for item in session_response.json()["messages"] if item["id"] == message_id)
    assert frame["text"] == projected["content"]
    assert projected["payload"]["responseFormat"] == "markdown"
    assert frame["response_kind"] == "SCIENTIFIC_INTERPRETATION"
    assert "9.9" not in frame["text"] and "绝对准确" not in frame["text"]
    assert "非常准确" not in frame["text"] and "未来源的方法常识" not in frame["text"]
    if case in {"valid", "reused-source", "legacy-binding", "partial"}:
        assert frame["text"].startswith("## RDF 解释\n\n")
        assert frame["text"].count("第一峰位于 2.5 angstrom。") == 1
        if case == "partial":
            assert "部分完成的分析" in frame["text"]
    else:
        assert "核验" in frame["text"] or "未通过当前事实校验" in frame["text"]
    with factory.session() as session:
        assert session.agent2.research_turns.get_message(message_id) == saved
        assert session.agent2.scientific_result_snapshots.get(snapshot_id) == snapshot
        if record is not None:
            assert session.agent2.interpretations.get(interpretation_id) == record
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/answer-stream").status_code == 403
    assert client.get("/research-sessions/session").status_code == 403


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


@pytest.mark.parametrize("error_code, expected_code, expected_message", [
    ("ORCHESTRATOR_PROVIDER_UNAVAILABLE", "ORCHESTRATOR_PROVIDER_UNAVAILABLE", "模型连接暂时不可用"),
    ("ORCHESTRATOR_TIMEOUT", "ORCHESTRATOR_TIMEOUT", "模型响应超时"),
    ("ORCHESTRATOR_PROVIDER_RATE_LIMITED", "ORCHESTRATOR_PROVIDER_RATE_LIMITED", "限流或额度不足"),
    ("ORCHESTRATOR_PROVIDER_AUTH_FAILED", "ORCHESTRATOR_PROVIDER_AUTH_FAILED", "拒绝了认证"),
    ("ORCHESTRATOR_PROVIDER_REQUEST_REJECTED", "ORCHESTRATOR_PROVIDER_REQUEST_REJECTED", "拒绝了当前请求"),
    ("ORCHESTRATOR_OUTPUT_TRUNCATED", "ORCHESTRATOR_OUTPUT_TRUNCATED", "输出长度上限"),
    ("ORCHESTRATOR_INVALID_OUTPUT", "ORCHESTRATOR_INVALID_OUTPUT", "返回内容未通过"),
    ("INTERPRETATION_GROUNDING_FAILED", "INTERPRETATION_GROUNDING_FAILED", "自动解读未通过证据校验"),
    ("INTERPRETATION_SCHEMA_INVALID", "INTERPRETATION_SCHEMA_INVALID", "自动解读格式不完整"),
    ("INTERPRETATION_PROVIDER_FAILED", "INTERPRETATION_PROVIDER_FAILED", "模型未能完成自动解读"),
    ("INTERPRETATION_PROVIDER_TIMEOUT", "INTERPRETATION_PROVIDER_TIMEOUT", "模型响应超时"),
    ("INTERPRETATION_PROVIDER_UNAVAILABLE", "INTERPRETATION_PROVIDER_UNAVAILABLE", "暂时无法连接模型服务"),
    ("INTERPRETATION_PROVIDER_RATE_LIMITED", "INTERPRETATION_PROVIDER_RATE_LIMITED", "限流或额度不足"),
    ("INTERPRETATION_PROVIDER_AUTH_FAILED", "INTERPRETATION_PROVIDER_AUTH_FAILED", "认证失败"),
    ("INTERPRETATION_PROVIDER_REQUEST_REJECTED", "INTERPRETATION_PROVIDER_REQUEST_REJECTED", "拒绝了本次解读请求"),
    ("INTERPRETATION_PROVIDER_OUTPUT_TRUNCATED", "INTERPRETATION_PROVIDER_OUTPUT_TRUNCATED", "输出长度上限"),
    ("INTERPRETATION_PROVIDER_INVALID_RESPONSE", "INTERPRETATION_PROVIDER_INVALID_RESPONSE", "有效的结构化解读"),
    ("CONTEXT_ASSEMBLY_FAILED", "CONTEXT_ASSEMBLY_FAILED", "数据上下文未能准备完成"),
    ("RESEARCH_STAGE_TIMEOUT", "RESEARCH_STAGE_TIMEOUT", "原问题已保留，可以重试"),
    ("RESEARCH_QUEUE_TIMEOUT", "RESEARCH_QUEUE_TIMEOUT", "研究排队等待超时"),
    ("EXECUTION_WORKER_LOST", "EXECUTION_WORKER_LOST", "原问题和已生成的文件已保留"),
    ("EXECUTION_QUEUE_TIMEOUT", "EXECUTION_QUEUE_TIMEOUT", "科学任务排队等待超时"),
    ("RESULT_PROJECTION_TIMEOUT", "RESULT_PROJECTION_TIMEOUT", "科学结果整理长时间未完成"),
    ("INTERPRETATION_STAGE_TIMEOUT", "INTERPRETATION_STAGE_TIMEOUT", "已有科学结果仍可查看"),
    ("private-unknown-error", "RESEARCH_FAILED", "本次研究未能完成"),
])
def test_failed_turn_without_a_job_has_safe_actionable_progress(api, error_code, expected_code, expected_message):
    client, active, _owner, _viewer, stranger, objects = api
    created = client.post("/api/projects/project/research/sessions/session/turns", json={"message": "Evaluate my uploaded data"}).json()
    turn_id = UUID(created["turn_id"])
    with objects.repository_factory.unit_of_work() as unit:
        current = unit.agent2.research_turns.get(turn_id)
        unit.agent2.research_turns.compare_and_set_status(
            turn_id, expected_status=current["status"], expected_version=current["row_version"],
            target_status="FAILED", error_code=error_code,
            error_summary="private-test-credential and hidden model reasoning must not appear",
        )
    response = client.get(f"/api/research/turns/{turn_id}/progress")
    assert response.status_code == 200
    progress = response.json()
    assert progress["status"] == "FAILED"
    assert progress["steps"] == []
    assert progress["warnings"][0]["code"] == expected_code
    assert expected_message in progress["warnings"][0]["message"]
    assert "private-" not in response.text
    assert "hidden model reasoning" not in response.text
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/progress").status_code == 403


@pytest.mark.parametrize("historical", [False, True])
def test_preflight_failure_progress_replaces_generic_message_and_is_read_stable(api, monkeypatch, historical):
    from tests.test_agent2_execution import _preflight_failure
    from mdi_api.db import research_execution_summaries
    from mdi_api.research_agent.execution.supervisor import ResearchExecutionSupervisor

    client, active, _owner, _viewer, stranger, _objects = api
    engine, factory, turn_id, job_id = _preflight_failure()
    monkeypatch.setattr("mdi_api.routers.agent2.create_repository_factory", lambda: factory)
    if historical:
        ResearchExecutionSupervisor(factory).sync_for_job(job_id)
        with engine.begin() as connection:
            from sqlalchemy import select
            saved = connection.execute(select(research_execution_summaries.c.summary_json)).scalar_one()
            saved["warnings"] = []
            connection.execute(update(research_execution_summaries).values(summary_json=saved))
            connection.execute(update(research_turns).values(error_code=None, error_summary=None))
    responses = [client.get(f"/api/research/turns/{turn_id}/progress") for _ in range(2)]
    assert all(response.status_code == 200 for response in responses)
    assert responses[0].json() == responses[1].json()
    view = responses[0].json()
    assert view["status"] == "FAILED" and view["steps"][0]["status"] == "SKIPPED"
    assert [warning["code"] for warning in view["warnings"]] == ["ROOT_RESOURCE_HASH_MISMATCH"]
    assert "一致性校验" in view["warnings"][0]["message"]
    assert "模型设置" not in responses[0].text and "private" not in responses[0].text
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/progress").status_code == 403


@pytest.mark.parametrize("terminal,target", [("completed", "RESULT_PENDING"), ("failed", "FAILED"), ("cancelled", "CANCELED")])
def test_committed_execution_handoff_recovers_api_progress(api, monkeypatch, terminal, target):
    from tests.test_research_execution_handoff_recovery import _finished_execution
    from mdi_api.research_agent.recovery import StaleResearchRecoveryService
    from mdi_api.config import ApiSettings

    client, active, _owner, _viewer, stranger, _objects = api
    factory, turn_id, _ = _finished_execution(terminal)
    monkeypatch.setattr("mdi_api.routers.agent2.create_repository_factory", lambda: factory)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).reconcile_finished_execution() == 1
    response = client.get(f"/api/research/turns/{turn_id}/progress")
    assert response.status_code == 200
    progress = response.json()
    assert progress["status"] == target and progress["active_step_ids"] == []
    assert progress["result_projection_pending"] == (target == "RESULT_PENDING")
    assert progress["execution_dispatch_pending"] is False
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/progress").status_code == 403


def test_expired_execution_queue_has_terminal_progress_and_cannot_redispatch(api, monkeypatch):
    from tests.test_research_execution_queue_recovery import _queued_execution
    from tests.test_agent2_execution import CaptureQueue
    from mdi_api.research_agent.recovery import StaleResearchRecoveryService
    from mdi_api.config import ApiSettings

    client, active, _owner, _viewer, stranger, _objects = api
    factory, turn_id, job_id = _queued_execution()
    monkeypatch.setattr("mdi_api.routers.agent2.create_repository_factory", lambda: factory)
    queue = CaptureQueue()
    monkeypatch.setattr("mdi_api.routers.agent2._research_execution_queue", lambda: queue)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_execution() == 1
    response = client.get(f"/api/research/turns/{turn_id}/progress")
    assert response.status_code == 200
    progress = response.json()
    assert progress["status"] == "FAILED" and progress["active_step_ids"] == []
    assert progress["execution_dispatch_pending"] is False
    assert any(w["code"] == "EXECUTION_QUEUE_TIMEOUT" and "科学任务排队等待超时" in w["message"] for w in progress["warnings"])
    with factory.session() as session:
        assert session.repositories.jobs.get(job_id)["executionAttempt"] == 0
    redispatch = client.post(f"/api/research/turns/{turn_id}/dispatch")
    assert redispatch.status_code == 409
    assert redispatch.json()["detail"]["code"] == "EXECUTION_PLAN_NOT_READY"
    assert queue.ids == []
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/progress").status_code == 403


def test_failed_projection_progress_keeps_authorized_output_links_without_a_snapshot(api, monkeypatch):
    from tests.test_research_result_loss_recovery import _completed_execution
    from mdi_api.research_agent.recovery import StaleResearchRecoveryService
    from mdi_api.config import ApiSettings
    from datetime import datetime, timedelta, timezone

    client, active, _owner, _viewer, stranger, _objects = api
    factory, turn_id, job_id = _completed_execution()
    monkeypatch.setattr("mdi_api.routers.agent2.create_repository_factory", lambda: factory)
    with factory.engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
            updated_at=datetime.now(timezone.utc) - timedelta(minutes=16),
        ))
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_results() == 1
    response = client.get(f"/api/research/turns/{turn_id}/progress")
    assert response.status_code == 200
    progress = response.json()
    assert progress["status"] == "FAILED"
    assert progress["incremental_outputs"][0]["content_url"] == f"/api/planner/jobs/{job_id}/artifacts/saved-output/content"
    assert any(warning["code"] == "RESULT_PROJECTION_TIMEOUT" for warning in progress["warnings"])
    assert client.get(f"/api/research/turns/{turn_id}/result").status_code == 404
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/progress").status_code == 403


def test_result_execution_records_exclude_other_attempts_before_output_limit(api, monkeypatch):
    from datetime import datetime, timedelta, timezone
    from mdi_api.db import artifacts, research_execution_summaries
    from tests.test_agent2_results import _persisted_projection

    client, active, _owner, _viewer, stranger, _objects = api
    factory, turn_id, job_id, service = _persisted_projection()
    monkeypatch.setattr(service, "_enqueue_interpretation", lambda _: None)
    monkeypatch.setattr("mdi_api.routers.agent2.create_repository_factory", lambda: factory)
    with factory.engine.begin() as connection:
        connection.execute(insert(artifacts), {
            "id": "saved-recipe", "project_id": "project", "dataset_id": "dataset", "job_id": job_id,
            "tool_call_id": "call-output", "type": "recipe_json", "name": "recipe.json", "version": "1",
            "storage_key": "test/recipe.json", "size_bytes": 42, "content_type": "application/json", "content_hash": "recipe",
        })
    # Freeze the fixture before introducing unrelated same-call output rows.
    with factory.session() as session:
        summary = session.agent2.research_execution_summaries.get_for_turn(turn_id)
    summary["summary_json"]["artifact_refs"].append({"artifact_id": "saved-recipe", "step_id": "step_1", "display_label": "recipe.json"})
    with factory.engine.begin() as connection:
        connection.execute(update(research_execution_summaries).where(
            research_execution_summaries.c.id == summary["id"],
        ).values(summary_json=summary["summary_json"]))
    original_loader = service.artifact_loader
    service.artifact_loader = lambda row: {} if row["id"] == "saved-recipe" else original_loader(row)
    snapshot = service.project_turn(turn_id)
    with factory.engine.begin() as connection:
        for index in range(70):
            connection.execute(insert(artifacts), {
                "id": f"old-output-{index:02}", "project_id": "project", "dataset_id": "dataset",
                "job_id": job_id, "tool_call_id": "call-output", "type": "table_json", "name": "Old retry output",
                "version": "1", "storage_key": f"test/old-{index}.json", "size_bytes": 42, "content_hash": "old",
                "content_type": "application/json", "created_at": datetime.now(timezone.utc) - timedelta(days=1),
            })
    with factory.session() as session:
        old_page = session.repositories.artifacts.list_for_job(job_id)[:64]
        assert all(item["id"].startswith("old-output-") for item in old_page)
    response = client.get(f"/api/research/turns/{turn_id}/result")
    assert response.status_code == 200, response.text
    assert {item["id"] for item in response.json()["artifacts"]} == {"saved-output", "saved-recipe"}
    assert response.json()["tool_call_ids"] == ["call-output"]
    with factory.session() as session:
        assert session.agent2.scientific_result_snapshots.get(snapshot["id"])["bundle_json"] == snapshot["bundle_json"]
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/result").status_code == 403


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
    from mdi_api.research_agent.execution.schemas import ResearchProgressView
    ResearchProgressView.model_validate(response.json())
    assert response.json() == {
        "contract_version": "1.0",
        "turn_id": str(turn_id),
        "status": "COMPLETED",
        "response_kind": "SCIENTIFIC_EXECUTION",
        "plan_title": "历史分析",
        "steps": [],
        "active_step_ids": [],
        "completed_step_count": 0,
        "total_step_count": 0,
        "incremental_outputs": [],
        "warnings": [{"code": "HISTORICAL_ANALYSIS_PLAN_PAYLOAD_UNAVAILABLE", "message": "历史分析的执行计划详情不可用；这里只显示已保存的研究状态。"}],
        "execution_outcome": None,
        "result_projection_pending": False,
    }


@pytest.mark.parametrize("status,outcome,has_result", [
    ("FAILED", "SUCCESS", True),
    ("CANCELED", "SUCCESS", True),
    ("CANCELED", "CANCELED", False),
    ("COMPLETED", None, True),
    ("FAILED", None, False),
])
def test_missing_plan_history_preserves_saved_outcome_and_result_access(api, monkeypatch, status, outcome, has_result):
    from sqlalchemy import select
    from mdi_api.db import analysis_plans, research_execution_summaries
    from tests.test_agent2_execution import _retired_capability_execution
    from tests.test_research_result_loss_recovery import _saved_result

    client, active, _owner, _viewer, stranger, _objects = api
    factory, turn_id, job_id, _registries = _retired_capability_execution(status)
    snapshot = _saved_result(factory, turn_id) if has_result else None
    with factory.engine.begin() as connection:
        connection.execute(update(analysis_plans).values(analysis_plan_json={}))
        if outcome is None:
            connection.execute(research_execution_summaries.delete())
        else:
            connection.execute(update(research_execution_summaries).values(execution_outcome=outcome))
        if status == "FAILED":
            connection.execute(update(research_turns).values(error_code="INTERPRETATION_GROUNDING_FAILED"))
    monkeypatch.setattr("mdi_api.routers.agent2.create_repository_factory", lambda: factory)

    def saved():
        with factory.session() as session:
            return (
                session.agent2.research_turns.get(turn_id),
                session.agent2.research_execution_summaries.get_for_turn(turn_id),
                session.agent2.research_turn_events.list_for_turn(turn_id),
                session.connection.execute(select(analysis_plans)).mappings().all(),
                session.agent2.scientific_result_snapshots.get(snapshot["id"]) if snapshot else None,
            )
    original = saved()
    for _ in range(2):
        response = client.get(f"/api/research/turns/{turn_id}/progress")
        assert response.status_code == 200
        progress = response.json()
        assert progress["status"] == status and progress["execution_outcome"] == outcome
        assert progress.get("preserved_result_available", False) is has_result
        assert progress["steps"] == [] and progress["incremental_outputs"] == []
        assert all(isinstance(item["code"], str) and isinstance(item["message"], str) for item in progress["warnings"])
        assert saved() == original
    if snapshot:
        response = client.get(f"/api/research/turns/{turn_id}/result")
        assert response.status_code == 200
        assert response.json()["result_snapshot_id"] == str(snapshot["id"])
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/progress").status_code == 403


@pytest.mark.parametrize("field,value", [("job_id", "different-job"), ("research_turn_id", "different-turn"), ("execution_outcome", "UNKNOWN")])
def test_missing_plan_history_does_not_guess_from_a_mismatched_execution_summary(field, value):
    from mdi_api.routers.agent2 import _historical_terminal_progress

    turn = {"id": "turn", "job_id": "job", "status": "FAILED"}
    summary = {"research_turn_id": "turn", "job_id": "job", "execution_outcome": "SUCCESS", field: value}
    assert _historical_terminal_progress(turn, summary)["execution_outcome"] is None


@pytest.mark.parametrize("reuse_status", [None, "INTERPRETING", "FAILED", "CANCELED", "COMPLETED"])
def test_agent2_result_projection_exposes_bounded_facts_and_exact_sources(api, reuse_status):
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
        result_row = unit.agent2.scientific_result_snapshots.add({
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

    source_turn_id = turn_id
    if reuse_status:
        reused = client.post(
            "/api/projects/project/research/sessions/session/turns",
            json={"message": "Only reinterpret the saved result"},
        ).json()
        turn_id = UUID(reused["turn_id"])
        with objects.repository_factory.unit_of_work() as unit:
            source_context = unit.agent2.research_context_snapshots.get_for_turn(source_turn_id)
            unit.agent2.research_context_snapshots.add({
                **source_context, "id": uuid4(), "research_turn_id": turn_id,
                "context_fingerprint": f"reused-{turn_id}",
                "referenced_result_refs_json": [{"candidate_key": "result_1", "result_id": str(result_row["id"])}],
            })
            unit.connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
                status=reuse_status, action_type="INTERPRET_RESULT",
            ))

    response = client.get(f"/api/research/turns/{turn_id}/result")
    assert response.status_code == 200
    payload = response.json()
    assert payload["result_id"] == str(bundle.result_id)
    assert payload["research_turn_id"] == str(turn_id)
    assert payload["source_research_turn_id"] == str(source_turn_id)
    assert payload["result_snapshot_id"]
    assert payload["result_snapshot_id"] != str(bundle.result_id)
    if reuse_status in {"FAILED", "CANCELED"}:
        progress = client.get(f"/api/research/turns/{turn_id}/progress")
        assert progress.json()["preserved_result_available"] is True
    assert payload["source_object_refs"][0] == {
        **ref.model_dump(mode="json"),
        "version_no": 1,
    }
    assert payload["facts"] == [bundle.facts[0].model_dump(mode="json")]
    assert payload["input_provenance"] is None
    assert payload["evidence"] == []
    assert payload["artifacts"] == []
    assert payload["scientific_selections"][0]["semantic_locator"] == {"sample_ref": "mat-2"}
    with objects.repository_factory.session() as session:
        assert session.agent2.scientific_result_snapshots.get(result_row["id"])["bundle_json"] == bundle.model_dump(mode="json")

    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/result").status_code == 403


@pytest.mark.parametrize("tool_id", ["generation.function_curve", "viz.inline_xy", "generation.ideal_crystal"])
def test_result_api_exposes_only_the_saved_public_parameter_provenance(api, tmp_path, monkeypatch, tool_id):
    from tests.test_project_parameters import _context
    from mdi_api.application.scientific_results.projectors.parameters import ParameterResultProjector
    from mdi_api.domain.scientific_results.reference_sources import project_reference_context
    client, active, _owner, _viewer, stranger, objects = api
    turn = client.post("/api/projects/project/research/sessions/session/turns", json={"message": "查看参数结果"}).json()
    turn_id = UUID(turn["turn_id"])
    bundle = ParameterResultProjector(tool_id).project(_context(tmp_path, tool_id, monkeypatch)).bundle
    bundle.research_turn_id = turn_id
    bundle.research_session_id = "session"
    bundle.provenance.internal_diagnostic = {"private": "must-not-be-public"}
    with objects.repository_factory.unit_of_work() as unit:
        current = unit.agent2.research_turns.get(turn_id)
        unit.agent2.research_turns.compare_and_set_status(turn_id, expected_status=str(current["status"]),
            expected_version=int(current["row_version"]), target_status="COMPLETED")
        unit.agent2.scientific_result_snapshots.add({
            "id": uuid4(), "project_id": "project", "research_turn_id": turn_id, "job_id": None,
            "schema_version": bundle.schema_version, "projection_version": bundle.projection_version,
            "execution_status": bundle.execution_status.value, "relevance_status": bundle.relevance_status.value,
            "source_fingerprint": "parameter-api-test", "bundle_json": bundle.model_dump(mode="json"),
        })
    response = client.get(f"/api/research/turns/{turn_id}/result")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["source_object_refs"] == []
    assert payload["input_provenance"] == project_reference_context(bundle)
    assert "must-not-be-public" not in response.text
    assert isinstance(payload["input_provenance"]["parameter_inputs"][0]["resolved_parameters"], dict)
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/result").status_code == 403


@pytest.mark.parametrize("reference_case", [
    "exact", "absent", "no_context", "multiple", "missing", "invalid", "foreign", "running",
    "missing_event", "missing_context", "incomplete_context", "interpreting",
])
@pytest.mark.parametrize("terminal_status", ["FAILED", "CANCELED"])
def test_preplanning_terminal_can_read_only_one_explicit_owned_result(api, reference_case, terminal_status):
    from tests.test_research_result_loss_recovery import _saved_result

    client, active, _owner, _viewer, stranger, objects = api
    source_project, source_session = ("other", "other-session") if reference_case == "foreign" else ("project", "session")
    source = client.post(f"/api/projects/{source_project}/research/sessions/{source_session}/turns", json={"message": "Original science"}).json()
    source_turn_id = UUID(source["turn_id"])
    snapshot = _saved_result(objects.repository_factory, source_turn_id)
    references = [str(snapshot["id"])]
    if reference_case in {"absent", "no_context", "missing_event", "missing_context", "incomplete_context", "interpreting"}:
        references = []
    elif reference_case == "multiple":
        references.append(str(uuid4()))
    elif reference_case == "missing":
        references = [str(uuid4())]
    elif reference_case == "invalid":
        references = ["invalid-snapshot"]
    created = client.post("/api/projects/project/research/sessions/session/turns", json={
        "message": "Explain the attached result",
        "ui_context": None if reference_case == "no_context" else {"explicit_result_ids": references},
    })
    if reference_case == "invalid":
        assert created.status_code == 422
        return
    assert created.status_code == 202
    turn_id = UUID(created.json()["turn_id"])
    with objects.repository_factory.unit_of_work() as unit:
        unit.connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
            status="ORCHESTRATING" if reference_case == "running" else terminal_status,
            action_type="INTERPRET_RESULT" if reference_case == "interpreting" else None,
            error_code="ORCHESTRATOR_TIMEOUT",
        ))
        if reference_case in {"missing_event", "missing_context", "incomplete_context"}:
            from mdi_api.db import research_turn_events

            received = next(event for event in unit.agent2.research_turn_events.list_for_turn(turn_id)
                            if event["event_type"] == "TURN_RECEIVED")
            if reference_case == "missing_event":
                unit.connection.execute(research_turn_events.delete().where(research_turn_events.c.id == received["id"]))
            else:
                payload = dict(received["payload_json"])
                if reference_case == "missing_context":
                    payload.pop("ui_context")
                else:
                    payload["ui_context"] = {}
                unit.connection.execute(update(research_turn_events).where(research_turn_events.c.id == received["id"]).values(payload_json=payload))
    response = client.get(f"/api/research/turns/{turn_id}/result")
    if reference_case == "exact":
        assert response.status_code == 200
        assert response.json()["research_turn_id"] == str(turn_id)
        assert response.json()["source_research_turn_id"] == str(source_turn_id)
        assert response.json()["result_snapshot_id"] == str(snapshot["id"])
        assert response.json()["facts"] == snapshot["bundle_json"]["facts"]
    elif reference_case == "foreign":
        assert response.status_code == 403
    else:
        assert response.status_code == (404 if reference_case in {"absent", "no_context", "missing"} else 409)
        if response.status_code == 409:
            assert response.json()["detail"]["code"] == "SCIENTIFIC_RESULT_NOT_READY"
        assert "facts" not in response.json()
    progress = client.get(f"/api/research/turns/{turn_id}/progress")
    assert progress.status_code == 200
    assert progress.json().get("preserved_result_available", False) is (reference_case == "exact")
    assert progress.json()["execution_outcome"] is None
    assert progress.json()["incremental_outputs"] == []
    with objects.repository_factory.session() as session:
        turn = session.agent2.research_turns.get(turn_id)
        assert turn["status"] == ("ORCHESTRATING" if reference_case == "running" else terminal_status)
        assert turn["job_id"] is None
        assert not session.agent2.scientific_result_snapshots.list_for_turn(turn_id)
        assert session.agent2.scientific_result_snapshots.get(snapshot["id"])["bundle_json"] == snapshot["bundle_json"]
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}/result").status_code == 403


@pytest.mark.parametrize("terminal_status", ["FAILED", "CANCELED"])
@pytest.mark.parametrize("context_ready", [False, True])
def test_preexecution_terminal_retains_exact_context_for_follow_up(api, terminal_status, context_ready):
    client, _active, _owner, _viewer, _stranger, objects = api
    ref = create_ref(objects, "project").model_dump(mode="json")
    original = client.post("/api/projects/project/research/sessions/session/turns", json={
        "message": "Analyze this exact structure", "ui_context": {
            "active_object_refs": [ref], "selection_refs": [ref], "explicit_object_refs": [ref],
        },
    }).json()
    turn_id = UUID(original["turn_id"])
    if context_ready:
        ResearchTurnService(objects.repository_factory).resolve_turn_context_stub(turn_id)
    if terminal_status == "CANCELED":
        assert client.post(f"/api/research/turns/{turn_id}/cancel").status_code == 200
    else:
        with objects.repository_factory.unit_of_work() as unit:
            unit.connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
                status=terminal_status, error_code="ORCHESTRATOR_PROVIDER_UNAVAILABLE",
            ))
    detail = client.get(f"/api/research/turns/{turn_id}")
    assert detail.status_code == 200
    before = detail.json()
    assert next(message for message in before["messages"] if message["role"] == "USER")["content"] == "Analyze this exact structure"
    assert before["context"]["scope"] == [ref]
    assert before["context"]["selection"] == [ref]
    assert before["context_source"] == ("RESOLVED" if context_ready else "SUBMITTED")
    assert (before["context_snapshot_summary"] is not None) is context_ready
    assert client.get(f"/api/research/turns/{turn_id}/result").status_code == 404
    continued = client.post("/api/projects/project/research/sessions/session/turns", json={
        "message": "Explain which analyses are available", "reply_to_turn_id": str(turn_id),
        "ui_context": {"active_object_refs": before["context"]["scope"], "explicit_object_refs": [ref]},
    })
    assert continued.status_code == 202
    assert continued.json()["turn_id"] != str(turn_id)
    follow_up = client.get(f"/api/research/turns/{continued.json()['turn_id']}")
    assert follow_up.status_code == 200
    assert follow_up.json()["parent_turn_id"] == str(turn_id)
    assert client.get(f"/api/research/turns/{turn_id}").json() == before
    with objects.repository_factory.session() as session:
        assert (session.agent2.research_context_snapshots.get_for_turn(turn_id) is not None) is context_ready
        events = session.agent2.research_turn_events.list_for_turn(UUID(continued.json()["turn_id"]))
        received = next(event for event in events if event["event_type"] == "TURN_RECEIVED")
        assert received["payload_json"]["ui_context"]["active_object_refs"] == [ref]
        assert received["payload_json"]["ui_context"]["explicit_result_ids"] == []


def test_submitted_sources_keep_explicit_objects_and_semantic_selection_without_a_snapshot(api):
    client, active, _owner, _viewer, stranger, objects = api
    refs = [create_ref(objects, "project").model_dump(mode="json") for _ in range(2)]
    selection = {
        "contract_version": "1.0", "object_ref": refs[1], "viewer_id": "structure",
        "selection_type": "ATOM", "semantic_locator": {"atom_index": 2}, "display_label": "Atom 2",
        "evidence_locator": None,
    }
    created = client.post("/api/projects/project/research/sessions/session/turns", json={
        "message": "Inspect the selected atom", "ui_context": {
            "active_object_refs": [refs[0]], "explicit_object_refs": refs,
            "selection_refs": [refs[1]], "scientific_selections": [selection],
        },
    })
    assert created.status_code == 202
    turn_id = UUID(created.json()["turn_id"])
    with objects.repository_factory.session() as session:
        before_turn = session.agent2.research_turns.get(turn_id)
        before_events = session.agent2.research_turn_events.list_for_turn(turn_id)
        before_message = session.agent2.research_turns.get_message(before_turn["user_message_id"])
    detail = client.get(f"/api/research/turns/{turn_id}")
    assert detail.status_code == 200
    assert detail.json()["context"] == {"scope": refs, "selection": [refs[1]], "scientific_selection": [selection]}
    assert detail.json()["context_source"] == "SUBMITTED"
    assert detail.json()["context_snapshot_summary"] is None
    assert client.get(f"/api/research/turns/{turn_id}/context-manifest").status_code == 409
    with objects.repository_factory.session() as session:
        assert session.agent2.research_turns.get(turn_id) == before_turn
        assert session.agent2.research_turn_events.list_for_turn(turn_id) == before_events
        assert session.agent2.research_turns.get_message(before_turn["user_message_id"]) == before_message
        assert session.agent2.research_context_snapshots.get_for_turn(turn_id) is None
    ResearchTurnService(objects.repository_factory).resolve_turn_context_stub(turn_id)
    resolved = client.get(f"/api/research/turns/{turn_id}").json()
    assert resolved["context_source"] == "RESOLVED"
    assert resolved["context"]["scope"] == [refs[0]]
    assert resolved["context"]["scientific_selection"] == [selection]
    active["value"] = stranger
    assert client.get(f"/api/research/turns/{turn_id}").status_code == 403


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
