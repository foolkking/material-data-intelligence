"""Stable application-facing entrypoints for Scientific Result projection."""

from mdi_api.application.scientific_results.entrypoints import (
    ScientificResultProjectorPort,
    project_queued_result,
)

__all__ = ["ScientificResultProjectorPort", "project_queued_result"]
