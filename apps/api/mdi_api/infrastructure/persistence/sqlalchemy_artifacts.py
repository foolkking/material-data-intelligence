"""SQLAlchemy artifact persistence implementation."""

from __future__ import annotations

from typing import Any, Mapping

from sqlalchemy import and_, func, insert, or_, select
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError

from mdi_schemas import Artifact

from mdi_api.db import artifacts, jobs, tool_calls
from mdi_api.application.jobs.leases import ExecutionLeaseLost
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
        stored_id = self._with_connection(
            lambda connection: self._save_on_connection(connection, record)
        )
        return self.get(stored_id)

    def _save_on_connection(
        self, connection: Connection, record: Mapping[str, Any]
    ) -> str:
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
        connection.execute(
            artifacts.update()
            .where(artifacts.c.id == existing_id)
            .values(**{**values, "id": existing_id})
        )
        return existing_id

    def save_for_execution(
        self,
        artifact: Artifact | Mapping[str, Any],
        *,
        owner: str,
        attempt: int,
    ) -> dict[str, Any]:
        record = _model_to_record(artifact)
        job_id = str(record["jobId"])
        tool_call_id = str(record.get("toolCallId") or "")

        def run(connection: Connection) -> str:
            current = connection.execute(
                select(jobs.c.id)
                .select_from(
                    jobs.outerjoin(
                        tool_calls, tool_calls.c.id == tool_call_id
                    )
                )
                .where(
                    jobs.c.id == job_id,
                    jobs.c.status == "running",
                    jobs.c.execution_owner == owner,
                    jobs.c.execution_attempt == attempt,
                    jobs.c.lease_expires_at > func.now(),
                    tool_calls.c.attempt == attempt,
                )
            ).scalar_one_or_none()
            if current is None:
                raise ExecutionLeaseLost(
                    f"stale Artifact publication rejected for {job_id} attempt {attempt}"
                )
            return self._save_on_connection(connection, record)

        stored_id = self._with_connection(run)
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
