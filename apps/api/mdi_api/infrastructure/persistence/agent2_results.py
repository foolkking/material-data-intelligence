from __future__ import annotations

from typing import Any
from typing import Mapping
from uuid import UUID

from sqlalchemy import Connection, and_, insert, select

from mdi_api.agent2_errors import ScientificResultSnapshotNotFound

from mdi_api.db import (
    research_turns,
    scientific_result_snapshots,
)

from mdi_api.infrastructure.persistence.agent2_common import _Repository, _optional_dict
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


__all__ = ['ScientificResultSnapshotRepository']
