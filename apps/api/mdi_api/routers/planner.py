"""Planner API routes — POST /planner/preview, /planner/validate, /planner/jobs."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
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
    AnalysisIntentError,
    AnalysisIntentRequest,
    AnalysisIntentValidator,
    ClarificationSubmission,
    DeterministicAnalysisIntentBuilder,
    LLMProviderError,
    MockLLMProvider,
    OpenAICompatibleAnalysisIntentBuilder,
    OpenAICompatibleProvider,
    PlannerRawResponse,
    PlannerRequest,
    PlannerUserConfig,
    redact_credential_values,
    redact_params_for_log,
)
from mdi_schemas import (
    AnalysisIntent,
    AnalysisIntentConstraints,
    AnalysisIntentOutcome,
    ClarificationAnswer,
    DataProfile,
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
    intentSchemaVersion: str | None = None
    intentId: str | None = None
    selectedResourceIds: list[str] = Field(default_factory=list, max_length=32)
    selectedTargetIds: list[str] = Field(default_factory=list, max_length=32)


class PlannerIntentCreateRequest(BaseModel):
    rawGoal: str = Field(min_length=1, max_length=16_384)
    projectId: str = Field(default="project_local", min_length=1)
    datasetId: str = Field(min_length=1)
    profileId: str = Field(min_length=1)
    selectedResourceIds: list[str] = Field(default_factory=list, max_length=32)
    selectedTargetIds: list[str] = Field(default_factory=list, max_length=32)
    constraints: AnalysisIntentConstraints = Field(default_factory=AnalysisIntentConstraints)
    provider: str | None = None
    baseUrl: str | None = None
    model: str | None = None
    secretId: str | None = None
    temperature: float | None = None
    maxTokens: int | None = None
    timeoutSeconds: float | None = None


class PlannerIntentClarificationRequest(BaseModel):
    expectedProfileSemanticHash: str = Field(min_length=1, max_length=128)
    answers: list[ClarificationAnswer] = Field(min_length=1, max_length=3)


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
    intent_id: str | None = None
    intent_outcome: str | None = None
    intent: dict[str, Any] | None = None
    error_code: str | None = None


@dataclass
class PlannerIntentResult:
    ok: bool
    intent_id: str | None
    outcome: str | None
    intent: dict[str, Any] | None
    error_code: str | None = None
    errors: list[dict[str, Any]] = field(default_factory=list)


def create_planner_intent(
    request: PlannerIntentCreateRequest,
    *,
    provider: Any = None,
    repositories: Any = None,
    queue_runtime: Any = None,
) -> PlannerIntentResult:
    repos, _runtime = _planner_repositories_and_runtime(repositories=repositories, queue_runtime=queue_runtime)
    created_by = "user_local"
    _ensure_planner_project_dataset(
        repos,
        project_id=request.projectId,
        dataset_id=request.datasetId,
        created_by=created_by,
    )
    try:
        profile = _planner_exact_data_profile(repos, request.datasetId, request.profileId)
        intent = _build_planner_intent(
            raw_goal=request.rawGoal,
            dataset_id=request.datasetId,
            profile_id=request.profileId,
            selected_resource_ids=request.selectedResourceIds,
            selected_target_ids=request.selectedTargetIds,
            constraints=request.constraints,
            requested_provider=request.provider,
            provider=provider,
            user_config=_planner_user_config_from_request(request),
            profile=profile,
        )
        _persist_planner_intent(repos, request.projectId, intent, created_by=created_by)
        return _intent_result(intent)
    except (AnalysisIntentError, LLMProviderError) as exc:
        return _intent_error_result(exc)


def get_planner_intent(intent_id: str, *, repositories: Any = None) -> PlannerIntentResult:
    repos = _planner_read_repositories(repositories)
    try:
        record = repos.analysis_intents.get_intent(intent_id)
        intent = AnalysisIntent.model_validate(record["analysisIntent"])
        return _intent_result(intent)
    except LookupError:
        return PlannerIntentResult(
            ok=False,
            intent_id=None,
            outcome=None,
            intent=None,
            error_code="INTENT_NOT_FOUND",
            errors=[{"code": "INTENT_NOT_FOUND", "message": "AnalysisIntent was not found.", "field": "intentId"}],
        )


def clarify_planner_intent(
    intent_id: str,
    request: PlannerIntentClarificationRequest,
    *,
    repositories: Any = None,
    queue_runtime: Any = None,
) -> PlannerIntentResult:
    repos, _runtime = _planner_repositories_and_runtime(repositories=repositories, queue_runtime=queue_runtime)
    try:
        record = repos.analysis_intents.get_intent(intent_id)
        parent = AnalysisIntent.model_validate(record["analysisIntent"])
        profile = _planner_exact_data_profile(repos, parent.datasetId, parent.profileId)
        revised = DeterministicAnalysisIntentBuilder().clarify(
            parent,
            ClarificationSubmission(
                intent_id=intent_id,
                answers=tuple(request.answers),
                expected_profile_semantic_hash=request.expectedProfileSemanticHash,
            ),
            profile=profile,
        )
        _persist_planner_intent(repos, str(record["projectId"]), revised, created_by=str(record.get("createdBy") or "user_local"))
        return _intent_result(revised)
    except LookupError:
        return PlannerIntentResult(
            ok=False,
            intent_id=intent_id,
            outcome=None,
            intent=None,
            error_code="INTENT_NOT_FOUND",
            errors=[{"code": "INTENT_NOT_FOUND", "message": "AnalysisIntent was not found.", "field": "intentId"}],
        )
    except AnalysisIntentError as exc:
        return _intent_error_result(exc, intent_id=intent_id)


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

    repos, runtime = _planner_repositories_and_runtime(repositories=repositories, queue_runtime=queue_runtime)
    created_by = "user_local"
    project_id = request.projectId
    dataset_id = request.datasetId
    profile_id = request.profileId or request.datasetId
    intent: AnalysisIntent | None = None
    if request.intentSchemaVersion is not None or request.intentId is not None:
        _ensure_planner_project_dataset(repos, project_id=project_id, dataset_id=dataset_id, created_by=created_by)
        if request.intentSchemaVersion not in {None, "1.0"}:
            return _planner_jobs_intent_error("INTENT_SCHEMA_UNSUPPORTED", "Only AnalysisIntent schema 1.0 is supported.")
        try:
            dp = _planner_exact_data_profile(repos, dataset_id, profile_id)
            if request.intentId:
                record = repos.analysis_intents.get_intent(request.intentId)
                intent = AnalysisIntent.model_validate(record["analysisIntent"])
                AnalysisIntentValidator().validate(intent, profile=dp)
                if intent.datasetId != dataset_id or intent.profileId != profile_id or intent.rawGoal != redact_credential_values(request.userPrompt):
                    raise AnalysisIntentError("Planner request does not match the persisted Intent.", code="INTENT_REQUEST_MISMATCH")
            else:
                intent = _build_planner_intent(
                    raw_goal=request.userPrompt,
                    dataset_id=dataset_id,
                    profile_id=profile_id,
                    selected_resource_ids=request.selectedResourceIds,
                    selected_target_ids=request.selectedTargetIds,
                    constraints=AnalysisIntentConstraints(
                        includeResourceIds=request.selectedResourceIds,
                        targetIds=request.selectedTargetIds,
                    ),
                    requested_provider=request.provider,
                    provider=llm,
                    user_config=user_config,
                    profile=dp,
                )
                _persist_planner_intent(repos, project_id, intent, created_by=created_by)
        except LookupError:
            return _planner_jobs_intent_error("INTENT_NOT_FOUND", "The requested AnalysisIntent was not found.")
        except (AnalysisIntentError, LLMProviderError) as exc:
            code = exc.code
            message = exc.safe_message if isinstance(exc, LLMProviderError) else str(exc)
            return _planner_jobs_intent_error(code, message)
        if intent.outcome is not AnalysisIntentOutcome.ready:
            return PlannerJobsResult(
                ok=False,
                job_id=None,
                plan_id=None,
                plan_hash=None,
                validation_errors=[],
                plan=None,
                planner_provider=_provider_name(llm),
                intent_id=intent.intentId,
                intent_outcome=intent.outcome.value,
                intent=intent.model_dump(mode="json"),
                error_code="INTENT_CLARIFICATION_REQUIRED" if intent.outcome is AnalysisIntentOutcome.needs_clarification else "INTENT_UNSUPPORTED",
            )
    else:
        dp = _planner_data_profile(dataset_id, profile_id)

    planner_req = PlannerRequest(
        user_prompt=intent.rawGoal if intent is not None else request.userPrompt,
        dataset_id=dataset_id,
        profile_id=profile_id,
        tool_registry_version=reg.version,
    )

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
            intent_id=intent.intentId if intent else None,
            intent_outcome=intent.outcome.value if intent else None,
            intent=intent.model_dump(mode="json") if intent else None,
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
            intent_id=intent.intentId if intent else None,
            intent_outcome=intent.outcome.value if intent else None,
            intent=intent.model_dump(mode="json") if intent else None,
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
            intent_id=intent.intentId if intent else None,
            intent_outcome=intent.outcome.value if intent else None,
            intent=intent.model_dump(mode="json") if intent else None,
        )

    plan_hash = compute_plan_hash(validated_plan)
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
    if intent is not None:
        repos.analysis_intents.attach_execution(intent.intentId, plan_id, job_id)
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
        intent_id=intent.intentId if intent else None,
        intent_outcome=intent.outcome.value if intent else None,
        intent=intent.model_dump(mode="json") if intent else None,
    )


def planner_preview_route(request: PlannerPreviewRequest) -> PlannerPreviewResult:
    return planner_preview(request)


def planner_validate_route(request: PlannerValidateRequest) -> PlannerValidateResult:
    return planner_validate(request)


def planner_jobs_route(request: PlannerJobsRequest) -> PlannerJobsResult:
    return planner_jobs(request)


def create_planner_intent_route(request: PlannerIntentCreateRequest) -> PlannerIntentResult:
    return create_planner_intent(request)


def get_planner_intent_route(intent_id: str) -> PlannerIntentResult:
    return get_planner_intent(intent_id)


def clarify_planner_intent_route(intent_id: str, request: PlannerIntentClarificationRequest) -> PlannerIntentResult:
    return clarify_planner_intent(intent_id, request)


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
    intent_binding = repos.analysis_intents.get_execution_for_job(job_id)
    intent_record = repos.analysis_intents.get_intent(intent_binding["intentId"]) if intent_binding else None
    intent_payload = (intent_record or {}).get("analysisIntent")
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
        "intentId": (intent_binding or {}).get("intentId"),
        "intentOutcome": (intent_payload or {}).get("outcome"),
        "analysisIntent": intent_payload,
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


def get_planner_job_artifact_content(
    job_id: str,
    artifact_id: str,
    *,
    repositories: Any = None,
    queue_runtime: QueueWorkerRuntime | None = None,
) -> Any:
    """Return bounded artifact bytes through the authenticated application API."""

    def make_response() -> Any:
        from fastapi.responses import Response

        repos, runtime = _planner_repositories_and_runtime(
            repositories=repositories,
            queue_runtime=queue_runtime,
        )
        job = repos.jobs.get(job_id)
        if not job:
            raise LookupError("Planner job was not found.")
        artifact = repos.artifacts.get(artifact_id)
        if str(artifact.get("jobId") or artifact.get("job_id")) != job_id:
            raise LookupError("Artifact does not belong to the requested job.")
        size = int(artifact.get("sizeBytes") or artifact.get("size_bytes") or 0)
        maximum = 67_108_864
        if size <= 0 or size > maximum:
            raise ValueError("Artifact content exceeds the browser transfer cap.")
        storage_key = str(artifact.get("storageKey") or artifact.get("storage_key") or "")
        content = runtime.artifact_storage.get_bytes(storage_key)
        expected_hash = str(artifact.get("sha256") or artifact.get("contentHash") or artifact.get("content_hash") or "")
        if len(content) != size or hashlib.sha256(content).hexdigest() != expected_hash:
            raise ValueError("Artifact content failed size or hash validation.")
        media_type = str(
            artifact.get("contentType")
            or artifact.get("content_type")
            or (artifact.get("metadata") or {}).get("provenance", {}).get("mediaType")
            or "application/octet-stream"
        )
        allowed = {
            "application/json",
            "application/gzip",
            "application/octet-stream",
            "application/vnd.mdi.volumetric+float32",
            "application/vnd.mdi.volumetric+float64",
            "text/markdown",
        }
        if media_type not in allowed:
            raise ValueError("Artifact media type is not available through the bounded content route.")
        return Response(
            content=content,
            media_type=media_type,
            headers={
                "X-Content-SHA256": expected_hash,
                "X-Content-Length-Validated": str(size),
                "Cache-Control": "private, no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )

    try:
        return make_response()
    except LookupError as error:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Planner artifact content was not found.") from error
    except ValueError as error:
        from fastapi import HTTPException

        raise HTTPException(status_code=422, detail="Planner artifact content failed bounded validation.") from error


def get_planner_job_artifact_content_route(job_id: str, artifact_id: str) -> Any:
    """HTTP boundary for bounded job-scoped artifact bytes."""

    return get_planner_job_artifact_content(job_id, artifact_id)


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


def _planner_exact_data_profile(repos: Any, dataset_id: str, profile_id: str) -> DataProfile:
    try:
        stored = repos.data_profiles.get(profile_id)
        profile = DataProfile.model_validate(stored)
    except LookupError:
        try:
            from mdi_api.phase2_runtime import get_phase2_dataset_profile_model

            profile = get_phase2_dataset_profile_model(dataset_id)
        except Exception as exc:
            raise AnalysisIntentError(
                "The exact DataProfile 2.0 record is unavailable.",
                code="STALE_PROFILE",
                field="profileId",
            ) from exc
        if profile.profileId == profile_id:
            repos.data_profiles.save(profile)
    if profile.datasetId != dataset_id or profile.profileId != profile_id:
        raise AnalysisIntentError(
            "The requested dataset/profile identity does not match the current profile.",
            code="STALE_PROFILE",
            field="profileId",
        )
    if profile.profileContractVersion != "2.0" or not profile.semanticHash:
        raise AnalysisIntentError(
            "AnalysisIntent requires an exact DataProfile 2.0 semantic identity.",
            code="PROFILE_2_REQUIRED",
            field="profileId",
        )
    return profile


def _build_planner_intent(
    *,
    raw_goal: str,
    dataset_id: str,
    profile_id: str,
    selected_resource_ids: list[str],
    selected_target_ids: list[str],
    constraints: AnalysisIntentConstraints,
    requested_provider: str | None,
    provider: Any,
    user_config: PlannerUserConfig | None,
    profile: DataProfile,
) -> AnalysisIntent:
    intent_request = AnalysisIntentRequest(
        raw_goal=raw_goal,
        dataset_id=dataset_id,
        profile_id=profile_id,
        selected_resource_ids=tuple(selected_resource_ids),
        selected_target_ids=tuple(selected_target_ids),
        constraints=constraints,
    )
    provider_name = (requested_provider or "mock").strip().lower()
    if provider_name == "openai_compatible":
        llm = provider if isinstance(provider, OpenAICompatibleProvider) else OpenAICompatibleProvider()
        return OpenAICompatibleAnalysisIntentBuilder(llm).build(intent_request, profile=profile, user_config=user_config)
    return DeterministicAnalysisIntentBuilder().build(intent_request, profile=profile)


def _persist_planner_intent(repos: Any, project_id: str, intent: AnalysisIntent, *, created_by: str) -> dict[str, Any]:
    return repos.analysis_intents.save_intent(
        {
            "projectId": project_id,
            "analysisIntent": intent.model_dump(mode="json"),
            "createdBy": created_by,
        }
    )


def _intent_result(intent: AnalysisIntent) -> PlannerIntentResult:
    return PlannerIntentResult(
        ok=True,
        intent_id=intent.intentId,
        outcome=intent.outcome.value,
        intent=intent.model_dump(mode="json"),
    )


def _intent_error_result(error: AnalysisIntentError | LLMProviderError, *, intent_id: str | None = None) -> PlannerIntentResult:
    code = error.code
    message = error.safe_message if isinstance(error, LLMProviderError) else str(error)
    field = getattr(error, "field", None)
    return PlannerIntentResult(
        ok=False,
        intent_id=intent_id,
        outcome=None,
        intent=None,
        error_code=code,
        errors=[{"code": code, "message": message, "field": field}],
    )


def _planner_jobs_intent_error(code: str, message: str) -> PlannerJobsResult:
    return PlannerJobsResult(
        ok=False,
        job_id=None,
        plan_id=None,
        plan_hash=None,
        validation_errors=[{"code": code, "message": message, "detail": None}],
        plan=None,
        error_code=code,
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
        "table.": "ml_table",
        "viz.": "ml_table",
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
