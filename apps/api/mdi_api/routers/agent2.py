"""Compatibility alias for the canonical agent2 transport router."""

from __future__ import annotations

import sys

from mdi_api.transport.routers import agent2 as _canonical_router

sys.modules[__name__] = _canonical_router
