from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from mdi_api.unit_of_work import RepositoryFactory

from mdi_api.infrastructure.scientific_reports.queue import DisabledReportQueue
from mdi_api.domain.scientific_reports.errors import ScientificReportError
from mdi_api.application.interpretation.grounding import project_grounded_communication, validate_interpretation
from mdi_api.domain.interpretation.contracts import ScientificInterpretationOutput
from mdi_api.domain.scientific_results.contracts import ScientificResultBundle


class ScientificReportRequestService:
    def __init__(self, repository_factory: RepositoryFactory, *, queue: Any | None = None) -> None:
        self.repository_factory = repository_factory
        self.queue = queue or DisabledReportQueue()

    def request(self, turn_id: UUID, *, requested_by: str) -> dict[str, Any]:
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get(turn_id)
            interpretation = unit.agent2.interpretations.get_for_turn(turn_id)
            if interpretation is None:
                raise ScientificReportError("REPORT_INTERPRETATION_NOT_READY", "报告需要已验证的 ScientificInterpretation。", 409)
            snapshot = unit.agent2.scientific_result_snapshots.get(interpretation["result_snapshot_id"])
            bundle = ScientificResultBundle.model_validate(snapshot["bundle_json"])
            readable = project_grounded_communication(
                ScientificInterpretationOutput.model_validate(interpretation["output_json"]["interpretation"]), bundle,
            )
            if (
                str(snapshot["project_id"]) != str(turn["project_id"])
                or interpretation["grounding_status"] != "VALID"
                or not validate_interpretation(readable, bundle).valid
            ):
                raise ScientificReportError("REPORT_INTERPRETATION_REJECTED", "原解读未通过当前事实校验。请先重新解读或编辑问题后重试。", 409)
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
                updated = unit.agent2.scientific_report_generations.compare_status(
                    generation["id"],
                    "REQUESTED",
                    expected_status="FAILED", expected_attempt=int(generation["attempt_count"]),
                    expected_updated_at=generation["updated_at"],
                    error_code=None,
                    error_summary=None,
                )
                generation = updated or unit.agent2.scientific_report_generations.get(generation["id"])
        if generation["status"] != "REQUESTED":
            return {**self._public(generation), "queue": {"enqueued": False, "backend": "durable", "message": "report request already handled"}}
        try:
            queued = self.queue.enqueue_generation(generation["id"], attempt=int(generation["attempt_count"]) + 1)
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
