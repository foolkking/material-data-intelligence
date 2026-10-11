from __future__ import annotations

from typing import Any

import pymatviz as pmv
import numpy as np
import plotly.graph_objects as go

from mdi_artifact_core import ArtifactPayload
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError
from ..ml_common import PreparedRegressionFrame, prepare_regression_frame, regression_metrics
from ..plotly_export import plotly_payloads


class DensityScatterAdapter(BaseToolAdapter):
    tool_id = "ml.density_scatter"
    adapter_version = "0.2.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedRegressionFrame:
        resolved = self._resolved_inputs
        raw = resolved[0] if len(resolved) == 1 else resolved
        return prepare_regression_frame(raw, params, tool_id=self.tool_id)

    def run(self, prepared: PreparedRegressionFrame, params: dict[str, Any]) -> dict[str, Any]:
        xs = prepared.dataframe[prepared.target_column].astype(float).to_numpy()
        ys = prepared.dataframe[prepared.prediction_column].astype(float).to_numpy()
        if not np.isfinite(xs).all() or not np.isfinite(ys).all():
            raise ToolExecutionError("TOOL_INPUT_INVALID", "Scatter coordinates must be finite.", self.tool_id)
        metrics = regression_metrics(prepared)
        constant_target = metrics["r2"] is None
        options = {
            "identity_line": params.get("identityLine", True),
            "best_fit_line": params.get("bestFitLine", True) and not constant_target,
            "stats": params.get("stats", True) if not constant_target else False,
        }
        raw_points = False
        requested_density = params.get("density")
        uses_kde = requested_density == "kde" or (not requested_density and not params.get("nBins", False))
        try:
            # Pymatviz silently substitutes empirical colors for a single point.
            # A 2D KDE needs at least three non-collinear samples.
            if uses_kde and (len(xs) < 3 or constant_target or bool(np.all(ys == ys[0]))):
                raise np.linalg.LinAlgError("Insufficient independent coordinates for KDE")
            fig = pmv.density_scatter(
                prepared.target_column, prepared.prediction_column,
                df=prepared.dataframe, n_bins=params.get("nBins", False), density=requested_density,
                xlabel=params.get("xLabel", prepared.target_column),
                ylabel=params.get("yLabel", prepared.prediction_column), **options,
            )
        except np.linalg.LinAlgError as error:
            if not uses_kde:
                raise
            if requested_density == "kde":
                raise ToolExecutionError(
                    "TOOL_INPUT_INVALID", "核密度无法估计：需要至少三个非共线样本；可使用默认原始散点显示。", self.tool_id,
                    details={"reason": "KDE_UNDEFINED_SINGULAR_COORDINATES"},
                ) from error
            raw_points = True
            fig = go.Figure(go.Scattergl(
                x=xs.tolist(), y=ys.tolist(), mode="markers", marker={"color": "#287d74", "size": 6},
            ))
            fig.update_layout(
                xaxis_title=params.get("xLabel", prepared.target_column),
                yaxis_title=params.get("yLabel", prepared.prediction_column),
                meta={"schemaVersion": "mdi.raw-parity-scatter/1.0"},
            )
            pmv.powerups.enhance_parity_plot(fig, xs=xs, ys=ys, **options)
            fig.add_annotation(
                text="核密度未估计：样本不足或坐标共线，显示原始散点。",
                x=0, y=0, xref="paper", yref="paper", showarrow=False,
            )
        if constant_target and params.get("stats", True):
            fig.add_annotation(
                text=f"MAE = {metrics['mae']:.6g}<br>R² 未定义（目标值为常量）",
                x=0, y=1, xref="paper", yref="paper", showarrow=False,
            )
        fig.update_layout(title_text=params.get("title", "Prediction Density Scatter"))
        return {"figure": fig, "prepared": prepared, "params": params, "raw_points": raw_points}

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
                        + ("- 核密度未估计：样本不足或坐标共线，显示原始散点。\n" if result["raw_points"] else "")
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
                "sourceFunction": "plotly.graph_objects.Scattergl + pymatviz.powerups.enhance_parity_plot" if result["raw_points"] else "pymatviz.density_scatter",
                "renderingMode": "raw_points_kde_unavailable" if result["raw_points"] else "density",
                "targetColumn": prepared.target_column,
                "predictionColumn": prepared.prediction_column,
                "pymatvizParamMap": {
                    "nBins": "n_bins",
                    "identityLine": "identity_line",
                    "bestFitLine": "best_fit_line",
                },
            },
        )
