from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from mdi_artifact_core import ArtifactPayload, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError
from ..ml_common import coerce_dataframe


def _finite_or_none(value: Any) -> float | int | None:
    if pd.isna(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(number) or number in (float("inf"), float("-inf")):
        return None
    return number


def _is_numeric_like(series: pd.Series) -> bool:
    return not pd.to_numeric(series, errors="coerce").dropna().empty


def _selected_columns(frame: pd.DataFrame, selected: list[str] | None, *, numeric: bool, tool_id: str) -> list[str]:
    if selected:
        missing = [column for column in selected if column not in frame.columns]
        if missing:
            raise ToolExecutionError(
                code="TOOL_INPUT_INVALID",
                message=f"Column not found: {missing[0]}",
                tool_id=tool_id,
                details={"errorType": "missing_column", "column": missing[0]},
            )
        columns = list(selected)
    elif numeric:
        columns = [str(column) for column in frame.columns if _is_numeric_like(frame[column])]
    else:
        columns = [str(column) for column in frame.columns if column not in frame.select_dtypes(include="number").columns]

    if numeric:
        non_numeric = [column for column in columns if not _is_numeric_like(frame[column])]
        if non_numeric:
            raise ToolExecutionError(
                code="TOOL_INPUT_INVALID",
                message=f"Column is not numeric: {non_numeric[0]}",
                tool_id=tool_id,
                details={"errorType": "non_numeric_column", "column": non_numeric[0]},
            )
    return columns


@dataclass(frozen=True)
class DistributionSummaryResult:
    summary: dict[str, Any]
    params: dict[str, Any]


class DistributionSummaryAdapter(BaseToolAdapter):
    tool_id = "table.distribution_summary"
    adapter_version = "0.1.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> pd.DataFrame:
        if not self._resolved_inputs:
            raise ToolExecutionError(
                code="TOOL_INPUT_INVALID",
                message="table.distribution_summary requires a table input.",
                tool_id=self.tool_id,
                details={"errorType": "unsupported_profile_type"},
            )
        frame = coerce_dataframe(self._resolved_inputs[0], tool_id=self.tool_id)
        if frame.empty:
            raise ToolExecutionError(
                code="TOOL_INPUT_INVALID",
                message="Table is empty.",
                tool_id=self.tool_id,
                details={"errorType": "empty_table"},
            )
        return frame

    def run(self, prepared: pd.DataFrame, params: dict[str, Any]) -> DistributionSummaryResult:
        frame = prepared
        quantiles = params.get("quantiles") or [0.25, 0.5, 0.75]
        max_categories = int(params.get("maxCategories") or 10)
        numeric_columns = _selected_columns(frame, params.get("numericColumns"), numeric=True, tool_id=self.tool_id)
        categorical_columns = _selected_columns(
            frame, params.get("categoricalColumns"), numeric=False, tool_id=self.tool_id
        )

        numeric_summary = {
            column: self._numeric_distribution(frame[column], quantiles=quantiles)
            for column in numeric_columns
        }
        categorical_summary = {
            column: self._categorical_distribution(frame[column], max_categories=max_categories)
            for column in categorical_columns
        }
        warnings: list[str] = []
        if not numeric_columns:
            warnings.append("No numeric columns were selected.")
        if not categorical_columns:
            warnings.append("No categorical columns were selected.")

        summary = {
            "rowCount": int(len(frame)),
            "columnCount": int(len(frame.columns)),
            "numericColumns": numeric_summary,
            "categoricalColumns": categorical_summary,
            "recommendedVisualizations": self._recommended_visualizations(numeric_columns, categorical_columns),
            "warnings": warnings,
        }
        return DistributionSummaryResult(summary=summary, params=params)

    def export(self, result: DistributionSummaryResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        requested = set(artifact_types) or {
            ArtifactType.table_json,
            ArtifactType.summary_md,
            ArtifactType.recipe_json,
        }
        payloads: list[ArtifactPayload] = []
        if ArtifactType.table_json in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.table_json,
                    file_name="distribution_summary.json",
                    content=stable_json_dumps(result.summary),
                    media_type="application/json",
                )
            )
        if ArtifactType.summary_md in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=self._summary_markdown(result.summary),
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.recipe_json,
                    file_name="recipe.json",
                    content=stable_json_dumps(
                        self.recipe_payload(
                            name="Table distribution summary",
                            params=result.params,
                            artifact_types=list(requested),
                        )
                    ),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={"adapter": "table.distribution_summary", "summaryRows": result.summary["rowCount"]},
        )

    @staticmethod
    def _numeric_distribution(series: pd.Series, *, quantiles: list[float]) -> dict[str, Any]:
        numeric = pd.to_numeric(series, errors="coerce")
        non_null = numeric.dropna()
        quantile_values = non_null.quantile(quantiles).to_dict() if len(non_null) else {}
        return {
            "count": int(non_null.count()),
            "missing": int(numeric.isna().sum()),
            "missingRate": float(numeric.isna().mean()) if len(numeric) else 0.0,
            "mean": _finite_or_none(non_null.mean()) if len(non_null) else None,
            "std": _finite_or_none(non_null.std()) if len(non_null) > 1 else None,
            "min": _finite_or_none(non_null.min()) if len(non_null) else None,
            "p25": _finite_or_none(quantile_values.get(0.25)),
            "median": _finite_or_none(quantile_values.get(0.5)),
            "p75": _finite_or_none(quantile_values.get(0.75)),
            "max": _finite_or_none(non_null.max()) if len(non_null) else None,
            "uniqueCount": int(non_null.nunique(dropna=True)),
        }

    @staticmethod
    def _categorical_distribution(series: pd.Series, *, max_categories: int) -> dict[str, Any]:
        values = series.astype("string")
        non_null = values.dropna()
        counts = non_null.value_counts(dropna=True).head(max_categories)
        return {
            "count": int(non_null.count()),
            "missing": int(values.isna().sum()),
            "missingRate": float(values.isna().mean()) if len(values) else 0.0,
            "uniqueCount": int(non_null.nunique(dropna=True)),
            "topValues": [{"value": str(index), "count": int(count)} for index, count in counts.items()],
        }

    @staticmethod
    def _recommended_visualizations(numeric_columns: list[str], categorical_columns: list[str]) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []
        for column in numeric_columns[:6]:
            recommendations.append({"toolId": "viz.histogram", "params": {"column": column}})
        if len(numeric_columns) >= 2:
            recommendations.append({"toolId": "viz.correlation", "params": {"numericColumns": numeric_columns[:12]}})
        for column in categorical_columns[:3]:
            recommendations.append({"toolId": "table.distribution_summary", "params": {"categoricalColumns": [column]}})
        return recommendations

    @staticmethod
    def _summary_markdown(summary: dict[str, Any]) -> str:
        numeric_names = ", ".join(summary["numericColumns"].keys()) or "none"
        categorical_names = ", ".join(summary["categoricalColumns"].keys()) or "none"
        return "\n".join(
            [
                "# Table Distribution Summary",
                "",
                f"- Rows: {summary['rowCount']}",
                f"- Columns: {summary['columnCount']}",
                f"- Numeric columns: {numeric_names}",
                f"- Categorical columns: {categorical_names}",
                f"- Recommended visualizations: {len(summary['recommendedVisualizations'])}",
            ]
        )
