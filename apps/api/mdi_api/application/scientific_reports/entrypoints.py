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
    ) -> dict[str, Any]: ...


def generate_queued_report(
    generation_id: str,
    *,
    repository_factory: ResearchRepositoryFactoryPort,
    report_generator: ScientificReportGeneratorPort,
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
        claimed = unit.agent2.scientific_report_generations.claim(identifier)
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
        )
    except ScientificReportError as exc:
        with repository_factory.unit_of_work() as unit:
            unit.agent2.scientific_report_generations.set_status(
                identifier,
                "FAILED",
                error_code=exc.code,
                error_summary=redact_sensitive_text(str(exc))[:1000],
            )
        raise
    except Exception as exc:
        with repository_factory.unit_of_work() as unit:
            unit.agent2.scientific_report_generations.set_status(
                identifier,
                "FAILED",
                error_code="REPORT_GENERATION_FAILED",
                error_summary=redact_sensitive_text(str(exc))[:1000],
            )
        raise

    with repository_factory.unit_of_work() as unit:
        unit.agent2.scientific_report_generations.set_status(identifier, "READY")
    return {
        "generation_id": generation_id,
        "report_id": str(report["report_id"]),
        "status": "READY",
    }


__all__ = ["ScientificReportGeneratorPort", "generate_queued_report"]
