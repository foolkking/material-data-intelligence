from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import create_engine, insert
from sqlalchemy.pool import StaticPool

from mdi_api.artifact_storage import LocalFileArtifactStorage
from mdi_api.db import datasets, metadata, organizations, projects, users
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.schemas import ScientificObjectKind, StorageRef
from mdi_api.scientific_objects.service import ScientificObjectService
from mdi_api.unit_of_work import RepositoryFactory
from mdi_workers.object_store import DurableObjectStoreResolver
from mdi_workers.source_resources import SOURCE_RESOURCE_INDEX_KEY


def _fixture(tmp_path):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    suffix = uuid4().hex[:8]
    project_id, dataset_id = f"project-{suffix}", f"dataset-{suffix}"
    with engine.begin() as connection:
        connection.execute(insert(users), {"id": "owner", "email": "owner@local.invalid", "display_name": "Owner", "is_active": True})
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(insert(projects), {"id": project_id, "organization_id": "org", "name": "Project", "created_by": "owner"})
        connection.execute(insert(datasets), {"id": dataset_id, "project_id": project_id, "name": "Dataset", "status": "profile_ready", "metadata_json": {}, "created_by": "owner"})
    factory = RepositoryFactory(engine)
    storage = LocalFileArtifactStorage(tmp_path)
    service = ScientificObjectService(factory, build_default_object_type_registry())
    logical = service.create_object(
        project_id=project_id,
        kind=ScientificObjectKind.STRUCTURE,
        object_type="structure.crystal",
        display_name="Exact historical structure",
        created_by_user_id="owner",
    )
    return engine, factory, storage, service, logical, project_id, dataset_id


def _create_version(service, storage, logical, project_id, dataset_id, *, label):
    payload = {"@module": "pymatgen.core.structure", "@class": "Structure", "label": label}
    stored = storage.put_json(f"projects/{project_id}/agent2/{label}.json", payload)
    version = service.create_version(
        logical["id"],
        object_type="structure.crystal",
        object_schema_version="1.0",
        source_resource_refs=[{"project_id": project_id, "dataset_id": dataset_id}],
        parent_object_version_refs=[],
        normalized_payload_ref=StorageRef(
            storage_backend="local",
            object_key=stored.storage_key,
            checksum=stored.sha256,
            media_type="application/json",
            byte_size=stored.size_bytes,
        ),
        content_hash=stored.sha256,
        semantic_hash=f"semantic-{label}",
        canonical_metadata={"label": label},
        created_by_user_id="owner",
    )
    return version, payload


def _plan(version_id):
    return {
        "steps": [{
            "stepId": "step_1",
            "inputRefs": [{
                "refType": "normalized_object",
                "ref": str(version_id),
                "objectType": "Structure",
            }],
        }],
    }


def test_worker_hydrates_the_exact_historical_version_not_current(tmp_path):
    _engine, factory, storage, service, logical, project_id, dataset_id = _fixture(tmp_path)
    version_1, payload_1 = _create_version(service, storage, logical, project_id, dataset_id, label="v1")
    version_2, _payload_2 = _create_version(service, storage, logical, project_id, dataset_id, label="v2")

    hydrated = DurableObjectStoreResolver(
        artifact_storage=storage,
        repository_factory=factory,
    ).hydrate_agent2_sources(
        {},
        job={"projectId": project_id, "datasetId": dataset_id},
        plan_payload=_plan(version_1["id"]),
    )

    assert hydrated[str(version_1["id"])] == payload_1
    assert str(version_2["id"]) not in hydrated
    identity = hydrated[SOURCE_RESOURCE_INDEX_KEY][str(version_1["id"])]
    assert identity["objectType"] == "Structure"
    assert identity["datasetId"] == dataset_id


def test_worker_rejects_tampered_exact_version_payload(tmp_path):
    _engine, factory, storage, service, logical, project_id, dataset_id = _fixture(tmp_path)
    version, _payload = _create_version(service, storage, logical, project_id, dataset_id, label="v1")
    storage.put_json(f"projects/{project_id}/agent2/v1.json", {"label": "tampered"})

    with pytest.raises(ValueError, match="checksum mismatch"):
        DurableObjectStoreResolver(
            artifact_storage=storage,
            repository_factory=factory,
        ).hydrate_agent2_sources(
            {},
            job={"projectId": project_id, "datasetId": dataset_id},
            plan_payload=_plan(version["id"]),
        )


def test_worker_rejects_cross_project_exact_version(tmp_path):
    _engine, factory, storage, service, logical, project_id, dataset_id = _fixture(tmp_path)
    version, _payload = _create_version(service, storage, logical, project_id, dataset_id, label="v1")

    with pytest.raises(ValueError, match="another Project"):
        DurableObjectStoreResolver(
            artifact_storage=storage,
            repository_factory=factory,
        ).hydrate_agent2_sources(
            {},
            job={"projectId": "foreign-project", "datasetId": dataset_id},
            plan_payload=_plan(version["id"]),
        )
