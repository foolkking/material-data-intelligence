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

    repos = InMemoryRepositoryBundle.create()
    runtime = queue_runtime or QueueWorkerRuntime(repositories=repos, queue_backend=InMemoryQueueBackend())
    return repos, runtime


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
