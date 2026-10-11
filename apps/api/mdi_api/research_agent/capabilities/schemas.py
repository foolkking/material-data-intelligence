from __future__ import annotations

from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from mdi_schemas.project_planning import PlatformReferenceDescription

from mdi_api.scientific_objects.schemas import ScientificObjectRef


class CapabilityEligibility(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    CONDITIONAL = "CONDITIONAL"
    INELIGIBLE = "INELIGIBLE"


class CapabilityCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability_id: str
    capability_version: str
    eligibility: CapabilityEligibility
    satisfies_requirement_ids: list[str]
    bound_source_inputs: dict[str, list[ScientificObjectRef]] = Field(default_factory=dict)
    bound_source_ref_keys: dict[str, list[str]] = Field(default_factory=dict)
    reusable_result_bindings: dict[str, list[str]] = Field(default_factory=dict)
    reusable_result_source_ref_keys: dict[str, dict[str, list[str]]] = Field(default_factory=dict)
    missing_input_slots: list[str] = Field(default_factory=list)
    possible_producers: dict[str, list[str]] = Field(default_factory=dict)
    reason_codes: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    planning_priority: int = Field(ge=0)


class CapabilityResolution(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["1.0"] = "1.0"
    research_turn_id: UUID
    objective: str = Field(min_length=1, max_length=2048)
    requirement_ids: list[str]
    candidates: list[CapabilityCandidate]
    unsatisfied_required_requirement_ids: list[str]
    optional_requirement_ids_not_covered: list[str]
    registry_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    resolver_version: str = "agent2.capability-resolver/1.1"


class CapabilityBindingKind(str, Enum):
    SOURCE_OBJECT = "SOURCE_OBJECT"
    PREVIOUS_RESULT = "PREVIOUS_RESULT"
    PLANNED_OUTPUT = "PLANNED_OUTPUT"


class CapabilityInputBinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: CapabilityBindingKind
    source_ref_key: str | None = None
    result_ref_key: str | None = None
    producer_step_id: str | None = None
    producer_output_slot: str | None = None

    @model_validator(mode="after")
    def validate_shape(self) -> "CapabilityInputBinding":
        values = {
            CapabilityBindingKind.SOURCE_OBJECT: (self.source_ref_key is not None, self.result_ref_key is None, self.producer_step_id is None, self.producer_output_slot is None),
            CapabilityBindingKind.PREVIOUS_RESULT: (self.source_ref_key is None, self.result_ref_key is not None, self.producer_step_id is None, self.producer_output_slot is None),
            CapabilityBindingKind.PLANNED_OUTPUT: (self.source_ref_key is None, self.result_ref_key is None, self.producer_step_id is not None, self.producer_output_slot is not None),
        }[self.kind]
        if not all(values):
            raise ValueError("binding fields do not match binding kind")
        return self


class PlannedCapabilityOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    slot_name: str
    result_type: str
    scientific_object_type: str | None = None


class CapabilityPlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    step_id: str = Field(pattern=r"^step_[1-9][0-9]*$")
    capability_ref_key: str = Field(pattern=r"^cap_[1-9][0-9]*$")
    satisfies_requirement_ids: list[str]
    input_bindings: dict[str, list[CapabilityInputBinding]] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)
    expected_outputs: list[PlannedCapabilityOutput] = Field(default_factory=list)


class CapabilityPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["1.0"] = "1.0"
    objective: str = Field(min_length=1, max_length=2048)
    steps: list[CapabilityPlanStep] = Field(min_length=1, max_length=8)
    omitted_optional_requirement_ids: list[str] = Field(default_factory=list)
    planner_summary: str | None = Field(default=None, max_length=512)


class CapabilityPlanningLimits(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_steps: int = Field(default=8, ge=1, le=8)
    max_dependencies: int = Field(default=16, ge=0, le=16)
    allow_optional_requirements: bool = True
    allow_reuse_results: bool = True


class PlannerRequirementView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    requirement_id: str
    criticality: str
    subject_ref_keys: list[str]
    constraints: dict[str, Any] = Field(default_factory=dict)


class PlannerInputSlotView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str
    accepted_object_types: list[str]
    required: bool
    min_count: int
    max_count: int | None


class PlannerOutputSlotView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str
    result_type: str
    scientific_object_type: str | None
    required: bool
    cardinality: Literal["ONE", "MANY"]


class PlannerCapabilityView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    ref_key: str
    capability_id: str
    version: str
    eligibility: CapabilityEligibility
    satisfies_requirement_ids: list[str]
    input_slots: list[PlannerInputSlotView]
    output_slots: list[PlannerOutputSlotView]
    bound_source_ref_keys: dict[str, list[str]] = Field(default_factory=dict)
    reusable_result_bindings: dict[str, list[str]] = Field(default_factory=dict)
    reusable_result_source_ref_keys: dict[str, dict[str, list[str]]] = Field(default_factory=dict)
    missing_input_slots: list[str] = Field(default_factory=list)
    possible_producer_ref_keys: dict[str, list[str]] = Field(default_factory=dict)
    qualification_level: str = "UNKNOWN"
    qualification_evidence_version: str | None = None
    qualification_evidence_fingerprint: str | None = None
    scientific_contract_fingerprint: str | None = None
    validated_domains: list[str] = Field(default_factory=list, max_length=16)
    known_limitations: list[str] = Field(default_factory=list, max_length=3)
    reference_sources: list[PlatformReferenceDescription] = Field(default_factory=list, max_length=8)


class PlannerSourceRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    ref_key: str
    object_type: str
    display_name: str


class PlannerResultRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    ref_key: str
    result_id: UUID
    relevance_status: str
    output_object_types: list[str] = Field(default_factory=list)


class CapabilityPlannerInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    contract_version: Literal["1.0"] = "1.0"
    research_objective: str
    requirements: list[PlannerRequirementView]
    candidates: list[PlannerCapabilityView]
    source_bindings: list[PlannerSourceRef]
    reusable_results: list[PlannerResultRef]
    explicit_constraints: list[dict[str, Any]]
    limits: CapabilityPlanningLimits = CapabilityPlanningLimits()
