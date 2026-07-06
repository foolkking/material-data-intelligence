from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pymatviz as pmv
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..composition_common import (
    FormulaStats,
    arity_label,
    export_composition_payloads,
    formula_list,
    formula_statistics,
    plotly_metadata,
    prepare_composition_input,
    slug,
    sunburst_figure,
)
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


@dataclass(frozen=True)
class ChemSysSunburstResult:
    metadata: dict[str, Any]
    figure: Any
    params: dict[str, Any]


class ChemSysSunburstAdapter(BaseToolAdapter):
    tool_id = "composition.chem_sys_sunburst"
    adapter_version = "0.1.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> FormulaStats:
        if not self._resolved_inputs:
            raise ToolExecutionError(
                "TOOL_INPUT_INVALID",
                "chem_sys_sunburst requires table or formula input.",
                self.tool_id,
                details={"errorType": "unsupported_profile_type"},
            )
        prepared = prepare_composition_input(self._resolved_inputs[0], {**params, "_toolId": self.tool_id}, tool_id=self.tool_id)
        return formula_statistics(prepared, params, tool_id=self.tool_id)

    def run(self, prepared: FormulaStats, params: dict[str, Any]) -> ChemSysSunburstResult:
        hierarchy = [str(item) for item in params.get("hierarchy", ["arity", "chem_sys", "reduced_formula"])]
        invalid_levels = [item for item in hierarchy if item not in {"arity", "chem_sys", "reduced_formula"}]
        if invalid_levels:
            raise ToolExecutionError(
                "TOOL_PARAM_INVALID",
                f"Unsupported hierarchy levels: {invalid_levels}",
                self.tool_id,
                details={"errorType": "unsupported_hierarchy", "levels": invalid_levels},
            )
        max_leaf_nodes = max(1, int(params.get("maxLeafNodes") or 100))
        nodes, warnings = _sunburst_nodes(prepared, hierarchy, max_leaf_nodes=max_leaf_nodes)
        try:
            group_by = "reduced_formula" if "reduced_formula" in hierarchy else "chem_sys"
            figure = pmv.chem_sys_sunburst(
                formula_list(prepared.parsed),
                group_by=group_by,
                max_slices=max_leaf_nodes,
                show_counts="value",
            )
            figure.update_layout(title_text=params.get("title") or "Chemical System Sunburst")
        except Exception:
            figure = sunburst_figure(
                [node["id"] for node in nodes],
                [node["label"] for node in nodes],
                [node["parent"] for node in nodes],
                [node["count"] for node in nodes],
                title=str(params.get("title") or "Chemical System Sunburst"),
            )
        metadata = {
            "artifactType": "composition.chem_sys_sunburst",
            "chartType": "sunburst",
            "formulaColumn": prepared.payload["formulaColumn"],
            "hierarchy": hierarchy,
            "nodes": nodes,
            "plotlyFigure": plotly_metadata(figure),
            "formulaCount": prepared.payload["formulaCount"],
            "parsedFormulaCount": prepared.payload["parsedFormulaCount"],
            "failedFormulaCount": prepared.payload["failedFormulaCount"],
            "warnings": list(prepared.payload.get("warnings", [])) + warnings,
        }
        return ChemSysSunburstResult(metadata=metadata, figure=figure, params=params)

    def export(self, result: ChemSysSunburstResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        return export_composition_payloads(
            self,
            metadata=result.metadata,
            figure=result.figure,
            params=result.params,
            artifact_types=artifact_types,
            json_name="chem_sys_sunburst.json",
            title="Chemical System Sunburst",
            provenance={
                "sourceFunction": "pymatviz.chem_sys_sunburst",
                "adapter": self.tool_id,
                "formulaColumn": result.metadata["formulaColumn"],
                "hierarchy": result.metadata["hierarchy"],
            },
        )


def _sunburst_nodes(prepared: FormulaStats, hierarchy: list[str], *, max_leaf_nodes: int) -> tuple[list[dict[str, Any]], list[str]]:
    counts: dict[str, dict[str, Any]] = {}
    for item in prepared.parsed:
        parent = ""
        for level in hierarchy:
            if level == "arity":
                label = arity_label(item.arity)
            elif level == "chem_sys":
                label = item.chemical_system
            else:
                label = item.reduced_formula
            node_id = slug(f"{parent}/{level}:{label}" if parent else f"{level}:{label}")
            if node_id not in counts:
                counts[node_id] = {"id": node_id, "label": label, "parent": parent, "count": 0}
            counts[node_id]["count"] += 1
            parent = node_id

    nodes = sorted(counts.values(), key=lambda item: (item["parent"], item["label"]))
    warnings: list[str] = []
    leaf_nodes = [node for node in nodes if not any(other["parent"] == node["id"] for other in nodes)]
    if len(leaf_nodes) > max_leaf_nodes:
        warnings.append("too_many_leaf_nodes_warning")
        allowed_leaf_ids = {node["id"] for node in leaf_nodes[:max_leaf_nodes]}
        nodes = [node for node in nodes if node["id"] in allowed_leaf_ids or node["id"] not in {leaf["id"] for leaf in leaf_nodes}]
    return [
        {
            "id": str(node["id"]),
            "label": str(node["label"]),
            "parent": str(node["parent"]),
            "count": int(node["count"]),
        }
        for node in nodes
    ], warnings
