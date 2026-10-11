from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from mdi_api.research_agent.context.schemas import CompactResearchContext
from mdi_api.research_agent.schemas import ResearchAction, RequirementCriticality


class OrchestratorConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ProposedRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement_id: str
    criticality: RequirementCriticality
    subject_ref_keys: list[str]
    constraints: dict[str, Any] = Field(default_factory=dict)

    @field_validator("subject_ref_keys")
    @classmethod
    def unique_subject_refs(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("subject_ref_keys must be unique")
        return values


class ClarificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=1000)
    candidate_keys: list[str]

    @field_validator("candidate_keys")
    @classmethod
    def unique_candidate_keys(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("candidate_keys must be unique")
        return values


class ResearchTurnDecision(BaseModel):
    # The provider sees this schema before the context-aware validator runs.
    # Analysis must not advertise null/empty fields as executable decisions.
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "allOf": [{
            "if": {"properties": {"action": {"enum": ["ANALYZE", "CONTINUE_ANALYSIS"]}}, "required": ["action"]},
            "then": {
                "required": ["research_objective", "selected_scope_ref_keys", "scientific_requirements"],
                "properties": {
                    "research_objective": {"type": "string", "minLength": 1},
                    "scientific_requirements": {
                        "minItems": 1,
                        "contains": {"properties": {"criticality": {"const": "REQUIRED"}}, "required": ["criticality"]},
                    },
                },
            },
        }],
    })

    contract_version: Literal["1.0"]
    action: ResearchAction
    assistant_message: str | None = Field(default=None, max_length=8000)
    research_objective: str | None = Field(default=None, max_length=2048)
    selected_scope_ref_keys: list[str]
    scientific_requirements: list[ProposedRequirement]
    reusable_result_ref_keys: list[str]
    clarification: ClarificationRequest | None
    confidence: OrchestratorConfidence

    @field_validator("selected_scope_ref_keys", "reusable_result_ref_keys")
    @classmethod
    def unique_ref_keys(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("reference keys must be unique")
        return values


class OrchestratorRequirementOption(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    requirement_id: str
    display_name: str
    description: str
    constraint_schema: dict[str, Any]
    requires_material: bool = True


class ResearchOrchestratorInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["1.0"]
    user_message: str
    research_context: CompactResearchContext
    available_requirement_ids: list[OrchestratorRequirementOption]
    allowed_actions: list[ResearchAction]


class DownstreamDispatchStatus(str, Enum):
    COMPLETED = "COMPLETED"
    READY_FOR_DOWNSTREAM = "READY_FOR_DOWNSTREAM"


class ActionRoutingResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    action: ResearchAction
    turn_status: str
    dispatch_status: DownstreamDispatchStatus
    assistant_message_id: str | None = None
