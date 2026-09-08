"""Compatibility facade for interpretation contracts."""
from mdi_api.domain.interpretation import contracts as _contracts
from mdi_api.domain.interpretation.contracts import *  # noqa: F403,F401
__all__ = _contracts.__all__
