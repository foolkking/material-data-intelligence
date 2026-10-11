from __future__ import annotations

from typing import Any

import numpy as np
import plotly.graph_objects as go

from mdi_artifact_core import ArtifactPayload
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError
from ..ml_common import (
    PreparedRegressionFrame,
    outlier_records,
    prepare_regression_frame,
    regression_metrics,
)
from ..plotly_export import plotly_payloads


class ErrorDistributionAdapter(BaseToolAdapter):
    tool_id = "ml.error_distribution"
    adapter_version = "0.3.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedRegressionFrame:
        resolved = self._resolved_inputs
        raw = resolved[0] if len(resolved) == 1 else resolved
        return prepare_regression_frame(raw, params, tool_id=self.tool_id)

    def run(self, prepared: PreparedRegressionFrame, params: dict[str, Any]) -> dict[str, Any]:
        frame = prepared.dataframe.copy()
        frame["error"] = frame[prepared.prediction_column].astype(float) - frame[prepared.target_column].astype(float)
        errors = frame["error"].to_numpy()
        bins = params.get("nBins", 30)
        if type(bins) is not int or not 1 <= bins <= 4096 or not np.isfinite(errors).all():
            raise ToolExecutionError("TOOL_INPUT_INVALID", "Residuals must be finite and nBins an integer from 1 to 4096.", self.tool_id)
        counts, edges = np.histogram(errors, bins=bins)
        histogram = {
            "counts": counts.tolist(), "edges": edges.tolist(),
            "sampleCount": len(errors), "residuals": errors.tolist(),
            "residualConvention": "prediction - target",
            "intervalConvention": "left-closed-right-open; final bin includes right edge",
        }
        # Save the actual bins; a browser must never calculate the scientific
        # distribution from raw samples or reinterpret an approximate nbins.
        fig = go.Figure(go.Bar(
            x=((edges[:-1] + edges[1:]) / 2).tolist(), y=counts.tolist(),
            width=np.diff(edges).tolist(), name="残差分布",
            customdata=np.column_stack((edges[:-1], edges[1:])).tolist(),
            hovertemplate="区间：%{customdata[0]} 至 %{customdata[1]}<br>样本数：%{y}<extra></extra>",
        ))
        fig.update_layout(
            title=params.get("title", "残差分布"),
            xaxis_title="残差（预测值 − 真实值）", yaxis_title="样本数",
            barmode="overlay", bargap=0,
            meta={"schemaVersion": "mdi.residual-histogram/1.0", "histogram": histogram},
        )
        return {
            "figure": fig,
            "metrics": regression_metrics(prepared),
            "records": outlier_records(prepared, top_k=int(params.get("topK", 10))),
            "prepared": prepared,
            "params": params,
        }

    def export(self, result: dict[str, Any], artifact_types: list[ArtifactType]) -> list[Artifact]:
        prepared: PreparedRegressionFrame = result["prepared"]
        metrics = result["metrics"]
        records = result["records"]
        params = result["params"]
        payloads = plotly_payloads(result["figure"], artifact_types)
        if ArtifactType.metrics_json in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.metrics_json,
                    file_name="metrics.json",
                    content={
                        "metrics": metrics,
                        "targetColumn": prepared.target_column,
                        "predictionColumn": prepared.prediction_column,
                    },
                    media_type="application/json",
                )
            )
        if ArtifactType.table_json in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.table_json,
                    file_name="table.json",
                    content={"rows": records, "sort": "abs_error_desc"},
                    media_type="application/json",
                )
            )
        if ArtifactType.summary_md in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=(
                        "# Error Distribution\n\n"
                        f"- Tool: `{self.tool_id}`\n"
                        f"- Rows: {metrics['n']}\n"
                        f"- Mean error: {metrics['meanError']:.6g}\n"
                        f"- MAE: {metrics['mae']:.6g}\n"
                    ),
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.recipe_json,
                    file_name="recipe.json",
                    content=self.recipe_payload(name="Error Distribution", params=params, artifact_types=artifact_types),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={
                "sourceFunction": "numpy.histogram",
                "numpyVersion": np.__version__,
                "binning": "saved equal-width bins; final bin includes right edge",
                "targetColumn": prepared.target_column,
                "predictionColumn": prepared.prediction_column,
            },
        )
