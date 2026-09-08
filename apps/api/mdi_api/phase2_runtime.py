"""Compatibility alias for the canonical Phase2 runtime module."""

from __future__ import annotations

import sys
from types import ModuleType

from mdi_api.application.phase2 import models as _phase2_models
from mdi_api.infrastructure.phase2 import runtime as _canonical_runtime


class _Phase2CompatibilityModule(ModuleType):
    """Keep historical monkeypatches of upload limits behavior-compatible."""

    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)
        if name in {"MAX_FILES_PER_UPLOAD", "MAX_FILE_BYTES", "MAX_TOTAL_UPLOAD_BYTES"}:
            setattr(_phase2_models, name, value)


_canonical_runtime.__class__ = _Phase2CompatibilityModule
sys.modules[__name__] = _canonical_runtime
