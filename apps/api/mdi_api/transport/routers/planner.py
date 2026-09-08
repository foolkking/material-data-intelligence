"""Planner API routes — POST /planner/preview, /planner/validate, /planner/jobs."""

from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass, field, replace
import hashlib
import json
import os
import re
from typing import Any, Literal, Mapping
import uuid

from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel, Field
from sqlalchemy import select

from mdi_api.config import load_settings
from mdi_api.application.providers.selection import (
    _MOCK_PROVIDER as _canonical_mock_provider,
    requested_provider_name,
    select_llm_provider,
    test_providers_allowed,
)
from mdi_api.artifact_storage import create_artifact_storage_from_settings
from mdi_api.bootstrap.repository_factory import create_repository_factory
from mdi_api.db import (
    agent2_scientific_interpretations,
    artifacts,
    scientific_result_snapshots,
    tool_calls,
)
from mdi_api.repositories import InMemoryRepositoryBundle, compute_plan_hash
from mdi_api.provider_connections import decrypt_api_key, get_connection, thinking_budget
from mdi_llm import (
    ARTIFACT_PROJECTOR_CONTRACTS,
    AnalysisIntentError,
    AnalysisIntentRequest,
    AnalysisIntentValidator,
    CapabilityPlanningError,
    CapabilityPlanningResult,
    ClarificationSubmission,
    DeterministicAnalysisIntentBuilder,
    DEEPSEEK_DEFAULT_MODEL,
    DeepSeekProvider,
    LLMProviderError,
    MockLLMProvider,  # noqa: F401 - preserved planner patch/import surface
    OpenAICompatibleAnalysisIntentBuilder,
    OpenAICompatibleProvider,
    PlannerRawResponse,
    PlannerRequest,
    PlannerUserConfig,
    plan_capabilities,
    redact_credential_values,
    ArtifactProjectionInput,
    InterpretationError,
    InterpretationSource,
    build_scientific_evidence_bundle,
    deterministic_interpret,
    no_supported_evidence_result,
    strict_provider_interpret,
)
from mdi_schemas import (
    AnalysisIntent,
    AnalysisIntentConstraints,
    AnalysisIntentOutcome,
    CapabilityPlanningDecision,
    CapabilityPlanningOutcome,
    ClarificationAnswer,
    DataProfile,
    DependencyExecutionRecord,
    EligibilityResolution,
    InterpretationMode,
    capability_semantic_hash,
    compute_analysis_intent_hash,
    deterministic_capability_id,
    deterministic_intent_id,
    is_supported_data_profile_contract_version,
    validate_interpretation_json_bounds,
)
from mdi_workers import InMemoryQueueBackend, QueueWorkerRuntime, RedisRQQueueBackend, preflight_execution_resources
from mdi_workers.object_store import DurableObjectStoreResolver
from mdi_tool_registry import ToolRegistry, load_manifests, validate_dependency_plan
from mdi_tool_registry.plan_validator import PlanValidationError, PlanValidationResult, validate_plan


_LLM_PROVIDER = _canonical_mock_provider
_IN_MEMORY_REPOSITORIES = InMemoryRepositoryBundle.create()
_IN_MEMORY_QUEUE_BACKEND = InMemoryQueueBackend()
_IN_MEMORY_QUEUE_RUNTIME = QueueWorkerRuntime(
    repositories=_IN_MEMORY_REPOSITORIES,
    queue_backend=_IN_MEMORY_QUEUE_BACKEND,
    object_store_resolver=lambda dataset_id: _phase2_object_store_for_dataset(dataset_id),
)
_INTERPRETATION_PROJECTABLE_ARTIFACT_TYPES = frozenset({
    "table_json",
    "metrics_json",
    "structure_json",
    "phonon_band_json",
    "phonon_dos_json",
    "phonon_band_dos_json",
    "phonon_summary_json",
    "volumetric_field_json",
})
_INTERPRETATION_PRESENTATION_COMPANION_TYPES = frozenset({
    "plotly_json",
    "summary_md",
    "recipe_json",
})


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
    thinkingMode: Literal["quick", "standard", "deep"] = "standard"


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
    thinkingMode: Literal["quick", "standard", "deep"] = "standard"
    intentSchemaVersion: str | None = None
    intentId: str | None = None
    selectedResourceIds: list[str] = Field(default_factory=list, max_length=32)
    selectedTargetIds: list[str] = Field(default_factory=list, max_length=32)
    researchSessionId: str | None = Field(default=None, min_length=1, max_length=64)


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
    thinkingMode: Literal["quick", "standard", "deep"] = "standard"


class PlannerIntentClarificationRequest(BaseModel):
    expectedProfileSemanticHash: str = Field(min_length=1, max_length=128)
    answers: list[ClarificationAnswer] = Field(min_length=1, max_length=3)


class PlannerInterpretationRequest(BaseModel):
    mode: Literal["DETERMINISTIC", "STRICT_PROVIDER"] = "DETERMINISTIC"
    expectedPlanHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    idempotencyKey: str | None = Field(default=None, min_length=1, max_length=128)
    provider: str | None = Field(default=None, min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    baseUrl: str | None = Field(default=None, min_length=1, max_length=512)
    model: str | None = Field(default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_./:-]+$")
    secretId: str | None = Field(default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")
    temperature: float | None = Field(default=None, ge=0, le=2)
    maxTokens: int | None = Field(default=None, ge=1, le=32_768)
    timeoutSeconds: float | None = Field(default=None, ge=1, le=120)
    thinkingMode: Literal["quick", "standard", "deep"] = "standard"


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
    capability_outcome: str | None = None
    eligibility_resolution: dict[str, Any] | None = None
    capability_decision: dict[str, Any] | None = None
    provider_visible_tool_ids: list[str] = field(default_factory=list)
    plan_schema_version: str | None = None
    graph_hash: str | None = None
    dependency_bindings: list[dict[str, Any]] = field(default_factory=list)
    topological_order: list[str] = field(default_factory=list)


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
            user_config=_planner_user_config_from_request(request, selected_provider=provider),
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
        user_config = _planner_user_config_from_request(request, selected_provider=llm)
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
        raw_response=None if _provider_name(llm) == "deepseek" else resp.raw_text,
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
        user_config = _planner_user_config_from_request(request, selected_provider=llm)
    except LLMProviderError as exc:
        return _planner_jobs_provider_error(exc, planner_provider=request.provider)
    tools = [t for t in reg.tools if t.stage == "mvp"]

    repos, runtime = _planner_repositories_and_runtime(repositories=repositories, queue_runtime=queue_runtime)
    created_by = "user_local"
    project_id = request.projectId
    dataset_id = request.datasetId
    profile_id = request.profileId or request.datasetId
    intent: AnalysisIntent | None = None
    capability_result: CapabilityPlanningResult | None = None
    if request.intentSchemaVersion is not None or request.intentId is not None:
        _ensure_planner_project_dataset(repos, project_id=project_id, dataset_id=dataset_id, created_by=created_by)
        if request.intentSchemaVersion not in {None, "1.0", "1.1"}:
            return _planner_jobs_intent_error("INTENT_SCHEMA_UNSUPPORTED", "Only AnalysisIntent schema 1.0 or 1.1 is supported.")
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

    plan_source = "llm"
    if intent is not None:
        try:
            capability_result = plan_capabilities(
                intent,
                profile=dp,
                registry=reg,
                provider=llm,
                user_config=user_config,
            )
        except CapabilityPlanningError as exc:
            return _planner_jobs_capability_error(exc, intent=intent, planner_provider=_provider_name(llm))
        _persist_capability_planning(repos, capability_result, created_by=created_by)
        if capability_result.outcome.value != "PLAN_READY" or capability_result.plan is None:
            return PlannerJobsResult(
                ok=False,
                job_id=None,
                plan_id=None,
                plan_hash=None,
                validation_errors=[
                    {
                        "code": item.code,
                        "message": item.message,
                        "detail": {"field": item.field, "toolId": item.toolId},
                    }
                    for item in capability_result.decision.diagnostics
                ],
                plan=None,
                plan_source="capability_planner",
                planner_provider=_provider_name(llm),
                intent_id=intent.intentId,
                intent_outcome=intent.outcome.value,
                intent=intent.model_dump(mode="json"),
                error_code=capability_result.outcome.value,
                capability_outcome=capability_result.outcome.value,
                eligibility_resolution=capability_result.resolution.model_dump(mode="json"),
                capability_decision=capability_result.decision.model_dump(mode="json"),
                provider_visible_tool_ids=list(capability_result.provider_visible_tool_ids),
            )
        plan = capability_result.plan.model_dump(mode="json")
        plan_source = "capability_planner"
    else:
        planner_req = PlannerRequest(
            user_prompt=request.userPrompt,
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

    dependency_order: list[str] = []
    if plan.get("schemaVersion") == "0.2":
        selected_ids = sorted(item.toolId for item in capability_result.decision.selections) if capability_result else None
        dependency_validation = validate_dependency_plan(plan, registry=reg, selected_tool_ids=selected_ids)
        if not dependency_validation.ok:
            return PlannerJobsResult(
                ok=False,
                job_id=None,
                plan_id=None,
                plan_hash=None,
                validation_errors=[
                    {
                        "code": item.code.value,
                        "message": item.message,
                        "detail": {"field": item.field, "bindingId": item.bindingId},
                    }
                    for item in dependency_validation.errors
                ],
                plan=None,
                plan_source=plan_source,
                planner_provider=_provider_name(llm),
                intent_id=intent.intentId if intent else None,
                intent_outcome=intent.outcome.value if intent else None,
                intent=intent.model_dump(mode="json") if intent else None,
                error_code="VALIDATION_FAILED",
                capability_outcome="VALIDATION_FAILED",
                eligibility_resolution=capability_result.resolution.model_dump(mode="json") if capability_result else None,
                capability_decision=capability_result.decision.model_dump(mode="json") if capability_result else None,
                provider_visible_tool_ids=list(capability_result.provider_visible_tool_ids) if capability_result else [],
                plan_schema_version="0.2",
                graph_hash=plan.get("graphHash"),
                dependency_bindings=list(plan.get("dependencyBindings") or []),
            )
        dependency_order = dependency_validation.topological_order
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

    from mdi_schemas import AnalysisPlan, AnalysisPlanV02

    validated_plan = AnalysisPlanV02.model_validate(plan) if plan.get("schemaVersion") == "0.2" else AnalysisPlan.model_validate(plan)
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
    try:
        object_store = _execution_object_store_for_dataset(
            runtime,
            dataset_id=request.datasetId,
            profile_id=profile_id,
        )
    except (LookupError, ValueError) as exc:
        return PlannerJobsResult(
            ok=False,
            job_id=None,
            plan_id=None,
            plan_hash=None,
            validation_errors=[
                {
                    "code": "DURABLE_ROOT_INPUTS_INVALID",
                    "message": "Executable root source inputs failed durable identity or integrity validation.",
                    "detail": {"reason": str(exc)},
                }
            ],
            plan=None,
            planner_provider=_provider_name(llm),
            intent_id=intent.intentId if intent else None,
            intent_outcome=intent.outcome.value if intent else None,
            intent=intent.model_dump(mode="json") if intent else None,
        )
    if (
        (request.enqueue or request.execute)
        and _requires_durable_root_inputs(runtime)
        and not object_store
    ):
        return PlannerJobsResult(
            ok=False,
            job_id=None,
            plan_id=None,
            plan_hash=None,
            validation_errors=[
                {
                    "code": "DURABLE_ROOT_INPUTS_REQUIRED",
                    "message": "Executable jobs require all root source inputs to be durably resolvable.",
                    "detail": {"datasetId": request.datasetId, "profileId": profile_id},
                }
            ],
            plan=None,
            planner_provider=_provider_name(llm),
            intent_id=intent.intentId if intent else None,
            intent_outcome=intent.outcome.value if intent else None,
            intent=intent.model_dump(mode="json") if intent else None,
        )
    if object_store:
        execution_preflight = preflight_execution_resources(
            validated_plan,
            object_store=object_store,
            registry=reg,
            dataset_id=request.datasetId,
        )
        if not execution_preflight.ok:
            return PlannerJobsResult(
                ok=False,
                job_id=None,
                plan_id=None,
                plan_hash=None,
                validation_errors=[
                    {
                        "code": item.code,
                        "message": item.message,
                        "detail": {"stepId": item.step_id, "ref": item.ref},
                    }
                    for item in execution_preflight.issues
                ],
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
            "planSource": plan_source,
            "plannerProvider": planner_provider,
            "analysisPlan": validated_plan.model_dump(mode="json"),
            "planHash": plan_hash,
            "validationStatus": "validated",
            "createdBy": created_by,
        }
    )
    if validated_plan.schemaVersion == "0.2":
        repos.dependency_execution.save_plan_bindings(
            plan_id,
            plan_hash,
            validated_plan.graphHash,
            [item.model_dump(mode="json") for item in validated_plan.dependencyBindings],
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
    if capability_result is not None:
        repos.capability_planning.attach_execution(
            capability_result.decision.decisionId,
            intent.intentId,
            plan_id,
            job_id,
        )
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
        payload={"planId": plan_id, "planHash": plan_hash, "planSource": plan_source, "plannerProvider": planner_provider},
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
        plan_source=plan_source,
        planner_provider=planner_provider,
        enqueued=enqueued,
        executed=executed,
        intent_id=intent.intentId if intent else None,
        intent_outcome=intent.outcome.value if intent else None,
        intent=intent.model_dump(mode="json") if intent else None,
        capability_outcome=capability_result.outcome.value if capability_result else None,
        eligibility_resolution=capability_result.resolution.model_dump(mode="json") if capability_result else None,
        capability_decision=capability_result.decision.model_dump(mode="json") if capability_result else None,
        provider_visible_tool_ids=list(capability_result.provider_visible_tool_ids) if capability_result else [],
        plan_schema_version=validated_plan.schemaVersion,
        graph_hash=getattr(validated_plan, "graphHash", None),
        dependency_bindings=[item.model_dump(mode="json") for item in getattr(validated_plan, "dependencyBindings", [])],
        topological_order=dependency_order,
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
    capability_binding = repos.capability_planning.get_execution_for_job(job_id)
    capability_decision_record = (
        repos.capability_planning.get_decision(capability_binding["decisionId"])
        if capability_binding
        else None
    )
    capability_decision = (capability_decision_record or {}).get("capabilityDecision")
    capability_resolution_record = (
        repos.capability_planning.get_resolution(capability_decision["resolutionId"])
        if capability_decision
        else None
    )
    dependency_execution = repos.dependency_execution.get_execution_for_job(job_id)
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
        "capabilityPlanningOutcome": (capability_decision or {}).get("outcome"),
        "eligibilityResolution": (capability_resolution_record or {}).get("eligibilityResolution"),
        "capabilityDecision": capability_decision,
        "dependencyExecutionSummary": _dependency_execution_summary(dependency_execution),
    }


def get_planner_job_dependencies(job_id: str, *, repositories: Any = None) -> dict[str, Any]:
    """Read the immutable 0.2 graph, execution states, resolutions, and lineage."""
    repos = _planner_read_repositories(repositories)
    job = repos.jobs.get(job_id)
    plan_record = _try_get_job_plan(repos, job)
    plan = (plan_record or {}).get("analysisPlan") or {}
    plan_id = str((plan_record or {}).get("planId") or (plan_record or {}).get("id") or "")
    is_dependency_plan = plan.get("schemaVersion") == "0.2"
    execution = repos.dependency_execution.get_execution_for_job(job_id) if is_dependency_plan else None
    return {
        "jobId": job.get("jobId") or job.get("id"),
        "planId": plan_id or None,
        "planHash": _plan_hash(plan_record),
        "planSchemaVersion": plan.get("schemaVersion"),
        "graphHash": plan.get("graphHash"),
        "dependencyBindings": list(plan.get("dependencyBindings") or []),
        "plannedBindingRecords": repos.dependency_execution.list_plan_bindings(plan_id) if is_dependency_plan else [],
        "topologicalOrder": list((execution or {}).get("topologicalOrder") or []),
        "execution": execution,
        "bindingResolutions": repos.dependency_execution.list_binding_resolutions(job_id) if is_dependency_plan else [],
        "artifactLineage": repos.dependency_execution.list_lineage_for_job(job_id) if is_dependency_plan else [],
    }


def create_planner_job_interpretation(
    job_id: str,
    request: PlannerInterpretationRequest,
    *,
    repositories: Any = None,
    queue_runtime: QueueWorkerRuntime | None = None,
    provider: Any = None,
) -> dict[str, Any]:
    """Create a read-only, evidence-grounded interpretation for a terminal planner job."""
    repos, runtime = _planner_repositories_and_runtime(repositories=repositories, queue_runtime=queue_runtime)
    idempotency_key_hash = (
        hashlib.sha256(request.idempotencyKey.encode("utf-8")).hexdigest()
        if request.idempotencyKey
        else None
    )
    guard = (
        repos.interpretations.idempotency_guard(job_id, request.mode, idempotency_key_hash)
        if idempotency_key_hash
        else nullcontext()
    )
    with guard:
        return _create_planner_job_interpretation_locked(
            job_id,
            request,
            repos=repos,
            runtime=runtime,
            provider=provider,
            idempotency_key_hash=idempotency_key_hash,
        )


def _create_planner_job_interpretation_locked(
    job_id: str,
    request: PlannerInterpretationRequest,
    *,
    repos: Any,
    runtime: QueueWorkerRuntime,
    provider: Any,
    idempotency_key_hash: str | None,
) -> dict[str, Any]:
    try:
        job = repos.jobs.get(job_id)
        plan_record = _try_get_job_plan(repos, job)
        if plan_record is None:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "The job has no exact persisted AnalysisPlan.")
        plan_hash = _plan_hash(plan_record)
        if not plan_hash or plan_hash != request.expectedPlanHash:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "The expected AnalysisPlan hash is stale or mismatched.")
        source = _interpretation_source(repos, job, plan_record)
        candidates, unsupported_artifact_count = _interpretation_artifact_candidates(repos, runtime, source)
        bundle = build_scientific_evidence_bundle(
            source,
            candidates,
            unsupported_artifact_count=unsupported_artifact_count,
        )
        repos.interpretations.save_bundle(bundle)
        if idempotency_key_hash:
            existing_run = repos.interpretations.get_run_by_idempotency(job_id, request.mode, idempotency_key_hash)
            if existing_run is not None:
                if existing_run["bundleId"] != bundle.bundleId:
                    raise InterpretationError("SOURCE_INTEGRITY_FAILED", "The idempotency key is bound to different scientific evidence.")
                stored_interpretation = None
                if existing_run.get("interpretationId"):
                    stored_interpretation = repos.interpretations.get_interpretation(existing_run["interpretationId"])["interpretation"]
                execution = existing_run["execution"]
                return _interpretation_response(
                    outcome=execution["outcome"],
                    bundle=bundle.model_dump(mode="json"),
                    interpretation=stored_interpretation,
                    execution=execution,
                    diagnostics=list(execution.get("diagnostics") or []),
                )
        provider_identity = "deterministic"
        provider_model = None
        provider_config_hash = None
        if request.mode == "STRICT_PROVIDER":
            provider_identity = _requested_planner_provider_name(request.provider)
            saved_connection = get_connection(provider_identity)
            provider_model = request.model or (saved_connection.default_model if saved_connection else None) or os.getenv("DEEPSEEK_MODEL") or DEEPSEEK_DEFAULT_MODEL
            provider_config_hash = hashlib.sha256(json.dumps({
                "provider": provider_identity,
                "baseUrl": saved_connection.base_url if saved_connection else "https://api.deepseek.com",
                "model": provider_model,
                "temperature": 0,
                "maxTokens": request.maxTokens,
                "thinkingMode": request.thinkingMode,
                "timeoutSeconds": request.timeoutSeconds,
            }, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        if not bundle.evidenceItems:
            result = no_supported_evidence_result(
                bundle,
                mode=InterpretationMode(request.mode),
                provider_identity=provider_identity,
                provider_model=provider_model,
                provider_config_hash=provider_config_hash,
                idempotency_key_hash=idempotency_key_hash,
            )
            repos.interpretations.save_run(bundle, result.execution_record)
            return _interpretation_response(
                outcome=result.outcome.value,
                bundle=bundle.model_dump(mode="json"),
                interpretation=None,
                execution=result.execution_record.model_dump(mode="json"),
                diagnostics=list(result.diagnostics),
            )
        if request.mode == "DETERMINISTIC":
            result = deterministic_interpret(bundle, idempotency_key_hash=idempotency_key_hash)
        else:
            user_config = _planner_user_config_from_request(request)
            if user_config is not None:
                user_config = replace(user_config, max_tokens=min(user_config.max_tokens, 2_048))
            try:
                selected_provider = _select_interpretation_provider(request, provider=provider)
            except LLMProviderError as selection_error:
                def call_provider(
                    _projection: dict[str, Any],
                    _repair: bool,
                    error: LLMProviderError = selection_error,
                ) -> str:
                    raise error
            else:
                def call_provider(projection: dict[str, Any], repair: bool) -> str:
                    system = (
                        "Return exactly one JSON object matching the supplied Phase 10L-4 claim-selection contract. "
                        "Use only providerVisibleEvidenceIds. For a direct claim, copy claimType and semanticPredicate "
                        "from that evidence item's allowedDirectClaim, use exactly one subjectEvidenceId, include the same "
                        "ID in supportingEvidenceIds, and use empty limitingEvidenceIds, contradictingEvidenceIds, qualifiers, "
                        "and recommendations unless the projection supplies an exact permitted value. Return between one and "
                        "four non-duplicate direct claims total; never enumerate every evidence item. Do not add text, numbers, "
                        "units, entities, tools, plans, code, "
                        "paths, URLs, fields, or a second JSON value."
                    )
                    user_payload = {"projection": projection, "repair": repair}
                    response = selected_provider.complete_json(
                        messages=[
                            {"role": "system", "content": system},
                            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))},
                        ],
                        user_config=user_config,
                        purpose="GROUNDED_INTERPRETATION",
                    )
                    return response.raw_text or json.dumps(response.raw_json, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

            result = strict_provider_interpret(
                bundle,
                call_provider,
                provider_identity=provider_identity,
                provider_model=provider_model,
                provider_config_hash=provider_config_hash,
                idempotency_key_hash=idempotency_key_hash,
            )
        if result.interpretation is not None and result.execution_record is not None:
            stored = repos.interpretations.save_interpretation(bundle, result.interpretation, result.execution_record)
            return _interpretation_response(
                outcome=result.outcome.value,
                bundle=bundle.model_dump(mode="json"),
                interpretation=stored["interpretation"],
                execution=stored["execution"],
                diagnostics=list(result.diagnostics),
            )
        if result.execution_record is not None:
            stored_run = repos.interpretations.save_run(bundle, result.execution_record)
            execution = stored_run["execution"]
        else:
            execution = None
        return _interpretation_response(
            outcome=result.outcome.value,
            bundle=bundle.model_dump(mode="json"),
            interpretation=None,
            execution=execution,
            diagnostics=list(result.diagnostics),
        )
    except InterpretationError as error:
        return _interpretation_response(
            outcome=error.code,
            bundle=None,
            interpretation=None,
            execution=None,
            diagnostics=[str(error)],
        )
    except LLMProviderError as error:
        return _interpretation_response(
            outcome="PROVIDER_FAILED",
            bundle=None,
            interpretation=None,
            execution=None,
            diagnostics=[error.safe_message],
        )


def create_planner_job_interpretation_route(job_id: str, request: PlannerInterpretationRequest) -> dict[str, Any]:
    return create_planner_job_interpretation(job_id, request)


def list_planner_job_interpretations(job_id: str, *, repositories: Any = None) -> dict[str, Any]:
    repos = _planner_read_repositories(repositories)
    repos.jobs.get(job_id)
    records = repos.interpretations.list_for_job(job_id)
    runs = repos.interpretations.list_runs_for_job(job_id)
    return {
        "jobId": job_id,
        "interpretations": [item["interpretation"] for item in records],
        "runs": [item["execution"] for item in runs],
        "count": len(records),
        "runCount": len(runs),
    }


def get_planner_interpretation(interpretation_id: str, *, repositories: Any = None) -> dict[str, Any]:
    repos = _planner_read_repositories(repositories)
    return repos.interpretations.get_interpretation(interpretation_id)


def _get_agent2_interpretation_evidence(interpretation_id: str, repos: Any) -> dict[str, Any] | None:
    """Project an Agent2 interpretation through the legacy planner evidence route.

    Agent2 interpretations are persisted in their own immutable table, while
    the presentation client intentionally reuses the secured planner evidence
    endpoint.  Keep this adapter read-only and bounded: the Result snapshot is
    the authority for facts/source versions, and the Job-scoped tables only
    contribute inspectable execution descriptors.
    """
    try:
        interpretation_uuid = uuid.UUID(str(interpretation_id))
    except (TypeError, ValueError, AttributeError):
        return None
    bind = getattr(repos.interpretations, "bind", None)
    if bind is None:
        return None

    def read(connection: Any) -> dict[str, Any] | None:
        interpretation = connection.execute(
            select(agent2_scientific_interpretations).where(
                agent2_scientific_interpretations.c.id == interpretation_uuid
            )
        ).mappings().first()
        if interpretation is None:
            return None
        snapshot = connection.execute(
            select(scientific_result_snapshots).where(
                scientific_result_snapshots.c.id == interpretation["result_snapshot_id"]
            )
        ).mappings().first()
        if snapshot is None:
            return None

        bundle = snapshot.get("bundle_json") or {}
        if not isinstance(bundle, dict):
            bundle = {}
        facts = bundle.get("facts") if isinstance(bundle.get("facts"), list) else []
        fact_by_id = {
            str(item.get("fact_id") or item.get("factId")): item
            for item in facts
            if isinstance(item, dict) and (item.get("fact_id") or item.get("factId"))
        }
        source_refs: list[dict[str, Any]] = []
        for item in bundle.get("source_object_refs") or []:
            if not isinstance(item, dict):
                continue
            object_id = item.get("object_id") or item.get("objectId")
            version_id = item.get("version_id") or item.get("versionId")
            if not object_id or not version_id:
                continue
            source_refs.append({
                "objectId": str(object_id),
                "versionId": str(version_id),
                "objectType": item.get("object_type") or item.get("objectType"),
                "displayName": item.get("display_name") or item.get("displayName"),
            })

        job_id = str(snapshot.get("job_id") or bundle.get("provenance", {}).get("job_id") or "")
        raw_artifacts = connection.execute(
            select(artifacts).where(artifacts.c.job_id == job_id).order_by(artifacts.c.created_at, artifacts.c.id)
        ).mappings().all() if job_id else []
        artifact_rows = [dict(row) for row in raw_artifacts]
        artifact_by_id = {str(row["id"]): row for row in artifact_rows}
        artifact_descriptors = [{
            "id": str(row["id"]),
            "artifactId": str(row["id"]),
            "jobId": str(row["job_id"]),
            "toolCallId": str(row["tool_call_id"]) if row.get("tool_call_id") else None,
            "type": row.get("type"),
            "name": row.get("name"),
            "contentHash": row.get("content_hash") or row.get("sha256"),
            "sha256": row.get("sha256") or row.get("content_hash"),
            "contentType": row.get("content_type"),
        } for row in artifact_rows[:64]]
        raw_tools = connection.execute(
            select(tool_calls).where(tool_calls.c.job_id == job_id).order_by(tool_calls.c.created_at, tool_calls.c.id)
        ).mappings().all() if job_id else []
        tool_descriptors = [{
            "id": str(row["id"]),
            "toolCallId": str(row["id"]),
            "toolId": row.get("tool_id"),
            "status": row.get("status"),
        } for row in raw_tools[:64]]

        evidence_items: list[dict[str, Any]] = []
        source_artifact_ids: list[str] = []
        for raw in (bundle.get("evidence") or [])[:64]:
            if not isinstance(raw, dict):
                continue
            evidence_id = raw.get("evidence_id") or raw.get("evidenceId")
            if not evidence_id:
                continue
            artifact_id = raw.get("artifact_id") or raw.get("artifactId")
            if artifact_id:
                source_artifact_ids.append(str(artifact_id))
            supported_fact_ids = raw.get("supports_fact_refs") or raw.get("supportsFactRefs") or []
            representative = next(
                (fact_by_id[str(fact_id)] for fact_id in supported_fact_ids if str(fact_id) in fact_by_id),
                None,
            )
            if representative is None:
                representative = {}
            representative_value = representative.get("value")
            representative_source = representative.get("source")
            if not isinstance(representative_source, dict):
                representative_source = {}
            supported_result_refs = raw.get("supports_result_item_refs") or raw.get("supportsResultItemRefs") or []
            display_value = (
                str(representative_value)
                if representative_value is not None
                else str(raw.get("evidence_type") or raw.get("evidenceType") or evidence_id)
            )
            source_artifact = artifact_by_id.get(str(artifact_id)) if artifact_id else None
            evidence_items.append({
                "schemaVersion": "1.0",
                "evidenceItemId": str(evidence_id),
                "semanticRole": representative.get("predicate") or raw.get("evidence_type") or raw.get("evidenceType") or "evidence",
                "evidenceKind": "PROVENANCE",
                "subjectId": representative.get("subject_ref") or (supported_result_refs[0] if supported_result_refs else str(evidence_id)),
                "displayValue": display_value,
                "unit": representative.get("unit"),
                "sourceArtifactId": str(artifact_id) if artifact_id else None,
                "sourceArtifactChecksum": (source_artifact or {}).get("sha256") or (source_artifact or {}).get("content_hash") or "",
                "artifactContract": (source_artifact or {}).get("type") or "scientific-result-evidence",
                "artifactContractVersion": "1.0",
                "sourceToolId": (
                    raw.get("tool_call_id")
                    or raw.get("toolCallId")
                    or representative_source.get("tool_call_id")
                    or representative_source.get("toolCallId")
                    or representative_source.get("tool_id")
                    or representative_source.get("toolId")
                    or (source_artifact or {}).get("tool_call_id")
                    or (source_artifact or {}).get("toolCallId")
                ),
                "sourceToolVersion": "1.0",
                "fieldLocator": {"fieldId": raw.get("artifact_locator") or raw.get("artifactLocator") or str(evidence_id)},
                "warnings": [],
                "limitations": [],
            })

        provenance = bundle.get("provenance") if isinstance(bundle.get("provenance"), dict) else {}
        return {
            "interpretationId": str(interpretation["id"]),
            "bundleId": f"agent2-result-{snapshot['id']}",
            "bundleHash": str(snapshot.get("source_fingerprint") or ""),
            "jobId": job_id,
            "projectId": str(interpretation.get("project_id") or snapshot.get("project_id") or ""),
            "planId": str(provenance.get("analysis_plan_id") or ""),
            "evidenceItems": evidence_items,
            "sourceArtifactIds": list(dict.fromkeys(source_artifact_ids)),
            "sourceObjectRefs": source_refs,
            "artifacts": artifact_descriptors,
            "toolCalls": tool_descriptors,
            "bundleWarnings": bundle.get("warnings") or [],
            "bundleLimitations": bundle.get("limitations") or [],
        }

    if hasattr(repos.interpretations, "_with_connection"):
        return repos.interpretations._with_connection(read)
    return None


def get_planner_interpretation_evidence(interpretation_id: str, *, repositories: Any = None) -> dict[str, Any]:
    repos = _planner_read_repositories(repositories)
    agent2_evidence = _get_agent2_interpretation_evidence(interpretation_id, repos)
    if agent2_evidence is not None:
        return agent2_evidence
    record = repos.interpretations.get_interpretation(interpretation_id)
    bundle = repos.interpretations.get_bundle(record["bundleId"])
    job_id = str(bundle.get("jobId") or "")
    source_object_refs: list[dict[str, Any]] = []
    # Evidence bundles intentionally keep their own immutable identity and do
    # not duplicate the ScientificResult source authority. Resolve the exact
    # source refs from the persisted Result snapshot for this Job when the
    # durable repository is available. In-memory compatibility repositories do
    # not have a Result table, so they safely return an empty list.
    bind = getattr(repos.interpretations, "bind", None)
    if bind is not None and job_id:
        statement = (
            select(scientific_result_snapshots.c.bundle_json)
            .where(scientific_result_snapshots.c.job_id == job_id)
            .order_by(scientific_result_snapshots.c.created_at.desc(), scientific_result_snapshots.c.id.desc())
            .limit(1)
        )
        try:
            def read_source_refs(connection: Any) -> list[dict[str, Any]]:
                row = connection.execute(statement).mappings().first()
                payload = row.get("bundle_json") if row else None
                refs = payload.get("source_object_refs") if isinstance(payload, dict) else None
                normalized: list[dict[str, Any]] = []
                if isinstance(refs, list):
                    for item in refs[:16]:
                        if not isinstance(item, dict):
                            continue
                        object_id = item.get("objectId") or item.get("object_id")
                        version_id = item.get("versionId") or item.get("version_id")
                        if not object_id or not version_id:
                            continue
                        normalized.append({
                            "objectId": str(object_id),
                            "versionId": str(version_id),
                            "objectType": item.get("objectType") or item.get("object_type"),
                            "displayName": item.get("displayName") or item.get("display_name"),
                        })
                return normalized

            source_object_refs = list(repos.interpretations._with_connection(read_source_refs))
        except Exception:
            # A legacy interpretation may predate a persisted Result snapshot.
            # Do not make evidence unreadable; the secured Job boundary still
            # protects the response and the bundle remains available.
            source_object_refs = []
    artifacts = []
    tool_calls = []
    if job_id:
        try:
            artifacts = repos.artifacts.list_for_job(job_id)[:64]
        except Exception:
            artifacts = []
        try:
            tool_calls = repos.tool_calls.list_for_job(job_id)[:64]
        except Exception:
            tool_calls = []
    return {
        "interpretationId": interpretation_id,
        "bundleId": bundle["bundleId"],
        "bundleHash": bundle["bundleHash"],
        "jobId": job_id,
        "projectId": str(bundle.get("projectId") or bundle.get("project_id") or "") or None,
        "planId": bundle["planId"],
        "evidenceItems": bundle["evidenceItems"],
        "sourceArtifactIds": bundle["sourceArtifactIds"],
        "sourceObjectRefs": source_object_refs,
        "artifacts": artifacts,
        "toolCalls": tool_calls,
        "bundleWarnings": bundle["bundleWarnings"],
        "bundleLimitations": bundle["bundleLimitations"],
    }


def _interpretation_response(
    *,
    outcome: str,
    bundle: dict[str, Any] | None,
    interpretation: dict[str, Any] | None,
    execution: dict[str, Any] | None,
    diagnostics: list[str],
) -> dict[str, Any]:
    return {
        "outcome": outcome,
        "interpretationId": interpretation.get("interpretationId") if interpretation else None,
        "bundleId": bundle.get("bundleId") if bundle else None,
        "bundleHash": bundle.get("bundleHash") if bundle else None,
        "sourceJobId": bundle.get("jobId") if bundle else None,
        "sourcePlanId": bundle.get("planId") if bundle else None,
        "sourcePlanHash": bundle.get("planHash") if bundle else None,
        "sourceGraphHash": bundle.get("graphHash") if bundle else None,
        "mode": interpretation.get("mode") if interpretation else (execution.get("mode") if execution else None),
        "claims": interpretation.get("claims", []) if interpretation else [],
        "warnings": interpretation.get("globalWarnings", []) if interpretation else (bundle.get("bundleWarnings", []) if bundle else []),
        "limitations": interpretation.get("globalLimitations", []) if interpretation else (bundle.get("bundleLimitations", []) if bundle else []),
        "recommendations": interpretation.get("recommendations", []) if interpretation else [],
        "partialResultState": interpretation.get("partialResultState", False) if interpretation else (bundle.get("partialResults", False) if bundle else False),
        "repairCount": interpretation.get("repairCount", 0) if interpretation else (execution.get("repairCount", 0) if execution else 0),
        "diagnostics": diagnostics[:128],
        "evidenceItemCount": len(bundle.get("evidenceItems", [])) if bundle else 0,
        "noExecution": {
            "toolCallCreated": False,
            "planCreated": False,
            "jobCreated": False,
            "enqueued": False,
            "recommendationExecutionAuthorized": False,
        },
        "execution": execution,
        "interpretation": interpretation,
    }


def _interpretation_source(repos: Any, job: dict[str, Any], plan_record: dict[str, Any]) -> InterpretationSource:
    plan = plan_record.get("analysisPlan") or {}
    status = str(job.get("status") or "")
    if status not in {"completed", "failed", "partial_success"}:
        raise InterpretationError("SOURCE_NOT_TERMINAL", "Interpretation requires a terminal job.")
    job_id = str(job.get("jobId") or job.get("id"))
    plan_id = str(plan_record.get("planId") or plan_record.get("id") or job.get("planId") or "")
    schema_version = str(plan.get("schemaVersion") or "0.1")
    dependency = repos.dependency_execution.get_execution_for_job(job_id) if schema_version == "0.2" else None
    if schema_version == "0.2":
        if dependency is None:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "AnalysisPlan 0.2 requires an exact dependency execution record.")
        try:
            dependency = DependencyExecutionRecord.model_validate(
                dependency.get("dependencyExecutionRecord") or dependency
            ).model_dump(mode="json")
        except Exception as exc:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Dependency execution identity is invalid.") from exc
        exact_plan_hash = str(_plan_hash(plan_record) or "")
        if (
            dependency.get("jobId") != job_id
            or dependency.get("planId") != plan_id
            or dependency.get("planHash") != exact_plan_hash
            or dependency.get("graphHash") != plan.get("graphHash")
        ):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Dependency execution does not match the exact job, plan, or graph.")
    tool_calls = repos.tool_calls.list_for_job(job_id)
    completed_tool_calls = sum(str(item.get("status") or "") == "completed" for item in tool_calls)
    failed_tool_calls = sum(str(item.get("status") or "") == "failed" for item in tool_calls)
    if dependency is not None:
        execution_outcome = str(dependency.get("outcome"))
    elif status == "completed" and failed_tool_calls == 0:
        execution_outcome = "ALL_SUCCEEDED"
    elif completed_tool_calls > 0:
        execution_outcome = "PARTIAL_RESULTS"
    else:
        execution_outcome = "ALL_FAILED"
    intent_execution = repos.analysis_intents.get_execution_for_job(job_id)
    capability_execution = repos.capability_planning.get_execution_for_job(job_id)
    intent = None
    resolution = None
    decision = None
    if intent_execution:
        try:
            intent = repos.analysis_intents.get_intent(str(intent_execution.get("intentId")))
        except (LookupError, ValueError):
            intent = None
    if capability_execution:
        try:
            decision = repos.capability_planning.get_decision(str(capability_execution.get("decisionId")))
            decision_payload = decision.get("capabilityDecision") or decision
            resolution = repos.capability_planning.get_resolution(str(decision_payload.get("resolutionId")))
        except (LookupError, ValueError):
            decision = None
            resolution = None
    profile_id = str(plan_record.get("profileId") or plan.get("profileId") or "") or None
    profile = None
    if profile_id:
        try:
            profile = repos.data_profiles.get(profile_id)
        except LookupError:
            profile = None
    profile_payload = profile or {}
    if schema_version == "0.2" and (
        profile_payload.get("datasetId") != str(job.get("datasetId") or plan_record.get("datasetId") or plan.get("datasetId") or "")
        or not is_supported_data_profile_contract_version(profile_payload.get("profileContractVersion"))
        or not profile_payload.get("semanticHash")
    ):
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "AnalysisPlan 0.2 interpretation requires the exact DataProfile 2.x identity.")
    intent_payload = (intent or {}).get("analysisIntent") or intent or {}
    decision_payload = (decision or {}).get("capabilityDecision") or decision or {}
    resolution_payload = (resolution or {}).get("eligibilityResolution") or resolution or {}
    if schema_version == "0.2":
        try:
            parsed_intent = AnalysisIntent.model_validate(intent_payload)
            parsed_decision = CapabilityPlanningDecision.model_validate(decision_payload)
            parsed_resolution = EligibilityResolution.model_validate(resolution_payload)
            parsed_profile = DataProfile.model_validate(profile_payload)
        except Exception as exc:
            raise InterpretationError(
                "SOURCE_INTEGRITY_FAILED",
                "AnalysisPlan 0.2 interpretation requires persisted, valid Intent and capability-planning records.",
            ) from exc
        if (
            intent_execution is None
            or capability_execution is None
            or intent_execution.get("planId") != plan_id
            or intent_execution.get("jobId") != job_id
            or capability_execution.get("planId") != plan_id
            or capability_execution.get("jobId") != job_id
            or intent_execution.get("intentId") != parsed_intent.intentId
            or capability_execution.get("intentId") != parsed_intent.intentId
            or capability_execution.get("decisionId") != parsed_decision.decisionId
        ):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Intent and capability execution associations are stale or mismatched.")
        if (
            parsed_intent.outcome is not AnalysisIntentOutcome.ready
            or compute_analysis_intent_hash(parsed_intent) != parsed_intent.intentHash
            or deterministic_intent_id(parsed_intent.intentHash) != parsed_intent.intentId
            or parsed_intent.datasetId != parsed_profile.datasetId
            or parsed_intent.profileId != parsed_profile.profileId
        ):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "AnalysisIntent identity or DataProfile binding is invalid.")
        if (
            capability_semantic_hash(parsed_resolution, identity_fields=("resolutionId", "resolutionHash"))
            != parsed_resolution.resolutionHash
            or deterministic_capability_id("resolution", parsed_resolution.resolutionHash) != parsed_resolution.resolutionId
            or capability_semantic_hash(parsed_decision, identity_fields=("decisionId", "decisionHash"))
            != parsed_decision.decisionHash
            or deterministic_capability_id("decision", parsed_decision.decisionHash) != parsed_decision.decisionId
        ):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Capability resolution or decision semantic identity is invalid.")
        dataset_version = str((parsed_profile.sampleIdentity or {}).datasetVersion if parsed_profile.sampleIdentity else parsed_profile.version)
        if (
            parsed_resolution.intentId != parsed_intent.intentId
            or parsed_resolution.intentHash != parsed_intent.intentHash
            or parsed_resolution.profileId != parsed_profile.profileId
            or parsed_resolution.profileSemanticHash != parsed_profile.semanticHash
            or parsed_resolution.profileContractVersion != parsed_profile.profileContractVersion
            or parsed_resolution.datasetId != parsed_profile.datasetId
            or parsed_resolution.datasetVersion != dataset_version
            or parsed_decision.outcome is not CapabilityPlanningOutcome.plan_ready
            or parsed_decision.intentId != parsed_intent.intentId
            or parsed_decision.intentHash != parsed_intent.intentHash
            or parsed_decision.profileId != parsed_profile.profileId
            or parsed_decision.profileSemanticHash != parsed_profile.semanticHash
            or parsed_decision.resolutionId != parsed_resolution.resolutionId
            or parsed_decision.resolutionHash != parsed_resolution.resolutionHash
            or parsed_decision.registrySnapshotId != parsed_resolution.registrySnapshotId
            or parsed_decision.registrySnapshotHash != parsed_resolution.registrySnapshotHash
        ):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Capability planning provenance does not match the exact source scope.")
    return InterpretationSource(
        project_id=str(job.get("projectId") or plan_record.get("projectId") or ""),
        dataset_id=str(job.get("datasetId") or plan_record.get("datasetId") or plan.get("datasetId") or ""),
        dataset_version=str(
            ((profile_payload.get("sampleIdentity") or {}).get("datasetVersion"))
            or profile_payload.get("version")
            or profile_payload.get("profileVersion")
            or f"legacy-plan:{plan_id}"
        ),
        profile_id=profile_id,
        profile_semantic_hash=profile_payload.get("semanticHash"),
        intent_id=intent_payload.get("intentId"),
        intent_hash=intent_payload.get("intentHash"),
        resolution_id=resolution_payload.get("resolutionId"),
        resolution_hash=resolution_payload.get("resolutionHash"),
        decision_id=decision_payload.get("decisionId"),
        decision_hash=decision_payload.get("decisionHash"),
        plan_id=plan_id,
        plan_hash=str(_plan_hash(plan_record) or ""),
        plan_schema_version=schema_version,
        graph_hash=plan.get("graphHash"),
        job_id=job_id,
        job_status=status,
        execution_outcome=execution_outcome,
        failed_step_count=int((dependency or {}).get("failedCount") or failed_tool_calls or (1 if status == "failed" else 0)),
        blocked_step_count=int((dependency or {}).get("blockedCount") or 0),
    )


def _interpretation_artifact_candidates(
    repos: Any,
    runtime: QueueWorkerRuntime,
    source: InterpretationSource,
) -> tuple[list[ArtifactProjectionInput], int]:
    tool_calls = {str(item.get("id")): item for item in repos.tool_calls.list_for_job(source.job_id)}
    lineage = {str(item.get("artifactId")): item for item in repos.dependency_execution.list_lineage_for_job(source.job_id)}
    job_artifacts = sorted(
        repos.artifacts.list_for_job(source.job_id),
        key=lambda item: str(item.get("artifactId") or item.get("id")),
    )
    calls_with_projectable_evidence = {
        tool_call_id
        for artifact in job_artifacts
        if (tool_call_id := str(artifact.get("toolCallId") or ""))
        and (tool_call := tool_calls.get(tool_call_id))
        and tool_call.get("status") == "completed"
        and (
            str(tool_call.get("toolId") or tool_call.get("tool_id") or ""),
            str(artifact.get("type") or ""),
        )
        in ARTIFACT_PROJECTOR_CONTRACTS
    }
    candidates: list[ArtifactProjectionInput] = []
    unsupported_artifact_count = 0
    for artifact in job_artifacts:
        tool_call_id = str(artifact.get("toolCallId") or "")
        tool_call = tool_calls.get(tool_call_id)
        if not tool_call or tool_call.get("status") != "completed":
            unsupported_artifact_count += 1
            continue
        tool_id = str(tool_call.get("toolId") or tool_call.get("tool_id") or "")
        artifact_type = str(artifact.get("type") or "")
        if (
            artifact_type in _INTERPRETATION_PRESENTATION_COMPANION_TYPES
            and tool_call_id in calls_with_projectable_evidence
        ):
            continue
        if artifact_type not in _INTERPRETATION_PROJECTABLE_ARTIFACT_TYPES:
            unsupported_artifact_count += 1
            continue
        if (tool_id, artifact_type) not in ARTIFACT_PROJECTOR_CONTRACTS:
            unsupported_artifact_count += 1
            continue
        size = int(artifact.get("sizeBytes") or 0)
        if size <= 0:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Structured interpretation artifact size is invalid.")
        if size > 262_144:
            unsupported_artifact_count += 1
            continue
        if str(artifact.get("contentType") or "").split(";", 1)[0].strip().lower() != "application/json":
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Structured interpretation artifacts require application/json media type.")
        storage_key = str(artifact.get("storageKey") or "")
        try:
            raw = runtime.artifact_storage.get_bytes_bounded(storage_key, max_bytes=262_144)
        except (OSError, ValueError) as exc:
            raise InterpretationError(
                "SOURCE_INTEGRITY_FAILED",
                "Structured artifact bytes could not be read within the interpretation limit.",
            ) from exc
        checksum = hashlib.sha256(raw).hexdigest()
        if len(raw) != size or checksum != str(artifact.get("sha256") or artifact.get("contentHash") or ""):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Artifact bytes failed size or checksum validation.")
        try:
            payload = json.loads(
                raw.decode("utf-8"),
                object_pairs_hook=_reject_duplicate_json_pairs,
                parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"non-finite JSON: {value}")),
            )
        except (UnicodeDecodeError, ValueError, TypeError) as exc:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Structured artifact JSON is invalid.") from exc
        try:
            validate_interpretation_json_bounds(payload, max_bytes=262_144)
        except (ValueError, RecursionError) as exc:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Structured artifact JSON exceeds depth or byte limits.") from exc
        if not isinstance(payload, dict):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Structured interpretation artifact must be one JSON object.")
        candidates.append(ArtifactProjectionInput(
            artifact=artifact,
            payload=payload,
            tool_call=tool_call,
            lineage=lineage.get(str(artifact.get("artifactId") or artifact.get("id"))),
            raw_checksum=checksum,
            raw_size_bytes=len(raw),
        ))
    if len(candidates) > 16 or unsupported_artifact_count > 128:
        raise InterpretationError(
            "EVIDENCE_CAP_EXCEEDED",
            "Interpretation exceeds the 16 projected-source or 128 unsupported-artifact audit cap.",
        )
    return candidates, unsupported_artifact_count


def _reject_duplicate_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _select_interpretation_provider(request: PlannerInterpretationRequest, *, provider: Any = None) -> Any:
    selected = provider or _select_planner_provider(request.provider or "deepseek")
    if not isinstance(selected, (DeepSeekProvider, OpenAICompatibleProvider)) and not hasattr(selected, "complete_json"):
        raise LLMProviderError("Strict interpretation requires the bounded DeepSeek JSON transport.", code="LLM_PROVIDER_UNSUPPORTED")
    return selected


def _dependency_execution_summary(execution: dict[str, Any] | None) -> dict[str, Any] | None:
    if execution is None:
        return None
    return {
        "executionId": execution.get("executionId"),
        "outcome": execution.get("outcome"),
        "graphHash": execution.get("graphHash"),
        "succeededCount": execution.get("succeededCount"),
        "failedCount": execution.get("failedCount"),
        "blockedCount": execution.get("blockedCount"),
        "notStartedCount": execution.get("notStartedCount"),
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
    download: bool = False,
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
        if size <= 0:
            raise ValueError("Artifact content exceeds the browser transfer cap.")
        storage_key = str(artifact.get("storageKey") or artifact.get("storage_key") or "")
        if not storage_key:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=410,
                detail={
                    "code": "ARTIFACT_CONTENT_GONE",
                    "message": (
                        "Artifact metadata is retained, but the exact persisted "
                        "payload is no longer available."
                    ),
                },
            )
        if size > maximum:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=413,
                detail={
                    "code": "ARTIFACT_CONTENT_TOO_LARGE",
                    "message": (
                        "The exact Artifact exceeds the bounded browser transfer "
                        "limit."
                    ),
                    "maximumBytes": maximum,
                    "sizeBytes": size,
                },
            )
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
        headers = {
            "X-Content-SHA256": expected_hash,
            "X-Content-Length-Validated": str(size),
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        }
        if download:
            raw_name = str(artifact.get("name") or f"{artifact_id}.artifact")
            safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", raw_name).lstrip(".")[:120]
            if not safe_name:
                safe_name = f"{artifact_id}.artifact"
            headers["Content-Disposition"] = f'attachment; filename="{safe_name}"'
        return Response(
            content=content,
            media_type=media_type,
            headers=headers,
        )

    try:
        return make_response()
    except FileNotFoundError as error:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail={
                "code": "ARTIFACT_CONTENT_NOT_FOUND",
                "message": "The exact Artifact payload is currently unavailable.",
            },
        ) from error
    except ClientError as error:
        from fastapi import HTTPException

        error_code = str((error.response or {}).get("Error", {}).get("Code", ""))
        if error_code in {"NoSuchKey", "NoSuchBucket", "NotFound", "404"}:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "ARTIFACT_CONTENT_NOT_FOUND",
                    "message": "The exact Artifact payload is currently unavailable.",
                },
            ) from error
        raise HTTPException(
            status_code=503,
            detail={
                "code": "ARTIFACT_STORAGE_UNAVAILABLE",
                "message": "Artifact storage is temporarily unavailable.",
            },
        ) from error
    except BotoCoreError as error:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail={
                "code": "ARTIFACT_STORAGE_UNAVAILABLE",
                "message": "Artifact storage is temporarily unavailable.",
            },
        ) from error
    except LookupError as error:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Planner artifact content was not found.") from error
    except ValueError as error:
        from fastapi import HTTPException

        raise HTTPException(status_code=422, detail="Planner artifact content failed bounded validation.") from error


def get_planner_job_artifact_content_route(
    job_id: str,
    artifact_id: str,
    download: bool = False,
) -> Any:
    """HTTP boundary for bounded job-scoped artifact bytes."""

    return get_planner_job_artifact_content(job_id, artifact_id, download=download)


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
    # The repository layer is also used with SQLite in the supported local
    # durable-runtime adapter; selecting it must follow runtime_backend, not
    # only the database URL scheme.
    # An explicit DATABASE_URL opts local development into the same durable
    # repository path as PostgreSQL. The default no-env test runtime remains
    # in-memory so isolated unit tests do not need a database schema.
    explicit_database_url = bool(os.getenv("DATABASE_URL") or os.getenv("MDI_DATABASE_URL"))
    use_durable_repository = (
        "postgres" in settings.database_url
        or settings.runtime_backend == "postgresql"
        or explicit_database_url
        # The local production API also owns a durable SQLite database. Keep
        # only pytest's isolated route tests on the in-memory bundle.
        or not os.getenv("PYTEST_CURRENT_TEST")
    )
    if use_durable_repository:
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
        from mdi_api.infrastructure.phase2.runtime import get_phase2_dataset_profile_model

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
            from mdi_api.infrastructure.phase2.runtime import get_phase2_dataset_profile_model

            profile = get_phase2_dataset_profile_model(dataset_id)
        except Exception as exc:
            raise AnalysisIntentError(
                "The exact supported DataProfile record is unavailable.",
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
    if not is_supported_data_profile_contract_version(profile.profileContractVersion) or not profile.semanticHash:
        raise AnalysisIntentError(
            "AnalysisIntent requires an exact supported DataProfile semantic identity.",
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
    provider_name = _requested_planner_provider_name(requested_provider)
    if provider is not None and requested_provider is None and not os.getenv("MDI_LLM_PROVIDER"):
        provider_name = "deepseek" if isinstance(provider, DeepSeekProvider) else "mock"
    if provider_name == "deepseek":
        llm = provider or DeepSeekProvider()
        return OpenAICompatibleAnalysisIntentBuilder(llm).build(intent_request, profile=profile, user_config=user_config)
    if provider_name in {"", "mock", "mock_llm", "deterministic", "safe_mock"}:
        if provider is None and not _test_providers_allowed():
            raise LLMProviderError(
                "Test and deterministic providers require the explicit offline test gate.",
                code="PROVIDER_NOT_ALLOWED",
            )
        return DeterministicAnalysisIntentBuilder().build(intent_request, profile=profile)
    raise LLMProviderError(
        "New real LLM calls are restricted to DeepSeek.",
        code="PROVIDER_NOT_ALLOWED",
    )


def _persist_planner_intent(repos: Any, project_id: str, intent: AnalysisIntent, *, created_by: str) -> dict[str, Any]:
    return repos.analysis_intents.save_intent(
        {
            "projectId": project_id,
            "analysisIntent": intent.model_dump(mode="json"),
            "createdBy": created_by,
        }
    )


def _persist_capability_planning(
    repos: Any,
    result: CapabilityPlanningResult,
    *,
    created_by: str,
) -> None:
    repos.capability_planning.save_resolution(
        {
            "eligibilityResolution": result.resolution.model_dump(mode="json"),
            "createdBy": created_by,
        }
    )
    repos.capability_planning.save_decision(
        {
            "capabilityDecision": result.decision.model_dump(mode="json"),
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


def _planner_jobs_capability_error(
    error: CapabilityPlanningError,
    *,
    intent: AnalysisIntent,
    planner_provider: str,
) -> PlannerJobsResult:
    return PlannerJobsResult(
        ok=False,
        job_id=None,
        plan_id=None,
        plan_hash=None,
        validation_errors=[{"code": error.code, "message": str(error), "detail": None}],
        plan=None,
        plan_source="capability_planner",
        planner_provider=planner_provider,
        intent_id=intent.intentId,
        intent_outcome=intent.outcome.value,
        intent=intent.model_dump(mode="json"),
        error_code=error.code,
        capability_outcome=error.outcome.value,
    )


def _phase2_object_store_for_dataset(dataset_id: str) -> dict[str, Any] | None:
    try:
        from mdi_api.infrastructure.phase2.runtime import get_phase2_dataset_object_store

        return get_phase2_dataset_object_store(dataset_id)
    except Exception:
        return None


def _execution_object_store_for_dataset(
    runtime: QueueWorkerRuntime,
    *,
    dataset_id: str,
    profile_id: str,
) -> Mapping[str, Any] | None:
    resolver = runtime.object_store_resolver
    exact_resolver = getattr(resolver, "resolve", None)
    if callable(exact_resolver):
        return exact_resolver(dataset_id, profile_id=profile_id)
    elif callable(resolver):
        resolved = resolver(dataset_id)
        if resolved:
            return resolved
    return _phase2_object_store_for_dataset(dataset_id)


def _requires_durable_root_inputs(runtime: QueueWorkerRuntime) -> bool:
    return isinstance(runtime.object_store_resolver, DurableObjectStoreResolver)


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
    """Transport facade over the canonical application provider-selection boundary."""

    return select_llm_provider(requested_provider, provider=provider)


def _requested_planner_provider_name(requested_provider: str | None) -> str:
    return requested_provider_name(requested_provider)


def _test_providers_allowed() -> bool:
    return test_providers_allowed()


def _planner_user_config_from_request(request: Any, *, selected_provider: Any = None) -> PlannerUserConfig | None:
    fields = ("baseUrl", "model", "secretId", "temperature", "maxTokens", "timeoutSeconds", "thinkingMode")
    provider_name = _requested_planner_provider_name(getattr(request, "provider", None))
    has_explicit_config = any(getattr(request, field, None) not in (None, "") for field in fields)
    connection = get_connection(provider_name)
    if connection is not None:
        requested_model = getattr(request, "model", None) or connection.default_model
        if requested_model and connection.model_ids and requested_model not in connection.model_ids:
            raise LLMProviderError("所选模型不在该 Provider 的模型目录中。", code="PROVIDER_MODEL_NOT_ALLOWED")
        return PlannerUserConfig(
            provider=connection.provider,
            model=requested_model or "",
            base_url=connection.base_url,
            api_key=decrypt_api_key(connection),
            timeout_seconds=float(getattr(request, "timeoutSeconds", None) or 120.0),
            temperature=0.0,
            max_tokens=thinking_budget(getattr(request, "thinkingMode", "standard"), int(getattr(request, "maxTokens", None) or 8192)),
            thinking_mode=getattr(request, "thinkingMode", "standard"),
        )
    if selected_provider is not None and not isinstance(selected_provider, DeepSeekProvider):
        return None
    if provider_name != "deepseek":
        return None
    if getattr(request, "baseUrl", None) or getattr(request, "secretId", None):
        raise LLMProviderError(
            "DeepSeek endpoint and credentials are server-owned and cannot be supplied per request.",
            code="DEEPSEEK_CONFIGURATION_NOT_ALLOWED",
        )
    temperature = getattr(request, "temperature", None)
    if temperature not in (None, 0, 0.0):
        raise LLMProviderError(
            "DeepSeek temperature is fixed at zero.",
            code="DEEPSEEK_CONFIGURATION_NOT_ALLOWED",
        )
    if not has_explicit_config:
        return None

    return PlannerUserConfig(
        provider="deepseek",
        model=getattr(request, "model", None) or os.getenv("DEEPSEEK_MODEL") or DEEPSEEK_DEFAULT_MODEL,
        timeout_seconds=float(getattr(request, "timeoutSeconds", None) or 120.0),
        temperature=0.0,
        max_tokens=thinking_budget(getattr(request, "thinkingMode", "standard"), int(getattr(request, "maxTokens", None) or 8192)),
        thinking_mode=getattr(request, "thinkingMode", "standard"),
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
