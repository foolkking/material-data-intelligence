from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mdi_api.scientific_objects.schemas import ScientificObjectRef


BoundedContextText = Annotated[str, Field(min_length=1, max_length=1000)]


class ReferenceCandidateSource(str, Enum):
    EXPLICIT_REFERENCE = "EXPLICIT_REFERENCE"
    UI_SELECTION = "UI_SELECTION"
    CURRENT_SCOPE = "CURRENT_SCOPE"
    PREVIOUS_TURN_RESULT = "PREVIOUS_TURN_RESULT"
    PREVIOUS_TURN = "PREVIOUS_TURN"
    PINNED_CONTEXT = "PINNED_CONTEXT"
    RECENT_CONTEXT = "RECENT_CONTEXT"
    LONG_SESSION_RETRIEVAL = "LONG_SESSION_RETRIEVAL"


class ReferenceCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    candidate_key: str = Field(pattern=r"^(obj|result|finding)_[1-9][0-9]*$")
    ref_type: Literal["SCIENTIFIC_OBJECT", "SCIENTIFIC_RESULT", "SCIENTIFIC_FINDING"]
    object_ref: ScientificObjectRef | None = None
    result_id: UUID | None = None
    finding_ref: str | None = None
    source: ReferenceCandidateSource
    display_label: str = Field(min_length=1, max_length=512)
    semantic_summary: str | None = Field(default=None, max_length=2000)
    recency_rank: int = Field(ge=0)
    stale: bool = False

    @model_validator(mode="after")
    def validate_identity(self) -> "ReferenceCandidate":
        present = (self.object_ref is not None, self.result_id is not None, self.finding_ref is not None)
        expected = {
            "SCIENTIFIC_OBJECT": (True, False, False),
            "SCIENTIFIC_RESULT": (False, True, False),
            "SCIENTIFIC_FINDING": (False, False, True),
        }[self.ref_type]
        if present != expected:
            raise ValueError(f"{self.ref_type} candidate must carry exactly its matching reference")
        return self


class CompactMessage(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    role: Literal["USER", "ASSISTANT"]
    turn_sequence_no: int = Field(ge=1)
    content: str = Field(min_length=1, max_length=4024)
    created_at: datetime


class ResearchContextCandidateBundle(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    project_id: str = Field(min_length=1, max_length=64)
    research_session_id: str = Field(min_length=1, max_length=64)
    research_turn_id: UUID
    active_object_candidates: list[ReferenceCandidate] = Field(max_length=80)
    result_candidates: list[ReferenceCandidate] = Field(max_length=16)
    finding_candidates: list[ReferenceCandidate] = Field(max_length=16)
    explicit_constraints: list[BoundedContextText | dict[str, Any]] = Field(max_length=32)
    current_research_goal: str | None = Field(max_length=2048)
    unresolved_questions: list[BoundedContextText] = Field(max_length=16)
    recent_messages: list[CompactMessage] = Field(max_length=12)
    recent_turn_ids: list[UUID] = Field(default_factory=list, max_length=6)
    pinned_result_ids: list[UUID] = Field(default_factory=list, max_length=64)
    omitted_supporting_items: list[str] = Field(default_factory=list, max_length=16)
    current_user_message: str | None = Field(default=None, max_length=16000)
    assembly_version: str = "agent2.context-assembly/1.0"

    @model_validator(mode="after")
    def unique_candidate_keys(self) -> "ResearchContextCandidateBundle":
        candidates = [*self.active_object_candidates, *self.result_candidates, *self.finding_candidates]
        keys = [item.candidate_key for item in candidates]
        if len(keys) != len(set(keys)):
            raise ValueError("candidate_key values must be unique")
        if any(item.object_ref and item.object_ref.project_id != self.project_id for item in candidates):
            raise ValueError("object candidates must belong to project_id")
        return self


class CompactObjectSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ref_key: str
    object_type: str
    display_name: str
    availability_status: str
    version_label: str | None = None
    summary: dict[str, Any]


class CompactResultSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ref_key: str
    # Kept for server-side projection only; Pydantic serialization used for
    # provider input excludes the database identity.  The model sees ref_key.
    result_id: UUID = Field(exclude=True)
    research_question: str | None
    execution_status: str
    relevance_status: str
    summary: str


class CompactFindingSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ref_key: str
    display_label: str
    summary: str
    relevance_status: str


class CompactResearchContext(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    project_summary: str = Field(min_length=1, max_length=1000)
    current_goal: str | None = Field(max_length=2048)
    objects: list[CompactObjectSummary]
    results: list[CompactResultSummary]
    relevant_findings: list[CompactFindingSummary] = Field(default_factory=list, max_length=16)
    current_user_message: str | None = Field(default=None, max_length=16000)
    pinned_results: list[CompactResultSummary] = Field(default_factory=list, max_length=16)
    # Provider-facing context must not expose database UUIDs or other runtime
    # identities. Turn references are stable opaque labels; the server keeps
    # the real IDs in the immutable context snapshot/fingerprint.
    relevant_prior_turns: list[str] = Field(default_factory=list, max_length=12)
    resolved_references: list[dict[str, Any]] = Field(default_factory=list, max_length=32)
    omitted_supporting_items: list[str] = Field(default_factory=list, max_length=16)
    explicit_constraints: list[BoundedContextText | dict[str, Any]] = Field(max_length=32)
    unresolved_questions: list[BoundedContextText] = Field(max_length=16)
    recent_conversation: list[CompactMessage]
    context_fingerprint: str
