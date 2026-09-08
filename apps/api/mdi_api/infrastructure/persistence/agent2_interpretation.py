from __future__ import annotations

from typing import Any
from typing import Mapping
from uuid import UUID

from sqlalchemy import Connection, insert, select

from mdi_api.db import (
    agent2_scientific_interpretations,
)

from mdi_api.infrastructure.persistence.agent2_common import _Repository, _optional_dict
class Agent2ScientificInterpretationRepository(_Repository):
    """Immutable Agent2 interpretation snapshots and idempotency boundary."""

    def add(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            existing = connection.execute(
                select(agent2_scientific_interpretations).where(
                    agent2_scientific_interpretations.c.research_turn_id == values["research_turn_id"]
                )
            ).mappings().first()
            if existing is not None:
                if str(existing["input_fingerprint"]) != str(values["input_fingerprint"]):
                    raise ValueError("Agent2 interpretations are immutable")
                return dict(existing)
            connection.execute(insert(agent2_scientific_interpretations).values(**values))
            return dict(connection.execute(select(agent2_scientific_interpretations).where(agent2_scientific_interpretations.c.id == values["id"])).mappings().one())
        return self._run(run)

    def get_for_turn(self, turn_id: UUID) -> dict[str, Any] | None:
        statement = select(agent2_scientific_interpretations).where(agent2_scientific_interpretations.c.research_turn_id == turn_id)
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))

    def get(self, interpretation_id: UUID) -> dict[str, Any]:
        statement = select(agent2_scientific_interpretations).where(agent2_scientific_interpretations.c.id == interpretation_id)
        return self._run(lambda connection: dict(connection.execute(statement).mappings().one()))


__all__ = ['Agent2ScientificInterpretationRepository']
