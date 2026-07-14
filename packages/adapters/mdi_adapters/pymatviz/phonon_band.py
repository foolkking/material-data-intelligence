from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import re
from typing import Any

import yaml

from mdi_artifact_core import (
    ArtifactPayload,
    DEFAULT_PHONON_CAPS,
    PHONON_BAND_SCHEMA_VERSION,
    PHONON_MANIFEST_SCHEMA_VERSION,
    PHONON_SUMMARY_SCHEMA_VERSION,
    convert_frequency,
    normalize_high_symmetry_label,
    phonon_content_hash,
    phonon_summary,
    reciprocal_path_step,
    stable_phonon_json,
    validate_phonon_band,
    validate_phonon_manifest,
    validate_phonon_summary,
)
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


_MAX_SOURCE_BYTES = 16_000_000
_MAX_SOURCE_NODES = 1_000_000
_MAX_TABLE_ROWS = 50_000
_FORBIDDEN_YAML_TOKEN = re.compile(r"(^|\s)[&*!][^\s,\[\]{}]+", re.MULTILINE)
_SHA256 = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class PhononBandResult:
    band: dict[str, Any]
    summary: dict[str, Any]
    report: dict[str, Any]
    manifest: dict[str, Any]
    plot: dict[str, Any]
    table: dict[str, Any]
    recipe: dict[str, Any]


class PhononBandAdapter(BaseToolAdapter):
    tool_id = "phonon.band"
    adapter_version = "0.1.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> Any:
        del context, input_refs, params
        if len(self._resolved_inputs) != 1:
            raise _error("PHONON_BAND_INPUT_COUNT_INVALID", "phonon.band requires exactly one approved band input.")
        return self._resolved_inputs[0]

    def run(self, prepared: Any, params: dict[str, Any]) -> PhononBandResult:
        normalized = _normalize_params(params)
        band, source_format, source_hash = _normalize_source(prepared, normalized)
        validation = validate_phonon_band(band)
        if not validation.valid:
            raise _error(
                "PHONON_BAND_VALIDATION_FAILED",
                "The normalized phonon band does not satisfy phase10h.phonon_band.v1.",
                {"errors": list(validation.errors)},
            )

        summary = phonon_summary(band)
        summary_validation = validate_phonon_summary(summary)
        if not summary_validation.valid:
            raise _error("PHONON_BAND_SUMMARY_INVALID", "The generated phonon summary is invalid.")

        report = _parse_report(band, validation.as_dict(), source_format, source_hash)
        plot = _plot_payload(band, summary)
        table = _table_payload(band, normalized["max_table_rows"])
        manifest = _manifest_payload(band, summary)
        manifest_validation = validate_phonon_manifest(manifest)
        if not manifest_validation.valid:
            raise _error("PHONON_BAND_MANIFEST_INVALID", "The generated phonon manifest is invalid.")
        recipe = _recipe_payload(self, normalized, band, source_format)
        return PhononBandResult(band, summary, report, manifest, plot, table, recipe)

    def export(self, result: PhononBandResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        defaults = {
            ArtifactType.phonon_band_json,
            ArtifactType.phonon_summary_json,
            ArtifactType.phonon_report_json,
            ArtifactType.phonon_manifest_json,
            ArtifactType.plotly_json,
            ArtifactType.table_json,
            ArtifactType.recipe_json,
        }
        requested = set(artifact_types) or defaults
        payload_by_type = {
            ArtifactType.phonon_band_json: ("phonon_band.json", stable_phonon_json(result.band), "application/json"),
            ArtifactType.phonon_summary_json: ("phonon_summary.json", stable_phonon_json(result.summary), "application/json"),
            ArtifactType.phonon_report_json: ("phonon_band_parse_report.json", stable_phonon_json(result.report), "application/json"),
            ArtifactType.phonon_manifest_json: ("phonon_manifest.json", stable_phonon_json(result.manifest), "application/json"),
            ArtifactType.plotly_json: ("phonon_band_plot.json", stable_phonon_json(result.plot), "application/json"),
            ArtifactType.table_json: ("phonon_band_table.json", stable_phonon_json(result.table), "application/json"),
            ArtifactType.recipe_json: ("recipe.json", stable_phonon_json(result.recipe), "application/json"),
        }
        payloads = [
            ArtifactPayload(artifact_type=kind, file_name=payload_by_type[kind][0], content=payload_by_type[kind][1], media_type=payload_by_type[kind][2])
            for kind in payload_by_type
            if kind in requested
        ]
        return self.export_payloads(
            payloads,
            provenance={
                "adapter": self.tool_id,
                "schemaVersion": PHONON_BAND_SCHEMA_VERSION,
                "structureIdentity": result.band["structure_identity"],
                "staticBandOnly": True,
                "dosIncluded": False,
                "eigenvectorsIncluded": False,
                "animationIncluded": False,
                "externalResources": False,
            },
        )


def _normalize_params(params: dict[str, Any]) -> dict[str, Any]:
    allowed = {"source_format", "source_frequency_unit", "max_table_rows", "plot_kind"}
    unknown = sorted(set(params) - allowed)
    if unknown:
        raise _error("PHONON_BAND_PARAM_INVALID", "Unknown phonon.band parameters are not accepted.", {"unknownParams": unknown})
    source_format = params.get("source_format", "auto")
    if source_format not in {"auto", PHONON_BAND_SCHEMA_VERSION, "phonopy_band_yaml"}:
        raise _error("PHONON_BAND_SOURCE_UNSUPPORTED", "The requested phonon band source format is not approved.")
    frequency_unit = params.get("source_frequency_unit", "terahertz")
    if frequency_unit not in {"terahertz", "inverse_centimeter", "millielectronvolt"}:
        raise _error("PHONON_BAND_UNIT_UNSUPPORTED", "The source frequency unit is not approved.")
    max_rows = params.get("max_table_rows", 20_000)
    if not isinstance(max_rows, int) or isinstance(max_rows, bool) or not 1 <= max_rows <= _MAX_TABLE_ROWS:
        raise _error("PHONON_BAND_PARAM_INVALID", "max_table_rows must be an integer between 1 and 50000.")
    if params.get("plot_kind", "line") != "line":
        raise _error("PHONON_BAND_PARAM_INVALID", "phonon.band only supports plot_kind=line.")
    return {
        "source_format": source_format,
        "source_frequency_unit": frequency_unit,
        "max_table_rows": max_rows,
        "plot_kind": "line",
    }


def _normalize_source(value: Any, params: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    source_format = params["source_format"]
    if isinstance(value, dict) and value.get("schema_version") == PHONON_BAND_SCHEMA_VERSION:
        if source_format not in {"auto", PHONON_BAND_SCHEMA_VERSION}:
            raise _error("PHONON_BAND_SOURCE_MISMATCH", "Input content does not match source_format.")
        result = validate_phonon_band(value)
        if not result.valid:
            raise _error("PHONON_BAND_VALIDATION_FAILED", "Canonical phonon band input is invalid.", {"errors": list(result.errors)})
        raw = stable_phonon_json(value)
        return value, PHONON_BAND_SCHEMA_VERSION, hashlib.sha256(raw.encode("utf-8")).hexdigest()

    if not isinstance(value, dict) or set(value) != {"source_format", "content", "structure_identity"}:
        raise _error("PHONON_BAND_SOURCE_UNSUPPORTED", "Expected canonical JSON or an approved phonopy_band_yaml wrapper.")
    if value.get("source_format") != "phonopy_band_yaml" or source_format not in {"auto", "phonopy_band_yaml"}:
        raise _error("PHONON_BAND_SOURCE_MISMATCH", "Input content does not match source_format.")
    structure_identity = value.get("structure_identity")
    if not isinstance(structure_identity, str) or _SHA256.fullmatch(structure_identity) is None:
        raise _error("PHONON_STRUCTURE_IDENTITY_REQUIRED", "phonopy band input requires a validated structure identity.")
    content = value.get("content")
    if not isinstance(content, str):
        raise _error("PHONON_BAND_SOURCE_UNSUPPORTED", "phonopy band content must be text.")
    source_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return _phonopy_yaml_to_band(content, structure_identity, params["source_frequency_unit"], source_hash), "phonopy_band_yaml", source_hash


def _safe_yaml(content: str) -> dict[str, Any]:
    raw = content.encode("utf-8")
    if not raw or len(raw) > _MAX_SOURCE_BYTES:
        raise _error("PHONON_BAND_SOURCE_LIMIT_EXCEEDED", "phonopy band YAML exceeds the approved source size.")
    if _FORBIDDEN_YAML_TOKEN.search(content):
        raise _error("PHONON_BAND_YAML_UNSAFE", "YAML aliases, anchors, and explicit tags are not accepted.")
    try:
        value = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise _error("PHONON_BAND_PARSE_FAILED", "phonopy band YAML could not be parsed safely.") from exc
    if not isinstance(value, dict):
        raise _error("PHONON_BAND_PARSE_FAILED", "phonopy band YAML root must be a mapping.")
    queue: list[tuple[Any, int]] = [(value, 0)]
    visited = 0
    while queue:
        item, depth = queue.pop()
        visited += 1
        if visited > _MAX_SOURCE_NODES or depth > DEFAULT_PHONON_CAPS["max_nesting_depth"]:
            raise _error("PHONON_BAND_SOURCE_LIMIT_EXCEEDED", "phonopy band YAML exceeds bounded parser limits.")
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                raise _error("PHONON_BAND_PARSE_FAILED", "phonopy band YAML keys must be strings.")
            queue.extend((child, depth + 1) for child in item.values())
        elif isinstance(item, list):
            queue.extend((child, depth + 1) for child in item)
        elif not isinstance(item, (str, int, float, bool, type(None))):
            raise _error("PHONON_BAND_YAML_UNSAFE", "phonopy band YAML contains an unsupported value type.")
    return value


def _phonopy_yaml_to_band(content: str, structure_identity: str, frequency_unit: str, source_hash: str) -> dict[str, Any]:
    data = _safe_yaml(content)
    allowed_root = {
        "natom", "lattice", "points", "reciprocal_lattice", "nqpoint", "npath", "segment_nqpoint",
        "labels", "phonon", "calculator", "frequency_unit", "supercell_matrix", "primitive_matrix",
    }
    unknown = sorted(set(data) - allowed_root)
    if unknown:
        raise _error("PHONON_BAND_SOURCE_FIELD_UNSUPPORTED", "phonopy band YAML contains unsupported root fields.", {"fields": unknown[:20]})
    lattice = _matrix(data.get("lattice"), "lattice", integers=False)
    points = data.get("points")
    atom_count = data.get("natom")
    if not isinstance(atom_count, int) or isinstance(atom_count, bool) or not 1 <= atom_count <= DEFAULT_PHONON_CAPS["max_atoms"]:
        raise _error("PHONON_ATOM_COUNT_INVALID", "phonopy natom is invalid.")
    if not isinstance(points, list) or len(points) != atom_count:
        raise _error("PHONON_SPECIES_ORDER_INVALID", "phonopy points must preserve one symbol per atom.")
    species: list[str] = []
    for point in points:
        if not isinstance(point, dict) or set(point) - {"symbol", "coordinates", "mass"} or not isinstance(point.get("symbol"), str):
            raise _error("PHONON_SPECIES_ORDER_INVALID", "phonopy point identity is invalid.")
        symbol = point["symbol"]
        if re.fullmatch(r"[A-Z][a-z]?", symbol) is None:
            raise _error("PHONON_SPECIES_ORDER_INVALID", "phonopy species symbols are invalid.")
        species.append(symbol)

    phonon = data.get("phonon")
    segment_counts = data.get("segment_nqpoint")
    if not isinstance(phonon, list) or not phonon or len(phonon) > DEFAULT_PHONON_CAPS["max_qpoints"]:
        raise _error("PHONON_QPOINT_SHAPE_INVALID", "phonopy phonon q-points are invalid or exceed the cap.")
    if data.get("nqpoint") != len(phonon) or not isinstance(segment_counts, list) or not segment_counts:
        raise _error("PHONON_PATH_SEGMENT_INVALID", "phonopy q-point and segment counts are inconsistent.")
    if len(segment_counts) > DEFAULT_PHONON_CAPS["max_segments"] or any(not isinstance(item, int) or isinstance(item, bool) or item < 1 for item in segment_counts) or sum(segment_counts) != len(phonon):
        raise _error("PHONON_PATH_SEGMENT_INVALID", "phonopy segment_nqpoint is invalid.")
    labels = data.get("labels")
    if labels is None:
        labels = [[None, None] for _ in segment_counts]
    if not isinstance(labels, list) or len(labels) != len(segment_counts):
        raise _error("PHONON_PATH_LABEL_INVALID", "phonopy labels must match segment_nqpoint.")

    qpoints: list[dict[str, Any]] = []
    segments: list[dict[str, Any]] = []
    qpoint_frequencies: list[list[float]] = []
    cursor = 0
    distance = 0.0
    previous_coordinates: list[float] | None = None
    branch_count = atom_count * 3
    for segment_index, count in enumerate(segment_counts):
        label_pair = labels[segment_index]
        if not isinstance(label_pair, list) or len(label_pair) != 2:
            raise _error("PHONON_PATH_LABEL_INVALID", "Each phonopy segment label must contain start and end labels.")
        start_index = cursor
        start_label = _label(label_pair[0])
        end_label = _label(label_pair[1])
        first_coordinates: list[float] | None = None
        for local_index in range(count):
            record = phonon[cursor]
            if not isinstance(record, dict) or set(record) - {"q-position", "distance", "band"}:
                raise _error("PHONON_QPOINT_SHAPE_INVALID", "phonopy q-point fields are invalid.")
            coordinates = _vector(record.get("q-position"), "q-position")
            if local_index == 0:
                first_coordinates = coordinates
                if segment_index > 0:
                    # Contract distances do not advance across a path discontinuity.
                    distance = qpoints[-1]["distance"]
            else:
                distance += reciprocal_path_step(previous_coordinates or coordinates, coordinates, lattice)
            bands = record.get("band")
            if not isinstance(bands, list) or len(bands) != branch_count:
                raise _error("PHONON_BRANCH_COUNT_MISMATCH", "phonopy band count must equal 3N at every q-point.")
            frequencies: list[float] = []
            for band in bands:
                if not isinstance(band, dict) or set(band) - {"frequency", "group_velocity"}:
                    raise _error("PHONON_FREQUENCY_SHAPE_INVALID", "phonopy band entries are invalid.")
                frequency = band.get("frequency")
                if not isinstance(frequency, (int, float)) or isinstance(frequency, bool) or not math.isfinite(float(frequency)):
                    raise _error("PHONON_FREQUENCY_NONFINITE", "phonopy frequencies must be finite.")
                frequencies.append(convert_frequency(float(frequency), frequency_unit, "terahertz"))
            source_label = label_pair[0] if local_index == 0 else label_pair[1] if local_index == count - 1 else None
            qpoints.append(
                {
                    "index": cursor,
                    "coordinates": coordinates,
                    "label": _label(source_label),
                    "source_label": str(source_label) if source_label is not None else None,
                    "segment_index": segment_index,
                    "distance": distance,
                }
            )
            qpoint_frequencies.append(frequencies)
            previous_coordinates = coordinates
            cursor += 1
        prior = qpoints[start_index - 1]["coordinates"] if start_index > 0 else None
        segments.append(
            {
                "segment_index": segment_index,
                "start_qpoint_index": start_index,
                "end_qpoint_index": cursor - 1,
                "start_label": start_label,
                "end_label": end_label,
                "discontinuous_from_previous": bool(segment_index > 0 and prior != first_coordinates),
            }
        )

    branches = [
        {"branch_index": branch_index, "frequencies": [values[branch_index] for values in qpoint_frequencies]}
        for branch_index in range(branch_count)
    ]
    warnings = sorted(
        {
            "PHONON_ACOUSTIC_MODES_NOT_CORRECTED",
            "PHONON_BAND_CONNECTIVITY_SOURCE_ORDER_ONLY",
            "PHONON_DEGENERACY_SOURCE_UNAVAILABLE",
            "PHONON_NAC_STATUS_UNKNOWN",
        }
    )
    return {
        "schema_version": PHONON_BAND_SCHEMA_VERSION,
        "structure_identity": structure_identity,
        "atom_count": atom_count,
        "species": species,
        "atom_ordering": "canonical_structure_order",
        "real_space_lattice_angstrom": lattice,
        "reciprocal_convention": "physics_2pi",
        "qpoint_coordinate_system": "reciprocal_fractional",
        "path_distance_unit": "radian_per_angstrom",
        "frequency_unit": "terahertz",
        "imaginary_frequency_encoding": "negative_real",
        "frequency_zero_tolerance": 1e-5,
        "branch_scope": "full",
        "qpoints": qpoints,
        "segments": segments,
        "branches": branches,
        "degeneracy_groups": [],
        "acoustic_sum_rule": {"applied": False, "method": None},
        "source": {
            "producer": "phonopy",
            "producer_version": None,
            "calculation_method": "source_band_sampling",
            "force_constants_source": "not_embedded",
            "supercell_matrix": _optional_matrix(data.get("supercell_matrix"), integers=True),
            "primitive_matrix": _optional_matrix(data.get("primitive_matrix"), integers=False),
            "nac": {"enabled": False, "gamma_direction": None, "direction_policy": None},
            "input_sha256": source_hash,
            "adapter_version": PhononBandAdapter.adapter_version,
        },
        "warnings": warnings,
        "security": {
            "contains_javascript": False,
            "contains_html": False,
            "external_urls_allowed": False,
            "executable_content_allowed": False,
            "external_assets": [],
        },
    }


def _matrix(value: Any, name: str, *, integers: bool) -> list[list[float]]:
    if not isinstance(value, list) or len(value) != 3:
        raise _error("PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED", f"phonopy {name} must be a 3x3 matrix.")
    matrix = [_vector(row, name) for row in value]
    if integers and any(not isinstance(item, int) or isinstance(item, bool) for row in value for item in row):
        raise _error("PHONON_BAND_PARSE_FAILED", f"phonopy {name} must contain integers.")
    return matrix


def _optional_matrix(value: Any, *, integers: bool) -> list[list[float]] | None:
    return None if value is None else _matrix(value, "matrix", integers=integers)


def _vector(value: Any, name: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 3 or any(not isinstance(item, (int, float)) or isinstance(item, bool) or not math.isfinite(float(item)) for item in value):
        raise _error("PHONON_QPOINT_SHAPE_INVALID", f"phonopy {name} must be a finite triplet.")
    return [float(item) for item in value]


def _label(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) > DEFAULT_PHONON_CAPS["max_label_length"]:
        raise _error("PHONON_PATH_LABEL_INVALID", "phonopy path labels must be bounded strings.")
    return normalize_high_symmetry_label(value)


def _manifest_payload(band: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    artifacts = []
    for name, schema_version, payload in (
        ("phonon_band.json", PHONON_BAND_SCHEMA_VERSION, band),
        ("phonon_summary.json", PHONON_SUMMARY_SCHEMA_VERSION, summary),
    ):
        content = stable_phonon_json(payload).encode("utf-8")
        artifacts.append(
            {"name": name, "schema_version": schema_version, "media_type": "application/json", "size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
        )
    return {
        "schema_version": PHONON_MANIFEST_SCHEMA_VERSION,
        "structure_identity": band["structure_identity"],
        "band_schema_version": PHONON_BAND_SCHEMA_VERSION,
        "dos_schema_version": None,
        "summary_schema_version": PHONON_SUMMARY_SCHEMA_VERSION,
        "artifacts": artifacts,
        "security": band["security"],
    }


def _parse_report(band: dict[str, Any], validation: dict[str, Any], source_format: str, source_hash: str) -> dict[str, Any]:
    return {
        "schema_version": "phase10h1.phonon_band_parse_report.v1",
        "source_format": source_format,
        "source_sha256": source_hash,
        "canonical_schema_version": PHONON_BAND_SCHEMA_VERSION,
        "structure_identity": band["structure_identity"],
        "atom_count": band["atom_count"],
        "qpoint_count": len(band["qpoints"]),
        "segment_count": len(band["segments"]),
        "branch_count": len(band["branches"]),
        "frequency_unit": band["frequency_unit"],
        "reciprocal_convention": band["reciprocal_convention"],
        "branch_order": "source_order_preserved",
        "validation": validation,
        "warnings": list(band["warnings"]),
        "security": band["security"],
    }


def _plot_payload(band: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    traces: list[dict[str, Any]] = []
    for branch in band["branches"]:
        for segment in band["segments"]:
            start, end = segment["start_qpoint_index"], segment["end_qpoint_index"] + 1
            traces.append(
                {
                    "type": "scatter",
                    "mode": "lines",
                    "name": f"Branch {branch['branch_index'] + 1}",
                    "legendgroup": f"branch-{branch['branch_index']}",
                    "showlegend": segment["segment_index"] == 0,
                    "x": [point["distance"] for point in band["qpoints"][start:end]],
                    "y": branch["frequencies"][start:end],
                    "hovertemplate": "Path %{x:.5f}<br>Frequency %{y:.5f} THz<extra></extra>",
                }
            )
    ticks = [(point["distance"], point["label"]) for point in band["qpoints"] if point["label"] is not None]
    return {
        "schema_version": "phase10h1.phonon_band_plot.v1",
        "artifact_type": "phonon.band_plot",
        "data": traces,
        "layout": {
            "title": {"text": "Phonon band structure"},
            "xaxis": {"title": {"text": "Wave vector path"}, "tickmode": "array", "tickvals": [item[0] for item in ticks], "ticktext": [item[1] for item in ticks]},
            "yaxis": {"title": {"text": "Frequency (THz)"}, "zeroline": True},
            "showlegend": False,
            "hovermode": "x unified",
        },
        "metadata": {
            "structure_identity": band["structure_identity"],
            "branch_count": summary["branch_count"],
            "segment_count": summary["segment_count"],
            "trace_count": len(traces),
            "negative_frequency_preserved": True,
            "discontinuities_split": True,
        },
        "security": band["security"],
    }


def _table_payload(band: dict[str, Any], max_rows: int) -> dict[str, Any]:
    total_rows = len(band["qpoints"]) * len(band["branches"])
    zero_tolerance = band["frequency_zero_tolerance"]
    rows: list[dict[str, Any]] = []
    for point in band["qpoints"]:
        for branch in band["branches"]:
            if len(rows) >= max_rows:
                break
            frequency = branch["frequencies"][point["index"]]
            rows.append(
                {
                    "qpoint_index": point["index"],
                    "segment_index": point["segment_index"],
                    "path_distance": point["distance"],
                    "q_x": point["coordinates"][0],
                    "q_y": point["coordinates"][1],
                    "q_z": point["coordinates"][2],
                    "label": point["label"],
                    "branch_index": branch["branch_index"],
                    "frequency_terahertz": frequency,
                    "classification": (
                        "imaginary"
                        if frequency < -zero_tolerance
                        else "near_zero"
                        if abs(frequency) <= zero_tolerance
                        else "real"
                    ),
                }
            )
        if len(rows) >= max_rows:
            break
    return {
        "schema_version": "phase10h1.phonon_band_table.v1",
        "columns": [
            "qpoint_index", "segment_index", "path_distance", "q_x", "q_y", "q_z",
            "label", "branch_index", "frequency_terahertz", "classification",
        ],
        "units": {
            "qpoint_coordinates": band["qpoint_coordinate_system"],
            "path_distance": band["path_distance_unit"],
            "frequency": band["frequency_unit"],
        },
        "rows": rows,
        "row_count": len(rows),
        "total_row_count": total_rows,
        "truncated": len(rows) < total_rows,
        "security": band["security"],
    }


def _recipe_payload(adapter: PhononBandAdapter, params: dict[str, Any], band: dict[str, Any], source_format: str) -> dict[str, Any]:
    return {
        "schema_version": "phase10h1.phonon_band_recipe.v1",
        "tool_id": adapter.tool_id,
        "adapter_version": adapter.adapter_version,
        "structure_identity": band["structure_identity"],
        "source_format": source_format,
        "params": params,
        "steps": ["resolve_approved_source", "safe_parse", "normalize_to_phase10h", "canonical_validate", "emit_static_artifacts"],
        "deterministic": True,
        "dos": False,
        "eigenvectors": False,
        "animation": False,
        "external_resources": False,
        "dependencies": {"new_dependencies_added": False, **adapter.dependency_versions()},
    }


def _error(code: str, message: str, details: dict[str, Any] | None = None) -> ToolExecutionError:
    return ToolExecutionError(code="TOOL_INPUT_INVALID", message=message, tool_id=PhononBandAdapter.tool_id, details={"errorType": code, **(details or {})})
