from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


class ScientificQuestionType(StrEnum):
    CHARACTERIZE = "CHARACTERIZE"
    COMPARE = "COMPARE"
    QUANTIFY = "QUANTIFY"
    VALIDATE = "VALIDATE"
    EXPLAIN = "EXPLAIN"
    TEST_HYPOTHESIS = "TEST_HYPOTHESIS"
    CHECK_CONSISTENCY = "CHECK_CONSISTENCY"
    IDENTIFY_LIMITATION = "IDENTIFY_LIMITATION"


class ScientificQuestionStatus(StrEnum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    LIMITED = "LIMITED"
    CONFLICTING = "CONFLICTING"


class EvidenceGapType(StrEnum):
    PROPERTY_NOT_QUANTIFIED = "PROPERTY_NOT_QUANTIFIED"
    COMPARISON_MISSING = "COMPARISON_MISSING"
    STRUCTURAL_CONTEXT_MISSING = "STRUCTURAL_CONTEXT_MISSING"
    TRANSPORT_METRIC_MISSING = "TRANSPORT_METRIC_MISSING"
    MODEL_ERROR_PATTERN_UNEXPLAINED = "MODEL_ERROR_PATTERN_UNEXPLAINED"
    CONTRADICTORY_RESULTS = "CONTRADICTORY_RESULTS"
    SOURCE_LIMITATION = "SOURCE_LIMITATION"
    METHOD_LIMITATION = "METHOD_LIMITATION"
    REFERENCE_BASELINE_MISSING = "REFERENCE_BASELINE_MISSING"
    SUPPLIED_RESULT_MISSING = "SUPPLIED_RESULT_MISSING"
    LITERATURE_CONTEXT_MISSING = "LITERATURE_CONTEXT_MISSING"
    PUBLISHED_COMPARISON_MISSING = "PUBLISHED_COMPARISON_MISSING"


class EvidenceOrigin(StrEnum):
    COMPUTED_EVIDENCE = "COMPUTED_EVIDENCE"
    LITERATURE_EVIDENCE = "LITERATURE_EVIDENCE"
    USER_PROVIDED_EVIDENCE = "USER_PROVIDED_EVIDENCE"


class EvidenceValue(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EvidenceStrength(StrEnum):
    WELL_SUPPORTED = "WELL_SUPPORTED"
    QUALIFIED_METHOD_DEPENDENT = "QUALIFIED_METHOD_DEPENDENT"
    LIMITED = "LIMITED"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"


class ScientificHypothesisStatus(StrEnum):
    PROPOSED = "PROPOSED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    SUPPORTED_WITHIN_SCOPE = "SUPPORTED_WITHIN_SCOPE"
    CONTRADICTED = "CONTRADICTED"
    UNRESOLVED = "UNRESOLVED"
    NOT_TESTABLE_WITH_AVAILABLE_CAPABILITIES = (
        "NOT_TESTABLE_WITH_AVAILABLE_CAPABILITIES"
    )


class ContradictionKind(StrEnum):
    DIFFERENT_EXACT_VERSIONS = "DIFFERENT_EXACT_VERSIONS"
    DIFFERENT_METHODS = "DIFFERENT_METHODS"
    DIFFERENT_PARAMETER_CONVENTIONS = "DIFFERENT_PARAMETER_CONVENTIONS"
    DIFFERENT_APPLICABILITY_DOMAINS = "DIFFERENT_APPLICABILITY_DOMAINS"
    DIFFERENT_UNITS = "DIFFERENT_UNITS"
    NUMERICAL_TOLERANCE = "NUMERICAL_TOLERANCE"
    GENUINE_UNRESOLVED = "GENUINE_UNRESOLVED"


class ComparisonCompatibilityStatus(StrEnum):
    COMPATIBLE = "COMPATIBLE"
    CONDITIONALLY_COMPATIBLE = "CONDITIONALLY_COMPATIBLE"
    NOT_COMPATIBLE = "NOT_COMPATIBLE"
    INSUFFICIENT_METADATA = "INSUFFICIENT_METADATA"


class ResearchStrategyAction(StrEnum):
    SYNTHESIZE = "SYNTHESIZE"
    CONTINUE_ANALYSIS = "CONTINUE_ANALYSIS"
    REUSE_RESULT = "REUSE_RESULT"
    TEST_HYPOTHESIS = "TEST_HYPOTHESIS"
    COMPARE = "COMPARE"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    STOP_WITH_LIMITATIONS = "STOP_WITH_LIMITATIONS"
    SEARCH_LITERATURE = "SEARCH_LITERATURE"


class EvidenceObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    result_id: UUID
    bundle_result_id: UUID
    fact_id: str
    predicate: str
    subject_ref: str
    value: Any
    unit: str | None = None
    capability_ids: list[str] = Field(default_factory=list, max_length=8)
    source_version_ids: list[UUID] = Field(default_factory=list, max_length=64)
    lineage_signature: str = Field(pattern=r"^[0-9a-f]{64}$")
    origin: EvidenceOrigin = EvidenceOrigin.COMPUTED_EVIDENCE


class EvidenceLineage(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    result_id: UUID
    bundle_result_id: UUID
    capability_ids: list[str] = Field(default_factory=list, max_length=8)
    source_version_ids: list[UUID] = Field(default_factory=list, max_length=64)
    artifact_ids: list[str] = Field(default_factory=list, max_length=64)
    parent_result_ids: list[UUID] = Field(default_factory=list, max_length=16)
    lineage_signature: str = Field(pattern=r"^[0-9a-f]{64}$")
    origin: EvidenceOrigin = EvidenceOrigin.COMPUTED_EVIDENCE


class LiteratureEvidenceReference(BaseModel):
    """Bounded strategy reference; full passages remain in Context authority."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: UUID
    project_id: str = Field(min_length=1, max_length=64)
    work_id: UUID
    snapshot_id: UUID
    evidence_scope: str = Field(min_length=1, max_length=64)
    support_type: str = Field(min_length=1, max_length=64)
    publication_status: str = Field(min_length=1, max_length=64)
    claim_refs: list[str] = Field(default_factory=list, max_length=32)
    lineage_signature: str = Field(pattern=r"^[0-9a-f]{64}$")


class ScientificQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    question_id: str = Field(min_length=1, max_length=96)
    question_type: ScientificQuestionType
    statement: str = Field(min_length=1, max_length=1000)
    status: ScientificQuestionStatus = ScientificQuestionStatus.OPEN
    evidence_result_ids: list[UUID] = Field(default_factory=list, max_length=16)
    evidence_gap_ids: list[str] = Field(default_factory=list, max_length=8)


class EvidenceGap(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    gap_id: str = Field(min_length=1, max_length=96)
    question_id: str = Field(min_length=1, max_length=96)
    gap_type: EvidenceGapType
    statement: str = Field(min_length=1, max_length=1000)
    evidence_value: EvidenceValue
    requirement_id: str | None = Field(default=None, max_length=128)
    required_result_types: list[str] = Field(default_factory=list, max_length=8)
    satisfied_by_result_ids: list[UUID] = Field(default_factory=list, max_length=16)


class ScientificHypothesis(BaseModel):
    """A bounded research proposal; never a scientific fact authority."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    hypothesis_id: str = Field(min_length=1, max_length=96)
    question_id: str = Field(min_length=1, max_length=96)
    statement: str = Field(min_length=1, max_length=1000)
    status: ScientificHypothesisStatus
    supporting_result_ids: list[UUID] = Field(default_factory=list, max_length=16)
    contradicting_result_ids: list[UUID] = Field(default_factory=list, max_length=16)
    testable_predictions: list[str] = Field(default_factory=list, max_length=8)
    known_assumptions: list[str] = Field(default_factory=list, max_length=8)
    evidence_gap_id: str | None = Field(default=None, max_length=96)


class EvidenceContradiction(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    contradiction_id: str = Field(min_length=1, max_length=96)
    predicate: str
    result_ids: list[UUID] = Field(min_length=2, max_length=8)
    kind: ContradictionKind
    resolution: str = Field(min_length=1, max_length=1000)
    unresolved: bool


class ComparisonCompatibility(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    left_result_id: UUID
    right_result_id: UUID
    predicate: str
    status: ComparisonCompatibilityStatus
    normalized_unit: str | None = None
    reason_codes: list[str] = Field(default_factory=list, max_length=8)


class ResearchEvidenceState(BaseModel):
    """Read-only strategy projection. ScientificResult remains authoritative."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["agent2.research-evidence-state/1.0"] = (
        "agent2.research-evidence-state/1.0"
    )
    project_id: str
    objective: str = Field(min_length=1, max_length=2048)
    result_ids: list[UUID] = Field(default_factory=list, max_length=32)
    exact_source_version_ids: list[UUID] = Field(default_factory=list, max_length=128)
    result_types: list[str] = Field(default_factory=list, max_length=64)
    capability_ids: list[str] = Field(default_factory=list, max_length=64)
    literature_evidence_ids: list[UUID] = Field(default_factory=list, max_length=24)
    literature_evidence: list[LiteratureEvidenceReference] = Field(
        default_factory=list, max_length=24
    )
    observations: list[EvidenceObservation] = Field(default_factory=list, max_length=256)
    lineages: list[EvidenceLineage] = Field(default_factory=list, max_length=32)
    questions: list[ScientificQuestion] = Field(default_factory=list, max_length=8)
    evidence_gaps: list[EvidenceGap] = Field(default_factory=list, max_length=16)
    hypotheses: list[ScientificHypothesis] = Field(default_factory=list, max_length=8)
    contradictions: list[EvidenceContradiction] = Field(
        default_factory=list, max_length=16
    )
    comparisons: list[ComparisonCompatibility] = Field(
        default_factory=list, max_length=32
    )
    limitations: list[str] = Field(default_factory=list, max_length=32)
    evidence_strength: EvidenceStrength = EvidenceStrength.INSUFFICIENT

    @computed_field
    @property
    def fingerprint(self) -> str:
        payload = self.model_dump(mode="json", exclude={"fingerprint"})
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()


class ResearchStrategyDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["agent2.research-strategy-decision/1.0"] = (
        "agent2.research-strategy-decision/1.0"
    )
    action: ResearchStrategyAction
    objective: str = Field(min_length=1, max_length=2048)
    current_question_id: str | None = Field(default=None, max_length=96)
    evidence_gap: EvidenceGap | None = None
    evidence_result_ids: list[UUID] = Field(default_factory=list, max_length=16)
    capability_need: str | None = Field(default=None, max_length=128)
    selected_capability_id: str | None = Field(default=None, max_length=128)
    hypothesis: ScientificHypothesis | None = None
    evidence_value: EvidenceValue | None = None
    reason_codes: list[str] = Field(min_length=1, max_length=16)
    limitations: list[str] = Field(default_factory=list, max_length=16)
    contradiction_ids: list[str] = Field(default_factory=list, max_length=8)
    comparison_status: ComparisonCompatibilityStatus | None = None
    literature_purpose: str | None = Field(default=None, max_length=64)
    evidence_state_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_action_shape(self) -> "ResearchStrategyDecision":
        continuing = self.action in {
            ResearchStrategyAction.CONTINUE_ANALYSIS,
            ResearchStrategyAction.TEST_HYPOTHESIS,
            ResearchStrategyAction.COMPARE,
        }
        if continuing and not (self.capability_need and self.selected_capability_id):
            raise ValueError(
                "continuing strategy decision requires capability need and selection"
            )
        if self.action == ResearchStrategyAction.TEST_HYPOTHESIS and self.hypothesis is None:
            raise ValueError("hypothesis test decision requires hypothesis")
        if self.action == ResearchStrategyAction.SEARCH_LITERATURE:
            if not self.evidence_gap or not self.literature_purpose:
                raise ValueError(
                    "literature strategy decision requires evidence gap and purpose"
                )
            if self.selected_capability_id or self.capability_need:
                raise ValueError(
                    "literature retrieval is not a scientific Capability selection"
                )
        return self


class ResearchStrategySummary(BaseModel):
    """Bounded event/projection payload derived from the full evidence state."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_state_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    evidence_strength: EvidenceStrength
    question_count: int = Field(ge=0, le=8)
    resolved_question_count: int = Field(ge=0, le=8)
    open_question_count: int = Field(ge=0, le=8)
    evidence_gap_count: int = Field(ge=0, le=16)
    hypothesis_count: int = Field(ge=0, le=8)
    unresolved_contradiction_count: int = Field(ge=0, le=16)
    result_count: int = Field(ge=0, le=32)
    lineage_count: int = Field(ge=0, le=32)
    questions: list[ScientificQuestion] = Field(default_factory=list, max_length=8)
    evidence_gaps: list[EvidenceGap] = Field(default_factory=list, max_length=16)
    hypotheses: list[ScientificHypothesis] = Field(default_factory=list, max_length=8)
    contradictions: list[EvidenceContradiction] = Field(
        default_factory=list, max_length=16
    )
    current_question: ScientificQuestion | None = None
    active_evidence_gap: EvidenceGap | None = None
    active_hypothesis: ScientificHypothesis | None = None

    @classmethod
    def from_state(
        cls,
        state: ResearchEvidenceState,
        decision: ResearchStrategyDecision,
    ) -> "ResearchStrategySummary":
        question = next(
            (
                item
                for item in state.questions
                if item.question_id == decision.current_question_id
            ),
            None,
        )
        return cls(
            evidence_state_fingerprint=state.fingerprint,
            evidence_strength=state.evidence_strength,
            question_count=len(state.questions),
            resolved_question_count=sum(
                item.status == ScientificQuestionStatus.RESOLVED
                for item in state.questions
            ),
            open_question_count=sum(
                item.status == ScientificQuestionStatus.OPEN
                for item in state.questions
            ),
            evidence_gap_count=len(state.evidence_gaps),
            hypothesis_count=len(state.hypotheses),
            unresolved_contradiction_count=sum(
                item.unresolved for item in state.contradictions
            ),
            result_count=len(state.result_ids),
            lineage_count=len(state.lineages),
            questions=state.questions,
            evidence_gaps=state.evidence_gaps,
            hypotheses=state.hypotheses,
            contradictions=state.contradictions,
            current_question=question,
            active_evidence_gap=decision.evidence_gap,
            active_hypothesis=decision.hypothesis,
        )


class ProviderStrategyProposal(BaseModel):
    """Bounded provider proposal using legal references supplied by the caller."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["1.0"] = "1.0"
    action: ResearchStrategyAction
    current_question_id: str | None = Field(default=None, max_length=96)
    evidence_gap_id: str | None = Field(default=None, max_length=96)
    capability_need: str | None = Field(default=None, max_length=128)
    evidence_result_ids: list[UUID] = Field(default_factory=list, max_length=16)
    hypothesis_id: str | None = Field(default=None, max_length=96)
    reason_codes: list[str] = Field(min_length=1, max_length=8)
    limitation_refs: list[str] = Field(default_factory=list, max_length=8)
    literature_purpose: str | None = Field(default=None, max_length=64)


__all__ = [
    "ComparisonCompatibility",
    "ComparisonCompatibilityStatus",
    "ContradictionKind",
    "EvidenceContradiction",
    "EvidenceGap",
    "EvidenceGapType",
    "EvidenceLineage",
    "EvidenceObservation",
    "EvidenceOrigin",
    "EvidenceStrength",
    "EvidenceValue",
    "ProviderStrategyProposal",
    "LiteratureEvidenceReference",
    "ResearchEvidenceState",
    "ResearchStrategyAction",
    "ResearchStrategyDecision",
    "ResearchStrategySummary",
    "ScientificHypothesis",
    "ScientificHypothesisStatus",
    "ScientificQuestion",
    "ScientificQuestionStatus",
    "ScientificQuestionType",
]
