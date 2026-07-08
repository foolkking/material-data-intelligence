from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pymatgen.core import Structure

try:  # pragma: no cover - dependency-present path is exercised in CI.
    from pymatgen.analysis.diffraction.xrd import XRDCalculator
except Exception:  # pragma: no cover
    XRDCalculator = None  # type: ignore[assignment]

from mdi_artifact_core import ArtifactPayload, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..errors import ToolExecutionError
from ..platform_builtin.structure import (
    PreparedStructures,
    _BaseStructureAdapter,
    _dedupe,
    _elements,
    _lattice_payload,
    _round,
)


@dataclass(frozen=True)
class XrdPatternResult:
    payload: dict[str, Any]
    plot_payload: dict[str, Any]
    summary: str
    recipe: dict[str, Any]
    params: dict[str, Any]


class XrdPatternAdapter(_BaseStructureAdapter):
    tool_id = "structure.xrd"
    adapter_version = "0.1.0"

    def run(self, prepared: PreparedStructures, params: dict[str, Any]) -> XrdPatternResult:
        normalized = _xrd_params(params)
        if XRDCalculator is None:
            raise ToolExecutionError(
                code="TOOL_DEPENDENCY_MISSING",
                message="structure.xrd requires pymatgen XRDCalculator.",
                tool_id=self.tool_id,
                details={"errorType": "XRD_CALCULATOR_UNAVAILABLE"},
            )

        calculator = XRDCalculator(wavelength=normalized["radiation"])
        records = [
            _structure_xrd_record(label, structure, calculator=calculator, params=normalized)
            for label, structure in sorted(prepared.structures.items())
        ]
        peaks = [peak for record in records for peak in record["peaks"]]
        peaks.sort(key=lambda item: (item["two_theta_deg"], -item["intensity"], item["d_spacing_angstrom"], item["structureId"]))
        peak_count_before_limit = len(peaks)
        if peak_count_before_limit == 0:
            raise ToolExecutionError(
                code="TOOL_RUNTIME_ERROR",
                message="No XRD peaks were generated in the requested range after filtering.",
                tool_id=self.tool_id,
                details={"errorType": "XRD_NO_PEAKS_IN_RANGE", "parameters": normalized},
            )

        warnings = list(prepared.warnings)
        warnings.extend(
            [
                "XRD_CUKA_ONLY",
                "XRD_SYNTHETIC_PATTERN_NOT_EXPERIMENTAL",
                "XRD_PEAK_TOLERANCE_PINNED",
                "XRD_NO_PROFILE_BROADENING",
                "XRD_NO_RIETVELD_REFINEMENT",
                "XRD_BROWSER_EVIDENCE_DEFERRED",
            ]
        )
        for record in records:
            warnings.extend(record["warnings"])
        truncated = peak_count_before_limit > normalized["max_peaks"]
        if truncated:
            warnings.append(f"XRD_PEAKS_TRUNCATED: retained {normalized['max_peaks']} of {peak_count_before_limit} peaks.")
            peaks = peaks[: normalized["max_peaks"]]

        first_record = records[0]
        payload = {
            "artifactType": self.tool_id,
            "schema_version": "phase10e4.xrd_pattern.v1",
            "tool_id": self.tool_id,
            "source": _source_payload(self.context),
            "structureCount": len(records),
            "structures": [
                {
                    "structureId": record["structureId"],
                    "formula": record["formula"],
                    "site_count": record["site_count"],
                    "species": record["species"],
                    "pbc": record["pbc"],
                    "lattice": record["lattice"],
                    "peak_count": record["peak_count"],
                }
                for record in records
            ],
            "structure": {
                "formula": first_record["formula"],
                "site_count": sum(int(record["site_count"]) for record in records),
                "species": sorted({element for record in records for element in record["species"]}),
                "pbc": first_record["pbc"],
                "lattice": first_record["lattice"],
            },
            "parameters": normalized,
            "radiation": {
                "name": normalized["radiation"],
                "wavelength_angstrom": _round(float(getattr(calculator, "wavelength", 0.0) or 0.0)),
            },
            "two_theta_range": [normalized["two_theta_min"], normalized["two_theta_max"]],
            "pattern": {
                "peaks": peaks,
                "peak_count": len(peaks),
                "intensity_scale": "relative_100",
            },
            "limits": {
                "max_peaks": normalized["max_peaks"],
                "peak_count_before_limit": peak_count_before_limit,
                "truncated": truncated,
            },
            "warnings": _dedupe(warnings),
            "security": _security_payload(),
        }
        plot_payload = _plot_payload(payload)
        summary = _summary_markdown(payload)
        recipe = _recipe_payload(self, normalized, payload)
        return XrdPatternResult(
            payload=payload,
            plot_payload=plot_payload,
            summary=summary,
            recipe=recipe,
            params=normalized,
        )

    def export(self, result: XrdPatternResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        default_requested = {
            ArtifactType.table_json,
            ArtifactType.plotly_json,
            ArtifactType.summary_md,
            ArtifactType.recipe_json,
        }
        requested = set(artifact_types) or default_requested
        payloads: list[ArtifactPayload] = []
        if ArtifactType.table_json in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.table_json,
                    file_name="xrd_pattern.json",
                    content=stable_json_dumps(result.payload),
                    media_type="application/json",
                )
            )
        if ArtifactType.plotly_json in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.plotly_json,
                    file_name="xrd_plot.json",
                    content=stable_json_dumps(result.plot_payload),
                    media_type="application/json",
                )
            )
        if ArtifactType.summary_md in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=result.summary,
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.recipe_json,
                    file_name="recipe.json",
                    content=stable_json_dumps(result.recipe),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={
                "adapter": self.tool_id,
                "artifactType": result.payload["artifactType"],
                "schemaVersion": result.payload["schema_version"],
                "radiation": result.params["radiation"],
                "twoThetaMin": result.params["two_theta_min"],
                "twoThetaMax": result.params["two_theta_max"],
                "staticPhysics": True,
                "browserApiEvidence": "deferred_to_phase10e5",
            },
        )


def _xrd_params(params: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "radiation",
        "two_theta_min",
        "two_theta_max",
        "intensity_threshold",
        "peak_merge_tolerance",
        "max_peaks",
        "include_hkl",
        "plot_kind",
    }
    unknown = sorted(set(params) - allowed)
    if unknown:
        raise _param_error("Unknown params are not accepted by structure.xrd.", {"unknownParams": unknown})

    radiation = str(params.get("radiation", "CuKa"))
    if radiation != "CuKa":
        raise _param_error("structure.xrd only supports radiation=CuKa in Phase 10E-4.", {"radiation": radiation})
    two_theta_min = _float_param(params, "two_theta_min", 0.0)
    two_theta_max = _float_param(params, "two_theta_max", 90.0)
    if two_theta_min < 0.0 or two_theta_min > 180.0:
        raise _param_error("two_theta_min must be between 0.0 and 180.0.", {"two_theta_min": two_theta_min})
    if two_theta_max < 1.0 or two_theta_max > 180.0:
        raise _param_error("two_theta_max must be between 1.0 and 180.0.", {"two_theta_max": two_theta_max})
    if two_theta_min >= two_theta_max:
        raise _param_error(
            "two_theta_min must be smaller than two_theta_max.",
            {"two_theta_min": two_theta_min, "two_theta_max": two_theta_max},
        )
    threshold = _float_param(params, "intensity_threshold", 0.0)
    if threshold < 0.0 or threshold > 100.0:
        raise _param_error("intensity_threshold must be between 0.0 and 100.0.", {"intensity_threshold": threshold})
    merge_tolerance = _float_param(params, "peak_merge_tolerance", 0.05)
    if merge_tolerance < 0.0 or merge_tolerance > 1.0:
        raise _param_error("peak_merge_tolerance must be between 0.0 and 1.0.", {"peak_merge_tolerance": merge_tolerance})
    max_peaks = _int_param(params, "max_peaks", 500)
    if max_peaks < 1 or max_peaks > 5000:
        raise _param_error("max_peaks must be between 1 and 5000.", {"max_peaks": max_peaks})
    plot_kind = str(params.get("plot_kind", "stem"))
    if plot_kind != "stem":
        raise _param_error("structure.xrd only supports plot_kind=stem.", {"plot_kind": plot_kind})
    return {
        "radiation": radiation,
        "two_theta_min": _round(two_theta_min),
        "two_theta_max": _round(two_theta_max),
        "intensity_threshold": _round(threshold),
        "peak_merge_tolerance": _round(merge_tolerance),
        "max_peaks": max_peaks,
        "include_hkl": bool(params.get("include_hkl", True)),
        "plot_kind": plot_kind,
    }


def _structure_xrd_record(
    label: str,
    structure: Structure,
    *,
    calculator: Any,
    params: dict[str, Any],
) -> dict[str, Any]:
    warnings: list[str] = []
    if not all(bool(item) for item in getattr(structure, "pbc", (True, True, True))):
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message="structure.xrd requires a periodic crystalline structure.",
            tool_id=XrdPatternAdapter.tool_id,
            details={"errorType": "XRD_NON_PERIODIC_STRUCTURE", "structure": label},
        )
    pattern = calculator.get_pattern(
        structure,
        two_theta_range=(float(params["two_theta_min"]), float(params["two_theta_max"])),
    )
    peaks: list[dict[str, Any]] = []
    for index, two_theta in enumerate(pattern.x):
        intensity = _round(float(pattern.y[index]))
        if intensity < float(params["intensity_threshold"]):
            continue
        peak: dict[str, Any] = {
            "structureId": label,
            "two_theta_deg": _round(float(two_theta)),
            "intensity": intensity,
            "d_spacing_angstrom": _round(float(pattern.d_hkls[index])),
        }
        if bool(params["include_hkl"]):
            peak["hkls"] = _hkls_payload(pattern.hkls[index])
        peaks.append(peak)
    peaks.sort(key=lambda item: (item["two_theta_deg"], -item["intensity"], item["d_spacing_angstrom"]))
    lattice = _lattice_payload(structure)
    lattice.pop("matrix", None)
    if _has_partial_occupancy(structure):
        warnings.append("XRD_PARTIAL_OCCUPANCY_PRESENT")
    return {
        "structureId": label,
        "formula": structure.composition.reduced_formula,
        "site_count": len(structure),
        "species": _elements(structure),
        "pbc": [bool(item) for item in getattr(structure, "pbc", (True, True, True))],
        "lattice": lattice,
        "peaks": peaks,
        "peak_count": len(peaks),
        "warnings": _dedupe(warnings),
    }


def _hkls_payload(values: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in values or []:
        hkl = item.get("hkl") if isinstance(item, dict) else None
        if hkl is None:
            continue
        normalized.append(
            {
                "hkl": [int(component) for component in hkl],
                "multiplicity": int(item.get("multiplicity", 0)),
            }
        )
    normalized.sort(key=lambda item: (tuple(item["hkl"]), item["multiplicity"]))
    return normalized


def _plot_payload(payload: dict[str, Any]) -> dict[str, Any]:
    peaks = payload["pattern"]["peaks"]
    x_values = [float(item["two_theta_deg"]) for item in peaks]
    y_values = [float(item["intensity"]) for item in peaks]
    return {
        "artifactType": "structure.xrd_plot",
        "schema_version": "phase10e4.static_chart.v1",
        "tool_id": "structure.xrd",
        "chart_type": "stem",
        "title": "XRD Pattern",
        "x_axis": {"label": "2theta (degrees)", "values": x_values},
        "y_axis": {"label": "Relative Intensity", "values": y_values},
        "series": [{"name": "XRD peaks", "x": x_values, "y": y_values}],
        "metadata": {
            "formula": payload["structure"]["formula"],
            "site_count": payload["structure"]["site_count"],
            "radiation": payload["parameters"]["radiation"],
            "two_theta_min": payload["parameters"]["two_theta_min"],
            "two_theta_max": payload["parameters"]["two_theta_max"],
        },
        "security": _security_payload(),
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    peaks = payload["pattern"]["peaks"]
    strongest = max(peaks, key=lambda item: (float(item["intensity"]), -float(item["two_theta_deg"]))) if peaks else None
    first_peaks = [
        {"two_theta_deg": item["two_theta_deg"], "intensity": item["intensity"]}
        for item in peaks[:5]
    ]
    warnings = payload.get("warnings") or []
    lines = [
        "# XRD Pattern",
        "",
        "## Input",
        f"- source: {payload['source']['resource_type']}",
        f"- parser: {payload['source']['parser']}",
        f"- formula: {payload['structure']['formula']}",
        f"- site count: {payload['structure']['site_count']}",
        f"- periodic: {all(bool(item) for item in payload['structure']['pbc'])}",
        "",
        "## Method",
        "- calculator: pymatgen XRDCalculator",
        f"- radiation: {payload['parameters']['radiation']}",
        f"- two-theta range: {payload['parameters']['two_theta_min']} to {payload['parameters']['two_theta_max']} degrees",
        f"- intensity threshold: {payload['parameters']['intensity_threshold']}",
        f"- peak limit: {payload['parameters']['max_peaks']}",
        "- rounding policy: two-theta, d-spacing, and intensity rounded to 6 decimals",
        "",
        "## Results",
        f"- peak count: {payload['pattern']['peak_count']}",
        f"- strongest peak: {strongest if strongest else 'none'}",
        f"- first peaks: {first_peaks}",
        "",
        "## Limits",
        f"- truncated: {payload['limits']['truncated']}",
        f"- warnings: {', '.join(str(item) for item in warnings) if warnings else 'none'}",
        "",
        "## Security",
        "- no artifact JavaScript",
        "- no external URLs",
        "- no WebGL renderer",
        "- no full 3D viewer",
    ]
    return "\n".join(lines) + "\n"


def _recipe_payload(adapter: XrdPatternAdapter, params: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    context = adapter.context
    return {
        "schema_version": "phase10e4.recipe.v1",
        "schemaVersion": "0.1",
        "recipeId": f"recipe_{context.tool_call_id}",
        "name": "XRD Pattern",
        "tool_id": adapter.tool_id,
        "toolId": adapter.tool_id,
        "inputs": {
            "dataset_id": context.dataset_id,
            "input_hashes": adapter._input_hashes,
        },
        "params": params,
        "steps": [
            "parse_structure",
            "validate_periodic_crystalline_structure",
            "initialize_xrd_calculator",
            "generate_xrd_pattern",
            "filter_two_theta_range",
            "apply_intensity_threshold",
            "apply_peak_limit",
            "round_numeric_values",
            "write_xrd_pattern_json",
            "write_static_chart_json",
            "write_summary",
        ],
        "deterministic": True,
        "dependencies": {
            "new_dependencies_added": False,
            **BaseToolAdapter.dependency_versions(),
        },
        "artifactTypes": ["table_json", "plotly_json", "summary_md", "recipe_json"],
        "artifacts": ["xrd_pattern.json", "xrd_plot.json", "summary.md", "recipe.json"],
        "numericTolerance": {
            "two_theta_rounding_decimals": 6,
            "d_spacing_rounding_decimals": 6,
            "intensity_rounding_decimals": 6,
            "peak_merge_tolerance": params["peak_merge_tolerance"],
        },
        "limits": payload["limits"],
    }


def _source_payload(context: Any) -> dict[str, Any]:
    return {
        "resource_id": context.dataset_id,
        "resource_type": "normalized_object",
        "filename": "structures",
        "parser": "pymatgen.Structure",
        "parser_version": BaseToolAdapter.dependency_versions().get("pymatgenVersion", "unknown"),
        "dataset_id": context.dataset_id,
        "project_id": context.project_id,
    }


def _security_payload() -> dict[str, Any]:
    return {
        "contains_javascript": False,
        "external_urls": [],
        "external_urls_allowed": False,
    }


def _has_partial_occupancy(structure: Structure) -> bool:
    return any(len(site.species) > 1 or abs(sum(float(amount) for amount in site.species.values()) - 1.0) > 1e-9 for site in structure)


def _float_param(params: dict[str, Any], key: str, default: float) -> float:
    try:
        return float(params.get(key, default))
    except (TypeError, ValueError) as exc:
        raise _param_error(f"{key} must be numeric.", {key: params.get(key)}) from exc


def _int_param(params: dict[str, Any], key: str, default: int) -> int:
    try:
        return int(params.get(key, default))
    except (TypeError, ValueError) as exc:
        raise _param_error(f"{key} must be an integer.", {key: params.get(key)}) from exc


def _param_error(message: str, details: dict[str, Any]) -> ToolExecutionError:
    return ToolExecutionError(
        code="TOOL_PARAM_INVALID",
        message=message,
        tool_id=XrdPatternAdapter.tool_id,
        details={"errorType": "XRD_INVALID_PARAMS", **details},
    )
