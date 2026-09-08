"""Compatibility facade for scientific-report contracts."""
from mdi_api.domain.scientific_reports import contracts as _contracts
from mdi_api.domain.scientific_reports.contracts import *  # noqa: F403,F401
__all__ = _contracts.__all__
