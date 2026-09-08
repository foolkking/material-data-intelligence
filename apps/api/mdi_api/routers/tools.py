"""Compatibility alias for the canonical tools transport router."""

from __future__ import annotations

import sys

from mdi_api.transport.routers import tools as _canonical_router

sys.modules[__name__] = _canonical_router
