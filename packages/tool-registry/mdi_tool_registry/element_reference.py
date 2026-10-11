"""Versioned inert reference data and bounded public query parameters."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from mdi_schemas import PlatformReferenceSource
from mdi_schemas.project_planning import PlatformReferenceDescription


ELEMENT_REFERENCE_SOURCE = PlatformReferenceSource(
    referenceId="elements", version="1.0.0",
    contentHash="fde671808a294589ff8d420ed79262fbc60b4bd1fe206a7f4540c2c66e67d245",
)


@lru_cache(maxsize=1)
def _reference_bytes() -> bytes:
    path = Path(__file__).resolve().parents[3] / "tool_registry" / "reference_data" / "elements.v1.json"
    raw = path.read_bytes()
    if len(raw) > 65_536 or hashlib.sha256(raw).hexdigest() != ELEMENT_REFERENCE_SOURCE.contentHash:
        raise ValueError("The installed element reference does not match its registered version.")
    return raw


def element_reference() -> dict[str, Any]:
    # Each caller receives independent data; no adapter can mutate the cache.
    return json.loads(_reference_bytes())


def element_reference_description(properties: list[str] | None = None) -> PlatformReferenceDescription:
    reference = element_reference()
    selected = sorted(set(properties)) if properties is not None else list(reference["properties"])
    return PlatformReferenceDescription.model_validate({
        **ELEMENT_REFERENCE_SOURCE.model_dump(mode="json"), "name": "元素参考资料",
        "sources": reference["sources"],
        "properties": {key: reference["properties"][key] for key in selected},
    })


def element_reference_params_schema(*, comparison: bool = False) -> dict[str, Any]:
    symbols = [item["symbol"] for item in element_reference()["records"]]
    properties: dict[str, Any] = {
        "property": {"enum": ["atomic_number", "covalent_radius"], **({} if comparison else {"default": "atomic_number"})},
        "elements": {"type": "array", "items": {"enum": symbols}, "uniqueItems": True,
                     "minItems": 2 if comparison else 1, "maxItems": 20 if comparison else 118},
    }
    if not comparison:
        properties["highlight_elements"] = {"type": "array", "items": {"enum": symbols}, "uniqueItems": True, "minItems": 1, "maxItems": 118}
    return {"type": "object", "properties": properties, "required": ["property", "elements"] if comparison else [], "additionalProperties": False}
