from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from mdi_adapters import ToolExecutionContext, ToolExecutionError, ToolExecutionResult, execute_tool_request
from mdi_schemas import JobEvent, JobEventStatus, JobStatus, ToolCall, ToolExecutionRequest
from mdi_tool_registry import ToolRegistry


SECRET_PARAM_MARKERS = ("secret", "api_key", "apikey", "token", "password", "byok")


@dataclass
class JobRecord:
    job_id: str
    project_id: str
    dataset_id: str
    status: JobStatus = JobStatus.created
    events: list[JobEvent] = field(default_factory=list)
    tool_calls: dict[str, ToolCall] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: _utc_now())
    updated_at: str = field(default_factory=lambda: _utc_now())


@dataclass(frozen=True)
class WorkerRunResult:
    execution: ToolExecutionResult
    job: JobRecord
    tool_call: ToolCall
    events: list[JobEvent]


class InMemoryJobStore:
    """Development-only Job/ToolCall/Event state store.

    Production will replace this with PostgreSQL-backed repositories while
    preserving the same status and event semantics.
    """

    def __init__(self) -> None:
        self.jobs: dict[str, JobRecord] = {}

    def ensure_job(self, context: ToolExecutionContext) -> JobRecord:
        if context.job_id not in self.jobs:
            self.jobs[context.job_id] = JobRecord(
                job_id=context.job_id,
                project_id=context.project_id,
                dataset_id=context.dataset_id,
            )
        return self.jobs[context.job_id]

    def set_job_status(self, job_id: str, status: JobStatus) -> None:
        job = self.jobs[job_id]
        job.status = status
        job.updated_at = _utc_now()

    def append_event(
        self,
        job_id: str,
        *,
        event_type: str,
        status: JobEventStatus,
        message: str,
        payload: dict[str, Any] | None = None,
        progress: float | None = None,
    ) -> JobEvent:
        job = self.jobs[job_id]
        seq = len(job.events) + 1
        event = JobEvent(
            id=f"evt_{job_id}_{seq:04d}",
            jobId=job_id,
            seq=seq,
            eventType=event_type,
            status=status,
            message=message,
            progress=progress,
            payload=payload,
            createdAt=_utc_now(),
        )
        job.events.append(event)
        job.updated_at = event.createdAt
        return event

    def start_tool_call(self, context: ToolExecutionContext, request: ToolExecutionRequest) -> ToolCall:
        job = self.jobs[context.job_id]
        tool_call = ToolCall(
            id=context.tool_call_id,
            jobId=context.job_id,
            stepId=request.stepId,
            toolId=request.toolId,
            status="running",
            params=_redact_secret_params(request.params),
        )
        job.tool_calls[tool_call.id] = tool_call
        job.updated_at = _utc_now()
        return tool_call

    def complete_tool_call(self, job_id: str, tool_call_id: str, artifact_ids: list[str]) -> ToolCall:
        tool_call = self.jobs[job_id].tool_calls[tool_call_id]
        updated = tool_call.model_copy(update={"status": "completed", "artifactIds": artifact_ids})
        self.jobs[job_id].tool_calls[tool_call_id] = updated
        self.jobs[job_id].updated_at = _utc_now()
        return updated

    def fail_tool_call(self, job_id: str, tool_call_id: str, error: ToolExecutionError) -> ToolCall:
        tool_call = self.jobs[job_id].tool_calls[tool_call_id]
        updated = tool_call.model_copy(update={"status": "failed", "error": error.to_dict()})
        self.jobs[job_id].tool_calls[tool_call_id] = updated
        self.jobs[job_id].updated_at = _utc_now()
        return updated


def run_tool_call_job(
    context: ToolExecutionContext,
    request: ToolExecutionRequest | dict[str, Any],
    *,
    store: InMemoryJobStore | None = None,
    registry: ToolRegistry | None = None,
    cache: dict[str, list[Any]] | None = None,
) -> WorkerRunResult:
    parsed_request = request if isinstance(request, ToolExecutionRequest) else ToolExecutionRequest.model_validate(request)
    active_store = store or InMemoryJobStore()
    job = active_store.ensure_job(context)
    active_store.set_job_status(job.job_id, JobStatus.running)
    started_at = len(job.events)

    tool_call = active_store.start_tool_call(context, parsed_request)
    active_store.append_event(
        job.job_id,
        event_type="tool.started",
        status=JobEventStatus.running,
        message=f"Started tool {parsed_request.toolId}.",
        payload={"toolCallId": tool_call.id, "toolId": parsed_request.toolId},
        progress=0.0,
    )

    try:
        execution = execute_tool_request(context, parsed_request, registry=registry, cache=cache)
    except ToolExecutionError as exc:
        failed_call = active_store.fail_tool_call(job.job_id, tool_call.id, exc)
        active_store.append_event(
            job.job_id,
            event_type="tool.failed",
            status=JobEventStatus.error,
            message=exc.message,
            payload={"toolCallId": tool_call.id, "toolId": parsed_request.toolId, "error": exc.to_dict()},
            progress=1.0,
        )
        active_store.set_job_status(job.job_id, JobStatus.failed)
        events = job.events[started_at:]
        raise WorkerToolExecutionError(error=exc, job=job, tool_call=failed_call, events=events) from exc

    completed_call = active_store.complete_tool_call(job.job_id, tool_call.id, [artifact.id for artifact in execution.artifacts])
    for artifact in execution.artifacts:
        active_store.append_event(
            job.job_id,
            event_type="artifact.ready",
            status=JobEventStatus.success,
            message=f"Artifact ready: {artifact.name}",
            payload={
                "toolCallId": tool_call.id,
                "artifactId": artifact.id,
                "artifactType": artifact.type.value,
                "storageKey": artifact.storageKey,
            },
        )
    active_store.append_event(
        job.job_id,
        event_type="tool.completed",
        status=JobEventStatus.success,
        message=f"Completed tool {parsed_request.toolId}.",
        payload={"toolCallId": tool_call.id, "cacheHit": execution.cache_hit, "cacheKey": execution.cache_key},
        progress=1.0,
    )
    active_store.set_job_status(job.job_id, JobStatus.completed)

    return WorkerRunResult(
        execution=execution,
        job=job,
        tool_call=completed_call,
        events=job.events[started_at:],
    )


class WorkerToolExecutionError(Exception):
    def __init__(self, *, error: ToolExecutionError, job: JobRecord, tool_call: ToolCall, events: list[JobEvent]) -> None:
        super().__init__(error.message)
        self.error = error
        self.job = job
        self.tool_call = tool_call
        self.events = events


def _redact_secret_params(params: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in params.items():
        lowered = str(key).lower()
        if any(marker in lowered for marker in SECRET_PARAM_MARKERS):
            redacted[key] = "[REDACTED]"
        elif isinstance(value, dict):
            redacted[key] = _redact_secret_params(value)
        else:
            redacted[key] = value
    return redacted


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

