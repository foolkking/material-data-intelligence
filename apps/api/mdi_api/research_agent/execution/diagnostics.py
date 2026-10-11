from __future__ import annotations

from typing import Any

from mdi_api.research_agent.execution.schemas import ExecutionStepStatus, ExecutionWarning


# Reviewed product explanations only: event messages, paths and exception text
# are deliberately excluded, even when their error code is recognized.
_FAILURE_MESSAGES = {
    "ROOT_RESOURCE_HASH_MISMATCH": "来源数据与保存的解析版本未通过一致性校验。请重新选择材料和版本后重试；若仍失败，请重新解析来源文件。",
    "ROOT_RESOURCE_HASH_MISSING": "所选来源缺少完整性校验信息。请重新解析来源文件后再运行。",
    "ROOT_RESOURCE_UNRESOLVED": "所选来源数据无法读取。请确认文件和版本仍可用，再重新选择材料。",
    "ROOT_PROFILE_RESOURCE_MISSING": "所选文件缺少对应的解析结果。请重新解析来源文件后再运行。",
    "ROOT_PROFILE_SCOPE_MISMATCH": "所选材料与解析版本不匹配。请重新选择材料和版本后再运行。",
    "ROOT_RESOURCE_SCOPE_MISMATCH": "分析方案中的来源归属不匹配。请重新选择材料并提交问题。",
    "ROOT_RESOURCE_KIND_MISMATCH": "所选数据类型与分析要求不匹配。请调整所选材料或分析问题。",
    "CORRELATION_PARAMS_INVALID": "相关性分析参数未通过校验。请选择 2–30 个不重复的数值列，并检查统计方法和最少有效样本数后重试。",
    "CORRELATION_COLUMN_LIMIT_EXCEEDED": "相关性分析一次最多支持 30 个数值列。请明确选择需要比较的列后重试。",
    "CORRELATION_COLUMN_IDENTITY_INVALID": "所选数据的列名不唯一或不是文本，无法确定相关性分析的列。请修正列名后重试。",
    "CORRELATION_NO_VALID_PAIRS": "所选列之间没有可计算的相关系数。请检查共同有效样本是否足够，并选择有变化的数值列后重试。",
    "HISTOGRAM_PARAMS_INVALID": "直方图参数未通过校验。请选择数值列，并将分箱数设为 1–4096 的整数。",
    "HISTOGRAM_COLUMN_INVALID": "所选列不存在或列名不唯一，请检查数据列后重试。",
    "HISTOGRAM_VALUES_INVALID": "直方图需要有限实数，请检查缺失值、无效数据或复数列后重试。",
    "HISTOGRAM_RANGE_INVALID": "当前数值范围无法生成精确分箱，请减少分箱数或调整数值尺度后重试。",
    "HISTOGRAM_GROUP_INVALID": "分组列需要文本、有限数值或布尔值，请选择类别列后重试。",
    "HISTOGRAM_GROUP_LIMIT": "分组直方图最多支持 16 组和 50000 个分箱记录，请减少分组或分箱数。",
    "SCATTER_PARAMS_INVALID": "散点图参数未通过校验。请选择横纵轴数值列，悬停信息最多选择 8 个不重复的数据列。",
    "SCATTER_COLUMN_INVALID": "所选列不存在或列名不唯一，请检查数据列后重试。",
    "SCATTER_VALUES_INVALID": "所选横纵轴与连续颜色列没有共同的有限实数，请检查所选列和缺失数据。",
    "SCATTER_RANGE_INVALID": "所选数值跨度超出绘图范围，请调整数值尺度后重试。",
    "SCATTER_GROUP_INVALID": "分类颜色列需要文本、有限数值或布尔值，请选择类别列。",
    "SCATTER_GROUP_LIMIT": "散点图最多支持 64 个颜色分组，请筛选类别或选择连续数值颜色列。",
    "EXECUTION_FAILED": "本次科学分析未能完成，现有记录不足以确定具体原因。可以重新运行；若再次失败，请联系管理员检查任务记录。",
    "EXECUTION_PARTIAL": "部分科学分析未能完成，已生成的结果仍可查看。可以调整问题或重新运行。",
}


def execution_failure_warning(code: str) -> ExecutionWarning | None:
    message = _FAILURE_MESSAGES.get(code)
    return ExecutionWarning(code=code, message=message) if message else None


def current_attempt_events(job: dict[str, Any], events: list[Any]) -> list[dict[str, Any]]:
    """Use the durable claim boundary for older, untagged worker events."""
    rows = [event.model_dump(mode="json") if hasattr(event, "model_dump") else event for event in events]
    attempt = int(job.get("executionAttempt") or 0)
    claims = [row for row in rows if row.get("eventType") in {"job.claimed", "job.reclaimed"}]
    starts = [int(row["seq"]) for row in claims if (row.get("payload") or {}).get("executionAttempt") == attempt]
    start = max(starts, default=None)
    end = min((int(row["seq"]) for row in claims if start is not None and int(row["seq"]) > start), default=None)
    selected = []
    for row in rows:
        explicit_attempt = (row.get("payload") or {}).get("executionAttempt")
        if explicit_attempt is not None:
            if explicit_attempt == attempt:
                selected.append(row)
        elif start is not None:
            seq = int(row.get("seq") or 0)
            if seq >= start and (end is None or seq < end):
                selected.append(row)
        elif attempt == 0 and not claims:
            selected.append(row)
    return selected


def execution_warnings(job: dict[str, Any], events: list[dict[str, Any]]) -> list[ExecutionWarning]:
    if job.get("status") not in {"failed", "partial_success"}:
        return []
    warnings: dict[str, ExecutionWarning] = {}
    for event in events:
        if event.get("status") != "error":
            continue
        payload = event.get("payload") or {}
        code = ""
        if event.get("eventType") in {"dependency.validation_aborted", "dependency.binding_failed"}:
            code = str(payload.get("errorCode") or "")
        elif event.get("eventType") == "tool.failed" and payload.get("toolId") in {"viz.correlation", "viz.histogram", "viz.scatter"}:
            error = payload.get("error")
            if isinstance(error, dict):
                details = error.get("details")
                reason = details.get("errorType") if isinstance(details, dict) else None
                prefix = {"viz.correlation": "CORRELATION", "viz.histogram": "HISTOGRAM", "viz.scatter": "SCATTER"}[payload["toolId"]]
                if error.get("code") == "TOOL_PARAM_INVALID":
                    code = f"{prefix}_PARAMS_INVALID"
                elif error.get("code") == "TOOL_INPUT_INVALID" and isinstance(reason, str) and reason.startswith(f"{prefix}_") and reason in _FAILURE_MESSAGES:
                    code = reason
        warning = execution_failure_warning(code)
        if warning:
            warnings[warning.code] = warning
    if not warnings:
        code = "EXECUTION_PARTIAL" if job["status"] == "partial_success" else "EXECUTION_FAILED"
        warnings[code] = ExecutionWarning(code=code, message=_FAILURE_MESSAGES[code])
    return list(warnings.values())


def execution_step_status(raw_status: str, job_status: str) -> ExecutionStepStatus:
    status = {
        "running": ExecutionStepStatus.RUNNING,
        "started": ExecutionStepStatus.RUNNING,
        "succeeded": ExecutionStepStatus.SUCCEEDED,
        "completed": ExecutionStepStatus.SUCCEEDED,
        "failed": ExecutionStepStatus.FAILED,
        "error": ExecutionStepStatus.FAILED,
        "skipped": ExecutionStepStatus.SKIPPED,
        "canceled": ExecutionStepStatus.CANCELED,
        "cancelled": ExecutionStepStatus.CANCELED,
    }.get(raw_status, ExecutionStepStatus.PENDING)
    if job_status in {"canceled", "cancelled"} and status in {ExecutionStepStatus.PENDING, ExecutionStepStatus.RUNNING}:
        return ExecutionStepStatus.CANCELED
    if job_status in {"failed", "partial_success", "completed"}:
        if status == ExecutionStepStatus.PENDING:
            return ExecutionStepStatus.SKIPPED
        if status == ExecutionStepStatus.RUNNING:
            return ExecutionStepStatus.FAILED
    return status
