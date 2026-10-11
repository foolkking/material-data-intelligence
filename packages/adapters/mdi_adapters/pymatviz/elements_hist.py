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
    adapter_version = "0.3.0"

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
        labels = [item["element"] for item in bars]
        counts = [item["count"] for item in bars]
        show_values = params.get("showValues", "percent")
        if isinstance(show_values, bool):
            show_values = "percent" if show_values else None
        if show_values not in ("percent", "count", None):
            raise ToolExecutionError("TOOL_PARAM_INVALID", "showValues must be percent, count, or a boolean.", self.tool_id)
        text = None if show_values is None else [
            f"{item['fraction']:.0%}" if show_values == "percent"
            else str(int(item["count"])) if item["count"].is_integer() else str(item["count"])
            for item in bars
        ]
        log_y = bool(params.get("logY", False))
        y_title = {"occurrence": "元素出现次数", "stoichiometric": "化学计量总数", "fractional": "分数贡献总和"}[count_mode]
        source_function = "pymatviz.elements_hist"

        try:
            # Counting, tie-breaking and top-N selection are already complete.
            # The library supplies styling, never a second scientific selection.
            figure = pmv.elements_hist(
                dict(ordered), log_y=log_y, show_values=None,
            )
        except Exception:
            figure = simple_bar_figure(
                labels, counts,
                title=str(params.get("title") or "Element Histogram"),
                x_title="Element",
                y_title=y_title,
            )
            source_function = "mdi_adapters.composition_common.simple_bar_figure"
        figure.update_traces(x=labels, y=counts, text=text, textposition="outside", width=0.7)
        figure.update_layout(
            title_text=params.get("title") or "Element Histogram", showlegend=False,
            xaxis={"type": "category", "categoryorder": "array", "categoryarray": labels, "title": "元素"},
            yaxis={"type": "log" if log_y else "linear", "title": f"{y_title}（对数刻度）" if log_y else y_title},
        )
        omitted = len(values) - len(bars)
        warnings = list(prepared.payload.get("warnings", []))
        if omitted:
            warnings.append(f"仅显示前 {len(bars)} 个元素，省略 {omitted} 个元素；百分比以显示元素的合计值为分母。")

        metadata = {
            "schemaVersion": "mdi.element-histogram/1.0",
            "artifactType": "composition.elements_hist",
            "chartType": "bar",
            "formulaColumn": prepared.payload["formulaColumn"],
            "countMode": count_mode,
            "elementCount": len(values),
            "omittedElementCount": omitted,
            "fractionScope": "displayed_elements",
            "totalElementValue": float(sum(values.values())),
            "retainedElementValue": float(sum(counts)),
            "showValues": show_values,
            "sourceFunction": source_function,
            "bars": bars,
            "plotlyFigure": plotly_metadata(figure),
            "formulaCount": prepared.payload["formulaCount"],
            "parsedFormulaCount": prepared.payload["parsedFormulaCount"],
            "failedFormulaCount": prepared.payload["failedFormulaCount"],
            "warnings": warnings,
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
                "sourceFunction": result.metadata["sourceFunction"],
                "adapter": self.tool_id,
                "formulaColumn": result.metadata["formulaColumn"],
                "countMode": result.metadata["countMode"],
            },
        )
