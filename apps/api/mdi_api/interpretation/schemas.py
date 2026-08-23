from __future__ import annotations

import re
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FindingImportance(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FindingConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LIMITED = "LIMITED"


class ScientificFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    finding_id: str = Field(min_length=1, max_length=128)
    statement: str = Field(min_length=1, max_length=4000)
    importance: FindingImportance
    confidence: FindingConfidence
    fact_refs: list[str] = Field(default_factory=list, max_length=32)
    evidence_refs: list[str] = Field(default_factory=list, max_length=32)
    result_item_refs: list[str] = Field(default_factory=list, max_length=32)


class ScientificInterpretationOutput(BaseModel):
    """The only provider output accepted by the Agent2 conversation path."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    contract_version: Literal["1.0"]
    title: str = Field(min_length=1, max_length=256)
    answer_lead: str = Field(min_length=1, max_length=4000)
    primary_findings: list[ScientificFinding] = Field(default_factory=list, max_length=8)
    supporting_findings: list[ScientificFinding] = Field(default_factory=list, max_length=16)
    limitations: list[str] = Field(default_factory=list, max_length=16)
    primary_result_refs: list[str] = Field(default_factory=list, max_length=16)
    supporting_result_refs: list[str] = Field(default_factory=list, max_length=32)
    follow_up_suggestions: list[str] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def validate_ids(self) -> "ScientificInterpretationOutput":
        findings = [*self.primary_findings, *self.supporting_findings]
        ids = [item.finding_id for item in findings]
        if len(ids) != len(set(ids)):
            raise ValueError("finding_id must be unique")
        if not findings:
            raise ValueError("at least one grounded finding is required")
        return self


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


def numeric_tokens(text: str) -> list[str]:
    return _NUMBER.findall(text or "")


__all__ = [
    "FindingConfidence",
    "FindingImportance",
    "GroundingValidationResult",
    "InterpretationInputEnvelope",
    "ScientificFinding",
    "ScientificInterpretationOutput",
    "numeric_tokens",
]
