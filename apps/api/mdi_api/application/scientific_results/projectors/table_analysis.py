"""Read saved table outputs; never calculate scientific values from a plot."""
from __future__ import annotations

import math
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from mdi_api.domain.scientific_results.contracts import FactSourceLocator, ScientificFact, ScientificWarning


def _finite(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def _count(value: Any) -> bool:
    return type(value) is int and value >= 0


def _name(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 512


def _pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def valid_table_output(tool_id: str, kind: str, payload: dict[str, Any]) -> bool:
    """Only the tool's scientific output can satisfy suite coverage."""
    if tool_id in {"table.numeric_summary", "table.distribution_summary"}:
        if kind != "table_json" or not _count(payload.get("rowCount")):
            return False
        for family in ("numericColumns", "categoricalColumns"):
            columns = payload.get(family)
            if not isinstance(columns, dict) or any(not _name(name) or not isinstance(stats, dict)
                    or not _count(stats.get("count")) or stats["count"] > payload["rowCount"]
                    for name, stats in columns.items()):
                return False
            for name, stats in columns.items():
                if "column" in stats and stats["column"] != name:
                    return False
                if any(stats.get(key) is not None and not _finite(stats[key]) for key in
                       ("mean", "std", "min", "p25", "median", "p75", "max", "missingRate")):
                    return False
                if any(key in stats and not _count(stats[key]) for key in ("missing", "unique", "uniqueCount")):
                    return False
                if "missing" in stats and stats["count"] + stats["missing"] != payload["rowCount"]:
                    return False
                if any(key in stats and stats[key] > stats["count"] for key in ("unique", "uniqueCount")):
                    return False
                if stats.get("std") is not None and stats["std"] < 0:
                    return False
                if stats.get("missingRate") is not None and (
                        not 0 <= stats["missingRate"] <= 1 or "missing" not in stats or
                        not math.isclose(stats["missingRate"], stats["missing"] / payload["rowCount"]
                                         if payload["rowCount"] else 0, abs_tol=1e-12)):
                    return False
                if family == "numericColumns":
                    if any(key not in stats for key in ("mean", "std", "min", "median", "max")):
                        return False
                    if stats["count"] == 0 and any(stats.get(key) is not None for key in
                            ("mean", "std", "min", "p25", "median", "p75", "max")):
                        return False
                    low, high = stats.get("min"), stats.get("max")
                    if low is not None and high is not None and (low > high or any(
                            stats.get(key) is not None and not low <= stats[key] <= high
                            for key in ("mean", "p25", "median", "p75"))):
                        return False
                top = stats.get("topValues", [])
                if not isinstance(top, list) or any(not isinstance(item, dict) or not isinstance(item.get("value"), str)
                        or not _count(item.get("count")) for item in top):
                    return False
                if sum(item["count"] for item in top) > stats["count"]:
                    return False
        if tool_id == "table.numeric_summary":
            columns = payload.get("columns")
            if not isinstance(columns, list) or any(not isinstance(col, dict) or not _name(col.get("name"))
                    or not _count(col.get("missingCount")) or not _count(col.get("nonNullCount"))
                    or col["missingCount"] + col["nonNullCount"] != payload["rowCount"] for col in columns):
                return False
            names = [col["name"] for col in columns]
            return len(set(names)) == len(names) and all(set(payload[key]) <= set(names)
                    for key in ("numericColumns", "categoricalColumns"))
        return _count(payload.get("columnCount")) and len(set(payload["numericColumns"]) | set(payload["categoricalColumns"])) <= payload["columnCount"]
    if tool_id == "viz.correlation":
        if kind == "plotly_json":
            return isinstance(payload.get("data"), list) and any(isinstance(trace, dict)
                    and trace.get("type") == "heatmap" for trace in payload["data"])
        columns, matrix = payload.get("columns"), payload.get("matrix")
        if (kind != "table_json" or payload.get("chartType") != "correlation_heatmap"
                or payload.get("method") not in {"pearson", "spearman", "kendall"}
                or not isinstance(columns, list) or not 2 <= len(columns) <= 30
                or not all(_name(name) for name in columns) or len(set(columns)) != len(columns)
                or not isinstance(matrix, list) or len(matrix) != len(columns)
                or any(not isinstance(row, list) or len(row) != len(columns) for row in matrix)):
            return False
        valid = 0
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                other = matrix[j][i]
                if value is None:
                    if other is not None:
                        return False
                elif (not _finite(value) or not -1 <= value <= 1 or not _finite(other)
                      or not math.isclose(value, other, abs_tol=1e-12)
                      or (i == j and not math.isclose(value, 1, abs_tol=1e-12))):
                    return False
                elif j > i:
                    valid += 1
        pairs = len(columns) * (len(columns) - 1) // 2
        if payload.get("pairCount") != pairs or not _count(payload["pairCount"]):
            return False
        # This is the Registry's minimum setting, not an observed pair's sample count.
        return all(key not in payload or (_count(payload[key]) and payload[key] == expected)
                   for key, expected in (("validPairCount", valid), ("missingPairCount", pairs - valid))) and (
                   "minNonNullCount" not in payload or (_count(payload["minNonNullCount"]) and payload["minNonNullCount"] >= 1))
    if kind != "plotly_json" or not isinstance(payload.get("figure"), dict):
        return False
    if tool_id == "viz.histogram":
        return (payload.get("chartType") == "histogram" and _name(payload.get("column"))
                and _count(payload.get("count")) and payload["count"] > 0
                and _count(payload.get("bins")) and payload["bins"] > 0
                and all(_finite(payload.get(key)) for key in ("min", "max", "mean", "median"))
                and ("schemaVersion" not in payload or _valid_histogram_counts(payload)))
    if tool_id == "viz.scatter":
        return (payload.get("chartType") == "scatter" and _name(payload.get("xColumn"))
                and _name(payload.get("yColumn")) and _count(payload.get("pointCount"))
                and all(isinstance(payload.get(key), list) and len(payload[key]) == 2
                        and all(value is None or _finite(value) for value in payload[key]) for key in ("xRange", "yRange"))
                and ("schemaVersion" not in payload or _valid_scatter_points(payload)))
    return False


def _valid_scatter_points(payload: dict[str, Any]) -> bool:
    p = payload
    if (p.get("schemaVersion") != "mdi.table-scatter/1.0" or p.get("colorMode") not in {"none", "numeric", "categorical"}
            or not all(_count(p.get(key)) for key in ("inputCount", "validPointCount", "excludedCount", "excludedCoordinateCount", "excludedColorCount", "omittedPointCount", "traces"))
            or not 1 <= p["pointCount"] <= 50_000 or p["inputCount"] != p["validPointCount"] + p["excludedCount"]
            or p["validPointCount"] != p["pointCount"] + p["omittedPointCount"]
            or p["excludedCount"] != p["excludedCoordinateCount"] + p["excludedColorCount"]
            or (p.get("colorColumn") is not None if p["colorMode"] == "none" else not _name(p.get("colorColumn")))
            or p["colorMode"] != "numeric" and p["excludedColorCount"] != 0
            or p.get("sampling") != ("source-order-even-with-extrema-and-groups" if p["omittedPointCount"] else "none")):
        return False
    traces, groups, hover = p["figure"].get("data"), p.get("groups"), p.get("hoverColumns")
    if (not isinstance(traces, list) or not 1 <= len(traces) <= 64 or not isinstance(groups, list)
            or len(groups) != len(traces) or len(traces) != p["traces"]
            or p["colorMode"] != "categorical" and len(groups) != 1
            or not isinstance(hover, list) or len(hover) > 8 or not all(_name(v) for v in hover)
            or len(set(hover)) != len(hover)):
        return False
    layout = p["figure"].get("layout")
    if (not isinstance(layout, dict) or any(key in layout for key in ("shapes", "annotations", "grid"))
            or any(not isinstance(layout.get(key), dict) or layout[key].get("type") != "linear" for key in ("xaxis", "yaxis"))):
        return False
    rows, names = set(), set()
    x_values, y_values = [], []
    valid = 0
    for trace, group in zip(traces, groups):
        if (not isinstance(trace, dict) or not isinstance(group, dict) or trace.get("type") not in {"scatter", "scattergl"}
                or trace.get("mode") != "markers" or not isinstance(group.get("label"), str) or group["label"] in names
                or trace.get("name") != group["label"] or not _count(group.get("pointCount")) or not group["pointCount"]
                or not _count(group.get("validPointCount")) or group["validPointCount"] < group["pointCount"]):
            return False
        names.add(group["label"])
        x, y, custom = trace.get("x"), trace.get("y"), trace.get("customdata")
        if (not isinstance(x, list) or not isinstance(y, list) or not isinstance(custom, list)
                or any(len(v) != group["pointCount"] for v in (x, y, custom)) or not all(_finite(v) for v in (*x, *y))):
            return False
        marker = trace.get("marker", {})
        if (not isinstance(marker, dict)
                or any(key in trace for key in ("transforms", "error_x", "error_y", "fill", "stackgroup", "xaxis", "yaxis"))
                or trace.get("visible", True) is not True):
            return False
        if p["colorMode"] == "numeric":
            colors = marker.get("color")
            if (not isinstance(colors, list) or len(colors) != len(x) or not all(_finite(v) for v in colors)
                    or marker.get("coloraxis") != "coloraxis"):
                return False
        elif "coloraxis" in marker or isinstance(marker.get("color"), list):
            return False
        for row in custom:
            if (not isinstance(row, list) or len(row) != len(hover) + 1 or not _count(row[0])
                    or not 1 <= row[0] <= p["inputCount"] or row[0] in rows
                    or any(v is not None and not isinstance(v, (str, bool)) and not _finite(v) for v in row[1:])):
                return False
            rows.add(row[0])
        x_values.extend(x); y_values.extend(y); valid += group["validPointCount"]
    return (len(rows) == p["pointCount"] and valid == p["validPointCount"]
            and p["xRange"] == [min(x_values), max(x_values)] and p["yRange"] == [min(y_values), max(y_values)])


def _valid_histogram_counts(payload: dict[str, Any]) -> bool:
    if payload.get("schemaVersion") != "mdi.table-histogram/1.0":
        return False
    bins, count = payload["bins"], payload["count"]
    edges, counts, groups = payload.get("binEdges"), payload.get("binCounts"), payload.get("groups")
    if (not 1 <= bins <= 4096 or not isinstance(edges, list) or len(edges) != bins + 1
            or not all(_finite(v) for v in edges) or any(a >= b for a, b in zip(edges, edges[1:]))
            or not isinstance(counts, list) or len(counts) != bins or not all(_count(v) for v in counts)
            or sum(counts) != count or not _count(payload.get("inputCount")) or not _count(payload.get("excludedCount"))
            or payload["inputCount"] != count + payload["excludedCount"]
            or not edges[0] <= payload["min"] <= payload["mean"] <= payload["max"] <= edges[-1]
            or not payload["min"] <= payload["median"] <= payload["max"]
            or payload.get("intervalConvention") != "left-closed-right-open; final bin includes right edge"
            or not isinstance(groups, list) or not 1 <= len(groups) <= 16 or len(groups) * bins > 50_000):
        return False
    group_by = payload.get("groupBy")
    figure = payload["figure"]
    traces, layout = figure.get("data"), figure.get("layout")
    if ((group_by is not None and not _name(group_by)) or not isinstance(traces, list) or len(traces) != len(groups)
            or not isinstance(layout, dict) or layout.get("barmode") != ("stack" if group_by is not None else "overlay")):
        return False
    totals, names = [0] * bins, set()
    for group, trace in zip(groups, traces):
        if (not isinstance(group, dict) or not _name(group.get("label")) or group["label"] in names
                or not _count(group.get("count")) or not group["count"]
                or not isinstance(group.get("binCounts"), list) or len(group["binCounts"]) != bins
                or not all(_count(v) for v in group["binCounts"]) or sum(group["binCounts"]) != group["count"]):
            return False
        if (not isinstance(trace, dict) or trace.get("type") != "bar" or trace.get("name") != group["label"]
                or trace.get("y") != group["binCounts"]
                or trace.get("width") != [b - a for a, b in zip(edges, edges[1:])]
                or trace.get("x") != [a + (b - a) / 2 for a, b in zip(edges, edges[1:])]):
            return False
        names.add(group["label"])
        totals = [a + b for a, b in zip(totals, group["binCounts"])]
    return totals == counts and (group_by is not None or len(groups) == 1)


def table_facts(artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificFact]:
    artifact_id = str(artifact.get("id") or artifact.get("artifactId"))
    facts: list[ScientificFact] = []

    def add(predicate: str, pointer: str, *, subject: str = "summary", unit: str | None = None):
        current: Any = payload
        for token in pointer.lstrip("/").split("/"):
            token = token.replace("~1", "/").replace("~0", "~")
            try:
                current = current[int(token)] if isinstance(current, list) else current[token]
            except (KeyError, IndexError, TypeError, ValueError):
                return
        if current is None or not (_finite(current) or isinstance(current, str)):
            return
        identity = f"{artifact_id}:{subject}:{predicate}:{pointer}"
        facts.append(ScientificFact(
            fact_id=f"fact.{uuid5(NAMESPACE_URL, identity).hex}", predicate=predicate,
            subject_ref=f"{artifact_id}:{subject}", value=current, unit=unit,
            source=FactSourceLocator(artifact_id=artifact_id, artifact_locator=pointer),
        ))

    chart = payload.get("chartType")
    if chart == "correlation_heatmap":
        for key, predicate in (("method", "method"), ("pairCount", "pair_count"),
                               ("validPairCount", "valid_pair_count"), ("missingPairCount", "missing_pair_count"),
                               ("minNonNullCount", "minimum_sample_count")):
            add(f"correlation.{predicate}", f"/{key}", unit=None if key == "method" else "count")
        for i, row in enumerate(payload["matrix"]):
            for j in range(i + 1, len(row)):
                if row[j] is None:
                    continue
                subject = f"pair-{i}-{j}"
                add("correlation.left_column", f"/columns/{i}", subject=subject)
                add("correlation.right_column", f"/columns/{j}", subject=subject)
                add("correlation.coefficient", f"/matrix/{i}/{j}", subject=subject)
    elif chart == "histogram":
        for key in ("column", "count", "bins", "min", "max", "mean", "median"):
            add(f"histogram.{key}", f"/{key}", unit="count" if key in {"count", "bins"} else None)
        for key, predicate in (("inputCount", "input_count"), ("excludedCount", "excluded_count")):
            add(f"histogram.{predicate}", f"/{key}", unit="count")
    elif chart == "scatter":
        for key, predicate in (("xColumn", "x_column"), ("yColumn", "y_column"), ("pointCount", "point_count")):
            add(f"scatter.{predicate}", f"/{key}", unit="count" if key == "pointCount" else None)
        for axis in ("x", "y"):
            for index, bound in enumerate(("min", "max")):
                add(f"scatter.{axis}_{bound}", f"/{axis}Range/{index}")
        for key, predicate in (("inputCount", "input_count"), ("validPointCount", "valid_point_count"),
                               ("excludedCount", "excluded_count"), ("omittedPointCount", "omitted_point_count")):
            add(f"scatter.{predicate}", f"/{key}", unit="count")
    elif "numericColumns" in payload:
        add("table.row_count", "/rowCount", unit="count")
        add("table.column_count", "/columnCount", unit="count")
        names = {col["name"]: i for i, col in enumerate(payload.get("columns", []))}
        for family, prefix in (("numericColumns", "numeric"), ("categoricalColumns", "categorical")):
            for index, (name, stats) in enumerate(payload[family].items()):
                if index >= 30:
                    break
                base, subject = f"/{family}/{_pointer(name)}", f"{prefix}-{index}"
                if "column" in stats:
                    add(f"table.{prefix}.column", f"{base}/column", subject=subject)
                elif name in names:
                    add(f"table.{prefix}.column", f"/columns/{names[name]}/name", subject=subject)
                else:
                    # Older distribution files have dictionary keys only. Do not
                    # synthesize a name as though it were a saved scalar value.
                    continue
                for key, predicate in (("count", "count"), ("missing", "missing"), ("missingRate", "missing_rate"),
                        ("mean", "mean"), ("std", "std"), ("min", "min"), ("p25", "p25"), ("median", "median"),
                        ("p75", "p75"), ("max", "max"), ("uniqueCount", "unique_count"), ("unique", "unique_count")):
                    add(f"table.{prefix}.{predicate}", f"{base}/{key}", subject=subject,
                        unit="count" if key in {"count", "missing", "uniqueCount", "unique"} else None)
                if name in names:
                    add(f"table.{prefix}.missing", f"/columns/{names[name]}/missingCount", subject=subject, unit="count")
                for rank, item in enumerate(stats.get("topValues", [])[:5]):
                    if not isinstance(item, dict) or not _name(item.get("value")) or not _count(item.get("count")):
                        continue
                    category = f"{subject}-category-{rank}"
                    add("table.category.column", f"{base}/column", subject=category)
                    add("table.category.value", f"{base}/topValues/{rank}/value", subject=category)
                    add("table.category.count", f"{base}/topValues/{rank}/count", subject=category, unit="count")
    return facts


def table_warnings(artifact_id: str, payload: dict[str, Any]) -> list[ScientificWarning]:
    messages = []
    if payload.get("chartType") == "correlation_heatmap" and any(value is None
            for i, row in enumerate(payload["matrix"]) for value in row[i + 1:]):
        messages.append(("TABLE_ANALYSIS_MISSING_CORRELATIONS", "部分变量对没有有效相关系数；空值不代表零相关，最低样本设置不代表实际共同样本数。"))
    if "numericColumns" in payload:
        if "columns" not in payload and any("column" not in stats for family in ("numericColumns", "categoricalColumns") for stats in payload[family].values()):
            messages.append(("TABLE_ANALYSIS_LEGACY_COLUMN_IDENTITY", "旧分布文件未保存可直接引用的列名；该文件的逐列统计仍可查看，但未转为模型事实。"))
        if any(len(payload[family]) > 30 or any(len(stats.get("topValues", [])) > 5 for stats in payload[family].values())
               for family in ("numericColumns", "categoricalColumns")):
            messages.append(("TABLE_ANALYSIS_FACT_SUBSET", "模型事实最多保留每类前 30 列及每列前 5 个类别；完整统计保留在原始结果文件。"))
    if payload.get("chartType") == "scatter" and "too_many_points_warning" in payload.get("warnings", []):
        messages.append(("TABLE_ANALYSIS_SCATTER_TRUNCATED", "散点结果仅保留前 50000 个有效点；范围统计限于这些点。"))
    if payload.get("schemaVersion") == "mdi.table-scatter/1.0":
        if payload["omittedPointCount"]:
            messages.append(("TABLE_ANALYSIS_SCATTER_SAMPLED", f"散点图显示 {payload['pointCount']} / {payload['validPointCount']} 个有效点，按来源行均匀采样并保留坐标极值和每个分组。"))
        if payload["excludedCount"]:
            messages.append(("TABLE_ANALYSIS_SCATTER_EXCLUDED", f"散点图排除了 {payload['excludedCount']} 行不具备完整有限坐标或连续颜色的记录。"))
    return [ScientificWarning(warning_id=f"warning.{uuid5(NAMESPACE_URL, artifact_id + code).hex}",
            code=code, message=message, source_ref=artifact_id) for code, message in messages]
