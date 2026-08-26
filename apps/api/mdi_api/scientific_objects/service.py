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
    ScientificDatasetQueryRequest,
    ScientificObjectKind,
    ScientificObjectVersionRef,
    StorageRef,
)
from mdi_api.unit_of_work import RepositoryFactory


CANONICAL_RELATIONS = frozenset({
    "derived_from", "contains", "member_of", "has_structure", "associated_with",
    "prediction_for", "measurement_of", "comparison_of", "aligned_with", "companion_of",
})
_RESOURCE_OBJECT_TYPES: dict[str, tuple[ScientificObjectKind, str]] = {
    "Structure": (ScientificObjectKind.STRUCTURE, "structure.crystal"),
    "DataFrame": (ScientificObjectKind.TABLE, "materials.table"),
    "Trajectory": (ScientificObjectKind.TRAJECTORY, "trajectory.atomic"),
    "ElectronicBand": (ScientificObjectKind.ELECTRONIC, "electronic.band_structure"),
    "ElectronicDos": (ScientificObjectKind.ELECTRONIC, "electronic.dos"),
}
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

    def admit_dataset_resource(
        self,
        *,
        project_id: str,
        dataset_id: str,
        resource_id: str,
        storage: ArtifactStorage,
        display_name: str | None = None,
        created_by_user_id: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Admit one current-generation persisted resource as a new logical object.

        Dataset ingestion remains the source, parser, Profile, byte-storage, and
        checksum authority. This bridge only projects an already verified exact
        resource into the Agent2 ScientificObject authority.
        """
        source = self._validated_dataset_resource(
            project_id=project_id,
            dataset_id=dataset_id,
            resource_id=resource_id,
            storage=storage,
        )
        logical = self.create_object(
            project_id=project_id,
            kind=source["kind"],
            object_type=source["object_type"],
            display_name=display_name or source["display_name"],
            created_by_user_id=created_by_user_id,
        )
        version = self._create_version_from_validated_resource(
            logical["id"],
            source=source,
            created_by_user_id=created_by_user_id,
        )
        return self.get_object(logical["id"]), version

    def create_version_from_dataset_resource(
        self,
        object_id: UUID,
        *,
        dataset_id: str,
        resource_id: str,
        storage: ArtifactStorage,
        created_by_user_id: str | None = None,
    ) -> dict[str, Any]:
        logical = self.get_object(object_id)
        source = self._validated_dataset_resource(
            project_id=str(logical["project_id"]),
            dataset_id=dataset_id,
            resource_id=resource_id,
            storage=storage,
        )
        if source["object_type"] != logical["object_type"] or source["kind"].value != logical["kind"]:
            raise InvalidScientificObjectVersion(
                "persisted resource type does not match the logical ScientificObject"
            )
        return self._create_version_from_validated_resource(
            object_id,
            source=source,
            created_by_user_id=created_by_user_id,
        )

    def _create_version_from_validated_resource(
        self,
        object_id: UUID,
        *,
        source: dict[str, Any],
        created_by_user_id: str | None,
    ) -> dict[str, Any]:
        return self.create_version(
            object_id,
            object_type=source["object_type"],
            object_schema_version="1.0",
            source_resource_refs=[{
                "project_id": source["project_id"],
                "dataset_id": source["dataset_id"],
                "resource_id": source["resource_id"],
            }],
            parent_object_version_refs=[],
            normalized_payload_ref=StorageRef(
                storage_backend="artifact_storage",
                object_key=source["storage_key"],
                checksum=source["content_hash"],
                media_type="application/json",
                byte_size=source["byte_size"],
            ),
            content_hash=source["content_hash"],
            semantic_hash=source["semantic_hash"],
            canonical_metadata=source["canonical_metadata"],
            semantic_profile_ref=source["semantic_profile_ref"],
            created_by_user_id=created_by_user_id,
        )

    def _validated_dataset_resource(
        self,
        *,
        project_id: str,
        dataset_id: str,
        resource_id: str,
        storage: ArtifactStorage,
    ) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            dataset = dict(session.repositories.datasets.get(dataset_id))
            profiles = list(session.repositories.data_profiles.list_for_dataset(dataset_id))
        if str(dataset.get("projectId")) != project_id:
            raise UnauthorizedScientificObjectReference("source dataset is outside the project")
        if str(dataset.get("status") or "") != "profile_ready" or not profiles:
            raise InvalidScientificObjectVersion("source dataset is not scientifically profiled")
        profiles.sort(key=lambda item: str(item.get("createdAt") or item.get("profileId") or ""))
        profile = dict(profiles[-1])
        metadata = dict(dataset.get("metadata") or {})
        exports = [item for item in metadata.get("normalizedExports") or [] if isinstance(item, dict)]
        matches = [item for item in exports if str(item.get("objectId") or "") == resource_id]
        if len(matches) != 1:
            raise InvalidScientificObjectVersion("the requested normalized scientific resource is unavailable")
        export = matches[0]
        storage_key = str(export.get("storageKey") or "")
        metadata_key = str(export.get("metadataKey") or "")
        content_hash = str(export.get("contentHash") or "")
        semantic_hash = str(export.get("objectHash") or "")
        required_scope = f"projects/{project_id}/datasets/{dataset_id}/normalized/{resource_id}/"
        if (
            not storage_key.startswith(required_scope)
            or not metadata_key.startswith(required_scope)
            or len(content_hash) != 64
            or len(semantic_hash) != 64
        ):
            raise InvalidScientificObjectVersion("persisted scientific resource manifest is incomplete")
        payload_bytes = storage.get_bytes_bounded(storage_key, max_bytes=8 * 1024 * 1024)
        if hashlib.sha256(payload_bytes).hexdigest() != content_hash:
            raise InvalidScientificObjectVersion("persisted scientific resource checksum mismatch")
        source_metadata = json.loads(
            storage.get_bytes_bounded(metadata_key, max_bytes=256 * 1024).decode("utf-8")
        )
        if (
            str(source_metadata.get("objectId") or "") != resource_id
            or str(source_metadata.get("contentHash") or "") != content_hash
        ):
            raise InvalidScientificObjectVersion("persisted scientific resource metadata mismatch")
        resource_type = str((source_metadata.get("provenance") or {}).get("objectType") or "")
        mapped = _RESOURCE_OBJECT_TYPES.get(resource_type)
        if mapped is None:
            raise InvalidScientificObjectVersion(
                "persisted scientific resource type is not admitted to ScientificObject authority"
            )
        profiled = [
            item for item in profile.get("objects") or []
            if isinstance(item, dict) and str(item.get("objectId") or "") == resource_id
        ]
        if len(profiled) != 1 or str(profiled[0].get("objectHash") or "") != semantic_hash:
            raise InvalidScientificObjectVersion("exact resource is not bound to the persisted DataProfile")
        canonical_metadata = self._resource_canonical_metadata(
            profile=profile,
            resource_id=resource_id,
            source_metadata=dict(source_metadata.get("metadata") or {}),
        )
        return {
            "project_id": project_id,
            "dataset_id": dataset_id,
            "resource_id": resource_id,
            "kind": mapped[0],
            "object_type": mapped[1],
            "display_name": str(dataset.get("name") or resource_id),
            "storage_key": storage_key,
            "content_hash": content_hash,
            "semantic_hash": semantic_hash,
            "byte_size": len(payload_bytes),
            "canonical_metadata": canonical_metadata,
            "semantic_profile_ref": {
                "profileId": str(profile.get("profileId") or profile.get("id") or ""),
                "datasetId": dataset_id,
                "contractVersion": str(profile.get("profileContractVersion") or profile.get("version") or ""),
                "semanticHash": str(profile.get("semanticHash") or ""),
                "resourceId": resource_id,
                "resourceHash": semantic_hash,
            },
        }

    @staticmethod
    def _resource_canonical_metadata(
        *,
        profile: dict[str, Any],
        resource_id: str,
        source_metadata: dict[str, Any],
    ) -> dict[str, Any]:
        result = dict(source_metadata)
        result["profileContractVersion"] = profile.get("profileContractVersion")
        for record in profile.get("resourceSemantics") or []:
            if isinstance(record, dict) and str(record.get("objectId") or "") == resource_id:
                result.update(dict(record.get("facts") or {}))
                break
        coordination = profile.get("coordinationReadiness") or {}
        for record in coordination.get("structures") or []:
            if isinstance(record, dict) and str(record.get("objectId") or "") == resource_id:
                result.update({
                    "latticeStatus": record.get("latticeStatus"),
                    "siteCount": record.get("siteCount"),
                    "coordinationInputStatus": record.get("coordinationInputStatus"),
                    "speciesOccupancyStatus": record.get("speciesOccupancyStatus"),
                })
                break
        return result

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

    def update_metadata(
        self,
        object_id: UUID,
        *,
        display_name: str | None = None,
        archived: bool | None = None,
    ) -> dict[str, Any]:
        if display_name is not None and not display_name.strip():
            raise InvalidScientificObjectVersion("display_name must not be blank")
        if display_name is None and archived is None:
            raise InvalidScientificObjectVersion("at least one metadata field is required")
        with _object_lock(object_id):
            with self.repository_factory.unit_of_work() as unit:
                repository = unit.agent2.scientific_objects
                repository.get_object(object_id, for_update=True)
                lifecycle_status = None
                archived_at = None
                if archived is True:
                    lifecycle_status = "ARCHIVED"
                    archived_at = datetime.now(timezone.utc)
                elif archived is False:
                    lifecycle_status = "ACTIVE"
                return repository.update_object_metadata(
                    object_id,
                    display_name=display_name.strip() if display_name is not None else None,
                    lifecycle_status=lifecycle_status,
                    archived_at=archived_at,
                )

    def query_dataset_version(
        self,
        object_id: UUID,
        version_id: UUID,
        *,
        storage: ArtifactStorage,
        request: ScientificDatasetQueryRequest,
    ) -> dict[str, Any]:
        logical = self.get_object(object_id)
        version = self.get_version(object_id, version_id)
        if logical["kind"] not in {ScientificObjectKind.DATASET.value, ScientificObjectKind.TABLE.value}:
            raise InvalidScientificObjectVersion("typed dataset query requires a DATASET or TABLE object")
        ref = StorageRef.model_validate(version["normalized_payload_ref_json"])
        payload_bytes = storage.get_bytes_bounded(ref.object_key, max_bytes=8 * 1024 * 1024)
        if hashlib.sha256(payload_bytes).hexdigest() != ref.checksum:
            raise InvalidScientificObjectVersion("dataset payload checksum mismatch")
        payload = json.loads(payload_bytes.decode("utf-8"))
        if not isinstance(payload, list) or any(not isinstance(row, dict) for row in payload):
            raise InvalidScientificObjectVersion("dataset payload must be a bounded list of objects")
        rows = [dict(row) for row in payload]
        columns = set().union(*(row.keys() for row in rows)) if rows else set()
        requested_columns = request.columns or sorted(columns)
        invalid_columns = [column for column in requested_columns if column not in columns]
        if invalid_columns:
            raise InvalidScientificObjectVersion(f"unknown dataset column: {invalid_columns[0]}")
        if request.sort_by and request.sort_by not in columns:
            raise InvalidScientificObjectVersion(f"unknown dataset column: {request.sort_by}")
        for clause in request.filters:
            if clause.column not in columns:
                raise InvalidScientificObjectVersion(f"unknown dataset column: {clause.column}")
            if clause.operator == "in" and (not isinstance(clause.value, list) or len(clause.value) > 100):
                raise InvalidScientificObjectVersion("in filter must contain at most 100 values")
        rows = [row for row in rows if all(self._matches_filter(row, clause) for clause in request.filters)]
        if request.sort_by:
            rows.sort(key=lambda row: self._sort_key(row.get(request.sort_by)), reverse=request.descending)
        selected = []
        for row in rows[: request.limit]:
            projected = {column: row.get(column) for column in requested_columns}
            projected["_stable_id"] = self._stable_row_identity(row)
            selected.append(projected)
        return {
            "object_id": str(object_id),
            "version_id": str(version_id),
            "total_matching": len(rows),
            "limit": request.limit,
            "columns": requested_columns,
            "items": selected,
        }

    @staticmethod
    def _stable_row_identity(row: dict[str, Any]) -> str:
        sample_id = row.get("sample_id")
        if sample_id is not None and str(sample_id).strip():
            return str(sample_id)
        canonical = json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
        return f"row-{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:24]}"

    @staticmethod
    def _sort_key(value: Any) -> tuple[int, Any]:
        return (1, "") if value is None else (0, value)

    @staticmethod
    def _matches_filter(row: dict[str, Any], clause: Any) -> bool:
        actual = row.get(clause.column)
        expected = clause.value
        if clause.operator == "eq":
            return actual == expected
        if clause.operator == "in":
            return actual in expected
        if actual is None:
            return False
        try:
            if clause.operator == "gt":
                return actual > expected
            if clause.operator == "gte":
                return actual >= expected
            if clause.operator == "lt":
                return actual < expected
            if clause.operator == "lte":
                return actual <= expected
        except TypeError as exc:
            raise InvalidScientificObjectVersion("dataset filter types are incompatible") from exc
        raise InvalidScientificObjectVersion(f"unsupported dataset filter operator: {clause.operator}")

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
