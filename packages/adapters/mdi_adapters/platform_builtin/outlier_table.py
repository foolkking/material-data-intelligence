from __future__ import annotations

from typing import Any

from mdi_artifact_core import ArtifactPayload
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..ml_common import PreparedRegressionFrame, outlier_records, prepare_regression_frame, table_to_csv


class OutlierTableAdapter(BaseToolAdapter):
    tool_id = "ml.outlier_table"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedRegressionFrame:
        resolved = self._resolved_inputs
        raw = resolved[0] if len(resolved) == 1 else resolved
        return prepare_regression_frame(raw, params, tool_id=self.tool_id)

    def run(self, prepared: PreparedRegressionFrame, params: dict[str, Any]) -> dict[str, Any]:
        top_k = int(params.get("topK", 10))
        records = outlier_records(prepared, top_k=top_k)
        return {"records": records, "prepared": prepared, "params": params}

    def export(self, result: dict[str, Any], artifact_types: list[ArtifactType]) -> list[Artifact]:
        prepared: PreparedRegressionFrame = result["prepared"]
        records = result["records"]
        params = result["params"]
        payloads: list[ArtifactPayload] = []
        if ArtifactType.table_json in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.table_json,
                    file_name="table.json",
                    content={
                        "rows": records,
                        "targetColumn": prepared.target_column,
                        "predictionColumn": prepared.prediction_column,
                        "sort": "abs_error_desc",
                    },
                    media_type="application/json",
                )
            )
        if ArtifactType.table_csv in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.table_csv,
                    file_name="table.csv",
                    content=table_to_csv(records),
                    media_type="text/csv",
                )
            )
        if ArtifactType.summary_md in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=(
                        "# Outlier Table\n\n"
                        f"- Tool: `{self.tool_id}`\n"
                        f"- Rows returned: {len(records)}\n"
                        f"- Sorted by: `abs_error` descending\n"
                    ),
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.recipe_json,
                    file_name="recipe.json",
                    content=self.recipe_payload(name="Outlier Table", params=params, artifact_types=artifact_types),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={
                "sourceFunction": "platform_builtin.outlier_table",
                "targetColumn": prepared.target_column,
                "predictionColumn": prepared.prediction_column,
            },
        )
