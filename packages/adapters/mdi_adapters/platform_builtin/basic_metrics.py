from __future__ import annotations

from typing import Any

from mdi_artifact_core import ArtifactPayload
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..ml_common import PreparedRegressionFrame, prepare_regression_frame, regression_metrics


class BasicMetricsAdapter(BaseToolAdapter):
    tool_id = "ml.basic_metrics"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedRegressionFrame:
        resolved = self._resolved_inputs
        raw = resolved[0] if len(resolved) == 1 else resolved
        return prepare_regression_frame(raw, params, tool_id=self.tool_id)

    def run(self, prepared: PreparedRegressionFrame, params: dict[str, Any]) -> dict[str, Any]:
        return {"metrics": regression_metrics(prepared), "prepared": prepared, "params": params}

    def export(self, result: dict[str, Any], artifact_types: list[ArtifactType]) -> list[Artifact]:
        prepared: PreparedRegressionFrame = result["prepared"]
        metrics = result["metrics"]
        params = result["params"]
        payloads: list[ArtifactPayload] = []
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
        if ArtifactType.summary_md in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=(
                        "# Basic Regression Metrics\n\n"
                        f"- Tool: `{self.tool_id}`\n"
                        f"- Rows: {metrics['n']}\n"
                        f"- MAE: {metrics['mae']:.6g}\n"
                        f"- RMSE: {metrics['rmse']:.6g}\n"
                        f"- R2: {metrics['r2']:.6g}\n"
                    ),
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.recipe_json,
                    file_name="recipe.json",
                    content=self.recipe_payload(name="Basic Regression Metrics", params=params, artifact_types=artifact_types),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={
                "sourceFunction": "platform_builtin.basic_metrics",
                "targetColumn": prepared.target_column,
                "predictionColumn": prepared.prediction_column,
            },
        )
