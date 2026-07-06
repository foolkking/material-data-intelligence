from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from mdi_artifact_core import ArtifactPayload, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError
from ..ml_common import coerce_dataframe
from ..plotly_export import plotly_payloads


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


def _table_input(resolved_inputs: list[Any], *, tool_id: str) -> pd.DataFrame:
    if not resolved_inputs:
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message=f"{tool_id} requires a table input.",
            tool_id=tool_id,
            details={"errorType": "unsupported_profile_type"},
        )
    frame = coerce_dataframe(resolved_inputs[0], tool_id=tool_id)
    if frame.empty:
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message="Table is empty.",
            tool_id=tool_id,
            details={"errorType": "empty_table"},
        )
    return frame


def _require_column(frame: pd.DataFrame, column: str, *, tool_id: str) -> None:
    if column not in frame.columns:
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message=f"Column not found: {column}",
            tool_id=tool_id,
            details={"errorType": "missing_column", "column": column},
        )


def _numeric_series(frame: pd.DataFrame, column: str, *, tool_id: str) -> pd.Series:
    _require_column(frame, column, tool_id=tool_id)
    numeric = pd.to_numeric(frame[column], errors="coerce")
    if numeric.dropna().empty:
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message=f"Column is not numeric: {column}",
            tool_id=tool_id,
            details={"errorType": "non_numeric_column", "column": column},
        )
    return numeric


def _require_numeric(frame: pd.DataFrame, column: str, *, tool_id: str) -> None:
    _numeric_series(frame, column, tool_id=tool_id)


def _numeric_columns(frame: pd.DataFrame, selected: list[str] | None, *, tool_id: str) -> list[str]:
    if selected:
        columns = list(selected)
        for column in columns:
            _require_numeric(frame, column, tool_id=tool_id)
        return columns
    return [str(column) for column in frame.columns if not pd.to_numeric(frame[column], errors="coerce").dropna().empty]


@dataclass(frozen=True)
class ChartResult:
    metadata: dict[str, Any]
    figure: Any
    params: dict[str, Any]


class ScatterAdapter(BaseToolAdapter):
    tool_id = "viz.scatter"
    adapter_version = "0.1.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> pd.DataFrame:
        return _table_input(self._resolved_inputs, tool_id=self.tool_id)

    def run(self, prepared: pd.DataFrame, params: dict[str, Any]) -> ChartResult:
        frame = prepared
        x_column = str(params.get("xColumn") or "")
        y_column = str(params.get("yColumn") or "")
        _require_numeric(frame, x_column, tool_id=self.tool_id)
        _require_numeric(frame, y_column, tool_id=self.tool_id)
        color_column = params.get("colorColumn")
        if color_column:
            _require_column(frame, str(color_column), tool_id=self.tool_id)
        hover_columns = [column for column in params.get("hoverColumns", []) if column in frame.columns]
        plot_frame = frame[[x_column, y_column, *([str(color_column)] if color_column else []), *hover_columns]].dropna(
            subset=[x_column, y_column]
        )
        warnings: list[str] = []
        if len(plot_frame) > 50000:
            warnings.append("too_many_points_warning")
            plot_frame = plot_frame.head(50000)
        fig = px.scatter(
            plot_frame,
            x=x_column,
            y=y_column,
            color=str(color_column) if color_column else None,
            hover_data=hover_columns or None,
            title=params.get("title") or f"{x_column} vs {y_column}",
        )
        metadata = {
            "chartType": "scatter",
            "xColumn": x_column,
            "yColumn": y_column,
            "pointCount": int(len(plot_frame)),
            "traces": int(len(fig.data)),
            "xRange": [_finite_or_none(plot_frame[x_column].min()), _finite_or_none(plot_frame[x_column].max())],
            "yRange": [_finite_or_none(plot_frame[y_column].min()), _finite_or_none(plot_frame[y_column].max())],
            "warnings": warnings,
        }
        return ChartResult(metadata=metadata, figure=fig, params=params)

    def export(self, result: ChartResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        return _export_chart(self, result, artifact_types, stem="scatter", title="Scatter plot")


class HistogramAdapter(BaseToolAdapter):
    tool_id = "viz.histogram"
    adapter_version = "0.1.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> pd.DataFrame:
        return _table_input(self._resolved_inputs, tool_id=self.tool_id)

    def run(self, prepared: pd.DataFrame, params: dict[str, Any]) -> ChartResult:
        frame = prepared
        column = str(params.get("column") or "")
        _require_numeric(frame, column, tool_id=self.tool_id)
        group_by = params.get("groupBy")
        if group_by:
            _require_column(frame, str(group_by), tool_id=self.tool_id)
        bins = max(1, int(params.get("bins") or 20))
        values = _numeric_series(frame, column, tool_id=self.tool_id).dropna()
        if values.empty:
            raise ToolExecutionError(
                code="TOOL_INPUT_INVALID",
                message=f"Column has no numeric values: {column}",
                tool_id=self.tool_id,
                details={"errorType": "non_numeric_column", "column": column},
            )
        bin_counts, bin_edges = np.histogram(values.to_numpy(), bins=bins)
        fig = px.histogram(
            frame,
            x=column,
            color=str(group_by) if group_by else None,
            nbins=bins,
            title=params.get("title") or f"{column} distribution",
        )
        metadata = {
            "chartType": "histogram",
            "column": column,
            "count": int(values.count()),
            "bins": int(bins),
            "binEdges": [_finite_or_none(value) for value in bin_edges.tolist()],
            "binCounts": [int(value) for value in bin_counts.tolist()],
            "min": _finite_or_none(values.min()),
            "max": _finite_or_none(values.max()),
            "mean": _finite_or_none(values.mean()),
            "median": _finite_or_none(values.median()),
            "warnings": [],
        }
        return ChartResult(metadata=metadata, figure=fig, params=params)

    def export(self, result: ChartResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        return _export_chart(self, result, artifact_types, stem="histogram", title="Histogram")


class CorrelationAdapter(BaseToolAdapter):
    tool_id = "viz.correlation"
    adapter_version = "0.1.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> pd.DataFrame:
        return _table_input(self._resolved_inputs, tool_id=self.tool_id)

    def run(self, prepared: pd.DataFrame, params: dict[str, Any]) -> ChartResult:
        frame = prepared
        method = str(params.get("method") or "pearson")
        if method not in {"pearson", "spearman"}:
            raise ToolExecutionError(
                code="TOOL_PARAM_INVALID",
                message=f"Unsupported correlation method: {method}",
                tool_id=self.tool_id,
                details={"errorType": "unsupported_method", "method": method},
            )
        columns = _numeric_columns(frame, params.get("numericColumns"), tool_id=self.tool_id)
        columns = columns[:30]
        if len(columns) < 2:
            raise ToolExecutionError(
                code="TOOL_INPUT_INVALID",
                message="At least two numeric columns are required.",
                tool_id=self.tool_id,
                details={"errorType": "insufficient_numeric_columns"},
            )
        min_non_null = max(1, int(params.get("minNonNullCount") or 2))
        numeric = frame[columns].apply(pd.to_numeric, errors="coerce")
        corr = numeric.corr(method=method, min_periods=min_non_null)
        matrix = [
            [_finite_or_none(corr.loc[row, column]) for column in columns]
            for row in columns
        ]
        fig = go.Figure(
            data=go.Heatmap(
                z=matrix,
                x=columns,
                y=columns,
                colorscale="RdBu",
                zmin=-1,
                zmax=1,
                colorbar={"title": method},
            )
        )
        fig.update_layout(title=params.get("title") or f"{method.title()} correlation")
        metadata = {
            "chartType": "correlation_heatmap",
            "method": method,
            "columns": columns,
            "matrix": matrix,
            "pairCount": int(len(columns) * (len(columns) - 1) / 2),
            "warnings": [],
        }
        return ChartResult(metadata=metadata, figure=fig, params=params)

    def export(self, result: ChartResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        requested = set(artifact_types) or {
            ArtifactType.table_json,
            ArtifactType.plotly_json,
            ArtifactType.plotly_html,
            ArtifactType.summary_md,
            ArtifactType.recipe_json,
        }
        payloads: list[ArtifactPayload] = []
        if ArtifactType.table_json in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.table_json,
                    file_name="correlation_matrix.json",
                    content=stable_json_dumps(result.metadata),
                    media_type="application/json",
                )
            )
        payloads.extend(plotly_payloads(result.figure, list(requested), stem="correlation_heatmap"))
        payloads.extend(_summary_and_recipe_payloads(self, result, requested, title="Correlation matrix"))
        return self.export_payloads(payloads, provenance={"adapter": self.tool_id, "columns": result.metadata["columns"]})


def _export_chart(
    adapter: BaseToolAdapter,
    result: ChartResult,
    artifact_types: list[ArtifactType],
    *,
    stem: str,
    title: str,
) -> list[Artifact]:
    requested = set(artifact_types) or {
        ArtifactType.plotly_json,
        ArtifactType.plotly_html,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }
    payloads: list[ArtifactPayload] = []
    if ArtifactType.plotly_json in requested:
        payloads.append(
            ArtifactPayload(
                artifact_type=ArtifactType.plotly_json,
                file_name=f"{stem}.json",
                content=stable_json_dumps({**result.metadata, "figure": result.figure.to_plotly_json()}),
                media_type="application/json",
            )
        )
    payloads.extend(
        plotly_payloads(
            result.figure,
            [artifact_type for artifact_type in requested if artifact_type != ArtifactType.plotly_json],
            stem=stem,
        )
    )
    payloads.extend(_summary_and_recipe_payloads(adapter, result, requested, title=title))
    return adapter.export_payloads(
        payloads,
        provenance={"adapter": adapter.tool_id, "chartType": result.metadata["chartType"]},
    )


def _summary_and_recipe_payloads(
    adapter: BaseToolAdapter,
    result: ChartResult,
    requested: set[ArtifactType],
    *,
    title: str,
) -> list[ArtifactPayload]:
    payloads: list[ArtifactPayload] = []
    if ArtifactType.summary_md in requested:
        payloads.append(
            ArtifactPayload(
                artifact_type=ArtifactType.summary_md,
                file_name="summary.md",
                content=_summary_markdown(title, result.metadata),
                media_type="text/markdown",
            )
        )
    if ArtifactType.recipe_json in requested:
        payloads.append(
            ArtifactPayload(
                artifact_type=ArtifactType.recipe_json,
                file_name="recipe.json",
                content=stable_json_dumps(
                    adapter.recipe_payload(
                        name=title,
                        params=result.params,
                        artifact_types=list(requested),
                    )
                ),
                media_type="application/json",
            )
        )
    return payloads


def _summary_markdown(title: str, metadata: dict[str, Any]) -> str:
    lines = [f"# {title}", ""]
    for key in ("chartType", "xColumn", "yColumn", "column", "pointCount", "count", "method", "pairCount"):
        if key in metadata:
            lines.append(f"- {key}: {metadata[key]}")
    if metadata.get("warnings"):
        lines.append(f"- warnings: {', '.join(metadata['warnings'])}")
    return "\n".join(lines)
