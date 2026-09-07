from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID


class ScientificResultProjectorPort(Protocol):
    def project_turn(self, turn_id: UUID) -> dict[str, Any]: ...


def project_queued_result(
    turn_id: str,
    *,
    projector: ScientificResultProjectorPort,
) -> dict[str, str]:
    """Project one queued Research turn into its authoritative result."""

    row = projector.project_turn(UUID(turn_id))
    return {
        "turn_id": turn_id,
        "snapshot_id": str(row["id"]),
        "status": "RESULT_READY",
    }


__all__ = ["ScientificResultProjectorPort", "project_queued_result"]
