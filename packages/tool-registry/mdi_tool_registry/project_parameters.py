"""Bounded contracts for scientific work from explicit parameters or text."""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from mdi_schemas import PlatformReferenceSource
from mdi_schemas.project_planning import PlatformReferenceDescription
from .element_reference import element_reference


PARAMETER_TOOLS = {
    "reference.convert_units": ("换算科学单位", "Convert explicit values between compatible SI units, with separate absolute-temperature and temperature-difference semantics."),
    "generation.function_curve": ("绘制函数曲线", "Plot bounded polynomial, sine, cosine, exponential, natural-logarithm or Gaussian functions from explicit numeric parameters. Never execute expressions or code."),
    "composition.from_formula": ("计算化学式组成", "Calculate stoichiometric counts and atomic fractions from an explicit formula. Parentheses and fractional stoichiometry are supported; mass fractions, molar masses, hydrates and charges are not."),
    "viz.inline_xy": ("绘制输入数据", "Plot 2–128 numeric rows copied verbatim from a user-supplied CSV, TSV or Markdown table with 2–4 columns. Preserve row order; do not fit, invent or silently drop data."),
    "generation.ideal_crystal": ("生成理想晶格", "Generate an ideal SC, BCC, FCC, diamond, rocksalt, CsCl or HCP model from explicit elements and lattice lengths. Includes a ready-to-view scene, requested supercell repetitions and periodic nearest-neighbor distance connections; no separate material inspection is needed. Not a measured sample, equilibrium prediction or chemical-bond assignment."),
}

SI_REFERENCE_SOURCE = PlatformReferenceSource(
    referenceId="si-conversions", version="1.0.0",
    contentHash="119a4093938d18b2a9e026f06b50a442f442d2651dc0466a6090d4df6d33f4db",
)


@lru_cache(maxsize=1)
def _si_bytes() -> bytes:
    path = Path(__file__).resolve().parents[3] / "tool_registry/reference_data/si-conversions.v1.json"
    raw = path.read_bytes()
    if len(raw) > 32768 or hashlib.sha256(raw).hexdigest() != SI_REFERENCE_SOURCE.contentHash:
        raise ValueError("The installed SI definitions do not match the registered version.")
    return raw


def si_reference() -> dict[str, Any]:
    return json.loads(_si_bytes())


def si_reference_description() -> PlatformReferenceDescription:
    data = si_reference()
    return PlatformReferenceDescription.model_validate({
        **SI_REFERENCE_SOURCE.model_dump(mode="json"), "name": data["name"], "sources": data["sources"],
        "properties": {key: {"label": value["label"], "unit": value["baseUnit"],
            "definition": value["definition"], "coverage": ", ".join(value["units"])}
            for key, value in data["definitions"].items()},
    })


def _object(properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {"type": "object", "properties": properties, "required": required, "additionalProperties": False}


def parameter_tool_schema(tool_id: str) -> dict[str, Any]:
    numeric = {"type": "number", "minimum": -1e12, "maximum": 1e12}
    symbols = [item["symbol"] for item in element_reference()["records"]]
    if tool_id == "reference.convert_units":
        units = [unit for item in si_reference()["definitions"].values() for unit in item["units"]]
        return _object({
            "values": {"type": "array", "items": numeric, "minItems": 1, "maxItems": 20},
            "from_unit": {"enum": units}, "to_unit": {"enum": units},
            "quantity": {"enum": ["value", "temperature_difference"], "default": "value"},
        }, ["values", "from_unit", "to_unit"])
    if tool_id == "generation.function_curve":
        common = {"amplitude": {**numeric, "default": 1}, "offset": {**numeric, "default": 0}}
        functions = [
            _object({"kind": {"const": "polynomial"}, "coefficients": {
                "type": "array", "items": numeric, "minItems": 1, "maxItems": 5,
                "description": "Coefficients in ascending powers: [c0,c1,c2] means c0 + c1*x + c2*x^2."}}, ["kind", "coefficients"]),
            _object({"kind": {"enum": ["sine", "cosine", "exponential", "logarithm"]}, **common,
                "rate": {**numeric, "default": 1}, "phase": {**numeric, "default": 0}}, ["kind"]),
            _object({"kind": {"const": "gaussian"}, **common, "center": {**numeric, "default": 0},
                "sigma": {"type": "number", "exclusiveMinimum": 0, "maximum": 1e12, "default": 1}}, ["kind"]),
        ]
        return _object({"x_min": numeric, "x_max": numeric,
            "point_count": {"type": "integer", "minimum": 2, "maximum": 1001, "default": 201},
            "functions": {"type": "array", "items": {"oneOf": functions}, "minItems": 1, "maxItems": 4},
        }, ["x_min", "x_max", "functions"])
    if tool_id == "composition.from_formula":
        return _object({"formula": {"type": "string", "minLength": 1, "maxLength": 128,
            "pattern": r"^[A-Za-z0-9.()]+$"}}, ["formula"])
    if tool_id == "viz.inline_xy":
        return _object({"data_text": {"type": "string", "minLength": 5, "maxLength": 12000,
                "description": "An exact contiguous copy of the numeric table in the current user message, including its header; never rewrite the cells."},
            "x_column": {"type": "integer", "minimum": 0, "maximum": 3, "default": 0},
            "y_columns": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 3},
                "minItems": 1, "maxItems": 3, "uniqueItems": True, "default": [1]},
            "style": {"enum": ["line", "scatter"], "default": "line"}}, ["data_text"])
    if tool_id == "generation.ideal_crystal":
        return _object({"prototype": {"enum": ["sc", "bcc", "fcc", "diamond", "rocksalt", "cscl", "hcp"]},
            "elements": {"type": "array", "items": {"enum": symbols}, "uniqueItems": True, "minItems": 1, "maxItems": 2},
            "lattice_a_angstrom": {"type": "number", "minimum": 0.5, "maximum": 30},
            "lattice_c_angstrom": {"type": "number", "minimum": 0.5, "maximum": 60},
            "repetitions": {"type": "array", "items": {"type": "integer", "minimum": 1, "maximum": 3},
                "minItems": 3, "maxItems": 3, "default": [1, 1, 1]},
        }, ["prototype", "elements", "lattice_a_angstrom"])
    raise KeyError(tool_id)
