"""Bounded, type-preserving JSON for inspectable validated tool parameters."""
from __future__ import annotations

import json
import math
from typing import Annotated, Any

from pydantic import BeforeValidator, JsonValue, WithJsonSchema
from typing_extensions import TypeAliasType


MAX_PARAMETER_DEPTH = 4
MAX_PARAMETER_ITEMS = 128
MAX_PARAMETER_PROPERTIES = 64
MAX_PARAMETER_TEXT = 16384
MAX_PARAMETER_NODES = 512
MAX_PARAMETER_BYTES = 65536


def _validate_parameter_value(value: Any) -> Any:
    remaining = MAX_PARAMETER_NODES

    def visit(item: Any, depth: int) -> None:
        nonlocal remaining
        remaining -= 1
        if remaining < 0:
            raise ValueError("Parameter provenance exceeds its value budget.")
        if item is None or type(item) is bool:
            return
        if type(item) in (int, float):
            if abs(item) > 1e100 or (type(item) is float and not math.isfinite(item)):
                raise ValueError("Parameter provenance requires bounded finite numbers.")
            return
        if type(item) is str:
            if len(item) > MAX_PARAMETER_TEXT:
                raise ValueError("Parameter provenance text exceeds its limit.")
            return
        if depth >= MAX_PARAMETER_DEPTH:
            raise ValueError("Parameter provenance is nested too deeply.")
        if type(item) is list:
            if len(item) > MAX_PARAMETER_ITEMS:
                raise ValueError("Parameter provenance array exceeds its limit.")
            for child in item:
                visit(child, depth + 1)
        elif type(item) is dict:
            if len(item) > MAX_PARAMETER_PROPERTIES:
                raise ValueError("Parameter provenance object exceeds its limit.")
            for key, child in item.items():
                if type(key) is not str or len(key) > 128:
                    raise ValueError("Parameter provenance requires bounded string keys.")
                visit(child, depth + 1)
        else:
            raise ValueError("Parameter provenance must contain JSON values only.")

    visit(value, 0)
    if len(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")) > MAX_PARAMETER_BYTES:
        raise ValueError("Parameter provenance exceeds its encoded size limit.")
    return value


def _parameter_schema(depth: int) -> dict[str, Any]:
    variants: list[dict[str, Any]] = [
        {"type": "null"}, {"type": "boolean"},
        {"type": "number", "minimum": -1e100, "maximum": 1e100},
        {"type": "string", "maxLength": MAX_PARAMETER_TEXT},
    ]
    if depth:
        child = _parameter_schema(depth - 1)
        variants.extend([
            {"type": "array", "maxItems": MAX_PARAMETER_ITEMS, "items": child},
            {"type": "object", "maxProperties": MAX_PARAMETER_PROPERTIES,
             "propertyNames": {"maxLength": 128}, "additionalProperties": child},
        ])
    return {"anyOf": variants}


ParameterValue = TypeAliasType("ParameterValue", Annotated[
    JsonValue, BeforeValidator(_validate_parameter_value),
    WithJsonSchema({**_parameter_schema(MAX_PARAMETER_DEPTH),
        "description": "Validated tool parameter JSON: at most 4 container levels, 512 values and 65536 UTF-8 bytes."}),
])
