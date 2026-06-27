"""Planner API routes — POST /planner/preview, /planner/validate, /planner/jobs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field

from mdi_api.phase2_runtime import Phase2ProductRuntime, build_phase2_plan
from mdi_api.secrets import InMemorySecretStore
from mdi_llm import (
    MockLLMProvider,
    PlannerRawResponse,
    PlannerRequest,
    PlannerUserConfig,
    redact_params_for_log,
)
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
    datasetId: str = Field(min_length=1)
    profileId: str = Field(default="")


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
    validation_errors: list[dict[str, Any]]
    plan: dict[str, Any] | None


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
) -> PlannerJobsResult:
    """Generate plan, validate, create job — all in one call.

    If validation fails, no job is created.
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
        return PlannerJobsResult(ok=False, job_id=None, validation_errors=[{"code": "PLAN_EMPTY", "message": "LLM returned no plan.", "detail": None}], plan=None)

    validation = validate_plan(plan, registry=reg)
    if not validation.ok:
        return PlannerJobsResult(
            ok=False,
            job_id=None,
            validation_errors=[{"code": e.code, "message": e.message, "detail": e.detail} for e in validation.errors],
            plan=plan,
        )

    # Plan is valid — create a job (uses the existing Phase 2 runtime path)
    from mdi_api.phase2_runtime import Phase2ProductRuntime, InlineUploadFile

    runtime = Phase2ProductRuntime()
    runtime.create_project({"name": f"project_{request.datasetId}"})
    project_id = list(runtime.projects.keys())[0]
    # Phase 2 runtime requires at least one file in upload; use a minimal inline CSV
    runtime.upload_dataset({
        "projectId": project_id,
        "datasetName": request.datasetId,
        "files": [{"fileName": "data.csv", "content": "formula,y_true,y_pred\nSiO2,2.1,2.0\nAl2O3,3.4,3.5\nCaO,1.8,1.9"}],
    })
    dataset_id = list(runtime.datasets.keys())[0]
    job = runtime.create_job({"projectId": project_id, "datasetId": dataset_id, "userPrompt": request.userPrompt})

    return PlannerJobsResult(ok=True, job_id=job["id"], validation_errors=[], plan=plan)
