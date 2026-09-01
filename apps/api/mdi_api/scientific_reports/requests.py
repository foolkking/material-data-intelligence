from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from mdi_api.unit_of_work import RepositoryFactory

from .queue import DisabledReportQueue
from .service import ScientificReportError


class ScientificReportRequestService:
    def __init__(self, repository_factory: RepositoryFactory, *, queue: Any | None = None) -> None:
        self.repository_factory = repository_factory
        self.queue = queue or DisabledReportQueue()

    def request(self, turn_id: UUID, *, requested_by: str) -> dict[str, Any]:
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get(turn_id)
            if unit.agent2.interpretations.get_for_turn(turn_id) is None:
                raise ScientificReportError("REPORT_INTERPRETATION_NOT_READY", "报告需要已验证的 ScientificInterpretation。", 409)
            generation = unit.agent2.scientific_report_generations.create({
                "id": uuid5(NAMESPACE_URL, f"mdi:agent2-report-generation:{turn_id}"),
                "project_id": str(turn["project_id"]),
                "research_turn_id": turn_id,
                "status": "REQUESTED",
                "requested_by": requested_by,
                "attempt_count": 0,
                "error_code": None,
                "error_summary": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            })
            if str(generation["status"]).upper() == "FAILED":
                generation = unit.agent2.scientific_report_generations.set_status(
                    generation["id"],
                    "REQUESTED",
                    error_code=None,
                    error_summary=None,
                )
        try:
            queued = self.queue.enqueue_generation(generation["id"])
        except Exception as exc:
            return {**self._public(generation), "queue": {"enqueued": False, "backend": "error", "message": type(exc).__name__}}
        return {**self._public(generation), "queue": {"enqueued": queued.enqueued, "backend": queued.backend, "message": queued.message}}

    @staticmethod
    def _public(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "generation_id": str(row["id"]),
            "project_id": str(row["project_id"]),
            "research_turn_id": str(row["research_turn_id"]),
            "status": row["status"],
            "attempt_count": int(row.get("attempt_count") or 0),
            "error_code": row.get("error_code"),
            "error_summary": row.get("error_summary"),
        }


__all__ = ["ScientificReportRequestService"]
