from __future__ import annotations

import mdi_api.report_composition as legacy
from mdi_api.infrastructure.reports import composition as canonical


def test_report_composition_legacy_symbols_are_true_aliases() -> None:
    for name in (
        "CompositionPreview",
        "REPORT_EXPORT_MAX_BYTES",
        "ReportCompositionDomainError",
        "ReportCompositionService",
        "ReportSourceEligibilityProjector",
        "_ARTIFACT_REPORT_ROLES",
        "_provider_report_projection",
    ):
        assert getattr(legacy, name) is getattr(canonical, name)
