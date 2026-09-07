"""Stable application-facing entrypoints for queued report generation."""

from mdi_api.application.scientific_reports.entrypoints import (
    ScientificReportGeneratorPort,
    generate_queued_report,
)

__all__ = ["ScientificReportGeneratorPort", "generate_queued_report"]
