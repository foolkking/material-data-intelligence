"""Compatibility alias for the canonical project_history transport router."""

from __future__ import annotations

import sys

from mdi_api.transport.routers import project_history as _canonical_router

sys.modules[__name__] = _canonical_router
