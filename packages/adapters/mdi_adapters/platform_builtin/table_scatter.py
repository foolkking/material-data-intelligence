"""Save paired numeric coordinates, exact row identities and explicit sampling."""
from __future__ import annotations

from html import escape
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from ..errors import ToolExecutionError


def saved_scatter(frame: pd.DataFrame, params: dict[str, Any], *, tool_id: str):
    def fail(reason: str, message: str, *, parameter: bool = False):
        raise ToolExecutionError("TOOL_PARAM_INVALID" if parameter else "TOOL_INPUT_INVALID", message,
                                 tool_id, details={"errorType": reason})

    x_column, y_column, color_column = params.get("xColumn"), params.get("yColumn"), params.get("colorColumn")
    hover = params.get("hoverColumns", [])
    if (not isinstance(hover, list) or len(hover) > 8 or any(not isinstance(v, str) for v in hover)
            or len(set(hover)) != len(hover)):
        fail("SCATTER_PARAMS_INVALID", "悬停信息最多选择 8 个不重复的数据列。", parameter=True)
    for column in [x_column, y_column, *([color_column] if color_column is not None else []), *hover]:
        if not isinstance(column, str) or not column.strip() or len(column) > 512:
            fail("SCATTER_PARAMS_INVALID", "请选择横轴和纵轴的数值列，并检查颜色列和悬停列。", parameter=True)
        if sum(item == column for item in frame.columns) != 1:
            fail("SCATTER_COLUMN_INVALID", "所选列不存在或列名不唯一，请检查数据列后重试。")

    def numbers(column):
        series = pd.to_numeric(frame[column], errors="coerce")
        if np.iscomplexobj(series):
            fail("SCATTER_VALUES_INVALID", "散点图坐标及连续颜色需要有限实数，请选择实数列。")
        return series.to_numpy(dtype=float, na_value=np.nan)

    x, y = numbers(x_column), numbers(y_column)
    xy_mask = np.isfinite(x) & np.isfinite(y)
    color_mode = "none" if color_column is None else "numeric" if (
        pd.api.types.is_numeric_dtype(frame[color_column]) and not pd.api.types.is_bool_dtype(frame[color_column])) else "categorical"
    color_values = numbers(color_column) if color_mode == "numeric" else None
    mask = xy_mask if color_values is None else xy_mask & np.isfinite(color_values)
    indices = np.flatnonzero(mask)
    if not len(indices):
        fail("SCATTER_VALUES_INVALID", "所选横纵轴与连续颜色列没有共同的有限数值，请检查所选列和缺失数据。")
    x, y = x[mask], y[mask]
    if color_values is not None:
        color_values = color_values[mask]
    with np.errstate(over="ignore"):
        if any(not np.isfinite(vector.max() - vector.min()) for vector in (x, y, *([color_values] if color_values is not None else []))):
            fail("SCATTER_RANGE_INVALID", "所选数值跨度超出绘图范围，请调整数值尺度后重试。")

    groups: list[dict[str, Any]] = []
    membership = np.zeros(len(indices), dtype=int)
    if color_mode == "categorical":
        identities: dict[tuple[str, Any], int] = {}
        for i, value in enumerate(frame[color_column].to_numpy()[mask]):
            if isinstance(value, np.generic):
                value = value.item()
            if value is None or value is pd.NA or value is pd.NaT or (type(value) is float and np.isnan(value)):
                value = None
            elif type(value) not in (str, int, float, bool) or (type(value) is float and not np.isfinite(value)):
                fail("SCATTER_GROUP_INVALID", "分类颜色列需要文本、有限数值或布尔值，请选择类别列。")
            identity = (type(value).__name__, value)
            if identity not in identities:
                if len(groups) >= 64:
                    fail("SCATTER_GROUP_LIMIT", "散点图最多支持 64 个颜色分组，请筛选类别或选择连续数值颜色列。")
                identities[identity] = len(groups)
                groups.append({"label": "（缺失）" if value is None else str(value), "value": value})
            membership[i] = identities[identity]
        labels = [group["label"] for group in groups]
        type_labels = {"NoneType": "空值", "str": "文本", "int": "整数", "float": "数值", "bool": "布尔值"}
        for group in groups:
            if labels.count(group["label"]) > 1:
                group["label"] += f"（{type_labels[type(group['value']).__name__]}）"
        if len({group['label'] for group in groups}) != len(groups):
            for i, group in enumerate(groups):
                group['label'] = f"{i + 1} · {group['label']}"
    else:
        groups = [{"label": f"{x_column} · {y_column}", "value": None}]

    # Keep both ends, global coordinate/color extrema and every category before
    # evenly sampling across the entire source order. Never take a leading slice.
    selected = set(range(len(indices))) if len(indices) <= 50_000 else {0, len(indices) - 1}
    if len(indices) > 50_000:
        for vector in (x, y, *([color_values] if color_values is not None else [])):
            selected.update((int(np.argmin(vector)), int(np.argmax(vector))))
        for i in range(len(groups)):
            selected.add(int(np.flatnonzero(membership == i)[0]))
        candidates = np.flatnonzero(~np.isin(np.arange(len(indices)), list(selected)))
        positions = np.linspace(0, len(candidates) - 1, 50_000 - len(selected), dtype=int)
        selected.update(int(i) for i in candidates[positions])
    selected_indices = np.array(sorted(selected), dtype=int)
    excluded_xy = int((~xy_mask).sum())
    excluded_color = int(xy_mask.sum()) - len(indices)
    omitted = len(indices) - len(selected_indices)
    warnings = []
    if excluded_xy:
        warnings.append(f"已排除 {excluded_xy} 行横轴或纵轴缺失、非数值或非有限值。")
    if excluded_color:
        warnings.append(f"另排除 {excluded_color} 行连续颜色缺失或非有限值。")
    if omitted:
        warnings.append(f"已绘制 {len(selected_indices)} / {len(indices)} 个有效点；按来源行均匀采样并保留极值和每个分组，原始数据未改动。")

    def scalar(value):
        if isinstance(value, np.generic):
            value = value.item()
        if value is None or value is pd.NA or value is pd.NaT or (type(value) is float and not np.isfinite(value)):
            return None
        if type(value) in (str, int, float, bool):
            return value
        return str(value)

    fig = go.Figure()
    hover_values = {column: frame[column].to_numpy() for column in hover}
    for i, group in enumerate(groups):
        subset = selected_indices[membership[selected_indices] == i]
        source_rows = indices[subset]
        customdata = [[int(row) + 1, *[scalar(hover_values[column][row]) for column in hover]] for row in source_rows]
        marker = {"size": 6, "opacity": 0.85}
        if color_values is not None:
            marker.update(color=color_values[subset].tolist(), coloraxis="coloraxis")
        tooltip = f"{escape(x_column)}：%{{x}}<br>{escape(y_column)}：%{{y}}<br>来源行：%{{customdata[0]}}"
        tooltip += "".join(f"<br>{escape(column)}：%{{customdata[{j + 1}]}}" for j, column in enumerate(hover))
        if color_values is not None:
            tooltip += f"<br>{escape(color_column)}：%{{marker.color}}"
        trace_class = go.Scattergl if len(selected_indices) > 1000 else go.Scatter
        fig.add_trace(trace_class(x=x[subset].tolist(), y=y[subset].tolist(), mode="markers", name=group["label"],
                                  marker=marker, customdata=customdata, hovertemplate=tooltip + "<extra>%{fullData.name}</extra>"))
        group.update(pointCount=len(subset), validPointCount=int((membership == i).sum()))
    fig.update_layout(title=params.get("title") or f"{x_column} · {y_column}",
                      xaxis={"title": x_column, "type": "linear"}, yaxis={"title": y_column, "type": "linear"},
                      showlegend=color_mode == "categorical", template=None)
    if color_values is not None:
        fig.update_layout(coloraxis={"colorscale": "Viridis", "colorbar": {"title": color_column}})
    metadata = {
        "schemaVersion": "mdi.table-scatter/1.0", "chartType": "scatter", "xColumn": x_column, "yColumn": y_column,
        "colorColumn": color_column, "colorMode": color_mode, "hoverColumns": hover,
        "inputCount": len(frame), "validPointCount": len(indices), "pointCount": len(selected_indices),
        "excludedCount": excluded_xy + excluded_color, "excludedCoordinateCount": excluded_xy, "excludedColorCount": excluded_color,
        "omittedPointCount": omitted, "sampling": "source-order-even-with-extrema-and-groups" if omitted else "none",
        "traces": len(groups), "groups": groups,
        "xRange": [float(x.min()), float(x.max())], "yRange": [float(y.min()), float(y.max())], "warnings": warnings,
    }
    return metadata, fig
