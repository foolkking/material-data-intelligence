from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from mdi_api.application.research.ports import ResearchRepositoryFactoryPort


class ScientificInterpreterPort(Protocol):
    def process_turn(self, turn_id: UUID) -> dict[str, Any]: ...


def interpret_queued_turn(
    turn_id: str,
    *,
    interpreter: ScientificInterpreterPort,
    repository_factory: ResearchRepositoryFactoryPort,
) -> dict[str, str]:
    """Interpret one queued result and expose its persisted terminal status."""

    identifier = UUID(turn_id)
    row = interpreter.process_turn(identifier)
    with repository_factory.session() as session:
        status = str(session.agent2.research_turns.get(identifier)["status"])
    return {
        "turn_id": turn_id,
        "interpretation_id": str(row["id"]),
        "status": status,
    }


__all__ = ["ScientificInterpreterPort", "interpret_queued_turn"]
