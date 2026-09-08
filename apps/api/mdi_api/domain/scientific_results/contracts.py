from __future__ import annotations

from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mdi_api.domain.scientific_objects.contracts import ScientificObjectRef


class ResultExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class ResultRelevanceStatus(str, Enum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    SOURCE_MISSING = "SOURCE_MISSING"
    INVALIDATED = "INVALIDATED"


class ScientificResultRole(str, Enum):
    PRIMARY = "PRIMARY"
    SUPPORTING = "SUPPORTING"


class ProjectedArtifactRole(str, Enum):
    PRIMARY_RESULT = "PRIMARY_RESULT"
    SUPPORTING_RESULT = "SUPPORTING_RESULT"
    FIGURE = "FIGURE"
    TABLE = "TABLE"
    STRUCTURED_DATA = "STRUCTURED_DATA"
    EVIDENCE = "EVIDENCE"
    METHOD = "METHOD"
    AUXILIARY = "AUXILIARY"


class FactSourceLocator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_call_id: str | None = Field(default=None, max_length=64)
    artifact_id: str | None = Field(default=None, max_length=96)
    artifact_locator: str | None = Field(default=None, max_length=2048)
    scientific_object_ref: ScientificObjectRef | None = None

    @model_validator(mode="after")
    def has_locator(self) -> "FactSourceLocator":
        if not any((self.tool_call_id, self.artifact_id, self.artifact_locator, self.scientific_object_ref)):
            raise ValueError("fact source requires at least one locator")
        return self


class ScientificFact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fact_id: str = Field(min_length=1, max_length=128)
    predicate: str = Field(min_length=1, max_length=128)
    subject_ref: str = Field(min_length=1, max_length=256)
    value: Any
    unit: str | None = Field(default=None, max_length=64)
    uncertainty: dict[str, Any] | None = None
    source: FactSourceLocator


class ScientificResultItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=128)
    result_type: str = Field(min_length=1, max_length=128)
    role: ScientificResultRole
    title: str = Field(min_length=1, max_length=512)
    artifact_ids: list[str]
    scientific_object_refs: list[ScientificObjectRef]
    fact_refs: list[str]
    evidence_refs: list[str]
    viewer_binding: str | None = Field(default=None, max_length=128)


class ScientificFigure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    figure_id: str = Field(min_length=1, max_length=128)
    figure_type: str = Field(min_length=1, max_length=128)
    role: ScientificResultRole
    title: str | None = Field(default=None, max_length=512)
    caption_seed: str | None = Field(default=None, max_length=2000)
    artifact_ids: list[str]
    fact_refs: list[str]
    evidence_refs: list[str]
    viewer_binding: str | None = Field(default=None, max_length=128)


class ScientificTable(BaseModel):
    model_config = ConfigDict(extra="forbid")

    table_id: str = Field(min_length=1, max_length=128)
    table_type: str = Field(min_length=1, max_length=128)
    role: ScientificResultRole
    title: str | None = Field(default=None, max_length=512)
    artifact_ids: list[str]
    fact_refs: list[str]
    evidence_refs: list[str]


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=1, max_length=128)
    evidence_type: str = Field(min_length=1, max_length=128)
    artifact_id: str | None = None
    tool_call_id: str | None = None
    artifact_locator: str | None = Field(default=None, max_length=2048)
    scientific_object_refs: list[ScientificObjectRef] = Field(default_factory=list)
    supports_fact_refs: list[str] = Field(default_factory=list)
    supports_result_item_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def has_locator(self) -> "EvidenceItem":
        if not any((self.artifact_id, self.tool_call_id, self.artifact_locator, self.scientific_object_refs)):
            raise ValueError("evidence requires a concrete locator")
        return self


class MethodRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method_id: str = Field(min_length=1, max_length=128)
    capability_id: str = Field(min_length=1, max_length=128)
    capability_version: str = Field(min_length=1, max_length=64)
    tool_id: str | None = None
    tool_version: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    source_object_refs: list[ScientificObjectRef] = Field(default_factory=list)


class ScientificLimitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limitation_id: str = Field(min_length=1, max_length=128)
    code: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=2000)
    source_ref: str | None = None


class ScientificWarning(BaseModel):
    model_config = ConfigDict(extra="forbid")

    warning_id: str = Field(min_length=1, max_length=128)
    code: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=2000)
    source_ref: str | None = None


class ProvenanceRecord(BaseModel):
    # Legacy Phase 1 fixtures stored small provenance extensions. Keep those
    # extensions readable while the canonical fields below are typed.
    model_config = ConfigDict(extra="allow")

    research_turn_id: UUID | None = None
    job_id: str | None = None
    analysis_plan_id: str | None = None
    capability_plan_id: str | None = None
    execution_summary_id: str | None = None
    source_object_version_ids: list[UUID] = Field(default_factory=list)
    tool_call_ids: list[str] = Field(default_factory=list)
    artifact_ids: list[str] = Field(default_factory=list)
    projector_ids: list[str] = Field(default_factory=list)


class ScientificResultBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"]
    result_id: UUID
    project_id: str = Field(min_length=1, max_length=64)
    research_session_id: str = Field(min_length=1, max_length=64)
    research_turn_id: UUID
    research_question: str = Field(min_length=1, max_length=16_000)
    source_object_refs: list[ScientificObjectRef]
    execution_status: ResultExecutionStatus
    relevance_status: ResultRelevanceStatus
    result_items: list[ScientificResultItem]
    facts: list[ScientificFact]
    figures: list[ScientificFigure]
    tables: list[ScientificTable]
    output_object_refs: list[ScientificObjectRef]
    evidence: list[EvidenceItem]
    methods: list[MethodRecord]
    limitations: list[ScientificLimitation]
    warnings: list[ScientificWarning]
    provenance: ProvenanceRecord
    projection_version: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_bundle(self) -> "ScientificResultBundle":
        refs = [*self.source_object_refs, *self.output_object_refs, *(ref for item in self.result_items for ref in item.scientific_object_refs)]
        if any(ref.project_id != self.project_id for ref in refs):
            raise ValueError("all scientific object refs must belong to project_id")
        fact_ids = [item.fact_id for item in self.facts]
        if len(fact_ids) != len(set(fact_ids)):
            raise ValueError("fact_id must be unique")
        result_ids = [item.id for item in self.result_items]
        if len(result_ids) != len(set(result_ids)):
            raise ValueError("result item id must be unique")
        figure_ids = [item.figure_id for item in self.figures]
        if len(figure_ids) != len(set(figure_ids)):
            raise ValueError("figure_id must be unique")
        table_ids = [item.table_id for item in self.tables]
        if len(table_ids) != len(set(table_ids)):
            raise ValueError("table_id must be unique")
        evidence_ids = [item.evidence_id for item in self.evidence]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("evidence_id must be unique")
        known_facts = set(fact_ids)
        if any(ref not in known_facts for item in self.result_items for ref in item.fact_refs):
            raise ValueError("result item references an unknown fact")
        known_items = set(result_ids)
        known_evidence = set(evidence_ids)
        known_artifacts = set(self.provenance.artifact_ids)
        if any(ref not in known_facts for item in [*self.figures, *self.tables] for ref in item.fact_refs):
            raise ValueError("figure/table references an unknown fact")
        if any(ref not in known_evidence for item in [*self.figures, *self.tables] for ref in item.evidence_refs):
            raise ValueError("figure/table references an unknown evidence item")
        if any(ref not in known_facts for item in self.evidence for ref in item.supports_fact_refs):
            raise ValueError("evidence references an unknown fact")
        if any(ref not in known_items for item in self.evidence for ref in item.supports_result_item_refs):
            raise ValueError("evidence references an unknown result item")
        referenced_artifacts = {
            *[artifact_id for item in self.result_items for artifact_id in item.artifact_ids],
            *[artifact_id for item in self.figures for artifact_id in item.artifact_ids],
            *[artifact_id for item in self.tables for artifact_id in item.artifact_ids],
            *[item.artifact_id for item in self.evidence if item.artifact_id],
        }
        if known_artifacts and not referenced_artifacts.issubset(known_artifacts):
            raise ValueError("bundle references an unknown artifact")
        return self
__all__ = [
    "EvidenceItem",
    "FactSourceLocator",
    "MethodRecord",
    "ProjectedArtifactRole",
    "ProvenanceRecord",
    "ResultExecutionStatus",
    "ResultRelevanceStatus",
    "ScientificFact",
    "ScientificFigure",
    "ScientificLimitation",
    "ScientificResultBundle",
    "ScientificResultItem",
    "ScientificResultRole",
    "ScientificTable",
    "ScientificWarning",
]
