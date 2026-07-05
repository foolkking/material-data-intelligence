"""Planner API routes — POST /planner/preview, /planner/validate, /planner/jobs."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from typing import Any
import uuid

from pydantic import BaseModel, Field

from mdi_api.config import load_settings
from mdi_api.artifact_storage import create_artifact_storage_from_settings
from mdi_api.database import create_repository_factory
from mdi_api.repositories import InMemoryRepositoryBundle, compute_plan_hash
from mdi_api.secrets import InMemorySecretStore
from mdi_llm import (
    LLMProviderError,
    MockLLMProvider,
    OpenAICompatibleProvider,
    PlannerRawResponse,
    PlannerRequest,
    PlannerUserConfig,
    redact_params_for_log,
)
from mdi_workers import InMemoryQueueBackend, QueueWorkerRuntime, RedisRQQueueBackend
from mdi_workers.object_store import DurableObjectStoreResolver
from mdi_tool_registry import ToolRegistry, load_manifests
from mdi_tool_registry.plan_validator import PlanValidationError, PlanValidationResult, validate_plan


_LLM_PROVIDER = MockLLMProvider()
_SECRET_STORE = InMemorySecretStore()
_IN_MEMORY_REPOSITORIES = InMemoryRepositoryBundle.create()
_IN_MEMORY_QUEUE_BACKEND = InMemoryQueueBackend()
_IN_MEMORY_QUEUE_RUNTIME = QueueWorkerRuntime(
    repositories=_IN_MEMORY_REPOSITORIES,
    queue_backend=_IN_MEMORY_QUEUE_BACKEND,
    object_store_resolver=lambda dataset_id: _phase2_object_store_for_dataset(dataset_id),
)


def _get_registry() -> ToolRegistry:
    return load_manifests()


class PlannerPreviewRequest(BaseModel):
    userPrompt: str = Field(min_length=1)
    datasetId: str = Field(min_length=1)
    profileId: str = Field(default="")
    provider: str | None = Field(default=None)
    baseUrl: str | None = None
    model: str | None = None
    secretId: str | None = None
    temperature: float | None = None
    maxTokens: int | None = None
    timeoutSeconds: float | None = None


class PlannerValidateRequest(BaseModel):
    plan: dict[str, Any]


class PlannerJobsRequest(BaseModel):
    userPrompt: str = Field(min_length=1)
    projectId: str = Field(default="project_local", min_length=1)
    datasetId: str = Field(min_length=1)
    profileId: str = Field(default="")
    enqueue: bool = Field(default=False)
    execute: bool = Field(default=False)
    provider: str | None = Field(default=None)
    baseUrl: str | None = None
    model: str | None = None
    secretId: str | None = None
    temperature: float | None = None
    maxTokens: int | None = None
    timeoutSeconds: float | None = None


@dataclass
class PlannerPreviewResult:
    plan: dict[str, Any] | None
    raw_response: str | None
    validation: PlanValidationResult | None
    model: str
    planner_provider: str | None = None


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
    planner_provider: str | None = None
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
    try:
        llm = _select_planner_provider(request.provider, provider=provider)
        user_config = _planner_user_config_from_request(request)
    except LLMProviderError as exc:
        return PlannerPreviewResult(
            plan=None,
            raw_response=None,
            validation=_provider_error_validation(exc),
            model="unavailable",
            planner_provider=request.provider,
        )
    tools = [t for t in reg.tools if t.stage == "mvp"]

    planner_req = PlannerRequest(
        user_prompt=request.userPrompt,
        dataset_id=request.datasetId,
        profile_id=request.profileId or request.datasetId,
        tool_registry_version=reg.version,
    )

    # We use a minimal data profile stub — in production the caller
    # would pass a real profile via the API request.
    dp = _planner_data_profile(request.datasetId, request.profileId or request.datasetId)

    try:
        resp: PlannerRawResponse = llm.generate_plan(planner_req, tools=tools, data_profile=dp, user_config=user_config)
    except LLMProviderError as exc:
        return PlannerPreviewResult(
            plan=None,
            raw_response=None,
            validation=_provider_error_validation(exc),
            model=_provider_model(llm),
            planner_provider=_provider_name(llm),
        )

    plan = resp.raw_json if resp.raw_json else None
    validation = validate_plan(plan, registry=reg) if plan else _empty_plan_validation()

    return PlannerPreviewResult(
        plan=plan,
        raw_response=resp.raw_text,
        validation=validation,
        model=resp.model,
        planner_provider=_provider_name(llm),
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
    try:
        llm = _select_planner_provider(request.provider, provider=provider)
        user_config = _planner_user_config_from_request(request)
    except LLMProviderError as exc:
        return _planner_jobs_provider_error(exc, planner_provider=request.provider)
    tools = [t for t in reg.tools if t.stage == "mvp"]

    planner_req = PlannerRequest(
        user_prompt=request.userPrompt,
        dataset_id=request.datasetId,
        profile_id=request.profileId or request.datasetId,
        tool_registry_version=reg.version,
    )

    dp = _planner_data_profile(request.datasetId, request.profileId or request.datasetId)

    try:
        resp: PlannerRawResponse = llm.generate_plan(planner_req, tools=tools, data_profile=dp, user_config=user_config)
    except LLMProviderError as exc:
        return _planner_jobs_provider_error(exc, planner_provider=_provider_name(llm))

    plan = resp.raw_json
    if plan is None:
        return PlannerJobsResult(
            ok=False,
            job_id=None,
            plan_id=None,
            plan_hash=None,
            validation_errors=[{"code": "PLAN_EMPTY", "message": "LLM returned no plan.", "detail": None}],
            plan=None,
            planner_provider=_provider_name(llm),
        )

    validation = validate_plan(plan, registry=reg)
    if not validation.ok:
        return PlannerJobsResult(
            ok=False,
            job_id=None,
            plan_id=None,
            plan_hash=None,
            validation_errors=[{"code": e.code, "message": e.message, "detail": e.detail} for e in validation.errors],
            plan=None,
            planner_provider=_provider_name(llm),
        )

    from mdi_schemas import AnalysisPlan

    validated_plan = AnalysisPlan.model_validate(plan)
    input_ref_errors = _validate_executable_input_refs(validated_plan, request.datasetId)
    if input_ref_errors:
        return PlannerJobsResult(
            ok=False,
            job_id=None,
            plan_id=None,
            plan_hash=None,
            validation_errors=input_ref_errors,
            plan=None,
            planner_provider=_provider_name(llm),
        )

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
    executed = False
    if request.enqueue or request.execute:
        enqueued = runtime.submit_job(job_id).enqueued
        executed = _maybe_execute_local_memory_job(
            runtime,
            job_id,
            repositories=repositories,
            queue_runtime=queue_runtime,
        )

    return PlannerJobsResult(
        ok=True,
        job_id=job_id,
        plan_id=plan_id,
        plan_hash=plan_hash,
        validation_errors=[],
        plan=validated_plan.model_dump(mode="json"),
        plan_source="llm",
        planner_provider=planner_provider,
        enqueued=enqueued,
        executed=executed,
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


def stream_planner_job_events(job_id: str, after_seq: int = 0, *, repositories: Any = None) -> Any:
    """Replay persisted planner JobEvents as SSE without mutating execution state."""
    events = get_planner_job_events(job_id, after_seq=after_seq, repositories=repositories)

    def body() -> Any:
        for event in events:
            yield _planner_sse_event(event)

    try:
        from fastapi.responses import StreamingResponse

        return StreamingResponse(body(), media_type="text/event-stream")
    except Exception:
        return events


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
        artifact_storage = create_artifact_storage_from_settings(settings)
        runtime = queue_runtime or QueueWorkerRuntime(
            repository_factory=factory,
            artifact_storage=artifact_storage,
            queue_backend=RedisRQQueueBackend(redis_url=settings.redis_url)
            if _should_use_redis_queue(settings)
            else InMemoryQueueBackend(),
            object_store_resolver=DurableObjectStoreResolver(
                repository_factory=factory,
                artifact_storage=artifact_storage,
            ),
            artifact_root=getattr(settings, "artifact_root", ".artifacts/phase2"),
        )
        return repos, runtime

    runtime = queue_runtime or _IN_MEMORY_QUEUE_RUNTIME
    return _IN_MEMORY_REPOSITORIES, runtime


def _planner_read_repositories(repositories: Any) -> Any:
    repos, _runtime = _planner_repositories_and_runtime(repositories=repositories, queue_runtime=None)
    return repos


def reset_planner_runtime() -> None:
    """Reset the local in-memory planner repository/queue runtime for tests."""
    global _IN_MEMORY_REPOSITORIES, _IN_MEMORY_QUEUE_BACKEND, _IN_MEMORY_QUEUE_RUNTIME
    _IN_MEMORY_REPOSITORIES = InMemoryRepositoryBundle.create()
    _IN_MEMORY_QUEUE_BACKEND = InMemoryQueueBackend()
    _IN_MEMORY_QUEUE_RUNTIME = QueueWorkerRuntime(
        repositories=_IN_MEMORY_REPOSITORIES,
        queue_backend=_IN_MEMORY_QUEUE_BACKEND,
        object_store_resolver=lambda dataset_id: _phase2_object_store_for_dataset(dataset_id),
    )


def _ensure_planner_project_dataset(repos: Any, *, project_id: str, dataset_id: str, created_by: str) -> None:
    try:
        repos.projects.get(project_id)
    except LookupError:
        repos.projects.save({"id": project_id, "name": project_id, "createdBy": created_by})
    try:
        repos.datasets.get(dataset_id)
    except LookupError:
        repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": dataset_id, "createdBy": created_by})


def _planner_data_profile(dataset_id: str, profile_id: str) -> Any:
    try:
        from mdi_api.phase2_runtime import get_phase2_dataset_profile_model

        return get_phase2_dataset_profile_model(dataset_id)
    except Exception:
        from mdi_schemas import DataProfile

        return DataProfile(
            profileId=profile_id or dataset_id,
            datasetId=dataset_id,
            version="0.1",
            datasetType="ml",
            createdAt="2026-06-27T00:00:00+00:00",
        )


def _phase2_object_store_for_dataset(dataset_id: str) -> dict[str, Any] | None:
    try:
        from mdi_api.phase2_runtime import get_phase2_dataset_object_store

        return get_phase2_dataset_object_store(dataset_id)
    except Exception:
        return None


def _validate_executable_input_refs(plan: Any, dataset_id: str) -> list[dict[str, Any]]:
    object_store = _phase2_object_store_for_dataset(dataset_id)
    if not object_store:
        return []

    available = set(str(key) for key in object_store.keys())
    errors: list[dict[str, Any]] = []
    required_ref_by_domain = {
        "composition.": "formulas",
        "structure.": "structures",
        "ml.": "ml_table",
    }
    for step in plan.steps:
        input_refs = list(step.inputRefs or [])
        expected_ref = None
        for prefix, ref in required_ref_by_domain.items():
            if step.toolId.startswith(prefix) and ref in available:
                expected_ref = ref
                break
        if expected_ref and not input_refs:
            errors.append(
                {
                    "code": "INPUT_REF_MISSING",
                    "message": f"Step '{step.stepId}' must reference dataset object '{expected_ref}'.",
                    "detail": {"stepId": step.stepId, "toolId": step.toolId, "availableRefs": sorted(available), "expectedRef": expected_ref},
                }
            )
            continue
        for input_ref in input_refs:
            ref = str(input_ref.ref)
            if ref not in available:
                errors.append(
                    {
                        "code": "INPUT_REF_UNRESOLVED",
                        "message": f"Step '{step.stepId}' references unavailable dataset object '{ref}'.",
                        "detail": {"stepId": step.stepId, "toolId": step.toolId, "ref": ref, "availableRefs": sorted(available)},
                    }
                )
    return errors


def _maybe_execute_local_memory_job(
    runtime: QueueWorkerRuntime,
    job_id: str,
    *,
    repositories: Any,
    queue_runtime: QueueWorkerRuntime | None,
) -> bool:
    if repositories is not None or queue_runtime is not None:
        return False
    settings = load_settings()
    if _should_use_redis_queue(settings):
        return False
    if not isinstance(getattr(runtime, "queue_backend", None), InMemoryQueueBackend):
        return False
    result = runtime.handle_job(job_id)
    return result.status == "completed"


def _provider_name(provider: Any) -> str:
    meta = getattr(provider, "meta", None)
    name = getattr(meta, "name", None)
    return str(name or provider.__class__.__name__)


def _provider_model(provider: Any) -> str:
    meta = getattr(provider, "meta", None)
    model = getattr(meta, "model", None)
    return str(model or "unavailable")


def _select_planner_provider(requested_provider: str | None, *, provider: Any = None) -> Any:
    if provider is not None:
        return provider
    provider_name = (requested_provider or os.getenv("MDI_LLM_PROVIDER") or "mock").strip().lower()
    if provider_name in {"", "mock", "mock_llm", "deterministic", "safe_mock"}:
        return _LLM_PROVIDER
    if provider_name == "openai_compatible":
        return OpenAICompatibleProvider()
    raise LLMProviderError(
        f"Unsupported planner provider '{provider_name}'.",
        code="LLM_PROVIDER_UNSUPPORTED",
    )


def _planner_user_config_from_request(request: Any) -> PlannerUserConfig | None:
    fields = ("baseUrl", "model", "secretId", "temperature", "maxTokens", "timeoutSeconds")
    provider_name = (getattr(request, "provider", None) or os.getenv("MDI_LLM_PROVIDER") or "mock").strip().lower()
    has_explicit_config = any(getattr(request, field, None) not in (None, "") for field in fields)
    if not has_explicit_config:
        return None
    if provider_name not in {"openai_compatible"}:
        return None

    api_key = None
    secret_id = getattr(request, "secretId", None)
    if secret_id:
        from mdi_api.routers.secrets import get_secret_value, mark_secret_used

        api_key = get_secret_value(secret_id)
        if not api_key:
            raise LLMProviderError(
                "OpenAI-compatible LLM provider is not configured: missing API key.",
                code="LLM_API_KEY_MISSING",
            )
        mark_secret_used(secret_id)

    return PlannerUserConfig(
        provider="openai_compatible",
        model=getattr(request, "model", None) or "gpt-4o",
        base_url=getattr(request, "baseUrl", None),
        api_key=api_key,
        timeout_seconds=float(getattr(request, "timeoutSeconds", None) or 30.0),
        temperature=float(getattr(request, "temperature", None) if getattr(request, "temperature", None) is not None else 0.2),
        max_tokens=int(getattr(request, "maxTokens", None) or 4096),
    )


def _provider_error_validation(error: LLMProviderError) -> PlanValidationResult:
    return PlanValidationResult(
        ok=False,
        errors=[
            PlanValidationError(
                code=error.code,
                message=error.safe_message,
                detail={"statusCode": error.status_code} if error.status_code else None,
            )
        ],
    )


def _provider_error_payload(error: LLMProviderError) -> list[dict[str, Any]]:
    return [
        {
            "code": error.code,
            "message": error.safe_message,
            "detail": {"statusCode": error.status_code} if error.status_code else None,
        }
    ]


def _planner_jobs_provider_error(error: LLMProviderError, *, planner_provider: str | None) -> PlannerJobsResult:
    return PlannerJobsResult(
        ok=False,
        job_id=None,
        plan_id=None,
        plan_hash=None,
        validation_errors=_provider_error_payload(error),
        plan=None,
        planner_provider=planner_provider,
        enqueued=False,
        executed=False,
    )


def _empty_plan_validation() -> PlanValidationResult:
    return PlanValidationResult(
        ok=False,
        errors=[PlanValidationError(code="PLAN_EMPTY", message="LLM returned no plan.", detail=None)],
    )


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


def _planner_sse_event(event: dict[str, Any]) -> str:
    event_id = str(event.get("seq") or event.get("id") or "")
    event_name = str(event.get("eventType") or event.get("event_type") or "message")
    data = json.dumps(event, separators=(",", ":"), sort_keys=True)
    return f"id: {event_id}\nevent: {event_name}\ndata: {data}\n\n"


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
