from __future__ import annotations

from typing import Any

import plotly.express as px

from mdi_artifact_core import ArtifactPayload
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..ml_common import (
    PreparedRegressionFrame,
    outlier_records,
    prepare_regression_frame,
    regression_metrics,
)
from ..plotly_export import plotly_payloads


class ErrorDistributionAdapter(BaseToolAdapter):
    tool_id = "ml.error_distribution"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedRegressionFrame:
        resolved = self._resolved_inputs
        raw = resolved[0] if len(resolved) == 1 else resolved
        return prepare_regression_frame(raw, params, tool_id=self.tool_id)

    def run(self, prepared: PreparedRegressionFrame, params: dict[str, Any]) -> dict[str, Any]:
        frame = prepared.dataframe.copy()
        frame["error"] = frame[prepared.prediction_column].astype(float) - frame[prepared.target_column].astype(float)
        frame["abs_error"] = frame["error"].abs()
        fig = px.histogram(
            frame,
            x="error",
            nbins=params.get("nBins", 30),
            title=params.get("title", "Prediction Error Distribution"),
            labels={"error": "Prediction error"},
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
                "sourceFunction": "plotly.express.histogram",
                "targetColumn": prepared.target_column,
                "predictionColumn": prepared.prediction_column,
            },
        )
