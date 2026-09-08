"""Compatibility facade for report generation service."""
from mdi_api.domain.scientific_reports.errors import ScientificReportError
from mdi_api.infrastructure.scientific_reports.service import ScientificReportService
__all__ = ["ScientificReportError", "ScientificReportService"]
