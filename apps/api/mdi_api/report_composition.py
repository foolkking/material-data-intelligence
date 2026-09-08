"""Compatibility facade for report composition."""

# ruff: noqa: F401

from mdi_api.infrastructure.reports.composition import (
    CompositionPreview,
    REPORT_EXPORT_MAX_BYTES,
    ReportCompositionDomainError,
    ReportCompositionService,
    ReportSourceEligibilityProjector,
    _ARTIFACT_REPORT_ROLES,
    _provider_report_projection,
)

__all__ = [
    "CompositionPreview",
    "REPORT_EXPORT_MAX_BYTES",
    "ReportCompositionDomainError",
    "ReportCompositionService",
    "ReportSourceEligibilityProjector",
]
