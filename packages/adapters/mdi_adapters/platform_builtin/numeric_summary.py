from __future__ import annotations

from math import isfinite
from typing import Any

import pandas as pd

from mdi_artifact_core import ArtifactPayload
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..ml_common import coerce_dataframe


class NumericSummaryAdapter(BaseToolAdapter):
    tool_id = "table.numeric_summary"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> pd.DataFrame:
        resolved = self._resolved_inputs
        raw = resolved[0] if len(resolved) == 1 else resolved
        return coerce_dataframe(raw, tool_id=self.tool_id)

    def run(self, prepared: pd.DataFrame, params: dict[str, Any]) -> dict[str, Any]:
        dataframe = prepared.copy()
        numeric_columns = _selected_columns(dataframe, params.get("numericColumns"), numeric=True)
        categorical_columns = _selected_columns(dataframe, params.get("categoricalColumns"), numeric=False)
        max_categories = int(params.get("maxCategories") or 12)
        max_categories = max(1, min(max_categories, 50))

        return {
            "rowCount": int(len(dataframe)),
            "columns": [_column_summary(dataframe, column) for column in dataframe.columns],
            "numericColumns": {
                str(column): _numeric_summary(dataframe[column]) for column in numeric_columns
            },
            "categoricalColumns": {
                str(column): _categorical_summary(dataframe[column], max_categories=max_categories)
                for column in categorical_columns
            },
        }

    def export(self, result: dict[str, Any], artifact_types: list[ArtifactType]) -> list[Artifact]:
        payloads: list[ArtifactPayload] = []
        if ArtifactType.table_json in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.table_json,
                    file_name="numeric_summary.json",
                    content=result,
                    media_type="application/json",
                )
            )
        if ArtifactType.summary_md in artifact_types:
            numeric_names = ", ".join(result["numericColumns"].keys()) or "none"
            categorical_names = ", ".join(result["categoricalColumns"].keys()) or "none"
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=(
                        "# Numeric Table Summary\n\n"
                        f"- Tool: `{self.tool_id}`\n"
                        f"- Rows: {result['rowCount']}\n"
                        f"- Numeric columns: {numeric_names}\n"
                        f"- Categorical columns: {categorical_names}\n"
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
                        name="Numeric Table Summary",
                        params={},
                        artifact_types=artifact_types,
                    ),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={"sourceFunction": "platform_builtin.numeric_summary"},
        )


def _selected_columns(dataframe: pd.DataFrame, requested: Any, *, numeric: bool) -> list[str]:
    columns = [str(column) for column in dataframe.columns]
    if isinstance(requested, list) and requested:
        requested_names = [str(column) for column in requested if str(column) in columns]
        return requested_names

    selected: list[str] = []
    for column in dataframe.columns:
        name = str(column)
        if not name or name.lower().startswith("unnamed:"):
            continue
        is_numeric = pd.api.types.is_numeric_dtype(dataframe[column])
        if numeric and is_numeric:
            selected.append(name)
        elif not numeric and not is_numeric:
            selected.append(name)
    return selected


def _column_summary(dataframe: pd.DataFrame, column: Any) -> dict[str, Any]:
    series = dataframe[column]
    return {
        "name": str(column),
        "dtype": str(series.dtype),
        "missingCount": int(series.isna().sum()),
        "nonNullCount": int(series.notna().sum()),
    }


def _numeric_summary(series: pd.Series) -> dict[str, Any]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return {"count": 0, "mean": None, "std": None, "min": None, "median": None, "max": None}
    return {
        "count": int(clean.count()),
        "mean": _finite_or_none(clean.mean()),
        "std": _finite_or_none(clean.std(ddof=1)) if len(clean) > 1 else 0.0,
        "min": _finite_or_none(clean.min()),
        "median": _finite_or_none(clean.median()),
        "max": _finite_or_none(clean.max()),
    }


def _categorical_summary(series: pd.Series, *, max_categories: int) -> dict[str, Any]:
    clean = series.dropna().astype(str)
    counts = clean.value_counts().head(max_categories)
    return {
        "count": int(clean.count()),
        "unique": int(clean.nunique()),
        "valueCounts": {str(key): int(value) for key, value in counts.items()},
    }


def _finite_or_none(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if isfinite(result) else None
