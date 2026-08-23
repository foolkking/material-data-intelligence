from __future__ import annotations

from datetime import datetime
from enum import Enum
import re
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from mdi_api.scientific_objects.schemas import ScientificObjectRef


class ResearchAction(str, Enum):
    ANSWER = "ANSWER"
    CLARIFY = "CLARIFY"
    ANALYZE = "ANALYZE"
    CONTINUE_ANALYSIS = "CONTINUE_ANALYSIS"
    INTERPRET_RESULT = "INTERPRET_RESULT"
    QUERY_DATA = "QUERY_DATA"
    MANAGE_DATA = "MANAGE_DATA"
    OPEN_OBJECT = "OPEN_OBJECT"
    CREATE_REPORT = "CREATE_REPORT"
    UPDATE_REPORT = "UPDATE_REPORT"
    EXPORT = "EXPORT"


class ResearchTurnStatus(str, Enum):
    RECEIVED = "RECEIVED"
    RESOLVING_CONTEXT = "RESOLVING_CONTEXT"
    ORCHESTRATING = "ORCHESTRATING"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    ANSWERED = "ANSWERED"
    UNSUPPORTED = "UNSUPPORTED"
    READY_TO_PLAN = "READY_TO_PLAN"
    PLANNING = "PLANNING"
    PLAN_READY = "PLAN_READY"
    PLAN_REJECTED = "PLAN_REJECTED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    CANCELING = "CANCELING"
    RESULT_PENDING = "RESULT_PENDING"
    RESULT_READY = "RESULT_READY"
    INTERPRETING = "INTERPRETING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


TERMINAL_TURN_STATUSES = frozenset({
    ResearchTurnStatus.NEEDS_CLARIFICATION,
    ResearchTurnStatus.ANSWERED,
    ResearchTurnStatus.UNSUPPORTED,
    ResearchTurnStatus.PLAN_REJECTED,
    ResearchTurnStatus.COMPLETED,
    ResearchTurnStatus.PARTIAL,
    ResearchTurnStatus.FAILED,
    ResearchTurnStatus.CANCELED,
})


class ResearchTurnEventType(str, Enum):
    TURN_RECEIVED = "TURN_RECEIVED"
    CONTEXT_RESOLUTION_STARTED = "CONTEXT_RESOLUTION_STARTED"
    CONTEXT_RESOLVED = "CONTEXT_RESOLVED"
    CONTEXT_AMBIGUOUS = "CONTEXT_AMBIGUOUS"
    ORCHESTRATION_STARTED = "ORCHESTRATION_STARTED"
    ORCHESTRATION_COMPLETED = "ORCHESTRATION_COMPLETED"
    CLARIFICATION_REQUESTED = "CLARIFICATION_REQUESTED"
    DIRECT_ANSWER_READY = "DIRECT_ANSWER_READY"
    PLAN_REQUESTED = "PLAN_REQUESTED"
    CAPABILITY_RESOLUTION_STARTED = "CAPABILITY_RESOLUTION_STARTED"
    CAPABILITY_RESOLUTION_COMPLETED = "CAPABILITY_RESOLUTION_COMPLETED"
    CAPABILITY_UNSUPPORTED = "CAPABILITY_UNSUPPORTED"
    CAPABILITY_PLANNING_STARTED = "CAPABILITY_PLANNING_STARTED"
    CAPABILITY_PLAN_CREATED = "CAPABILITY_PLAN_CREATED"
    CAPABILITY_PLAN_REJECTED = "CAPABILITY_PLAN_REJECTED"
    ANALYSIS_PLAN_BOUND = "ANALYSIS_PLAN_BOUND"
    PLAN_READY = "PLAN_READY"
    EXECUTION_DISPATCH_STARTED = "EXECUTION_DISPATCH_STARTED"
    JOB_QUEUE_PUBLISHED = "JOB_QUEUE_PUBLISHED"
    EXECUTION_STEP_STARTED = "EXECUTION_STEP_STARTED"
    EXECUTION_STEP_COMPLETED = "EXECUTION_STEP_COMPLETED"
    EXECUTION_STEP_FAILED = "EXECUTION_STEP_FAILED"
    EXECUTION_STEP_SKIPPED = "EXECUTION_STEP_SKIPPED"
    EXECUTION_OUTPUT_AVAILABLE = "EXECUTION_OUTPUT_AVAILABLE"
    CANCELLATION_REQUESTED = "CANCELLATION_REQUESTED"
    EXECUTION_SUCCEEDED = "EXECUTION_SUCCEEDED"
    EXECUTION_PARTIAL = "EXECUTION_PARTIAL"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    EXECUTION_CANCELED = "EXECUTION_CANCELED"
    RESULT_PENDING = "RESULT_PENDING"
    PLAN_ATTACHED = "PLAN_ATTACHED"
    PLAN_REJECTED = "PLAN_REJECTED"
    JOB_ATTACHED = "JOB_ATTACHED"
    JOB_STARTED = "JOB_STARTED"
    JOB_TERMINAL = "JOB_TERMINAL"
    RESULT_PROJECTED = "RESULT_PROJECTED"
    RESULT_PROJECTION_STARTED = "RESULT_PROJECTION_STARTED"
    RESULT_PROJECTION_FAILED = "RESULT_PROJECTION_FAILED"
    RESULT_READY = "RESULT_READY"
    INTERPRETATION_STARTED = "INTERPRETATION_STARTED"
    INTERPRETATION_READY = "INTERPRETATION_READY"
    TURN_COMPLETED = "TURN_COMPLETED"
    TURN_PARTIAL = "TURN_PARTIAL"
    TURN_FAILED = "TURN_FAILED"
    TURN_CANCELED = "TURN_CANCELED"
    TURN_UNSUPPORTED = "TURN_UNSUPPORTED"


class ContextResolutionStatus(str, Enum):
    EXACT = "EXACT"
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_FOUND = "NOT_FOUND"
    STALE_REFERENCE = "STALE_REFERENCE"
    UNAUTHORIZED = "UNAUTHORIZED"


class ResolvedReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phrase: str = Field(min_length=1, max_length=512)
    candidate_ids: list[str]
    selected_ref: ScientificObjectRef | None
    status: ContextResolutionStatus

    @model_validator(mode="after")
    def validate_reference(self) -> "ResolvedReference":
        if len(self.candidate_ids) != len(set(self.candidate_ids)):
            raise ValueError("candidate_ids must be unique")
        if self.status == ContextResolutionStatus.UNAUTHORIZED and self.selected_ref is not None:
            raise ValueError("unauthorized reference cannot select an object")
        return self


class ResolvedResearchContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str = Field(min_length=1, max_length=64)
    research_session_id: str = Field(min_length=1, max_length=64)
    active_objects: list[ScientificObjectRef]
    selection_refs: list[ScientificObjectRef]
    resolved_references: list[ResolvedReference]
    referenced_result_ids: list[UUID]
    research_goal: str | None
    user_constraints: list[str]
    unresolved_questions: list[str]
    requires_clarification: bool

    @model_validator(mode="after")
    def validate_scope(self) -> "ResolvedResearchContext":
        refs = [*self.active_objects, *self.selection_refs, *(item.selected_ref for item in self.resolved_references if item.selected_ref)]
        if any(ref.project_id != self.project_id for ref in refs):
            raise ValueError("all scientific object refs must belong to project_id")
        if any(item.status == ContextResolutionStatus.AMBIGUOUS for item in self.resolved_references) and not self.requires_clarification:
            raise ValueError("ambiguous references require clarification")
        return self


class RequirementCriticality(str, Enum):
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"


class RequirementOrigin(str, Enum):
    USER_EXPLICIT = "USER_EXPLICIT"
    CONTEXT_RESOLVED = "CONTEXT_RESOLVED"
    AGENT_DERIVED = "AGENT_DERIVED"


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]{2,127}$")


class ScientificRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement_id: str
    criticality: RequirementCriticality
    subject_refs: list[ScientificObjectRef]
    constraints: dict[str, Any] = Field(default_factory=dict)
    origin: RequirementOrigin

    @field_validator("requirement_id")
    @classmethod
    def valid_requirement_id(cls, value: str) -> str:
        if not _IDENTIFIER.fullmatch(value):
            raise ValueError("invalid requirement_id")
        return value


class ScientificRequirementSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str = Field(min_length=1, max_length=2048)
    requirements: list[ScientificRequirement]
    source_turn_id: UUID

    @model_validator(mode="after")
    def validate_requirements(self) -> "ScientificRequirementSet":
        ids = [item.requirement_id for item in self.requirements]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate requirement_id")
        projects = {ref.project_id for item in self.requirements for ref in item.subject_refs}
        if len(projects) > 1:
            raise ValueError("requirement subjects must share one project")
        return self


class CapabilityStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPERIMENTAL = "EXPERIMENTAL"
    DEPRECATED = "DEPRECATED"


class CapabilityInputSlot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=96)
    accepted_object_types: list[str] = Field(min_length=1)
    required: bool = True
    min_count: int = Field(default=1, ge=0)
    max_count: int | None = Field(default=1, ge=1)

    @model_validator(mode="after")
    def valid_count_range(self) -> "CapabilityInputSlot":
        if self.max_count is not None and self.max_count < self.min_count:
            raise ValueError("max_count must be greater than or equal to min_count")
        return self


class CapabilityOutputSlot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=96)
    result_type: str = Field(default="generic.result", min_length=3, max_length=128)
    scientific_object_type: str | None = Field(default=None, min_length=3, max_length=128)
    # `object_type` is retained as a read/construct compatibility alias for
    # Phase 1 manifests; new manifests should use scientific_object_type.
    object_type: str | None = Field(default=None, min_length=3, max_length=128)
    required: bool = True
    cardinality: Literal["ONE", "MANY"] = "ONE"

    @model_validator(mode="after")
    def normalize_object_type(self) -> "CapabilityOutputSlot":
        if self.scientific_object_type is None and self.object_type is not None:
            object.__setattr__(self, "scientific_object_type", self.object_type)
        if self.object_type is None:
            object.__setattr__(self, "object_type", self.scientific_object_type)
        return self


class CapabilityPrecondition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    predicate_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]{2,127}$")
    input_slot: str | None = Field(default=None, min_length=1, max_length=96)
    parameters: dict[str, Any] = Field(default_factory=dict)
    required: bool = True


class ToolBinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_id: str = Field(min_length=3, max_length=128)
    version_constraint: str = Field(min_length=1, max_length=64)
    priority: int = 100
    input_mapping: dict[str, Any] = Field(default_factory=dict)
    parameter_mapping: dict[str, Any] = Field(default_factory=dict)
    output_mapping: dict[str, Any] = Field(default_factory=dict)
    conditions: list[str] = Field(default_factory=list)


class RequirementManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    requirement_id: str
    display_name: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=1024)
    scientific_domain: str = Field(default="generic", min_length=1, max_length=96)
    accepted_object_types: list[str] = Field(default_factory=list)
    constraint_schema: dict[str, Any] = Field(default_factory=lambda: {"type": "object", "additionalProperties": False})
    status: Literal["ACTIVE", "EXPERIMENTAL", "DEPRECATED"] = "ACTIVE"

    @field_validator("requirement_id")
    @classmethod
    def valid_requirement_id(cls, value: str) -> str:
        if not _IDENTIFIER.fullmatch(value):
            raise ValueError("invalid requirement_id")
        return value


class CapabilityManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability_id: str = Field(min_length=3, max_length=128)
    version: str = Field(min_length=1, max_length=32)
    domain: str = Field(min_length=1, max_length=64)
    display_name: str = Field(min_length=1, max_length=160)
    scientific_purpose: str = Field(min_length=1, max_length=1024)
    satisfies_requirements: list[str]
    input_slots: list[CapabilityInputSlot]
    output_slots: list[CapabilityOutputSlot]
    preconditions: list[CapabilityPrecondition]
    limitations: list[str]
    tool_bindings: list[ToolBinding]
    viewer_bindings: list[str]
    evidence_projector: str | None
    result_projector: str = Field(min_length=1, max_length=128)
    report_projector: str | None
    progress_projector: str = Field(min_length=1, max_length=128)
    status: CapabilityStatus
    planning_priority: int = Field(default=100, ge=0, le=10_000)
    manifest_schema_version: Literal["1.1"] = "1.1"


class ResearchTurnUIContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    active_object_refs: list[ScientificObjectRef] = Field(default_factory=list, max_length=64)
    selection_refs: list[ScientificObjectRef] = Field(default_factory=list, max_length=16)
    explicit_object_refs: list[ScientificObjectRef] = Field(default_factory=list, max_length=64)
    explicit_result_ids: list[UUID] = Field(default_factory=list, max_length=16)
    explicit_finding_refs: list[str] = Field(default_factory=list, max_length=16)


class CreateResearchTurnRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=16_000)
    ui_context: ResearchTurnUIContext | None = None
    reply_to_turn_id: UUID | None = None

    @field_validator("message")
    @classmethod
    def non_blank_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message must not be blank")
        return value


class ResearchTurnMessageDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    role: str
    content: str


class CreateResearchTurnResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    turn_id: UUID
    research_session_id: str
    project_id: str
    sequence_no: int = Field(ge=1)
    status: ResearchTurnStatus
    user_message: ResearchTurnMessageDTO
    created_at: datetime


class ResearchTurnEventDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(ge=1)
    type: str
    turn_id: UUID
    timestamp: datetime
    payload: dict[str, Any]
