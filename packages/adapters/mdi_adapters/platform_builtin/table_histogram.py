"""A single saved binning drives histogram plots and downstream inspection."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from ..errors import ToolExecutionError


def saved_histogram(frame: pd.DataFrame, params: dict[str, Any], *, tool_id: str):
    def fail(reason: str, message: str, *, parameter: bool = False):
        raise ToolExecutionError("TOOL_PARAM_INVALID" if parameter else "TOOL_INPUT_INVALID",
                                 message, tool_id, details={"errorType": reason})

    column, group_by, bins = params.get("column"), params.get("groupBy"), params.get("bins", 20)
    if type(bins) is not int or not 1 <= bins <= 4096:
        fail("HISTOGRAM_PARAMS_INVALID", "直方图分箱数必须是 1–4096 的整数。", parameter=True)
    if not isinstance(column, str) or not column or (group_by is not None and (not isinstance(group_by, str) or not group_by)):
        fail("HISTOGRAM_PARAMS_INVALID", "请选择数值列；分组时还需选择分组列。", parameter=True)
    for name in (column, *([group_by] if group_by is not None else [])):
        if sum(item == name for item in frame.columns) != 1:
            fail("HISTOGRAM_COLUMN_INVALID", "所选列不存在或列名不唯一，请检查数据列后重试。")
    numeric = pd.to_numeric(frame[column], errors="coerce")
    if np.iscomplexobj(numeric):
        fail("HISTOGRAM_VALUES_INVALID", "直方图需要有限实数，请选择实数列后重试。")
    raw = numeric.to_numpy(dtype=float, na_value=np.nan)
    mask = np.isfinite(raw)
    values = raw[mask]
    if not len(values):
        fail("HISTOGRAM_VALUES_INVALID", "所选列没有有限数值，请检查缺失值和无效数据。")
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            counts, edges = np.histogram(values, bins=bins)
            widths = np.diff(edges)
            centers = edges[:-1] + widths / 2
            # Scaling avoids overflow in means and even-sized medians.
            scale = max(float(np.max(np.abs(values))), 1.0)
            mean = float(np.mean(values / scale) * scale)
            median = float(np.median(values / scale) * scale)
        if not (np.isfinite(edges).all() and np.isfinite(widths).all() and (widths > 0).all()
                and np.isfinite(centers).all() and int(counts.sum()) == len(values)):
            raise ValueError("unrepresentable bins")
    except (ValueError, IndexError, OverflowError, FloatingPointError):
        fail("HISTOGRAM_RANGE_INVALID", "当前数值范围无法生成精确分箱，请减少分箱数或调整数值尺度后重试。")

    groups: list[dict[str, Any]] = []
    samples: list[list[float]] = []
    identities: dict[tuple[str, Any], int] = {}
    if group_by is not None:
        for value, group in zip(values, frame[group_by].to_numpy()[mask], strict=True):
            if isinstance(group, np.generic):
                group = group.item()
            if group is None or group is pd.NA or group is pd.NaT or (type(group) is float and np.isnan(group)):
                group = None
            elif type(group) not in (str, int, float, bool) or (type(group) is float and not np.isfinite(group)):
                fail("HISTOGRAM_GROUP_INVALID", "分组列需要文本、有限数值或布尔值，请选择类别列后重试。")
            identity = (type(group).__name__, group)
            if identity not in identities:
                if len(groups) >= 16 or (len(groups) + 1) * bins > 50_000:
                    fail("HISTOGRAM_GROUP_LIMIT", "分组直方图最多支持 16 组和 50000 个分箱记录，请减少分组或分箱数。")
                identities[identity] = len(groups)
                # Typed keys prevent numeric and textual labels from merging.
                label = "（缺失）" if group is None else str(group)
                groups.append({"value": group, "label": label})
                samples.append([])
            samples[identities[identity]].append(float(value))
        labels = [group["label"] for group in groups]
        for group in groups:
            if labels.count(group["label"]) > 1:
                group["label"] += f" [{type(group['value']).__name__}]"
        # Prefix only remaining collisions (including literal typed labels).
        if len({group['label'] for group in groups}) != len(groups):
            for index, group in enumerate(groups):
                group['label'] = f"{index + 1} · {group['label']}"
        for group, group_values in zip(groups, samples, strict=True):
            group.update(count=len(group_values), binCounts=np.histogram(group_values, bins=edges)[0].tolist())
    else:
        groups = [{"value": None, "label": column, "count": len(values), "binCounts": counts.tolist()}]

    excluded = len(frame) - len(values)
    metadata = {
        "schemaVersion": "mdi.table-histogram/1.0", "chartType": "histogram", "column": column,
        "inputCount": len(frame), "count": len(values), "excludedCount": excluded,
        "bins": bins, "binEdges": edges.tolist(), "binCounts": counts.tolist(),
        "groupBy": group_by, "groups": groups,
        "intervalConvention": "left-closed-right-open; final bin includes right edge",
        "min": float(values.min()), "max": float(values.max()), "mean": mean, "median": median,
        "warnings": [f"已排除 {excluded} 行缺失、非数值或非有限值。"] if excluded else [],
    }
    fig = go.Figure()
    intervals = [[float(edges[i]), float(edges[i + 1]), "]" if i == bins - 1 else ")"] for i in range(bins)]
    for group in groups:
        fig.add_bar(x=centers.tolist(), y=group["binCounts"], width=widths.tolist(), name=group["label"],
                    customdata=intervals,
                    hovertemplate="区间：[%{customdata[0]}, %{customdata[1]}%{customdata[2]}<br>样本数：%{y}<extra>%{fullData.name}</extra>")
    fig.update_layout(title=params.get("title") or f"{column} 分布", xaxis_title=column,
                      yaxis_title="样本数", barmode="stack" if group_by is not None else "overlay", bargap=0,
                      xaxis={"type": "linear", "range": [float(edges[0]), float(edges[-1])]},
                      yaxis={"type": "linear", "rangemode": "tozero"}, showlegend=group_by is not None)
    return metadata, fig
