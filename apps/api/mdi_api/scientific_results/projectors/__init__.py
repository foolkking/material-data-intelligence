"""Compatibility facade for scientific-result projector package."""
from mdi_api.application.scientific_results.projectors.registry import (
    InMemoryScientificResultProjectorRegistry,
    ScientificResultProjectorRegistry,
)
__all__ = ["InMemoryScientificResultProjectorRegistry", "ScientificResultProjectorRegistry"]
