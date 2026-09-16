from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Mapping, Sequence
from uuid import UUID, uuid4

from mdi_api.application.scientific_knowledge.ports import ScholarlyProvider
from mdi_api.domain.scientific_knowledge.contracts import (
    LiteratureCitation,
    LiteratureEvidence,
    LiteratureEvidenceAnchor,
    LiteratureEvidenceScope,
    LiteratureNumericClaim,
    LiteratureProvider,
    LiteraturePublicationStatus,
    LiteratureQuery,
    LiteratureSearchCandidate,
    LiteratureSearchRecord,
    LiteratureSearchStatus,
    LiteratureSnapshot,
    LiteratureSupportType,
    LiteratureWork,
    canonical_work_key,
    normalize_doi,
)
from mdi_api.research_agent.strategy.schemas import (
    EvidenceGap,
    EvidenceGapType,
    ResearchEvidenceState,
)


_UUID = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_WINDOWS_PATH = re.compile(r"\b[A-Za-z]:\\")
_URI = re.compile(r"\b(?:https?|file|ftp)://", re.IGNORECASE)
_PRIVATE_LABEL = re.compile(
    r"\b(?:project|dataset|sample|user|session|turn|artifact|job)[_-][A-Za-z0-9_-]{4,}\b",
    re.IGNORECASE,
)


class ScientificKnowledgeError(ValueError):
    code = "SCIENTIFIC_KNOWLEDGE_ERROR"
    status_code = 400

    def __init__(self, message: str, *, code: str | None = None, status_code: int | None = None):
        super().__init__(message)
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code


@dataclass(frozen=True)
class LiteratureSearchOutcome:
    record: LiteratureSearchRecord
    candidates: tuple[LiteratureSearchCandidate, ...]


class LiteratureQueryProjector:
    """Validate the only representation allowed to leave the Project boundary."""

    def project(self, query: LiteratureQuery) -> LiteratureQuery:
        terms = [
            query.scientific_question,
            *query.search_terms,
            *query.method_terms,
            *query.material_terms,
            *query.property_terms,
        ]
        for term in terms:
            if any(
                pattern.search(term)
                for pattern in (_UUID, _EMAIL, _WINDOWS_PATH, _URI, _PRIVATE_LABEL)
            ):
                raise ScientificKnowledgeError(
                    "External scholarly query contains private or implementation identity.",
                    code="UNAUTHORIZED_EXTERNAL_QUERY",
                )
        return query


def query_fingerprint(query: LiteratureQuery) -> str:
    payload = query.model_dump(mode="json")
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _candidate_identity(candidate: LiteratureSearchCandidate) -> str:
    return candidate.work.canonical_key


def reconcile_candidates(
    candidates: Iterable[LiteratureSearchCandidate],
) -> list[LiteratureSearchCandidate]:
    """Merge exact identities only; fuzzy title matches remain possible duplicates."""

    by_identity: dict[str, LiteratureSearchCandidate] = {}
    title_index: dict[str, str] = {}
    for candidate in candidates:
        identity = _candidate_identity(candidate)
        existing = by_identity.get(identity)
        if existing is not None:
            snapshots = {
                (item.provider.value, item.provider_record_id, item.raw_metadata_hash): item
                for item in [*existing.snapshots, *candidate.snapshots]
            }
            relations = {
                (
                    item.relation_type.value,
                    item.target_identity,
                    item.provider.value,
                ): item
                for item in [*existing.work.relations, *candidate.work.relations]
            }
            merged_work = existing.work.model_copy(
                update={"relations": list(relations.values())[:32]}
            )
            canonical_work_id = existing.work.work_id
            by_identity[identity] = existing.model_copy(
                update={
                    "work": merged_work,
                    "snapshots": [
                        item.model_copy(update={"work_id": canonical_work_id})
                        for item in list(snapshots.values())[:4]
                    ],
                }
            )
            continue
        normalized_title = re.sub(
            r"[^a-z0-9]+", " ", candidate.preferred_snapshot.title.lower()
        ).strip()
        possible: list[str] = []
        prior_identity = title_index.get(normalized_title)
        if prior_identity and prior_identity != identity:
            possible.append(prior_identity)
        title_index.setdefault(normalized_title, identity)
        by_identity[identity] = candidate.model_copy(
            update={"possible_duplicate_of": possible}
        )
    return list(by_identity.values())


class ScientificKnowledgeService:
    def __init__(
        self,
        providers: Mapping[LiteratureProvider, ScholarlyProvider],
        *,
        query_projector: LiteratureQueryProjector | None = None,
    ) -> None:
        self.providers = dict(providers)
        self.query_projector = query_projector or LiteratureQueryProjector()

    def search(
        self,
        *,
        project_id: str,
        requested_by: str,
        query: LiteratureQuery,
        research_turn_id: UUID | None = None,
    ) -> LiteratureSearchOutcome:
        outbound = self.query_projector.project(query)
        started = datetime.now(timezone.utc)
        errors: dict[str, str] = {}
        rows: list[LiteratureSearchCandidate] = []
        for provider_id in outbound.provider_scope:
            provider = self.providers.get(provider_id)
            if provider is None:
                errors[provider_id.value] = "PROVIDER_NOT_CONFIGURED"
                continue
            try:
                rows.extend(provider.search(outbound))
            except Exception:
                errors[provider_id.value] = "EXTERNAL_KNOWLEDGE_UNAVAILABLE"
        candidates = tuple(reconcile_candidates(rows)[: outbound.maximum_results])
        status = (
            LiteratureSearchStatus.COMPLETED
            if candidates or not errors
            else LiteratureSearchStatus.EXTERNAL_KNOWLEDGE_UNAVAILABLE
        )
        record = LiteratureSearchRecord(
            search_id=uuid4(),
            project_id=project_id,
            research_turn_id=research_turn_id,
            requested_by=requested_by,
            query=outbound,
            query_fingerprint=query_fingerprint(outbound),
            status=status,
            candidate_ids=[item.candidate_id for item in candidates],
            provider_errors=errors,
            created_at=started,
            completed_at=datetime.now(timezone.utc),
        )
        return LiteratureSearchOutcome(record=record, candidates=candidates)

    def exact_doi(
        self,
        doi: str,
        *,
        provider_scope: Sequence[LiteratureProvider] = (
            LiteratureProvider.OPENALEX,
            LiteratureProvider.CROSSREF,
        ),
    ) -> list[LiteratureSearchCandidate]:
        normalized = normalize_doi(doi)
        assert normalized is not None
        found: list[LiteratureSearchCandidate] = []
        for provider_id in provider_scope[:2]:
            provider = self.providers.get(provider_id)
            if provider is None:
                continue
            candidate = provider.lookup_doi(normalized)
            if candidate is not None:
                found.append(candidate)
        return reconcile_candidates(found)

    def select_evidence(
        self,
        *,
        candidate: LiteratureSearchCandidate,
        project_id: str,
        selected_by: str,
        purpose,
        scope: LiteratureEvidenceScope,
        support_type: LiteratureSupportType,
        passage: str | None = None,
        anchor: LiteratureEvidenceAnchor | None = None,
        numeric_claims: Sequence[LiteratureNumericClaim] = (),
        claim_refs: Sequence[str] = (),
        research_turn_id: UUID | None = None,
    ) -> LiteratureEvidence:
        snapshot = candidate.preferred_snapshot
        if snapshot.publication_status in {
            LiteraturePublicationStatus.RETRACTED,
            LiteraturePublicationStatus.WITHDRAWN,
        } and support_type != LiteratureSupportType.DISCUSSES_RETRACTION:
            raise ScientificKnowledgeError(
                "Retracted or withdrawn work cannot be ordinary supporting evidence.",
                code="RETRACTED_SOURCE_SUPPORT_REJECTED",
            )
        if scope == LiteratureEvidenceScope.ABSTRACT_ONLY:
            abstract = snapshot.abstract or ""
            if not passage or passage.strip() not in abstract:
                raise ScientificKnowledgeError(
                    "Abstract-only evidence must be anchored in the retrieved abstract.",
                    code="ABSTRACT_SCOPE_VIOLATION",
                )
        if scope in {
            LiteratureEvidenceScope.OPEN_FULL_TEXT,
            LiteratureEvidenceScope.STRUCTURED_REPOSITORY_FULL_TEXT,
        } and snapshot.access_status.value != "OPEN_ACCESS":
            raise ScientificKnowledgeError(
                "Open full-text evidence requires explicit open-access authority.",
                code="OPEN_FULL_TEXT_ACCESS_NOT_AUTHORIZED",
            )
        if scope in {
            LiteratureEvidenceScope.OPEN_FULL_TEXT,
            LiteratureEvidenceScope.STRUCTURED_REPOSITORY_FULL_TEXT,
            LiteratureEvidenceScope.USER_PROVIDED_FULL_TEXT,
        } and (
            not passage or passage.strip() not in snapshot.retrieved_passages
        ):
            raise ScientificKnowledgeError(
                "Full-text evidence must be an exact passage from the immutable snapshot.",
                code="FULL_TEXT_PASSAGE_NOT_RETRIEVED",
            )
        if scope == LiteratureEvidenceScope.USER_PROVIDED_FULL_TEXT and (
            snapshot.provider != LiteratureProvider.USER_UPLOAD
            or snapshot.access_status.value != "USER_PROVIDED"
            or not snapshot.content_hash
        ):
            raise ScientificKnowledgeError(
                "User-provided full text requires an exact uploaded-file snapshot.",
                code="USER_PROVIDED_SOURCE_AUTHORITY_REQUIRED",
            )
        source_text = passage or snapshot.title
        return LiteratureEvidence(
            evidence_id=uuid4(),
            project_id=project_id,
            research_turn_id=research_turn_id,
            work_id=candidate.work.work_id,
            snapshot_id=snapshot.snapshot_id,
            scope=scope,
            support_type=support_type,
            purpose=purpose,
            passage=passage,
            anchor=anchor,
            numeric_claims=list(numeric_claims),
            claim_refs=list(claim_refs),
            source_content_hash=hashlib.sha256(source_text.encode()).hexdigest(),
            selected_by=selected_by,
            selected_at=datetime.now(timezone.utc),
        )


_UNIT_SCALE: dict[str, tuple[str, float]] = {
    "ev": ("energy", 1.0),
    "mev": ("energy", 1e-3),
    "å": ("length", 1.0),
    "angstrom": ("length", 1.0),
    "nm": ("length", 10.0),
    "ps": ("time", 1.0),
    "fs": ("time", 1e-3),
    "k": ("temperature", 1.0),
    # Diffusion base unit is Å²/ps:
    # 1 cm²/s = (10^8 Å)² / (10^12 ps) = 10^4 Å²/ps.
    "å^2/ps": ("diffusion", 1.0),
    "å²/ps": ("diffusion", 1.0),
    "angstrom^2/ps": ("diffusion", 1.0),
    "cm^2/s": ("diffusion", 1e4),
    "cm²/s": ("diffusion", 1e4),
    "m^2/s": ("diffusion", 1e8),
    "m²/s": ("diffusion", 1e8),
}


def compare_literature_numeric_claim(
    *,
    result_quantity: str,
    result_value: float,
    result_unit: str,
    result_conditions: Mapping[str, str | float | int],
    literature_claim: LiteratureNumericClaim,
) -> dict[str, object]:
    if result_quantity.strip().lower() != literature_claim.quantity.strip().lower():
        return {"status": "COMPARISON_NOT_SUPPORTED", "reasons": ["QUANTITY_DIFFERS"]}
    left = _UNIT_SCALE.get(result_unit.strip().lower())
    right = _UNIT_SCALE.get(literature_claim.unit.strip().lower())
    if left is None or right is None or left[0] != right[0]:
        return {"status": "COMPARISON_NOT_SUPPORTED", "reasons": ["UNIT_SEMANTICS_DIFFER"]}
    reasons: list[str] = []
    for key in sorted(set(result_conditions) | set(literature_claim.conditions)):
        if key not in result_conditions or key not in literature_claim.conditions:
            reasons.append(f"CONDITION_MISSING:{key}")
        elif result_conditions[key] != literature_claim.conditions[key]:
            reasons.append(f"CONDITION_DIFFERS:{key}")
    left_value = float(result_value) * left[1]
    right_value = float(literature_claim.value) * right[1]
    if not math.isfinite(left_value) or not math.isfinite(right_value):
        return {"status": "COMPARISON_NOT_SUPPORTED", "reasons": ["NON_FINITE_VALUE"]}
    return {
        "status": "COMPARISON_LIMITED" if reasons else "COMPARABLE",
        "reasons": reasons or ["QUANTITY_UNIT_AND_CONDITIONS_COMPATIBLE"],
        "normalized_result_value": left_value,
        "normalized_literature_value": right_value,
        "normalized_dimension": left[0],
    }


def render_literature_citation(snapshot: LiteratureSnapshot) -> LiteratureCitation:
    author_text = ", ".join(snapshot.authors[:3])
    if len(snapshot.authors) > 3:
        author_text = f"{author_text}, et al."
    year = snapshot.publication_date.year if snapshot.publication_date else None
    identity = (
        f"doi:{snapshot.doi}"
        if snapshot.doi
        else f"arXiv:{snapshot.arxiv_id}"
        if snapshot.arxiv_id
        else snapshot.provider_record_id
    )
    parts = [
        author_text or "Unknown authors",
        f"({year})" if year else "(date unavailable)",
        snapshot.title,
    ]
    if snapshot.venue:
        parts.append(snapshot.venue)
    parts.append(identity)
    return LiteratureCitation(
        work_id=snapshot.work_id,
        snapshot_id=snapshot.snapshot_id,
        authors=snapshot.authors[:32],
        title=snapshot.title,
        venue=snapshot.venue,
        year=year,
        doi=snapshot.doi,
        arxiv_id=snapshot.arxiv_id,
        publication_status=snapshot.publication_status,
        display_text=". ".join(parts),
    )


def validate_numeric_claim_grounding(
    evidence: LiteratureEvidence,
) -> tuple[str, ...]:
    if not evidence.numeric_claims:
        return ()
    passage = (evidence.passage or "").lower()
    errors: list[str] = []
    for index, claim in enumerate(evidence.numeric_claims, start=1):
        value_forms = {str(claim.value).lower(), f"{claim.value:g}".lower()}
        if not any(value in passage for value in value_forms):
            errors.append(f"NUMERIC_VALUE_NOT_IN_EVIDENCE:{index}")
        if claim.unit.lower() not in passage:
            errors.append(f"NUMERIC_UNIT_NOT_IN_EVIDENCE:{index}")
    return tuple(errors)


def candidate_from_snapshot(snapshot: LiteratureSnapshot) -> LiteratureSearchCandidate:
    work_id = uuid4()
    key = canonical_work_key(
        doi=snapshot.doi,
        arxiv_id=snapshot.arxiv_id,
        provider=snapshot.provider,
        provider_record_id=snapshot.provider_record_id,
    )
    work = LiteratureWork(
        work_id=work_id,
        candidate_id=hashlib.sha256(key.encode()).hexdigest()[:24],
        canonical_key=key,
        doi=snapshot.doi,
        arxiv_id=snapshot.arxiv_id,
    )
    rebound = snapshot.model_copy(update={"work_id": work_id})
    return LiteratureSearchCandidate(
        candidate_id=work.candidate_id,
        work=work,
        snapshots=[rebound],
    )


def candidate_from_user_document(
    *,
    provider_record_id: str,
    content_hash: str,
    title: str,
    parsed_passages: Sequence[str],
    authors: Sequence[str] = (),
    doi: str | None = None,
    arxiv_id: str | None = None,
) -> LiteratureSearchCandidate:
    """Create exact user-provided authority from an already authorized parser."""

    snapshot = LiteratureSnapshot(
        snapshot_id=uuid4(),
        work_id=uuid4(),
        provider=LiteratureProvider.USER_UPLOAD,
        provider_record_id=provider_record_id,
        provider_roles=[
            "IDENTITY",
            "BIBLIOGRAPHIC_METADATA",
            "FULL_TEXT",
        ],
        title=title,
        authors=list(authors)[:256],
        publication_status=LiteraturePublicationStatus.UNKNOWN,
        doi=doi,
        arxiv_id=arxiv_id,
        retrieved_passages=list(parsed_passages)[:24],
        access_status="USER_PROVIDED",
        retrieved_at=datetime.now(timezone.utc),
        provider_field_sources={
            "title": "USER_UPLOAD",
            "authors": "USER_UPLOAD",
            "retrieved_passages": "USER_UPLOAD",
        },
        raw_metadata_hash=hashlib.sha256(
            json.dumps(
                {
                    "provider_record_id": provider_record_id,
                    "title": title,
                    "authors": list(authors),
                    "doi": doi,
                    "arxiv_id": arxiv_id,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest(),
        content_hash=content_hash,
    )
    return candidate_from_snapshot(snapshot)


def literature_search_needed(
    *,
    evidence_state: ResearchEvidenceState,
    evidence_gap: EvidenceGap,
) -> bool:
    """Existing authoritative evidence wins over new external retrieval."""

    if evidence_gap.satisfied_by_result_ids:
        return False
    if evidence_state.literature_evidence_ids:
        linked_claims = {
            claim_ref
            for item in evidence_state.literature_evidence
            for claim_ref in item.claim_refs
        }
        if evidence_gap.gap_id in linked_claims:
            return False
    return evidence_gap.gap_type in {
        EvidenceGapType.LITERATURE_CONTEXT_MISSING,
        EvidenceGapType.PUBLISHED_COMPARISON_MISSING,
        EvidenceGapType.REFERENCE_BASELINE_MISSING,
        EvidenceGapType.METHOD_LIMITATION,
    }


__all__ = [
    "LiteratureQueryProjector",
    "LiteratureSearchOutcome",
    "ScientificKnowledgeError",
    "ScientificKnowledgeService",
    "candidate_from_snapshot",
    "candidate_from_user_document",
    "compare_literature_numeric_claim",
    "query_fingerprint",
    "reconcile_candidates",
    "literature_search_needed",
    "render_literature_citation",
    "validate_numeric_claim_grounding",
]
