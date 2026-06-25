from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pymatviz as pmv
from pymatgen.core import Composition, Structure

from mdi_artifact_core import ArtifactPayload
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError
from ..plotly_export import plotly_payloads


@dataclass
class PreparedElementsHist:
    formulas: list[str | Composition]
    n_inputs: int


class ElementsHistAdapter(BaseToolAdapter):
    tool_id = "composition.elements_hist"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedElementsHist:
        resolved = self._resolved_inputs
        if not resolved:
            raise ToolExecutionError("TOOL_INPUT_INVALID", "elements_hist requires at least one input ref.", self.tool_id)
        formulas = self._coerce_formulas(resolved[0] if len(resolved) == 1 else resolved)
        if not formulas:
            raise ToolExecutionError("TOOL_INPUT_INVALID", "No formulas could be derived from input.", self.tool_id)
        return PreparedElementsHist(formulas=formulas, n_inputs=len(formulas))

    def run(self, prepared: PreparedElementsHist, params: dict[str, Any]) -> dict[str, Any]:
        fig = pmv.elements_hist(
            prepared.formulas,
            count_mode=params.get("countMode", "composition"),
            keep_top=params.get("keepTop"),
            log_y=bool(params.get("logY", False)),
            show_values=params.get("showValues", "percent"),
        )
        fig.update_layout(title_text=params.get("title", "Element Histogram"))
        return {"figure": fig, "prepared": prepared, "params": params}

    def export(self, result: dict[str, Any], artifact_types: list[ArtifactType]) -> list[Artifact]:
        prepared: PreparedElementsHist = result["prepared"]
        params = result["params"]
        payloads = plotly_payloads(result["figure"], artifact_types)
        if ArtifactType.summary_md in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=(
                        "# Element Histogram\n\n"
                        f"- Tool: `{self.tool_id}`\n"
                        f"- Input records: {prepared.n_inputs}\n"
                    ),
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.recipe_json,
                    file_name="recipe.json",
                    content=self.recipe_payload(name="Element Histogram", params=params, artifact_types=artifact_types),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={
                "sourceFunction": "pymatviz.elements_hist",
                "pymatvizParamMap": {
                    "countMode": "count_mode",
                    "keepTop": "keep_top",
                    "logY": "log_y",
                    "showValues": "show_values",
                },
            },
        )

    def _coerce_formulas(self, raw: Any) -> list[str | Composition]:
        if isinstance(raw, dict) and "formulas" in raw:
            return self._coerce_formulas(raw["formulas"])
        if isinstance(raw, dict) and "structures" in raw:
            return self._coerce_formulas(raw["structures"])
        if isinstance(raw, (str, Composition)):
            return [raw]
        if isinstance(raw, Structure):
            return [raw.composition.reduced_formula]
        if isinstance(raw, dict) and "@module" in raw and "@class" in raw:
            return [Structure.from_dict(raw).composition.reduced_formula]
        if isinstance(raw, (list, tuple)):
            formulas: list[str | Composition] = []
            for item in raw:
                formulas.extend(self._coerce_formulas(item))
            return formulas
        raise ToolExecutionError(
            "TOOL_INPUT_INVALID",
            "elements_hist input must be formulas, Composition objects, or Structures.",
            self.tool_id,
            details={"inputType": type(raw).__name__},
        )
