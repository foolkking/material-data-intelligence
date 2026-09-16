from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from mdi_api.research_agent.capabilities.schemas import CapabilityPlan, CapabilityResolution
from mdi_api.research_agent.execution.fingerprint import execution_source_fingerprint
from mdi_api.research_agent.execution.progress import GenericScientificProgressProjector
from mdi_api.research_agent.execution.schemas import (
    ExecutionArtifactRef,
    ExecutionOutcome,
    ExecutionStepStatus,
    ExecutionStepSummary,
    ExecutionWarning,
    ResearchExecutionSummary,
)
from mdi_api.research_agent.schemas import (
    TERMINAL_TURN_STATUSES,
    ResearchTurnEventType,
    ResearchTurnStatus,
)


def _v(row: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if isinstance(row, dict) and name in row:
            return row[name]
        if hasattr(row, name):
            return getattr(row, name)
    return default


class ExecutionOutcomeClassifier:
    def classify(
        self,
        *,
        analysis_plan: dict[str, Any],
        job: dict[str, Any],
        tool_calls: list[dict[str, Any]],
        artifacts: list[dict[str, Any]],
    ) -> ExecutionOutcome | None:
        status = str(_v(job, "status", default=""))
        if status in {"cancelled", "canceled"}:
            return ExecutionOutcome.CANCELED
        if status in {"created", "queued", "running", "cancel_requested"}:
            return None
        plan_payload = analysis_plan.get("analysisPlan") or analysis_plan.get("analysis_plan_json") or analysis_plan
        required_step_ids = {
            str(_v(item, "stepId", "step_id"))
            for item in plan_payload.get("steps") or []
        }
        calls_by_step = {
            str(_v(item, "stepId", "step_id")): item
            for item in tool_calls
        }
        succeeded_step_ids = {
            step_id
            for step_id, item in calls_by_step.items()
            if str(_v(item, "status", default="")) in {"succeeded", "completed"}
        }
        failed_step_ids = {
            step_id
            for step_id, item in calls_by_step.items()
            if str(_v(item, "status", default="")) in {"failed", "error"}
        }
        if status == "completed" and required_step_ids and required_step_ids <= succeeded_step_ids:
            return ExecutionOutcome.SUCCESS
        usable_success = bool(succeeded_step_ids & required_step_ids) and bool(artifacts)
        if status in {"partial_success", "completed", "failed"}:
            if usable_success and (failed_step_ids or not required_step_ids <= succeeded_step_ids):
                return ExecutionOutcome.PARTIAL
            return ExecutionOutcome.FAILED
        return None


class ResearchExecutionSupervisor:
    def __init__(
        self,
        repository_factory: Any,
        *,
        projector: GenericScientificProgressProjector | None = None,
        registries: Any | None = None,
        projector_version: str = "agent2_execution_1.0",
    ) -> None:
        if registries is None:
            from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES

            registries = DEFAULT_AGENT2_REGISTRIES
        self.repository_factory = repository_factory
        self.projector_override = projector
        self.registries = registries
        self.projector_version = projector_version
        self.classifier = ExecutionOutcomeClassifier()

    def sync_for_job(self, job_id: str) -> Any | None:
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_job(job_id, for_update=True)
            if turn is None:
                return None
            job = unit.repositories.jobs.get(job_id)
            tool_calls = unit.repositories.tool_calls.list_for_job(job_id)
            current_attempt = int(job.get("executionAttempt") or 0)
            if current_attempt:
                tool_calls = [
                    item
                    for item in tool_calls
                    if int(item.get("attempt") or 0) == current_attempt
                ]
            artifacts = unit.repositories.artifacts.list_for_job(job_id)
            if current_attempt:
                current_call_ids = {str(item.get("id")) for item in tool_calls}
                artifacts = [
                    item
                    for item in artifacts
                    if str(item.get("toolCallId") or "") in current_call_ids
                ]
            events = unit.repositories.job_events.list_for_job(job_id)
            plan_record = (
                unit.repositories.analysis_plans.get_plan(str(turn["analysis_plan_id"]))
                if turn.get("analysis_plan_id")
                else {"analysisPlan": {}}
            )
            capability_context, projector = self._capability_context(unit, turn)
            projected_artifacts = _declared_output_artifacts(plan_record, tool_calls, artifacts)
            outcome = self.classifier.classify(
                analysis_plan=plan_record,
                job=job,
                tool_calls=tool_calls,
                artifacts=projected_artifacts,
            )
            current_status = ResearchTurnStatus(str(turn["status"]))

            if current_status == ResearchTurnStatus.QUEUED and str(_v(job, "status")) == "running":
                turn = self._transition(
                    unit,
                    turn,
                    ResearchTurnStatus.RUNNING,
                    ResearchTurnEventType.JOB_STARTED,
                    {"status": ResearchTurnStatus.RUNNING.value},
                )
                current_status = ResearchTurnStatus.RUNNING

            self._project_artifacts(unit, turn, projected_artifacts, tool_calls, capability_context)
            self._project_tool_states(unit, turn, tool_calls, capability_context)
            if outcome is None:
                return projector.project(
                    turn=turn,
                    capability_plan=capability_context,
                    analysis_plan=plan_record,
                    job=job,
                    tool_calls=tool_calls,
                    artifacts=projected_artifacts,
                )

            # Progress polling is intentionally idempotent after the result
            # worker has completed the turn.  The interpreter may attach the
            # final assistant message between two browser polls; in that
            # window the same successful execution must be projected again,
            # not treated as a conflicting RESULT_PENDING transition.
            existing_summary = unit.agent2.research_execution_summaries.get_for_turn(turn["id"])
            if existing_summary is not None and current_status in TERMINAL_TURN_STATUSES:
                return projector.project(
                    turn=turn,
                    capability_plan=capability_context,
                    analysis_plan=plan_record,
                    job=job,
                    tool_calls=tool_calls,
                    artifacts=projected_artifacts,
                    summary=existing_summary,
                )

            if outcome in {ExecutionOutcome.SUCCESS, ExecutionOutcome.PARTIAL} and turn.get("assistant_final_message_id") is not None:
                from mdi_api.research_agent.execution.errors import ExecutionSummaryConflict

                raise ExecutionSummaryConflict("RESULT_PENDING requires no assistant final message")

            summary = self._build_summary(
                turn,
                plan_record,
                job,
                tool_calls,
                projected_artifacts,
                events,
                outcome,
                capability_context,
            )
            stored = unit.agent2.research_execution_summaries.add(
                {
                    "id": uuid4(),
                    "research_turn_id": turn["id"],
                    "job_id": job_id,
                    "contract_version": "1.0",
                    "execution_outcome": outcome.value,
                    "summary_json": summary.model_dump(mode="json"),
                    "source_fingerprint": summary.source_fingerprint,
                    "projector_version": self.projector_version,
                }
            )

            if outcome in {ExecutionOutcome.SUCCESS, ExecutionOutcome.PARTIAL}:
                event = (
                    ResearchTurnEventType.EXECUTION_SUCCEEDED
                    if outcome == ExecutionOutcome.SUCCESS
                    else ResearchTurnEventType.EXECUTION_PARTIAL
                )
                self._event_once(unit, turn["id"], event, {"outcome": outcome.value})
                if current_status in {
                    ResearchTurnStatus.QUEUED,
                    ResearchTurnStatus.RUNNING,
                    ResearchTurnStatus.CANCELING,
                }:
                    turn = self._transition(
                        unit,
                        turn,
                        ResearchTurnStatus.RESULT_PENDING,
                        ResearchTurnEventType.RESULT_PENDING,
                        {"status": ResearchTurnStatus.RESULT_PENDING.value, "outcome": outcome.value},
                    )
            else:
                target = ResearchTurnStatus.CANCELED if outcome == ExecutionOutcome.CANCELED else ResearchTurnStatus.FAILED
                event = (
                    ResearchTurnEventType.EXECUTION_CANCELED
                    if outcome == ExecutionOutcome.CANCELED
                    else ResearchTurnEventType.EXECUTION_FAILED
                )
                if current_status in {
                    ResearchTurnStatus.QUEUED,
                    ResearchTurnStatus.RUNNING,
                    ResearchTurnStatus.CANCELING,
                }:
                    turn = self._transition(unit, turn, target, event, {"status": target.value, "outcome": outcome.value})

            return projector.project(
                turn=turn,
                capability_plan=capability_context,
                analysis_plan=plan_record,
                job=job,
                tool_calls=tool_calls,
                artifacts=projected_artifacts,
                summary=stored,
            )

    def request_cancel(self, turn_id: UUID) -> dict[str, Any]:
        job_id = ""
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            status = ResearchTurnStatus(str(turn["status"]))
            if status not in {ResearchTurnStatus.QUEUED, ResearchTurnStatus.RUNNING, ResearchTurnStatus.CANCELING}:
                return turn
            if status != ResearchTurnStatus.CANCELING:
                turn = self._transition(
                    unit,
                    turn,
                    ResearchTurnStatus.CANCELING,
                    ResearchTurnEventType.CANCELLATION_REQUESTED,
                    {"status": ResearchTurnStatus.CANCELING.value},
                )
            job_id = str(turn.get("job_id") or "")
        if job_id:
            try:
                with self.repository_factory.unit_of_work() as unit:
                    unit.repositories.jobs.request_cancel(job_id)
            except Exception as exc:
                from mdi_api.research_agent.execution.errors import ExecutionCancelRequestFailed

                raise ExecutionCancelRequestFailed(
                    "cancellation intent is durable but the Job cancel request must be reconciled"
                ) from exc
        return turn

    def _capability_context(self, unit: Any, turn: dict[str, Any]) -> tuple[dict[str, Any], Any]:
        plan_record = unit.agent2.research_capability_plans.get_for_turn(turn["id"])
        resolution_record = unit.agent2.research_capability_resolutions.get_for_turn(turn["id"])
        context: dict[str, Any] = {"step_metadata": {}}
        projector_ids: set[str] = set()
        if plan_record is not None and resolution_record is not None:
            try:
                plan = CapabilityPlan.model_validate(plan_record["plan_json"])
                resolution = CapabilityResolution.model_validate(resolution_record["resolution_json"])
            except ValueError:
                plan = None
                resolution = None
            if plan is not None and resolution is not None:
                candidates = {
                    f"cap_{index}": item
                    for index, item in enumerate(
                        sorted(
                            resolution.candidates,
                            key=lambda item: (item.planning_priority, item.capability_id, item.capability_version),
                        ),
                        1,
                    )
                }
                for step in plan.steps:
                    candidate = candidates.get(step.capability_ref_key)
                    if candidate is None:
                        continue
                    manifest = self.registries.capabilities.require(candidate.capability_id, candidate.capability_version)
                    self.registries.progress_projectors.require(manifest.progress_projector)
                    projector_ids.add(manifest.progress_projector)
                    context["step_metadata"][step.step_id] = {
                        "capability_id": candidate.capability_id,
                        "capability_version": candidate.capability_version,
                        "display_name": manifest.display_name,
                        "running_label": f"正在{manifest.display_name}",
                        "completed_label": f"{manifest.display_name}已完成",
                    }
        projector = self.projector_override or GenericScientificProgressProjector()
        if self.projector_override is None and len(projector_ids) == 1:
            projector = self.registries.progress_projectors.require(next(iter(projector_ids)))
        return context, projector

    def _project_artifacts(
        self,
        unit: Any,
        turn: dict[str, Any],
        artifacts: list[dict[str, Any]],
        tool_calls: list[dict[str, Any]],
        capability_context: dict[str, Any],
    ) -> None:
        existing = unit.agent2.research_turn_events.list_for_turn(turn["id"])
        seen = {
            str((item.get("payload_json") or {}).get("artifact_id"))
            for item in existing
            if item["event_type"] == ResearchTurnEventType.EXECUTION_OUTPUT_AVAILABLE.value
        }
        calls_by_id = {str(_v(call, "id")): call for call in tool_calls}
        metadata = capability_context.get("step_metadata") or {}
        for artifact in artifacts:
            artifact_id = str(_v(artifact, "id", "artifactId"))
            if artifact_id in seen:
                continue
            call = calls_by_id.get(str(_v(artifact, "toolCallId", "tool_call_id"))) or {}
            step_id = str(_v(call, "stepId", "step_id", default=""))
            label = str((metadata.get(step_id) or {}).get("completed_label") or "科学分析输出已生成")
            self._append_event(
                unit,
                turn["id"],
                ResearchTurnEventType.EXECUTION_OUTPUT_AVAILABLE,
                {"artifact_id": artifact_id, "step_id": step_id, "label": label},
            )
            seen.add(artifact_id)

    def _project_tool_states(
        self,
        unit: Any,
        turn: dict[str, Any],
        tool_calls: list[dict[str, Any]],
        capability_context: dict[str, Any],
    ) -> None:
        existing = unit.agent2.research_turn_events.list_for_turn(turn["id"])
        seen = {
            (item["event_type"], str((item.get("payload_json") or {}).get("step_id")))
            for item in existing
        }
        metadata = capability_context.get("step_metadata") or {}
        for call in tool_calls:
            step_id = str(_v(call, "stepId", "step_id", default=""))
            raw = str(_v(call, "status", default=""))
            if raw in {"running", "started"}:
                event_type = ResearchTurnEventType.EXECUTION_STEP_STARTED
                label = str((metadata.get(step_id) or {}).get("running_label") or "正在执行科学分析步骤")
            elif raw in {"completed", "succeeded"}:
                event_type = ResearchTurnEventType.EXECUTION_STEP_COMPLETED
                label = str((metadata.get(step_id) or {}).get("completed_label") or "科学分析步骤已完成")
            elif raw in {"failed", "error"}:
                event_type = ResearchTurnEventType.EXECUTION_STEP_FAILED
                label = str((metadata.get(step_id) or {}).get("display_name") or "科学分析步骤")
            elif raw in {"skipped", "canceled"}:
                event_type = ResearchTurnEventType.EXECUTION_STEP_SKIPPED
                label = str((metadata.get(step_id) or {}).get("display_name") or "科学分析步骤")
            else:
                continue
            key = (event_type.value, step_id)
            if key in seen:
                continue
            self._append_event(unit, turn["id"], event_type, {"step_id": step_id, "label": label})
            seen.add(key)

    def _transition(
        self,
        unit: Any,
        turn: dict[str, Any],
        target: ResearchTurnStatus,
        event: ResearchTurnEventType,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        updated = unit.agent2.research_turns.compare_and_set_status(
            turn["id"],
            expected_status=str(turn["status"]),
            expected_version=int(turn["row_version"]),
            target_status=target.value,
            completed_at=(
                datetime.now(timezone.utc)
                if target in {ResearchTurnStatus.FAILED, ResearchTurnStatus.CANCELED}
                else None
            ),
        )
        self._append_event(unit, turn["id"], event, payload)
        return updated

    def _event_once(
        self,
        unit: Any,
        turn_id: UUID,
        event_type: ResearchTurnEventType,
        payload: dict[str, Any],
    ) -> None:
        existing = unit.agent2.research_turn_events.list_for_turn(turn_id)
        if any(item["event_type"] == event_type.value for item in existing):
            return
        self._append_event(unit, turn_id, event_type, payload)

    @staticmethod
    def _append_event(unit: Any, turn_id: UUID, event_type: ResearchTurnEventType, payload: dict[str, Any]) -> None:
        unit.agent2.research_turn_events.append_turn_event(
            {
                "id": uuid4(),
                "turn_id": turn_id,
                "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id),
                "event_type": event_type.value,
                "payload_json": payload,
            }
        )

    def _build_summary(
        self,
        turn: dict[str, Any],
        plan_record: dict[str, Any],
        job: dict[str, Any],
        tool_calls: list[dict[str, Any]],
        artifacts: list[dict[str, Any]],
        events: list[Any],
        outcome: ExecutionOutcome,
        capability_context: dict[str, Any],
    ) -> ResearchExecutionSummary:
        plan_payload = plan_record.get("analysisPlan") or {}
        calls_by_step = {str(_v(item, "stepId", "step_id")): item for item in tool_calls}
        artifacts_by_call: dict[str, list[dict[str, Any]]] = {}
        for artifact in artifacts:
            artifacts_by_call.setdefault(str(_v(artifact, "toolCallId", "tool_call_id")), []).append(artifact)
        metadata = capability_context.get("step_metadata") or {}
        steps: list[ExecutionStepSummary] = []
        for item in list(plan_payload.get("steps") or []):
            step_id = str(_v(item, "stepId", "step_id"))
            call = calls_by_step.get(step_id)
            raw = str(_v(call, "status", default="planned")) if call else "planned"
            status = {
                "planned": ExecutionStepStatus.PENDING,
                "running": ExecutionStepStatus.RUNNING,
                "succeeded": ExecutionStepStatus.SUCCEEDED,
                "completed": ExecutionStepStatus.SUCCEEDED,
                "failed": ExecutionStepStatus.FAILED,
                "skipped": ExecutionStepStatus.SKIPPED,
                "canceled": ExecutionStepStatus.CANCELED,
            }.get(raw, ExecutionStepStatus.PENDING)
            refs = [
                ExecutionArtifactRef(
                    artifact_id=str(_v(artifact, "id", "artifactId")),
                    step_id=step_id,
                    artifact_type=str(_v(artifact, "type", default="")) or None,
                    media_type=str(_v(artifact, "contentType", "content_type", default="")) or None,
                    display_label=str(_v(artifact, "name", default="科学分析输出")),
                    preview_available=bool(_v(artifact, "previewKey", "preview_key")),
                    download_available=True,
                )
                for artifact in artifacts_by_call.get(str(_v(call, "id", default="")), [])
            ]
            step_meta = metadata.get(step_id) or {}
            steps.append(
                ExecutionStepSummary(
                    step_id=step_id,
                    capability_id=str(step_meta.get("capability_id") or "agent2.legacy-bound-step"),
                    capability_version=str(step_meta.get("capability_version") or "1.0"),
                    display_name=str(step_meta.get("display_name") or _v(item, "purpose", default="科学分析步骤")),
                    status=status,
                    tool_call_ids=[str(_v(call, "id"))] if call and _v(call, "id") else [],
                    output_artifact_refs=refs,
                    started_at=_v(call, "createdAt", "created_at") if call else None,
                    completed_at=_v(call, "updatedAt", "updated_at") if call and status in {
                        ExecutionStepStatus.SUCCEEDED,
                        ExecutionStepStatus.FAILED,
                        ExecutionStepStatus.SKIPPED,
                        ExecutionStepStatus.CANCELED,
                    } else None,
                )
            )
        successful = [item.step_id for item in steps if item.status == ExecutionStepStatus.SUCCEEDED]
        failed = [item.step_id for item in steps if item.status == ExecutionStepStatus.FAILED]
        skipped = [item.step_id for item in steps if item.status == ExecutionStepStatus.SKIPPED]
        refs = [ref for item in steps for ref in item.output_artifact_refs]
        warnings: list[ExecutionWarning] = []
        if ResearchTurnStatus(str(turn["status"])) == ResearchTurnStatus.CANCELING and outcome in {
            ExecutionOutcome.SUCCESS,
            ExecutionOutcome.PARTIAL,
        }:
            warnings.append(
                ExecutionWarning(
                    code="CANCELLATION_REQUESTED_AFTER_EXECUTION_COMPLETED",
                    message="取消请求到达时执行已结束，已保留真实执行输出。",
                )
            )
        fingerprint = execution_source_fingerprint(
            analysis_plan_id=str(turn["analysis_plan_id"]),
            job=job,
            tool_calls=tool_calls,
            artifacts=artifacts,
            events=events,
            projector_version=self.projector_version,
        )
        started = min(
            (value for value in (_v(call, "createdAt", "created_at") for call in tool_calls) if value is not None),
            default=None,
        )
        terminal = _v(job, "updatedAt", "updated_at", default=datetime.now(timezone.utc))
        return ResearchExecutionSummary(
            contract_version="1.0",
            research_turn_id=UUID(str(turn["id"])),
            analysis_plan_id=str(turn["analysis_plan_id"]),
            job_id=str(turn["job_id"]),
            outcome=outcome,
            steps=steps,
            successful_step_ids=successful,
            failed_step_ids=failed,
            skipped_step_ids=skipped,
            artifact_refs=refs,
            warnings=warnings,
            started_at=started,
            terminal_at=terminal,
            source_fingerprint=fingerprint,
            projector_version=self.projector_version,
        )


def _declared_output_artifacts(
    plan_record: dict[str, Any],
    tool_calls: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Keep only outputs declared by the immutable AnalysisPlan contract."""
    plan_payload = plan_record.get("analysisPlan") or plan_record.get("analysis_plan_json") or {}
    allowed = {
        (str(_v(item, "fromStepId", "from_step_id")), str(_v(item, "type")))
        for item in plan_payload.get("expectedArtifacts") or []
    }
    if not allowed:
        return []
    calls_by_id = {str(_v(call, "id")): call for call in tool_calls}
    projected: list[dict[str, Any]] = []
    for artifact in artifacts:
        call = calls_by_id.get(str(_v(artifact, "toolCallId", "tool_call_id")))
        if call is None:
            continue
        identity = (
            str(_v(call, "stepId", "step_id")),
            str(_v(artifact, "type", default="")),
        )
        if identity in allowed:
            projected.append(artifact)
    return projected
