from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import re
from typing import Any

from mdi_artifact_core import (
    ArtifactPayload,
    DEFAULT_PHONON_CAPS,
    PHONON_DOS_MANIFEST_SCHEMA_VERSION,
    PHONON_DOS_SCHEMA_VERSION,
    PHONON_DOS_SUMMARY_SCHEMA_VERSION,
    convert_frequency,
    phonon_dos_summary,
    stable_phonon_json,
    trapezoidal_integral,
    validate_phonon_dos,
    validate_phonon_dos_manifest,
    validate_phonon_dos_summary,
)
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


_MAX_SOURCE_BYTES = 32_000_000
_MAX_TABLE_ROWS = 50_000
_MAX_PLOT_VALUES = 250_000
_SHA256 = re.compile(r"[0-9a-f]{64}")
_ELEMENT = re.compile(r"[A-Z][a-z]?")
_SECURITY = {
    "contains_javascript": False,
    "contains_html": False,
    "external_urls_allowed": False,
    "executable_content_allowed": False,
    "external_assets": [],
}


@dataclass(frozen=True)
class PhononDosResult:
    dos: dict[str, Any]
    summary: dict[str, Any]
    report: dict[str, Any]
    manifest: dict[str, Any]
    plot: dict[str, Any]
    table: dict[str, Any]
    recipe: dict[str, Any]


class PhononDosAdapter(BaseToolAdapter):
    tool_id = "phonon.dos"
    adapter_version = "0.1.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> Any:
        del context, input_refs, params
        if len(self._resolved_inputs) != 1:
            raise _error("PHONON_DOS_INPUT_COUNT_INVALID", "phonon.dos requires exactly one approved DOS input.")
        return self._resolved_inputs[0]

    def run(self, prepared: Any, params: dict[str, Any]) -> PhononDosResult:
        normalized = _normalize_params(params)
        dos, source_format, source_hash, completeness, conversion = _normalize_source(prepared, normalized)
        validation = validate_phonon_dos(dos)
        if not validation.valid:
            raise _error("PHONON_DOS_VALIDATION_FAILED", "The normalized phonon DOS does not satisfy phase10h.phonon_dos.v1.", {"errors": list(validation.errors)})
        summary = phonon_dos_summary(dos, projection_completeness=completeness)
        if not validate_phonon_dos_summary(summary).valid:
            raise _error("PHONON_DOS_SUMMARY_INVALID", "The generated phonon DOS summary is invalid.")
        report = _parse_report(dos, validation.as_dict(), source_format, source_hash, completeness, conversion)
        plot = _plot_payload(dos, summary, normalized["max_plot_values"])
        table = _table_payload(dos, normalized["max_table_rows"])
        manifest = _manifest_payload(dos, summary)
        if not validate_phonon_dos_manifest(manifest).valid:
            raise _error("PHONON_DOS_MANIFEST_INVALID", "The generated phonon DOS manifest is invalid.")
        recipe = _recipe_payload(self, normalized, dos, source_format, completeness)
        return PhononDosResult(dos, summary, report, manifest, plot, table, recipe)

    def export(self, result: PhononDosResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        defaults = {
            ArtifactType.phonon_dos_json,
            ArtifactType.phonon_summary_json,
            ArtifactType.phonon_report_json,
            ArtifactType.phonon_manifest_json,
            ArtifactType.plotly_json,
            ArtifactType.table_json,
            ArtifactType.recipe_json,
        }
        requested = set(artifact_types) or defaults
        payload_by_type = {
            ArtifactType.phonon_dos_json: ("phonon_dos.json", stable_phonon_json(result.dos)),
            ArtifactType.phonon_summary_json: ("phonon_dos_summary.json", stable_phonon_json(result.summary)),
            ArtifactType.phonon_report_json: ("phonon_dos_parse_report.json", stable_phonon_json(result.report)),
            ArtifactType.phonon_manifest_json: ("phonon_manifest.json", stable_phonon_json(result.manifest)),
            ArtifactType.plotly_json: ("phonon_dos_plot.json", stable_phonon_json(result.plot)),
            ArtifactType.table_json: ("phonon_dos_table.json", stable_phonon_json(result.table)),
            ArtifactType.recipe_json: ("recipe.json", stable_phonon_json(result.recipe)),
        }
        payloads = [
            ArtifactPayload(artifact_type=kind, file_name=name, content=content, media_type="application/json")
            for kind, (name, content) in payload_by_type.items()
            if kind in requested
        ]
        return self.export_payloads(
            payloads,
            provenance={
                "adapter": self.tool_id,
                "schemaVersion": PHONON_DOS_SCHEMA_VERSION,
                "structureIdentity": result.dos["structure_identity"],
                "staticDosOnly": True,
                "bandsIncluded": False,
                "combinedViewIncluded": False,
                "eigenvectorsIncluded": False,
                "animationIncluded": False,
                "externalResources": False,
            },
        )


def _normalize_params(params: dict[str, Any]) -> dict[str, Any]:
    allowed = {"source_format", "source_frequency_unit", "source_normalization", "max_table_rows", "max_plot_values", "plot_kind"}
    unknown = sorted(set(params) - allowed)
    if unknown:
        raise _error("PHONON_DOS_PARAM_INVALID", "Unknown phonon.dos parameters are not accepted.", {"unknownParams": unknown})
    source_format = params.get("source_format", "auto")
    formats = {"auto", PHONON_DOS_SCHEMA_VERSION, "phonopy_total_dos", "phonopy_projected_dos"}
    if source_format not in formats:
        raise _error("PHONON_DOS_SOURCE_FORMAT_UNSUPPORTED", "The requested phonon DOS source format is not approved.")
    frequency_unit = params.get("source_frequency_unit", "terahertz")
    if frequency_unit not in {"terahertz", "inverse_centimeter", "millielectronvolt"}:
        raise _error("PHONON_DOS_UNIT_OVERRIDE_INVALID", "The source frequency unit is not approved.")
    normalization = params.get("source_normalization", "total_modes")
    if normalization not in {"total_modes", "unit_area"}:
        raise _error("PHONON_DOS_NORMALIZATION_OVERRIDE_INVALID", "The source normalization must be total_modes or unit_area.")
    max_rows = params.get("max_table_rows", 20_000)
    max_plot = params.get("max_plot_values", 100_000)
    if not isinstance(max_rows, int) or isinstance(max_rows, bool) or not 1 <= max_rows <= _MAX_TABLE_ROWS:
        raise _error("PHONON_DOS_PARAM_INVALID", "max_table_rows must be an integer between 1 and 50000.")
    if not isinstance(max_plot, int) or isinstance(max_plot, bool) or not 2 <= max_plot <= _MAX_PLOT_VALUES:
        raise _error("PHONON_DOS_PARAM_INVALID", "max_plot_values must be an integer between 2 and 250000.")
    if params.get("plot_kind", "line") != "line":
        raise _error("PHONON_DOS_PARAM_INVALID", "phonon.dos only supports plot_kind=line.")
    return {
        "source_format": source_format,
        "source_frequency_unit": frequency_unit,
        "source_normalization": normalization,
        "max_table_rows": max_rows,
        "max_plot_values": max_plot,
        "plot_kind": "line",
    }


def _normalize_source(value: Any, params: dict[str, Any]) -> tuple[dict[str, Any], str, str, str, dict[str, Any]]:
    requested = params["source_format"]
    if isinstance(value, dict) and value.get("schema_version") == PHONON_DOS_SCHEMA_VERSION:
        if requested not in {"auto", PHONON_DOS_SCHEMA_VERSION}:
            raise _error("PHONON_DOS_SOURCE_MISMATCH", "Input content does not match source_format.")
        result = validate_phonon_dos(value)
        if not result.valid:
            raise _error("PHONON_DOS_VALIDATION_FAILED", "Canonical phonon DOS input is invalid.", {"errors": list(result.errors)})
        raw = stable_phonon_json(value)
        completeness = _canonical_completeness(value)
        conversion = {
            "source_frequency_unit": "terahertz", "source_density_unit": "modes_per_terahertz",
            "source_normalization": "total_modes", "frequency_scale": 1.0, "density_jacobian": 1.0,
            "normalization_scale": 1.0, "frequency_conversion_applied": False,
            "density_jacobian_applied": False, "normalization_scale_applied": False,
        }
        return value, PHONON_DOS_SCHEMA_VERSION, hashlib.sha256(raw.encode("utf-8")).hexdigest(), completeness, conversion

    if not isinstance(value, dict):
        raise _error("PHONON_DOS_SOURCE_FORMAT_UNSUPPORTED", "Expected canonical JSON or an approved phonopy DOS wrapper.")
    required = {
        "source_format", "content", "structure_identity", "atom_count", "species", "source_frequency_unit",
        "source_normalization", "projection_completeness", "projections", "broadening", "source",
    }
    if set(value) != required:
        raise _error("PHONON_DOS_SOURCE_FIELD_UNSUPPORTED", "The phonopy DOS wrapper fields are not exact.")
    source_format = value.get("source_format")
    if source_format not in {"phonopy_total_dos", "phonopy_projected_dos"} or requested not in {"auto", source_format}:
        raise _error("PHONON_DOS_SOURCE_MISMATCH", "Input content does not match source_format.")
    if value.get("source_frequency_unit") != params["source_frequency_unit"] or value.get("source_normalization") != params["source_normalization"]:
        raise _error("PHONON_DOS_SOURCE_MISMATCH", "Wrapper units and normalization must match validated parameters.")
    return _phonopy_text_to_dos(value)


def _phonopy_text_to_dos(wrapper: dict[str, Any]) -> tuple[dict[str, Any], str, str, str, dict[str, Any]]:
    content = wrapper.get("content")
    if not isinstance(content, str) or not content.strip() or len(content.encode("utf-8")) > _MAX_SOURCE_BYTES:
        raise _error("PHONON_DOS_SOURCE_LIMIT_EXCEEDED", "Phonopy DOS text is empty or exceeds the approved source size.")
    structure_identity = wrapper.get("structure_identity")
    atom_count = wrapper.get("atom_count")
    species = wrapper.get("species")
    if not isinstance(structure_identity, str) or _SHA256.fullmatch(structure_identity) is None:
        raise _error("PHONON_DOS_STRUCTURE_MISMATCH", "A validated structure identity is required.")
    if not isinstance(atom_count, int) or isinstance(atom_count, bool) or not 1 <= atom_count <= DEFAULT_PHONON_CAPS["max_atoms"]:
        raise _error("PHONON_ATOM_COUNT_INVALID", "The wrapper atom_count is invalid.")
    if not isinstance(species, list) or len(species) != atom_count or any(not isinstance(item, str) or _ELEMENT.fullmatch(item) is None for item in species):
        raise _error("PHONON_SPECIES_ORDER_INVALID", "The wrapper species order is invalid.")
    completeness = wrapper.get("projection_completeness")
    if completeness not in {"complete", "partial", "unknown"}:
        raise _error("PHONON_DOS_PROJECTION_UNSUPPORTED", "projection_completeness is invalid.")
    descriptors = _projection_descriptors(wrapper.get("projections"), species, wrapper["source_format"])
    expected_columns = 2 + len(descriptors)
    rows = _numeric_rows(content, expected_columns)
    if len(rows) > DEFAULT_PHONON_CAPS["max_dos_points"]:
        raise _error("PHONON_DOS_SOURCE_LIMIT_EXCEEDED", "The DOS grid exceeds the canonical point cap.")
    if len(descriptors) > DEFAULT_PHONON_CAPS["max_projected_dos_series"]:
        raise _error("PHONON_DOS_SOURCE_LIMIT_EXCEEDED", "The projected DOS series exceed the canonical cap.")
    if len(rows) * (2 + len(descriptors)) > DEFAULT_PHONON_CAPS["max_total_numeric_values"]:
        raise _error("PHONON_DOS_SOURCE_LIMIT_EXCEEDED", "The DOS numeric value count exceeds the canonical cap.")
    source_unit = wrapper["source_frequency_unit"]
    frequency_scale = convert_frequency(1.0, source_unit, "terahertz")
    if not math.isfinite(frequency_scale) or frequency_scale <= 0:
        raise _error("PHONON_DOS_UNIT_OVERRIDE_INVALID", "Frequency conversion is invalid.")
    frequencies = [row[0] * frequency_scale for row in rows]
    if any(right <= left for left, right in zip(frequencies, frequencies[1:])):
        raise _error("PHONON_DOS_GRID_INVALID", "The source frequency grid must be strictly increasing.")
    density_jacobian = 1.0 / frequency_scale
    total = [row[1] * density_jacobian for row in rows]
    projected_columns = [[row[index + 2] * density_jacobian for row in rows] for index in range(len(descriptors))]
    if any(value < 0 for value in total) or any(value < 0 for column in projected_columns for value in column):
        raise _error("PHONON_DOS_NONFINITE", "DOS densities must be finite and nonnegative.")
    integral = trapezoidal_integral(frequencies, total)
    if integral <= 0:
        raise _error("PHONON_DOS_INTEGRAL_MISMATCH", "The source DOS integral must be positive.")
    expected_modes = atom_count * 3
    normalization_scale = expected_modes / integral if wrapper["source_normalization"] == "unit_area" else 1.0
    if normalization_scale != 1.0:
        total = [value * normalization_scale for value in total]
        projected_columns = [[value * normalization_scale for value in column] for column in projected_columns]
    observed = trapezoidal_integral(frequencies, total)
    relative_error = abs(observed - expected_modes) / expected_modes
    if relative_error > 0.01:
        raise _error("PHONON_DOS_INTEGRAL_MISMATCH", "The normalized DOS integral does not match 3N within one percent.", {"relativeError": relative_error})
    source_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    source = _source_metadata(wrapper.get("source"), source_hash)
    broadening = _broadening(wrapper.get("broadening"))
    projected = [
        {
            "projection_index": index,
            "projection_type": descriptor["projection_type"],
            "atom_index": descriptor.get("atom_index"),
            "species": descriptor["species"],
            "values": projected_columns[index],
            "source_guarantees_sum": completeness == "complete",
        }
        for index, descriptor in enumerate(descriptors)
    ]
    dos = {
        "schema_version": PHONON_DOS_SCHEMA_VERSION,
        "structure_identity": structure_identity,
        "atom_count": atom_count,
        "species": species,
        "atom_ordering": "canonical_structure_order",
        "frequency_unit": "terahertz",
        "imaginary_frequency_encoding": "negative_real",
        "frequency_zero_tolerance": 1e-6,
        "density_unit": "modes_per_terahertz",
        "normalization": "total_modes",
        "frequency_grid_semantics": "sample_grid_points",
        "frequencies": frequencies,
        "total_dos": total,
        "projected_dos": projected,
        "broadening": broadening,
        "integration": {
            "method": "trapezoidal", "expected_mode_count": expected_modes, "observed_integral": observed,
            "relative_tolerance": 0.01, "status": "within_tolerance" if relative_error <= 1e-10 else "approximate",
        },
        "source": source,
        "warnings": [],
        "security": dict(_SECURITY),
    }
    validation = validate_phonon_dos(dos)
    if not validation.valid:
        raise _error("PHONON_DOS_VALIDATION_FAILED", "Normalized phonopy DOS is invalid.", {"errors": list(validation.errors)})
    conversion = {
        "source_frequency_unit": source_unit,
        "source_density_unit": f"modes_per_{source_unit}",
        "source_normalization": wrapper["source_normalization"],
        "frequency_scale": frequency_scale,
        "density_jacobian": density_jacobian,
        "normalization_scale": normalization_scale,
        "frequency_conversion_applied": source_unit != "terahertz",
        "density_jacobian_applied": source_unit != "terahertz",
        "normalization_scale_applied": wrapper["source_normalization"] == "unit_area",
    }
    return dos, wrapper["source_format"], source_hash, completeness, conversion


def _numeric_rows(content: str, expected_columns: int) -> list[list[float]]:
    rows: list[list[float]] = []
    for line_number, raw_line in enumerate(content.splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != expected_columns:
            raise _error("PHONON_DOS_PARSE_FAILED", "Every DOS data row must have the declared number of columns.", {"line": line_number})
        try:
            row = [float(part) for part in parts]
        except ValueError as exc:
            raise _error("PHONON_DOS_PARSE_FAILED", "DOS data rows must contain only finite numbers.", {"line": line_number}) from exc
        if any(not math.isfinite(value) or abs(value) > DEFAULT_PHONON_CAPS["max_numeric_magnitude"] for value in row):
            raise _error("PHONON_DOS_PARSE_FAILED", "DOS data rows must contain only bounded finite numbers.", {"line": line_number})
        rows.append(row)
    if len(rows) < 2:
        raise _error("PHONON_DOS_GRID_INVALID", "At least two DOS grid points are required.")
    return rows


def _projection_descriptors(value: Any, species: list[str], source_format: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise _error("PHONON_DOS_PROJECTION_UNSUPPORTED", "Projection descriptors must be a list.")
    if source_format == "phonopy_total_dos" and value:
        raise _error("PHONON_DOS_PROJECTION_UNSUPPORTED", "Total DOS input cannot declare projected columns.")
    if source_format == "phonopy_projected_dos" and not value:
        raise _error("PHONON_DOS_PROJECTION_UNSUPPORTED", "Projected DOS input requires explicit column identities.")
    identities: set[tuple[str, Any]] = set()
    previous: tuple[int, Any] | None = None
    result: list[dict[str, Any]] = []
    for descriptor in value:
        if not isinstance(descriptor, dict) or set(descriptor) != {"projection_type", "atom_index", "species"}:
            raise _error("PHONON_DOS_PROJECTION_UNSUPPORTED", "Projection descriptor fields are invalid.")
        kind, atom_index, symbol = descriptor["projection_type"], descriptor["atom_index"], descriptor["species"]
        if kind == "atom":
            valid = isinstance(atom_index, int) and not isinstance(atom_index, bool) and 0 <= atom_index < len(species) and symbol == species[atom_index]
            identity, order = ("atom", atom_index), (0, atom_index)
        elif kind == "species":
            valid = atom_index is None and isinstance(symbol, str) and symbol in species
            identity, order = ("species", symbol), (1, symbol)
        else:
            valid, identity, order = False, ("invalid", len(result)), (2, len(result))
        if not valid or identity in identities or (previous is not None and order <= previous):
            raise _error("PHONON_DOS_PROJECTION_UNSUPPORTED", "Projection identities must be valid, unique, and deterministically ordered.")
        identities.add(identity)
        previous = order
        result.append(dict(descriptor))
    return result


def _source_metadata(value: Any, source_hash: str) -> dict[str, Any]:
    fields = {"producer", "producer_version", "calculation_method", "force_constants_source", "supercell_matrix", "primitive_matrix", "nac", "adapter_version"}
    if not isinstance(value, dict) or set(value) != fields:
        raise _error("PHONON_DOS_SOURCE_FIELD_UNSUPPORTED", "Source metadata fields are invalid.")
    return {**value, "input_sha256": source_hash}


def _broadening(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"method", "width", "unit", "source"}:
        raise _error("PHONON_DOS_SOURCE_FIELD_UNSUPPORTED", "Broadening metadata fields are invalid.")
    return dict(value)


def _canonical_completeness(dos: dict[str, Any]) -> str:
    projected = dos["projected_dos"]
    if not projected:
        return "unknown"
    return "complete" if all(item["source_guarantees_sum"] for item in projected) else "partial"


def _manifest_payload(dos: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    artifacts = []
    for name, schema, payload in (
        ("phonon_dos.json", PHONON_DOS_SCHEMA_VERSION, dos),
        ("phonon_dos_summary.json", PHONON_DOS_SUMMARY_SCHEMA_VERSION, summary),
    ):
        content = stable_phonon_json(payload).encode("utf-8")
        artifacts.append({"name": name, "schema_version": schema, "media_type": "application/json", "size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
    return {
        "schema_version": PHONON_DOS_MANIFEST_SCHEMA_VERSION,
        "structure_identity": dos["structure_identity"],
        "dos_schema_version": PHONON_DOS_SCHEMA_VERSION,
        "summary_schema_version": PHONON_DOS_SUMMARY_SCHEMA_VERSION,
        "artifacts": artifacts,
        "security": dos["security"],
    }


def _parse_report(dos: dict[str, Any], validation: dict[str, Any], source_format: str, source_hash: str, completeness: str, conversion: dict[str, Any]) -> dict[str, Any]:
    summary = phonon_dos_summary(dos, projection_completeness=completeness)
    return {
        "schema_version": "phase10h2.phonon_dos_parse_report.v1",
        "source_format": source_format,
        "source_sha256": source_hash,
        "canonical_schema_version": PHONON_DOS_SCHEMA_VERSION,
        "structure_identity": dos["structure_identity"],
        "atom_count": dos["atom_count"],
        "grid_point_count": len(dos["frequencies"]),
        "projection_count": len(dos["projected_dos"]),
        "projection_completeness": completeness,
        "target_frequency_unit": dos["frequency_unit"],
        "target_density_unit": dos["density_unit"],
        "target_normalization": dos["normalization"],
        "normalization_integral": dos["integration"]["observed_integral"],
        "expected_modes": dos["integration"]["expected_mode_count"],
        "negative_region_integral": summary["imaginary_region_integral"],
        "conversion": conversion,
        "validation": validation,
        "warnings": list(dos["warnings"]),
        "deterministic": True,
        "security": dos["security"],
    }


def _plot_payload(dos: dict[str, Any], summary: dict[str, Any], max_values: int) -> dict[str, Any]:
    available = 1 + len(dos["projected_dos"])
    max_series = max(1, min(8, max_values // len(dos["frequencies"])))
    selected = dos["projected_dos"][: max(0, max_series - 1)]
    traces = [{"type": "scatter", "mode": "lines", "name": "Total DOS", "x": dos["frequencies"], "y": dos["total_dos"], "hovertemplate": "Frequency %{x:.5f} THz<br>DOS %{y:.5f} modes/THz<extra></extra>"}]
    for projection in selected:
        identity = f"Atom {projection['atom_index']} ({projection['species']})" if projection["projection_type"] == "atom" else f"Species {projection['species']}"
        traces.append({"type": "scatter", "mode": "lines", "name": identity, "x": dos["frequencies"], "y": projection["values"], "hovertemplate": f"{identity}<br>Frequency %{{x:.5f}} THz<br>DOS %{{y:.5f}} modes/THz<extra></extra>"})
    return {
        "schema_version": "phase10h2.phonon_dos_plot.v1",
        "artifact_type": "phonon.dos_plot",
        "data": traces,
        "layout": {"title": {"text": "Phonon density of states"}, "xaxis": {"title": {"text": "Frequency (THz)"}, "zeroline": True}, "yaxis": {"title": {"text": "DOS (modes/THz)"}}, "showlegend": True, "hovermode": "x unified"},
        "metadata": {
            "structure_identity": dos["structure_identity"], "grid_point_count": len(dos["frequencies"]),
            "available_series": available, "rendered_series": len(traces), "degraded": len(traces) < available,
            "degraded_code": "PHONON_DOS_PLOT_DEGRADED" if len(traces) < available else None,
            "negative_frequency_preserved": summary["frequency_min"] < 0, "orientation": "frequency_x_dos_y",
        },
        "security": dos["security"],
    }


def _table_payload(dos: dict[str, Any], max_rows: int) -> dict[str, Any]:
    rows = []
    tolerance = dos["frequency_zero_tolerance"]
    for index, (frequency, total) in enumerate(zip(dos["frequencies"], dos["total_dos"])):
        if len(rows) >= max_rows:
            break
        rows.append({
            "grid_index": index,
            "frequency_terahertz": frequency,
            "total_dos_modes_per_terahertz": total,
            "classification": "imaginary" if frequency < -tolerance else "near_zero" if abs(frequency) <= tolerance else "real",
        })
    return {
        "schema_version": "phase10h2.phonon_dos_table.v1",
        "columns": ["grid_index", "frequency_terahertz", "total_dos_modes_per_terahertz", "classification"],
        "units": {"frequency": dos["frequency_unit"], "density": dos["density_unit"]},
        "rows": rows, "row_count": len(rows), "total_row_count": len(dos["frequencies"]),
        "truncated": len(rows) < len(dos["frequencies"]),
        "projection_data_available_in_canonical_json": bool(dos["projected_dos"]),
        "security": dos["security"],
    }


def _recipe_payload(adapter: PhononDosAdapter, params: dict[str, Any], dos: dict[str, Any], source_format: str, completeness: str) -> dict[str, Any]:
    return {
        "schema_version": "phase10h2.phonon_dos_recipe.v1",
        "tool_id": adapter.tool_id,
        "adapter_version": adapter.adapter_version,
        "structure_identity": dos["structure_identity"],
        "source_format": source_format,
        "params": params,
        "projection_completeness": completeness,
        "steps": ["resolve_approved_source", "safe_parse", "convert_frequency_and_density", "normalize_total_modes", "canonical_validate", "emit_static_artifacts"],
        "deterministic": True,
        "bands": False, "combined_view": False, "eigenvectors": False, "animation": False,
        "broadening_applied": False, "external_resources": False,
        "dependencies": {"new_dependencies_added": False, **adapter.dependency_versions()},
    }


def _error(code: str, message: str, details: dict[str, Any] | None = None) -> ToolExecutionError:
    return ToolExecutionError(code="TOOL_INPUT_INVALID", message=message, tool_id=PhononDosAdapter.tool_id, details={"errorType": code, **(details or {})})
