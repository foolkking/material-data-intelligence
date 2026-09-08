"""Compatibility alias for the canonical report_compositions transport router."""

from __future__ import annotations

import sys

from mdi_api.transport.routers import report_compositions as _canonical_router

sys.modules[__name__] = _canonical_router
