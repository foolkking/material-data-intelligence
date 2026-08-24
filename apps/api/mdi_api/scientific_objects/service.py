from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import re
import threading
from typing import Any, Iterator
from uuid import UUID, uuid4

from sqlalchemy import select

from mdi_api.agent2_errors import (
    InvalidScientificObjectRelationship,
    InvalidScientificObjectVersion,
    UnauthorizedScientificObjectReference,
)
from mdi_api.db import datasets
from mdi_api.artifact_storage import ArtifactStorage
from mdi_api.scientific_objects.registry import ObjectTypeRegistry
from mdi_api.scientific_objects.schemas import (
    ScientificObjectAvailability,
    ScientificObjectKind,
    ScientificObjectVersionRef,
    StorageRef,
)
from mdi_api.unit_of_work import RepositoryFactory


CANONICAL_RELATIONS = frozenset({
    "derived_from", "contains", "member_of", "has_structure", "associated_with",
    "prediction_for", "measurement_of", "comparison_of", "aligned_with", "companion_of",
})
_NAMESPACED_RELATION = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
_locks_guard = threading.Lock()
_object_locks: dict[str, threading.Lock] = {}


@contextmanager
def _object_lock(object_id: UUID) -> Iterator[None]:
    key = str(object_id)
    with _locks_guard:
        lock = _object_locks.setdefault(key, threading.Lock())
    with lock:
        yield


class ScientificObjectService:
    def __init__(self, repository_factory: RepositoryFactory, object_types: ObjectTypeRegistry) -> None:
        self.repository_factory = repository_factory
        self.object_types = object_types

    def create_object(
        self,
        *,
        project_id: str,
        kind: ScientificObjectKind,
        object_type: str,
        display_name: str,
        created_by_user_id: str | None = None,
    ) -> dict[str, Any]:
        manifest = self.object_types.require(object_type)
        if manifest.kind != kind:
            raise InvalidScientificObjectVersion(f"{object_type} belongs to {manifest.kind.value}, not {kind.value}")
        object_id = uuid4()
        with self.repository_factory.unit_of_work() as unit:
            return unit.agent2.scientific_objects.add_object({
                "id": object_id,
                "project_id": project_id,
                "kind": kind.value,
                "object_type": object_type,
                "display_name": display_name,
                "lifecycle_status": "ACTIVE",
                "created_by_user_id": created_by_user_id,
                "row_version": 1,
            })

    def create_version(
        self,
        object_id: UUID,
        *,
        object_type: str,
        object_schema_version: str,
        source_resource_refs: list[dict[str, Any]],
        parent_object_version_refs: list[ScientificObjectVersionRef],
        normalized_payload_ref: StorageRef,
        content_hash: str,
        semantic_hash: str,
        canonical_metadata: dict[str, Any],
        availability_status: ScientificObjectAvailability = ScientificObjectAvailability.AVAILABLE,
        semantic_profile_ref: dict[str, Any] | None = None,
        created_by_user_id: str | None = None,
    ) -> dict[str, Any]:
        if not content_hash.strip() or not semantic_hash.strip():
            raise InvalidScientificObjectVersion("content_hash and semantic_hash are required")
        with _object_lock(object_id):
            with self.repository_factory.unit_of_work() as unit:
                repository = unit.agent2.scientific_objects
                logical = repository.get_object(object_id, for_update=True)
                manifest = self.object_types.require(object_type)
                if object_type != logical["object_type"] or manifest.kind.value != logical["kind"]:
                    raise InvalidScientificObjectVersion("version object_type must equal the logical object type and kind")
                if object_schema_version not in manifest.schema_versions:
                    raise InvalidScientificObjectVersion(f"unregistered schema version: {object_schema_version}")
                self._validate_sources(unit.connection, str(logical["project_id"]), source_resource_refs)
                self._validate_parents(repository, logical, parent_object_version_refs)
                version_id = uuid4()
                version = repository.add_version({
                    "id": version_id,
                    "scientific_object_id": object_id,
                    "version_no": repository.next_version_no(object_id),
                    "object_type": object_type,
                    "object_schema_version": object_schema_version,
                    "source_resource_refs_json": source_resource_refs,
                    "parent_object_version_refs_json": [item.model_dump(mode="json") for item in parent_object_version_refs],
                    "semantic_profile_ref_json": semantic_profile_ref,
                    "normalized_payload_ref_json": normalized_payload_ref.model_dump(mode="json"),
                    "content_hash": content_hash,
                    "semantic_hash": semantic_hash,
                    "canonical_metadata_json": canonical_metadata,
                    "availability_status": availability_status.value,
                    "created_by_user_id": created_by_user_id,
                })
                repository.set_current_version(object_id, version_id)
                return version

    def create_derived_object(self, *, parent_object_version_refs: list[ScientificObjectVersionRef], **values: Any) -> tuple[dict[str, Any], dict[str, Any]]:
        logical = self.create_object(
            project_id=values["project_id"],
            kind=values["kind"],
            object_type=values["object_type"],
            display_name=values["display_name"],
            created_by_user_id=values.get("created_by_user_id"),
        )
        version = self.create_version(
            logical["id"],
            parent_object_version_refs=parent_object_version_refs,
            **{key: value for key, value in values.items() if key not in {"project_id", "kind", "display_name"}},
        )
        # create_version advances the durable current-version projection.
        # Reload so API callers never observe a stale logical object.
        return self.get_object(logical["id"]), version

    def create_table_from_dataset(
        self,
        *,
        project_id: str,
        dataset_id: str,
        storage: ArtifactStorage,
        resource_id: str | None = None,
        display_name: str | None = None,
        created_by_user_id: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Promote a persisted, parsed DataFrame resource into the Agent2 authority.

        Dataset upload/normalization remains the source of the bytes. This method
        only creates the versioned ScientificObject projection after checking the
        durable manifest, checksum, project scope, and DataFrame resource type.
        """
        with self.repository_factory.session() as session:
            dataset = dict(session.repositories.datasets.get(dataset_id))
            if str(dataset.get("projectId")) != project_id:
                raise UnauthorizedScientificObjectReference("source dataset is outside the project")
            metadata = dict(dataset.get("metadata") or {})
            exports = [item for item in (metadata.get("normalizedExports") or []) if isinstance(item, dict)]
        candidates = [item for item in exports if not resource_id or str(item.get("objectId")) == resource_id]
        if not candidates:
            raise InvalidScientificObjectVersion("the requested dataset table resource is unavailable")
        export = candidates[0]
        object_id = str(export.get("objectId") or "")
        storage_key = str(export.get("storageKey") or "")
        metadata_key = str(export.get("metadataKey") or "")
        content_hash = str(export.get("contentHash") or "")
        semantic_hash = str(export.get("objectHash") or content_hash)
        if not object_id or not storage_key or not metadata_key or len(content_hash) != 64:
            raise InvalidScientificObjectVersion("the persisted table manifest is incomplete")
        expected_scope = f"projects/{project_id}/datasets/{dataset_id}/normalized/"
        if not storage_key.startswith(expected_scope) or not metadata_key.startswith(expected_scope):
            raise UnauthorizedScientificObjectReference("normalized table source is outside the dataset scope")
        payload_bytes = storage.get_bytes_bounded(storage_key, max_bytes=8 * 1024 * 1024)
        if hashlib.sha256(payload_bytes).hexdigest() != content_hash:
            raise InvalidScientificObjectVersion("normalized table source checksum mismatch")
        payload = json.loads(payload_bytes.decode("utf-8"))
        source_metadata = json.loads(storage.get_bytes_bounded(metadata_key, max_bytes=256 * 1024).decode("utf-8"))
        object_type = str((source_metadata.get("provenance") or {}).get("objectType") or (source_metadata.get("metadata") or {}).get("objectType") or "")
        if object_type != "DataFrame":
            raise InvalidScientificObjectVersion("the selected normalized resource is not a scientific table")
        if not isinstance(payload, list):
            raise InvalidScientificObjectVersion("scientific table payload must be a bounded row list")
        logical = self.create_object(
            project_id=project_id,
            kind=ScientificObjectKind.TABLE,
            object_type="materials.table",
            display_name=display_name or str(dataset.get("name") or "Scientific materials table"),
            created_by_user_id=created_by_user_id,
        )
        version = self.create_version(
            logical["id"],
            object_type="materials.table",
            object_schema_version="1.0",
            source_resource_refs=[{"project_id": project_id, "dataset_id": dataset_id, "resource_id": object_id}],
            parent_object_version_refs=[],
            normalized_payload_ref=StorageRef(
                storage_backend="artifact_storage",
                object_key=storage_key,
                checksum=content_hash,
                media_type="application/json",
                byte_size=len(payload_bytes),
            ),
            content_hash=content_hash,
            semantic_hash=semantic_hash,
            canonical_metadata={
                **dict(source_metadata.get("metadata") or {}),
                "row_count": len(payload),
                "source_resource_id": object_id,
                "dataset_id": dataset_id,
            },
            created_by_user_id=created_by_user_id,
        )
        # create_version advances the durable current-version projection.
        # Reload so API callers never observe a stale logical object.
        return self.get_object(logical["id"]), version

    def get_object(self, object_id: UUID) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            return session.agent2.scientific_objects.get_object(object_id)

    def get_version(self, object_id: UUID, version_id: UUID) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            logical = session.agent2.scientific_objects.get_object(object_id)
            version = session.agent2.scientific_objects.get_version(version_id)
            if version["scientific_object_id"] != logical["id"]:
                raise InvalidScientificObjectVersion("version does not belong to the requested object")
            return version

    def list_project_objects(self, project_id: str, **filters: Any) -> list[dict[str, Any]]:
        with self.repository_factory.session() as session:
            return session.agent2.scientific_objects.list_project_objects(project_id, **filters)

    def list_versions(self, object_id: UUID) -> list[dict[str, Any]]:
        with self.repository_factory.session() as session:
            session.agent2.scientific_objects.get_object(object_id)
            return session.agent2.scientific_objects.list_versions(object_id)

    def set_current_version(self, object_id: UUID, version_id: UUID) -> dict[str, Any]:
        with _object_lock(object_id):
            with self.repository_factory.unit_of_work() as unit:
                logical = unit.agent2.scientific_objects.get_object(object_id, for_update=True)
                version = unit.agent2.scientific_objects.get_version(version_id)
                if version["scientific_object_id"] != logical["id"]:
                    raise InvalidScientificObjectVersion("current version must belong to the same ScientificObject")
                return unit.agent2.scientific_objects.set_current_version(object_id, version_id)

    def create_relationship(
        self,
        *,
        project_id: str,
        source_version_id: UUID,
        target_version_id: UUID,
        relation_type: str,
        metadata: dict[str, Any] | None = None,
        created_by_user_id: str | None = None,
    ) -> dict[str, Any]:
        if source_version_id == target_version_id:
            raise InvalidScientificObjectRelationship("self relationships are forbidden")
        if relation_type not in CANONICAL_RELATIONS and not _NAMESPACED_RELATION.fullmatch(relation_type):
            raise InvalidScientificObjectRelationship("relation_type must be canonical or namespaced")
        with self.repository_factory.unit_of_work() as unit:
            repository = unit.agent2.scientific_objects
            source = repository.get_version(source_version_id)
            target = repository.get_version(target_version_id)
            source_object = repository.get_object(source["scientific_object_id"])
            target_object = repository.get_object(target["scientific_object_id"])
            if source_object["project_id"] != project_id or target_object["project_id"] != project_id:
                raise UnauthorizedScientificObjectReference("relationship versions must belong to the authorized project")
            return repository.add_relationship({
                "id": uuid4(),
                "project_id": project_id,
                "source_version_id": source_version_id,
                "target_version_id": target_version_id,
                "relation_type": relation_type,
                "metadata_json": metadata or {},
                "created_by_user_id": created_by_user_id,
            })

    def list_relationships(self, object_id: UUID) -> list[dict[str, Any]]:
        with self.repository_factory.session() as session:
            session.agent2.scientific_objects.get_object(object_id)
            return session.agent2.scientific_objects.list_relationships(object_id)

    def archive(self, object_id: UUID) -> dict[str, Any]:
        with _object_lock(object_id):
            with self.repository_factory.unit_of_work() as unit:
                unit.agent2.scientific_objects.get_object(object_id, for_update=True)
                return unit.agent2.scientific_objects.archive_object(object_id, datetime.now(timezone.utc))

    @staticmethod
    def _validate_sources(connection: Any, project_id: str, refs: list[dict[str, Any]]) -> None:
        for ref in refs:
            if ref.get("scope") == "system_fixture":
                continue
            ref_project = str(ref.get("project_id") or ref.get("projectId") or "")
            if ref_project:
                if ref_project != project_id:
                    raise UnauthorizedScientificObjectReference("cross-project source reference")
                continue
            dataset_id = ref.get("dataset_id") or ref.get("datasetId")
            if dataset_id:
                owner = connection.execute(select(datasets.c.project_id).where(datasets.c.id == str(dataset_id))).scalar_one_or_none()
                if owner != project_id:
                    raise UnauthorizedScientificObjectReference("source dataset is outside the project")
                continue
            raise UnauthorizedScientificObjectReference("source reference lacks an authorized project or system fixture scope")

    @staticmethod
    def _validate_parents(repository: Any, logical: dict[str, Any], refs: list[ScientificObjectVersionRef]) -> None:
        target_object_id = logical["id"]
        project_id = str(logical["project_id"])
        visited: set[UUID] = set()

        def walk(version_id: UUID) -> None:
            if version_id in visited:
                return
            visited.add(version_id)
            version = repository.get_version(version_id)
            parent_object = repository.get_object(version["scientific_object_id"])
            if str(parent_object["project_id"]) != project_id:
                raise UnauthorizedScientificObjectReference("cross-project parent reference")
            if parent_object["id"] == target_object_id:
                raise InvalidScientificObjectVersion("parent graph would create a cycle")
            for raw in version["parent_object_version_refs_json"] or []:
                walk(UUID(str(raw["version_id"])))

        for ref in refs:
            if ref.project_id != project_id:
                raise UnauthorizedScientificObjectReference("cross-project parent reference")
            walk(ref.version_id)
