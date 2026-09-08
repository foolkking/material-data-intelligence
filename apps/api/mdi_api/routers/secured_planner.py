"""Compatibility alias for the canonical secured_planner transport router."""

from __future__ import annotations

import sys

from mdi_api.transport.routers import secured_planner as _canonical_router

sys.modules[__name__] = _canonical_router
