"""Compatibility alias for the canonical secured_runtime transport router."""

from __future__ import annotations

import sys

from mdi_api.transport.routers import secured_runtime as _canonical_router

sys.modules[__name__] = _canonical_router
