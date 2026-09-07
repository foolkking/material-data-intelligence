"""In-memory artifact persistence implementation."""

from __future__ import annotations

from typing import Any, Mapping

from mdi_schemas import Artifact

from mdi_api.infrastructure.persistence.base import (
    _InMemoryRecordRepository,
    _json_copy,
    _model_to_record,
    _required_id,
)

class InMemoryArtifactRepository(_InMemoryRecordRepository):
    def save(self, artifact: Artifact | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(artifact)
        artifact_id = _required_id(record, "artifactId")
        _validate_artifact_storage_record(record)
        existing_id = self._find_existing_id(artifact_id, record)
        if existing_id:
            current = self.records[existing_id]
            record["id"] = existing_id
            self.records[existing_id] = {**_json_copy(current), **_json_copy(record)}
            return _json_copy(self.records[existing_id])
        return self._save(record, record_id=artifact_id)

    def get(self, artifact_id: str) -> dict[str, Any]:
        return self._get(artifact_id)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("jobId") == job_id]

    def list_artifacts_by_job(self, job_id: str) -> list[dict[str, Any]]:
        return self.list_for_job(job_id)

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("projectId") == project_id]

    def _find_existing_id(self, artifact_id: str, record: Mapping[str, Any]) -> str | None:
        if artifact_id in self.records:
            return artifact_id
        storage_key = record.get("storageKey")
        sha256 = record.get("sha256") or record.get("contentHash")
        for existing_id, existing in self.records.items():
            existing_sha = existing.get("sha256") or existing.get("contentHash")
            if existing.get("jobId") == record.get("jobId") and existing.get("storageKey") == storage_key and existing_sha == sha256:
                return existing_id
        return None
def _validate_artifact_storage_record(record: Mapping[str, Any]) -> None:
    metadata = record.get("metadata") or {}
    if hasattr(metadata, "model_dump"):
        metadata = metadata.model_dump(mode="json")
    provider = str(
        record.get("storageProvider")
        or record.get("storage_provider")
        or metadata.get("storageProvider")
        or metadata.get("storage_provider")
        or "local"
    )
    if provider not in {"local", "s3", "minio"}:
        raise ValueError(f"Unknown artifact storage provider: {provider}")
    bucket = record.get("bucket") or metadata.get("bucket")
    if provider in {"s3", "minio"} and not bucket:
        raise ValueError(f"Artifact storage provider {provider} requires bucket")
    size_bytes = int(record.get("sizeBytes") or record.get("size_bytes") or 0)
    if size_bytes < 0:
        raise ValueError("Artifact sizeBytes must be non-negative")
    if not (record.get("storageKey") or record.get("storage_key")):
        raise ValueError("Artifact record is missing storageKey")

__all__ = ["InMemoryArtifactRepository"]
