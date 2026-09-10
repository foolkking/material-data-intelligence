from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from mdi_api.application.research.ports import ResearchRepositoryFactoryPort


class ScientificInterpreterPort(Protocol):
    def process_turn(self, turn_id: UUID) -> dict[str, Any]: ...


class BoundedAutonomyPort(Protocol):
    def advance_after_interpretation(self, turn_id: UUID) -> Any | None: ...


def interpret_queued_turn(
    turn_id: str,
    *,
    interpreter: ScientificInterpreterPort,
    repository_factory: ResearchRepositoryFactoryPort,
    autonomy: BoundedAutonomyPort | None = None,
) -> dict[str, Any]:
    """Interpret one queued result and expose its persisted terminal status."""

    identifier = UUID(turn_id)
    row = interpreter.process_turn(identifier)
    with repository_factory.session() as session:
        status = str(session.agent2.research_turns.get(identifier)["status"])
    response: dict[str, Any] = {
        "turn_id": turn_id,
        "interpretation_id": str(row["id"]),
        "status": status,
    }
    if autonomy is not None and status in {"COMPLETED", "PARTIAL"}:
        advance = autonomy.advance_after_interpretation(identifier)
        if advance is not None:
            response["autonomy"] = advance.model_dump(mode="json")
    return response


__all__ = ["BoundedAutonomyPort", "ScientificInterpreterPort", "interpret_queued_turn"]
