from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


REPORT_COMPOSER_CONTRACT_VERSION = "2.0"
REPORT_COMPOSER_VERSION = "agent2.report-composer/2.0"
REPORT_COMPOSER_PROMPT_VERSION = "scientific-report-composer/2.0"
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


class ReportGenerationStatus(StrEnum):
    REQUESTED = "REQUESTED"
    COMPOSING = "COMPOSING"
    READY = "READY"
    FAILED = "FAILED"


class ReportGroundingStatus(StrEnum):
    VALID = "VALID"


class ReportContextBundle(BaseModel):
    """Bounded, operation-specific report input.

    This is deliberately a communication contract, not a second scientific
    result store. Scientific values remain in the nested bounded Result
    projection and all provider-facing references are opaque identifiers.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["2.0"] = REPORT_COMPOSER_CONTRACT_VERSION
    research_question: str = Field(min_length=1, max_length=16000)
    result: dict[str, Any]
    interpretation: dict[str, Any]
    evidence: list[dict[str, Any]] = Field(default_factory=list, max_length=64)
    opaque_refs: dict[str, list[str]] = Field(default_factory=dict)
    omitted_supporting_items: list[str] = Field(default_factory=list, max_length=64)


class ReportFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    statement: str = Field(min_length=1, max_length=4000)
    finding_refs: list[str] = Field(default_factory=list, max_length=32)
    fact_refs: list[str] = Field(default_factory=list, max_length=32)
    evidence_refs: list[str] = Field(default_factory=list, max_length=32)


class ReportFigure(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    figure_ref: str = Field(min_length=1, max_length=128)
    caption: str = Field(min_length=1, max_length=2000)
    fact_refs: list[str] = Field(default_factory=list, max_length=32)
    evidence_refs: list[str] = Field(default_factory=list, max_length=32)


class ReportSupportingResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    result_item_ref: str = Field(min_length=1, max_length=128)
    description: str = Field(min_length=1, max_length=2000)


class ReportLimitation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    statement: str = Field(min_length=1, max_length=2000)
    source_refs: list[str] = Field(default_factory=list, max_length=32)


class ReportNarrativeSection(BaseModel):
    """A bounded, provenance-aware narrative section.

    Narrative is communication only.  Any scientific claim carried in a
    section must point back to the validated Result facts/evidence.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    text: str = Field(min_length=1, max_length=6000)
    fact_refs: list[str] = Field(default_factory=list, max_length=32)
    evidence_refs: list[str] = Field(default_factory=list, max_length=32)


class ScientificReportOutput(BaseModel):
    """Structured report content; it is not accepted until grounding passes."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["1.0", "2.0"] = REPORT_COMPOSER_CONTRACT_VERSION
    title: str = Field(min_length=1, max_length=256)
    research_question: str = Field(min_length=1, max_length=16000)
    summary: str = Field(min_length=1, max_length=6000)
    discussion: ReportNarrativeSection | None = None
    conclusion: ReportNarrativeSection | None = None
    next_steps: ReportNarrativeSection | None = None
    main_findings: list[ReportFinding] = Field(default_factory=list, max_length=16)
    primary_figures: list[ReportFigure] = Field(default_factory=list, max_length=16)
    supporting_results: list[ReportSupportingResult] = Field(default_factory=list, max_length=32)
    method_summary: str = Field(min_length=1, max_length=6000)
    limitations: list[ReportLimitation] = Field(default_factory=list, max_length=32)
    data_sources: list[str] = Field(default_factory=list, max_length=64)
    evidence_refs: list[str] = Field(default_factory=list, max_length=128)
    reproducibility_summary: str = Field(min_length=1, max_length=6000)
    omitted_supporting_items: list[str] = Field(default_factory=list, max_length=64)

    @model_validator(mode="after")
    def validate_ids(self) -> "ScientificReportOutput":
        refs = [*self.data_sources, *self.evidence_refs]
        for item in refs:
            if not _SAFE_ID.fullmatch(item):
                raise ValueError("report references must use stable opaque identities")
        if not self.main_findings:
            raise ValueError("report requires at least one grounded main finding")
        return self


class ScientificReportSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["1.0", "2.0"] = REPORT_COMPOSER_CONTRACT_VERSION
    report_id: str = Field(min_length=1, max_length=96)
    snapshot_id: UUID
    project_id: str = Field(min_length=1, max_length=64)
    research_session_id: str | None = Field(default=None, max_length=64)
    research_turn_id: UUID
    scientific_result_snapshot_id: UUID
    scientific_interpretation_id: UUID
    execution_status: str = Field(min_length=1, max_length=32)
    relevance_at_generation: str = Field(min_length=1, max_length=32)
    title: str = Field(min_length=1, max_length=256)
    report: ScientificReportOutput
    source_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    composer_version: str = REPORT_COMPOSER_VERSION
    prompt_version: str = REPORT_COMPOSER_PROMPT_VERSION
    grounding_status: Literal["VALID"] = "VALID"
    composer_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    @property
    def semantic_hash(self) -> str:
        payload = self.model_dump(mode="json", exclude={"snapshot_id", "created_at"})
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


__all__ = [
    "REPORT_COMPOSER_CONTRACT_VERSION", "REPORT_COMPOSER_PROMPT_VERSION", "REPORT_COMPOSER_VERSION",
    "ReportContextBundle",
    "ReportFigure", "ReportFinding", "ReportGenerationStatus", "ReportGroundingStatus",
    "ReportLimitation", "ReportNarrativeSection", "ReportSupportingResult",
    "ScientificReportOutput", "ScientificReportSnapshot",
]
