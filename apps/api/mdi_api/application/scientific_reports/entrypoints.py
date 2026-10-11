from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from mdi_api.application.research.ports import ResearchRepositoryFactoryPort
from mdi_api.domain.scientific_reports.errors import ScientificReportError
from mdi_llm import redact_sensitive_text


class ScientificReportGeneratorPort(Protocol):
    def generate_for_turn(
        self,
        turn_id: UUID,
        *,
        created_by: str = "user_local",
        generation_id: UUID | None = None,
        expected_attempt: int | None = None,
    ) -> dict[str, Any]: ...


def generate_queued_report(
    generation_id: str,
    *,
    repository_factory: ResearchRepositoryFactoryPort,
    report_generator: ScientificReportGeneratorPort,
    expected_attempt: int | None = None,
) -> dict[str, str]:
    """Run the durable report-generation lifecycle for one queued request."""

    identifier = UUID(generation_id)
    with repository_factory.unit_of_work() as unit:
        generation = unit.agent2.scientific_report_generations.get(identifier)
        if str(generation["status"]) == "READY":
            report = unit.agent2.scientific_reports.get_for_turn(
                generation["research_turn_id"]
            )
            return {
                "generation_id": generation_id,
                "report_id": str((report or {}).get("report_id") or ""),
                "status": "READY",
            }
        claimed = unit.agent2.scientific_report_generations.claim(identifier, expected_attempt=expected_attempt)
        if claimed is None:
            return {
                "generation_id": generation_id,
                "report_id": "",
                "status": str(generation["status"]),
            }
        generation = claimed

    try:
        report = report_generator.generate_for_turn(
            generation["research_turn_id"],
            created_by=str(generation["requested_by"]),
            generation_id=identifier,
            expected_attempt=int(generation["attempt_count"]),
        )
    except ScientificReportError as exc:
        with repository_factory.unit_of_work() as unit:
            updated = unit.agent2.scientific_report_generations.compare_status(
                identifier,
                "FAILED",
                expected_status="COMPOSING", expected_attempt=int(generation["attempt_count"]),
                error_code=exc.code,
                error_summary=redact_sensitive_text(str(exc))[:1000],
            )
            if updated is None:
                current = unit.agent2.scientific_report_generations.get(identifier)
                return {"generation_id": generation_id, "report_id": "", "status": str(current["status"])}
        raise
    except Exception as exc:
        with repository_factory.unit_of_work() as unit:
            updated = unit.agent2.scientific_report_generations.compare_status(
                identifier,
                "FAILED",
                expected_status="COMPOSING", expected_attempt=int(generation["attempt_count"]),
                error_code="REPORT_GENERATION_FAILED",
                error_summary="报告生成异常结束，可重试生成；已保存的科学结果保留。",
            )
            if updated is None:
                current = unit.agent2.scientific_report_generations.get(identifier)
                return {"generation_id": generation_id, "report_id": "", "status": str(current["status"])}
        raise

    with repository_factory.unit_of_work() as unit:
        updated = unit.agent2.scientific_report_generations.compare_status(
            identifier, "READY", expected_status="COMPOSING", expected_attempt=int(generation["attempt_count"]),
        )
        if updated is None:
            current = unit.agent2.scientific_report_generations.get(identifier)
            if current["status"] != "READY":
                return {"generation_id": generation_id, "report_id": "", "status": str(current["status"])}
    return {
        "generation_id": generation_id,
        "report_id": str(report["report_id"]),
        "status": "READY",
    }


__all__ = ["ScientificReportGeneratorPort", "generate_queued_report"]
