from __future__ import annotations

from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Mapping
from uuid import UUID

from sqlalchemy import Connection, insert, select, update

from mdi_api.db import (
    agent2_scientific_report_generations,
    agent2_scientific_report_snapshots,
)

from mdi_api.infrastructure.persistence.agent2_common import _Repository, _optional_dict
class Agent2ScientificReportGenerationRepository(_Repository):
    def create(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            existing = connection.execute(select(agent2_scientific_report_generations).where(agent2_scientific_report_generations.c.research_turn_id == values["research_turn_id"])).mappings().first()
            if existing is not None:
                return dict(existing)
            connection.execute(insert(agent2_scientific_report_generations).values(**values))
            return dict(connection.execute(select(agent2_scientific_report_generations).where(agent2_scientific_report_generations.c.id == values["id"])).mappings().one())
        return self._run(run)

    def get(self, generation_id: UUID) -> dict[str, Any]:
        statement = select(agent2_scientific_report_generations).where(agent2_scientific_report_generations.c.id == generation_id)
        return self._run(lambda connection: dict(connection.execute(statement).mappings().one()))

    def get_for_turn(self, turn_id: UUID) -> dict[str, Any] | None:
        statement = select(agent2_scientific_report_generations).where(agent2_scientific_report_generations.c.research_turn_id == turn_id).limit(1)
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))

    def set_status(self, generation_id: UUID, status: str, *, error_code: str | None = None, error_summary: str | None = None, increment_attempt: bool = False) -> dict[str, Any]:
        values: dict[str, Any] = {"status": status, "error_code": error_code, "error_summary": error_summary, "updated_at": datetime.now(timezone.utc)}
        if increment_attempt:
            values["attempt_count"] = agent2_scientific_report_generations.c.attempt_count + 1
        statement = update(agent2_scientific_report_generations).where(agent2_scientific_report_generations.c.id == generation_id).values(**values)
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(statement)
            return dict(connection.execute(select(agent2_scientific_report_generations).where(agent2_scientific_report_generations.c.id == generation_id)).mappings().one())
        return self._run(run)

    def claim(self, generation_id: UUID) -> dict[str, Any] | None:
        now = datetime.now(timezone.utc)
        statement = update(agent2_scientific_report_generations).where(
            agent2_scientific_report_generations.c.id == generation_id,
            agent2_scientific_report_generations.c.status.in_(("REQUESTED", "FAILED")),
        ).values(
            status="COMPOSING",
            attempt_count=agent2_scientific_report_generations.c.attempt_count + 1,
            error_code=None,
            error_summary=None,
            updated_at=now,
        )
        def run(connection: Connection) -> dict[str, Any] | None:
            result = connection.execute(statement)
            if result.rowcount != 1:
                return None
            return dict(connection.execute(select(agent2_scientific_report_generations).where(agent2_scientific_report_generations.c.id == generation_id)).mappings().one())
        return self._run(run)


class Agent2ScientificReportRepository(_Repository):
    """Immutable Agent2 report snapshots linked to the existing Report identity."""

    def add(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            existing = connection.execute(
                select(agent2_scientific_report_snapshots).where(
                    agent2_scientific_report_snapshots.c.research_turn_id == values["research_turn_id"],
                    agent2_scientific_report_snapshots.c.source_fingerprint == values["source_fingerprint"],
                )
            ).mappings().first()
            if existing is not None:
                return dict(existing)
            connection.execute(insert(agent2_scientific_report_snapshots).values(**values))
            return dict(connection.execute(select(agent2_scientific_report_snapshots).where(agent2_scientific_report_snapshots.c.id == values["id"])).mappings().one())
        return self._run(run)

    def get(self, snapshot_id: UUID) -> dict[str, Any]:
        statement = select(agent2_scientific_report_snapshots).where(agent2_scientific_report_snapshots.c.id == snapshot_id)
        return self._run(lambda connection: dict(connection.execute(statement).mappings().one()))

    def get_for_turn(self, turn_id: UUID) -> dict[str, Any] | None:
        statement = select(agent2_scientific_report_snapshots).where(agent2_scientific_report_snapshots.c.research_turn_id == turn_id).order_by(agent2_scientific_report_snapshots.c.created_at.desc()).limit(1)
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))

    def list_for_turn(self, turn_id: UUID) -> list[dict[str, Any]]:
        statement = (
            select(agent2_scientific_report_snapshots)
            .where(agent2_scientific_report_snapshots.c.research_turn_id == turn_id)
            .order_by(agent2_scientific_report_snapshots.c.created_at.asc())
        )
        return self._run(
            lambda connection: [
                dict(row) for row in connection.execute(statement).mappings().all()
            ]
        )

    def get_by_report_id(self, report_id: str) -> dict[str, Any] | None:
        statement = select(agent2_scientific_report_snapshots).where(agent2_scientific_report_snapshots.c.report_id == report_id).limit(1)
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))

    def list_by_project(self, project_id: str, *, limit: int = 50) -> list[dict[str, Any]]:
        statement = select(agent2_scientific_report_snapshots).where(agent2_scientific_report_snapshots.c.project_id == project_id).order_by(agent2_scientific_report_snapshots.c.created_at.desc()).limit(limit)
        return self._run(lambda connection: [dict(row) for row in connection.execute(statement).mappings().all()])


__all__ = ['Agent2ScientificReportGenerationRepository', 'Agent2ScientificReportRepository']
