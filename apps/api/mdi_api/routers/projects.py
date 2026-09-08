"""Compatibility alias for the canonical projects transport router."""

from __future__ import annotations

import sys

from mdi_api.transport.routers import projects as _canonical_router

sys.modules[__name__] = _canonical_router
