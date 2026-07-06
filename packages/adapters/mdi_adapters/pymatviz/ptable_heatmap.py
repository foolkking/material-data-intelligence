from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pymatviz as pmv
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..composition_common import (
    FormulaStats,
    element_value_map,
    export_composition_payloads,
    formula_statistics,
    plotly_metadata,
    prepare_composition_input,
)
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


@dataclass(frozen=True)
class PTableHeatmapResult:
    metadata: dict[str, Any]
    figure: Any
    params: dict[str, Any]


class PTableHeatmapAdapter(BaseToolAdapter):
    tool_id = "composition.ptable_heatmap"
    adapter_version = "0.2.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> FormulaStats:
        if not self._resolved_inputs:
            raise ToolExecutionError(
                "TOOL_INPUT_INVALID",
                "ptable_heatmap requires table or formula input.",
                self.tool_id,
                details={"errorType": "unsupported_profile_type"},
            )
        prepared = prepare_composition_input(self._resolved_inputs[0], {**params, "_toolId": self.tool_id}, tool_id=self.tool_id)
        return formula_statistics(prepared, params, tool_id=self.tool_id)

    def run(self, prepared: FormulaStats, params: dict[str, Any]) -> PTableHeatmapResult:
        count_mode = str(params.get("countMode") or "occurrence")
        try:
            values = element_value_map(prepared.parsed, mode=count_mode)
        except ValueError as exc:
            raise ToolExecutionError(
                "TOOL_PARAM_INVALID",
                str(exc),
                self.tool_id,
                details={"errorType": "unsupported_count_mode"},
            ) from exc

        use_log = bool(params.get("log", False))
        figure = pmv.ptable_heatmap(values, log=use_log, colorscale=params.get("colorScale", "viridis"))
        figure.update_layout(title_text=params.get("title") or "Periodic Table Heatmap")
        metadata = {
            "artifactType": "composition.ptable_heatmap",
            "chartType": "periodic_table_heatmap",
            "formulaColumn": prepared.payload["formulaColumn"],
            "countMode": count_mode,
            "log": use_log,
            "elementValues": values,
            "elementCount": len(values),
            "formulaCount": prepared.payload["formulaCount"],
            "parsedFormulaCount": prepared.payload["parsedFormulaCount"],
            "failedFormulaCount": prepared.payload["failedFormulaCount"],
            "plotlyFigure": plotly_metadata(figure),
            "warnings": list(prepared.payload.get("warnings", [])),
        }
        return PTableHeatmapResult(metadata=metadata, figure=figure, params=params)

    def export(self, result: PTableHeatmapResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        return export_composition_payloads(
            self,
            metadata=result.metadata,
            figure=result.figure,
            params=result.params,
            artifact_types=artifact_types,
            json_name="figure.json",
            title="Periodic Table Heatmap",
            provenance={
                "sourceFunction": "pymatviz.ptable_heatmap",
                "adapter": self.tool_id,
                "formulaColumn": result.metadata["formulaColumn"],
                "countMode": result.metadata["countMode"],
            },
        )
