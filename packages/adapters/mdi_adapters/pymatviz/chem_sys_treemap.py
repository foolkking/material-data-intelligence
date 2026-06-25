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
class PreparedChemSysTreemap:
    data: list[str | Composition | Structure]
    n_inputs: int


class ChemSysTreemapAdapter(BaseToolAdapter):
    tool_id = "composition.chem_sys_treemap"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedChemSysTreemap:
        resolved = self._resolved_inputs
        if not resolved:
            raise ToolExecutionError("TOOL_INPUT_INVALID", "chem_sys_treemap requires at least one input ref.", self.tool_id)
        data = self._coerce_data(resolved[0] if len(resolved) == 1 else resolved)
        if not data:
            raise ToolExecutionError("TOOL_INPUT_INVALID", "No composition data could be derived from input.", self.tool_id)
        return PreparedChemSysTreemap(data=data, n_inputs=len(data))

    def run(self, prepared: PreparedChemSysTreemap, params: dict[str, Any]) -> dict[str, Any]:
        fig = pmv.chem_sys_treemap(
            prepared.data,
            show_counts=params.get("showCounts", "value"),
            max_cells=params.get("maxCells"),
        )
        fig.update_layout(title_text=params.get("title", "Chemical System Treemap"))
        return {"figure": fig, "prepared": prepared, "params": params}

    def export(self, result: dict[str, Any], artifact_types: list[ArtifactType]) -> list[Artifact]:
        prepared: PreparedChemSysTreemap = result["prepared"]
        params = result["params"]
        payloads = plotly_payloads(result["figure"], artifact_types)
        if ArtifactType.summary_md in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=(
                        "# Chemical System Treemap\n\n"
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
                    content=self.recipe_payload(name="Chemical System Treemap", params=params, artifact_types=artifact_types),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={
                "sourceFunction": "pymatviz.chem_sys_treemap",
                "pymatvizParamMap": {"showCounts": "show_counts", "maxCells": "max_cells"},
            },
        )

    def _coerce_data(self, raw: Any) -> list[str | Composition | Structure]:
        if isinstance(raw, dict) and "formulas" in raw:
            return self._coerce_data(raw["formulas"])
        if isinstance(raw, dict) and "structures" in raw:
            return self._coerce_data(raw["structures"])
        if isinstance(raw, (str, Composition, Structure)):
            return [raw]
        if isinstance(raw, dict) and "@module" in raw and "@class" in raw:
            return [Structure.from_dict(raw)]
        if isinstance(raw, (list, tuple)):
            data: list[str | Composition | Structure] = []
            for item in raw:
                data.extend(self._coerce_data(item))
            return data
        raise ToolExecutionError(
            "TOOL_INPUT_INVALID",
            "chem_sys_treemap input must be formulas, Composition objects, or Structures.",
            self.tool_id,
            details={"inputType": type(raw).__name__},
        )
