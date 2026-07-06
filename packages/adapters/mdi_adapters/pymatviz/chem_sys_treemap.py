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
    treemap_figure,
)
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


@dataclass(frozen=True)
class ChemSysTreemapResult:
    metadata: dict[str, Any]
    figure: Any
    params: dict[str, Any]


class ChemSysTreemapAdapter(BaseToolAdapter):
    tool_id = "composition.chem_sys_treemap"
    adapter_version = "0.2.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> FormulaStats:
        if not self._resolved_inputs:
            raise ToolExecutionError(
                "TOOL_INPUT_INVALID",
                "chem_sys_treemap requires table or formula input.",
                self.tool_id,
                details={"errorType": "unsupported_profile_type"},
            )
        prepared = prepare_composition_input(self._resolved_inputs[0], {**params, "_toolId": self.tool_id}, tool_id=self.tool_id)
        return formula_statistics(prepared, params, tool_id=self.tool_id)

    def run(self, prepared: FormulaStats, params: dict[str, Any]) -> ChemSysTreemapResult:
        group_mode = str(params.get("groupMode") or "chem_sys")
        if group_mode not in {"chem_sys", "arity", "reduced_formula"}:
            raise ToolExecutionError(
                "TOOL_PARAM_INVALID",
                f"Unsupported groupMode: {group_mode}",
                self.tool_id,
                details={"errorType": "unsupported_group_mode", "groupMode": group_mode},
            )
        max_groups = max(1, int(params.get("maxGroups") or params.get("maxCells") or 50))
        groups = _group_records(prepared, group_mode)[:max_groups]
        if len(groups) == max_groups and len(_group_records(prepared, group_mode)) > max_groups:
            prepared.payload["warnings"].append("too_many_groups_warning")
        try:
            figure = pmv.chem_sys_treemap(
                formula_list(prepared.parsed),
                group_by="chem_sys" if group_mode == "chem_sys" else "formula",
                max_cells=max_groups,
                show_counts=params.get("showCounts", "value"),
            )
            figure.update_layout(title_text=params.get("title") or "Chemical System Treemap")
        except Exception:
            figure = treemap_figure(
                [group["label"] for group in groups],
                ["" for _ in groups],
                [group["count"] for group in groups],
                title=str(params.get("title") or "Chemical System Treemap"),
            )
        metadata = {
            "artifactType": "composition.chem_sys_treemap",
            "chartType": "treemap",
            "formulaColumn": prepared.payload["formulaColumn"],
            "groupMode": group_mode,
            "groups": groups,
            "plotlyFigure": plotly_metadata(figure),
            "formulaCount": prepared.payload["formulaCount"],
            "parsedFormulaCount": prepared.payload["parsedFormulaCount"],
            "failedFormulaCount": prepared.payload["failedFormulaCount"],
            "warnings": list(prepared.payload.get("warnings", [])),
        }
        return ChemSysTreemapResult(metadata=metadata, figure=figure, params=params)

    def export(self, result: ChemSysTreemapResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        return export_composition_payloads(
            self,
            metadata=result.metadata,
            figure=result.figure,
            params=result.params,
            artifact_types=artifact_types,
            json_name="chem_sys_treemap.json",
            title="Chemical System Treemap",
            provenance={
                "sourceFunction": "pymatviz.chem_sys_treemap",
                "adapter": self.tool_id,
                "formulaColumn": result.metadata["formulaColumn"],
                "groupMode": result.metadata["groupMode"],
            },
        )


def _group_records(prepared: FormulaStats, group_mode: str) -> list[dict[str, Any]]:
    counts: dict[str, dict[str, Any]] = {}
    for item in prepared.parsed:
        if group_mode == "arity":
            label = arity_label(item.arity)
        elif group_mode == "reduced_formula":
            label = item.reduced_formula
        else:
            label = item.chemical_system
        if label not in counts:
            counts[label] = {"label": label, "count": 0, "arity": item.arity}
        counts[label]["count"] += 1
    total = sum(item["count"] for item in counts.values()) or 1
    return [
        {
            "label": item["label"],
            "count": int(item["count"]),
            "fraction": float(item["count"]) / total,
            "arity": int(item["arity"]),
        }
        for item in sorted(counts.values(), key=lambda row: (-row["count"], row["label"]))
    ]
