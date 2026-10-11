from __future__ import annotations

import json
import os

from mdi_api.application.scientific_reports import generate_queued_report
from mdi_api.bootstrap.repository_factory import create_repository_factory
from mdi_api.infrastructure.scientific_reports.client import FakeStructuredReportComposerClient
from mdi_api.infrastructure.scientific_reports.service import ScientificReportService


def run_queued_report_generation(generation_id: str, *, expected_attempt: int | None = None) -> dict:
    factory = create_repository_factory()
    client = None
    fixture = os.getenv("MDI_AGENT2_REPORT_FIXTURE_JSON")
    if fixture and os.getenv("MDI_ENV", "").lower() in {"test", "ci"}:
        client = FakeStructuredReportComposerClient(json.loads(fixture))
    result = generate_queued_report(
        generation_id,
        repository_factory=factory,
        report_generator=ScientificReportService(factory, client=client),
        expected_attempt=expected_attempt,
    )
    return {**result, "process_id": os.getpid()}


__all__ = ["run_queued_report_generation"]
