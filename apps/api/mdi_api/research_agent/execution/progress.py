from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from mdi_api.research_agent.execution.diagnostics import execution_step_status
from mdi_api.research_agent.execution.schemas import (
    ExecutionOutcome, ExecutionStepStatus, ProgressOutput, ProgressWarning,
    ResearchProgressStep, ResearchProgressView,
)
from mdi_api.research_agent.schemas import ResearchTurnStatus


def _value(row: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if isinstance(row, dict) and name in row:
            return row[name]
        if hasattr(row, name):
            return getattr(row, name)
    return default


class GenericScientificProgressProjector:
    """Capability-level projection; it never exposes Tool or worker identities."""

    def project(self, *, turn: dict[str, Any], capability_plan: dict[str, Any] | None, analysis_plan: dict[str, Any], job: dict[str, Any], tool_calls: list[dict[str, Any]], artifacts: list[dict[str, Any]], summary: Any = None) -> ResearchProgressView:
        plan_payload = analysis_plan.get("analysisPlan") or analysis_plan.get("analysis_plan_json") or {}
        plan_steps = list(plan_payload.get("steps") or [])
        calls_by_step = {str(_value(call, "stepId", "step_id")): call for call in tool_calls}
        artifacts_by_call: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for artifact in artifacts:
            call_id = _value(artifact, "toolCallId", "tool_call_id")
            artifacts_by_call[str(call_id)].append(artifact)
        steps: list[ResearchProgressStep] = []
        outputs: list[ProgressOutput] = []
        step_metadata = (capability_plan or {}).get("step_metadata") or {}
        for step in plan_steps:
            step_id = str(_value(step, "stepId", "step_id", default="step"))
            call = calls_by_step.get(step_id)
            raw_status = str(_value(call, "status", default="planned")) if call else "planned"
            status = execution_step_status(raw_status, str(job.get("status") or ""))
            call_id = str(_value(call, "id", default="")) if call else ""
            step_artifacts = artifacts_by_call.get(call_id, [])
            metadata = step_metadata.get(step_id) or {}
            display_name = str(metadata.get("display_name") or _value(step, "purpose", "reason", default="科学分析步骤"))
            running_label = str(metadata.get("running_label") or f"正在{display_name}") if status == ExecutionStepStatus.RUNNING else None
            completed_label = str(metadata.get("completed_label") or f"{display_name}已完成") if status == ExecutionStepStatus.SUCCEEDED else None
            warning = None
            if status == ExecutionStepStatus.FAILED:
                warning = "该步骤未能完成，已保留已生成的输出。"
            steps.append(ResearchProgressStep(step_id=step_id, display_name=display_name, status=status, running_label=running_label, completed_label=completed_label, output_available=bool(step_artifacts), warning=warning))
            for index, artifact in enumerate(step_artifacts, 1):
                artifact_id = str(_value(artifact, "id", "artifactId"))
                created = _value(artifact, "createdAt", "created_at", default=datetime.now(timezone.utc))
                outputs.append(ProgressOutput(output_key=f"{step_id}.output_{index}", step_id=step_id, display_label=f"{display_name}输出已生成", artifact_id=artifact_id, output_slot=None, preview_available=bool(_value(artifact, "previewKey", "preview_key")), available_at=created))
        outcome = None
        if summary is not None:
            outcome = ExecutionOutcome(str(_value(summary, "execution_outcome", "outcome")))
        completed = sum(1 for item in steps if item.status == ExecutionStepStatus.SUCCEEDED)
        active = [item.step_id for item in steps if item.status == ExecutionStepStatus.RUNNING]
        warnings = [ProgressWarning(code="EXECUTION_STEP_FAILED", message=item.warning) for item in steps if item.warning]
        if summary is not None:
            raw_summary = _value(summary, "summary_json", default={}) or {}
            for warning in raw_summary.get("warnings") or []:
                warnings.append(ProgressWarning.model_validate(warning))
        status = ResearchTurnStatus(str(turn["status"]))
        return ResearchProgressView(contract_version="1.0", turn_id=UUID(str(turn["id"])), status=status, response_kind="SCIENTIFIC_EXECUTION", plan_title=str(plan_payload.get("goal") or "科学分析"), steps=steps, active_step_ids=active, completed_step_count=completed, total_step_count=len(steps), incremental_outputs=outputs, warnings=warnings, execution_outcome=outcome, result_projection_pending=status == ResearchTurnStatus.RESULT_PENDING)
