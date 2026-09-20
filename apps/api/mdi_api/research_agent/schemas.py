from __future__ import annotations

from datetime import datetime
from enum import Enum
import json
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


class AutonomyMode(str, Enum):
    STANDARD = "STANDARD"
    BOUNDED_AUTONOMOUS = "BOUNDED_AUTONOMOUS"


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
    CONTEXT_MANIFEST_RECORDED = "CONTEXT_MANIFEST_RECORDED"
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
    INTERPRETATION_RETRY_SCHEDULED = "INTERPRETATION_RETRY_SCHEDULED"
    INTERPRETATION_READY = "INTERPRETATION_READY"
    TURN_COMPLETED = "TURN_COMPLETED"
    TURN_PARTIAL = "TURN_PARTIAL"
    TURN_FAILED = "TURN_FAILED"
    TURN_CANCELED = "TURN_CANCELED"
    TURN_UNSUPPORTED = "TURN_UNSUPPORTED"
    AUTONOMY_CYCLE_CREATED = "AUTONOMY_CYCLE_CREATED"
    AUTONOMY_ASSESSMENT_RECORDED = "AUTONOMY_ASSESSMENT_RECORDED"
    AUTONOMY_CHILD_TURN_CREATED = "AUTONOMY_CHILD_TURN_CREATED"
    AUTONOMY_QUEUE_PUBLISHED = "AUTONOMY_QUEUE_PUBLISHED"
    AUTONOMY_QUEUE_PUBLISH_FAILED = "AUTONOMY_QUEUE_PUBLISH_FAILED"
    AUTONOMY_STOPPED = "AUTONOMY_STOPPED"


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


class ScientificSelectionContext(BaseModel):
    """Bounded semantic viewer selection captured as turn evidence."""

    model_config = ConfigDict(extra="forbid")

    contract_version: Literal["1.0"] = "1.0"
    object_ref: ScientificObjectRef
    viewer_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]{2,127}$")
    selection_type: str = Field(pattern=r"^[A-Z][A-Z0-9_]{1,63}$")
    semantic_locator: dict[str, Any] = Field(default_factory=dict, max_length=24)
    display_label: str = Field(min_length=1, max_length=512)
    evidence_locator: dict[str, Any] | None = Field(default=None, max_length=24)

    @field_validator("semantic_locator", "evidence_locator")
    @classmethod
    def validate_locator(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        for key, item in value.items():
            if not re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", key):
                raise ValueError("selection locator keys must be stable semantic identifiers")
            values = item if isinstance(item, list) else [item]
            if isinstance(item, (dict, tuple, set)) or len(values) > 64:
                raise ValueError("selection locator values must be bounded scalars or scalar lists")
            for scalar in values:
                if scalar is not None and not isinstance(scalar, (str, int, float, bool)):
                    raise ValueError("selection locator values must be JSON scalars")
                if isinstance(scalar, str) and len(scalar) > 512:
                    raise ValueError("selection locator strings must be bounded")
        if len(json.dumps(value, sort_keys=True, separators=(",", ":"))) > 8192:
            raise ValueError("selection locator payload is too large")
        return value


class ResolvedResearchContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str = Field(min_length=1, max_length=64)
    research_session_id: str = Field(min_length=1, max_length=64)
    active_objects: list[ScientificObjectRef]
    selection_refs: list[ScientificObjectRef]
    scientific_selections: list[ScientificSelectionContext] = Field(default_factory=list, max_length=16)
    resolved_references: list[ResolvedReference]
    referenced_result_ids: list[UUID]
    research_goal: str | None
    user_constraints: list[str]
    unresolved_questions: list[str]
    requires_clarification: bool

    @model_validator(mode="after")
    def validate_scope(self) -> "ResolvedResearchContext":
        refs = [
            *self.active_objects,
            *self.selection_refs,
            *(item.object_ref for item in self.scientific_selections),
            *(item.selected_ref for item in self.resolved_references if item.selected_ref),
        ]
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


class CapabilitySurfaceSupport(str, Enum):
    """Explicit completeness state for optional capability surfaces."""

    REQUIRED = "REQUIRED"
    SUPPORTED = "SUPPORTED"
    GENERIC = "GENERIC"
    NONE = "NONE"


class CapabilityPlannerVisibility(str, Enum):
    VISIBLE = "VISIBLE"
    HIDDEN = "HIDDEN"


class CapabilityResourceProfile(BaseModel):
    """Planning hint; the Tool Registry remains the execution authority."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    authority: Literal["TOOL_BINDING"] = "TOOL_BINDING"
    resource_class: Literal[
        "DERIVED_FROM_TOOL",
        "CPU",
        "MEMORY",
        "GPU",
        "IO",
        "EXTERNAL",
        "MIXED",
    ] = "DERIVED_FROM_TOOL"
    expected_cost_class: Literal[
        "DERIVED_FROM_TOOL",
        "LOW",
        "MEDIUM",
        "HIGH",
    ] = "DERIVED_FROM_TOOL"


class CapabilityExecutionPolicy(BaseModel):
    """Conservative recovery metadata consumed by lifecycle tooling."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    retryability: Literal["SAFE", "CONDITIONAL", "UNSAFE", "UNKNOWN"] = "CONDITIONAL"
    idempotency: Literal[
        "IDEMPOTENT",
        "IDENTITY_GUARDED",
        "NON_IDEMPOTENT",
        "UNKNOWN",
    ] = "IDENTITY_GUARDED"
    partial_output_policy: Literal[
        "PRESERVE_VALIDATED",
        "DISCARD",
        "NONE",
        "UNKNOWN",
    ] = "PRESERVE_VALIDATED"
    resumability: Literal[
        "RESUMABLE",
        "RESTART_FROM_DURABLE_BOUNDARY",
        "NON_RESUMABLE",
        "UNKNOWN",
    ] = "RESTART_FROM_DURABLE_BOUNDARY"


class CapabilityQualification(BaseModel):
    """Structural/scientific qualification are deliberately distinct."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    level: Literal[
        "STRUCTURAL_ONLY",
        "REFERENCE_VALIDATED",
        "DOMAIN_VALIDATED",
        "CROSS_IMPLEMENTATION_VALIDATED",
        "EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED",
        "NOT_YET_SCIENTIFICALLY_QUALIFIED",
        "SCIENTIFICALLY_QUALIFIED",
        "EXPERIMENTAL",
        "UNKNOWN",
    ] = "STRUCTURAL_ONLY"
    evidence_refs: list[str] = Field(default_factory=list, max_length=32)
    validated_domains: list[str] = Field(default_factory=list, max_length=32)
    known_limitations: list[str] = Field(default_factory=list, max_length=32)
    evidence_version: str | None = Field(default=None, min_length=1, max_length=32)
    evidence_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[0-9a-f]{64}$",
    )
    reference_case_count: int = Field(default=0, ge=0)
    invariant_case_count: int = Field(default=0, ge=0)
    domain_negative_case_count: int = Field(default=0, ge=0)
    result_projection_case_count: int = Field(default=0, ge=0)
    interpretation_evaluation_count: int = Field(default=0, ge=0)
    report_evaluation_count: int = Field(default=0, ge=0)
    reproducibility: Literal[
        "DETERMINISTIC",
        "SEEDED_STOCHASTIC",
        "NONDETERMINISTIC_EXTERNAL",
        "UNKNOWN",
    ] = "UNKNOWN"


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
    result_projector: str | None = Field(default=None, min_length=1, max_length=128)
    interpretation_profile: str | None = Field(default=None, min_length=1, max_length=128)
    report_projector: str | None
    progress_projector: str = Field(min_length=1, max_length=128)
    result_support: CapabilitySurfaceSupport = CapabilitySurfaceSupport.REQUIRED
    artifact_port_support: CapabilitySurfaceSupport = CapabilitySurfaceSupport.GENERIC
    interpretation_support: CapabilitySurfaceSupport = CapabilitySurfaceSupport.GENERIC
    viewer_support: CapabilitySurfaceSupport = CapabilitySurfaceSupport.GENERIC
    report_support: CapabilitySurfaceSupport = CapabilitySurfaceSupport.GENERIC
    planner_visibility: CapabilityPlannerVisibility = CapabilityPlannerVisibility.VISIBLE
    resource_profile: CapabilityResourceProfile = Field(default_factory=CapabilityResourceProfile)
    execution_policy: CapabilityExecutionPolicy = Field(default_factory=CapabilityExecutionPolicy)
    qualification: CapabilityQualification = Field(default_factory=CapabilityQualification)
    status: CapabilityStatus
    planning_priority: int = Field(default=100, ge=0, le=10_000)
    manifest_schema_version: Literal["1.1", "1.2"] = "1.2"

    @model_validator(mode="after")
    def validate_extension_surfaces(self) -> "CapabilityManifest":
        if self.result_support == CapabilitySurfaceSupport.NONE and self.result_projector:
            raise ValueError("result_support NONE cannot declare a result_projector")
        if self.result_support != CapabilitySurfaceSupport.NONE and not self.result_projector:
            raise ValueError("result-producing capability requires a result_projector")
        if self.viewer_support == CapabilitySurfaceSupport.REQUIRED and not self.viewer_bindings:
            raise ValueError("viewer_support REQUIRED requires viewer_bindings")
        if self.viewer_support == CapabilitySurfaceSupport.NONE and self.viewer_bindings:
            raise ValueError("viewer_support NONE cannot declare viewer_bindings")
        if (
            self.interpretation_support
            in {CapabilitySurfaceSupport.REQUIRED, CapabilitySurfaceSupport.SUPPORTED}
            and not self.interpretation_profile
        ):
            raise ValueError(
                "explicit interpretation support requires interpretation_profile"
            )
        if (
            self.interpretation_support == CapabilitySurfaceSupport.NONE
            and self.interpretation_profile
        ):
            raise ValueError(
                "interpretation_support NONE cannot declare interpretation_profile"
            )
        if self.report_support == CapabilitySurfaceSupport.REQUIRED and not self.report_projector:
            raise ValueError("report_support REQUIRED requires report_projector")
        if self.report_support == CapabilitySurfaceSupport.NONE and self.report_projector:
            raise ValueError("report_support NONE cannot declare report_projector")
        return self


class ResearchTurnUIContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    active_object_refs: list[ScientificObjectRef] = Field(default_factory=list, max_length=64)
    selection_refs: list[ScientificObjectRef] = Field(default_factory=list, max_length=16)
    scientific_selections: list[ScientificSelectionContext] = Field(default_factory=list, max_length=16)
    explicit_object_refs: list[ScientificObjectRef] = Field(default_factory=list, max_length=64)
    explicit_result_ids: list[UUID] = Field(default_factory=list, max_length=16)
    explicit_finding_refs: list[str] = Field(default_factory=list, max_length=16)


class CreateResearchTurnRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=16_000)
    ui_context: ResearchTurnUIContext | None = None
    reply_to_turn_id: UUID | None = None
    autonomy_mode: AutonomyMode = AutonomyMode.STANDARD
    admission_key: str | None = Field(default=None, min_length=1, max_length=128)

    @field_validator("message")
    @classmethod
    def non_blank_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message must not be blank")
        return value

    @field_validator("admission_key")
    @classmethod
    def normalized_admission_key(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("admission_key must not be blank")
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
    idempotent_replay: bool = False


class ResearchTurnEventDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(ge=1)
    type: str
    turn_id: UUID
    timestamp: datetime
    payload: dict[str, Any]
