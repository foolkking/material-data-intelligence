from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from pymatgen.core import Structure

from mdi_artifact_core import ArtifactPayload, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..errors import ToolExecutionError
from ..platform_builtin.structure import (
    PreparedStructures,
    _BaseStructureAdapter,
    _dedupe,
    _elements,
    _round,
)


@dataclass(frozen=True)
class RdfResult:
    payload: dict[str, Any]
    plot_payload: dict[str, Any]
    summary: str
    recipe: dict[str, Any]
    params: dict[str, Any]


class RdfAdapter(_BaseStructureAdapter):
    tool_id = "structure.rdf"
    adapter_version = "0.1.0"

    def run(self, prepared: PreparedStructures, params: dict[str, Any]) -> RdfResult:
        normalized = _rdf_params(params)
        bin_edges, bin_centers = _radial_bins(normalized)
        records = [
            _structure_rdf_record(label, structure, params=normalized, bin_edges=bin_edges, bin_centers=bin_centers)
            for label, structure in sorted(prepared.structures.items())
        ]
        payload = _payload(self, prepared=prepared, params=normalized, records=records, bin_edges=bin_edges, bin_centers=bin_centers)
        plot_payload = _plot_payload(payload)
        summary = _summary_markdown(payload)
        recipe = _recipe_payload(self, normalized, payload)
        return RdfResult(payload=payload, plot_payload=plot_payload, summary=summary, recipe=recipe, params=normalized)

    def export(self, result: RdfResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
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
                    file_name="rdf.json",
                    content=stable_json_dumps(result.payload),
                    media_type="application/json",
                )
            )
        if ArtifactType.plotly_json in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.plotly_json,
                    file_name="rdf_plot.json",
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
                "normalization": result.params["normalization"],
                "rMaxAngstrom": result.params["r_max_angstrom"],
                "binWidthAngstrom": result.params["bin_width_angstrom"],
                "staticPhysics": True,
                "browserApiEvidence": "deferred_to_phase10e8",
            },
        )


def _rdf_params(params: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "r_max_angstrom",
        "bin_width_angstrom",
        "normalization",
        "include_partial_pairs",
        "max_partial_pairs",
        "max_sites",
        "max_bins",
        "max_neighbors_total",
        "plot_kind",
    }
    unknown = sorted(set(params) - allowed)
    if unknown:
        raise _param_error("Unknown params are not accepted by structure.rdf.", {"unknownParams": unknown})

    r_max = _float_param(params, "r_max_angstrom", 8.0)
    if r_max < 0.5 or r_max > 30.0:
        raise _param_error("r_max_angstrom must be between 0.5 and 30.0.", {"r_max_angstrom": r_max})
    bin_width = _float_param(params, "bin_width_angstrom", 0.1)
    if bin_width < 0.01 or bin_width > 1.0:
        raise _param_error("bin_width_angstrom must be between 0.01 and 1.0.", {"bin_width_angstrom": bin_width})
    normalization = str(params.get("normalization", "number_density"))
    if normalization != "number_density":
        raise _param_error("structure.rdf only supports normalization=number_density.", {"normalization": normalization})
    max_partial_pairs = _int_param(params, "max_partial_pairs", 64)
    if max_partial_pairs < 1 or max_partial_pairs > 256:
        raise _param_error("max_partial_pairs must be between 1 and 256.", {"max_partial_pairs": max_partial_pairs})
    max_sites = _int_param(params, "max_sites", 500)
    if max_sites < 1 or max_sites > 5000:
        raise _param_error("max_sites must be between 1 and 5000.", {"max_sites": max_sites})
    max_bins = _int_param(params, "max_bins", 1000)
    if max_bins < 1 or max_bins > 5000:
        raise _param_error("max_bins must be between 1 and 5000.", {"max_bins": max_bins})
    max_neighbors_total = _int_param(params, "max_neighbors_total", 200000)
    if max_neighbors_total < 1 or max_neighbors_total > 2000000:
        raise _param_error("max_neighbors_total must be between 1 and 2000000.", {"max_neighbors_total": max_neighbors_total})
    bin_count = int(math.ceil(r_max / bin_width))
    if bin_count > max_bins:
        raise ToolExecutionError(
            code="TOOL_PARAM_INVALID",
            message="RDF bin count exceeds max_bins.",
            tool_id=RdfAdapter.tool_id,
            details={
                "errorType": "RDF_BIN_LIMIT_EXCEEDED",
                "bin_count": bin_count,
                "max_bins": max_bins,
                "r_max_angstrom": r_max,
                "bin_width_angstrom": bin_width,
            },
        )
    plot_kind = str(params.get("plot_kind", "line"))
    if plot_kind != "line":
        raise _param_error("structure.rdf only supports plot_kind=line.", {"plot_kind": plot_kind})
    return {
        "r_max_angstrom": _round(r_max),
        "bin_width_angstrom": _round(bin_width),
        "normalization": normalization,
        "include_partial_pairs": bool(params.get("include_partial_pairs", True)),
        "max_partial_pairs": max_partial_pairs,
        "max_sites": max_sites,
        "max_bins": max_bins,
        "max_neighbors_total": max_neighbors_total,
        "plot_kind": plot_kind,
    }


def _radial_bins(params: dict[str, Any]) -> tuple[list[float], list[float]]:
    bin_count = int(math.ceil(float(params["r_max_angstrom"]) / float(params["bin_width_angstrom"])))
    width = float(params["bin_width_angstrom"])
    edges = [_round(index * width) for index in range(bin_count + 1)]
    centers = [_round((float(edges[index]) + float(edges[index + 1])) / 2.0) for index in range(bin_count)]
    return edges, centers


def _structure_rdf_record(
    label: str,
    structure: Structure,
    *,
    params: dict[str, Any],
    bin_edges: list[float],
    bin_centers: list[float],
) -> dict[str, Any]:
    warnings: list[str] = []
    pbc = [bool(item) for item in getattr(structure, "pbc", (True, True, True))]
    if pbc != [True, True, True]:
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message="structure.rdf requires pbc == [true, true, true].",
            tool_id=RdfAdapter.tool_id,
            details={"errorType": "RDF_NON_PERIODIC_STRUCTURE", "structure": label, "pbc": pbc},
        )
    volume = float(getattr(structure, "volume", 0.0) or 0.0)
    if volume <= 0.0:
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message="structure.rdf requires a positive lattice volume.",
            tool_id=RdfAdapter.tool_id,
            details={"errorType": "RDF_INVALID_LATTICE_VOLUME", "structure": label, "volume": volume},
        )
    site_count = len(structure)
    if site_count > int(params["max_sites"]):
        raise ToolExecutionError(
            code="TOOL_RESOURCE_LIMIT",
            message="Structure exceeds max_sites for structure.rdf.",
            tool_id=RdfAdapter.tool_id,
            details={"errorType": "RDF_SITE_LIMIT_EXCEEDED", "structure": label, "site_count": site_count, "max_sites": params["max_sites"]},
        )

    species = _elements(structure)
    species_counts = {element: 0 for element in species}
    for site in structure:
        species_counts[_site_element(site)] = species_counts.get(_site_element(site), 0) + 1

    bin_count = len(bin_centers)
    global_counts = [0 for _ in range(bin_count)]
    partial_counts: dict[tuple[str, str], list[int]] = {
        (center, neighbor): [0 for _ in range(bin_count)]
        for center in species
        for neighbor in species
    }
    neighbor_records: list[dict[str, Any]] = []
    neighbors_by_site = structure.get_all_neighbors(float(params["r_max_angstrom"]))
    for center_index, neighbors in enumerate(neighbors_by_site):
        center_element = _site_element(structure[center_index])
        for neighbor in neighbors:
            distance = float(getattr(neighbor, "nn_distance", getattr(neighbor, "distance", 0.0)) or 0.0)
            if distance <= 1e-12 or distance > float(params["r_max_angstrom"]):
                continue
            neighbor_index = int(getattr(neighbor, "index", -1))
            neighbor_element = _site_element(structure[neighbor_index]) if 0 <= neighbor_index < len(structure) else str(neighbor.species_string)
            image = _image_tuple(getattr(neighbor, "image", None))
            neighbor_records.append(
                {
                    "center_index": center_index,
                    "center_element": center_element,
                    "neighbor_index": neighbor_index,
                    "neighbor_element": neighbor_element,
                    "distance": distance,
                    "image": image,
                }
            )
            if len(neighbor_records) > int(params["max_neighbors_total"]):
                raise ToolExecutionError(
                    code="TOOL_RESOURCE_LIMIT",
                    message="RDF periodic neighbor count exceeds max_neighbors_total.",
                    tool_id=RdfAdapter.tool_id,
                    details={
                        "errorType": "RDF_NEIGHBOR_LIMIT_EXCEEDED",
                        "structure": label,
                        "max_neighbors_total": params["max_neighbors_total"],
                    },
                )
    neighbor_records.sort(
        key=lambda item: (
            int(item["center_index"]),
            _round(float(item["distance"])),
            int(item["neighbor_index"]),
            tuple(item["image"]),
            str(item["neighbor_element"]),
        )
    )
    width = float(params["bin_width_angstrom"])
    for record in neighbor_records:
        bin_index = min(int(math.floor(float(record["distance"]) / width)), bin_count - 1)
        global_counts[bin_index] += 1
        key = (str(record["center_element"]), str(record["neighbor_element"]))
        partial_counts.setdefault(key, [0 for _ in range(bin_count)])[bin_index] += 1

    global_denominators = _denominators(
        bin_edges=bin_edges,
        center_site_count=site_count,
        neighbor_site_count=site_count,
        volume=volume,
    )
    partial_denominators = {
        pair: _denominators(
            bin_edges=bin_edges,
            center_site_count=species_counts[pair[0]],
            neighbor_site_count=species_counts[pair[1]],
            volume=volume,
        )
        for pair in partial_counts
    }
    return {
        "structureId": label,
        "formula": structure.composition.reduced_formula,
        "site_count": site_count,
        "species": species,
        "pbc": pbc,
        "volume_angstrom3": _round(volume),
        "global_counts": global_counts,
        "global_denominators": global_denominators,
        "partial_counts": partial_counts,
        "partial_denominators": partial_denominators,
        "neighbor_count": len(neighbor_records),
        "species_counts": species_counts,
        "warnings": _dedupe(warnings),
    }


def _payload(
    adapter: RdfAdapter,
    *,
    prepared: PreparedStructures,
    params: dict[str, Any],
    records: list[dict[str, Any]],
    bin_edges: list[float],
    bin_centers: list[float],
) -> dict[str, Any]:
    warnings = list(prepared.warnings)
    warnings.extend(
        [
            "RDF_NORMALIZATION_NUMBER_DENSITY_ONLY",
            "RDF_CUTOFF_SENSITIVE",
            "RDF_BIN_WIDTH_SENSITIVE",
            "RDF_PERIODIC_IMAGES_REQUIRED",
            "RDF_LARGE_STRUCTURE_DEFERRED",
            "RDF_BROWSER_EVIDENCE_DEFERRED",
            "RDF_NOT_EXPERIMENTAL_PDF_FITTING",
            "RDF_NO_PHONON_DOS",
        ]
    )
    for record in records:
        warnings.extend(record["warnings"])

    bin_count = len(bin_centers)
    global_counts = [sum(int(record["global_counts"][index]) for record in records) for index in range(bin_count)]
    global_denominators = [
        sum(float(record["global_denominators"][index]) for record in records)
        for index in range(bin_count)
    ]
    global_g = [_round(global_counts[index] / global_denominators[index]) if global_denominators[index] > 0 else 0.0 for index in range(bin_count)]

    partial_pair_keys = sorted({pair for record in records for pair in record["partial_counts"]})
    partial_pair_count_before_limit = len(partial_pair_keys)
    partial_truncated = bool(params["include_partial_pairs"]) and partial_pair_count_before_limit > int(params["max_partial_pairs"])
    if partial_truncated:
        warnings.append(f"RDF_PARTIAL_PAIRS_TRUNCATED: retained {params['max_partial_pairs']} of {partial_pair_count_before_limit} ordered pairs.")
    if not bool(params["include_partial_pairs"]):
        partial_pair_keys = []
    else:
        partial_pair_keys = partial_pair_keys[: int(params["max_partial_pairs"])]

    partial_rdf = []
    for center, neighbor in partial_pair_keys:
        counts = [
            sum(int(record["partial_counts"].get((center, neighbor), [0] * bin_count)[index]) for record in records)
            for index in range(bin_count)
        ]
        denominators = [
            sum(float(record["partial_denominators"].get((center, neighbor), [0.0] * bin_count)[index]) for record in records)
            for index in range(bin_count)
        ]
        partial_rdf.append(
            {
                "center_element": center,
                "neighbor_element": neighbor,
                "r_angstrom": bin_centers,
                "g_r": [_round(counts[index] / denominators[index]) if denominators[index] > 0 else 0.0 for index in range(bin_count)],
                "counts": counts,
            }
        )

    first = records[0]
    total_site_count = sum(int(record["site_count"]) for record in records)
    total_volume = sum(float(record["volume_angstrom3"]) for record in records)
    total_neighbor_count = sum(int(record["neighbor_count"]) for record in records)
    payload = {
        "artifactType": adapter.tool_id,
        "schema_version": "phase10e7.rdf.v1",
        "tool_id": adapter.tool_id,
        "source": _source_payload(adapter.context),
        "structureCount": len(records),
        "structures": [
            {
                "structureId": record["structureId"],
                "formula": record["formula"],
                "site_count": record["site_count"],
                "species": record["species"],
                "pbc": record["pbc"],
                "volume_angstrom3": record["volume_angstrom3"],
                "neighbor_count": record["neighbor_count"],
            }
            for record in records
        ],
        "structure": {
            "formula": first["formula"],
            "site_count": total_site_count,
            "species": sorted({element for record in records for element in record["species"]}),
            "pbc": first["pbc"],
            "volume_angstrom3": _round(total_volume),
        },
        "parameters": params,
        "rdf": {
            "r_angstrom": bin_centers,
            "g_r": global_g,
            "counts": global_counts,
            "bin_edges_angstrom": bin_edges,
            "normalization": {
                "method": "number_density",
                "center_site_count": total_site_count,
                "neighbor_site_count": total_site_count,
                "number_density_per_angstrom3": _round(total_site_count / total_volume) if total_volume > 0 else 0.0,
            },
        },
        "partial_rdf": partial_rdf,
        "limits": {
            "max_sites": params["max_sites"],
            "max_bins": params["max_bins"],
            "max_neighbors_total": params["max_neighbors_total"],
            "max_partial_pairs": params["max_partial_pairs"],
            "site_count_before_limit": total_site_count,
            "bin_count": bin_count,
            "neighbor_count": total_neighbor_count,
            "partial_pair_count": len(partial_rdf),
            "partial_pair_count_before_limit": partial_pair_count_before_limit,
            "truncated": partial_truncated,
        },
        "warnings": _dedupe(warnings),
        "security": _security_payload(),
    }
    return payload


def _denominators(
    *,
    bin_edges: list[float],
    center_site_count: int,
    neighbor_site_count: int,
    volume: float,
) -> list[float]:
    if center_site_count <= 0 or neighbor_site_count <= 0 or volume <= 0.0:
        return [0.0 for _ in range(len(bin_edges) - 1)]
    density = neighbor_site_count / volume
    denominators = []
    for index in range(len(bin_edges) - 1):
        inner = float(bin_edges[index])
        outer = float(bin_edges[index + 1])
        shell_volume = (4.0 * math.pi / 3.0) * (outer**3 - inner**3)
        denominators.append(float(center_site_count) * density * shell_volume)
    return denominators


def _plot_payload(payload: dict[str, Any]) -> dict[str, Any]:
    x_values = [float(item) for item in payload["rdf"]["r_angstrom"]]
    y_values = [float(item) for item in payload["rdf"]["g_r"]]
    series = [{"name": "All pairs", "x": x_values, "y": y_values}]
    for partial in payload.get("partial_rdf") or []:
        series.append(
            {
                "name": f"{partial['center_element']}->{partial['neighbor_element']}",
                "x": [float(item) for item in partial["r_angstrom"]],
                "y": [float(item) for item in partial["g_r"]],
            }
        )
    return {
        "artifactType": "structure.rdf_plot",
        "schema_version": "phase10e7.static_chart.v1",
        "tool_id": "structure.rdf",
        "chart_type": "line",
        "title": "Radial Distribution Function",
        "x_axis": {"label": "r (angstrom)", "values": x_values},
        "y_axis": {"label": "g(r)", "values": y_values},
        "series": series,
        "metadata": {
            "formula": payload["structure"]["formula"],
            "site_count": payload["structure"]["site_count"],
            "r_max_angstrom": payload["parameters"]["r_max_angstrom"],
            "bin_width_angstrom": payload["parameters"]["bin_width_angstrom"],
            "normalization": payload["parameters"]["normalization"],
            "partial_pair_count": payload["limits"]["partial_pair_count"],
        },
        "security": _security_payload(),
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    first_peak = "none"
    if payload["rdf"]["g_r"]:
        peak_index = max(range(len(payload["rdf"]["g_r"])), key=lambda index: (float(payload["rdf"]["g_r"][index]), -index))
        if float(payload["rdf"]["g_r"][peak_index]) > 0.0:
            first_peak = f"r={payload['rdf']['r_angstrom'][peak_index]} angstrom, g(r)={payload['rdf']['g_r'][peak_index]}"
    warnings = payload.get("warnings") or []
    lines = [
        "# Radial Distribution Function",
        "",
        "## Input",
        f"- source: {payload['source']['resource_type']}",
        f"- parser: {payload['source']['parser']}",
        f"- formula: {payload['structure']['formula']}",
        f"- site count: {payload['structure']['site_count']}",
        f"- periodic: {all(bool(item) for item in payload['structure']['pbc'])}",
        f"- volume: {payload['structure']['volume_angstrom3']} angstrom^3",
        "",
        "## Method",
        f"- r max: {payload['parameters']['r_max_angstrom']} angstrom",
        f"- bin width: {payload['parameters']['bin_width_angstrom']} angstrom",
        f"- normalization: {payload['parameters']['normalization']}",
        "- periodic-image policy: pymatgen periodic neighbors with pbc == [true, true, true]",
        f"- partial RDF: {payload['parameters']['include_partial_pairs']}",
        f"- resource caps: max_sites={payload['limits']['max_sites']}, max_bins={payload['limits']['max_bins']}, max_neighbors_total={payload['limits']['max_neighbors_total']}",
        "",
        "## Results",
        f"- bin count: {payload['limits']['bin_count']}",
        f"- first peak: {first_peak}",
        f"- partial pairs: {payload['limits']['partial_pair_count']}",
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


def _recipe_payload(adapter: RdfAdapter, params: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    context = adapter.context
    return {
        "schema_version": "phase10e7.recipe.v1",
        "schemaVersion": "0.1",
        "recipeId": f"recipe_{context.tool_call_id}",
        "name": "Radial Distribution Function",
        "tool_id": adapter.tool_id,
        "toolId": adapter.tool_id,
        "inputs": {
            "dataset_id": context.dataset_id,
            "input_hashes": adapter._input_hashes,
        },
        "params": params,
        "steps": [
            "parse_structure",
            "validate_periodic_structure",
            "validate_lattice_volume",
            "validate_rdf_params",
            "build_radial_bins",
            "collect_periodic_neighbors",
            "count_global_distances",
            "normalize_by_number_density",
            "aggregate_partial_pairs",
            "round_numeric_values",
            "write_rdf_json",
            "write_static_chart_json",
            "write_summary",
        ],
        "deterministic": True,
        "dependencies": {
            "new_dependencies_added": False,
            **BaseToolAdapter.dependency_versions(),
        },
        "artifactTypes": ["table_json", "plotly_json", "summary_md", "recipe_json"],
        "artifacts": ["rdf.json", "rdf_plot.json", "summary.md", "recipe.json"],
        "numericTolerance": {
            "r_rounding_decimals": 6,
            "g_r_rounding_decimals": 6,
            "density_rounding_decimals": 6,
            "bin_assignment": "floor(distance / bin_width), final bin includes r_max",
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


def _site_element(site: Any) -> str:
    try:
        return str(site.specie.symbol)
    except Exception:
        try:
            elements = site.species.elements
            return str(elements[0].symbol) if elements else str(site.species_string)
        except Exception:
            return str(site.species_string)


def _image_tuple(value: Any) -> tuple[int | float, ...]:
    if value is None:
        return ()
    try:
        return tuple(int(component) for component in value)
    except Exception:
        try:
            return tuple(_round(float(component)) for component in value)
        except Exception:
            return ()


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
        tool_id=RdfAdapter.tool_id,
        details={"errorType": "RDF_INVALID_PARAMS", **details},
    )
