"""Compatibility facade for scientific-result contracts."""
from mdi_api.domain.scientific_results import contracts as _contracts
from mdi_api.domain.scientific_results.contracts import *  # noqa: F403,F401

__all__ = _contracts.__all__
