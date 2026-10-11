from __future__ import annotations

import re
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from mdi_api.domain.scientific_reasoning.contracts import (
    ClaimSupportAssessment,
    ClaimSupportStatus,
    MethodComparisonStatus,
    ScientificClaimType,
)


class FindingImportance(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FindingConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LIMITED = "LIMITED"


class ScientificFindingProposal(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    finding_id: str = Field(min_length=1, max_length=128)
    statement: str = Field(min_length=1, max_length=4000)
    importance: FindingImportance
    confidence: FindingConfidence
    fact_refs: list[str] = Field(default_factory=list, max_length=32)
    evidence_refs: list[str] = Field(default_factory=list, max_length=32)
    result_item_refs: list[str] = Field(default_factory=list, max_length=32)
    claim_type: ScientificClaimType = ScientificClaimType.DIRECT_OBSERVATION
    support_status: ClaimSupportStatus = ClaimSupportStatus.DIRECTLY_SUPPORTED
    scope: str = Field(default="current ScientificResult scope", max_length=1000)
    qualifiers: list[str] = Field(default_factory=list, max_length=16)
    comparison_status: MethodComparisonStatus | None = None
    hypothesis_status: str | None = Field(default=None, max_length=64)


class ScientificFinding(ScientificFindingProposal):
    """Stored finding, including the server-owned support assessment."""

    reasoning_assessment: ClaimSupportAssessment | None = None


class ScientificInterpretationProposal(BaseModel):
    """Provider-authored fields before deterministic scientific assessment."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    contract_version: Literal["1.0", "1.1"]
    title: str = Field(min_length=1, max_length=256)
    answer_lead: str = Field(min_length=1, max_length=4000)
    primary_findings: list[ScientificFindingProposal] = Field(default_factory=list, max_length=8)
    supporting_findings: list[ScientificFindingProposal] = Field(default_factory=list, max_length=16)
    limitations: list[str] = Field(default_factory=list, max_length=16)
    primary_result_refs: list[str] = Field(default_factory=list, max_length=16)
    supporting_result_refs: list[str] = Field(default_factory=list, max_length=32)
    follow_up_suggestions: list[str] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def validate_ids(self) -> "ScientificInterpretationProposal":
        findings = [*self.primary_findings, *self.supporting_findings]
        ids = [item.finding_id for item in findings]
        if len(ids) != len(set(ids)):
            raise ValueError("finding_id must be unique")
        if not findings:
            raise ValueError("at least one grounded finding is required")
        return self


class ScientificInterpretationOutput(ScientificInterpretationProposal):
    """Persisted and readable interpretation with server support assessments."""

    primary_findings: list[ScientificFinding] = Field(default_factory=list, max_length=8)
    supporting_findings: list[ScientificFinding] = Field(default_factory=list, max_length=16)


class InterpretationInputEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: Literal["1.0"]
    research_question: str = Field(min_length=1, max_length=16000)
    result: dict
    evidence: list[dict]
    conversation_context: dict
    omitted_supporting_items: list[str] = Field(default_factory=list)


class GroundingValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valid: bool
    errors: list[str] = Field(default_factory=list)


_NUMBER = re.compile(r"(?<![A-Za-z0-9_.])[-+]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?%?")
_OPAQUE_IDENTIFIER = re.compile(
    r"(?i)(?:\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b|"
    r"\b(?:fact|evidence|result|object|version|job|call|artifact)[._-][0-9a-f-]+\b|"
    # Stable scientific sample locators are identifiers, not measurements.
    # Keep this bounded to the repository's canonical ``mat-*`` / ``sample-*``
    # forms so ordinary hyphenated scientific prose remains numeric-aware.
    r"\b(?:mat|sample)[_-][A-Za-z0-9_-]+\b)"
)


def numeric_tokens(text: str) -> list[str]:
    # Opaque provenance refs can contain digits, but they are identifiers rather
    # than scientific measurements and must not satisfy quantitative grounding.
    return _NUMBER.findall(_OPAQUE_IDENTIFIER.sub(" ", text or ""))


__all__ = [
    "FindingConfidence",
    "FindingImportance",
    "GroundingValidationResult",
    "InterpretationInputEnvelope",
    "ScientificFinding",
    "ScientificInterpretationOutput",
    "numeric_tokens",
]
__all__ = [
    "FindingConfidence", "FindingImportance", "GroundingValidationResult",
    "InterpretationInputEnvelope", "ScientificFinding",
    "ScientificInterpretationOutput", "numeric_tokens",
]
