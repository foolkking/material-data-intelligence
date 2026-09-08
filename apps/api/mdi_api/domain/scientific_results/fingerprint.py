"""Stable identity for a scientific result projection."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), default=str)


def scientific_result_source_fingerprint(*, facts: dict[str, Any]) -> str:
    """Hash only immutable execution/projection identities, never timestamps or URLs."""
    return hashlib.sha256(canonical_json(facts).encode("utf-8")).hexdigest()


class ScientificResultSourceFingerprint:
    @staticmethod
    def compute(**facts: Any) -> str:
        return scientific_result_source_fingerprint(facts=facts)
