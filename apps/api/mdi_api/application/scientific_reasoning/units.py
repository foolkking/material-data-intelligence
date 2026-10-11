"""Shared lexical unit grounding for saved scientific facts, without conversion."""

from __future__ import annotations

import re
from typing import Any


# Match compounds before their denominators. Temperature K is case-sensitive:
# the lowercase k in k-point labels is not a Kelvin claim.
_POTENTIAL_UNIT = r"(?:electronvolt|eV|hartree/elementary_charge|hartree|Ha/e|Ha|volt|V)"
UNIT_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(?:(?i:"
    + _POTENTIAL_UNIT + r"\s*(?:[·⋅*×]\s*|\s+|(?=Å|angstrom|bohr|nm))(?:Å|angstrom|bohr|nm)(?:\^\{?[23]\}?|²|³)|"
    r"(?:electrons?|电子|elementary_charge|bohr_magneton)\s*/\s*(?:Å|angstrom|bohr|nm)(?:\^\{?3\}?|³)|"
    r"(?:Å|angstrom)(?:\^\{?2\}?|²)/(?:ps|picosecond)|"
    r"(?:Å|angstrom)(?:\^\{?2\}?|²)|"
    r"(?:Å|angstrom)(?:\^\{?-?3\}?|⁻³|³|-3)?|"
    r"femtosecond|picosecond|nm|pm|meV|fs|ps|%|THz|terahertz|cm-?1|1/s|m\^?2/s|"
    + _POTENTIAL_UNIT +
    r")|K)(?![A-Za-z0-9])"
)


def canonical_unit(value: object) -> str:
    normalized = (
        str(value).strip().lower()
        .replace("angstrom", "å")
        .replace("⁻³", "^-3")
        .replace("³", "^3")
        .replace("²", "^2")
        .replace("{", "")
        .replace("}", "")
    )
    normalized = re.sub(r"\s+", "", normalized)
    normalized = re.sub(r"^(?:electrons|电子)/", "electron/", normalized)
    normalized = re.sub(r"^(å)-3$", r"\1^-3", normalized)
    normalized = normalized.replace("cm-1", "cm1")
    potential = re.fullmatch(r"(electronvolt|ev|hartree/elementary_charge|hartree|ha/e|ha|volt|v)(?:[·⋅*×]?((?:å|bohr|nm)\^[23]))?", normalized)
    if potential:
        base = {"electronvolt": "ev", "hartree": "ha", "hartree/elementary_charge": "ha/e", "volt": "v"}.get(potential[1], potential[1])
        return base + (f"*{potential[2]}" if potential[2] else "")
    # Spelling aliases only: preserve the physical quantity and length scale.
    return {
        "μm": "um", "µm": "um", "μs": "us", "µs": "us", "°c": "degc",
        "terahertz": "thz",
        "electronvolt": "ev",
        "ps": "picosecond",
        "fs": "femtosecond",
        "å^2/ps": "å^2/picosecond",
    }.get(normalized, normalized)


def supported_fact_units(referenced: list[dict[str, Any]]) -> set[str]:
    units = {canonical_unit(fact["unit"]) for fact in referenced if fact.get("unit")}
    # Only explicit unit-definition predicates confer unit support. A field
    # name or arbitrary categorical value containing a unit does not.
    units.update(
        canonical_unit(fact["value"])
        for fact in referenced
        if fact.get("predicate") in {
            "volumetric.length_unit", "volumetric.canonical_unit", "volumetric.selected_canonical_unit", "volumetric.source_unit",
            "phonon.frequency_unit",
        }
        and isinstance(fact.get("value"), str)
    )
    return units


def exclude_saved_column_labels(text: str, referenced: list[dict[str, Any]]) -> str:
    """A cited column identifier is not a measurement or a unit declaration."""
    predicates = {"correlation.left_column", "correlation.right_column", "table.numeric.column",
                  "table.categorical.column", "table.category.column", "histogram.column",
                  "scatter.x_column", "scatter.y_column", "inline.column"}
    names = {fact["value"] for fact in referenced if fact.get("predicate") in predicates
             and isinstance(fact.get("value"), str) and fact["value"]}
    for name in sorted(names, key=len, reverse=True):
        for left, right in (("`", "`"), ('"', '"'), ("“", "”"), ("「", "」")):
            text = text.replace(left + name + right, "列名")
        # Unquoted identifier-like names such as energy/eV are unambiguous.
        # Bare units, numbers and phrases still require scientific support.
        if re.fullmatch(r"[A-Za-z_][^\s]*", name) and not UNIT_PATTERN.fullmatch(name):
            text = re.sub(r"(?<![\w])" + re.escape(name) + r"(?![\w])", "列名", text)
    return text


def reference_version_claims(text: str, referenced: list[dict[str, Any]]) -> tuple[str, list[str]]:
    """Match an explicit reference-version label against its complete citation.

    Version components cannot be borrowed as scientific measurements. The
    caller enables this only for a result containing reference-version facts.
    """
    versions = {fact["value"] for fact in referenced if fact.get("predicate") == "reference.version"
                and isinstance(fact.get("value"), str)}
    unsupported: list[str] = []

    def replace(match: re.Match[str]) -> str:
        version = match.group("version")
        if version not in versions:
            unsupported.append(version)
        return "参考版本"

    rendered = re.sub(
        r"(?:版本(?:号)?|version)(?:\s*(?:为|是|is))?\s*[:：]?\s*v?"
        r"(?P<version>\d+(?:\.\d+){1,4}(?:-[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*)?)"
        r"(?![A-Za-z0-9_-]|\.\d)",
        replace, text, flags=re.IGNORECASE,
    )
    return rendered, unsupported


def parameter_claimed_units(text: str, referenced: list[dict[str, Any]]) -> set[str]:
    """Recognize additional SI units in explicit parameter measurements.

    A bare chemical symbol such as Pa or a function variable such as s is
    not a unit claim. These additional tokens need a number or unit label.
    Existing sample unit detection retains its established behavior.
    """
    if not any(str(fact.get("predicate", "")).startswith(("calculation.", "inline.", "model.", "composition.")) for fact in referenced):
        return set()
    pattern = r"(?<![A-Za-z0-9_])(?:angstrom|degC|°C|μm|µm|μs|µs|cm|mm|um|nm|pm|ms|us|ns|ps|fs|kJ|meV|eV|kPa|MPa|GPa|Pa|kHz|MHz|GHz|THz|Hz|m|s|J|K)(?![A-Za-z0-9_])"
    return {canonical_unit(match[0]) for match in re.finditer(pattern, text)
            if re.search(r"(?:\d\s*|(?:单位|units?|in)\s*(?:为|是|is|[:：])?\s*[（(]?)$", text[:match.start()], flags=re.IGNORECASE)}


def exclude_saved_parameter_expressions(text: str, referenced: list[dict[str, Any]]) -> str:
    """A complete cited formula conveys its notation, not reusable numbers."""
    for fact in referenced:
        value = fact.get("value")
        if fact.get("predicate") in {"calculation.function", "composition.formula", "model.formula"} and isinstance(value, str) and value:
            text = re.sub(r"(?<![A-Za-z0-9_.])" + re.escape(value) + r"(?![A-Za-z0-9_.])", "已引用公式", text)
    return text
