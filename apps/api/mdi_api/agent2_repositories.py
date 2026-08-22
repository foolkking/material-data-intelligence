from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import UUID

from sqlalchemy import Connection, Engine, and_, func, insert, or_, select, update

from mdi_api.agent2_errors import (
    ConcurrentTurnModification,
    ResearchTurnNotFound,
    ScientificObjectNotFound,
    ScientificObjectVersionNotFound,
    ScientificResultSnapshotNotFound,
)
from mdi_api.db import (
    messages,
    research_context_snapshots,
    research_turn_decisions,
    research_capability_resolutions,
    research_capability_plans,
    research_turn_events,
    research_turns,
    scientific_object_relationships,
    scientific_object_versions,
    scientific_objects,
    scientific_result_snapshots,
    sessions,
)


class _Repository:
    def __init__(self, bind: Engine | Connection) -> None:
        self.bind = bind

    def _run(self, fn: Any) -> Any:
        if isinstance(self.bind, Engine):
            with self.bind.begin() as connection:
                return fn(connection)
        return fn(self.bind)


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
                .values(lifecycle_status="ARCHIVED", archived_at=archived_at, row_version=scientific_objects.c.row_version + 1)
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


class ResearchTurnRepository(_Repository):
    def lock_session(self, session_id: str) -> dict[str, Any] | None:
        statement = select(sessions).where(sessions.c.id == session_id).with_for_update()
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))

    def allocate_sequence(self, session_id: str) -> int:
        statement = select(func.coalesce(func.max(research_turns.c.sequence_no), 0) + 1).where(
            research_turns.c.research_session_id == session_id
        )
        return self._run(lambda connection: int(connection.execute(statement).scalar_one()))

    def add_message(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(messages).values(**values))
            return dict(connection.execute(select(messages).where(messages.c.id == values["id"])).mappings().one())
        return self._run(run)

    def add(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(research_turns).values(**values))
            return self._row(connection, values["id"])
        return self._run(run)

    def get(self, turn_id: UUID, *, for_update: bool = False) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            statement = select(research_turns).where(research_turns.c.id == turn_id)
            if for_update:
                statement = statement.with_for_update()
            return self._required(connection.execute(statement).mappings().first(), turn_id)
        return self._run(run)

    def get_for_update(self, turn_id: UUID) -> dict[str, Any]:
        return self.get(turn_id, for_update=True)

    def list_for_session(self, session_id: str, *, cursor: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
        statement = select(research_turns).where(research_turns.c.research_session_id == session_id)
        if cursor is not None:
            statement = statement.where(research_turns.c.sequence_no > cursor)
        statement = statement.order_by(research_turns.c.sequence_no.asc()).limit(limit)
        return self._run(lambda connection: [dict(row) for row in connection.execute(statement).mappings().all()])

    def list_recent_before(self, session_id: str, sequence_no: int, *, limit: int = 6) -> list[dict[str, Any]]:
        terminal_statuses = (
            "NEEDS_CLARIFICATION", "ANSWERED", "UNSUPPORTED", "PLAN_REJECTED",
            "COMPLETED", "PARTIAL", "FAILED", "CANCELED",
        )
        statement = (
            select(research_turns)
            .where(and_(
                research_turns.c.research_session_id == session_id,
                research_turns.c.sequence_no < sequence_no,
                research_turns.c.status.in_(terminal_statuses),
            ))
            .order_by(research_turns.c.sequence_no.desc())
            .limit(limit)
        )
        return self._run(lambda connection: [dict(row) for row in connection.execute(statement).mappings().all()])

    def get_message(self, message_id: str) -> dict[str, Any]:
        statement = select(messages).where(messages.c.id == message_id)
        return self._run(lambda connection: dict(connection.execute(statement).mappings().one()))

    def compare_and_set_status(
        self,
        turn_id: UUID,
        *,
        expected_status: str,
        expected_version: int,
        target_status: str,
        completed_at: datetime | None = None,
        error_code: str | None = None,
        error_summary: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        values: dict[str, Any] = {
            "status": target_status,
            "row_version": research_turns.c.row_version + 1,
            "updated_at": now,
        }
        if target_status == "RESOLVING_CONTEXT":
            values["started_at"] = now
        if completed_at is not None:
            values["completed_at"] = completed_at
        if error_code is not None:
            values["error_code"] = error_code
        if error_summary is not None:
            values["error_summary"] = error_summary

        def run(connection: Connection) -> dict[str, Any]:
            result = connection.execute(
                update(research_turns)
                .where(and_(
                    research_turns.c.id == turn_id,
                    research_turns.c.status == expected_status,
                    research_turns.c.row_version == expected_version,
                ))
                .values(**values)
            )
            if result.rowcount != 1:
                raise ConcurrentTurnModification(str(turn_id))
            return self._row(connection, turn_id)
        return self._run(run)

    def attach_context_snapshot(self, turn_id: UUID, snapshot_id: UUID) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            result = connection.execute(
                update(research_turns)
                .where(and_(research_turns.c.id == turn_id, research_turns.c.context_snapshot_id.is_(None)))
                .values(context_snapshot_id=snapshot_id, row_version=research_turns.c.row_version + 1, updated_at=datetime.now(timezone.utc))
            )
            if result.rowcount != 1:
                raise ConcurrentTurnModification(str(turn_id))
            return self._row(connection, turn_id)
        return self._run(run)

    def attach_message_refs(self, turn_id: UUID, *, assistant_pre_message_id: str | None = None, assistant_final_message_id: str | None = None) -> dict[str, Any]:
        values = {key: value for key, value in {
            "assistant_pre_message_id": assistant_pre_message_id,
            "assistant_final_message_id": assistant_final_message_id,
        }.items() if value is not None}
        values.update(row_version=research_turns.c.row_version + 1, updated_at=datetime.now(timezone.utc))
        def run(connection: Connection) -> dict[str, Any]:
            result = connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(**values))
            if result.rowcount != 1:
                raise ResearchTurnNotFound(str(turn_id))
            return self._row(connection, turn_id)
        return self._run(run)

    def attach_analysis_plan(self, turn_id: UUID, plan_id: str) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            result = connection.execute(
                update(research_turns)
                .where(and_(research_turns.c.id == turn_id, research_turns.c.analysis_plan_id.is_(None)))
                .values(analysis_plan_id=plan_id, row_version=research_turns.c.row_version + 1, updated_at=datetime.now(timezone.utc))
            )
            if result.rowcount != 1:
                raise ConcurrentTurnModification(str(turn_id))
            return self._row(connection, turn_id)
        return self._run(run)

    def apply_decision_projection(
        self,
        turn_id: UUID,
        *,
        expected_version: int,
        action_type: str,
        target_status: str,
        assistant_pre_message_id: str | None = None,
        assistant_final_message_id: str | None = None,
        continuation_of_turn_id: UUID | None = None,
        completed_at: datetime | None = None,
    ) -> dict[str, Any]:
        values: dict[str, Any] = {
            "action_type": action_type,
            "status": target_status,
            "assistant_pre_message_id": assistant_pre_message_id,
            "assistant_final_message_id": assistant_final_message_id,
            "row_version": research_turns.c.row_version + 1,
            "updated_at": datetime.now(timezone.utc),
        }
        if continuation_of_turn_id is not None:
            values["continuation_of_turn_id"] = continuation_of_turn_id
        if completed_at is not None:
            values["completed_at"] = completed_at

        def run(connection: Connection) -> dict[str, Any]:
            result = connection.execute(
                update(research_turns)
                .where(and_(
                    research_turns.c.id == turn_id,
                    research_turns.c.status == "ORCHESTRATING",
                    research_turns.c.row_version == expected_version,
                    research_turns.c.action_type.is_(None),
                ))
                .values(**values)
            )
            if result.rowcount != 1:
                raise ConcurrentTurnModification(str(turn_id))
            return self._row(connection, turn_id)
        return self._run(run)

    def referenced_messages(self, turn: Mapping[str, Any]) -> list[dict[str, Any]]:
        ids = [turn.get("user_message_id"), turn.get("assistant_pre_message_id"), turn.get("assistant_final_message_id")]
        ids = [str(item) for item in ids if item]
        if not ids:
            return []
        statement = select(messages).where(messages.c.id.in_(ids))
        rows = self._run(lambda connection: [dict(row) for row in connection.execute(statement).mappings().all()])
        order = {item: index for index, item in enumerate(ids)}
        return sorted(rows, key=lambda row: order[str(row["id"])])

    @staticmethod
    def _required(row: Any, turn_id: UUID) -> dict[str, Any]:
        if row is None:
            raise ResearchTurnNotFound(str(turn_id))
        return dict(row)

    def _row(self, connection: Connection, turn_id: UUID) -> dict[str, Any]:
        return self._required(
            connection.execute(select(research_turns).where(research_turns.c.id == turn_id)).mappings().first(),
            turn_id,
        )


class ResearchContextSnapshotRepository(_Repository):
    def add(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(research_context_snapshots).values(**values))
            return dict(connection.execute(select(research_context_snapshots).where(research_context_snapshots.c.id == values["id"])).mappings().one())
        return self._run(run)

    def get_for_turn(self, turn_id: UUID) -> dict[str, Any] | None:
        statement = select(research_context_snapshots).where(research_context_snapshots.c.research_turn_id == turn_id)
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))


class ResearchTurnEventRepository(_Repository):
    def append_turn_event(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(research_turn_events).values(**values))
            return dict(connection.execute(select(research_turn_events).where(research_turn_events.c.id == values["id"])).mappings().one())
        return self._run(run)

    def next_sequence_no(self, turn_id: UUID) -> int:
        statement = select(func.coalesce(func.max(research_turn_events.c.sequence_no), 0) + 1).where(research_turn_events.c.turn_id == turn_id)
        return self._run(lambda connection: int(connection.execute(statement).scalar_one()))

    def list_for_turn(self, turn_id: UUID, *, after_sequence: int = 0) -> list[dict[str, Any]]:
        statement = select(research_turn_events).where(and_(
            research_turn_events.c.turn_id == turn_id,
            research_turn_events.c.sequence_no > after_sequence,
        )).order_by(research_turn_events.c.sequence_no.asc())
        return self._run(lambda connection: [dict(row) for row in connection.execute(statement).mappings().all()])


class ScientificResultSnapshotRepository(_Repository):
    def add(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(scientific_result_snapshots).values(**values))
            return dict(connection.execute(select(scientific_result_snapshots).where(scientific_result_snapshots.c.id == values["id"])).mappings().one())
        return self._run(run)

    def get_latest_for_turn(self, turn_id: UUID) -> dict[str, Any]:
        statement = select(scientific_result_snapshots).where(
            scientific_result_snapshots.c.research_turn_id == turn_id
        ).order_by(scientific_result_snapshots.c.created_at.desc(), scientific_result_snapshots.c.id.desc()).limit(1)
        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(statement).mappings().first()
            if row is None:
                raise ScientificResultSnapshotNotFound(str(turn_id))
            return dict(row)
        return self._run(run)

    def get_by_identity(self, turn_id: UUID, projection_version: str, source_fingerprint: str) -> dict[str, Any] | None:
        statement = select(scientific_result_snapshots).where(and_(
            scientific_result_snapshots.c.research_turn_id == turn_id,
            scientific_result_snapshots.c.projection_version == projection_version,
            scientific_result_snapshots.c.source_fingerprint == source_fingerprint,
        ))
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))

    def get(self, snapshot_id: UUID) -> dict[str, Any]:
        statement = select(scientific_result_snapshots).where(scientific_result_snapshots.c.id == snapshot_id)
        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(statement).mappings().first()
            if row is None:
                raise ScientificResultSnapshotNotFound(str(snapshot_id))
            return dict(row)
        return self._run(run)

    def list_for_turn(self, turn_id: UUID) -> list[dict[str, Any]]:
        statement = select(scientific_result_snapshots).where(
            scientific_result_snapshots.c.research_turn_id == turn_id
        ).order_by(scientific_result_snapshots.c.created_at.asc(), scientific_result_snapshots.c.id.asc())
        return self._run(lambda connection: [dict(row) for row in connection.execute(statement).mappings().all()])

    def exists_for_turn(self, turn_id: UUID) -> bool:
        statement = select(scientific_result_snapshots.c.id).where(scientific_result_snapshots.c.research_turn_id == turn_id).limit(1)
        return self._run(lambda connection: connection.execute(statement).first() is not None)

    def list_recent_for_session(
        self,
        session_id: str,
        *,
        before_sequence: int,
        limit: int = 6,
    ) -> list[dict[str, Any]]:
        statement = (
            select(scientific_result_snapshots, research_turns.c.sequence_no)
            .join(research_turns, scientific_result_snapshots.c.research_turn_id == research_turns.c.id)
            .where(and_(
                research_turns.c.research_session_id == session_id,
                research_turns.c.sequence_no < before_sequence,
            ))
            .order_by(research_turns.c.sequence_no.desc(), scientific_result_snapshots.c.created_at.desc())
            .limit(limit)
        )
        return self._run(lambda connection: [dict(row) for row in connection.execute(statement).mappings().all()])


class ResearchTurnDecisionRepository(_Repository):
    def add(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(research_turn_decisions).values(**values))
            return dict(connection.execute(
                select(research_turn_decisions).where(research_turn_decisions.c.id == values["id"])
            ).mappings().one())
        return self._run(run)

    def get_for_turn(self, turn_id: UUID) -> dict[str, Any] | None:
        statement = select(research_turn_decisions).where(research_turn_decisions.c.research_turn_id == turn_id)
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))


class ResearchCapabilityResolutionRepository(_Repository):
    def add(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(research_capability_resolutions).values(**values))
            return dict(connection.execute(select(research_capability_resolutions).where(research_capability_resolutions.c.id == values["id"])).mappings().one())
        return self._run(run)

    def get_for_turn(self, turn_id: UUID) -> dict[str, Any] | None:
        statement = select(research_capability_resolutions).where(research_capability_resolutions.c.research_turn_id == turn_id)
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))


class ResearchCapabilityPlanRepository(_Repository):
    def add(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(research_capability_plans).values(**values))
            return dict(connection.execute(select(research_capability_plans).where(research_capability_plans.c.id == values["id"])).mappings().one())
        return self._run(run)

    def get_for_turn(self, turn_id: UUID) -> dict[str, Any] | None:
        statement = select(research_capability_plans).where(research_capability_plans.c.research_turn_id == turn_id)
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))


@dataclass(frozen=True)
class Agent2RepositoryBundle:
    scientific_objects: ScientificObjectRepository
    research_turns: ResearchTurnRepository
    research_context_snapshots: ResearchContextSnapshotRepository
    research_turn_events: ResearchTurnEventRepository
    scientific_result_snapshots: ScientificResultSnapshotRepository
    research_turn_decisions: ResearchTurnDecisionRepository
    research_capability_resolutions: ResearchCapabilityResolutionRepository
    research_capability_plans: ResearchCapabilityPlanRepository

    @classmethod
    def create(cls, bind: Engine | Connection) -> "Agent2RepositoryBundle":
        return cls(
            scientific_objects=ScientificObjectRepository(bind),
            research_turns=ResearchTurnRepository(bind),
            research_context_snapshots=ResearchContextSnapshotRepository(bind),
            research_turn_events=ResearchTurnEventRepository(bind),
            scientific_result_snapshots=ScientificResultSnapshotRepository(bind),
            research_turn_decisions=ResearchTurnDecisionRepository(bind),
            research_capability_resolutions=ResearchCapabilityResolutionRepository(bind),
            research_capability_plans=ResearchCapabilityPlanRepository(bind),
        )


def _optional_dict(row: Any) -> dict[str, Any] | None:
    return dict(row) if row is not None else None
