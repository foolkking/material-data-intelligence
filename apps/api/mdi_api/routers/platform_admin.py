"""Compatibility alias for the canonical platform_admin transport router."""

from __future__ import annotations

import sys

from mdi_api.transport.routers import platform_admin as _canonical_router

sys.modules[__name__] = _canonical_router
