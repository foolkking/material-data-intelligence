from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field

from mdi_api.access import require_project_access
from mdi_api.application.scientific_knowledge.service import (
    LiteratureQueryProjector,
    ScientificKnowledgeError,
    ScientificKnowledgeService,
    query_fingerprint,
    render_literature_citation,
)
from mdi_api.bootstrap.repository_factory import create_repository_factory
from mdi_api.domain.scientific_knowledge.contracts import (
    LiteratureEvidenceAnchor,
    LiteratureEvidenceScope,
    LiteratureNumericClaim,
    LiteratureProvider,
    LiteratureQuery,
    LiteratureQueryPurpose,
    LiteratureRelation,
    LiteratureSearchCandidate,
    LiteratureSnapshot,
    LiteratureSupportType,
    LiteratureWork,
)
from mdi_api.infrastructure.scientific_knowledge.providers import (
    CrossrefProvider,
    OpenAlexProvider,
)
from mdi_api.transport.routers.auth import CurrentUser, get_current_user


class LiteratureSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: LiteratureQuery
    research_turn_id: UUID | None = None


class LiteratureEvidenceSelectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str = Field(min_length=1, max_length=128)
    research_turn_id: UUID | None = None
    purpose: LiteratureQueryPurpose
    scope: LiteratureEvidenceScope
    support_type: LiteratureSupportType
    passage: str | None = Field(default=None, max_length=12000)
    anchor: LiteratureEvidenceAnchor | None = None
    numeric_claims: list[LiteratureNumericClaim] = Field(default_factory=list, max_length=32)
    claim_refs: list[str] = Field(default_factory=list, max_length=64)


def _service() -> ScientificKnowledgeService:
    return ScientificKnowledgeService(
        {
            LiteratureProvider.OPENALEX: OpenAlexProvider(),
            LiteratureProvider.CROSSREF: CrossrefProvider(),
        }
    )


def _error(exc: Exception) -> None:
    if isinstance(exc, ScientificKnowledgeError):
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": str(exc)},
        ) from None
    if isinstance(exc, LookupError):
        raise HTTPException(
            status_code=404,
            detail={"code": "LITERATURE_RESOURCE_NOT_FOUND", "message": str(exc)},
        ) from None


def _require_turn_scope(
    session: Any,
    *,
    project_id: str,
    turn_id: UUID | None,
) -> None:
    if turn_id is None:
        return
    turn = session.agent2.research_turns.get(turn_id)
    if str(turn["project_id"]) != project_id:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "CROSS_PROJECT_LITERATURE_SCOPE_REJECTED",
                "message": "Literature evidence may not cross Project boundaries.",
            },
        )


def _aware_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _snapshot_from_row(row: dict[str, Any]) -> LiteratureSnapshot:
    return LiteratureSnapshot(
        snapshot_id=row["id"],
        work_id=row["work_id"],
        provider=row["provider"],
        provider_record_id=row["provider_record_id"],
        provider_roles=row["provider_roles_json"],
        title=row["title"],
        authors=row["authors_json"],
        venue=row["venue"],
        publication_date=(
            row["publication_date"].date()
            if hasattr(row["publication_date"], "date")
            else row["publication_date"]
        ),
        publication_status=row["publication_status"],
        publication_type=row["publication_type"],
        doi=row["doi"],
        arxiv_id=row["arxiv_id"],
        abstract=row["abstract"],
        retrieved_passages=row["retrieved_passages_json"],
        cited_by_count=row["cited_by_count"],
        access_status=row["access_status"],
        source_url=row["source_url"],
        open_access_url=row["open_access_url"],
        license=row["license"],
        provider_updated_at=row["provider_updated_at"],
        retrieved_at=row["retrieved_at"],
        provider_field_sources=row["provider_field_sources_json"],
        raw_metadata_hash=row["raw_metadata_hash"],
        content_hash=row["content_hash"],
    )


def _candidate_from_rows(payload: dict[str, Any]) -> LiteratureSearchCandidate:
    row = payload["work"]
    work = LiteratureWork(
        work_id=row["id"],
        candidate_id=row["candidate_id"],
        canonical_key=row["canonical_key"],
        doi=row["doi"],
        arxiv_id=row["arxiv_id"],
        arxiv_version=row["arxiv_version"],
        relations=[
            LiteratureRelation.model_validate(item)
            for item in row["relations_json"] or []
        ],
    )
    return LiteratureSearchCandidate(
        candidate_id=work.candidate_id,
        work=work,
        snapshots=[_snapshot_from_row(item) for item in payload["snapshots"]],
    )


def search_scientific_literature(
    project_id: str,
    request: LiteratureSearchRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    factory = create_repository_factory()
    try:
        projected_query = LiteratureQueryProjector().project(request.query)
        fingerprint = query_fingerprint(projected_query)
        with factory.session() as session:
            require_project_access(session.connection, project_id, current_user, write=True)
            _require_turn_scope(
                session,
                project_id=project_id,
                turn_id=request.research_turn_id,
            )
            cached = session.agent2.scientific_knowledge.find_latest_search(
                project_id=project_id,
                query_fingerprint=fingerprint,
            )
            if (
                cached is not None
                and cached["status"] == "COMPLETED"
                and _aware_utc(cached["created_at"])
                >= datetime.now(timezone.utc) - timedelta(hours=24)
            ):
                candidates = [
                    _candidate_from_rows(
                        session.agent2.scientific_knowledge.get_candidate(
                            candidate_id
                        )
                    )
                    for candidate_id in cached["candidate_ids_json"]
                ]
                return jsonable_encoder(
                    {
                        "search": cached,
                        "candidates": candidates,
                        "cacheStatus": "REUSED_FRESH_PUBLIC_METADATA",
                        "evidenceAuthority": "LITERATURE_EVIDENCE",
                        "scientificResultAuthority": False,
                        "qualificationAuthority": False,
                    }
                )
        outcome = _service().search(
            project_id=project_id,
            requested_by=current_user.id,
            query=projected_query,
            research_turn_id=request.research_turn_id,
        )
        with factory.session() as session:
            for candidate in outcome.candidates:
                session.agent2.scientific_knowledge.save_candidate(
                    candidate.model_dump(mode="python")
                )
            record = outcome.record
            session.agent2.scientific_knowledge.save_search(
                {
                    "id": record.search_id,
                    "project_id": record.project_id,
                    "research_turn_id": record.research_turn_id,
                    "requested_by": record.requested_by,
                    "query_json": record.query.model_dump(mode="json"),
                    "query_fingerprint": record.query_fingerprint,
                    "status": record.status.value,
                    "candidate_ids_json": record.candidate_ids,
                    "provider_errors_json": record.provider_errors,
                    "created_at": record.created_at,
                    "completed_at": record.completed_at,
                }
            )
        return jsonable_encoder(
            {
                "search": outcome.record,
                "candidates": outcome.candidates,
                "evidenceAuthority": "LITERATURE_EVIDENCE",
                "scientificResultAuthority": False,
                "qualificationAuthority": False,
            }
        )
    except Exception as exc:
        _error(exc)
        raise


def select_scientific_literature_evidence(
    project_id: str,
    request: LiteratureEvidenceSelectionRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    factory = create_repository_factory()
    try:
        with factory.session() as session:
            require_project_access(session.connection, project_id, current_user, write=True)
            _require_turn_scope(
                session,
                project_id=project_id,
                turn_id=request.research_turn_id,
            )
            candidate = _candidate_from_rows(
                session.agent2.scientific_knowledge.get_candidate(
                    request.candidate_id
                )
            )
        evidence = _service().select_evidence(
            candidate=candidate,
            project_id=project_id,
            selected_by=current_user.id,
            purpose=request.purpose,
            scope=request.scope,
            support_type=request.support_type,
            passage=request.passage,
            anchor=request.anchor,
            numeric_claims=request.numeric_claims,
            claim_refs=request.claim_refs,
            research_turn_id=request.research_turn_id,
        )
        with factory.session() as session:
            session.agent2.scientific_knowledge.save_evidence(
                {
                    "id": evidence.evidence_id,
                    "project_id": evidence.project_id,
                    "research_turn_id": evidence.research_turn_id,
                    "work_id": evidence.work_id,
                    "snapshot_id": evidence.snapshot_id,
                    "scope": evidence.scope.value,
                    "support_type": evidence.support_type.value,
                    "purpose": evidence.purpose.value,
                    "passage": evidence.passage,
                    "anchor_json": (
                        evidence.anchor.model_dump(mode="json")
                        if evidence.anchor
                        else None
                    ),
                    "numeric_claims_json": [
                        item.model_dump(mode="json")
                        for item in evidence.numeric_claims
                    ],
                    "claim_refs_json": evidence.claim_refs,
                    "source_content_hash": evidence.source_content_hash,
                    "selected_by": evidence.selected_by,
                    "selected_at": evidence.selected_at,
                }
            )
        return jsonable_encoder(evidence)
    except Exception as exc:
        _error(exc)
        raise


def get_scientific_literature_evidence(
    evidence_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    factory = create_repository_factory()
    try:
        with factory.session() as session:
            evidence = session.agent2.scientific_knowledge.get_evidence(evidence_id)
            require_project_access(
                session.connection, str(evidence["project_id"]), current_user
            )
            snapshot = session.agent2.scientific_knowledge.get_snapshot(
                evidence["snapshot_id"]
            )
            work = session.agent2.scientific_knowledge.get_work(evidence["work_id"])
        return jsonable_encoder(
            {
                "evidence": evidence,
                "work": work,
                "snapshot": snapshot,
                "citation": render_literature_citation(_snapshot_from_row(snapshot)),
                "historicalSnapshotPreserved": True,
                "scientificResultAuthority": False,
                "qualificationAuthority": False,
            }
        )
    except Exception as exc:
        _error(exc)
        raise


def list_turn_scientific_literature(
    turn_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    factory = create_repository_factory()
    try:
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(
                session.connection, str(turn["project_id"]), current_user
            )
            rows = session.agent2.scientific_knowledge.list_evidence_for_turn(
                turn_id
            )
            enriched = []
            for row in rows:
                snapshot = _snapshot_from_row(
                    session.agent2.scientific_knowledge.get_snapshot(
                        row["snapshot_id"]
                    )
                )
                enriched.append(
                    {
                        **row,
                        "title": snapshot.title,
                        "citation": render_literature_citation(
                            snapshot
                        ).display_text,
                        "publication_status": snapshot.publication_status.value,
                        "source_url": snapshot.source_url,
                        "doi": snapshot.doi,
                        "arxiv_id": snapshot.arxiv_id,
                        "retrieved_at": snapshot.retrieved_at,
                    }
                )
        return {
            "turnId": str(turn_id),
            "literatureEvidence": jsonable_encoder(enriched),
        }
    except Exception as exc:
        _error(exc)
        raise


__all__ = [
    "get_scientific_literature_evidence",
    "list_turn_scientific_literature",
    "search_scientific_literature",
    "select_scientific_literature_evidence",
]
