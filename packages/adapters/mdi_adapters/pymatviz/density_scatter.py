from __future__ import annotations

from typing import Any

import pymatviz as pmv

from mdi_artifact_core import ArtifactPayload
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..ml_common import PreparedRegressionFrame, prepare_regression_frame
from ..plotly_export import plotly_payloads


class DensityScatterAdapter(BaseToolAdapter):
    tool_id = "ml.density_scatter"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedRegressionFrame:
        resolved = self._resolved_inputs
        raw = resolved[0] if len(resolved) == 1 else resolved
        return prepare_regression_frame(raw, params, tool_id=self.tool_id)

    def run(self, prepared: PreparedRegressionFrame, params: dict[str, Any]) -> dict[str, Any]:
        fig = pmv.density_scatter(
            prepared.target_column,
            prepared.prediction_column,
            df=prepared.dataframe,
            n_bins=params.get("nBins", False),
            density=params.get("density"),
            xlabel=params.get("xLabel", prepared.target_column),
            ylabel=params.get("yLabel", prepared.prediction_column),
            identity_line=params.get("identityLine", True),
            best_fit_line=params.get("bestFitLine", True),
            stats=params.get("stats", True),
        )
        fig.update_layout(title_text=params.get("title", "Prediction Density Scatter"))
        return {"figure": fig, "prepared": prepared, "params": params}

    def export(self, result: dict[str, Any], artifact_types: list[ArtifactType]) -> list[Artifact]:
        prepared: PreparedRegressionFrame = result["prepared"]
        params = result["params"]
        payloads = plotly_payloads(result["figure"], artifact_types)
        if ArtifactType.summary_md in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=(
                        "# Prediction Density Scatter\n\n"
                        f"- Tool: `{self.tool_id}`\n"
                        f"- Rows: {len(prepared.dataframe)}\n"
                        f"- Target column: `{prepared.target_column}`\n"
                        f"- Prediction column: `{prepared.prediction_column}`\n"
                    ),
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.recipe_json,
                    file_name="recipe.json",
                    content=self.recipe_payload(name="Prediction Density Scatter", params=params, artifact_types=artifact_types),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={
                "sourceFunction": "pymatviz.density_scatter",
                "targetColumn": prepared.target_column,
                "predictionColumn": prepared.prediction_column,
                "pymatvizParamMap": {
                    "nBins": "n_bins",
                    "identityLine": "identity_line",
                    "bestFitLine": "best_fit_line",
                },
            },
        )
