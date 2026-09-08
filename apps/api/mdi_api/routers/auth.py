"""Compatibility alias for the canonical auth transport router."""

from __future__ import annotations

import sys

from mdi_api.transport.routers import auth as _canonical_router

sys.modules[__name__] = _canonical_router
