from __future__ import annotations

from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mdi_api.scientific_objects.schemas import ScientificObjectRef


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
    figures: list[dict[str, Any]]
    tables: list[dict[str, Any]]
    output_object_refs: list[ScientificObjectRef]
    evidence: list[dict[str, Any]]
    methods: list[dict[str, Any]]
    limitations: list[dict[str, Any]]
    warnings: list[dict[str, Any]]
    provenance: dict[str, Any]
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
        known_facts = set(fact_ids)
        if any(ref not in known_facts for item in self.result_items for ref in item.fact_refs):
            raise ValueError("result item references an unknown fact")
        return self
