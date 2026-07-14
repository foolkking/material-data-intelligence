from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Any, Literal

from .phonon_contract import (
    DENSITY_UNIT,
    FREQUENCY_UNIT,
    IMAGINARY_FREQUENCY_ENCODING,
    PHONON_BAND_SCHEMA_VERSION,
    PHONON_DOS_SCHEMA_VERSION,
    convert_frequency,
    stable_phonon_json,
    trapezoidal_integral,
    validate_phonon_band,
    validate_phonon_dos,
)


PHONON_BAND_DOS_SCHEMA_VERSION = "phase10h.phonon_band_dos.v1"
PHONON_BAND_DOS_SUMMARY_SCHEMA_VERSION = "phase10h.phonon_band_dos_summary.v1"
PHONON_BAND_DOS_COMPATIBILITY_SCHEMA_VERSION = "phase10h.phonon_band_dos_compatibility_report.v1"
PHONON_BAND_DOS_PLOT_SCHEMA_VERSION = "phase10h.phonon_band_dos_plot.v1"
PHONON_BAND_DOS_TABLE_SCHEMA_VERSION = "phase10h.phonon_band_dos_table.v1"
PHONON_BAND_DOS_MANIFEST_SCHEMA_VERSION = "phase10h.phonon_band_dos_manifest.v1"

COMBINED_CHECK_ORDER = (
    "input_artifacts",
    "band_schema",
    "dos_schema",
    "artifact_hashes",
    "structure_identity",
    "atom_count",
    "species_ordering",
    "cell_lineage",
    "source_lineage",
    "force_constants",
    "frequency_unit",
    "imaginary_encoding",
    "zero_tolerance",
    "nac",
    "dos_normalization",
    "projection_identity",
    "display_caps",
    "frequency_domain",
    "display_options",
)

COMBINED_CAPS = {
    "max_visible_projections": 4,
    "max_combined_plot_values_interactive": 500_000,
    "max_combined_plot_values": 1_000_000,
    "max_plot_traces": 4_096,
    "max_table_rows": 500,
    "max_artifact_bytes": 64_000_000,
    "max_warnings": 32,
}

COMBINED_WARNING_CODES = frozenset(
    {
        "PHONON_BAND_DOS_ASR_METADATA_PARTIAL",
        "PHONON_BAND_DOS_FREQUENCY_RANGE_DIFFERENCE",
        "PHONON_BAND_DOS_LINEAGE_INCOMPLETE",
        "PHONON_BAND_DOS_PLOT_DEGRADED",
    }
)

_COMPATIBILITY_CODES = frozenset(
    {
        "PHONON_BAND_DOS_INPUT_SCHEMA_INVALID",
        "PHONON_BAND_DOS_STRUCTURE_MISMATCH",
        "PHONON_BAND_DOS_ATOM_COUNT_MISMATCH",
        "PHONON_BAND_DOS_ATOM_ORDER_MISMATCH",
        "PHONON_BAND_DOS_CELL_LINEAGE_MISMATCH",
        "PHONON_BAND_DOS_SOURCE_LINEAGE_MISMATCH",
        "PHONON_BAND_DOS_FORCE_CONSTANTS_MISMATCH",
        "PHONON_BAND_DOS_FREQUENCY_UNIT_INCOMPATIBLE",
        "PHONON_BAND_DOS_UNIT_CONVERSION_APPLIED",
        "PHONON_BAND_DOS_IMAGINARY_ENCODING_MISMATCH",
        "PHONON_BAND_DOS_ZERO_TOLERANCE_MISMATCH",
        "PHONON_BAND_DOS_NAC_MISMATCH",
        "PHONON_BAND_DOS_NAC_DIRECTION_MISMATCH",
        "PHONON_BAND_DOS_NORMALIZATION_INVALID",
    }
)

_SECURITY = {
    "contains_javascript": False,
    "contains_html": False,
    "external_urls_allowed": False,
    "executable_content_allowed": False,
    "external_assets": [],
}
_HASH = re.compile(r"[0-9a-f]{64}")
_SAFE_ID = re.compile(r"[A-Za-z0-9_.:-]{1,128}")
_FORBIDDEN_KEYS = {
    "callback", "callbacks", "code", "eval", "function", "html", "iframe", "module",
    "script", "shader", "src", "texture", "url", "urls", "__proto__", "constructor", "prototype",
}
_FORBIDDEN_MARKERS = ("http://", "https://", "javascript:", "<script", "<iframe", "eval(", "new function", "file://")


@dataclass(frozen=True)
class CombinedValidationResult:
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "errors": list(self.errors), "warnings": list(self.warnings)}


@dataclass(frozen=True)
class PhononArtifactReference:
    artifact_id: str
    schema_version: str
    media_type: str
    size_bytes: int
    sha256: str
    payload: dict[str, Any]
    canonicalization: dict[str, Any] | None

    def public(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "schema_version": self.schema_version,
            "media_type": self.media_type,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class PhononBandDosProducts:
    combined: dict[str, Any]
    summary: dict[str, Any]
    compatibility_report: dict[str, Any]
    plot: dict[str, Any]
    table: dict[str, Any]
    manifest: dict[str, Any]


class PhononBandDosContractError(ValueError):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


def combined_content_hash(payload: Any) -> str:
    return hashlib.sha256(stable_phonon_json(payload).encode("utf-8")).hexdigest()


def convert_dos_frequency_density(
    frequencies: list[float],
    total_dos: list[float],
    projected_dos: list[list[float]],
    *,
    source_unit: str,
    target_unit: str = FREQUENCY_UNIT,
    broadening_width: float | None = None,
) -> dict[str, Any]:
    if len(frequencies) < 2 or len(total_dos) != len(frequencies) or any(len(values) != len(frequencies) for values in projected_dos):
        raise PhononBandDosContractError("PHONON_BAND_DOS_FREQUENCY_UNIT_INCOMPATIBLE", "DOS conversion arrays have incompatible shapes.")
    factor = convert_frequency(1.0, source_unit, target_unit)
    if not math.isfinite(factor) or factor <= 0:
        raise PhononBandDosContractError("PHONON_BAND_DOS_FREQUENCY_UNIT_INCOMPATIBLE", "DOS conversion factor is invalid.")
    source_values = [*frequencies, *total_dos, *(value for values in projected_dos for value in values)]
    if any(not _finite(value) for value in source_values) or any(value < 0 for value in [*total_dos, *(value for values in projected_dos for value in values)]):
        raise PhononBandDosContractError("PHONON_BAND_DOS_FREQUENCY_UNIT_INCOMPATIBLE", "DOS conversion values must be finite and densities non-negative.")
    converted_frequencies = [float(value) * factor for value in frequencies]
    converted_total = [float(value) / factor for value in total_dos]
    converted_projected = [[float(value) / factor for value in values] for values in projected_dos]
    before = trapezoidal_integral([float(value) for value in frequencies], [float(value) for value in total_dos])
    after = trapezoidal_integral(converted_frequencies, converted_total)
    if abs(before - after) > max(1e-10, abs(before) * 1e-10):
        raise PhononBandDosContractError("PHONON_BAND_DOS_DENSITY_JACOBIAN_INVALID", "DOS integral changed during unit conversion.")
    if broadening_width is not None and (not _finite(broadening_width) or broadening_width <= 0):
        raise PhononBandDosContractError("PHONON_BAND_DOS_FREQUENCY_UNIT_INCOMPATIBLE", "Broadening width is invalid.")
    return {
        "frequencies": converted_frequencies,
        "total_dos": converted_total,
        "projected_dos": converted_projected,
        "broadening_width": None if broadening_width is None else float(broadening_width) * factor,
        "factor": factor,
        "density_jacobian": 1.0 / factor,
        "integral_before": before,
        "integral_after": after,
    }


def resolve_phonon_artifact_reference(value: Any, *, role: Literal["band", "dos"]) -> PhononArtifactReference:
    expected = PHONON_BAND_SCHEMA_VERSION if role == "band" else PHONON_DOS_SCHEMA_VERSION
    if isinstance(value, dict) and "payload" not in value and value.get("schema_version") == expected:
        payload = value
        content = stable_phonon_json(payload).encode("utf-8")
        if len(content) > COMBINED_CAPS["max_artifact_bytes"]:
            raise PhononBandDosContractError(f"PHONON_BAND_DOS_{role.upper()}_ARTIFACT_INVALID", f"The {role} artifact exceeds the approved size cap.")
        digest = hashlib.sha256(content).hexdigest()
        return PhononArtifactReference(f"inline-{role}-{digest[:16]}", expected, "application/json", len(content), digest, payload, None)
    if not isinstance(value, dict):
        raise PhononBandDosContractError(f"PHONON_BAND_DOS_{role.upper()}_ARTIFACT_INVALID", f"The {role} input is not an approved artifact reference.")
    allowed = {"artifact_id", "schema_version", "media_type", "size_bytes", "sha256", "payload", "canonicalization"}
    if set(value) - allowed or not isinstance(value.get("payload"), dict):
        raise PhononBandDosContractError(f"PHONON_BAND_DOS_{role.upper()}_ARTIFACT_INVALID", f"The {role} artifact reference has unsupported fields.")
    payload = value["payload"]
    content = stable_phonon_json(payload).encode("utf-8")
    digest = hashlib.sha256(content).hexdigest()
    artifact_id = value.get("artifact_id")
    if not isinstance(artifact_id, str) or _SAFE_ID.fullmatch(artifact_id) is None:
        raise PhononBandDosContractError(f"PHONON_BAND_DOS_{role.upper()}_ARTIFACT_INVALID", f"The {role} artifact id is invalid.")
    if value.get("schema_version") != expected or payload.get("schema_version") != expected or value.get("media_type") != "application/json":
        raise PhononBandDosContractError("PHONON_BAND_DOS_ARTIFACT_SCHEMA_UNSUPPORTED", f"The {role} artifact schema or media type is unsupported.")
    if value.get("sha256") != digest:
        raise PhononBandDosContractError("PHONON_BAND_DOS_ARTIFACT_HASH_MISMATCH", f"The {role} artifact hash does not match its canonical content.")
    if value.get("size_bytes") != len(content) or len(content) > COMBINED_CAPS["max_artifact_bytes"]:
        raise PhononBandDosContractError(f"PHONON_BAND_DOS_{role.upper()}_ARTIFACT_INVALID", f"The {role} artifact size metadata is invalid.")
    canonicalization = value.get("canonicalization")
    if canonicalization is not None:
        _validate_canonicalization(canonicalization, payload, role)
    return PhononArtifactReference(artifact_id, expected, "application/json", len(content), digest, payload, canonicalization)


def compose_phonon_band_dos(
    band_input: Any,
    dos_input: Any,
    *,
    selected_projection_ids: list[str] | None = None,
    domain_policy: Literal["union", "manual_view"] = "union",
    manual_frequency_domain: tuple[float, float] | None = None,
    max_table_rows: int = 200,
) -> PhononBandDosProducts:
    band_ref = resolve_phonon_artifact_reference(band_input, role="band")
    dos_ref = resolve_phonon_artifact_reference(dos_input, role="dos")
    band, dos = band_ref.payload, dos_ref.payload
    band_result, dos_result = validate_phonon_band(band), validate_phonon_dos(dos)
    if not band_result.valid:
        raise PhononBandDosContractError("PHONON_BAND_DOS_BAND_ARTIFACT_INVALID", "The band artifact failed independent canonical validation.", {"errors": list(band_result.errors)})
    if not dos_result.valid:
        raise PhononBandDosContractError("PHONON_BAND_DOS_DOS_ARTIFACT_INVALID", "The DOS artifact failed independent canonical validation.", {"errors": list(dos_result.errors)})
    selected = selected_projection_ids or []
    if len(selected) > COMBINED_CAPS["max_visible_projections"] or len(selected) != len(set(selected)):
        raise PhononBandDosContractError("PHONON_BAND_DOS_PROJECTION_LIMIT_EXCEEDED", "Visible projected DOS selection exceeds the application-owned limit.")
    projection_by_id = {_projection_id(item): item for item in dos["projected_dos"]}
    if any(item not in projection_by_id for item in selected):
        raise PhononBandDosContractError("PHONON_BAND_DOS_PROJECTION_INVALID", "A selected projected DOS identity is unavailable.")
    if not isinstance(max_table_rows, int) or isinstance(max_table_rows, bool) or not 1 <= max_table_rows <= COMBINED_CAPS["max_table_rows"]:
        raise PhononBandDosContractError("PHONON_BAND_DOS_DISPLAY_OPTIONS_INVALID", "Combined table row limit is invalid.")

    checks, hard_errors, warnings = _compatibility_checks(band_ref, dos_ref)
    if hard_errors:
        raise PhononBandDosContractError(hard_errors[0], "Band and DOS artifacts are scientifically incompatible.", {"errors": hard_errors, "checks": checks})
    conversion = _conversion_report(band_ref, dos_ref)
    compatibility_status: Literal["compatible", "convertible"] = "convertible" if conversion["frequency_conversion_applied"] else "compatible"
    band_values = [float(value) for branch in band["branches"] for value in branch["frequencies"]]
    dos_values = [float(value) for value in dos["frequencies"]]
    union_domain = [min(min(band_values), min(dos_values)), max(max(band_values), max(dos_values))]
    display_domain = _display_domain(domain_policy, manual_frequency_domain, union_domain)
    band_domain = [min(band_values), max(band_values)]
    dos_domain = [min(dos_values), max(dos_values)]
    if _range_difference_is_notable(band_domain, dos_domain):
        warnings.add("PHONON_BAND_DOS_FREQUENCY_RANGE_DIFFERENCE")
    frequency_domain = {"band": band_domain, "dos": dos_domain, "display": display_domain, "union": union_domain, "policy": domain_policy}

    plot = _plot_payload(
        band,
        dos,
        band_ref,
        dos_ref,
        selected,
        projection_by_id,
        display_domain,
        domain_policy,
        warnings,
    )
    report = _compatibility_report(band_ref, dos_ref, compatibility_status, checks, conversion, frequency_domain, warnings)
    summary = _summary_payload(band, dos, compatibility_status, frequency_domain, warnings)
    table = _table_payload(report, summary, max_table_rows)
    report_hash = combined_content_hash(report)
    combined = {
        "schema_version": PHONON_BAND_DOS_SCHEMA_VERSION,
        "tool_id": "phonon.band_dos",
        "structure_identity": band["structure_identity"],
        "band": band_ref.public(),
        "dos": dos_ref.public(),
        "compatibility": {
            "status": compatibility_status,
            "report_name": "phonon_band_dos_compatibility_report.json",
            "report_sha256": report_hash,
            "frequency_conversion_applied": conversion["frequency_conversion_applied"],
            "density_jacobian_applied": conversion["density_jacobian_applied"],
            "warnings": sorted(warnings),
        },
        "frequency_axis": {
            "unit": FREQUENCY_UNIT,
            "minimum": display_domain[0],
            "maximum": display_domain[1],
            "domain_policy": domain_policy,
            "zero_tolerance": band["frequency_zero_tolerance"],
        },
        "display": {
            "layout": "band_left_dos_right",
            "shared_frequency_axis": True,
            "dos_orientation": "density_x_frequency_y",
            "performance_mode": plot["display"]["mode"],
            "default_projection_mode": "total_only",
            "selected_projection_ids": plot["display"]["selected_projection_ids"],
        },
        "provenance": {"deterministic": True, "source_hashes": [band_ref.sha256, dos_ref.sha256], "derived_for_display": True},
        "warnings": sorted(warnings),
        "security": dict(_SECURITY),
    }
    artifacts = [
        ("phonon_band_dos.json", PHONON_BAND_DOS_SCHEMA_VERSION, combined),
        ("phonon_band_dos_summary.json", PHONON_BAND_DOS_SUMMARY_SCHEMA_VERSION, summary),
        ("phonon_band_dos_compatibility_report.json", PHONON_BAND_DOS_COMPATIBILITY_SCHEMA_VERSION, report),
        ("phonon_band_dos_plot.json", PHONON_BAND_DOS_PLOT_SCHEMA_VERSION, plot),
        ("phonon_band_dos_table.json", PHONON_BAND_DOS_TABLE_SCHEMA_VERSION, table),
    ]
    manifest = _manifest_payload(band_ref, dos_ref, compatibility_status, artifacts)
    validators = (
        validate_phonon_band_dos,
        validate_phonon_band_dos_summary,
        validate_phonon_band_dos_compatibility_report,
        validate_phonon_band_dos_plot,
        validate_phonon_band_dos_table,
    )
    for (name, _, payload), validator in zip(artifacts, validators, strict=True):
        result = validator(payload)
        if not result.valid:
            raise PhononBandDosContractError(
                "PHONON_BAND_DOS_OUTPUT_INVALID",
                "A generated combined artifact failed validation.",
                {"artifact": name, "errors": list(result.errors)},
            )
    manifest_result = validate_phonon_band_dos_manifest(manifest)
    if not manifest_result.valid:
        raise PhononBandDosContractError("PHONON_BAND_DOS_OUTPUT_INVALID", "The generated combined manifest failed validation.", {"errors": list(manifest_result.errors)})
    return PhononBandDosProducts(combined, summary, report, plot, table, manifest)


def validate_phonon_band_dos(payload: Any) -> CombinedValidationResult:
    fields = {"schema_version", "tool_id", "structure_identity", "band", "dos", "compatibility", "frequency_axis", "display", "provenance", "warnings", "security"}
    errors = _base_validation(payload, fields, PHONON_BAND_DOS_SCHEMA_VERSION)
    if not isinstance(payload, dict):
        return _validation(errors)
    if payload.get("tool_id") != "phonon.band_dos" or not _hash(payload.get("structure_identity")):
        errors.add("PHONON_BAND_DOS_SCHEMA_INVALID")
    for role, schema in (("band", PHONON_BAND_SCHEMA_VERSION), ("dos", PHONON_DOS_SCHEMA_VERSION)):
        if not _valid_public_ref(payload.get(role), schema):
            errors.add("PHONON_BAND_DOS_ARTIFACT_REFERENCE_INVALID")
    compatibility = payload.get("compatibility")
    if not isinstance(compatibility, dict) or set(compatibility) != {"status", "report_name", "report_sha256", "frequency_conversion_applied", "density_jacobian_applied", "warnings"} or compatibility.get("status") not in {"compatible", "convertible"} or compatibility.get("report_name") != "phonon_band_dos_compatibility_report.json" or not _hash(compatibility.get("report_sha256")):
        errors.add("PHONON_BAND_DOS_SCHEMA_INVALID")
    axis = payload.get("frequency_axis")
    if not isinstance(axis, dict) or set(axis) != {"unit", "minimum", "maximum", "domain_policy", "zero_tolerance"} or axis.get("unit") != FREQUENCY_UNIT or axis.get("domain_policy") not in {"union", "manual_view"} or not _ordered_range(axis.get("minimum"), axis.get("maximum")) or not _finite(axis.get("zero_tolerance")):
        errors.add("PHONON_BAND_DOS_DOMAIN_INVALID")
    display = payload.get("display")
    if not isinstance(display, dict) or set(display) != {"layout", "shared_frequency_axis", "dos_orientation", "performance_mode", "default_projection_mode", "selected_projection_ids"} or display.get("layout") != "band_left_dos_right" or display.get("shared_frequency_axis") is not True or display.get("dos_orientation") != "density_x_frequency_y" or display.get("performance_mode") not in {"interactive", "degraded", "refused"} or display.get("default_projection_mode") != "total_only" or not _valid_projection_ids(display.get("selected_projection_ids")):
        errors.add("PHONON_BAND_DOS_DISPLAY_OPTIONS_INVALID")
    _validate_warning_list(payload.get("warnings"), errors)
    return _validation(errors, payload.get("warnings"))


def validate_phonon_band_dos_summary(payload: Any) -> CombinedValidationResult:
    fields = {
        "schema_version", "structure_identity", "atom_count", "species", "branch_count", "qpoint_count", "segment_count",
        "dos_grid_point_count", "projection_count", "frequency_unit", "frequency_min", "frequency_max", "band_frequency_min",
        "band_frequency_max", "dos_frequency_min", "dos_frequency_max", "imaginary_band_mode_count", "imaginary_dos_integral",
        "dos_density_unit", "dos_normalization", "dos_integral", "expected_modes", "compatibility_status", "nac_enabled",
        "band_asr_applied", "broadening", "warnings", "security",
    }
    errors = _base_validation(payload, fields, PHONON_BAND_DOS_SUMMARY_SCHEMA_VERSION)
    if not isinstance(payload, dict):
        return _validation(errors)
    counts = [payload.get(key) for key in ("atom_count", "branch_count", "qpoint_count", "segment_count", "dos_grid_point_count", "projection_count", "imaginary_band_mode_count", "expected_modes")]
    atom_count = payload.get("atom_count") if _positive_int(payload.get("atom_count")) else 0
    if not _hash(payload.get("structure_identity")) or any(not _nonnegative_int(value) for value in counts) or atom_count < 1 or payload.get("branch_count") != 3 * atom_count or payload.get("expected_modes") != 3 * atom_count:
        errors.add("PHONON_BAND_DOS_SCHEMA_INVALID")
    ranges = [("frequency_min", "frequency_max"), ("band_frequency_min", "band_frequency_max"), ("dos_frequency_min", "dos_frequency_max")]
    if any(not _ordered_range(payload.get(a), payload.get(b)) for a, b in ranges) or payload.get("frequency_unit") != FREQUENCY_UNIT or payload.get("dos_density_unit") != DENSITY_UNIT or payload.get("dos_normalization") != "total_modes" or payload.get("compatibility_status") not in {"compatible", "convertible"}:
        errors.add("PHONON_BAND_DOS_SCHEMA_INVALID")
    if not _finite(payload.get("imaginary_dos_integral")) or not _finite(payload.get("dos_integral")) or type(payload.get("nac_enabled")) is not bool or type(payload.get("band_asr_applied")) is not bool or not _valid_species(payload.get("species")) or not _valid_broadening(payload.get("broadening")):
        errors.add("PHONON_BAND_DOS_SCHEMA_INVALID")
    _validate_warning_list(payload.get("warnings"), errors)
    return _validation(errors, payload.get("warnings"))


def validate_phonon_band_dos_compatibility_report(payload: Any) -> CombinedValidationResult:
    fields = {"schema_version", "status", "band_artifact", "dos_artifact", "checks", "conversion", "frequency_domain", "warnings", "deterministic", "security"}
    errors = _base_validation(payload, fields, PHONON_BAND_DOS_COMPATIBILITY_SCHEMA_VERSION)
    if not isinstance(payload, dict):
        return _validation(errors)
    checks = payload.get("checks")
    if payload.get("status") not in {"compatible", "convertible", "incompatible"} or payload.get("deterministic") is not True or not isinstance(checks, list) or [item.get("name") for item in checks if isinstance(item, dict)] != list(COMBINED_CHECK_ORDER):
        errors.add("PHONON_BAND_DOS_COMPATIBILITY_REPORT_INVALID")
    for item in checks if isinstance(checks, list) else []:
        if not isinstance(item, dict) or set(item) != {"name", "status", "result_code", "band_value", "dos_value"} or item.get("status") not in {"pass", "convertible", "warning", "fail"} or (item.get("result_code") is not None and item.get("result_code") not in _COMPATIBILITY_CODES):
            errors.add("PHONON_BAND_DOS_COMPATIBILITY_REPORT_INVALID")
    if not _valid_public_ref(payload.get("band_artifact"), PHONON_BAND_SCHEMA_VERSION) or not _valid_public_ref(payload.get("dos_artifact"), PHONON_DOS_SCHEMA_VERSION):
        errors.add("PHONON_BAND_DOS_ARTIFACT_REFERENCE_INVALID")
    if not _valid_conversion(payload.get("conversion")):
        errors.add("PHONON_BAND_DOS_COMPATIBILITY_REPORT_INVALID")
    elif payload.get("status") == "convertible" and not payload["conversion"]["frequency_conversion_applied"]:
        errors.add("PHONON_BAND_DOS_COMPATIBILITY_REPORT_INVALID")
    _validate_domain(payload.get("frequency_domain"), errors)
    _validate_warning_list(payload.get("warnings"), errors)
    return _validation(errors, payload.get("warnings"))


def validate_phonon_band_dos_plot(payload: Any) -> CombinedValidationResult:
    fields = {"schema_version", "layout", "shared_frequency_axis", "band_panel", "dos_panel", "display", "source_refs", "security"}
    errors = _base_validation(payload, fields, PHONON_BAND_DOS_PLOT_SCHEMA_VERSION)
    if not isinstance(payload, dict):
        return _validation(errors)
    axis = payload.get("shared_frequency_axis")
    if payload.get("layout") != "band_left_dos_right" or not isinstance(axis, dict) or set(axis) != {"unit", "minimum", "maximum", "zero_tolerance", "domain_policy"} or axis.get("unit") != FREQUENCY_UNIT or axis.get("domain_policy") not in {"union", "manual_view"} or not _ordered_range(axis.get("minimum"), axis.get("maximum")) or not _finite(axis.get("zero_tolerance")) or float(axis.get("zero_tolerance", -1)) < 0:
        errors.add("PHONON_BAND_DOS_PLOT_INVALID")
    band_panel, dos_panel, display = payload.get("band_panel"), payload.get("dos_panel"), payload.get("display")
    if not isinstance(band_panel, dict) or set(band_panel) != {"x_axis", "series", "ticks", "preserve_segment_breaks"} or band_panel.get("x_axis") != "q_path_distance" or band_panel.get("preserve_segment_breaks") is not True:
        errors.add("PHONON_BAND_DOS_PLOT_INVALID")
    if not isinstance(dos_panel, dict) or set(dos_panel) != {"x_axis", "y_axis", "density_unit", "frequencies", "total_dos", "projections"} or dos_panel.get("x_axis") != "dos_density" or dos_panel.get("y_axis") != "shared_frequency" or dos_panel.get("density_unit") != DENSITY_UNIT:
        errors.add("PHONON_BAND_DOS_PLOT_INVALID")
    if not isinstance(display, dict) or set(display) != {"show_imaginary_region", "show_high_symmetry_labels", "mode", "reason", "numeric_values", "trace_count", "selected_projection_ids"} or display.get("mode") not in {"interactive", "degraded", "refused"}:
        errors.add("PHONON_BAND_DOS_PLOT_INVALID")
    numeric = display.get("numeric_values") if isinstance(display, dict) else None
    traces = display.get("trace_count") if isinstance(display, dict) else None
    if not _nonnegative_int(numeric) or not _nonnegative_int(traces) or numeric > COMBINED_CAPS["max_combined_plot_values"] or traces > COMBINED_CAPS["max_plot_traces"]:
        errors.add("PHONON_BAND_DOS_PLOT_BUDGET_EXCEEDED")
    _validate_plot_series(band_panel, dos_panel, display, errors)
    refs = payload.get("source_refs")
    if not isinstance(refs, dict) or set(refs) != {"band", "dos"} or not _valid_public_ref(refs.get("band"), PHONON_BAND_SCHEMA_VERSION) or not _valid_public_ref(refs.get("dos"), PHONON_DOS_SCHEMA_VERSION):
        errors.add("PHONON_BAND_DOS_ARTIFACT_REFERENCE_INVALID")
    return _validation(errors)


def validate_phonon_band_dos_table(payload: Any) -> CombinedValidationResult:
    fields = {"schema_version", "compatibility_columns", "compatibility_rows", "summary_rows", "row_count", "truncated", "security"}
    errors = _base_validation(payload, fields, PHONON_BAND_DOS_TABLE_SCHEMA_VERSION)
    if not isinstance(payload, dict):
        return _validation(errors)
    rows = payload.get("compatibility_rows")
    summary = payload.get("summary_rows")
    if payload.get("compatibility_columns") != ["check", "band_value", "dos_value", "status", "result_code"] or not isinstance(rows, list) or not isinstance(summary, list) or not _nonnegative_int(payload.get("row_count")) or payload.get("row_count") != len(rows) + len(summary) or payload.get("row_count") > COMBINED_CAPS["max_table_rows"] or type(payload.get("truncated")) is not bool:
        errors.add("PHONON_BAND_DOS_TABLE_INVALID")
    return _validation(errors)


def validate_phonon_band_dos_manifest(payload: Any) -> CombinedValidationResult:
    fields = {"schema_version", "tool_id", "structure_identity", "compatibility_status", "frequency_unit", "source_artifacts", "artifact_order", "artifacts", "capabilities", "security"}
    errors = _base_validation(payload, fields, PHONON_BAND_DOS_MANIFEST_SCHEMA_VERSION)
    if not isinstance(payload, dict):
        return _validation(errors)
    order = ["phonon_band_dos.json", "phonon_band_dos_summary.json", "phonon_band_dos_compatibility_report.json", "phonon_band_dos_plot.json", "phonon_band_dos_table.json", "phonon_band_dos_manifest.json"]
    if payload.get("tool_id") != "phonon.band_dos" or not _hash(payload.get("structure_identity")) or payload.get("compatibility_status") not in {"compatible", "convertible"} or payload.get("frequency_unit") != FREQUENCY_UNIT or payload.get("artifact_order") != order:
        errors.add("PHONON_BAND_DOS_MANIFEST_INVALID")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list) or [item.get("name") for item in artifacts if isinstance(item, dict)] != order[:-1]:
        errors.add("PHONON_BAND_DOS_MANIFEST_INVALID")
    else:
        for item in artifacts:
            if not isinstance(item, dict) or set(item) != {"name", "schema_version", "media_type", "size_bytes", "sha256"} or item.get("media_type") != "application/json" or not _positive_int(item.get("size_bytes")) or not _hash(item.get("sha256")):
                errors.add("PHONON_BAND_DOS_MANIFEST_INVALID")
    capabilities = payload.get("capabilities")
    expected = {"band": True, "dos": True, "combined_view": True, "shared_frequency_axis": True, "projected_dos": True, "eigenvectors": False, "animation": False, "thermal_properties": False, "phonon_calculation": False, "external_resources": False}
    if capabilities != expected:
        errors.add("PHONON_BAND_DOS_MANIFEST_INVALID")
    return _validation(errors)


def _compatibility_checks(band_ref: PhononArtifactReference, dos_ref: PhononArtifactReference) -> tuple[list[dict[str, Any]], list[str], set[str]]:
    band, dos = band_ref.payload, dos_ref.payload
    checks: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: set[str] = {"PHONON_BAND_DOS_ASR_METADATA_PARTIAL"}

    def check(name: str, passed: bool, code: str | None, band_value: Any, dos_value: Any, *, convertible: bool = False, warning: bool = False) -> None:
        status = "pass" if passed else "convertible" if convertible else "warning" if warning else "fail"
        checks.append({"name": name, "status": status, "result_code": code if not passed else None, "band_value": _summary_value(band_value), "dos_value": _summary_value(dos_value)})
        if not passed and not convertible and not warning and code:
            errors.append(code)

    check("input_artifacts", True, None, band_ref.artifact_id, dos_ref.artifact_id)
    check("band_schema", band.get("schema_version") == PHONON_BAND_SCHEMA_VERSION, "PHONON_BAND_DOS_INPUT_SCHEMA_INVALID", band.get("schema_version"), PHONON_BAND_SCHEMA_VERSION)
    check("dos_schema", dos.get("schema_version") == PHONON_DOS_SCHEMA_VERSION, "PHONON_BAND_DOS_INPUT_SCHEMA_INVALID", dos.get("schema_version"), PHONON_DOS_SCHEMA_VERSION)
    check("artifact_hashes", True, None, band_ref.sha256, dos_ref.sha256)
    check("structure_identity", band["structure_identity"] == dos["structure_identity"], "PHONON_BAND_DOS_STRUCTURE_MISMATCH", band["structure_identity"], dos["structure_identity"])
    check("atom_count", band["atom_count"] == dos["atom_count"], "PHONON_BAND_DOS_ATOM_COUNT_MISMATCH", band["atom_count"], dos["atom_count"])
    check("species_ordering", band["species"] == dos["species"] and band["atom_ordering"] == dos["atom_ordering"], "PHONON_BAND_DOS_ATOM_ORDER_MISMATCH", band["species"], dos["species"])
    band_source, dos_source = band["source"], dos["source"]
    cell_match = band_source["primitive_matrix"] == dos_source["primitive_matrix"] and band_source["supercell_matrix"] == dos_source["supercell_matrix"]
    check("cell_lineage", cell_match, "PHONON_BAND_DOS_CELL_LINEAGE_MISMATCH", [band_source["primitive_matrix"], band_source["supercell_matrix"]], [dos_source["primitive_matrix"], dos_source["supercell_matrix"]])
    force_band, force_dos = band_source["force_constants_source"], dos_source["force_constants_source"]
    lineage_match = band_source["producer"] == dos_source["producer"] and band_source["calculation_method"] == dos_source["calculation_method"] and ((force_band is not None and force_band == force_dos) or (force_band is None and force_dos is None and band_source["input_sha256"] == dos_source["input_sha256"]))
    check("source_lineage", lineage_match, "PHONON_BAND_DOS_SOURCE_LINEAGE_MISMATCH", [band_source["producer"], band_source["calculation_method"], band_source["input_sha256"]], [dos_source["producer"], dos_source["calculation_method"], dos_source["input_sha256"]])
    force_match = force_band == force_dos and (force_band is not None or band_source["input_sha256"] == dos_source["input_sha256"])
    check("force_constants", force_match, "PHONON_BAND_DOS_FORCE_CONSTANTS_MISMATCH", force_band, force_dos)
    conversion = _conversion_report(band_ref, dos_ref)
    canonical_units = band["frequency_unit"] == dos["frequency_unit"] == FREQUENCY_UNIT
    conversion_applied = conversion["frequency_conversion_applied"]
    check(
        "frequency_unit",
        canonical_units and not conversion_applied,
        "PHONON_BAND_DOS_UNIT_CONVERSION_APPLIED" if canonical_units and conversion_applied else "PHONON_BAND_DOS_FREQUENCY_UNIT_INCOMPATIBLE",
        conversion["band_frequency_unit_from"],
        conversion["dos_frequency_unit_from"],
        convertible=canonical_units and conversion_applied,
    )
    check("imaginary_encoding", band["imaginary_frequency_encoding"] == dos["imaginary_frequency_encoding"] == IMAGINARY_FREQUENCY_ENCODING, "PHONON_BAND_DOS_IMAGINARY_ENCODING_MISMATCH", band["imaginary_frequency_encoding"], dos["imaginary_frequency_encoding"])
    check("zero_tolerance", abs(float(band["frequency_zero_tolerance"]) - float(dos["frequency_zero_tolerance"])) <= 1e-12, "PHONON_BAND_DOS_ZERO_TOLERANCE_MISMATCH", band["frequency_zero_tolerance"], dos["frequency_zero_tolerance"])
    nac_band, nac_dos = band_source["nac"], dos_source["nac"]
    nac_code = "PHONON_BAND_DOS_NAC_MISMATCH" if nac_band.get("enabled") != nac_dos.get("enabled") else "PHONON_BAND_DOS_NAC_DIRECTION_MISMATCH"
    check("nac", nac_band == nac_dos, nac_code, nac_band, nac_dos)
    integration = dos["integration"]
    normalization_ok = dos["normalization"] == "total_modes" and dos["density_unit"] == DENSITY_UNIT and integration["expected_mode_count"] == 3 * dos["atom_count"] and integration["status"] in {"within_tolerance", "approximate"}
    check("dos_normalization", normalization_ok, "PHONON_BAND_DOS_NORMALIZATION_INVALID", ["n/a", 3 * band["atom_count"]], [dos["normalization"], integration["observed_integral"]])
    check("projection_identity", True, None, band["species"], len(dos["projected_dos"]))
    check("display_caps", True, None, len(band["qpoints"]) * len(band["branches"]), len(dos["frequencies"]) * (len(dos["projected_dos"]) + 1))
    check("frequency_domain", True, None, [min(value for branch in band["branches"] for value in branch["frequencies"]), max(value for branch in band["branches"] for value in branch["frequencies"])], [min(dos["frequencies"]), max(dos["frequencies"])])
    check("display_options", True, None, "band_left", "dos_right")
    return checks, errors, warnings


def _conversion_report(band_ref: PhononArtifactReference, dos_ref: PhononArtifactReference) -> dict[str, Any]:
    band_info = band_ref.canonicalization or _identity_canonicalization("band", band_ref.payload)
    dos_info = dos_ref.canonicalization or _identity_canonicalization("dos", dos_ref.payload)
    applied = band_info["source_frequency_unit"] != FREQUENCY_UNIT or dos_info["source_frequency_unit"] != FREQUENCY_UNIT
    return {
        "band_frequency_unit_from": band_info["source_frequency_unit"],
        "dos_frequency_unit_from": dos_info["source_frequency_unit"],
        "frequency_unit_to": FREQUENCY_UNIT,
        "band_frequency_factor": band_info["frequency_factor_to_terahertz"],
        "dos_frequency_factor": dos_info["frequency_factor_to_terahertz"],
        "frequency_conversion_applied": applied,
        "density_jacobian_applied": bool(dos_info["density_jacobian_applied"]),
        "broadening_width_converted": bool(dos_info["broadening_width_converted"]),
        "integral_before": dos_info["integral_before"],
        "integral_after": dos_info["integral_after"],
    }


def _identity_canonicalization(role: str, payload: dict[str, Any]) -> dict[str, Any]:
    integral = payload["integration"]["observed_integral"] if role == "dos" else None
    return {
        "source_frequency_unit": FREQUENCY_UNIT,
        "frequency_factor_to_terahertz": 1.0,
        "density_jacobian_applied": False,
        "broadening_width_converted": False,
        "integral_before": integral,
        "integral_after": integral,
    }


def _validate_canonicalization(value: Any, payload: dict[str, Any], role: str) -> None:
    fields = {"source_frequency_unit", "frequency_factor_to_terahertz", "density_jacobian_applied", "broadening_width_converted", "integral_before", "integral_after"}
    if not isinstance(value, dict) or set(value) != fields or value.get("source_frequency_unit") not in {"terahertz", "inverse_centimeter", "millielectronvolt"}:
        raise PhononBandDosContractError("PHONON_BAND_DOS_CANONICALIZATION_INVALID", "Canonicalization proof is invalid.")
    expected = convert_frequency(1.0, value["source_frequency_unit"], FREQUENCY_UNIT)
    if not _finite(value.get("frequency_factor_to_terahertz")) or abs(float(value["frequency_factor_to_terahertz"]) - expected) > max(1e-12, expected * 1e-12):
        raise PhononBandDosContractError("PHONON_BAND_DOS_CANONICALIZATION_INVALID", "Canonicalization frequency factor is invalid.")
    converted = value["source_frequency_unit"] != FREQUENCY_UNIT
    if type(value.get("density_jacobian_applied")) is not bool or type(value.get("broadening_width_converted")) is not bool:
        raise PhononBandDosContractError("PHONON_BAND_DOS_CANONICALIZATION_INVALID", "Canonicalization flags are invalid.")
    if role == "band" and value["density_jacobian_applied"]:
        raise PhononBandDosContractError("PHONON_BAND_DOS_CANONICALIZATION_INVALID", "Band canonicalization cannot apply a DOS Jacobian.")
    if role == "dos":
        if value["density_jacobian_applied"] is not converted or not _finite(value.get("integral_before")) or not _finite(value.get("integral_after")) or abs(float(value["integral_before"]) - float(value["integral_after"])) > max(1e-10, abs(float(value["integral_before"])) * 1e-10):
            raise PhononBandDosContractError("PHONON_BAND_DOS_CANONICALIZATION_INVALID", "DOS Jacobian or integral proof is invalid.")
        expects_width = converted and payload["broadening"]["method"] != "none"
        if value["broadening_width_converted"] is not expects_width:
            raise PhononBandDosContractError("PHONON_BAND_DOS_CANONICALIZATION_INVALID", "Broadening conversion proof is invalid.")
    elif value["integral_before"] is not None or value["integral_after"] is not None or value["broadening_width_converted"]:
        raise PhononBandDosContractError("PHONON_BAND_DOS_CANONICALIZATION_INVALID", "Band canonicalization contains DOS-only proof fields.")


def _plot_payload(
    band: dict[str, Any], dos: dict[str, Any], band_ref: PhononArtifactReference, dos_ref: PhononArtifactReference,
    selected: list[str], projection_by_id: dict[str, dict[str, Any]], domain: list[float], domain_policy: str,
    warnings: set[str],
) -> dict[str, Any]:
    segment_point_count = sum(segment["end_qpoint_index"] - segment["start_qpoint_index"] + 1 for segment in band["segments"])
    band_value_count = 2 * segment_point_count * len(band["branches"]) + sum(point["label"] is not None for point in band["qpoints"])
    total_count = len(dos["frequencies"])
    projection_value_count = total_count * len(projection_by_id)
    numeric_values = band_value_count + 2 * total_count + projection_value_count
    trace_count = len(band["segments"]) * len(band["branches"]) + 1 + len(selected)
    mode = "interactive"
    reason = None
    available = list(projection_by_id)
    active = selected
    if numeric_values > COMBINED_CAPS["max_combined_plot_values_interactive"]:
        mode = "degraded"
        reason = "PHONON_BAND_DOS_PLOT_DEGRADED"
        warnings.add(reason)
        available = []
        active = []
        numeric_values = band_value_count + 2 * total_count
        trace_count = len(band["segments"]) * len(band["branches"]) + 1
    if numeric_values > COMBINED_CAPS["max_combined_plot_values"] or trace_count > COMBINED_CAPS["max_plot_traces"]:
        mode = "refused"
        reason = "PHONON_BAND_DOS_PLOT_BUDGET_EXCEEDED"
        available = []
        active = []
        numeric_values = 0
        trace_count = 0
    band_series: list[dict[str, Any]] = []
    if mode != "refused":
        for branch in band["branches"]:
            for segment in band["segments"]:
                start, end = segment["start_qpoint_index"], segment["end_qpoint_index"] + 1
                band_series.append({
                    "branch_index": branch["branch_index"],
                    "segment_index": segment["segment_index"],
                    "path_distance": [point["distance"] for point in band["qpoints"][start:end]],
                    "frequencies": branch["frequencies"][start:end],
                })
    ticks = [] if mode == "refused" else [{"distance": point["distance"], "label": point["label"]} for point in band["qpoints"] if point["label"] is not None]
    projections = [] if mode == "refused" else [
        {"projection_id": identity, "projection_type": projection_by_id[identity]["projection_type"], "atom_index": projection_by_id[identity]["atom_index"], "species": projection_by_id[identity]["species"], "source_guarantees_sum": projection_by_id[identity]["source_guarantees_sum"], "values": projection_by_id[identity]["values"]}
        for identity in available
    ]
    return {
        "schema_version": PHONON_BAND_DOS_PLOT_SCHEMA_VERSION,
        "layout": "band_left_dos_right",
        "shared_frequency_axis": {"unit": FREQUENCY_UNIT, "minimum": domain[0], "maximum": domain[1], "zero_tolerance": band["frequency_zero_tolerance"], "domain_policy": domain_policy},
        "band_panel": {"x_axis": "q_path_distance", "series": band_series, "ticks": ticks, "preserve_segment_breaks": True},
        "dos_panel": {"x_axis": "dos_density", "y_axis": "shared_frequency", "density_unit": DENSITY_UNIT, "frequencies": [] if mode == "refused" else dos["frequencies"], "total_dos": [] if mode == "refused" else dos["total_dos"], "projections": projections},
        "display": {"show_imaginary_region": True, "show_high_symmetry_labels": True, "mode": mode, "reason": reason, "numeric_values": numeric_values, "trace_count": trace_count, "selected_projection_ids": active},
        "source_refs": {"band": band_ref.public(), "dos": dos_ref.public()},
        "security": dict(_SECURITY),
    }


def _compatibility_report(
    band_ref: PhononArtifactReference, dos_ref: PhononArtifactReference, status: str, checks: list[dict[str, Any]],
    conversion: dict[str, Any], domain: dict[str, Any], warnings: set[str],
) -> dict[str, Any]:
    return {
        "schema_version": PHONON_BAND_DOS_COMPATIBILITY_SCHEMA_VERSION,
        "status": status,
        "band_artifact": band_ref.public(),
        "dos_artifact": dos_ref.public(),
        "checks": checks,
        "conversion": conversion,
        "frequency_domain": domain,
        "warnings": sorted(warnings),
        "deterministic": True,
        "security": dict(_SECURITY),
    }


def _summary_payload(band: dict[str, Any], dos: dict[str, Any], status: str, domain: dict[str, Any], warnings: set[str]) -> dict[str, Any]:
    band_values = [float(value) for branch in band["branches"] for value in branch["frequencies"]]
    tolerance = float(band["frequency_zero_tolerance"])
    negative_dos = _negative_integral(dos["frequencies"], dos["total_dos"], -tolerance)
    return {
        "schema_version": PHONON_BAND_DOS_SUMMARY_SCHEMA_VERSION,
        "structure_identity": band["structure_identity"],
        "atom_count": band["atom_count"],
        "species": band["species"],
        "branch_count": len(band["branches"]),
        "qpoint_count": len(band["qpoints"]),
        "segment_count": len(band["segments"]),
        "dos_grid_point_count": len(dos["frequencies"]),
        "projection_count": len(dos["projected_dos"]),
        "frequency_unit": FREQUENCY_UNIT,
        "frequency_min": domain["display"][0],
        "frequency_max": domain["display"][1],
        "band_frequency_min": domain["band"][0],
        "band_frequency_max": domain["band"][1],
        "dos_frequency_min": domain["dos"][0],
        "dos_frequency_max": domain["dos"][1],
        "imaginary_band_mode_count": sum(value < -tolerance for value in band_values),
        "imaginary_dos_integral": negative_dos,
        "dos_density_unit": DENSITY_UNIT,
        "dos_normalization": dos["normalization"],
        "dos_integral": dos["integration"]["observed_integral"],
        "expected_modes": 3 * band["atom_count"],
        "compatibility_status": status,
        "nac_enabled": band["source"]["nac"]["enabled"],
        "band_asr_applied": band["acoustic_sum_rule"]["applied"],
        "broadening": dos["broadening"],
        "warnings": sorted(warnings),
        "security": dict(_SECURITY),
    }


def _table_payload(report: dict[str, Any], summary: dict[str, Any], max_rows: int) -> dict[str, Any]:
    compatibility_rows = [
        {"check": item["name"], "band_value": item["band_value"], "dos_value": item["dos_value"], "status": item["status"], "result_code": item["result_code"]}
        for item in report["checks"]
    ]
    summary_keys = (
        "structure_identity", "atom_count", "frequency_unit", "frequency_min", "frequency_max", "nac_enabled",
        "dos_normalization", "dos_integral", "expected_modes", "imaginary_band_mode_count", "imaginary_dos_integral",
    )
    summary_rows = [{"name": key, "value": summary[key]} for key in summary_keys]
    all_rows = compatibility_rows + summary_rows
    truncated = len(all_rows) > max_rows
    if truncated:
        compatibility_rows = compatibility_rows[:max_rows]
        summary_rows = []
    return {
        "schema_version": PHONON_BAND_DOS_TABLE_SCHEMA_VERSION,
        "compatibility_columns": ["check", "band_value", "dos_value", "status", "result_code"],
        "compatibility_rows": compatibility_rows,
        "summary_rows": summary_rows,
        "row_count": len(compatibility_rows) + len(summary_rows),
        "truncated": truncated,
        "security": dict(_SECURITY),
    }


def _manifest_payload(band_ref: PhononArtifactReference, dos_ref: PhononArtifactReference, status: str, artifacts: list[tuple[str, str, dict[str, Any]]]) -> dict[str, Any]:
    entries = []
    for name, schema, payload in artifacts:
        content = stable_phonon_json(payload).encode("utf-8")
        entries.append({"name": name, "schema_version": schema, "media_type": "application/json", "size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
    return {
        "schema_version": PHONON_BAND_DOS_MANIFEST_SCHEMA_VERSION,
        "tool_id": "phonon.band_dos",
        "structure_identity": band_ref.payload["structure_identity"],
        "compatibility_status": status,
        "frequency_unit": FREQUENCY_UNIT,
        "source_artifacts": {"band": band_ref.public(), "dos": dos_ref.public()},
        "artifact_order": [item["name"] for item in entries] + ["phonon_band_dos_manifest.json"],
        "artifacts": entries,
        "capabilities": {"band": True, "dos": True, "combined_view": True, "shared_frequency_axis": True, "projected_dos": True, "eigenvectors": False, "animation": False, "thermal_properties": False, "phonon_calculation": False, "external_resources": False},
        "security": dict(_SECURITY),
    }


def _display_domain(policy: str, manual: tuple[float, float] | None, union: list[float]) -> list[float]:
    if policy == "union" and manual is None:
        return union
    if policy != "manual_view" or manual is None or not _ordered_range(manual[0], manual[1]) or manual[0] < union[0] or manual[1] > union[1]:
        raise PhononBandDosContractError("PHONON_BAND_DOS_DOMAIN_INVALID", "Manual frequency view must be a finite ordered subset of the union domain.")
    return [float(manual[0]), float(manual[1])]


def _range_difference_is_notable(band: list[float], dos: list[float]) -> bool:
    union_span = max(band[1], dos[1]) - min(band[0], dos[0])
    overlap = max(0.0, min(band[1], dos[1]) - max(band[0], dos[0]))
    return union_span > 0 and overlap / union_span < 0.8


def _negative_integral(x: list[float], y: list[float], threshold: float) -> float:
    points = [(float(a), float(b)) for a, b in zip(x, y, strict=True) if float(a) < threshold]
    if len(points) < 2:
        return 0.0
    return trapezoidal_integral([item[0] for item in points], [item[1] for item in points])


def _projection_id(projection: dict[str, Any]) -> str:
    return f"atom:{projection['atom_index']}" if projection["projection_type"] == "atom" else f"species:{projection['species']}"


def _base_validation(payload: Any, fields: set[str], version: str) -> set[str]:
    errors: set[str] = set()
    if not isinstance(payload, dict) or set(payload) != fields or payload.get("schema_version") != version:
        errors.add("PHONON_BAND_DOS_SCHEMA_INVALID")
        return errors
    _scan_inert(payload, errors)
    if payload.get("security") != _SECURITY:
        errors.add("PHONON_BAND_DOS_EXTERNAL_REFERENCE_FORBIDDEN")
    try:
        if len(stable_phonon_json(payload).encode("utf-8")) > COMBINED_CAPS["max_artifact_bytes"]:
            errors.add("PHONON_BAND_DOS_ARTIFACT_LIMIT_EXCEEDED")
    except (TypeError, ValueError, RecursionError):
        errors.add("PHONON_BAND_DOS_SCHEMA_INVALID")
    return errors


def _scan_inert(root: Any, errors: set[str]) -> None:
    queue: list[tuple[Any, str, int]] = [(root, "", 0)]
    visited = 0
    while queue:
        value, key, depth = queue.pop()
        visited += 1
        if visited > 5_000_000 or depth > 12:
            errors.add("PHONON_BAND_DOS_ARTIFACT_LIMIT_EXCEEDED")
            return
        if key.lower() in _FORBIDDEN_KEYS:
            errors.add("PHONON_BAND_DOS_EXTERNAL_REFERENCE_FORBIDDEN")
        if isinstance(value, dict):
            queue.extend((child, str(child_key), depth + 1) for child_key, child in value.items())
        elif isinstance(value, list):
            queue.extend((child, key, depth + 1) for child in value)
        elif isinstance(value, str) and any(marker in value.lower() for marker in _FORBIDDEN_MARKERS):
            errors.add("PHONON_BAND_DOS_EXTERNAL_REFERENCE_FORBIDDEN")


def _valid_public_ref(value: Any, schema: str) -> bool:
    return isinstance(value, dict) and set(value) == {"artifact_id", "schema_version", "media_type", "size_bytes", "sha256"} and isinstance(value.get("artifact_id"), str) and _SAFE_ID.fullmatch(value["artifact_id"]) is not None and value.get("schema_version") == schema and value.get("media_type") == "application/json" and _positive_int(value.get("size_bytes")) and value["size_bytes"] <= COMBINED_CAPS["max_artifact_bytes"] and _hash(value.get("sha256"))


def _valid_projection_ids(value: Any) -> bool:
    return isinstance(value, list) and len(value) <= COMBINED_CAPS["max_visible_projections"] and value == list(dict.fromkeys(value)) and all(isinstance(item, str) and re.fullmatch(r"(?:atom:[0-9]{1,6}|species:[A-Z][a-z]?)", item) is not None for item in value)


def _validate_warning_list(value: Any, errors: set[str]) -> None:
    if not isinstance(value, list) or len(value) > COMBINED_CAPS["max_warnings"] or value != sorted(set(value)) or any(item not in COMBINED_WARNING_CODES for item in value):
        errors.add("PHONON_BAND_DOS_WARNING_INVALID")


def _validate_domain(value: Any, errors: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != {"band", "dos", "display", "union", "policy"} or value.get("policy") not in {"union", "manual_view"} or any(not isinstance(value.get(key), list) or len(value[key]) != 2 or not _ordered_range(value[key][0], value[key][1]) for key in ("band", "dos", "display", "union")):
        errors.add("PHONON_BAND_DOS_DOMAIN_INVALID")


def _valid_conversion(value: Any) -> bool:
    fields = {
        "band_frequency_unit_from",
        "dos_frequency_unit_from",
        "frequency_unit_to",
        "band_frequency_factor",
        "dos_frequency_factor",
        "frequency_conversion_applied",
        "density_jacobian_applied",
        "broadening_width_converted",
        "integral_before",
        "integral_after",
    }
    units = {"terahertz", "inverse_centimeter", "millielectronvolt"}
    if not isinstance(value, dict) or set(value) != fields or value.get("band_frequency_unit_from") not in units or value.get("dos_frequency_unit_from") not in units or value.get("frequency_unit_to") != FREQUENCY_UNIT:
        return False
    band_factor = convert_frequency(1.0, value["band_frequency_unit_from"], FREQUENCY_UNIT)
    dos_factor = convert_frequency(1.0, value["dos_frequency_unit_from"], FREQUENCY_UNIT)
    if not _finite(value.get("band_frequency_factor")) or not _finite(value.get("dos_frequency_factor")) or abs(float(value["band_frequency_factor"]) - band_factor) > max(1e-12, band_factor * 1e-12) or abs(float(value["dos_frequency_factor"]) - dos_factor) > max(1e-12, dos_factor * 1e-12):
        return False
    converted = value["band_frequency_unit_from"] != FREQUENCY_UNIT or value["dos_frequency_unit_from"] != FREQUENCY_UNIT
    dos_converted = value["dos_frequency_unit_from"] != FREQUENCY_UNIT
    if value.get("frequency_conversion_applied") is not converted or value.get("density_jacobian_applied") is not dos_converted or type(value.get("broadening_width_converted")) is not bool:
        return False
    before, after = value.get("integral_before"), value.get("integral_after")
    return _finite(before) and _finite(after) and abs(float(before) - float(after)) <= max(1e-10, abs(float(before)) * 1e-10)


def _validate_plot_series(band_panel: Any, dos_panel: Any, display: Any, errors: set[str]) -> None:
    if not isinstance(band_panel, dict) or not isinstance(dos_panel, dict) or not isinstance(display, dict):
        return
    series = band_panel.get("series")
    ticks = band_panel.get("ticks")
    frequencies = dos_panel.get("frequencies")
    total = dos_panel.get("total_dos")
    projections = dos_panel.get("projections")
    if not isinstance(series, list) or len(series) > COMBINED_CAPS["max_plot_traces"] or not isinstance(ticks, list) or not isinstance(frequencies, list) or not isinstance(total, list) or not isinstance(projections, list):
        errors.add("PHONON_BAND_DOS_PLOT_INVALID")
        return
    numeric_values = 0
    for item in series:
        if not isinstance(item, dict) or set(item) != {"branch_index", "segment_index", "path_distance", "frequencies"} or not _nonnegative_int(item.get("branch_index")) or not _nonnegative_int(item.get("segment_index")):
            errors.add("PHONON_BAND_DOS_PLOT_INVALID")
            continue
        path, values = item.get("path_distance"), item.get("frequencies")
        if not isinstance(path, list) or not isinstance(values, list) or len(path) != len(values) or len(path) < 2 or any(not _finite(value) for value in [*path, *values]) or any(float(path[index]) > float(path[index + 1]) for index in range(len(path) - 1)):
            errors.add("PHONON_BAND_DOS_PLOT_INVALID")
            continue
        numeric_values += len(path) + len(values)
    for tick in ticks:
        if not isinstance(tick, dict) or set(tick) != {"distance", "label"} or not _finite(tick.get("distance")) or not isinstance(tick.get("label"), str) or not 1 <= len(tick["label"]) <= 64:
            errors.add("PHONON_BAND_DOS_PLOT_INVALID")
        else:
            numeric_values += 1
    if len(frequencies) != len(total) or (frequencies and len(frequencies) < 2) or any(not _finite(value) for value in [*frequencies, *total]) or any(float(value) < 0 for value in total) or any(float(frequencies[index]) >= float(frequencies[index + 1]) for index in range(len(frequencies) - 1)):
        errors.add("PHONON_BAND_DOS_PLOT_INVALID")
    numeric_values += len(frequencies) + len(total)
    projection_ids: list[str] = []
    for item in projections:
        fields = {"projection_id", "projection_type", "atom_index", "species", "source_guarantees_sum", "values"}
        if not isinstance(item, dict) or set(item) != fields:
            errors.add("PHONON_BAND_DOS_PLOT_INVALID")
            continue
        projection_id = item.get("projection_id")
        kind, atom_index, species = item.get("projection_type"), item.get("atom_index"), item.get("species")
        valid_identity = (
            kind == "atom"
            and _nonnegative_int(atom_index)
            and isinstance(species, str)
            and projection_id == f"atom:{atom_index}"
        ) or (
            kind == "species"
            and atom_index is None
            and isinstance(species, str)
            and re.fullmatch(r"[A-Z][a-z]?", species) is not None
            and projection_id == f"species:{species}"
        )
        values = item.get("values")
        if not valid_identity or type(item.get("source_guarantees_sum")) is not bool or not isinstance(values, list) or len(values) != len(frequencies) or any(not _finite(value) or float(value) < 0 for value in values):
            errors.add("PHONON_BAND_DOS_PLOT_INVALID")
            continue
        projection_ids.append(projection_id)
        numeric_values += len(values)
    if projection_ids != list(dict.fromkeys(projection_ids)):
        errors.add("PHONON_BAND_DOS_PLOT_INVALID")
    selected = display.get("selected_projection_ids")
    reason_by_mode = {"interactive": None, "degraded": "PHONON_BAND_DOS_PLOT_DEGRADED", "refused": "PHONON_BAND_DOS_PLOT_BUDGET_EXCEEDED"}
    mode = display.get("mode")
    expected_traces = 0 if mode == "refused" else len(series) + 1 + (len(selected) if isinstance(selected, list) else 0)
    if type(display.get("show_imaginary_region")) is not bool or type(display.get("show_high_symmetry_labels")) is not bool or display.get("reason") != reason_by_mode.get(mode) or not _valid_projection_ids(selected) or any(item not in projection_ids for item in selected) or display.get("numeric_values") != numeric_values or display.get("trace_count") != expected_traces:
        errors.add("PHONON_BAND_DOS_PLOT_INVALID")
    if mode == "refused" and (series or ticks or frequencies or total or projections or selected):
        errors.add("PHONON_BAND_DOS_PLOT_INVALID")
    if mode == "degraded" and (projections or selected):
        errors.add("PHONON_BAND_DOS_PLOT_INVALID")


def _valid_species(value: Any) -> bool:
    return isinstance(value, list) and 1 <= len(value) <= 100_000 and all(isinstance(item, str) and re.fullmatch(r"[A-Z][a-z]?", item) is not None for item in value)


def _valid_broadening(value: Any) -> bool:
    if not isinstance(value, dict) or set(value) != {"method", "width", "unit", "source"} or value.get("method") not in {"none", "gaussian", "source_defined"}:
        return False
    source = value.get("source")
    if source is not None and (not isinstance(source, str) or len(source) > 128 or any(marker in source.lower() for marker in _FORBIDDEN_MARKERS)):
        return False
    if value["method"] == "none":
        return value.get("width") is None and value.get("unit") is None
    return _finite(value.get("width")) and float(value["width"]) > 0 and value.get("unit") == FREQUENCY_UNIT


def _summary_value(value: Any) -> Any:
    if isinstance(value, str):
        return value[:128]
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [_summary_value(item) for item in value[:12]]
    if isinstance(value, dict):
        return {str(key)[:64]: _summary_value(item) for key, item in sorted(value.items())[:12]}
    return str(type(value).__name__)


def _validation(errors: set[str], warnings: Any = None) -> CombinedValidationResult:
    safe_warnings = tuple(warnings) if isinstance(warnings, list) and all(isinstance(item, str) for item in warnings) else ()
    return CombinedValidationResult(not errors, tuple(sorted(errors)), safe_warnings)


def _ordered_range(minimum: Any, maximum: Any) -> bool:
    return _finite(minimum) and _finite(maximum) and float(minimum) < float(maximum)


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) and abs(float(value)) <= 1e12


def _nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _positive_int(value: Any) -> bool:
    return _nonnegative_int(value) and value > 0


def _hash(value: Any) -> bool:
    return isinstance(value, str) and _HASH.fullmatch(value) is not None
