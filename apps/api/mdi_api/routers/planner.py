"""Compatibility alias for the canonical planner transport router."""

from __future__ import annotations

import sys

from mdi_api.transport.routers import planner as _canonical_router

sys.modules[__name__] = _canonical_router
