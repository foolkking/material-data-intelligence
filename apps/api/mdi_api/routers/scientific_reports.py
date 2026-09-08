"""Compatibility alias for the canonical scientific_reports transport router."""

from __future__ import annotations

import sys

from mdi_api.transport.routers import scientific_reports as _canonical_router

sys.modules[__name__] = _canonical_router
