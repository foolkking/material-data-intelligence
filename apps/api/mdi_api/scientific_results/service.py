"""Compatibility facade for scientific-result projection services."""
from mdi_api.infrastructure.scientific_results.service import (
    ScientificResultProjectionService,
    ScientificResultSnapshotService,
)
__all__ = ["ScientificResultProjectionService", "ScientificResultSnapshotService"]
