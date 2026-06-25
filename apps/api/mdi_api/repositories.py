from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol

from sqlalchemy import delete, func, insert, select
from sqlalchemy.engine import Connection, Engine

from mdi_api.db import artifacts, datasets, job_events, jobs, organizations, projects, tool_calls, users, visualization_recipes
from mdi_schemas import Artifact, JobEvent, JobEventStatus, JobStatus, ToolCall, VisualizationRecipe


class ProjectRepository(Protocol):
    def save(self, project: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, project_id: str) -> dict[str, Any]:
        ...

    def list(self) -> list[dict[str, Any]]:
        ...


class DatasetRepository(Protocol):
    def save(self, dataset: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, dataset_id: str) -> dict[str, Any]:
        ...

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        ...


class JobRepository(Protocol):
    def save(self, job: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, job_id: str) -> dict[str, Any]:
        ...

    def set_status(self, job_id: str, status: JobStatus | str) -> dict[str, Any]:
        ...


class JobEventRepository(Protocol):
    def append_event(
        self,
        job_id: str,
        *,
        event_type: str,
        status: JobEventStatus | str,
        message: str,
        payload: Mapping[str, Any] | None = None,
        progress: float | None = None,
    ) -> JobEvent:
        ...

    def list_for_job(self, job_id: str) -> list[JobEvent]:
        ...

    def list_events_after_seq(self, job_id: str, after_seq: int) -> list[JobEvent]:
        ...


class ToolCallRepository(Protocol):
    def save(self, tool_call: ToolCall | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...


class ArtifactRepository(Protocol):
    def save(self, artifact: Artifact | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, artifact_id: str) -> dict[str, Any]:
        ...

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...


class RecipeRepository(Protocol):
    def save(self, recipe: VisualizationRecipe | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, recipe_id: str) -> dict[str, Any]:
        ...

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...


@dataclass
class InMemoryRepositoryBundle:
    projects: "InMemoryProjectRepository"
    datasets: "InMemoryDatasetRepository"
    jobs: "InMemoryJobRepository"
    job_events: "InMemoryJobEventRepository"
    tool_calls: "InMemoryToolCallRepository"
    artifacts: "InMemoryArtifactRepository"
    recipes: "InMemoryRecipeRepository"

    @classmethod
    def create(cls) -> "InMemoryRepositoryBundle":
        return cls(
            projects=InMemoryProjectRepository(),
            datasets=InMemoryDatasetRepository(),
            jobs=InMemoryJobRepository(),
            job_events=InMemoryJobEventRepository(),
            tool_calls=InMemoryToolCallRepository(),
            artifacts=InMemoryArtifactRepository(),
            recipes=InMemoryRecipeRepository(),
        )


class _InMemoryRecordRepository:
    def __init__(self) -> None:
        self.records: dict[str, dict[str, Any]] = {}

    def _save(self, record: Mapping[str, Any], *, record_id: str) -> dict[str, Any]:
        stored = _json_copy(record)
        stored.setdefault("id", record_id)
        self.records[record_id] = stored
        return _json_copy(stored)

    def _get(self, record_id: str) -> dict[str, Any]:
        try:
            return _json_copy(self.records[record_id])
        except KeyError as exc:
            raise LookupError(f"Unknown record id: {record_id}") from exc


class InMemoryProjectRepository(_InMemoryRecordRepository):
    def save(self, project: Mapping[str, Any]) -> dict[str, Any]:
        return self._save(project, record_id=_required_id(project, "projectId"))

    def get(self, project_id: str) -> dict[str, Any]:
        return self._get(project_id)

    def list(self) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values()]


class InMemoryDatasetRepository(_InMemoryRecordRepository):
    def save(self, dataset: Mapping[str, Any]) -> dict[str, Any]:
        return self._save(dataset, record_id=_required_id(dataset, "datasetId"))

    def get(self, dataset_id: str) -> dict[str, Any]:
        return self._get(dataset_id)

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("projectId") == project_id]


class InMemoryJobRepository(_InMemoryRecordRepository):
    def save(self, job: Mapping[str, Any]) -> dict[str, Any]:
        return self._save(job, record_id=_required_id(job, "jobId"))

    def get(self, job_id: str) -> dict[str, Any]:
        return self._get(job_id)

    def set_status(self, job_id: str, status: JobStatus | str) -> dict[str, Any]:
        record = self._get(job_id)
        record["status"] = _enum_value(status)
        record["updatedAt"] = _utc_now()
        self.records[job_id] = record
        return _json_copy(record)


class InMemoryJobEventRepository:
    def __init__(self) -> None:
        self.events_by_job: dict[str, list[JobEvent]] = {}

    def append_event(
        self,
        job_id: str,
        *,
        event_type: str,
        status: JobEventStatus | str,
        message: str,
        payload: Mapping[str, Any] | None = None,
        progress: float | None = None,
    ) -> JobEvent:
        events = self.events_by_job.setdefault(job_id, [])
        seq = len(events) + 1
        event = JobEvent(
            id=f"evt_{job_id}_{seq:04d}",
            jobId=job_id,
            seq=seq,
            eventType=event_type,
            status=JobEventStatus(_enum_value(status)),
            message=message,
            progress=progress,
            payload=dict(payload or {}),
            createdAt=_utc_now(),
        )
        events.append(event)
        return event

    def save_event(self, event: JobEvent) -> JobEvent:
        events = self.events_by_job.setdefault(event.jobId, [])
        if any(existing.seq == event.seq for existing in events):
            raise ValueError(f"Duplicate job event seq {event.seq} for job {event.jobId}")
        if events and event.seq <= events[-1].seq:
            raise ValueError(f"Job event seq must increase for job {event.jobId}")
        events.append(event)
        return event

    def list_for_job(self, job_id: str) -> list[JobEvent]:
        return list(self.events_by_job.get(job_id, []))

    def list_events_after_seq(self, job_id: str, after_seq: int) -> list[JobEvent]:
        return [event for event in self.events_by_job.get(job_id, []) if event.seq > after_seq]


class InMemoryToolCallRepository(_InMemoryRecordRepository):
    def save(self, tool_call: ToolCall | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(tool_call)
        return self._save(record, record_id=_required_id(record))

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("jobId") == job_id]


class InMemoryArtifactRepository(_InMemoryRecordRepository):
    def save(self, artifact: Artifact | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(artifact)
        return self._save(record, record_id=_required_id(record, "artifactId"))

    def get(self, artifact_id: str) -> dict[str, Any]:
        return self._get(artifact_id)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("jobId") == job_id]


class InMemoryRecipeRepository(_InMemoryRecordRepository):
    def save(self, recipe: VisualizationRecipe | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(recipe)
        return self._save(record, record_id=_required_id(record, "recipeId"))

    def get(self, recipe_id: str) -> dict[str, Any]:
        return self._get(recipe_id)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("sourceJobId") == job_id]


@dataclass
class SqlAlchemyRepositoryBundle:
    projects: "SqlAlchemyProjectRepository"
    datasets: "SqlAlchemyDatasetRepository"
    jobs: "SqlAlchemyJobRepository"
    job_events: "SqlAlchemyJobEventRepository"
    tool_calls: "SqlAlchemyToolCallRepository"
    artifacts: "SqlAlchemyArtifactRepository"
    recipes: "SqlAlchemyRecipeRepository"

    @classmethod
    def create(cls, bind: Engine | Connection) -> "SqlAlchemyRepositoryBundle":
        return cls(
            projects=SqlAlchemyProjectRepository(bind),
            datasets=SqlAlchemyDatasetRepository(bind),
            jobs=SqlAlchemyJobRepository(bind),
            job_events=SqlAlchemyJobEventRepository(bind),
            tool_calls=SqlAlchemyToolCallRepository(bind),
            artifacts=SqlAlchemyArtifactRepository(bind),
            recipes=SqlAlchemyRecipeRepository(bind),
        )


class _SqlAlchemyRepository:
    def __init__(self, bind: Engine | Connection) -> None:
        self.bind = bind

    def _with_connection(self, fn: Any) -> Any:
        if isinstance(self.bind, Engine):
            with self.bind.begin() as connection:
                return fn(connection)
        return fn(self.bind)

    def _fetch_one_dict(self, statement: Any) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(statement).mappings().first()
            if row is None:
                raise LookupError("Record not found")
            return _row_to_json_dict(row)

        return self._with_connection(run)

    def _fetch_all_dicts(self, statement: Any) -> list[dict[str, Any]]:
        def run(connection: Connection) -> list[dict[str, Any]]:
            return [_row_to_json_dict(row) for row in connection.execute(statement).mappings().all()]

        return self._with_connection(run)


class SqlAlchemyProjectRepository(_SqlAlchemyRepository):
    def save(self, project: Mapping[str, Any]) -> dict[str, Any]:
        project_id = _required_id(project, "projectId")
        organization_id = str(project.get("organizationId") or project.get("organization_id") or "org_local")
        created_by = str(project.get("createdBy") or project.get("created_by") or "user_local")
        values = {
            "id": project_id,
            "organization_id": organization_id,
            "name": str(project.get("name") or project_id),
            "description": str(project.get("description") or ""),
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            _ensure_actor_and_org(connection, user_id=created_by, organization_id=organization_id)
            connection.execute(delete(projects).where(projects.c.id == project_id))
            connection.execute(insert(projects).values(**values))

        self._with_connection(run)
        return self.get(project_id)

    def get(self, project_id: str) -> dict[str, Any]:
        return _project_from_row(self._fetch_one_dict(select(projects).where(projects.c.id == project_id)))

    def list(self) -> list[dict[str, Any]]:
        return [_project_from_row(row) for row in self._fetch_all_dicts(select(projects).order_by(projects.c.created_at, projects.c.id))]


class SqlAlchemyDatasetRepository(_SqlAlchemyRepository):
    def save(self, dataset: Mapping[str, Any]) -> dict[str, Any]:
        dataset_id = _required_id(dataset, "datasetId")
        created_by = str(dataset.get("createdBy") or dataset.get("created_by") or "user_local")
        values = {
            "id": dataset_id,
            "project_id": str(dataset["projectId"]),
            "name": str(dataset.get("name") or dataset.get("datasetName") or dataset_id),
            "status": str(dataset.get("status") or "created"),
            "metadata_json": _json_copy(dataset.get("metadata") or dataset),
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            _ensure_user(connection, user_id=created_by)
            connection.execute(delete(datasets).where(datasets.c.id == dataset_id))
            connection.execute(insert(datasets).values(**values))

        self._with_connection(run)
        return self.get(dataset_id)

    def get(self, dataset_id: str) -> dict[str, Any]:
        return _dataset_from_row(self._fetch_one_dict(select(datasets).where(datasets.c.id == dataset_id)))

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        statement = select(datasets).where(datasets.c.project_id == project_id).order_by(datasets.c.created_at, datasets.c.id)
        return [_dataset_from_row(row) for row in self._fetch_all_dicts(statement)]


class SqlAlchemyJobRepository(_SqlAlchemyRepository):
    def save(self, job: Mapping[str, Any]) -> dict[str, Any]:
        job_id = _required_id(job, "jobId")
        created_by = str(job.get("createdBy") or job.get("created_by") or "user_local")
        values = {
            "id": job_id,
            "project_id": str(job["projectId"]),
            "dataset_id": job.get("datasetId"),
            "kind": str(job.get("kind") or "analysis"),
            "status": str(job.get("status") or JobStatus.created.value),
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            _ensure_user(connection, user_id=created_by)
            connection.execute(delete(jobs).where(jobs.c.id == job_id))
            connection.execute(insert(jobs).values(**values))

        self._with_connection(run)
        return self.get(job_id)

    def get(self, job_id: str) -> dict[str, Any]:
        return _job_from_row(self._fetch_one_dict(select(jobs).where(jobs.c.id == job_id)))

    def set_status(self, job_id: str, status: JobStatus | str) -> dict[str, Any]:
        def run(connection: Connection) -> None:
            connection.execute(jobs.update().where(jobs.c.id == job_id).values(status=_enum_value(status), updated_at=func.now()))

        self._with_connection(run)
        return self.get(job_id)


class SqlAlchemyJobEventRepository(_SqlAlchemyRepository):
    def append_event(
        self,
        job_id: str,
        *,
        event_type: str,
        status: JobEventStatus | str,
        message: str,
        payload: Mapping[str, Any] | None = None,
        progress: float | None = None,
    ) -> JobEvent:
        def run(connection: Connection) -> JobEvent:
            max_seq = connection.execute(select(func.max(job_events.c.seq)).where(job_events.c.job_id == job_id)).scalar()
            seq = int(max_seq or 0) + 1
            event = JobEvent(
                id=f"evt_{job_id}_{seq:04d}",
                jobId=job_id,
                seq=seq,
                eventType=event_type,
                status=JobEventStatus(_enum_value(status)),
                message=message,
                progress=progress,
                payload=dict(payload or {}),
                createdAt=_utc_now(),
            )
            connection.execute(insert(job_events).values(**_job_event_values(event)))
            return event

        return self._with_connection(run)

    def list_for_job(self, job_id: str) -> list[JobEvent]:
        return self.list_events_after_seq(job_id, 0)

    def list_events_after_seq(self, job_id: str, after_seq: int) -> list[JobEvent]:
        statement = (
            select(job_events)
            .where(job_events.c.job_id == job_id, job_events.c.seq > after_seq)
            .order_by(job_events.c.seq)
        )
        return [_job_event_from_row(row) for row in self._fetch_all_dicts(statement)]


class SqlAlchemyToolCallRepository(_SqlAlchemyRepository):
    def save(self, tool_call: ToolCall | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(tool_call)
        tool_call_id = _required_id(record)
        values = {
            "id": tool_call_id,
            "job_id": str(record["jobId"]),
            "step_id": str(record["stepId"]),
            "tool_id": str(record["toolId"]),
            "status": str(record.get("status") or "created"),
            "params_json": _json_copy(record.get("params") or {}),
            "error_json": _json_copy(record.get("error")) if record.get("error") else None,
        }

        def run(connection: Connection) -> None:
            connection.execute(delete(tool_calls).where(tool_calls.c.id == tool_call_id))
            connection.execute(insert(tool_calls).values(**values))

        self._with_connection(run)
        return self.get(tool_call_id)

    def get(self, tool_call_id: str) -> dict[str, Any]:
        return _tool_call_from_row(self._fetch_one_dict(select(tool_calls).where(tool_calls.c.id == tool_call_id)))

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        statement = select(tool_calls).where(tool_calls.c.job_id == job_id).order_by(tool_calls.c.created_at, tool_calls.c.id)
        return [_tool_call_from_row(row) for row in self._fetch_all_dicts(statement)]


class SqlAlchemyArtifactRepository(_SqlAlchemyRepository):
    def save(self, artifact: Artifact | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(artifact)
        artifact_id = _required_id(record, "artifactId")
        metadata = _json_copy(record.get("metadata") or {})
        content_type = str(record.get("contentType") or metadata.get("provenance", {}).get("mediaType") or "application/octet-stream")
        sha256 = str(record.get("sha256") or record.get("contentHash") or "")
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
            "preview_key": record.get("previewKey"),
            "size_bytes": int(record.get("sizeBytes") or 0),
            "content_type": content_type,
            "content_hash": str(record.get("contentHash") or sha256),
            "sha256": sha256,
            "metadata_json": metadata,
        }

        def run(connection: Connection) -> None:
            connection.execute(delete(artifacts).where(artifacts.c.id == artifact_id))
            connection.execute(insert(artifacts).values(**values))

        self._with_connection(run)
        return self.get(artifact_id)

    def get(self, artifact_id: str) -> dict[str, Any]:
        return _artifact_from_row(self._fetch_one_dict(select(artifacts).where(artifacts.c.id == artifact_id)))

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        statement = select(artifacts).where(artifacts.c.job_id == job_id).order_by(artifacts.c.created_at, artifacts.c.id)
        return [_artifact_from_row(row) for row in self._fetch_all_dicts(statement)]


class SqlAlchemyRecipeRepository(_SqlAlchemyRepository):
    def save(self, recipe: VisualizationRecipe | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(recipe)
        recipe_id = _required_id(record, "recipeId")
        created_by = str(record.get("createdBy") or record.get("created_by") or "user_local")
        values = {
            "id": recipe_id,
            "project_id": str(record["projectId"]),
            "source_job_id": record.get("sourceJobId"),
            "name": str(record.get("name") or recipe_id),
            "recipe_json": _json_copy(record),
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            _ensure_user(connection, user_id=created_by)
            connection.execute(delete(visualization_recipes).where(visualization_recipes.c.id == recipe_id))
            connection.execute(insert(visualization_recipes).values(**values))

        self._with_connection(run)
        return self.get(recipe_id)

    def get(self, recipe_id: str) -> dict[str, Any]:
        row = self._fetch_one_dict(select(visualization_recipes).where(visualization_recipes.c.id == recipe_id))
        return _recipe_from_row(row)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        statement = (
            select(visualization_recipes)
            .where(visualization_recipes.c.source_job_id == job_id)
            .order_by(visualization_recipes.c.created_at, visualization_recipes.c.id)
        )
        return [_recipe_from_row(row) for row in self._fetch_all_dicts(statement)]


def _ensure_actor_and_org(connection: Connection, *, user_id: str, organization_id: str) -> None:
    _ensure_user(connection, user_id=user_id)
    exists = connection.execute(select(organizations.c.id).where(organizations.c.id == organization_id)).first()
    if exists is None:
        connection.execute(insert(organizations).values(id=organization_id, name=organization_id))


def _ensure_user(connection: Connection, *, user_id: str) -> None:
    exists = connection.execute(select(users.c.id).where(users.c.id == user_id)).first()
    if exists is None:
        connection.execute(insert(users).values(id=user_id, email=f"{user_id}@local.invalid", display_name=user_id))


def _job_event_values(event: JobEvent) -> dict[str, Any]:
    return {
        "id": event.id,
        "job_id": event.jobId,
        "seq": event.seq,
        "event_type": event.eventType,
        "status": event.status.value,
        "message": event.message,
        "progress": event.progress,
        "payload_json": event.payload or {},
        "created_at": _parse_iso(event.createdAt),
    }


def _job_event_from_row(row: Mapping[str, Any]) -> JobEvent:
    return JobEvent(
        id=str(row["id"]),
        jobId=str(row["job_id"]),
        seq=int(row["seq"]),
        eventType=str(row["event_type"]),
        status=JobEventStatus(str(row["status"])),
        message=str(row["message"]),
        progress=row.get("progress"),
        payload=_json_copy(row.get("payload_json") or {}),
        createdAt=_iso(row["created_at"]),
    )


def _project_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "projectId": row["id"],
        "organizationId": row["organization_id"],
        "name": row["name"],
        "description": row["description"],
        "createdBy": row["created_by"],
        "createdAt": _iso(row["created_at"]),
        "updatedAt": _iso(row["updated_at"]),
    }


def _dataset_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "datasetId": row["id"],
        "projectId": row["project_id"],
        "name": row["name"],
        "status": row["status"],
        "metadata": _json_copy(row.get("metadata_json") or {}),
        "createdBy": row["created_by"],
        "createdAt": _iso(row["created_at"]),
        "updatedAt": _iso(row["updated_at"]),
    }


def _job_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "jobId": row["id"],
        "projectId": row["project_id"],
        "datasetId": row["dataset_id"],
        "kind": row["kind"],
        "status": row["status"],
        "createdBy": row["created_by"],
        "createdAt": _iso(row["created_at"]),
        "updatedAt": _iso(row["updated_at"]),
    }


def _tool_call_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "jobId": row["job_id"],
        "stepId": row["step_id"],
        "toolId": row["tool_id"],
        "status": row["status"],
        "params": _json_copy(row.get("params_json") or {}),
        "error": _json_copy(row.get("error_json")) if row.get("error_json") else None,
    }


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
        "previewKey": row["preview_key"],
        "sizeBytes": row["size_bytes"],
        "contentType": row["content_type"],
        "contentHash": row["content_hash"],
        "sha256": row["sha256"],
        "metadata": _json_copy(row.get("metadata_json") or {}),
        "createdAt": _iso(row["created_at"]),
    }


def _recipe_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    recipe = _json_copy(row.get("recipe_json") or {})
    recipe.setdefault("recipeId", row["id"])
    recipe.setdefault("id", row["id"])
    recipe.setdefault("projectId", row["project_id"])
    recipe.setdefault("sourceJobId", row["source_job_id"])
    recipe.setdefault("name", row["name"])
    recipe["createdAt"] = _iso(row["created_at"])
    return recipe


def _required_id(record: Mapping[str, Any], alias: str = "id") -> str:
    value = record.get("id") or record.get(alias)
    if not value:
        raise ValueError(f"Record is missing id/{alias}")
    return str(value)


def _model_to_record(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return _json_copy(value)


def _row_to_json_dict(row: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items()}


def _json_copy(value: Any) -> Any:
    if value is None:
        return None
    return json.loads(json.dumps(value, default=str))


def _enum_value(value: Any) -> str:
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _iso(value: Any) -> str:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
