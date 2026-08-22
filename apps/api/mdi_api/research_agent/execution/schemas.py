from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from mdi_api.research_agent.schemas import ResearchTurnStatus


class ExecutionOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class ExecutionStepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    CANCELED = "CANCELED"


class ExecutionArtifactRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    step_id: str
    output_slot: str | None = None
    artifact_type: str | None = None
    media_type: str | None = None
    display_label: str = Field(min_length=1, max_length=512)
    preview_available: bool = False
    download_available: bool = True


class ExecutionWarning(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=1000)


class ExecutionStepSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str
    capability_id: str
    capability_version: str
    display_name: str
    status: ExecutionStepStatus
    # The existing runtime uses opaque, replay-stable ToolCall identities.
    tool_call_ids: list[str] = Field(default_factory=list)
    output_artifact_refs: list[ExecutionArtifactRef] = Field(default_factory=list)
    warning_codes: list[str] = Field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ResearchExecutionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: Literal["1.0"]
    research_turn_id: UUID
    # Existing AnalysisPlan and Job repositories use opaque string identities
    # (for example ``agent2_plan_*`` and ``job_*``); the contract preserves
    # those exact runtime identities rather than inventing a second UUID type.
    analysis_plan_id: str
    job_id: str
    outcome: ExecutionOutcome
    steps: list[ExecutionStepSummary]
    successful_step_ids: list[str] = Field(default_factory=list)
    failed_step_ids: list[str] = Field(default_factory=list)
    skipped_step_ids: list[str] = Field(default_factory=list)
    artifact_refs: list[ExecutionArtifactRef] = Field(default_factory=list)
    warnings: list[ExecutionWarning] = Field(default_factory=list)
    started_at: datetime | None = None
    terminal_at: datetime
    source_fingerprint: str = Field(min_length=16, max_length=128)
    projector_version: str = Field(min_length=1, max_length=64)


class ResearchProgressStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str
    display_name: str
    status: ExecutionStepStatus
    running_label: str | None = None
    completed_label: str | None = None
    output_available: bool = False
    warning: str | None = None


class ProgressOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    output_key: str
    step_id: str
    display_label: str
    artifact_id: str
    output_slot: str | None = None
    preview_available: bool = False
    available_at: datetime


class ProgressWarning(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str


class ResearchProgressView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: Literal["1.0"]
    turn_id: UUID
    status: ResearchTurnStatus
    plan_title: str | None = None
    steps: list[ResearchProgressStep] = Field(default_factory=list)
    active_step_ids: list[str] = Field(default_factory=list)
    completed_step_count: int = Field(default=0, ge=0)
    total_step_count: int = Field(default=0, ge=0)
    incremental_outputs: list[ProgressOutput] = Field(default_factory=list)
    warnings: list[ProgressWarning] = Field(default_factory=list)
    execution_outcome: ExecutionOutcome | None = None
    result_projection_pending: bool = False
