from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
import re
from typing import Any, Mapping


BAND_RESOURCE_SCHEMA = "phase10n5.electronic_band_resource.v1"
DOS_RESOURCE_SCHEMA = "phase10n5.electronic_dos_resource.v1"
BAND_ARTIFACT_SCHEMA = "phase10n5.electronic_band_structure.v1"
DOS_ARTIFACT_SCHEMA = "phase10n5.electronic_dos.v1"
ELECTRONIC_CAPS = {
    "maxKpoints": 65_536,
    "maxBands": 4_096,
    "maxBandValues": 4_000_000,
    "maxPathSegments": 1_024,
    "maxDosPoints": 262_144,
    "maxProjections": 512,
    "maxDosValues": 4_000_000,
}
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}$")
_HASH = re.compile(r"^[0-9a-f]{64}$")
_SPINS = {"none", "up", "down"}


@dataclass(frozen=True)
class ElectronicValidationResult:
    valid: bool
    errors: tuple[str, ...]


def electronic_resource_hash(value: Mapping[str, Any]) -> str:
    canonical = {key: item for key, item in value.items() if key != "resourceHash"}
    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


def validate_electronic_band_resource(value: Any) -> ElectronicValidationResult:
    errors = _common(value, BAND_RESOURCE_SCHEMA)
    if not isinstance(value, Mapping):
        return ElectronicValidationResult(False, tuple(errors))
    _unknown(value, {
        "schemaVersion", "resourceId", "resourceVersion", "resourceHash",
        "calculationIdentity", "sourceMetadata", "structureIdentity", "energyUnit",
        "energyReference", "fermiEnergyEv", "spinMode", "reciprocalCoordinates",
        "kpoints", "pathSegments", "bands",
    }, errors)
    _enum(value.get("reciprocalCoordinates"), {"fractional_reciprocal"}, "BAND_RECIPROCAL_COORDINATES_UNSUPPORTED", errors)
    kpoints = value.get("kpoints")
    bands = value.get("bands")
    segments = value.get("pathSegments")
    if not isinstance(kpoints, list) or not 1 <= len(kpoints) <= ELECTRONIC_CAPS["maxKpoints"]:
        errors.append("BAND_KPOINT_LIMIT_EXCEEDED")
        kpoints = []
    if not isinstance(bands, list) or not 1 <= len(bands) <= ELECTRONIC_CAPS["maxBands"]:
        errors.append("BAND_LIMIT_EXCEEDED")
        bands = []
    if not isinstance(segments, list) or not 1 <= len(segments) <= ELECTRONIC_CAPS["maxPathSegments"]:
        errors.append("BAND_PATH_INVALID")
        segments = []
    kpoint_ids: set[str] = set()
    segment_ids: set[str] = set()
    for point in kpoints:
        if not _exact_keys(point, {"kpointId", "fractionalCoordinates", "pathDistance", "segmentId", "label"}, {"kpointId", "fractionalCoordinates", "pathDistance", "segmentId"}):
            errors.append("BAND_KPOINT_IDENTITY_MISSING")
            continue
        point_id = point.get("kpointId")
        if not _id(point_id) or point_id in kpoint_ids:
            errors.append("BAND_KPOINT_IDENTITY_MISSING")
        else:
            kpoint_ids.add(point_id)
        if not _vector3(point.get("fractionalCoordinates")) or not _finite(point.get("pathDistance")):
            errors.append("BAND_PATH_INVALID")
        if not _id(point.get("segmentId")):
            errors.append("BAND_PATH_INVALID")
    previous_end = -math.inf
    for segment in segments:
        if not _exact_keys(segment, {"segmentId", "startKpointId", "endKpointId", "breakAfter"}, {"segmentId", "startKpointId", "endKpointId", "breakAfter"}):
            errors.append("BAND_PATH_INVALID")
            continue
        segment_id = segment.get("segmentId")
        if not _id(segment_id) or segment_id in segment_ids or segment.get("startKpointId") not in kpoint_ids or segment.get("endKpointId") not in kpoint_ids or not isinstance(segment.get("breakAfter"), bool):
            errors.append("BAND_PATH_INVALID")
        else:
            segment_ids.add(segment_id)
    if any(point.get("segmentId") not in segment_ids for point in kpoints):
        errors.append("BAND_PATH_INVALID")
    band_ids: set[tuple[str, str]] = set()
    value_count = 0
    for band in bands:
        if not _exact_keys(band, {"bandId", "spinChannel", "energiesEv", "occupations"}, {"bandId", "spinChannel", "energiesEv"}):
            errors.append("BAND_ENERGY_NON_FINITE")
            continue
        identity = (str(band.get("spinChannel")), str(band.get("bandId")))
        energies = band.get("energiesEv")
        occupations = band.get("occupations")
        if not _id(band.get("bandId")) or identity in band_ids or not _spin_allowed(value.get("spinMode"), band.get("spinChannel")):
            errors.append("BAND_IDENTITY_INVALID")
        else:
            band_ids.add(identity)
        if not _finite_array(energies, len(kpoints)):
            errors.append("BAND_ENERGY_NON_FINITE")
        else:
            value_count += len(energies)
        if occupations is not None and (not _finite_array(occupations, len(kpoints)) or any(float(item) < 0 or float(item) > 1 for item in occupations)):
            errors.append("BAND_OCCUPATION_INVALID")
    if value_count > ELECTRONIC_CAPS["maxBandValues"]:
        errors.append("BAND_LIMIT_EXCEEDED")
    return ElectronicValidationResult(not errors, tuple(sorted(set(errors))))


def validate_electronic_dos_resource(value: Any) -> ElectronicValidationResult:
    errors = _common(value, DOS_RESOURCE_SCHEMA)
    if not isinstance(value, Mapping):
        return ElectronicValidationResult(False, tuple(errors))
    _unknown(value, {
        "schemaVersion", "resourceId", "resourceVersion", "resourceHash",
        "calculationIdentity", "sourceMetadata", "structureIdentity", "energyUnit",
        "energyReference", "fermiEnergyEv", "spinMode", "dosUnitSemantic", "energiesEv",
        "totalDos", "projections", "projectionCompleteness",
    }, errors)
    _enum(value.get("dosUnitSemantic"), {"states_per_ev", "states_per_ev_cell", "states_per_ev_formula_unit", "source_relative"}, "DOS_UNIT_UNSUPPORTED", errors)
    _enum(value.get("projectionCompleteness"), {"COMPLETE", "PARTIAL", "UNKNOWN"}, "DOS_PROJECTION_COMPLETENESS_UNKNOWN", errors)
    energies = value.get("energiesEv")
    if not _finite_array(energies) or not 2 <= len(energies) <= ELECTRONIC_CAPS["maxDosPoints"] or any(float(energies[i]) >= float(energies[i + 1]) for i in range(len(energies) - 1)):
        errors.append("DOS_ENERGY_GRID_INVALID")
        energies = []
    totals = value.get("totalDos")
    if not isinstance(totals, list) or not totals:
        errors.append("DOS_TOTAL_MISSING")
        totals = []
    projections = value.get("projections", [])
    if not isinstance(projections, list) or len(projections) > ELECTRONIC_CAPS["maxProjections"]:
        errors.append("DOS_LIMIT_EXCEEDED")
        projections = []
    channel_ids: set[tuple[str, str]] = set()
    numeric_count = 0
    for channel in [*totals, *projections]:
        is_projection = channel in projections
        allowed = {"channelId", "spinChannel", "values"} | ({"projectionKind", "label"} if is_projection else set())
        required = allowed
        if not _exact_keys(channel, allowed, required):
            errors.append("DOS_PROJECTION_UNSUPPORTED" if is_projection else "DOS_TOTAL_MISSING")
            continue
        identity = (str(channel.get("spinChannel")), str(channel.get("channelId")))
        if not _id(channel.get("channelId")) or identity in channel_ids or not _spin_allowed(value.get("spinMode"), channel.get("spinChannel")):
            errors.append("DOS_CHANNEL_IDENTITY_INVALID")
        else:
            channel_ids.add(identity)
        values = channel.get("values")
        if not _finite_array(values, len(energies)):
            errors.append("DOS_VALUE_NON_FINITE")
        else:
            numeric_count += len(values)
        if is_projection and (channel.get("projectionKind") not in {"element", "orbital"} or not _id(channel.get("label"))):
            errors.append("DOS_PROJECTION_UNSUPPORTED")
    if numeric_count > ELECTRONIC_CAPS["maxDosValues"]:
        errors.append("DOS_LIMIT_EXCEEDED")
    return ElectronicValidationResult(not errors, tuple(sorted(set(errors))))


def electronic_band_dos_compatibility(band: Mapping[str, Any], dos: Mapping[str, Any], *, fermi_tolerance_ev: float = 1e-8) -> ElectronicValidationResult:
    errors: list[str] = []
    for field in ("calculationIdentity", "energyUnit", "energyReference", "spinMode"):
        if band.get(field) != dos.get(field):
            errors.append("BAND_DOS_SOURCE_MISMATCH" if field == "calculationIdentity" else ("BAND_DOS_SPIN_MISMATCH" if field == "spinMode" else "BAND_DOS_ENERGY_REFERENCE_MISMATCH"))
    if band.get("structureIdentity") != dos.get("structureIdentity"):
        errors.append("BAND_DOS_SOURCE_MISMATCH")
    left, right = band.get("fermiEnergyEv"), dos.get("fermiEnergyEv")
    if (left is None) != (right is None) or (left is not None and abs(float(left) - float(right)) > fermi_tolerance_ev):
        errors.append("BAND_DOS_ENERGY_REFERENCE_MISMATCH")
    return ElectronicValidationResult(not errors, tuple(sorted(set(errors))))


def _common(value: Any, schema: str) -> list[str]:
    if not isinstance(value, Mapping):
        return ["ELECTRONIC_RESOURCE_UNSUPPORTED"]
    errors: list[str] = []
    if value.get("schemaVersion") != schema:
        errors.append("ELECTRONIC_RESOURCE_UNSUPPORTED")
    for field in ("resourceId", "resourceVersion", "calculationIdentity"):
        if not _id(value.get(field)):
            errors.append("ELECTRONIC_IDENTITY_INVALID")
    if not isinstance(value.get("resourceHash"), str) or not _HASH.fullmatch(value["resourceHash"]):
        errors.append("CHECKSUM_MISMATCH")
    elif value["resourceHash"] != electronic_resource_hash(value):
        errors.append("CHECKSUM_MISMATCH")
    _enum(value.get("energyUnit"), {"eV"}, "ELECTRONIC_ENERGY_UNIT_UNSUPPORTED", errors)
    _enum(value.get("energyReference"), {"source_absolute", "fermi_referenced"}, "ELECTRONIC_ENERGY_REFERENCE_UNSUPPORTED", errors)
    _enum(value.get("spinMode"), {"non_spin_polarized", "spin_polarized"}, "ELECTRONIC_SPIN_MODE_UNSUPPORTED", errors)
    if value.get("fermiEnergyEv") is not None and not _finite(value.get("fermiEnergyEv")):
        errors.append("ELECTRONIC_FERMI_INVALID")
    if value.get("energyReference") == "fermi_referenced" and value.get("fermiEnergyEv") is None:
        errors.append("ELECTRONIC_FERMI_MISSING")
    structure = value.get("structureIdentity")
    if structure is not None and (not _exact_keys(structure, {"structureId", "structureHash"}, {"structureId", "structureHash"}) or not _id(structure.get("structureId")) or not isinstance(structure.get("structureHash"), str) or not _HASH.fullmatch(structure["structureHash"])):
        errors.append("ELECTRONIC_STRUCTURE_IDENTITY_INVALID")
    metadata = value.get("sourceMetadata")
    if metadata is not None and (not _exact_keys(metadata, {"code", "codeVersion", "method"}, set()) or any(not isinstance(item, str) or len(item) > 128 for item in metadata.values())):
        errors.append("ELECTRONIC_RESOURCE_UNSUPPORTED")
    return errors


def _unknown(value: Mapping[str, Any], allowed: set[str], errors: list[str]) -> None:
    if set(value) - allowed:
        errors.append("ELECTRONIC_RESOURCE_UNSUPPORTED")


def _exact_keys(value: Any, allowed: set[str], required: set[str]) -> bool:
    return isinstance(value, Mapping) and not (set(value) - allowed) and required.issubset(value)


def _enum(value: Any, allowed: set[str], code: str, errors: list[str]) -> None:
    if value not in allowed:
        errors.append(code)


def _id(value: Any) -> bool:
    return isinstance(value, str) and bool(_ID.fullmatch(value))


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _finite_array(value: Any, length: int | None = None) -> bool:
    return isinstance(value, list) and (length is None or len(value) == length) and all(_finite(item) for item in value)


def _vector3(value: Any) -> bool:
    return _finite_array(value, 3)


def _spin_allowed(mode: Any, channel: Any) -> bool:
    return channel in _SPINS and ((mode == "non_spin_polarized" and channel == "none") or (mode == "spin_polarized" and channel in {"up", "down"}))
