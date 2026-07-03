"""Planner API routes — POST /planner/preview, /planner/validate, /planner/jobs."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Any
import uuid

from pydantic import BaseModel, Field

from mdi_api.config import load_settings
from mdi_api.database import create_repository_factory
from mdi_api.repositories import InMemoryRepositoryBundle, compute_plan_hash
from mdi_api.secrets import InMemorySecretStore
from mdi_llm import (
    MockLLMProvider,
    PlannerRawResponse,
    PlannerRequest,
    PlannerUserConfig,
    redact_params_for_log,
)
from mdi_workers import InMemoryQueueBackend, QueueWorkerRuntime, RedisRQQueueBackend
from mdi_tool_registry import ToolRegistry, load_manifests
from mdi_tool_registry.plan_validator import PlanValidationResult, validate_plan


_LLM_PROVIDER = MockLLMProvider()
_SECRET_STORE = InMemorySecretStore()
_IN_MEMORY_REPOSITORIES = InMemoryRepositoryBundle.create()
_IN_MEMORY_QUEUE_BACKEND = InMemoryQueueBackend()
_IN_MEMORY_QUEUE_RUNTIME = QueueWorkerRuntime(
    repositories=_IN_MEMORY_REPOSITORIES,
    queue_backend=_IN_MEMORY_QUEUE_BACKEND,
)


def _get_registry() -> ToolRegistry:
    return load_manifests()


class PlannerPreviewRequest(BaseModel):
    userPrompt: str = Field(min_length=1)
    datasetId: str = Field(min_length=1)
    profileId: str = Field(default="")


class PlannerValidateRequest(BaseModel):
    plan: dict[str, Any]


class PlannerJobsRequest(BaseModel):
    userPrompt: str = Field(min_length=1)
    projectId: str = Field(default="project_local", min_length=1)
    datasetId: str = Field(min_length=1)
    profileId: str = Field(default="")
    enqueue: bool = Field(default=False)
    execute: bool = Field(default=False)


@dataclass
class PlannerPreviewResult:
    plan: dict[str, Any] | None
    raw_response: str | None
    validation: PlanValidationResult | None
    model: str


@dataclass
class PlannerValidateResult:
    ok: bool
    errors: list[dict[str, Any]]


@dataclass
class PlannerJobsResult:
    ok: bool
    job_id: str | None
    plan_id: str | None
    plan_hash: str | None
    validation_errors: list[dict[str, Any]]
    plan: dict[str, Any] | None
    plan_source: str = "llm"
    enqueued: bool = False
    executed: bool = False


# ── POST /planner/preview ──────────────────────────────────────────

def planner_preview(
    request: PlannerPreviewRequest,
    *,
    provider: Any = None,
    registry: ToolRegistry | None = None,
) -> PlannerPreviewResult:
    """Generate an AnalysisPlan preview without creating a job."""
    reg = registry or _get_registry()
    llm = provider or _LLM_PROVIDER
    tools = [t for t in reg.tools if t.stage == "mvp"]

    planner_req = PlannerRequest(
        user_prompt=request.userPrompt,
        dataset_id=request.datasetId,
        profile_id=request.profileId or request.datasetId,
        tool_registry_version=reg.version,
    )

    # We use a minimal data profile stub — in production the caller
    # would pass a real profile via the API request.
    from mdi_schemas import DataProfile
    dp = DataProfile(
        profileId=request.profileId or request.datasetId,
        datasetId=request.datasetId,
        version="0.1",
        datasetType="ml",
        createdAt="2026-06-27T00:00:00+00:00",
    )

    resp: PlannerRawResponse = llm.generate_plan(planner_req, tools=tools, data_profile=dp)

    plan = resp.raw_json if resp.raw_json else None
    validation = validate_plan(plan, registry=reg) if plan else None

    return PlannerPreviewResult(
        plan=plan,
        raw_response=resp.raw_text,
        validation=validation,
        model=resp.model,
    )


# ── POST /planner/validate ─────────────────────────────────────────

def planner_validate(
    request: PlannerValidateRequest,
    *,
    registry: ToolRegistry | None = None,
) -> PlannerValidateResult:
    """Validate an AnalysisPlan JSON without executing it."""
    reg = registry or _get_registry()
    result = validate_plan(request.plan, registry=reg)
    return PlannerValidateResult(
        ok=result.ok,
        errors=[{"code": e.code, "message": e.message, "detail": e.detail} for e in result.errors],
    )


# ── POST /planner/jobs ─────────────────────────────────────────────

def planner_jobs(
    request: PlannerJobsRequest,
    *,
    provider: Any = None,
    registry: ToolRegistry | None = None,
    repositories: Any = None,
    queue_runtime: Any = None,
) -> PlannerJobsResult:
    """Generate plan, validate, persist plan, create job, and optionally enqueue.

    If validation fails, no AnalysisPlan or Job is persisted. Runtime execution is
    intentionally delegated to QueueWorkerRuntime, which loads the persisted plan
    by job_id.
    """
    reg = registry or _get_registry()
    llm = provider or _LLM_PROVIDER
    tools = [t for t in reg.tools if t.stage == "mvp"]

    planner_req = PlannerRequest(
        user_prompt=request.userPrompt,
        dataset_id=request.datasetId,
        profile_id=request.profileId or request.datasetId,
        tool_registry_version=reg.version,
    )

    from mdi_schemas import DataProfile
    dp = DataProfile(
        profileId=request.profileId or request.datasetId,
        datasetId=request.datasetId,
        version="0.1",
        datasetType="ml",
        createdAt="2026-06-27T00:00:00+00:00",
    )

    resp: PlannerRawResponse = llm.generate_plan(planner_req, tools=tools, data_profile=dp)

    plan = resp.raw_json
    if plan is None:
        return PlannerJobsResult(
            ok=False,
            job_id=None,
            plan_id=None,
            plan_hash=None,
            validation_errors=[{"code": "PLAN_EMPTY", "message": "LLM returned no plan.", "detail": None}],
            plan=None,
        )

    validation = validate_plan(plan, registry=reg)
    if not validation.ok:
        return PlannerJobsResult(
            ok=False,
            job_id=None,
            plan_id=None,
            plan_hash=None,
            validation_errors=[{"code": e.code, "message": e.message, "detail": e.detail} for e in validation.errors],
            plan=plan,
        )

    from mdi_schemas import AnalysisPlan

    validated_plan = AnalysisPlan.model_validate(plan)
    plan_hash = compute_plan_hash(validated_plan)
    repos, runtime = _planner_repositories_and_runtime(repositories=repositories, queue_runtime=queue_runtime)
    created_by = "user_local"
    project_id = request.projectId
    dataset_id = request.datasetId
    profile_id = request.profileId or request.datasetId
    planner_provider = _provider_name(llm)
    plan_id = f"plan_{uuid.uuid4().hex[:24]}"
    job_id = f"job_{uuid.uuid4().hex[:24]}"

    _ensure_planner_project_dataset(repos, project_id=project_id, dataset_id=dataset_id, created_by=created_by)
    repos.analysis_plans.save_plan(
        {
            "id": plan_id,
            "projectId": project_id,
            "datasetId": dataset_id,
            "profileId": profile_id,
            "planSource": "llm",
            "plannerProvider": planner_provider,
            "analysisPlan": validated_plan.model_dump(mode="json"),
            "planHash": plan_hash,
            "validationStatus": "validated",
            "createdBy": created_by,
        }
    )
    repos.jobs.save(
        {
            "id": job_id,
            "projectId": project_id,
            "datasetId": dataset_id,
            "planId": plan_id,
            "status": "created",
            "kind": "analysis",
            "createdBy": created_by,
        }
    )
    repos.analysis_plans.attach_plan_to_job(plan_id, job_id)
    repos.job_events.append_event(
        job_id,
        event_type="job.created",
        status="info",
        message="Planner job created with persisted AnalysisPlan.",
        payload={"projectId": project_id, "datasetId": dataset_id, "planId": plan_id, "planHash": plan_hash},
        progress=0.0,
    )
    repos.job_events.append_event(
        job_id,
        event_type="plan.persisted",
        status="success",
        message=f"Persisted validated AnalysisPlan with {len(validated_plan.steps)} step(s).",
        payload={"planId": plan_id, "planHash": plan_hash, "planSource": "llm", "plannerProvider": planner_provider},
        progress=0.0,
    )

    enqueued = False
    if request.enqueue or request.execute:
        enqueued = runtime.submit_job(job_id).enqueued

    return PlannerJobsResult(
        ok=True,
        job_id=job_id,
        plan_id=plan_id,
        plan_hash=plan_hash,
        validation_errors=[],
        plan=validated_plan.model_dump(mode="json"),
        plan_source="llm",
        enqueued=enqueued,
        executed=False,
    )


def planner_preview_route(request: PlannerPreviewRequest) -> PlannerPreviewResult:
    return planner_preview(request)


def planner_validate_route(request: PlannerValidateRequest) -> PlannerValidateResult:
    return planner_validate(request)


def planner_jobs_route(request: PlannerJobsRequest) -> PlannerJobsResult:
    return planner_jobs(request)


def get_planner_analysis_plan(plan_id: str, *, repositories: Any = None) -> dict[str, Any]:
    """Read a persisted AnalysisPlan without mutating or executing anything."""
    repos = _planner_read_repositories(repositories)
    return _analysis_plan_response(repos.analysis_plans.get_plan(plan_id))


def get_planner_job(job_id: str, *, repositories: Any = None) -> dict[str, Any]:
    """Read a planner-created job and its persisted plan binding."""
    repos = _planner_read_repositories(repositories)
    job = repos.jobs.get(job_id)
    plan = _try_get_job_plan(repos, job)
    events = repos.job_events.list_for_job(job_id)
    tool_calls = repos.tool_calls.list_for_job(job_id)
    artifacts = repos.artifacts.list_for_job(job_id)
    plan_hash = _plan_hash(plan)
    return {
        **job,
        "jobId": job.get("jobId") or job.get("id"),
        "planId": job.get("planId") or job.get("plan_id") or (plan or {}).get("planId"),
        "planHash": plan_hash,
        "planSource": (plan or {}).get("planSource"),
        "analysisPlan": (plan or {}).get("analysisPlan"),
        "validationStatus": (plan or {}).get("validationStatus"),
        "toolCallCount": len(tool_calls),
        "artifactCount": len(artifacts),
        "eventCount": len(events),
        "provenance": _planner_job_provenance(job, plan),
    }


def get_planner_job_events(job_id: str, after_seq: int = 0, *, repositories: Any = None) -> list[dict[str, Any]]:
    """Read persisted planner job events without touching execution state."""
    repos = _planner_read_repositories(repositories)
    repos.jobs.get(job_id)
    events = repos.job_events.list_events_after_seq(job_id, after_seq)
    return [_event_to_dict(event) for event in events]


def get_planner_job_tool_calls(job_id: str, *, repositories: Any = None) -> list[dict[str, Any]]:
    """Read ToolCalls and expose persisted-plan provenance for the UI."""
    repos = _planner_read_repositories(repositories)
    job = repos.jobs.get(job_id)
    plan = _try_get_job_plan(repos, job)
    provenance = _planner_job_provenance(job, plan)
    return [
        {
            **tool_call,
            "planId": provenance.get("planId"),
            "planHash": provenance.get("planHash"),
            "inputSummary": _params_summary(tool_call.get("params")),
            "outputSummary": _tool_call_output_summary(tool_call),
        }
        for tool_call in repos.tool_calls.list_for_job(job_id)
    ]


def get_planner_job_artifacts(job_id: str, *, repositories: Any = None) -> list[dict[str, Any]]:
    """Read artifacts and surface artifact-level plan provenance when present."""
    repos = _planner_read_repositories(repositories)
    job = repos.jobs.get(job_id)
    plan = _try_get_job_plan(repos, job)
    fallback = _planner_job_provenance(job, plan)
    artifacts = []
    for artifact in repos.artifacts.list_for_job(job_id):
        provenance = _artifact_plan_provenance(artifact) or fallback
        artifacts.append(
            {
                **artifact,
                "planId": provenance.get("planId"),
                "planHash": provenance.get("planHash"),
                "provenance": provenance,
            }
        )
    return artifacts


def get_planner_job_result(job_id: str, *, repositories: Any = None) -> dict[str, Any]:
    """Read a compact result summary for a planner job."""
    repos = _planner_read_repositories(repositories)
    job = repos.jobs.get(job_id)
    plan = _try_get_job_plan(repos, job)
    provenance = _planner_job_provenance(job, plan)
    tool_calls = repos.tool_calls.list_for_job(job_id)
    artifacts = get_planner_job_artifacts(job_id, repositories=repos)
    status = str(job.get("status") or "unknown")
    summary = (
        f"Job completed with {len(tool_calls)} ToolCall(s) and {len(artifacts)} Artifact(s)."
        if status == "completed"
        else "Result not available yet."
    )
    return {
        "jobId": job.get("jobId") or job.get("id"),
        "status": status,
        "planId": provenance.get("planId"),
        "planHash": provenance.get("planHash"),
        "summary": summary,
        "toolCallCount": len(tool_calls),
        "artifactCount": len(artifacts),
        "artifacts": artifacts,
        "provenance": provenance,
    }


def _planner_repositories_and_runtime(*, repositories: Any, queue_runtime: QueueWorkerRuntime | None) -> tuple[Any, QueueWorkerRuntime]:
    if repositories is not None:
        runtime = queue_runtime or QueueWorkerRuntime(repositories=repositories, queue_backend=InMemoryQueueBackend())
        return repositories, runtime

    settings = load_settings()
    if "postgres" in settings.database_url:
        factory = create_repository_factory(settings)
        repos = factory.create_repositories()
        runtime = queue_runtime or QueueWorkerRuntime(
            repository_factory=factory,
            queue_backend=RedisRQQueueBackend(redis_url=settings.redis_url)
            if _should_use_redis_queue(settings)
            else InMemoryQueueBackend(),
        )
        return repos, runtime

    runtime = queue_runtime or _IN_MEMORY_QUEUE_RUNTIME
    return _IN_MEMORY_REPOSITORIES, runtime


def _planner_read_repositories(repositories: Any) -> Any:
    repos, _runtime = _planner_repositories_and_runtime(repositories=repositories, queue_runtime=None)
    return repos


def _ensure_planner_project_dataset(repos: Any, *, project_id: str, dataset_id: str, created_by: str) -> None:
    try:
        repos.projects.get(project_id)
    except LookupError:
        repos.projects.save({"id": project_id, "name": project_id, "createdBy": created_by})
    try:
        repos.datasets.get(dataset_id)
    except LookupError:
        repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": dataset_id, "createdBy": created_by})


def _provider_name(provider: Any) -> str:
    meta = getattr(provider, "meta", None)
    name = getattr(meta, "name", None)
    return str(name or provider.__class__.__name__)


def _should_use_redis_queue(settings: Any) -> bool:
    return settings.queue_backend == "redis" or bool(os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL"))


def _try_get_job_plan(repos: Any, job: dict[str, Any]) -> dict[str, Any] | None:
    plan_id = job.get("planId") or job.get("plan_id")
    if plan_id:
        return repos.analysis_plans.get_plan(str(plan_id))
    try:
        return repos.analysis_plans.get_plan_for_job(str(job.get("jobId") or job["id"]))
    except LookupError:
        return None


def _analysis_plan_response(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        **plan,
        "analysisPlan": plan.get("analysisPlan"),
        "planId": plan.get("planId") or plan.get("id"),
        "planHash": _plan_hash(plan),
    }


def _planner_job_provenance(job: dict[str, Any], plan: dict[str, Any] | None) -> dict[str, Any]:
    plan_id = (plan or {}).get("planId") or (plan or {}).get("id") or job.get("planId") or job.get("plan_id")
    plan_hash = _plan_hash(plan)
    return {
        "planId": plan_id,
        "planHash": plan_hash,
        "planSource": (plan or {}).get("planSource"),
        "loadedFrom": "persisted_analysis_plan" if plan_id else None,
        "binding": "jobs.plan_id -> analysis_plans.id" if plan_id else None,
        "toolPath": "Tool Registry + Adapter" if plan_id else None,
        "fallbackUsed": False if plan_id else None,
    }


def _artifact_plan_provenance(artifact: dict[str, Any]) -> dict[str, Any] | None:
    metadata = artifact.get("metadata") if isinstance(artifact, dict) else None
    provenance = (metadata or {}).get("provenance") if isinstance(metadata, dict) else None
    if isinstance(provenance, dict) and (provenance.get("planId") or provenance.get("planHash")):
        return provenance
    return None


def _event_to_dict(event: Any) -> dict[str, Any]:
    if hasattr(event, "model_dump"):
        return event.model_dump(mode="json")
    return dict(event)


def _params_summary(params: Any) -> str:
    if not isinstance(params, dict) or not params:
        return "No params"
    keys = ", ".join(sorted(str(key) for key in params.keys()))
    return f"Params: {keys}"


def _tool_call_output_summary(tool_call: dict[str, Any]) -> str:
    artifact_ids = tool_call.get("artifactIds") or tool_call.get("artifact_ids") or []
    if artifact_ids:
        return f"{len(artifact_ids)} artifact(s)"
    error = tool_call.get("error")
    if error:
        return str(error.get("message") or error)
    return "Not available yet"


def _plan_hash(plan: dict[str, Any] | None) -> str | None:
    if not plan:
        return None
    value = plan.get("planHash") or plan.get("plan_hash")
    return str(value) if value else None
