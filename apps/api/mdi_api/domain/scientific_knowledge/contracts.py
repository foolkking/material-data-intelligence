from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


SCIENTIFIC_KNOWLEDGE_CONTRACT_VERSION = "1.0"
_DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
_ARXIV_PATTERN = re.compile(
    r"^(?:arxiv:)?(?P<id>(?:\d{4}\.\d{4,5}|[a-z-]+/\d{7}))(?P<version>v\d+)?$",
    re.IGNORECASE,
)
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


class LiteratureProvider(StrEnum):
    OPENALEX = "OPENALEX"
    CROSSREF = "CROSSREF"
    USER_UPLOAD = "USER_UPLOAD"


class LiteratureProviderRole(StrEnum):
    DISCOVERY = "DISCOVERY"
    IDENTITY = "IDENTITY"
    BIBLIOGRAPHIC_METADATA = "BIBLIOGRAPHIC_METADATA"
    PUBLICATION_RELATIONS = "PUBLICATION_RELATIONS"
    OPEN_ACCESS_LOCATION = "OPEN_ACCESS_LOCATION"
    FULL_TEXT = "FULL_TEXT"


class LiteratureQueryPurpose(StrEnum):
    BACKGROUND = "BACKGROUND"
    METHOD_CONTEXT = "METHOD_CONTEXT"
    REFERENCE_VALUE = "REFERENCE_VALUE"
    BENCHMARK = "BENCHMARK"
    COMPARE_WITH_PUBLISHED_WORK = "COMPARE_WITH_PUBLISHED_WORK"
    HYPOTHESIS_CONTEXT = "HYPOTHESIS_CONTEXT"
    CONTRADICTION_RESOLUTION = "CONTRADICTION_RESOLUTION"
    RELATED_WORK = "RELATED_WORK"


class LiteraturePublicationStatus(StrEnum):
    UNKNOWN = "UNKNOWN"
    PREPRINT = "PREPRINT"
    PEER_REVIEWED_ARTICLE = "PEER_REVIEWED_ARTICLE"
    REVIEW = "REVIEW"
    CORRECTION = "CORRECTION"
    RETRACTED = "RETRACTED"
    WITHDRAWN = "WITHDRAWN"
    EXPRESSION_OF_CONCERN = "EXPRESSION_OF_CONCERN"


class LiteratureEvidenceScope(StrEnum):
    METADATA_ONLY = "METADATA_ONLY"
    ABSTRACT_ONLY = "ABSTRACT_ONLY"
    OPEN_FULL_TEXT = "OPEN_FULL_TEXT"
    USER_PROVIDED_FULL_TEXT = "USER_PROVIDED_FULL_TEXT"
    STRUCTURED_REPOSITORY_FULL_TEXT = "STRUCTURED_REPOSITORY_FULL_TEXT"
    REFERENCE_ONLY = "REFERENCE_ONLY"


class LiteratureSupportType(StrEnum):
    MENTIONED = "MENTIONED"
    SUPPORTING = "SUPPORTING"
    CONTRADICTING = "CONTRADICTING"
    BACKGROUND = "BACKGROUND"
    MIXED = "MIXED"
    DISCUSSES_RETRACTION = "DISCUSSES_RETRACTION"


class LiteratureAccessStatus(StrEnum):
    METADATA_ONLY = "METADATA_ONLY"
    OPEN_ACCESS = "OPEN_ACCESS"
    USER_PROVIDED = "USER_PROVIDED"
    RESTRICTED = "RESTRICTED"
    UNKNOWN = "UNKNOWN"


class LiteratureRelationType(StrEnum):
    PREPRINT_OF = "PREPRINT_OF"
    PUBLISHED_VERSION_OF = "PUBLISHED_VERSION_OF"
    UPDATED_VERSION = "UPDATED_VERSION"
    CORRECTS = "CORRECTS"
    RETRACTS = "RETRACTS"
    EXPRESSION_OF_CONCERN_FOR = "EXPRESSION_OF_CONCERN_FOR"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"


class LiteratureSearchStatus(StrEnum):
    REQUESTED = "REQUESTED"
    COMPLETED = "COMPLETED"
    EXTERNAL_KNOWLEDGE_UNAVAILABLE = "EXTERNAL_KNOWLEDGE_UNAVAILABLE"
    REJECTED = "REJECTED"


def normalize_doi(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    normalized = re.sub(r"^doi:\s*", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(
        r"^https?://(?:dx\.)?doi\.org/", "", normalized, flags=re.IGNORECASE
    )
    normalized = normalized.strip().rstrip(".,;").lower()
    if not _DOI_PATTERN.fullmatch(normalized):
        raise ValueError("invalid DOI")
    return normalized


def normalize_arxiv_id(value: str | None) -> tuple[str | None, str | None]:
    if value is None:
        return None, None
    normalized = value.strip()
    normalized = re.sub(
        r"^https?://arxiv\.org/(?:abs|pdf)/", "", normalized, flags=re.IGNORECASE
    ).removesuffix(".pdf")
    match = _ARXIV_PATTERN.fullmatch(normalized)
    if match is None:
        raise ValueError("invalid arXiv identity")
    return match.group("id").lower(), (
        match.group("version").lower() if match.group("version") else None
    )


def canonical_work_key(
    *,
    doi: str | None,
    arxiv_id: str | None,
    provider: LiteratureProvider,
    provider_record_id: str,
) -> str:
    if doi:
        return f"doi:{normalize_doi(doi)}"
    if arxiv_id:
        normalized, _version = normalize_arxiv_id(arxiv_id)
        return f"arxiv:{normalized}"
    return f"{provider.value.lower()}:{provider_record_id.strip()}"


class LiteratureRelation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    relation_type: LiteratureRelationType
    target_identity: str = Field(min_length=1, max_length=512)
    provider: LiteratureProvider
    evidence_note: str | None = Field(default=None, max_length=1000)


class LiteratureWork(BaseModel):
    """Canonical scholarly-work identity; never a scientific Result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["1.0"] = SCIENTIFIC_KNOWLEDGE_CONTRACT_VERSION
    work_id: UUID
    candidate_id: str = Field(min_length=1, max_length=128)
    canonical_key: str = Field(min_length=1, max_length=512)
    doi: str | None = Field(default=None, max_length=512)
    arxiv_id: str | None = Field(default=None, max_length=128)
    arxiv_version: str | None = Field(default=None, max_length=16)
    relations: list[LiteratureRelation] = Field(default_factory=list, max_length=32)

    @field_validator("doi")
    @classmethod
    def normalize_work_doi(cls, value: str | None) -> str | None:
        return normalize_doi(value)

    @field_validator("arxiv_id")
    @classmethod
    def normalize_work_arxiv(cls, value: str | None) -> str | None:
        normalized, _version = normalize_arxiv_id(value)
        return normalized

    @model_validator(mode="after")
    def validate_identity(self) -> "LiteratureWork":
        doi = normalize_doi(self.doi)
        arxiv_id, version = normalize_arxiv_id(self.arxiv_id)
        if self.arxiv_version and version and self.arxiv_version.lower() != version:
            raise ValueError("arXiv version identity conflicts")
        if doi and self.canonical_key != f"doi:{doi}":
            raise ValueError("DOI must own canonical work identity")
        if not doi and arxiv_id and self.canonical_key != f"arxiv:{arxiv_id}":
            raise ValueError("arXiv identity must own canonical work identity")
        return self


class LiteratureSnapshot(BaseModel):
    """Immutable provider retrieval used by historical Research."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["1.0"] = SCIENTIFIC_KNOWLEDGE_CONTRACT_VERSION
    snapshot_id: UUID
    work_id: UUID
    provider: LiteratureProvider
    provider_record_id: str = Field(min_length=1, max_length=512)
    provider_roles: list[LiteratureProviderRole] = Field(min_length=1, max_length=8)
    title: str = Field(min_length=1, max_length=2000)
    authors: list[str] = Field(default_factory=list, max_length=256)
    venue: str | None = Field(default=None, max_length=1000)
    publication_date: date | None = None
    publication_status: LiteraturePublicationStatus = (
        LiteraturePublicationStatus.UNKNOWN
    )
    publication_type: str | None = Field(default=None, max_length=128)
    doi: str | None = Field(default=None, max_length=512)
    arxiv_id: str | None = Field(default=None, max_length=128)
    abstract: str | None = Field(default=None, max_length=40000)
    retrieved_passages: list[str] = Field(default_factory=list, max_length=24)
    cited_by_count: int | None = Field(default=None, ge=0)
    access_status: LiteratureAccessStatus = LiteratureAccessStatus.UNKNOWN
    source_url: str | None = Field(default=None, max_length=2000)
    open_access_url: str | None = Field(default=None, max_length=2000)
    license: str | None = Field(default=None, max_length=512)
    provider_updated_at: datetime | None = None
    retrieved_at: datetime
    provider_field_sources: dict[str, str] = Field(default_factory=dict)
    raw_metadata_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    content_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @field_validator("doi")
    @classmethod
    def validate_doi(cls, value: str | None) -> str | None:
        return normalize_doi(value)

    @field_validator("title", "venue", "abstract")
    @classmethod
    def reject_control_characters(cls, value: str | None) -> str | None:
        if value is not None and _CONTROL_CHARS.search(value):
            raise ValueError("literature metadata contains unsupported control characters")
        return value

    @field_validator("retrieved_passages")
    @classmethod
    def validate_retrieved_passages(cls, value: list[str]) -> list[str]:
        for passage in value:
            if not passage.strip() or len(passage) > 12000:
                raise ValueError("retrieved literature passage is invalid")
            if _CONTROL_CHARS.search(passage):
                raise ValueError("retrieved passage contains unsupported control characters")
        return value

    @property
    def fingerprint(self) -> str:
        payload = self.model_dump(mode="json", exclude={"snapshot_id"})
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


class LiteratureSearchCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    candidate_id: str = Field(min_length=1, max_length=128)
    work: LiteratureWork
    snapshots: list[LiteratureSnapshot] = Field(min_length=1, max_length=4)
    relevance_reason: str | None = Field(default=None, max_length=1000)
    possible_duplicate_of: list[str] = Field(default_factory=list, max_length=8)

    @property
    def preferred_snapshot(self) -> LiteratureSnapshot:
        return sorted(
            self.snapshots,
            key=lambda item: (
                item.publication_status == LiteraturePublicationStatus.RETRACTED,
                item.provider != LiteratureProvider.CROSSREF,
                -int(item.retrieved_at.timestamp()),
            ),
        )[0]


class LiteratureQuery(BaseModel):
    """Only this bounded projection may leave the project boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["1.0"] = SCIENTIFIC_KNOWLEDGE_CONTRACT_VERSION
    purpose: LiteratureQueryPurpose
    scientific_question: str = Field(min_length=1, max_length=1000)
    search_terms: list[str] = Field(min_length=1, max_length=12)
    method_terms: list[str] = Field(default_factory=list, max_length=8)
    material_terms: list[str] = Field(default_factory=list, max_length=8)
    property_terms: list[str] = Field(default_factory=list, max_length=8)
    date_from: date | None = None
    date_to: date | None = None
    maximum_results: int = Field(default=12, ge=1, le=20)
    provider_scope: list[LiteratureProvider] = Field(
        default_factory=lambda: [
            LiteratureProvider.OPENALEX,
            LiteratureProvider.CROSSREF,
        ],
        min_length=1,
        max_length=2,
    )
    use_external_scientific_knowledge: Literal[True]

    @model_validator(mode="after")
    def validate_dates_and_providers(self) -> "LiteratureQuery":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must not be after date_to")
        if LiteratureProvider.USER_UPLOAD in self.provider_scope:
            raise ValueError("user uploads are not external search providers")
        if len(set(self.provider_scope)) != len(self.provider_scope):
            raise ValueError("provider scope must be unique")
        return self


class LiteratureEvidenceAnchor(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    section: str | None = Field(default=None, max_length=512)
    page: int | None = Field(default=None, ge=1, le=100000)
    paragraph: int | None = Field(default=None, ge=1, le=100000)
    provider_locator: str | None = Field(default=None, max_length=1000)


class LiteratureNumericClaim(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    quantity: str = Field(min_length=1, max_length=256)
    value: float
    unit: str = Field(min_length=1, max_length=64)
    material_or_system: str = Field(min_length=1, max_length=512)
    method: str | None = Field(default=None, max_length=512)
    conditions: dict[str, str | float | int] = Field(default_factory=dict)


class LiteratureEvidence(BaseModel):
    """Bounded external evidence actually used in one authorized Research scope."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["1.0"] = SCIENTIFIC_KNOWLEDGE_CONTRACT_VERSION
    evidence_id: UUID
    project_id: str = Field(min_length=1, max_length=64)
    research_turn_id: UUID | None = None
    work_id: UUID
    snapshot_id: UUID
    scope: LiteratureEvidenceScope
    support_type: LiteratureSupportType
    purpose: LiteratureQueryPurpose
    passage: str | None = Field(default=None, max_length=12000)
    anchor: LiteratureEvidenceAnchor | None = None
    numeric_claims: list[LiteratureNumericClaim] = Field(
        default_factory=list, max_length=32
    )
    claim_refs: list[str] = Field(default_factory=list, max_length=64)
    source_content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    selected_by: str = Field(min_length=1, max_length=64)
    selected_at: datetime

    @model_validator(mode="after")
    def validate_scope(self) -> "LiteratureEvidence":
        passage_scopes = {
            LiteratureEvidenceScope.ABSTRACT_ONLY,
            LiteratureEvidenceScope.OPEN_FULL_TEXT,
            LiteratureEvidenceScope.USER_PROVIDED_FULL_TEXT,
            LiteratureEvidenceScope.STRUCTURED_REPOSITORY_FULL_TEXT,
        }
        if self.scope in passage_scopes and not self.passage:
            raise ValueError("passage-bearing literature scope requires passage")
        if self.scope in {
            LiteratureEvidenceScope.METADATA_ONLY,
            LiteratureEvidenceScope.REFERENCE_ONLY,
        } and (self.passage or self.numeric_claims):
            raise ValueError("metadata/reference-only evidence cannot carry passage claims")
        return self


class LiteratureClaimLink(BaseModel):
    """Machine-readable claim support; citation text alone is insufficient."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    claim_ref: str = Field(min_length=1, max_length=128)
    statement: str = Field(min_length=1, max_length=4000)
    evidence_ids: list[UUID] = Field(min_length=1, max_length=16)
    scientific_result_ids: list[UUID] = Field(default_factory=list, max_length=16)
    support_type: LiteratureSupportType
    limitations: list[str] = Field(default_factory=list, max_length=16)


class LiteratureCitation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    work_id: UUID
    snapshot_id: UUID
    authors: list[str] = Field(default_factory=list, max_length=32)
    title: str = Field(min_length=1, max_length=2000)
    venue: str | None = Field(default=None, max_length=1000)
    year: int | None = Field(default=None, ge=1000, le=9999)
    doi: str | None = Field(default=None, max_length=512)
    arxiv_id: str | None = Field(default=None, max_length=128)
    publication_status: LiteraturePublicationStatus
    display_text: str = Field(min_length=1, max_length=4000)


class LiteratureSearchRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    search_id: UUID
    project_id: str = Field(min_length=1, max_length=64)
    research_turn_id: UUID | None = None
    requested_by: str = Field(min_length=1, max_length=64)
    query: LiteratureQuery
    query_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    status: LiteratureSearchStatus
    candidate_ids: list[str] = Field(default_factory=list, max_length=20)
    provider_errors: dict[str, str] = Field(default_factory=dict)
    created_at: datetime
    completed_at: datetime | None = None


__all__ = [
    "SCIENTIFIC_KNOWLEDGE_CONTRACT_VERSION",
    "LiteratureAccessStatus",
    "LiteratureCitation",
    "LiteratureClaimLink",
    "LiteratureEvidence",
    "LiteratureEvidenceAnchor",
    "LiteratureEvidenceScope",
    "LiteratureNumericClaim",
    "LiteratureProvider",
    "LiteratureProviderRole",
    "LiteraturePublicationStatus",
    "LiteratureQuery",
    "LiteratureQueryPurpose",
    "LiteratureRelation",
    "LiteratureRelationType",
    "LiteratureSearchCandidate",
    "LiteratureSearchRecord",
    "LiteratureSearchStatus",
    "LiteratureSnapshot",
    "LiteratureSupportType",
    "LiteratureWork",
    "canonical_work_key",
    "normalize_arxiv_id",
    "normalize_doi",
]
