from __future__ import annotations

import json
import os
from uuid import UUID

from mdi_api.database import create_repository_factory
from mdi_api.scientific_reports.client import FakeStructuredReportComposerClient
from mdi_api.scientific_reports.service import ScientificReportError, ScientificReportService


def run_queued_report_generation(generation_id: str) -> dict:
    factory = create_repository_factory()
    identifier = UUID(generation_id)
    with factory.unit_of_work() as unit:
        generation = unit.agent2.scientific_report_generations.get(identifier)
        if str(generation["status"]) == "READY":
            report = unit.agent2.scientific_reports.get_for_turn(generation["research_turn_id"])
            return {"generation_id": generation_id, "report_id": str((report or {}).get("report_id") or ""), "status": "READY", "process_id": os.getpid()}
        claimed = unit.agent2.scientific_report_generations.claim(identifier)
        if claimed is None:
            return {"generation_id": generation_id, "report_id": "", "status": str(generation["status"]), "process_id": os.getpid()}
        generation = claimed
    client = None
    fixture = os.getenv("MDI_AGENT2_REPORT_FIXTURE_JSON")
    if fixture and os.getenv("MDI_ENV", "").lower() in {"test", "ci"}:
        client = FakeStructuredReportComposerClient(json.loads(fixture))
    try:
        report = ScientificReportService(factory, client=client).generate_for_turn(generation["research_turn_id"], created_by=str(generation["requested_by"]))
    except ScientificReportError as exc:
        with factory.unit_of_work() as unit:
            unit.agent2.scientific_report_generations.set_status(identifier, "FAILED", error_code=exc.code, error_summary=str(exc)[:1000])
        raise
    with factory.unit_of_work() as unit:
        unit.agent2.scientific_report_generations.set_status(identifier, "READY")
    return {"generation_id": generation_id, "report_id": report["report_id"], "status": "READY", "process_id": os.getpid()}


__all__ = ["run_queued_report_generation"]
