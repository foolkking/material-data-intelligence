from __future__ import annotations

from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Mapping
from uuid import UUID

from sqlalchemy import Connection, and_, func, insert, select, update

from mdi_api.agent2_errors import ConcurrentTurnModification, ResearchTurnNotFound

from mdi_api.db import (
    messages,
    projects,
    research_capability_plans,
    research_capability_resolutions,
    research_context_snapshots,
    research_execution_summaries,
    research_session_context_items,
    research_session_states,
    research_turn_decisions,
    research_turn_events,
    research_turns,
    sessions,
)

from mdi_api.infrastructure.persistence.agent2_common import _Repository, _optional_dict
class ResearchTurnRepository(_Repository):
    def get_session(self, session_id: str) -> dict[str, Any] | None:
        statement = select(sessions).where(sessions.c.id == session_id)
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))

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

    def get_for_job(self, job_id: str, *, for_update: bool = False) -> dict[str, Any] | None:
        statement = select(research_turns).where(research_turns.c.job_id == job_id)
        if for_update:
            statement = statement.with_for_update()
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))

    def lock_project_for_turn_admission(self, project_id: str) -> None:
        """Serialize the bounded active-Turn admission decision per Project."""

        statement = select(projects.c.id).where(projects.c.id == project_id).with_for_update()
        self._run(lambda connection: connection.execute(statement).scalar_one())

    def count_active_for_project(self, project_id: str) -> int:
        terminal = (
            "NEEDS_CLARIFICATION", "ANSWERED", "UNSUPPORTED", "PLAN_REJECTED",
            "COMPLETED", "PARTIAL", "FAILED", "CANCELED",
        )
        statement = select(func.count()).select_from(research_turns).where(
            research_turns.c.project_id == project_id,
            research_turns.c.status.not_in(terminal),
        )
        return self._run(lambda connection: int(connection.execute(statement).scalar_one()))

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

    def list_all_before(self, session_id: str, sequence_no: int, *, limit: int = 500) -> list[dict[str, Any]]:
        """Bounded long-session history, ordered newest first for retrieval."""
        statement = (
            select(research_turns)
            .where(and_(research_turns.c.research_session_id == session_id, research_turns.c.sequence_no < sequence_no))
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

    def attach_job(self, turn_id: UUID, job_id: str) -> dict[str, Any]:
        """Attach exactly one existing Job to a Turn using a compare-safe write."""
        def run(connection: Connection) -> dict[str, Any]:
            result = connection.execute(
                update(research_turns)
                .where(and_(research_turns.c.id == turn_id, research_turns.c.job_id.is_(None)))
                .values(job_id=job_id, row_version=research_turns.c.row_version + 1, updated_at=datetime.now(timezone.utc))
            )
            if result.rowcount != 1:
                current = self._row(connection, turn_id)
                if str(current.get("job_id") or "") == str(job_id):
                    return current
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


class ResearchSessionMemoryRepository(_Repository):
    """Persistence boundary for mutable session memory and its audit items."""

    def get_state(self, session_id: str, *, for_update: bool = False) -> dict[str, Any] | None:
        statement = select(research_session_states).where(research_session_states.c.session_id == session_id)
        if for_update:
            statement = statement.with_for_update()
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))

    def ensure_state(self, *, session_id: str, project_id: str, state_id: UUID) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            existing = connection.execute(select(research_session_states).where(research_session_states.c.session_id == session_id)).mappings().first()
            if existing is not None:
                return dict(existing)
            connection.execute(insert(research_session_states).values(
                id=state_id, session_id=session_id, project_id=project_id,
                active_scope_refs_json=[], active_selection_refs_json=[],
                pinned_object_refs_json=[], pinned_result_refs_json=[],
                session_constraints_json=[], open_questions_json=[], version=1,
            ))
            return dict(connection.execute(select(research_session_states).where(research_session_states.c.session_id == session_id)).mappings().one())
        return self._run(run)

    def update_state(self, session_id: str, *, expected_version: int, values: Mapping[str, Any]) -> dict[str, Any]:
        statement = update(research_session_states).where(and_(
            research_session_states.c.session_id == session_id,
            research_session_states.c.version == expected_version,
        )).values(**values, version=expected_version + 1, updated_at=datetime.now(timezone.utc))
        def run(connection: Connection) -> dict[str, Any]:
            result = connection.execute(statement)
            if result.rowcount != 1:
                raise ConcurrentTurnModification(f"ResearchSession state version changed: {session_id}")
            return dict(connection.execute(select(research_session_states).where(research_session_states.c.session_id == session_id)).mappings().one())
        return self._run(run)

    def add_item(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(research_session_context_items).values(**values))
            return dict(connection.execute(select(research_session_context_items).where(research_session_context_items.c.id == values["id"])).mappings().one())
        return self._run(run)

    def list_items(self, session_id: str, *, active_only: bool = True, limit: int = 200) -> list[dict[str, Any]]:
        statement = select(research_session_context_items).where(research_session_context_items.c.session_id == session_id)
        if active_only:
            statement = statement.where(research_session_context_items.c.active.is_(True))
        statement = statement.order_by(research_session_context_items.c.created_at.asc(), research_session_context_items.c.id.asc()).limit(limit)
        return self._run(lambda connection: [dict(row) for row in connection.execute(statement).mappings().all()])

    def deactivate_items(self, session_id: str, *, item_type: str, predicate: Any | None = None) -> int:
        statement = update(research_session_context_items).where(and_(
            research_session_context_items.c.session_id == session_id,
            research_session_context_items.c.item_type == item_type,
            research_session_context_items.c.active.is_(True),
        )).values(active=False, updated_at=datetime.now(timezone.utc))
        def run(connection: Connection) -> int:
            if predicate is None:
                return int(connection.execute(statement).rowcount or 0)
            rows = connection.execute(select(research_session_context_items).where(and_(
                research_session_context_items.c.session_id == session_id,
                research_session_context_items.c.item_type == item_type,
                research_session_context_items.c.active.is_(True),
            ))).mappings().all()
            ids = [row["id"] for row in rows if predicate(dict(row))]
            if not ids:
                return 0
            return int(connection.execute(update(research_session_context_items).where(research_session_context_items.c.id.in_(ids)).values(active=False, updated_at=datetime.now(timezone.utc))).rowcount or 0)
        return self._run(run)


class ResearchTurnEventRepository(_Repository):
    def append_turn_event(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(research_turn_events).values(**values))
            return dict(connection.execute(select(research_turn_events).where(research_turn_events.c.id == values["id"])).mappings().one())
        return self._run(run)

    def next_sequence_no(self, turn_id: UUID) -> int:
        def run(connection: Connection) -> int:
            # Event append is intentionally a separate repository operation in
            # several lifecycle services. Serialize sequence allocation on the
            # authoritative turn row so concurrent transactions cannot both
            # observe the same MAX(sequence_no).
            connection.execute(
                select(research_turns.c.id)
                .where(research_turns.c.id == turn_id)
                .with_for_update()
            ).scalar_one()
            statement = select(func.coalesce(func.max(research_turn_events.c.sequence_no), 0) + 1).where(
                research_turn_events.c.turn_id == turn_id
            )
            return int(connection.execute(statement).scalar_one())

        return self._run(run)

    def list_for_turn(self, turn_id: UUID, *, after_sequence: int = 0) -> list[dict[str, Any]]:
        statement = select(research_turn_events).where(and_(
            research_turn_events.c.turn_id == turn_id,
            research_turn_events.c.sequence_no > after_sequence,
        )).order_by(research_turn_events.c.sequence_no.asc())
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

    def complete_legacy_dispatch(self, turn_id: UUID) -> dict[str, Any]:
        """Repair the bounded pre-terminal QUERY_DATA projection defect.

        The orchestration decision itself remains immutable.  Only its
        delivery projection advances from the historical
        ``READY_FOR_DOWNSTREAM`` value to ``COMPLETED`` after the owning Turn
        has been deterministically terminalized.
        """

        def run(connection: Connection) -> dict[str, Any]:
            result = connection.execute(
                update(research_turn_decisions)
                .where(and_(
                    research_turn_decisions.c.research_turn_id == turn_id,
                    research_turn_decisions.c.action == "QUERY_DATA",
                    research_turn_decisions.c.action_dispatch_status == "READY_FOR_DOWNSTREAM",
                ))
                .values(action_dispatch_status="COMPLETED")
            )
            if result.rowcount != 1:
                current = connection.execute(
                    select(research_turn_decisions).where(
                        research_turn_decisions.c.research_turn_id == turn_id
                    )
                ).mappings().first()
                if current is None or str(current["action_dispatch_status"]) != "COMPLETED":
                    raise ConcurrentTurnModification(str(turn_id))
            return dict(connection.execute(
                select(research_turn_decisions).where(
                    research_turn_decisions.c.research_turn_id == turn_id
                )
            ).mappings().one())

        return self._run(run)


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


class ResearchExecutionSummaryRepository(_Repository):
    """Immutable projection of terminal Job/ToolCall/Artifact facts."""

    def add(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            existing = connection.execute(
                select(research_execution_summaries).where(
                    research_execution_summaries.c.research_turn_id == values["research_turn_id"]
                )
            ).mappings().first()
            if existing is not None:
                if str(existing["source_fingerprint"]) != str(values["source_fingerprint"]):
                    from mdi_api.research_agent.execution.errors import ExecutionSummaryConflict
                    raise ExecutionSummaryConflict("terminal execution facts changed for an immutable ResearchTurn")
                return dict(existing)
            connection.execute(insert(research_execution_summaries).values(**values))
            return dict(connection.execute(
                select(research_execution_summaries).where(research_execution_summaries.c.id == values["id"])
            ).mappings().one())
        return self._run(run)

    def get_for_turn(self, turn_id: UUID) -> dict[str, Any] | None:
        statement = select(research_execution_summaries).where(research_execution_summaries.c.research_turn_id == turn_id)
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))

    def get_for_job(self, job_id: str) -> dict[str, Any] | None:
        statement = select(research_execution_summaries).where(research_execution_summaries.c.job_id == job_id)
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))


__all__ = ['ResearchTurnRepository', 'ResearchContextSnapshotRepository', 'ResearchSessionMemoryRepository', 'ResearchTurnEventRepository', 'ResearchTurnDecisionRepository', 'ResearchCapabilityResolutionRepository', 'ResearchCapabilityPlanRepository', 'ResearchExecutionSummaryRepository']
