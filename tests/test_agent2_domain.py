from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, func, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool

from mdi_api.agent2_errors import (
    ConcurrentTurnModification,
    InvalidScientificObjectRelationship,
    InvalidScientificObjectVersion,
    ScientificObjectTypeNotRegistered,
    UnauthorizedScientificObjectReference,
)
from mdi_api.db import (
    analysis_plans,
    jobs,
    messages,
    metadata,
    organizations,
    projects,
    research_turn_events,
    research_turns,
    sessions,
    tool_calls,
    users,
)
from mdi_api.artifact_storage import LocalFileArtifactStorage
from mdi_api.research_agent.schemas import CreateResearchTurnRequest, ResearchTurnStatus
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.auth import CurrentUser
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.schemas import (
    ScientificDatasetFilter,
    ScientificDatasetQueryRequest,
    ScientificObjectAvailability,
    ScientificObjectKind,
    ScientificObjectRef,
    ScientificObjectVersionRef,
    StorageRef,
)
from mdi_api.scientific_objects.service import ScientificObjectService
from mdi_api.scientific_results.schemas import ResultExecutionStatus, ResultRelevanceStatus, ScientificResultBundle
from mdi_api.scientific_results.service import ScientificResultSnapshotService
from mdi_api.unit_of_work import RepositoryFactory


def foundation():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    owner = CurrentUser(id="owner", email="owner@example.invalid", displayName="Owner", roles=[])
    with engine.begin() as connection:
        connection.execute(insert(users), {"id": owner.id, "email": owner.email, "display_name": owner.displayName, "is_active": True})
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(insert(projects), [
            {"id": "project", "organization_id": "org", "name": "Project", "created_by": owner.id},
            {"id": "other", "organization_id": "org", "name": "Other", "created_by": owner.id},
        ])
        connection.execute(insert(sessions), [
            {"id": "session", "project_id": "project", "mode": "project", "status": "active", "created_by": owner.id},
            {"id": "other-session", "project_id": "other", "mode": "project", "status": "active", "created_by": owner.id},
        ])
    factory = RepositoryFactory(engine)
    return engine, owner, factory, ScientificObjectService(factory, build_default_object_type_registry()), ResearchTurnService(factory)


def storage(key: str) -> StorageRef:
    return StorageRef(storage_backend="minio", object_key=key, checksum=f"checksum-{key}", media_type="application/json", byte_size=12)


def create_structure(service: ScientificObjectService, project_id: str, name: str = "Si"):
    return service.create_object(
        project_id=project_id, kind=ScientificObjectKind.STRUCTURE,
        object_type="structure.crystal", display_name=name, created_by_user_id="owner",
    )


def create_version(service: ScientificObjectService, logical: dict, key: str, parents=None):
    return service.create_version(
        logical["id"], object_type="structure.crystal", object_schema_version="1.0",
        source_resource_refs=[{"scope": "system_fixture", "resource_id": key}],
        parent_object_version_refs=parents or [], normalized_payload_ref=storage(key),
        content_hash=f"content-{key}", semantic_hash=f"semantic-{key}",
        canonical_metadata={"fixture": key}, availability_status=ScientificObjectAvailability.AVAILABLE,
        created_by_user_id="owner",
    )


def version_ref(logical: dict, version: dict, project_id: str) -> ScientificObjectVersionRef:
    return ScientificObjectVersionRef(
        object_id=logical["id"], version_id=version["id"], project_id=project_id,
        object_type="structure.crystal",
    )


def test_scientific_object_versions_are_immutable_and_historical():
    _engine, _owner, _factory, service, _turns = foundation()
    logical = create_structure(service, "project")
    v1 = create_version(service, logical, "v1")
    v2 = create_version(service, logical, "v2")
    current = service.get_object(logical["id"])
    assert current["current_version_id"] == v2["id"]
    assert current["row_version"] == 3
    assert service.get_version(logical["id"], v1["id"])["content_hash"] == "content-v1"
    assert [row["version_no"] for row in service.list_versions(logical["id"])] == [1, 2]

    second = create_structure(service, "project", "Ge")
    other_v1 = create_version(service, second, "other")
    with pytest.raises(InvalidScientificObjectVersion):
        service.set_current_version(logical["id"], other_v1["id"])
    with pytest.raises(ScientificObjectTypeNotRegistered):
        service.create_object(project_id="project", kind=ScientificObjectKind.STRUCTURE, object_type="structure.unknown", display_name="Unknown")
    with pytest.raises(InvalidScientificObjectVersion):
        service.create_object(project_id="project", kind=ScientificObjectKind.TABLE, object_type="structure.crystal", display_name="Wrong kind")


def test_parent_project_cycle_relationship_and_archive_rules():
    _engine, _owner, factory, service, _turns = foundation()
    a = create_structure(service, "project", "A")
    av1 = create_version(service, a, "a1")
    b = create_structure(service, "project", "B")
    bv1 = create_version(service, b, "b1", [version_ref(a, av1, "project")])
    with pytest.raises(InvalidScientificObjectVersion, match="cycle"):
        create_version(service, a, "a2", [version_ref(b, bv1, "project")])

    outside = create_structure(service, "other", "Outside")
    outside_v1 = create_version(service, outside, "outside")
    with pytest.raises(UnauthorizedScientificObjectReference):
        create_version(service, b, "b2", [version_ref(outside, outside_v1, "other")])
    with pytest.raises(UnauthorizedScientificObjectReference):
        service.create_version(
            b["id"], object_type="structure.crystal", object_schema_version="1.0",
            source_resource_refs=[{"project_id": "other", "resource_id": "x"}],
            parent_object_version_refs=[], normalized_payload_ref=storage("bad-source"),
            content_hash="content", semantic_hash="semantic", canonical_metadata={},
        )

    relationship = service.create_relationship(
        project_id="project", source_version_id=bv1["id"], target_version_id=av1["id"], relation_type="derived_from",
    )
    assert relationship["relation_type"] == "derived_from"
    with pytest.raises(InvalidScientificObjectRelationship):
        service.create_relationship(project_id="project", source_version_id=av1["id"], target_version_id=av1["id"], relation_type="derived_from")
    with pytest.raises(IntegrityError):
        service.create_relationship(project_id="project", source_version_id=bv1["id"], target_version_id=av1["id"], relation_type="derived_from")
    assert len(service.list_relationships(a["id"])) == 1
    archived = service.archive(a["id"])
    assert archived["lifecycle_status"] == "ARCHIVED" and archived["archived_at"] is not None
    assert service.get_version(a["id"], av1["id"])["version_no"] == 1

    with factory.unit_of_work() as unit:
        with pytest.raises(IntegrityError):
            unit.agent2.scientific_objects.add_version({
                **av1,
                "id": uuid4(),
                "source_resource_refs_json": av1["source_resource_refs_json"],
                "parent_object_version_refs_json": av1["parent_object_version_refs_json"],
                "normalized_payload_ref_json": av1["normalized_payload_ref_json"],
                "canonical_metadata_json": av1["canonical_metadata_json"],
            })


def test_object_metadata_archive_restore_and_rename_preserve_versions():
    _engine, _owner, _factory, service, _turns = foundation()
    logical = create_structure(service, "project", "Original")
    v1 = create_version(service, logical, "stable")

    renamed = service.update_metadata(logical["id"], display_name="Renamed structure")
    assert renamed["display_name"] == "Renamed structure"
    assert renamed["lifecycle_status"] == "ACTIVE"

    archived = service.update_metadata(logical["id"], archived=True)
    assert archived["lifecycle_status"] == "ARCHIVED"
    assert archived["archived_at"] is not None
    assert archived["current_version_id"] == v1["id"]

    restored = service.update_metadata(logical["id"], archived=False)
    assert restored["lifecycle_status"] == "ACTIVE"
    assert restored["archived_at"] is None
    assert restored["current_version_id"] == v1["id"]
    assert service.get_version(logical["id"], v1["id"])["content_hash"] == "content-stable"

    with pytest.raises(InvalidScientificObjectVersion, match="at least one"):
        service.update_metadata(logical["id"])
    with pytest.raises(InvalidScientificObjectVersion, match="must not be blank"):
        service.update_metadata(logical["id"], display_name="   ")


def test_typed_dataset_query_uses_stable_identity_and_bounds(tmp_path):
    _engine, _owner, _factory, service, _turns = foundation()
    storage_backend = LocalFileArtifactStorage(tmp_path)
    payload = [
        {"sample_id": "s-2", "formula": "SiO2", "band_gap": 1.2},
        {"sample_id": "s-1", "formula": "Si", "band_gap": 0.0},
        {"sample_id": "s-3", "formula": "Ge", "band_gap": 0.7},
    ]
    stored = storage_backend.put_json("project/dataset.json", payload)
    logical = service.create_object(
        project_id="project",
        kind=ScientificObjectKind.DATASET,
        object_type="materials.dataset",
        display_name="Canonical materials",
        created_by_user_id="owner",
    )
    version = service.create_version(
        logical["id"],
        object_type="materials.dataset",
        object_schema_version="1.0",
        source_resource_refs=[{"scope": "system_fixture", "resource_id": "dataset-query"}],
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
        canonical_metadata={"row_count": len(payload), "sample_identity": "sample_id"},
        created_by_user_id="owner",
    )
    result = service.query_dataset_version(
        logical["id"],
        version["id"],
        storage=storage_backend,
        request=ScientificDatasetQueryRequest(
            filters=[ScientificDatasetFilter(column="band_gap", operator="gt", value=0)],
            sort_by="band_gap",
            descending=True,
            columns=["sample_id", "formula", "band_gap"],
            limit=2,
        ),
    )
    assert result["total_matching"] == 2
    assert [row["_stable_id"] for row in result["items"]] == ["s-2", "s-3"]
    assert [row["formula"] for row in result["items"]] == ["SiO2", "Ge"]
    with pytest.raises(InvalidScientificObjectVersion, match="unknown dataset column"):
        service.query_dataset_version(
            logical["id"],
            version["id"],
            storage=storage_backend,
            request=ScientificDatasetQueryRequest(filters=[ScientificDatasetFilter(column="unknown", value="x")]),
        )


def test_concurrent_version_allocation_is_unique_and_ordered():
    _engine, _owner, _factory, service, _turns = foundation()
    logical = create_structure(service, "project")
    create_version(service, logical, "base")
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda index: create_version(service, logical, f"v{index}"), range(2, 6)))
    assert sorted(row["version_no"] for row in rows) == [2, 3, 4, 5]
    assert [row["version_no"] for row in service.list_versions(logical["id"])] == [1, 2, 3, 4, 5]


def test_receive_turn_is_atomic_no_llm_no_plan_no_job_no_tool_call(monkeypatch):
    engine, owner, _factory, _objects, turns = foundation()
    import mdi_llm.providers as providers

    def forbidden(*_args, **_kwargs):
        raise AssertionError("Phase 1 receive must not call an LLM provider")

    monkeypatch.setattr(providers.MockLLMProvider, "generate_plan", forbidden)
    monkeypatch.setattr(providers.DeepSeekProvider, "generate_plan", forbidden)
    monkeypatch.setattr(providers.OpenAICompatibleProvider, "generate_plan", forbidden)
    with engine.connect() as connection:
        before = {
            "plans": connection.execute(select(func.count()).select_from(analysis_plans)).scalar_one(),
            "jobs": connection.execute(select(func.count()).select_from(jobs)).scalar_one(),
            "tools": connection.execute(select(func.count()).select_from(tool_calls)).scalar_one(),
        }
    response = turns.receive_turn(
        project_id="project", session_id="session",
        request=CreateResearchTurnRequest(message="Inspect the current structure"), current_user=owner,
    )
    assert response.status == ResearchTurnStatus.RECEIVED
    with engine.connect() as connection:
        assert connection.execute(select(func.count()).select_from(messages)).scalar_one() == 1
        assert connection.execute(select(func.count()).select_from(research_turns)).scalar_one() == 1
        assert connection.execute(select(func.count()).select_from(research_turn_events)).scalar_one() == 1
        after = {
            "plans": connection.execute(select(func.count()).select_from(analysis_plans)).scalar_one(),
            "jobs": connection.execute(select(func.count()).select_from(jobs)).scalar_one(),
            "tools": connection.execute(select(func.count()).select_from(tool_calls)).scalar_one(),
        }
    assert after == before


def test_concurrent_turn_sequence_and_cas_are_deterministic():
    _engine, owner, _factory, _objects, turns = foundation()
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(
            lambda index: turns.receive_turn(
                project_id="project", session_id="session",
                request=CreateResearchTurnRequest(message=f"Question {index}"), current_user=owner,
            ),
            range(12),
        ))
    assert sorted(row.sequence_no for row in rows) == list(range(1, 13))

    target = rows[0]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(
            turns.transition,
            turn_id=target.turn_id,
            expected_status=ResearchTurnStatus.RECEIVED,
            expected_version=1,
            target_status=ResearchTurnStatus.RESOLVING_CONTEXT,
        ) for _ in range(2)]
    results = []
    errors = []
    for future in futures:
        try:
            results.append(future.result())
        except Exception as exc:
            errors.append(exc)
    assert len(results) == 1
    assert len(errors) == 1 and isinstance(errors[0], ConcurrentTurnModification)


def test_receive_turn_can_branch_from_terminal_turn_without_mutating_parent():
    engine, owner, factory, _objects, turns = foundation()
    parent_turn_id = uuid4()
    parent_message_id = f"message_{uuid4().hex}"
    now = datetime.now(timezone.utc)
    with factory.unit_of_work() as unit:
        unit.agent2.research_turns.add_message({
            "id": parent_message_id,
            "session_id": "session",
            "role": "user",
            "content_summary": "Original research question",
            "payload_json": {"source": "test"},
            "created_at": now,
        })
        unit.agent2.research_turns.add({
            "id": parent_turn_id,
            "project_id": "project",
            "research_session_id": "session",
            "sequence_no": 1,
            "parent_turn_id": None,
            "user_message_id": parent_message_id,
            "action_type": "ANALYZE",
            "status": ResearchTurnStatus.COMPLETED.value,
            "row_version": 2,
            "created_at": now,
            "updated_at": now,
            "completed_at": now,
        })

    child = turns.receive_turn(
        project_id="project",
        session_id="session",
        request=CreateResearchTurnRequest(
            message="Revised research question",
            reply_to_turn_id=parent_turn_id,
        ),
        current_user=owner,
    )

    with factory.session() as session:
        parent = session.agent2.research_turns.get(parent_turn_id)
        child_row = session.agent2.research_turns.get(child.turn_id)
    assert parent["status"] == ResearchTurnStatus.COMPLETED.value
    assert parent["user_message_id"] == parent_message_id
    assert child_row["parent_turn_id"] == parent_turn_id
    assert child_row["status"] == ResearchTurnStatus.RECEIVED.value


def test_context_stub_stops_at_orchestrating_and_result_snapshot_round_trips():
    _engine, owner, factory, objects, turns = foundation()
    logical = create_structure(objects, "project")
    version = create_version(objects, logical, "context")
    ref = ScientificObjectRef(
        object_id=logical["id"], version_id=version["id"], project_id="project",
        object_type="structure.crystal", display_name="Si",
    )
    response = turns.receive_turn(
        project_id="project", session_id="session",
        request=CreateResearchTurnRequest(message="Inspect", ui_context={"active_object_refs": [ref], "selection_refs": []}),
        current_user=owner,
    )
    resolved = turns.resolve_turn_context_stub(response.turn_id)
    assert resolved["status"] == ResearchTurnStatus.ORCHESTRATING.value
    view = turns.get_turn(response.turn_id, owner)
    assert view["status"] == ResearchTurnStatus.ORCHESTRATING.value
    assert view["context_snapshot_summary"]["active_object_count"] == 1

    bundle = ScientificResultBundle(
        schema_version="1.0", result_id=uuid4(), project_id="project", research_session_id="session",
        research_turn_id=response.turn_id, research_question="Inspect", source_object_refs=[ref],
        execution_status=ResultExecutionStatus.PARTIAL, relevance_status=ResultRelevanceStatus.CURRENT,
        result_items=[], facts=[], figures=[], tables=[], output_object_refs=[], evidence=[], methods=[],
        limitations=[], warnings=[], provenance={"fixture": True}, projection_version="fixture/1.0",
    )
    snapshots = ScientificResultSnapshotService(factory)
    first = snapshots.persist_snapshot(bundle, "source-fingerprint")
    replay = snapshots.persist_snapshot(bundle, "source-fingerprint")
    assert first["id"] == replay["id"]
    assert snapshots.get_latest_for_turn(response.turn_id) == bundle
    assert turns.get_turn(response.turn_id, owner)["result_available"] is True

    outside = create_structure(objects, "other", "Outside")
    outside_version = create_version(objects, outside, "outside-result")
    outside_ref = ScientificObjectRef(
        object_id=outside["id"], version_id=outside_version["id"], project_id="other",
        object_type="structure.crystal", display_name="Outside",
    )
    unauthorized_bundle = bundle.model_copy(
        update={"source_object_refs": [outside_ref]},
    )
    with pytest.raises(InvalidScientificObjectVersion, match="unauthorized"):
        snapshots.persist_snapshot(unauthorized_bundle, "outside-fingerprint")
