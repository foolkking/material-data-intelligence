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
    formula_list,
    formula_statistics,
    normalize_count_mode,
    plotly_metadata,
    prepare_composition_input,
    simple_bar_figure,
)
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


@dataclass(frozen=True)
class ElementsHistResult:
    metadata: dict[str, Any]
    figure: Any
    params: dict[str, Any]


class ElementsHistAdapter(BaseToolAdapter):
    tool_id = "composition.elements_hist"
    adapter_version = "0.2.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> FormulaStats:
        if not self._resolved_inputs:
            raise ToolExecutionError(
                "TOOL_INPUT_INVALID",
                "elements_hist requires table or formula input.",
                self.tool_id,
                details={"errorType": "unsupported_profile_type"},
            )
        prepared = prepare_composition_input(self._resolved_inputs[0], {**params, "_toolId": self.tool_id}, tool_id=self.tool_id)
        return formula_statistics(prepared, params, tool_id=self.tool_id)

    def run(self, prepared: FormulaStats, params: dict[str, Any]) -> ElementsHistResult:
        try:
            count_mode = normalize_count_mode(params.get("countMode") or "occurrence")
        except ValueError as exc:
            raise ToolExecutionError(
                "TOOL_PARAM_INVALID",
                str(exc),
                self.tool_id,
                details={"errorType": "unsupported_count_mode"},
            ) from exc

        values = element_value_map(prepared.parsed, mode=count_mode)
        top_n = max(1, int(params.get("topN") or params.get("keepTop") or 30))
        ordered = sorted(values.items(), key=lambda item: (-item[1], item[0]))[:top_n]
        total = sum(value for _, value in ordered) or 1.0
        bars = [
            {"element": element, "count": float(count), "fraction": float(count) / total}
            for element, count in ordered
        ]

        try:
            pymatviz_mode = {
                "occurrence": "occurrence",
                "stoichiometric": "composition",
                "fractional": "fractional_composition",
            }[count_mode]
            figure = pmv.elements_hist(
                formula_list(prepared.parsed),
                count_mode=pymatviz_mode,
                keep_top=top_n,
                log_y=bool(params.get("logY", False)),
                show_values=params.get("showValues", "percent"),
            )
            figure.update_layout(title_text=params.get("title") or "Element Histogram")
        except Exception:
            figure = simple_bar_figure(
                [item["element"] for item in bars],
                [item["count"] for item in bars],
                title=str(params.get("title") or "Element Histogram"),
                x_title="Element",
                y_title=count_mode,
            )

        metadata = {
            "artifactType": "composition.elements_hist",
            "chartType": "bar",
            "formulaColumn": prepared.payload["formulaColumn"],
            "countMode": count_mode,
            "elementCount": len(values),
            "bars": bars,
            "plotlyFigure": plotly_metadata(figure),
            "formulaCount": prepared.payload["formulaCount"],
            "parsedFormulaCount": prepared.payload["parsedFormulaCount"],
            "failedFormulaCount": prepared.payload["failedFormulaCount"],
            "warnings": list(prepared.payload.get("warnings", [])),
        }
        return ElementsHistResult(metadata=metadata, figure=figure, params=params)

    def export(self, result: ElementsHistResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        return export_composition_payloads(
            self,
            metadata=result.metadata,
            figure=result.figure,
            params=result.params,
            artifact_types=artifact_types,
            json_name="elements_hist.json",
            title="Element Histogram",
            provenance={
                "sourceFunction": "pymatviz.elements_hist",
                "adapter": self.tool_id,
                "formulaColumn": result.metadata["formulaColumn"],
                "countMode": result.metadata["countMode"],
            },
        )
