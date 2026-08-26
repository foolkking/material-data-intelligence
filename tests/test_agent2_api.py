from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert
from sqlalchemy.pool import StaticPool

from mdi_api.db import metadata, organizations, project_members, projects, sessions, users
from mdi_api.artifact_storage import LocalFileArtifactStorage
from mdi_api.main import create_app
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor
from mdi_api.research_agent.registry_validation import build_default_agent2_registries
from mdi_api.routers.auth import CurrentUser, get_current_user
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.schemas import (
    ScientificObjectKind,
    ScientificObjectRef,
    StorageRef,
)
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
    monkeypatch.setattr("mdi_api.routers.agent2.create_repository_factory", lambda: factory)
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
