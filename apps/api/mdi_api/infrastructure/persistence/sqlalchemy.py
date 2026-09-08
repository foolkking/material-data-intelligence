"""SQLAlchemy Project/Data persistence implementations."""

from __future__ import annotations

from typing import Any, Mapping

from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Connection

from mdi_schemas import DataProfile

from mdi_api.db import (
    data_profiles,
    datasets,
    organizations,
    project_members,
    projects,
    users,
)
from mdi_api.infrastructure.persistence.base import (
    _SqlAlchemyRepository,
    _json_copy,
    _model_to_record,
    _required_id,
    _iso,
)


def _ensure_actor_and_org(connection: Connection, *, user_id: str, organization_id: str) -> None:
    _ensure_user(connection, user_id=user_id)
    exists = connection.execute(select(organizations.c.id).where(organizations.c.id == organization_id)).first()
    if exists is None:
        connection.execute(insert(organizations).values(id=organization_id, name=organization_id))


def _ensure_user(connection: Connection, *, user_id: str) -> None:
    exists = connection.execute(select(users.c.id).where(users.c.id == user_id)).first()
    if exists is None:
        connection.execute(insert(users).values(id=user_id, email=f"{user_id}@local.invalid", display_name=user_id))


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


def _data_profile_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    profile = _json_copy(row.get("profile_json") or {})
    profile.setdefault("id", row["id"])
    profile.setdefault("profileId", row["id"])
    profile.setdefault("datasetId", row["dataset_id"])
    profile.setdefault("version", row["version"])
    profile["createdAt"] = profile.get("createdAt") or _iso(row["created_at"])
    return profile


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
            existing = connection.execute(
                select(projects.c.id).where(projects.c.id == project_id)
            ).scalar_one_or_none()
            if existing is None:
                connection.execute(insert(projects).values(**values))
            else:
                connection.execute(
                    update(projects)
                    .where(projects.c.id == project_id)
                    .values(
                        organization_id=organization_id,
                        name=values["name"],
                        description=values["description"],
                        created_by=created_by,
                    )
                )
            owner_membership = connection.execute(
                select(project_members.c.role).where(
                    project_members.c.project_id == project_id,
                    project_members.c.user_id == created_by,
                )
            ).scalar_one_or_none()
            if owner_membership is None:
                connection.execute(
                    insert(project_members).values(
                        project_id=project_id,
                        user_id=created_by,
                        role="owner",
                    )
                )

        self._with_connection(run)
        return self.get(project_id)

    def get(self, project_id: str) -> dict[str, Any]:
        return _project_from_row(self._fetch_one_dict(select(projects).where(projects.c.id == project_id)))

    def list(self) -> list[dict[str, Any]]:
        return [
            _project_from_row(row)
            for row in self._fetch_all_dicts(select(projects).order_by(projects.c.created_at, projects.c.id))
        ]


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

    def list(self) -> list[dict[str, Any]]:
        statement = select(datasets).order_by(datasets.c.project_id, datasets.c.created_at, datasets.c.id)
        return [_dataset_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        statement = (
            select(datasets)
            .where(datasets.c.project_id == project_id)
            .order_by(datasets.c.created_at, datasets.c.id)
        )
        return [_dataset_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        return self.list_for_project(project_id)


class SqlAlchemyDataProfileRepository(_SqlAlchemyRepository):
    def save(self, profile: DataProfile | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(profile)
        profile_id = _required_id(record, "profileId")
        values = {
            "id": profile_id,
            "dataset_id": str(record["datasetId"]),
            "version": str(record.get("version") or "1"),
            "profile_json": _json_copy(record),
        }

        def run(connection: Connection) -> None:
            connection.execute(delete(data_profiles).where(data_profiles.c.id == profile_id))
            connection.execute(insert(data_profiles).values(**values))

        self._with_connection(run)
        return self.get(profile_id)

    def get(self, profile_id: str) -> dict[str, Any]:
        return _data_profile_from_row(
            self._fetch_one_dict(select(data_profiles).where(data_profiles.c.id == profile_id))
        )

    def list(self) -> list[dict[str, Any]]:
        statement = select(data_profiles).order_by(
            data_profiles.c.dataset_id,
            data_profiles.c.created_at,
            data_profiles.c.id,
        )
        return [_data_profile_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_for_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        statement = (
            select(data_profiles)
            .where(data_profiles.c.dataset_id == dataset_id)
            .order_by(data_profiles.c.created_at, data_profiles.c.id)
        )
        return [_data_profile_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        statement = (
            select(data_profiles)
            .select_from(data_profiles.join(datasets, data_profiles.c.dataset_id == datasets.c.id))
            .where(datasets.c.project_id == project_id)
            .order_by(data_profiles.c.created_at, data_profiles.c.id)
        )
        return [_data_profile_from_row(row) for row in self._fetch_all_dicts(statement)]


__all__ = [
    "SqlAlchemyDataProfileRepository",
    "SqlAlchemyDatasetRepository",
    "SqlAlchemyProjectRepository",
]
