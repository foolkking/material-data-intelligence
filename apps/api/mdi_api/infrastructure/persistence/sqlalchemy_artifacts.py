"""SQLAlchemy artifact persistence implementation."""

from __future__ import annotations

from typing import Any, Mapping

from sqlalchemy import and_, insert, or_, select
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError

from mdi_schemas import Artifact

from mdi_api.db import artifacts
from mdi_api.infrastructure.persistence.base import (
    _SqlAlchemyRepository,
    _enum_value,
    _iso,
    _json_copy,
    _model_to_record,
    _required_id,
    _row_to_json_dict,
)

class SqlAlchemyArtifactRepository(_SqlAlchemyRepository):
    def save(self, artifact: Artifact | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(artifact)
        artifact_id = _required_id(record, "artifactId")
        _validate_artifact_storage_record(record)
        metadata = _json_copy(record.get("metadata") or {})
        content_type = str(record.get("contentType") or metadata.get("provenance", {}).get("mediaType") or "application/octet-stream")
        sha256 = str(record.get("sha256") or record.get("contentHash") or "")
        storage_provider = str(record.get("storageProvider") or record.get("storage_provider") or metadata.get("storageProvider") or metadata.get("storage_provider") or "local")
        bucket = record.get("bucket") or metadata.get("bucket")
        values = {
            "id": artifact_id,
            "project_id": str(record["projectId"]),
            "dataset_id": record.get("datasetId"),
            "job_id": str(record["jobId"]),
            "tool_call_id": record.get("toolCallId"),
            "type": _enum_value(record.get("type")),
            "name": str(record.get("name") or artifact_id),
            "version": str(record.get("version") or "1"),
            "storage_key": str(record["storageKey"]),
            "storage_provider": storage_provider,
            "bucket": str(bucket) if bucket else None,
            "preview_key": record.get("previewKey"),
            "size_bytes": int(record.get("sizeBytes") or 0),
            "content_type": content_type,
            "content_hash": str(record.get("contentHash") or sha256),
            "sha256": sha256,
            "metadata_json": metadata,
        }

        def run(connection: Connection) -> str:
            existing = connection.execute(
                select(artifacts).where(
                    or_(
                        artifacts.c.id == artifact_id,
                        and_(
                            artifacts.c.job_id == values["job_id"],
                            artifacts.c.storage_key == values["storage_key"],
                            artifacts.c.sha256 == values["sha256"],
                        ),
                    )
                )
            ).mappings().first()
            if existing is None:
                connection.execute(insert(artifacts).values(**values))
                return artifact_id
            existing_row = _row_to_json_dict(existing)
            existing_id = str(existing_row["id"])
            connection.execute(artifacts.update().where(artifacts.c.id == existing_id).values(**{**values, "id": existing_id}))
            return existing_id

        try:
            stored_id = self._with_connection(run)
        except IntegrityError as exc:
            # A duplicate worker can race on the job/storage/checksum
            # uniqueness boundary.  Reuse the committed Artifact after the
            # losing transaction rolls back; never mint a second provenance
            # row for the same persisted bytes.
            existing = self._fetch_one_dict(
                select(artifacts).where(
                    or_(
                        artifacts.c.id == artifact_id,
                        and_(
                            artifacts.c.job_id == values["job_id"],
                            artifacts.c.storage_key == values["storage_key"],
                            artifacts.c.sha256 == values["sha256"],
                        ),
                    )
                )
            )
            if existing is None:
                raise
            existing_row = _row_to_json_dict(existing)
            if (
                str(existing_row.get("project_id") or "") != values["project_id"]
                or str(existing_row.get("job_id") or "") != values["job_id"]
                or str(existing_row.get("storage_key") or "") != values["storage_key"]
                or str(existing_row.get("sha256") or "") != values["sha256"]
            ):
                raise ValueError("Artifact idempotency key is already bound to a different persisted object.") from exc
            stored_id = str(existing_row["id"])
        return self.get(stored_id)

    def get(self, artifact_id: str) -> dict[str, Any]:
        return _artifact_from_row(self._fetch_one_dict(select(artifacts).where(artifacts.c.id == artifact_id)))

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        statement = select(artifacts).where(artifacts.c.job_id == job_id).order_by(artifacts.c.created_at, artifacts.c.id)
        return [_artifact_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_artifacts_by_job(self, job_id: str) -> list[dict[str, Any]]:
        return self.list_for_job(job_id)

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        statement = select(artifacts).where(artifacts.c.project_id == project_id).order_by(artifacts.c.created_at.desc(), artifacts.c.id)
        return [_artifact_from_row(row) for row in self._fetch_all_dicts(statement)]
def _artifact_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "artifactId": row["id"],
        "projectId": row["project_id"],
        "datasetId": row["dataset_id"],
        "jobId": row["job_id"],
        "toolCallId": row["tool_call_id"],
        "type": row["type"],
        "name": row["name"],
        "version": row["version"],
        "storageKey": row["storage_key"],
        "storageProvider": row.get("storage_provider") or "local",
        "bucket": row.get("bucket"),
        "previewKey": row["preview_key"],
        "sizeBytes": row["size_bytes"],
        "contentType": row["content_type"],
        "contentHash": row["content_hash"],
        "sha256": row["sha256"],
        "metadata": _json_copy(row.get("metadata_json") or {}),
        "createdAt": _iso(row["created_at"]),
    }
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

__all__ = ["SqlAlchemyArtifactRepository"]
