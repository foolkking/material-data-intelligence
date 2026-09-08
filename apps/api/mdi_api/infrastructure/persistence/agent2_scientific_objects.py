from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import Mapping
from uuid import UUID

from sqlalchemy import Connection, func, insert, or_, select, update

from mdi_api.agent2_errors import ScientificObjectNotFound, ScientificObjectVersionNotFound

from mdi_api.db import (
    scientific_object_relationships,
    scientific_object_versions,
    scientific_objects,
)

from mdi_api.infrastructure.persistence.agent2_common import _Repository
class ScientificObjectRepository(_Repository):
    def add_object(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(scientific_objects).values(**values))
            return self._object_row(connection, values["id"])
        return self._run(run)

    def get_object(self, object_id: UUID, *, for_update: bool = False) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            statement = select(scientific_objects).where(scientific_objects.c.id == object_id)
            if for_update:
                statement = statement.with_for_update()
            return self._required(connection.execute(statement).mappings().first(), ScientificObjectNotFound(str(object_id)))
        return self._run(run)

    def list_project_objects(
        self,
        project_id: str,
        *,
        kind: str | None = None,
        object_type: str | None = None,
        lifecycle_status: str | None = None,
        search: str | None = None,
        cursor: UUID | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        statement = select(scientific_objects).where(scientific_objects.c.project_id == project_id)
        if kind:
            statement = statement.where(scientific_objects.c.kind == kind)
        if object_type:
            statement = statement.where(scientific_objects.c.object_type == object_type)
        if lifecycle_status:
            statement = statement.where(scientific_objects.c.lifecycle_status == lifecycle_status)
        if search:
            pattern = f"%{search.strip().lower()}%"
            statement = statement.where(or_(func.lower(scientific_objects.c.display_name).like(pattern), func.lower(scientific_objects.c.object_type).like(pattern)))
        if cursor:
            statement = statement.where(scientific_objects.c.id > cursor)
        statement = statement.order_by(scientific_objects.c.id.asc()).limit(limit)
        return self._run(lambda connection: [dict(row) for row in connection.execute(statement).mappings().all()])

    def add_version(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(scientific_object_versions).values(**values))
            return self._version_row(connection, values["id"])
        return self._run(run)

    def get_version(self, version_id: UUID) -> dict[str, Any]:
        return self._run(lambda connection: self._version_row(connection, version_id))

    def list_versions(self, object_id: UUID) -> list[dict[str, Any]]:
        statement = select(scientific_object_versions).where(
            scientific_object_versions.c.scientific_object_id == object_id
        ).order_by(scientific_object_versions.c.version_no.asc())
        return self._run(lambda connection: [dict(row) for row in connection.execute(statement).mappings().all()])

    def next_version_no(self, object_id: UUID) -> int:
        statement = select(func.coalesce(func.max(scientific_object_versions.c.version_no), 0) + 1).where(
            scientific_object_versions.c.scientific_object_id == object_id
        )
        return self._run(lambda connection: int(connection.execute(statement).scalar_one()))

    def set_current_version(self, object_id: UUID, version_id: UUID) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            result = connection.execute(
                update(scientific_objects)
                .where(scientific_objects.c.id == object_id)
                .values(current_version_id=version_id, row_version=scientific_objects.c.row_version + 1)
            )
            if result.rowcount != 1:
                raise ScientificObjectNotFound(str(object_id))
            return self._object_row(connection, object_id)
        return self._run(run)

    def add_relationship(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(scientific_object_relationships).values(**values))
            row = connection.execute(select(scientific_object_relationships).where(scientific_object_relationships.c.id == values["id"])).mappings().one()
            return dict(row)
        return self._run(run)

    def list_relationships(self, object_id: UUID) -> list[dict[str, Any]]:
        statement = (
            select(scientific_object_relationships)
            .join(scientific_object_versions, or_(
                scientific_object_relationships.c.source_version_id == scientific_object_versions.c.id,
                scientific_object_relationships.c.target_version_id == scientific_object_versions.c.id,
            ))
            .where(scientific_object_versions.c.scientific_object_id == object_id)
            .order_by(scientific_object_relationships.c.created_at.asc(), scientific_object_relationships.c.id.asc())
        )
        return self._run(lambda connection: [dict(row) for row in connection.execute(statement).mappings().all()])

    def archive_object(self, object_id: UUID, archived_at: datetime) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            result = connection.execute(
                update(scientific_objects)
                .where(scientific_objects.c.id == object_id)
                .values(
                    lifecycle_status="ARCHIVED",
                    archived_at=archived_at,
                    pre_trash_lifecycle_status=None,
                    row_version=scientific_objects.c.row_version + 1,
                )
            )
            if result.rowcount != 1:
                raise ScientificObjectNotFound(str(object_id))
            return self._object_row(connection, object_id)
        return self._run(run)

    def update_object_metadata(
        self,
        object_id: UUID,
        *,
        display_name: str | None = None,
        lifecycle_status: str | None = None,
        archived_at: datetime | None = None,
        pre_trash_lifecycle_status: str | None = None,
        clear_pre_trash_lifecycle: bool = False,
    ) -> dict[str, Any]:
        values: dict[str, Any] = {"row_version": scientific_objects.c.row_version + 1}
        if display_name is not None:
            values["display_name"] = display_name
        if lifecycle_status is not None:
            values["lifecycle_status"] = lifecycle_status
        if archived_at is not None or lifecycle_status == "ACTIVE":
            values["archived_at"] = archived_at
        if pre_trash_lifecycle_status is not None:
            values["pre_trash_lifecycle_status"] = pre_trash_lifecycle_status
        elif clear_pre_trash_lifecycle:
            values["pre_trash_lifecycle_status"] = None

        def run(connection: Connection) -> dict[str, Any]:
            result = connection.execute(
                update(scientific_objects)
                .where(scientific_objects.c.id == object_id)
                .values(**values)
            )
            if result.rowcount != 1:
                raise ScientificObjectNotFound(str(object_id))
            return self._object_row(connection, object_id)

        return self._run(run)

    @staticmethod
    def _required(row: Any, error: Exception) -> dict[str, Any]:
        if row is None:
            raise error
        return dict(row)

    def _object_row(self, connection: Connection, object_id: UUID) -> dict[str, Any]:
        return self._required(
            connection.execute(select(scientific_objects).where(scientific_objects.c.id == object_id)).mappings().first(),
            ScientificObjectNotFound(str(object_id)),
        )

    def _version_row(self, connection: Connection, version_id: UUID) -> dict[str, Any]:
        return self._required(
            connection.execute(select(scientific_object_versions).where(scientific_object_versions.c.id == version_id)).mappings().first(),
            ScientificObjectVersionNotFound(str(version_id)),
        )


__all__ = ['ScientificObjectRepository']
