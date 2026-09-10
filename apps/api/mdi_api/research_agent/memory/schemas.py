from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from mdi_api.research_agent.context.provenance import (
    ContextAuthorityClass,
    ContextFreshness,
    MemoryEpistemicStatus,
)
from mdi_api.scientific_objects.schemas import ScientificObjectRef


class ContextScope(str, Enum):
    TURN = "TURN"
    SESSION = "SESSION"


class ResearchContextItemType(str, Enum):
    ACTIVE_SCOPE = "ACTIVE_SCOPE"
    ACTIVE_SELECTION = "ACTIVE_SELECTION"
    PINNED_OBJECT = "PINNED_OBJECT"
    PINNED_RESULT = "PINNED_RESULT"
    SESSION_CONSTRAINT = "SESSION_CONSTRAINT"
    RESEARCH_GOAL = "RESEARCH_GOAL"
    OPEN_QUESTION = "OPEN_QUESTION"
    PRIOR_FINDING = "PRIOR_FINDING"


class SessionConstraint(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    scope: ContextScope
    statement: str = Field(min_length=1, max_length=1000)
    structured_constraint: dict[str, Any] | None = None
    source_message_id: str
    explicitly_requested: bool = True
    active: bool = True
    created_at: datetime
    updated_at: datetime


class ResearchSessionState(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    session_id: str
    project_id: str
    active_scope_refs: list[ScientificObjectRef] = Field(default_factory=list, max_length=64)
    active_selection_refs: list[ScientificObjectRef] = Field(default_factory=list, max_length=16)
    pinned_object_refs: list[ScientificObjectRef] = Field(default_factory=list, max_length=64)
    pinned_result_refs: list[UUID] = Field(default_factory=list, max_length=64)
    session_constraints: list[SessionConstraint] = Field(default_factory=list, max_length=32)
    active_research_goal: str | None = Field(default=None, max_length=2048)
    open_questions: list[str] = Field(default_factory=list, max_length=16)
    version: int = Field(default=1, ge=1)
    updated_at: datetime
    created_at: datetime


class MemoryReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ref_type: Literal["SCIENTIFIC_OBJECT", "SCIENTIFIC_RESULT", "SCIENTIFIC_FINDING"]
    object_ref: ScientificObjectRef | None = None
    result_id: UUID | None = None
    finding_ref: str | None = None
    display_label: str = Field(min_length=1, max_length=512)
    source: str
    stale: bool = False
    authorized: bool = True
    recency_rank: int = Field(default=0, ge=0)
    authority_class: ContextAuthorityClass = ContextAuthorityClass.MEMORY
    freshness: ContextFreshness = ContextFreshness.CURRENT
    epistemic_status: MemoryEpistemicStatus = MemoryEpistemicStatus.OBSERVED
    provenance_refs: list[str] = Field(default_factory=list, max_length=16)


class PinObjectRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_ref: ScientificObjectRef
