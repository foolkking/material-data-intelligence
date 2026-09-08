"""Compatibility alias for the canonical planner_providers transport router."""

from __future__ import annotations

import sys

from mdi_api.transport.routers import planner_providers as _canonical_router

sys.modules[__name__] = _canonical_router
