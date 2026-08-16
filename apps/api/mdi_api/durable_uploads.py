from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping

from mdi_api.artifact_storage import ArtifactStorage, create_artifact_storage_from_settings
from mdi_api.config import ApiSettings, load_settings
from mdi_api.database import create_repository_factory
from mdi_api.input_transport import MAX_FILE_BYTES
from mdi_workers.object_store import DurableObjectStoreResolver


@dataclass(frozen=True)
class DurableUploadResult:
    dataset_id: str
    profile_id: str
    normalized_resource_ids: tuple[str, ...]
    storage_keys: tuple[str, ...]


def persist_phase2_upload(
    runtime: Any,
    dataset_id: str,
    *,
    settings: ApiSettings | None = None,
    artifact_storage: ArtifactStorage | None = None,
    repository_factory: Any | None = None,
) -> DurableUploadResult | None:
    """Persist a parsed Phase 2 upload for reconstruction by a fresh worker.

    Local development keeps the original in-memory product loop. PostgreSQL
    runtime mode copies the already-normalized source objects into the existing
    ArtifactStorage authority and stores their exact manifest plus DataProfile
    in the existing repositories.
    """

    active_settings = settings or load_settings()
    if active_settings.runtime_backend != "postgresql":
        return None

    record = runtime.datasets[dataset_id]
    project = runtime.projects[record.project_id]
    storage = artifact_storage or create_artifact_storage_from_settings(active_settings)
    factory = repository_factory or create_repository_factory(active_settings)
    durable_exports = _persist_normalized_exports(
        source_storage=runtime.artifact_storage,
        durable_storage=storage,
        project_id=record.project_id,
        dataset_id=record.id,
        exports=record.normalized_exports,
    )
    durable_raw_uploads = _persist_raw_uploads(
        source_storage=runtime.artifact_storage,
        durable_storage=storage,
        project_id=record.project_id,
        dataset_id=record.id,
        files=record.files,
    )

    dataset_metadata = {
        **record.summary(),
        "files": record.files,
        "normalizedExports": durable_exports,
        "rawUploads": durable_raw_uploads,
        "inputTransport": record.input_transport,
        "sourceResourceAuthority": "artifact_storage",
    }
    with factory.session() as session:
        repos = session.repositories
        try:
            repos.projects.get(project.id)
        except LookupError:
            repos.projects.save({**project.summary(), "createdBy": "user_local"})
        repos.datasets.save(
            {
                "id": record.id,
                "projectId": record.project_id,
                "name": record.name,
                "status": record.status,
                "metadata": dataset_metadata,
                "createdBy": "user_local",
            }
        )
        repos.data_profiles.save(record.profile)

    resolver = DurableObjectStoreResolver(
        repository_factory=factory,
        artifact_storage=storage,
    )
    restored = resolver.resolve(record.id, profile_id=record.profile.profileId)
    if restored is None or "profile" not in restored:
        raise ValueError("Durable upload verification failed: DataProfile is not resolvable.")
    missing = [item["objectId"] for item in durable_exports if item["objectId"] not in restored]
    if missing:
        raise ValueError(f"Durable upload verification failed: unresolved source resources {missing}.")

    return DurableUploadResult(
        dataset_id=record.id,
        profile_id=record.profile.profileId,
        normalized_resource_ids=tuple(item["objectId"] for item in durable_exports),
        storage_keys=tuple(item["storageKey"] for item in durable_exports),
    )


def _persist_raw_uploads(
    *,
    source_storage: ArtifactStorage,
    durable_storage: ArtifactStorage,
    project_id: str,
    dataset_id: str,
    files: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    required_scope = f"projects/{project_id}/datasets/{dataset_id}/raw/"
    durable: list[dict[str, Any]] = []
    for item in files:
        storage_key = str(item.get("storageKey") or "")
        expected_hash = str(item.get("sha256") or "")
        expected_size = int(item.get("byteSize") or 0)
        if not storage_key.startswith(required_scope) or len(expected_hash) != 64 or not 0 < expected_size <= MAX_FILE_BYTES:
            raise ValueError("Raw upload manifest is incomplete or outside the dataset scope.")
        content = source_storage.get_bytes_bounded(storage_key, max_bytes=MAX_FILE_BYTES)
        if len(content) != expected_size or hashlib.sha256(content).hexdigest() != expected_hash:
            raise ValueError(f"Raw upload checksum mismatch for {item.get('fileId')}.")
        durable_key = _put_exact(
            durable_storage,
            storage_key,
            content,
            content_type="application/octet-stream",
            expected_hash=expected_hash,
        )
        restored = durable_storage.get_bytes_bounded(durable_key, max_bytes=MAX_FILE_BYTES)
        if len(restored) != expected_size or hashlib.sha256(restored).hexdigest() != expected_hash:
            raise ValueError(f"Durable raw upload verification failed for {item.get('fileId')}.")
        durable.append(
            {
                "fileId": str(item.get("fileId")),
                "fileName": str(item.get("name")),
                "storageKey": durable_key,
                "sha256": expected_hash,
                "byteSize": expected_size,
            }
        )
    return durable


def _persist_normalized_exports(
    *,
    source_storage: ArtifactStorage,
    durable_storage: ArtifactStorage,
    project_id: str,
    dataset_id: str,
    exports: list[Mapping[str, Any]],
) -> list[dict[str, str]]:
    if not exports:
        raise ValueError("Durable upload requires at least one normalized source resource.")

    durable_exports: list[dict[str, str]] = []
    required_scope = f"projects/{project_id}/datasets/{dataset_id}/normalized/"
    for export in exports:
        object_id = str(export.get("objectId") or "")
        storage_key = str(export.get("storageKey") or "")
        metadata_key = str(export.get("metadataKey") or "")
        expected_hash = str(export.get("contentHash") or "")
        object_hash = str(export.get("objectHash") or expected_hash)
        if not object_id or not storage_key or not metadata_key or not expected_hash or not object_hash:
            raise ValueError("Normalized source manifest is incomplete.")
        if not storage_key.startswith(required_scope) or not metadata_key.startswith(required_scope):
            raise ValueError("Normalized source manifest is outside the dataset scope.")

        content = source_storage.get_bytes(storage_key)
        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError(f"Normalized source checksum mismatch for {object_id}.")
        metadata = json.loads(source_storage.get_bytes(metadata_key).decode("utf-8"))
        if str(metadata.get("objectId") or "") != object_id:
            raise ValueError(f"Normalized source identity mismatch for {object_id}.")
        if str(metadata.get("contentHash") or "") != expected_hash:
            raise ValueError(f"Normalized source metadata checksum mismatch for {object_id}.")
        durable_metadata = {
            "objectId": object_id,
            "storageKey": storage_key,
            "contentHash": expected_hash,
            "metadata": metadata.get("metadata") or {},
            "provenance": metadata.get("provenance") or {},
        }
        metadata_bytes = json.dumps(
            durable_metadata,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        _put_exact(
            durable_storage,
            storage_key,
            content,
            content_type="application/json",
            expected_hash=expected_hash,
        )
        metadata_result = _put_metadata_exact(
            durable_storage,
            metadata_key,
            metadata_bytes,
            expected=durable_metadata,
        )
        data_result_key = _durable_key(durable_storage, storage_key)
        durable_exports.append(
            {
                "objectId": object_id,
                "storageKey": data_result_key,
                "metadataKey": metadata_result,
                "objectHash": object_hash,
                "contentHash": expected_hash,
            }
        )
    return durable_exports


def _put_exact(
    storage: ArtifactStorage,
    storage_key: str,
    content: bytes,
    *,
    content_type: str,
    expected_hash: str,
) -> str:
    durable_key = _durable_key(storage, storage_key)
    if storage.exists(durable_key):
        existing_hash = hashlib.sha256(storage.get_bytes(durable_key)).hexdigest()
        if existing_hash != expected_hash:
            raise ValueError(f"Conflicting durable source content for {durable_key}.")
        return durable_key
    result = storage.put_bytes(storage_key, content, content_type=content_type)
    if result.sha256 != expected_hash:
        raise ValueError(f"Durable source write checksum mismatch for {storage_key}.")
    retrieved_hash = hashlib.sha256(storage.get_bytes(result.storage_key)).hexdigest()
    if retrieved_hash != expected_hash:
        raise ValueError(f"Durable source retrieval checksum mismatch for {storage_key}.")
    return result.storage_key


def _put_metadata_exact(
    storage: ArtifactStorage,
    storage_key: str,
    content: bytes,
    *,
    expected: Mapping[str, Any],
) -> str:
    durable_key = _durable_key(storage, storage_key)
    if storage.exists(durable_key):
        current = json.loads(storage.get_bytes(durable_key).decode("utf-8"))
        comparable = {
            "objectId": current.get("objectId"),
            "storageKey": current.get("storageKey"),
            "contentHash": current.get("contentHash"),
            "metadata": current.get("metadata") or {},
            "provenance": current.get("provenance") or {},
        }
        if comparable != dict(expected):
            raise ValueError(f"Conflicting durable source metadata for {durable_key}.")
        return durable_key
    result = storage.put_bytes(storage_key, content, content_type="application/json")
    return result.storage_key


def _durable_key(storage: ArtifactStorage, storage_key: str) -> str:
    full_key = getattr(storage, "_full_key", None)
    return str(full_key(storage_key)) if callable(full_key) else storage_key
