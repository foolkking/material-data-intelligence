from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mdi_api.research_agent.context.provenance import (
    ContextAuthorityClass,
    ContextFreshness,
    context_role_for_item,
    ContextSourceClass,
    MemoryEpistemicStatus,
    authority_for_candidate,
    candidate_source_ref,
    source_class_for_candidate,
    support_eligibility_for_item,
)
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

    candidate_key: str = Field(pattern=r"^(obj|result|finding|literature)_[1-9][0-9]*$")
    ref_type: Literal[
        "SCIENTIFIC_OBJECT",
        "SCIENTIFIC_RESULT",
        "SCIENTIFIC_FINDING",
        "LITERATURE_EVIDENCE",
    ]
    object_ref: ScientificObjectRef | None = None
    result_id: UUID | None = None
    finding_ref: str | None = None
    literature_evidence_id: UUID | None = None
    source: ReferenceCandidateSource
    display_label: str = Field(min_length=1, max_length=512)
    semantic_summary: str | None = Field(default=None, max_length=2000)
    recency_rank: int = Field(ge=0)
    stale: bool = False
    source_class: ContextSourceClass | None = None
    authority_class: ContextAuthorityClass | None = None
    freshness: ContextFreshness | None = None
    epistemic_status: MemoryEpistemicStatus | None = None
    source_ref: str | None = Field(default=None, max_length=256)
    support_eligible: bool = False

    @model_validator(mode="before")
    @classmethod
    def add_provenance_metadata(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        payload = dict(value)
        source = payload.get("source")
        ref_type = str(payload.get("ref_type") or "")
        payload.setdefault("source_class", source_class_for_candidate(source, ref_type))
        payload.setdefault("authority_class", authority_for_candidate(ref_type, source))
        payload.setdefault(
            "freshness",
            ContextFreshness.STALE if payload.get("stale") else ContextFreshness.CURRENT,
        )
        payload.setdefault(
            "epistemic_status",
            MemoryEpistemicStatus.COMPUTED
            if ref_type in {"SCIENTIFIC_RESULT", "SCIENTIFIC_FINDING"}
            else MemoryEpistemicStatus.REPORTED
            if ref_type == "LITERATURE_EVIDENCE"
            else MemoryEpistemicStatus.OBSERVED,
        )
        payload.setdefault(
            "support_eligible",
            support_eligibility_for_item(
                ref_type,
                str(payload.get("authority_class") or authority_for_candidate(ref_type, source)),
            ),
        )
        if payload.get("source_ref") is None:
            payload["source_ref"] = candidate_source_ref(payload)
        return payload

    @model_validator(mode="after")
    def validate_identity(self) -> "ReferenceCandidate":
        present = (
            self.object_ref is not None,
            self.result_id is not None,
            self.finding_ref is not None,
            self.literature_evidence_id is not None,
        )
        expected = {
            "SCIENTIFIC_OBJECT": (True, False, False, False),
            "SCIENTIFIC_RESULT": (False, True, False, False),
            "SCIENTIFIC_FINDING": (False, False, True, False),
            "LITERATURE_EVIDENCE": (False, False, False, True),
        }[self.ref_type]
        if present != expected:
            raise ValueError(f"{self.ref_type} candidate must carry exactly its matching reference")
        expected_support = self.ref_type in {
            "SCIENTIFIC_RESULT",
            "SCIENTIFIC_FINDING",
            "LITERATURE_EVIDENCE",
        }
        if self.support_eligible != expected_support:
            raise ValueError(
                f"{self.ref_type} candidate support eligibility must be {expected_support}"
            )
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
    literature_candidates: list[ReferenceCandidate] = Field(
        default_factory=list, max_length=24
    )
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
        candidates = [
            *self.active_object_candidates,
            *self.result_candidates,
            *self.finding_candidates,
            *self.literature_candidates,
        ]
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
    context_role: Literal[
        "EVIDENCE", "CONTINUITY", "SUBJECT", "CONSTRAINT", "PREFERENCE"
    ] = "SUBJECT"
    support_eligible: bool = False


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
    context_role: Literal[
        "EVIDENCE", "CONTINUITY", "SUBJECT", "CONSTRAINT", "PREFERENCE"
    ] = "EVIDENCE"
    support_eligible: bool = True


class CompactFindingSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ref_key: str
    display_label: str
    summary: str
    relevance_status: str
    context_role: Literal[
        "EVIDENCE", "CONTINUITY", "SUBJECT", "CONSTRAINT", "PREFERENCE"
    ] = "EVIDENCE"
    support_eligible: bool = True


class CompactLiteratureEvidenceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ref_key: str
    title: str = Field(min_length=1, max_length=1000)
    citation: str = Field(min_length=1, max_length=2000)
    evidence_scope: str = Field(min_length=1, max_length=64)
    support_type: str = Field(min_length=1, max_length=64)
    passage: str | None = Field(default=None, max_length=4000)
    publication_status: str = Field(min_length=1, max_length=64)
    context_role: Literal[
        "EVIDENCE", "CONTINUITY", "SUBJECT", "CONSTRAINT", "PREFERENCE"
    ] = "EVIDENCE"
    support_eligible: bool = True


class CompactResearchContext(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    project_summary: str = Field(min_length=1, max_length=1000)
    current_goal: str | None = Field(max_length=2048)
    objects: list[CompactObjectSummary]
    results: list[CompactResultSummary]
    relevant_findings: list[CompactFindingSummary] = Field(default_factory=list, max_length=16)
    literature_evidence: list[CompactLiteratureEvidenceSummary] = Field(
        default_factory=list, max_length=24
    )
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


class ContextManifestItem(BaseModel):
    """Auditable, provider-safe inclusion decision for one context item.

    Server-side identities remain available for replay while the provider
    receives only bounded opaque references.  This is a read-model over the
    immutable turn event; it is not a second scientific authority.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    item_id: str = Field(min_length=1, max_length=128)
    kind: Literal[
        "SCIENTIFIC_OBJECT",
        "SCIENTIFIC_SELECTION",
        "SCIENTIFIC_RESULT",
        "INTERPRETATION",
        "USER_CONSTRAINT",
        "RESEARCH_GOAL",
        "CAPABILITY_CANDIDATE",
        "SCIENTIFIC_EVIDENCE",
        "LITERATURE_EVIDENCE",
    ]
    authority_class: Literal[
        "SCIENTIFIC_DATA",
        "SCIENTIFIC_RESULT",
        "SCIENTIFIC_KNOWLEDGE",
        "SCIENTIFIC_EVIDENCE",
        "USER_CONSTRAINT",
        "CONVERSATIONAL_NARRATIVE",
        "SYSTEM_RUNTIME_STATE",
        "DERIVED_SUMMARY",
    ]
    server_side_source_identity: str = Field(min_length=1, max_length=256)
    provider_opaque_ref: str = Field(min_length=1, max_length=128)
    exact_object_id: str | None = Field(default=None, max_length=64)
    exact_object_version_id: str | None = Field(default=None, max_length=64)
    result_ref: str | None = Field(default=None, max_length=64)
    inclusion_reason: str = Field(min_length=1, max_length=256)
    selection_mode: Literal[
        "EXPLICIT",
        "UI_SELECTION",
        "CURRENT",
        "PINNED",
        "RECENT",
        "RETRIEVED",
        "CONTINUATION",
    ]
    authorization_checked: bool
    content_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    representation_type: str = Field(default="BOUNDED_JSON", min_length=1, max_length=64)
    representation_version: str = Field(default="1.0", min_length=1, max_length=64)
    serialized_representation: Any | None = None
    lineage_refs: list[str] = Field(default_factory=list, max_length=16)
    estimated_tokens: int = Field(ge=1, le=20000)
    source_class: str = "UNKNOWN"
    freshness: str = "UNKNOWN"
    epistemic_status: str = "OBSERVED"
    context_role: Literal[
        "EVIDENCE",
        "CONTINUITY",
        "SUBJECT",
        "CONSTRAINT",
        "PREFERENCE",
    ] = "CONTINUITY"
    support_eligible: bool = False
    was_compacted: bool = False
    was_truncated: bool = False
    superseded_state: Literal["CURRENT", "STALE", "NONE"] = "NONE"

    @model_validator(mode="before")
    @classmethod
    def add_context_semantics(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        payload = dict(value)
        kind = str(payload.get("kind") or "")
        authority = str(payload.get("authority_class") or "")
        role = context_role_for_item(kind, authority)
        expected_support = support_eligibility_for_item(kind, authority)
        if "context_role" in payload and str(payload["context_role"]) != role.value:
            raise ValueError(f"{kind} context role must be {role.value}")
        if "support_eligible" in payload and bool(payload["support_eligible"]) != expected_support:
            raise ValueError(f"{kind} support eligibility must be {expected_support}")
        payload["context_role"] = role.value
        payload["support_eligible"] = expected_support
        return payload


class ContextManifestExclusion(BaseModel):
    """A factual exclusion recorded by the server-side context selector."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    item_id: str = Field(min_length=1, max_length=128)
    reason: Literal[
        "DUPLICATE",
        "BUDGET",
        "EXCLUDED_BY_USER",
        "UNAUTHORIZED",
        "INVALIDATED",
        "NOT_SELECTED",
        "NOT_RELEVANT",
        "UNKNOWN",
    ]
    detail: str = Field(min_length=1, max_length=256)


class ContextManifest(BaseModel):
    """Bounded per-turn context provenance contract.

    It is intentionally persisted inside the immutable CONTEXT_RESOLVED event
    payload so historical turns can be audited without introducing another
    mutable context authority.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    context_manifest_id: UUID
    operation: Literal["ORCHESTRATOR", "PLANNER", "INTERPRETER", "DATA", "REPORT"]
    project_id: str = Field(min_length=1, max_length=64)
    research_session_id: str = Field(min_length=1, max_length=64)
    research_turn_id: UUID
    policy_version: str = Field(min_length=1, max_length=64)
    input_state: Literal["PROSPECTIVE", "ACTUAL"] = "PROSPECTIVE"
    invocation_role: str | None = Field(default=None, max_length=64)
    prompt_template_version: str | None = Field(default=None, max_length=64)
    serialized_input_version: str | None = Field(default=None, max_length=64)
    serialized_input: dict[str, Any] | None = None
    serialized_input_fingerprint: str | None = Field(
        default=None, pattern=r"^[0-9a-f]{64}$"
    )
    included_items: list[ContextManifestItem] = Field(max_length=128)
    excluded_items: list[str] = Field(default_factory=list, max_length=64)
    excluded_item_details: list[ContextManifestExclusion] = Field(
        default_factory=list, max_length=64
    )
    estimated_input_tokens: int = Field(ge=0, le=100000)
    input_budget: int = Field(ge=256, le=100000)
    reserved_output_tokens: int = Field(ge=0, le=100000)
    repair_margin: int = Field(ge=0, le=100000)
    compaction_state: Literal["NONE", "COMPACTED"] = "NONE"
    truncation_state: Literal["NONE", "TRUNCATED"] = "NONE"
    context_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    created_at: datetime
