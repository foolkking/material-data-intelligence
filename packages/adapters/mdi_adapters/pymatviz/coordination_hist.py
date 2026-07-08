from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pymatgen.core import Structure

from mdi_artifact_core import ArtifactPayload, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..errors import ToolExecutionError
from ..platform_builtin.structure import PreparedStructures, _BaseStructureAdapter, _dedupe, _elements, _round


@dataclass(frozen=True)
class CoordinationHistResult:
    payload: dict[str, Any]
    plot_payload: dict[str, Any]
    summary: str
    recipe: dict[str, Any]
    params: dict[str, Any]


class CoordinationHistAdapter(_BaseStructureAdapter):
    tool_id = "structure.coordination_hist"
    adapter_version = "0.1.0"

    def run(self, prepared: PreparedStructures, params: dict[str, Any]) -> CoordinationHistResult:
        normalized = _coordination_params(params)
        records = [
            _structure_coordination_record(label, structure, params=normalized)
            for label, structure in sorted(prepared.structures.items())
        ]
        warnings = list(prepared.warnings)
        warnings.append("COORDINATION_NEIGHBOR_POLICY_DISTANCE_CUTOFF_ONLY")
        warnings.append("COORDINATION_CUTOFF_SENSITIVE")
        warnings.append("COORDINATION_ADVANCED_ENVIRONMENT_CLASSIFICATION_NOT_PERFORMED")
        for record in records:
            warnings.extend(record["warnings"])

        site_details = [
            detail
            for record in records
            for detail in record["site_details"]
        ] if normalized["include_site_details"] else []
        all_coordination_numbers = [
            int(detail["coordination_number"])
            for record in records
            for detail in record["site_details"]
        ]
        histogram = _histogram_bins(all_coordination_numbers)
        by_element = _by_element_bins(records) if normalized["group_by_element"] else []
        pair_counts = _pair_counts(records) if normalized["include_pair_counts"] else []
        first = records[0]
        site_count_before_truncation = sum(int(record["limits"]["site_count_before_truncation"]) for record in records)
        truncated = any(bool(record["limits"]["truncated"]) for record in records)
        payload = {
            "artifactType": self.tool_id,
            "schema_version": "phase10e1.coordination_hist.v1",
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
                }
                for record in records
            ],
            "structure": {
                "formula": first["formula"],
                "site_count": sum(int(record["site_count"]) for record in records),
                "species": sorted({element for record in records for element in record["species"]}),
                "pbc": first["pbc"],
            },
            "parameters": normalized,
            "histogram": {
                "bins": histogram,
                "total_sites": len(all_coordination_numbers),
            },
            "by_element": by_element,
            "pair_counts": pair_counts,
            "site_details": site_details,
            "limits": {
                "max_sites": normalized["max_sites"],
                "max_neighbors_per_site": normalized["max_neighbors_per_site"],
                "site_count_before_truncation": site_count_before_truncation,
                "truncated": truncated,
            },
            "warnings": _dedupe(warnings),
            "security": _security_payload(),
        }
        plot_payload = _plot_payload(payload)
        summary = _summary_markdown(payload)
        recipe = _recipe_payload(self, normalized, payload)
        return CoordinationHistResult(
            payload=payload,
            plot_payload=plot_payload,
            summary=summary,
            recipe=recipe,
            params=normalized,
        )

    def export(self, result: CoordinationHistResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
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
                    file_name="coordination_hist.json",
                    content=stable_json_dumps(result.payload),
                    media_type="application/json",
                )
            )
        if ArtifactType.plotly_json in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.plotly_json,
                    file_name="coordination_hist_plot.json",
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
                "neighborPolicy": result.params["neighbor_policy"],
                "cutoffAngstrom": result.params["cutoff_angstrom"],
                "staticPhysics": True,
                "browserApiEvidence": "deferred_to_phase10e2",
            },
        )


def _coordination_params(params: dict[str, Any]) -> dict[str, Any]:
    policy = str(params.get("neighbor_policy", "distance_cutoff"))
    if policy != "distance_cutoff":
        raise ToolExecutionError(
            code="TOOL_PARAM_INVALID",
            message="structure.coordination_hist only supports neighbor_policy=distance_cutoff in Phase 10E-1.",
            tool_id=CoordinationHistAdapter.tool_id,
            details={"errorType": "COORDINATION_HIST_INVALID_PARAMS", "neighbor_policy": policy},
        )
    cutoff = _float_param(params, "cutoff_angstrom", 3.0)
    if cutoff < 0.1 or cutoff > 10.0:
        raise ToolExecutionError(
            code="TOOL_PARAM_INVALID",
            message="cutoff_angstrom must be between 0.1 and 10.0.",
            tool_id=CoordinationHistAdapter.tool_id,
            details={"errorType": "COORDINATION_HIST_INVALID_PARAMS", "cutoff_angstrom": cutoff},
        )
    max_sites = _int_param(params, "max_sites", 500)
    if max_sites < 1 or max_sites > 5000:
        raise ToolExecutionError(
            code="TOOL_PARAM_INVALID",
            message="max_sites must be between 1 and 5000.",
            tool_id=CoordinationHistAdapter.tool_id,
            details={"errorType": "COORDINATION_HIST_INVALID_PARAMS", "max_sites": max_sites},
        )
    max_neighbors = _int_param(params, "max_neighbors_per_site", 128)
    if max_neighbors < 0 or max_neighbors > 1000:
        raise ToolExecutionError(
            code="TOOL_PARAM_INVALID",
            message="max_neighbors_per_site must be between 0 and 1000.",
            tool_id=CoordinationHistAdapter.tool_id,
            details={"errorType": "COORDINATION_HIST_INVALID_PARAMS", "max_neighbors_per_site": max_neighbors},
        )
    plot_kind = str(params.get("plot_kind", "bar"))
    if plot_kind != "bar":
        raise ToolExecutionError(
            code="TOOL_PARAM_INVALID",
            message="structure.coordination_hist only supports plot_kind=bar.",
            tool_id=CoordinationHistAdapter.tool_id,
            details={"errorType": "COORDINATION_HIST_INVALID_PARAMS", "plot_kind": plot_kind},
        )
    return {
        "neighbor_policy": policy,
        "cutoff_angstrom": _round(cutoff),
        "max_sites": max_sites,
        "max_neighbors_per_site": max_neighbors,
        "include_site_details": bool(params.get("include_site_details", True)),
        "group_by_element": bool(params.get("group_by_element", True)),
        "include_pair_counts": bool(params.get("include_pair_counts", True)),
        "plot_kind": plot_kind,
    }


def _structure_coordination_record(label: str, structure: Structure, *, params: dict[str, Any]) -> dict[str, Any]:
    warnings: list[str] = []
    max_sites = int(params["max_sites"])
    site_count = len(structure)
    selected_count = min(site_count, max_sites)
    if site_count > selected_count:
        warnings.append(f"COORDINATION_SITES_TRUNCATED: retained {selected_count} of {site_count} sites.")
    details: list[dict[str, Any]] = []
    for site_index in range(selected_count):
        site = structure[site_index]
        neighbors = []
        for neighbor in structure.get_neighbors(site, float(params["cutoff_angstrom"])):
            neighbor_index = int(getattr(neighbor, "index", -1))
            distance = _round(float(getattr(neighbor, "nn_distance", getattr(neighbor, "distance", 0.0))))
            if neighbor_index == site_index and distance == 0.0:
                continue
            neighbors.append(
                {
                    "index": neighbor_index,
                    "distance": distance,
                    "element": _site_element(structure[neighbor_index]) if 0 <= neighbor_index < len(structure) else str(neighbor.species_string),
                }
            )
        neighbors.sort(key=lambda item: (item["distance"], item["index"], item["element"]))
        before_limit = len(neighbors)
        if before_limit > int(params["max_neighbors_per_site"]):
            warnings.append(
                f"COORDINATION_NEIGHBORS_TRUNCATED: site {site_index} retained {params['max_neighbors_per_site']} of {before_limit} neighbors."
            )
            neighbors = neighbors[: int(params["max_neighbors_per_site"])]
        if len(site.species) > 1:
            warnings.append("COORDINATION_PARTIAL_OCCUPANCY_PRESENT")
        details.append(
            {
                "structureId": label,
                "site_index": site_index,
                "element": _site_element(site),
                "coordination_number": len(neighbors),
                "neighbor_indices": [item["index"] for item in neighbors],
                "neighbor_elements": [item["element"] for item in neighbors],
                "neighbor_distances_angstrom": [item["distance"] for item in neighbors],
                "neighbor_count_before_truncation": before_limit,
            }
        )
    return {
        "structureId": label,
        "formula": structure.composition.reduced_formula,
        "site_count": site_count,
        "species": _elements(structure),
        "pbc": [bool(item) for item in getattr(structure, "pbc", (True, True, True))],
        "site_details": details,
        "limits": {
            "max_sites": max_sites,
            "max_neighbors_per_site": int(params["max_neighbors_per_site"]),
            "site_count_before_truncation": site_count,
            "truncated": site_count > selected_count or any(
                int(detail["neighbor_count_before_truncation"]) > int(params["max_neighbors_per_site"])
                for detail in details
            ),
        },
        "warnings": _dedupe(warnings),
    }


def _histogram_bins(values: list[int]) -> list[dict[str, Any]]:
    total = len(values)
    counts: dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return [
        {
            "coordination_number": coordination,
            "count": count,
            "fraction": _round(count / total) if total else 0.0,
        }
        for coordination, count in sorted(counts.items())
    ]


def _by_element_bins(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[int]] = {}
    for record in records:
        for detail in record["site_details"]:
            element = str(detail["element"])
            grouped.setdefault(element, []).append(int(detail["coordination_number"]))
    return [
        {
            "element": element,
            "bins": _histogram_bins(values),
            "total_sites": len(values),
        }
        for element, values in sorted(grouped.items())
    ]


def _pair_counts(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[tuple[str, str], int] = {}
    for record in records:
        for detail in record["site_details"]:
            center = str(detail["element"])
            for neighbor in detail["neighbor_elements"]:
                key = (center, str(neighbor))
                counts[key] = counts.get(key, 0) + 1
    return [
        {"center_element": center, "neighbor_element": neighbor, "count": count}
        for (center, neighbor), count in sorted(counts.items())
    ]


def _plot_payload(payload: dict[str, Any]) -> dict[str, Any]:
    bins = payload["histogram"]["bins"]
    x_values = [int(item["coordination_number"]) for item in bins]
    y_values = [int(item["count"]) for item in bins]
    series = [{"name": "All sites", "x": x_values, "y": y_values}]
    for element_group in payload.get("by_element") or []:
        series.append(
            {
                "name": str(element_group["element"]),
                "x": [int(item["coordination_number"]) for item in element_group["bins"]],
                "y": [int(item["count"]) for item in element_group["bins"]],
            }
        )
    return {
        "artifactType": "structure.coordination_hist_plot",
        "schema_version": "phase10e1.static_chart.v1",
        "tool_id": "structure.coordination_hist",
        "chart_type": "bar",
        "title": "Coordination Number Histogram",
        "x_axis": {"label": "Coordination Number", "values": x_values},
        "y_axis": {"label": "Site Count", "values": y_values},
        "series": series,
        "metadata": {
            "formula": payload["structure"]["formula"],
            "site_count": payload["structure"]["site_count"],
            "neighbor_policy": payload["parameters"]["neighbor_policy"],
            "cutoff_angstrom": payload["parameters"]["cutoff_angstrom"],
        },
        "security": _security_payload(),
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    dominant = "none"
    if payload["histogram"]["bins"]:
        top = max(payload["histogram"]["bins"], key=lambda item: (int(item["count"]), -int(item["coordination_number"])))
        dominant = f"{top['coordination_number']} ({top['count']} site(s))"
    warnings = payload.get("warnings") or []
    lines = [
        "# Coordination Histogram",
        "",
        "## Input",
        f"- source: {payload['source']['resource_type']}",
        f"- parser: {payload['source']['parser']}",
        f"- formula: {payload['structure']['formula']}",
        f"- site count: {payload['structure']['site_count']}",
        "",
        "## Method",
        f"- neighbor policy: {payload['parameters']['neighbor_policy']}",
        f"- cutoff: {payload['parameters']['cutoff_angstrom']} angstrom",
        f"- max sites: {payload['parameters']['max_sites']}",
        f"- max neighbors per site: {payload['parameters']['max_neighbors_per_site']}",
        "",
        "## Results",
        f"- histogram: {payload['histogram']['bins']}",
        f"- dominant coordination number: {dominant}",
        f"- element groups: {len(payload.get('by_element') or [])}",
        f"- pair counts: {len(payload.get('pair_counts') or [])}",
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


def _recipe_payload(adapter: CoordinationHistAdapter, params: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    context = adapter.context
    return {
        "schema_version": "phase10e1.recipe.v1",
        "schemaVersion": "0.1",
        "recipeId": f"recipe_{context.tool_call_id}",
        "name": "Coordination Histogram",
        "tool_id": adapter.tool_id,
        "toolId": adapter.tool_id,
        "inputs": {
            "dataset_id": context.dataset_id,
            "input_hashes": adapter._input_hashes,
        },
        "params": params,
        "steps": [
            "parse_structure",
            "normalize_sites",
            "apply_distance_cutoff_neighbor_policy",
            "count_neighbors_per_site",
            "aggregate_histogram",
            "aggregate_by_element",
            "write_coordination_hist_json",
            "write_static_chart_json",
            "write_summary",
        ],
        "deterministic": True,
        "dependencies": {
            "new_dependencies_added": False,
            **BaseToolAdapter.dependency_versions(),
        },
        "artifactTypes": ["table_json", "plotly_json", "summary_md", "recipe_json"],
        "artifacts": ["coordination_hist.json", "coordination_hist_plot.json", "summary.md", "recipe.json"],
        "numericTolerance": {
            "distance_rounding_decimals": 6,
            "neighbor_comparison": "distance <= cutoff_angstrom",
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


def _float_param(params: dict[str, Any], key: str, default: float) -> float:
    try:
        return float(params.get(key, default))
    except (TypeError, ValueError) as exc:
        raise ToolExecutionError(
            code="TOOL_PARAM_INVALID",
            message=f"{key} must be numeric.",
            tool_id=CoordinationHistAdapter.tool_id,
            details={"errorType": "COORDINATION_HIST_INVALID_PARAMS", key: params.get(key)},
        ) from exc


def _int_param(params: dict[str, Any], key: str, default: int) -> int:
    try:
        return int(params.get(key, default))
    except (TypeError, ValueError) as exc:
        raise ToolExecutionError(
            code="TOOL_PARAM_INVALID",
            message=f"{key} must be an integer.",
            tool_id=CoordinationHistAdapter.tool_id,
            details={"errorType": "COORDINATION_HIST_INVALID_PARAMS", key: params.get(key)},
        ) from exc
