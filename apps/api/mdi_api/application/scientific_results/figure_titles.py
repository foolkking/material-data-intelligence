"""Presentation labels from exact committed figure producers, never filenames."""
from collections.abc import Sequence
from typing import Any


def scientific_figure_title(
    title: str, artifact_ids: Sequence[str], *, artifacts: Sequence[dict[str, Any]],
    calls: Sequence[dict[str, Any]], job_id: str, project_id: str,
) -> str:
    return _scientific_artifact_title(title, artifact_ids, artifacts=artifacts, calls=calls,
                                     job_id=job_id, project_id=project_id, kind="figure")


def scientific_table_title(
    title: str, artifact_ids: Sequence[str], *, artifacts: Sequence[dict[str, Any]],
    calls: Sequence[dict[str, Any]], job_id: str, project_id: str,
) -> str:
    return _scientific_artifact_title(title, artifact_ids, artifacts=artifacts, calls=calls,
                                     job_id=job_id, project_id=project_id, kind="table")


def _scientific_artifact_title(
    title: str, artifact_ids: Sequence[str], *, artifacts: Sequence[dict[str, Any]],
    calls: Sequence[dict[str, Any]], job_id: str, project_id: str, kind: str,
) -> str:
    table_title = "数值表格分布与相关性分析"
    is_table = title == table_title or title.startswith(table_title + " · ")
    if (title != "材料回归评估" and not is_table) or len(artifact_ids) != 1 or not job_id or not project_id:
        return title
    matches = [a for a in artifacts if str(a.get("id") or a.get("artifactId")) == artifact_ids[0]]
    if len(matches) != 1:
        return title
    artifact = matches[0]
    artifact_type = artifact.get("type")
    allowed = {"plotly_json", "plotly_html", "preview_png"} if kind == "figure" else {"metrics_json", "table_json", "table_csv"}
    if (artifact.get("jobId") != job_id or artifact.get("projectId") != project_id or artifact_type not in allowed):
        return title
    producer_id = artifact.get("toolCallId")
    producers = [c for c in calls if producer_id and c.get("id") == producer_id]
    if len(producers) != 1 or producers[0].get("jobId") != job_id:
        return title
    tool_id = producers[0].get("toolId")
    if is_table:
        producer = producers[0]
        if str(producer.get("state") or producer.get("status") or "").lower() != "completed":
            return title
        label = _table_analysis_label(tool_id, kind, artifact_type, producer.get("paramsJson"))
        result = label + title[len(table_title):] if label else title
        return result if len(result) <= 512 else title
    if kind == "figure":
        return {"ml.density_scatter": "真实值与预测值", "ml.error_distribution": "残差分布"}.get(tool_id, title)
    if artifact_type == "metrics_json":
        return {"ml.basic_metrics": "回归评估指标", "ml.error_distribution": "回归评估指标（残差分析）"}.get(tool_id, title)
    return {"ml.error_distribution": "高误差样本（残差分析）", "ml.outlier_table": "高误差样本",
            "ml.regression_evaluation": "材料属性回归评估"}.get(tool_id, title)


def _table_analysis_label(tool_id: str, kind: str, artifact_type: str, raw_params: Any) -> str | None:
    params = raw_params if isinstance(raw_params, dict) else {}

    def column(key: str) -> str | None:
        value = params.get(key)
        return value if isinstance(value, str) and value.strip() and len(value) <= 120 else None

    if tool_id == "viz.correlation":
        if kind == "table" and artifact_type != "table_json":
            return None
        raw_method = params.get("method", "pearson") if isinstance(raw_params, dict) else None
        method = {"pearson": "Pearson", "spearman": "Spearman"}.get(raw_method) if isinstance(raw_method, str) else None
        return (method + " " if method else "") + ("相关矩阵" if kind == "figure" else "相关系数")
    if kind == "table" and artifact_type == "table_json":
        return {"table.distribution_summary": "数据分布概览", "table.numeric_summary": "数值统计"}.get(tool_id)
    if kind == "figure" and tool_id == "viz.histogram":
        selected = column("column")
        return "直方图" + (f" · {selected}" if selected else "")
    if kind == "figure" and tool_id == "viz.scatter":
        x, y = column("xColumn"), column("yColumn")
        return "散点图" + (f" · {x} × {y}" if x and y else "")
    return None
