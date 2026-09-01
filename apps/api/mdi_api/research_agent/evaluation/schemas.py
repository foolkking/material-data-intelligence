from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mdi_api.research_agent.context.schemas import ReferenceCandidateSource
from mdi_api.research_agent.schemas import ResearchAction


class AgentEvalCategory(str, Enum):
    ROUTING = "ROUTING"
    CONTEXT_RESOLUTION = "CONTEXT_RESOLUTION"
    CLARIFICATION = "CLARIFICATION"
    REQUIREMENT_SELECTION = "REQUIREMENT_SELECTION"
    MULTI_TURN = "MULTI_TURN"
    DATA_MANAGEMENT = "DATA_MANAGEMENT"
    REPORTING = "REPORTING"
    SAFETY = "SAFETY"


class ExpectedToolPolicy(str, Enum):
    MUST_NOT_CALL = "MUST_NOT_CALL"
    MUST_CALL_LATER = "MUST_CALL_LATER"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class EvalObjectCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    key: str = Field(pattern=r"^obj_[1-9][0-9]*$")
    object_type: str
    display_name: str
    source: ReferenceCandidateSource
    semantic_summary: str = "Authorized scientific object"
    project_id: str = "eval-project"
    stale: bool = False


class EvalResultCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    key: str = Field(pattern=r"^result_[1-9][0-9]*$")
    display_name: str
    summary: str
    stale: bool = False


class AgentEvalExpectation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    action: ResearchAction | None = None
    acceptable_actions: list[ResearchAction] = Field(default_factory=list)
    selected_scope_ref_keys: list[str] = Field(default_factory=list)
    requirement_ids: list[str] = Field(default_factory=list)
    reusable_result_ref_keys: list[str] = Field(default_factory=list)
    constraint_subset: dict[str, Any] = Field(default_factory=dict)
    validation_error_code: str | None = None
    rejected_before_provider: bool = False
    deterministic_clarification: bool = False
    must_not_actions: list[ResearchAction] = Field(default_factory=list)


class AgentEvalCase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str = Field(pattern=r"^(?:C(?:0[1-9]|1[0-5])|R10-[0-9]{3})$")
    category: AgentEvalCategory
    message: str = Field(min_length=1, max_length=4000)
    paraphrases: list[str] = Field(min_length=3)
    object_candidates: list[EvalObjectCandidate] = Field(default_factory=list)
    result_candidates: list[EvalResultCandidate] = Field(default_factory=list)
    provider_decision: dict[str, Any] | None = None
    expected: AgentEvalExpectation
    tool_policy: ExpectedToolPolicy

    @model_validator(mode="after")
    def validate_fixture_shape(self) -> "AgentEvalCase":
        if len(set(self.paraphrases)) != len(self.paraphrases):
            raise ValueError("paraphrases must be unique")
        if not self.expected.rejected_before_provider and not self.expected.deterministic_clarification and self.provider_decision is None:
            raise ValueError("provider_decision is required for provider-routed cases")
        if (
            self.expected.action is None
            and not self.expected.acceptable_actions
            and not self.expected.rejected_before_provider
            and not self.expected.validation_error_code
        ):
            raise ValueError("an expected action or acceptable_actions is required")
        return self
