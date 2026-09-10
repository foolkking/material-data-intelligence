from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

from mdi_api.research_agent.strategy.schemas import (
    ResearchStrategyDecision,
    ResearchStrategySummary,
)


class AutonomyProgressOutcome(StrEnum):
    GOAL_SATISFIED = "GOAL_SATISFIED"
    CONTINUE_WITH_ANALYSIS = "CONTINUE_WITH_ANALYSIS"
    REUSE_EXISTING_RESULT = "REUSE_EXISTING_RESULT"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    NO_QUALIFIED_CAPABILITY = "NO_QUALIFIED_CAPABILITY"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    NON_PROGRESS = "NON_PROGRESS"
    STOP_WITH_LIMITATIONS = "STOP_WITH_LIMITATIONS"
    CANCELLED = "CANCELLED"


class AutonomyPolicy(BaseModel):
    """Finite policy snapshot governing one bounded autonomous branch."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: Literal["agent2.autonomy-policy/1.0"] = "agent2.autonomy-policy/1.0"
    max_cycles: int = Field(default=4, ge=1, le=8)
    max_capability_executions: int = Field(default=8, ge=1, le=32)
    # AnalysisPlan 0.2 has a hard four-step dependency cap. Keep the autonomy
    # policy honest about the executable contract instead of advertising a
    # larger per-cycle plan that can never be persisted.
    max_dependency_steps_per_cycle: int = Field(default=4, ge=1, le=4)
    max_llm_decision_calls: int = Field(default=8, ge=1, le=32)
    max_replans: int = Field(default=3, ge=0, le=8)
    max_context_input_tokens: int = Field(default=12_000, ge=2_000, le=64_000)
    max_cost_class: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    allowed_qualification_levels: tuple[str, ...] = (
        "DOMAIN_VALIDATED",
        "REFERENCE_VALIDATED",
        "CROSS_IMPLEMENTATION_VALIDATED",
        "EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED",
    )

    @computed_field
    @property
    def fingerprint(self) -> str:
        payload = self.model_dump(mode="json", exclude={"fingerprint"})
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()


class CapabilityQualificationSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability_id: str
    capability_version: str
    qualification_level: str
    allowed_for_autonomy: bool
    evidence_version: str | None = None
    evidence_fingerprint: str | None = None
    scientific_contract_fingerprint: str
    validated_domains: list[str] = Field(default_factory=list, max_length=32)
    known_limitations: list[str] = Field(default_factory=list, max_length=8)
    reason_code: str


class AutonomyAssessment(BaseModel):
    """Structured decision provenance; never stores hidden model reasoning."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["1.0"] = "1.0"
    research_turn_id: UUID
    root_turn_id: UUID
    cycle_index: int = Field(ge=1)
    research_objective: str = Field(min_length=1, max_length=2048)
    outcome: AutonomyProgressOutcome
    evidence_result_ids: list[UUID] = Field(default_factory=list, max_length=16)
    completed_capability_ids: list[str] = Field(default_factory=list, max_length=32)
    unresolved_requirement_id: str | None = None
    selected_capability_id: str | None = None
    selected_capability_version: str | None = None
    selected_parameters: dict[str, object] = Field(default_factory=dict)
    qualification: CapabilityQualificationSnapshot | None = None
    exact_source_version_ids: list[UUID] = Field(default_factory=list, max_length=64)
    context_snapshot_id: UUID | None = None
    context_snapshot_fingerprint: str | None = Field(
        default=None, pattern=r"^[0-9a-f]{64}$"
    )
    semantic_step_signature: str | None = Field(
        default=None, pattern=r"^[0-9a-f]{64}$"
    )
    reason_codes: list[str] = Field(min_length=1, max_length=16)
    limitations: list[str] = Field(default_factory=list, max_length=16)
    strategy_decision: ResearchStrategyDecision | None = None
    strategy_summary: ResearchStrategySummary | None = None
    policy_version: str
    policy_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")


class AutonomyAdvanceResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    turn_id: UUID
    outcome: AutonomyProgressOutcome
    cycle_index: int = Field(ge=1)
    child_turn_id: UUID | None = None
    enqueued: bool = False
    reused_result_id: UUID | None = None
    assessment: AutonomyAssessment


__all__ = [
    "AutonomyAdvanceResult",
    "AutonomyAssessment",
    "AutonomyPolicy",
    "AutonomyProgressOutcome",
    "CapabilityQualificationSnapshot",
]
