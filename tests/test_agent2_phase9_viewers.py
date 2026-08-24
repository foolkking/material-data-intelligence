from __future__ import annotations

import hashlib
import json
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, insert, select
from sqlalchemy.pool import StaticPool

from mdi_api.artifact_storage import LocalFileArtifactStorage
from mdi_api.db import (
    analysis_plans,
    artifacts,
    jobs,
    metadata,
    organizations,
    project_members,
    projects,
    research_context_snapshots,
    sessions,
    scientific_result_snapshots,
    tool_calls,
    users,
)
from mdi_api.main import create_app
from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES
from mdi_api.research_agent.schemas import CreateResearchTurnRequest, ResearchTurnUIContext, ScientificSelectionContext
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.auth import CurrentUser, get_current_user
from mdi_api.scientific_objects.schemas import ScientificObjectKind, StorageRef
from mdi_api.scientific_objects.service import ScientificObjectService
from mdi_api.scientific_viewers import ScientificViewerProjectionService, build_scientific_viewer_registry
from mdi_api.unit_of_work import RepositoryFactory


def _environment(tmp_path):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    owner = CurrentUser(id="owner", email="owner@example.invalid", displayName="Owner", roles=[])
    stranger = CurrentUser(id="stranger", email="stranger@example.invalid", displayName="Stranger", roles=[])
    with engine.begin() as connection:
        connection.execute(insert(users), [
            {"id": owner.id, "email": owner.email, "display_name": owner.displayName, "is_active": True},
            {"id": stranger.id, "email": stranger.email, "display_name": stranger.displayName, "is_active": True},
        ])
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(insert(projects), {"id": "project", "organization_id": "org", "name": "Project", "created_by": owner.id})
        connection.execute(insert(project_members), {"project_id": "project", "user_id": owner.id, "role": "owner"})
        connection.execute(insert(sessions), {"id": "session", "project_id": "project", "mode": "project", "status": "active", "created_by": owner.id})
    factory = RepositoryFactory(engine)
    storage = LocalFileArtifactStorage(tmp_path / "artifacts")
    objects = ScientificObjectService(factory, DEFAULT_AGENT2_REGISTRIES.object_types)
    return engine, factory, storage, objects, owner, stranger


def _object(objects, storage, *, object_type: str, kind: ScientificObjectKind, payload, name: str = "Viewer source"):
    logical = objects.create_object(project_id="project", kind=kind, object_type=object_type, display_name=name, created_by_user_id="owner")
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    key = f"phase9/{uuid4().hex}.json"
    stored = storage.put_bytes(key, raw, content_type="application/json")
    version = objects.create_version(
        logical["id"],
        object_type=object_type,
        object_schema_version="1.0",
        source_resource_refs=[{"scope": "system_fixture", "resource_id": name}],
        parent_object_version_refs=[],
        normalized_payload_ref=StorageRef(
            storage_backend="local",
            object_key=stored.storage_key,
            checksum=stored.sha256,
            media_type="application/json",
            byte_size=stored.size_bytes,
        ),
        content_hash=hashlib.sha256(raw).hexdigest(),
        semantic_hash=f"semantic-{uuid4().hex}",
        canonical_metadata={"formula": "LiFePO4"},
        created_by_user_id="owner",
    )
    return logical, version


def test_phase9_registry_covers_every_current_scientific_object_type():
    registry = build_scientific_viewer_registry()
    expected = {
        "materials.dataset", "structure.crystal", "trajectory.atomic",
        "diffraction.xrd.experimental", "diffraction.xrd.theoretical",
        "electronic.band_structure", "electronic.dos",
        "phonon.band_structure", "phonon.dos", "volumetric.charge_density",
    }
    assert {item.object_type for item in registry.list()} == expected
    assert all(item.support == "PROFESSIONAL" for item in registry.list())
    assert registry.resolve("archive.generic").support == "FALLBACK"


def test_phase9_projection_is_exact_version_and_bounds_large_tables(tmp_path):
    _engine, factory, storage, objects, _owner, _stranger = _environment(tmp_path)
    logical, first = _object(objects, storage, object_type="materials.dataset", kind=ScientificObjectKind.DATASET, payload={"rows": [{"id": index} for index in range(620)]})
    _logical, second = logical, objects.create_version(
        logical["id"], object_type="materials.dataset", object_schema_version="1.0",
        source_resource_refs=[{"scope": "system_fixture", "resource_id": "v2"}], parent_object_version_refs=[],
        normalized_payload_ref=StorageRef(storage_backend="local", object_key=storage.put_json("phase9/v2.json", {"rows": [{"id": "v2"}]}).storage_key, checksum=storage.put_json("phase9/v2-copy.json", {"rows": [{"id": "v2"}]}).sha256),
        content_hash="v2-content", semantic_hash="v2-semantic", canonical_metadata={}, created_by_user_id="owner",
    )
    projection = ScientificViewerProjectionService(factory, storage, build_scientific_viewer_registry()).project(logical["id"], first["id"])
    assert projection.version_id == first["id"]
    assert projection.version_id != second["id"]
    assert projection.is_current_version is False
    assert len(projection.payload["rows"]) == 500
    assert projection.omitted_item_count == 120
    assert projection.viewer.renderer_key == "scientific-table"


def test_phase9_volumetric_projection_omits_unbounded_scalar_array(tmp_path):
    _engine, factory, storage, objects, _owner, _stranger = _environment(tmp_path)
    logical, version = _object(
        objects, storage,
        object_type="volumetric.charge_density", kind=ScientificObjectKind.VOLUMETRIC,
        payload={"shape": [65, 65, 65], "values": [0.0] * 274_625},
    )
    projection = ScientificViewerProjectionService(factory, storage, build_scientific_viewer_registry()).project(logical["id"], version["id"])
    assert projection.payload["shape"] == [65, 65, 65]
    assert "values" not in projection.payload
    assert projection.payload["value_count"] == 274_625
    assert projection.omitted_item_count == 274_625


def test_phase9_authorized_viewer_api_is_read_only_and_cross_project_safe(tmp_path, monkeypatch):
    engine, factory, storage, objects, owner, stranger = _environment(tmp_path)
    logical, version = _object(objects, storage, object_type="structure.crystal", kind=ScientificObjectKind.STRUCTURE, payload={"sites": [{"species": "Li", "abc": [0, 0, 0]}]})
    monkeypatch.setattr("mdi_api.routers.agent2.get_scientific_object_service", lambda: objects)
    monkeypatch.setattr("mdi_api.routers.agent2.create_repository_factory", lambda: factory)
    monkeypatch.setattr("mdi_api.routers.agent2.create_artifact_storage_from_settings", lambda _settings: storage)
    active = {"user": owner}
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: active["user"]
    client = TestClient(app)

    tables = (analysis_plans, jobs, tool_calls, artifacts, scientific_result_snapshots)
    with engine.connect() as connection:
        before = [connection.execute(select(func.count()).select_from(table)).scalar_one() for table in tables]
    response = client.get(f"/api/scientific-objects/{logical['id']}/versions/{version['id']}/viewer")
    with engine.connect() as connection:
        after = [connection.execute(select(func.count()).select_from(table)).scalar_one() for table in tables]
    assert response.status_code == 200
    assert response.json()["version_id"] == str(version["id"])
    assert response.json()["viewer"]["renderer_key"] == "structure-3d"
    assert before == after == [0, 0, 0, 0, 0]

    active["user"] = stranger
    rejected = client.get(f"/api/scientific-objects/{logical['id']}/versions/{version['id']}/viewer")
    assert rejected.status_code == 403
    assert "LiFePO4" not in rejected.text and "Viewer source" not in rejected.text


def test_phase9_semantic_selection_is_exact_and_immutable_turn_evidence(tmp_path):
    engine, factory, storage, objects, owner, _stranger = _environment(tmp_path)
    logical, version = _object(
        objects, storage, object_type="structure.crystal", kind=ScientificObjectKind.STRUCTURE,
        payload={"sites": [{"species": "O", "abc": [0.25, 0.25, 0.25]}]},
        name="LiFePO4 structure",
    )
    object_ref = {
        "object_id": logical["id"], "version_id": version["id"],
        "project_id": "project", "object_type": "structure.crystal",
        "display_name": "LiFePO4 structure",
    }
    turns = ResearchTurnService(factory)
    first = turns.receive_turn(
        project_id="project", session_id="session", current_user=owner,
        request=CreateResearchTurnRequest(
            message="分析这个氧位点的局部环境",
            ui_context=ResearchTurnUIContext(
                active_object_refs=[object_ref], selection_refs=[object_ref],
                scientific_selections=[ScientificSelectionContext(
                    object_ref=object_ref, viewer_id="structure.3d",
                    selection_type="PERIODIC_SITE", semantic_locator={"site_id": "site-12", "species": "O"},
                    display_label="O 位点 12",
                )],
            ),
        ),
    )
    turns.resolve_turn_context_stub(first.turn_id)
    with engine.connect() as connection:
        snapshot = connection.execute(
            select(research_context_snapshots).where(research_context_snapshots.c.research_turn_id == first.turn_id)
        ).mappings().one()
        original = json.loads(json.dumps(snapshot["scientific_selections_json"], default=str))
    assert original[0]["semantic_locator"] == {"site_id": "site-12", "species": "O"}
    assert str(original[0]["object_ref"]["version_id"]) == str(version["id"])

    second = turns.receive_turn(
        project_id="project", session_id="session", current_user=owner,
        request=CreateResearchTurnRequest(
            message="改看另一个位点",
            ui_context=ResearchTurnUIContext(
                selection_refs=[object_ref],
                scientific_selections=[ScientificSelectionContext(
                    object_ref=object_ref, viewer_id="structure.3d",
                    selection_type="PERIODIC_SITE", semantic_locator={"site_id": "site-13"},
                    display_label="O 位点 13",
                )],
            ),
        ),
    )
    turns.resolve_turn_context_stub(second.turn_id)
    with engine.connect() as connection:
        persisted = connection.execute(
            select(research_context_snapshots.c.scientific_selections_json).where(
                research_context_snapshots.c.research_turn_id == first.turn_id
            )
        ).scalar_one()
    assert persisted == snapshot["scientific_selections_json"]
