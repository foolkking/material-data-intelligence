from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


SCIENTIFIC_REASONING_CONTRACT_VERSION = "scientific-reasoning/1.0"
SCIENTIFIC_REASONING_POLICY_VERSION = "scientific-reasoning-policy/1.0"


class ScientificClaimType(StrEnum):
    DIRECT_OBSERVATION = "DIRECT_OBSERVATION"
    DESCRIPTIVE_SYNTHESIS = "DESCRIPTIVE_SYNTHESIS"
    QUANTITATIVE_COMPARISON = "QUANTITATIVE_COMPARISON"
    QUALITATIVE_COMPARISON = "QUALITATIVE_COMPARISON"
    TREND = "TREND"
    ASSOCIATION = "ASSOCIATION"
    MECHANISTIC_INTERPRETATION = "MECHANISTIC_INTERPRETATION"
    CAUSAL_CLAIM = "CAUSAL_CLAIM"
    GENERALIZATION = "GENERALIZATION"
    METHOD_INTERPRETATION = "METHOD_INTERPRETATION"
    LIMITATION = "LIMITATION"
    RECOMMENDATION = "RECOMMENDATION"


class ClaimSupportStatus(StrEnum):
    DIRECTLY_SUPPORTED = "DIRECTLY_SUPPORTED"
    SUPPORTED_WITHIN_SCOPE = "SUPPORTED_WITHIN_SCOPE"
    CONSISTENT_WITH = "CONSISTENT_WITH"
    SUGGESTIVE = "SUGGESTIVE"
    CONFLICTED = "CONFLICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NOT_SUPPORTED = "NOT_SUPPORTED"


class MethodComparisonStatus(StrEnum):
    DIRECTLY_COMPARABLE = "DIRECTLY_COMPARABLE"
    COMPARABLE_WITH_QUALIFIERS = "COMPARABLE_WITH_QUALIFIERS"
    COMPLEMENTARY = "COMPLEMENTARY"
    METHOD_DEPENDENT_DIFFERENCE = "METHOD_DEPENDENT_DIFFERENCE"
    NOT_COMPARABLE = "NOT_COMPARABLE"
    INSUFFICIENT_METHOD_METADATA = "INSUFFICIENT_METHOD_METADATA"


class ScientificReasoningOutcome(StrEnum):
    SUPPORTED = "SUPPORTED"
    SUPPORTED_WITH_QUALIFIERS = "SUPPORTED_WITH_QUALIFIERS"
    SUPPORTED_ONLY_AS_HYPOTHESIS = "SUPPORTED_ONLY_AS_HYPOTHESIS"
    METHOD_DEPENDENT_DIFFERENCE = "METHOD_DEPENDENT_DIFFERENCE"
    CONDITION_EXPLAINED_DIFFERENCE = "CONDITION_EXPLAINED_DIFFERENCE"
    CONFLICTED = "CONFLICTED"
    DERIVATION_REQUIRED = "DERIVATION_REQUIRED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    SCIENTIFIC_AUTHORITY_VIOLATION = "SCIENTIFIC_AUTHORITY_VIOLATION"


class ReasoningDefectType(StrEnum):
    QUALITATIVE_SUPPORT = "QUALITATIVE_SUPPORT"
    CAUSAL_OVERCLAIM = "CAUSAL_OVERCLAIM"
    MECHANISTIC_OVERCLAIM = "MECHANISTIC_OVERCLAIM"
    SCOPE_EXPANSION = "SCOPE_EXPANSION"
    METHOD_MISINTERPRETATION = "METHOD_MISINTERPRETATION"
    INVALID_COMPARISON = "INVALID_COMPARISON"
    EVIDENCE_DOUBLE_COUNT = "EVIDENCE_DOUBLE_COUNT"
    CONTRADICTION_COLLAPSE = "CONTRADICTION_COLLAPSE"
    MISSING_LIMITATION = "MISSING_LIMITATION"
    HYPOTHESIS_ESCALATION = "HYPOTHESIS_ESCALATION"
    DERIVED_NUMBER_INVENTION = "DERIVED_NUMBER_INVENTION"
    SOURCE_SCOPE_OVERREACH = "SOURCE_SCOPE_OVERREACH"
    SCIENTIFIC_AUTHORITY = "SCIENTIFIC_AUTHORITY"


class ReasoningDefectSeverity(StrEnum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MODERATE = "MODERATE"
    MINOR = "MINOR"


class EvidenceOrigin(StrEnum):
    COMPUTED = "COMPUTED"
    LITERATURE = "LITERATURE"
    USER_PROVIDED = "USER_PROVIDED"


class ReasoningEvidence(BaseModel):
    """A bounded read projection over existing evidence authorities."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ref: str = Field(pattern=r"^(?:result|literature|evidence)_[A-Za-z0-9_.:-]+$")
    origin: EvidenceOrigin
    text: str = Field(min_length=1, max_length=12000)
    scope: str = Field(min_length=1, max_length=1000)
    method: str | None = Field(default=None, max_length=1000)
    conditions: list[str] = Field(default_factory=list, max_length=16)
    lineage: str = Field(min_length=1, max_length=512)
    depends_on: list[str] = Field(default_factory=list, max_length=16)
    relation: str | None = Field(default=None, max_length=512)
    publication_role: str | None = Field(default=None, max_length=64)
    evidence_scope: str | None = Field(default=None, max_length=64)
    publication_status: str | None = Field(default=None, max_length=64)
    limitations: list[str] = Field(default_factory=list, max_length=16)
    semantic_tags: list[str] = Field(default_factory=list, max_length=16)
    causal_authority: bool = False
    generalization_authority: bool = False


class ProposedScientificClaim(BaseModel):
    """Provider-safe proposed claim; never scientific fact authority."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    claim_id: str = Field(min_length=1, max_length=128)
    text: str = Field(min_length=1, max_length=4000)
    claim_type: ScientificClaimType
    support_status: ClaimSupportStatus
    evidence_refs: list[str] = Field(min_length=1, max_length=16)
    contradicting_refs: list[str] = Field(default_factory=list, max_length=16)
    scope: str = Field(min_length=1, max_length=1000)
    qualifiers: list[str] = Field(default_factory=list, max_length=16)
    limitations: list[str] = Field(default_factory=list, max_length=16)
    comparison_status: MethodComparisonStatus | None = None
    hypothesis_status: str | None = Field(default=None, max_length=64)
    derived_fact_ref: str | None = Field(default=None, max_length=128)
    derived_numeric: bool = False

    @model_validator(mode="after")
    def validate_refs(self) -> "ProposedScientificClaim":
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("claim evidence refs must be unique")
        if len(self.contradicting_refs) != len(set(self.contradicting_refs)):
            raise ValueError("claim contradicting refs must be unique")
        return self


class ClaimSupportAssessment(BaseModel):
    """Observable scientific support projection; no hidden reasoning."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["scientific-reasoning/1.0"] = (
        SCIENTIFIC_REASONING_CONTRACT_VERSION
    )
    assessment_version: Literal["scientific-reasoning-policy/1.0"] = (
        SCIENTIFIC_REASONING_POLICY_VERSION
    )
    claim_id: str
    claim_type: ScientificClaimType
    support_status: ClaimSupportStatus
    outcome: ScientificReasoningOutcome
    accepted: bool
    supporting_refs: list[str] = Field(default_factory=list, max_length=16)
    contradicting_refs: list[str] = Field(default_factory=list, max_length=16)
    scope: str
    method_context: list[str] = Field(default_factory=list, max_length=16)
    comparison_status: MethodComparisonStatus | None = None
    required_qualifiers: list[str] = Field(default_factory=list, max_length=16)
    limitations: list[str] = Field(default_factory=list, max_length=32)
    reason_codes: list[str] = Field(default_factory=list, max_length=32)
    independent_evidence_groups: int = Field(ge=0, le=16)
    defects: list[ReasoningDefectType] = Field(default_factory=list, max_length=16)
    severity: ReasoningDefectSeverity | None = None

    @property
    def fingerprint(self) -> str:
        payload = self.model_dump(mode="json", exclude={"fingerprint"})
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


__all__ = [
    "ClaimSupportAssessment",
    "ClaimSupportStatus",
    "EvidenceOrigin",
    "MethodComparisonStatus",
    "ProposedScientificClaim",
    "ReasoningDefectSeverity",
    "ReasoningDefectType",
    "ReasoningEvidence",
    "SCIENTIFIC_REASONING_CONTRACT_VERSION",
    "SCIENTIFIC_REASONING_POLICY_VERSION",
    "ScientificClaimType",
    "ScientificReasoningOutcome",
]
