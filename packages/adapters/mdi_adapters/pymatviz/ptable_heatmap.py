from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pymatviz as pmv
from pymatgen.core import Composition

from mdi_artifact_core import ArtifactPayload
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError
from ..plotly_export import plotly_payloads


@dataclass
class PreparedPTableHeatmap:
    values: dict[str, float]
    mode: str
    n_inputs: int


class PTableHeatmapAdapter(BaseToolAdapter):
    tool_id = "composition.ptable_heatmap"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedPTableHeatmap:
        resolved = self._resolved_inputs
        if not resolved:
            raise ToolExecutionError("TOOL_INPUT_INVALID", "ptable_heatmap requires at least one input ref.", self.tool_id)

        raw = resolved[0] if len(resolved) == 1 else resolved
        values, mode, n_inputs = self._coerce_values(raw, params)
        if not values:
            raise ToolExecutionError("TOOL_INPUT_INVALID", "No element values could be derived from input.", self.tool_id)
        return PreparedPTableHeatmap(values=values, mode=mode, n_inputs=n_inputs)

    def run(self, prepared: PreparedPTableHeatmap, params: dict[str, Any]) -> dict[str, Any]:
        color_scale = params.get("colorScale", "viridis")
        title = params.get("title") or "Periodic Table Heatmap"
        fig = pmv.ptable_heatmap(prepared.values, colorscale=color_scale)
        fig.update_layout(title_text=title)
        return {"figure": fig, "prepared": prepared, "params": params}

    def export(self, result: dict[str, Any], artifact_types: list[ArtifactType]) -> list[Artifact]:
        prepared: PreparedPTableHeatmap = result["prepared"]
        params = result["params"]
        payloads = plotly_payloads(result["figure"], artifact_types)
        if ArtifactType.summary_md in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=(
                        "# Periodic Table Heatmap\n\n"
                        f"- Tool: `{self.tool_id}`\n"
                        f"- Input mode: `{prepared.mode}`\n"
                        f"- Input records: {prepared.n_inputs}\n"
                        f"- Elements with values: {len(prepared.values)}\n"
                    ),
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.recipe_json,
                    file_name="recipe.json",
                    content=self.recipe_payload(
                        name="Periodic Table Heatmap",
                        params=params,
                        artifact_types=artifact_types,
                    ),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={
                "sourceFunction": "pymatviz.ptable_heatmap",
                "adapterInputMode": prepared.mode,
                "pymatvizParamMap": {
                    "colorScale": "colorscale",
                    "normalize": "adapter-side element value normalization",
                    "countMode": "adapter-side composition aggregation",
                },
            },
        )

    def _coerce_values(self, raw: Any, params: dict[str, Any]) -> tuple[dict[str, float], str, int]:
        if isinstance(raw, dict) and "formulas" in raw:
            return self._aggregate_formulas(raw["formulas"], params)
        if isinstance(raw, dict) and "element_values" in raw:
            return self._normalize_if_requested(self._numeric_map(raw["element_values"]), params), "element_value_map", len(raw["element_values"])
        if isinstance(raw, dict) and self._looks_like_element_value_map(raw):
            return self._normalize_if_requested(self._numeric_map(raw), params), "element_value_map", len(raw)
        if isinstance(raw, (str, Composition)):
            return self._aggregate_formulas([raw], params)
        if isinstance(raw, (list, tuple)):
            return self._aggregate_formulas(raw, params)
        raise ToolExecutionError(
            "TOOL_INPUT_INVALID",
            "ptable_heatmap input must be formulas, Composition objects, or an element value map.",
            self.tool_id,
            details={"inputType": type(raw).__name__},
        )

    def _aggregate_formulas(self, formulas: Any, params: dict[str, Any]) -> tuple[dict[str, float], str, int]:
        values: dict[str, float] = {}
        count_mode = str(params.get("countMode", "composition")).lower()
        n_inputs = 0
        for formula in formulas:
            try:
                comp = formula if isinstance(formula, Composition) else Composition(str(formula))
            except Exception as exc:
                raise ToolExecutionError(
                    "TOOL_INPUT_INVALID",
                    f"Could not parse formula `{formula}`.",
                    self.tool_id,
                    details={"formula": str(formula)},
                ) from exc
            n_inputs += 1
            for element, amount in comp.element_composition.items():
                increment = 1.0 if count_mode == "occurrence" else float(amount)
                values[element.symbol] = values.get(element.symbol, 0.0) + increment
        return self._normalize_if_requested(values, params), "formula_or_composition", n_inputs

    @staticmethod
    def _looks_like_element_value_map(raw: dict[Any, Any]) -> bool:
        return all(isinstance(key, str) and 1 <= len(key) <= 3 for key in raw) and all(isinstance(value, (int, float)) for value in raw.values())

    @staticmethod
    def _numeric_map(raw: dict[Any, Any]) -> dict[str, float]:
        return {str(key): float(value) for key, value in raw.items()}

    @staticmethod
    def _normalize_if_requested(values: dict[str, float], params: dict[str, Any]) -> dict[str, float]:
        if not params.get("normalize"):
            return values
        total = sum(abs(value) for value in values.values())
        if total == 0:
            return values
        return {key: value / total for key, value in values.items()}

