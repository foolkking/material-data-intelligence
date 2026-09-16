from __future__ import annotations

import asyncio
from datetime import date, datetime, timezone
import json
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import create_engine

from mdi_api.application.scientific_knowledge.service import (
    LiteratureQueryProjector,
    ScientificKnowledgeError,
    ScientificKnowledgeService,
    candidate_from_snapshot,
    candidate_from_user_document,
    compare_literature_numeric_claim,
    literature_search_needed,
    reconcile_candidates,
    render_literature_citation,
    validate_numeric_claim_grounding,
)
from mdi_api.application.scientific_knowledge.synthesis import (
    BoundedLiteratureSynthesisProvider,
    LiteratureSynthesisOutput,
    LiteratureSynthesisValidationError,
    validate_literature_synthesis,
)
from mdi_api.domain.scientific_knowledge.contracts import (
    LiteratureAccessStatus,
    LiteratureEvidenceScope,
    LiteratureNumericClaim,
    LiteratureProvider,
    LiteratureProviderRole,
    LiteraturePublicationStatus,
    LiteratureQuery,
    LiteratureQueryPurpose,
    LiteratureRelation,
    LiteratureRelationType,
    LiteratureSnapshot,
    LiteratureSupportType,
    normalize_arxiv_id,
    normalize_doi,
)
from mdi_api.infrastructure.scientific_knowledge.providers import (
    CrossrefProvider,
    OpenAlexProvider,
)
from mdi_api.db import (
    literature_evidence,
    literature_searches,
    literature_snapshots,
    literature_works,
    metadata,
)
from mdi_api.infrastructure.persistence.scientific_knowledge import (
    ScientificKnowledgeRepository,
)
from mdi_api.research_agent.strategy.evidence import literature_reference
from mdi_api.research_agent.strategy.schemas import (
    EvidenceGap,
    EvidenceGapType,
    EvidenceStrength,
    EvidenceValue,
    ResearchEvidenceState,
    ProviderStrategyProposal,
    ResearchStrategyAction,
)
from mdi_api.research_agent.strategy.validation import (
    StrategyProposalValidator,
    StrategyValidationError,
)
from mdi_api.research_agent.context.manifest import build_operation_manifest
from mdi_api.research_agent.context.policy import ContextOperation
from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.domain.scientific_reports.contracts import ReportLiteratureSource


def _snapshot(
    *,
    provider: LiteratureProvider = LiteratureProvider.CROSSREF,
    doi: str | None = "10.5555/example",
    title: str = "Diffusion in a model crystal",
    status: LiteraturePublicationStatus = LiteraturePublicationStatus.PEER_REVIEWED_ARTICLE,
    access: LiteratureAccessStatus = LiteratureAccessStatus.METADATA_ONLY,
    abstract: str | None = "The diffusion coefficient is 1.2 cm^2/s.",
) -> LiteratureSnapshot:
    return LiteratureSnapshot(
        snapshot_id=uuid4(),
        work_id=uuid4(),
        provider=provider,
        provider_record_id=doi or "arxiv:2601.00001v2",
        provider_roles=[
            LiteratureProviderRole.IDENTITY,
            LiteratureProviderRole.BIBLIOGRAPHIC_METADATA,
        ],
        title=title,
        authors=["A Researcher"],
        venue="Journal of Testable Science",
        publication_date=date(2026, 1, 1),
        publication_status=status,
        publication_type="journal-article",
        doi=doi,
        arxiv_id=None if doi else "2601.00001v2",
        abstract=abstract,
        access_status=access,
        source_url="https://doi.org/10.5555/example",
        retrieved_at=datetime.now(timezone.utc),
        provider_field_sources={"title": provider.value},
        raw_metadata_hash="a" * 64,
    )


def _query(**updates: object) -> LiteratureQuery:
    payload = {
        "purpose": LiteratureQueryPurpose.BACKGROUND,
        "scientific_question": "How is diffusion measured in crystalline materials?",
        "search_terms": ["diffusion", "crystal"],
        "method_terms": ["molecular dynamics"],
        "material_terms": ["lithium"],
        "property_terms": ["diffusion coefficient"],
        "use_external_scientific_knowledge": True,
    }
    payload.update(updates)
    return LiteratureQuery.model_validate(payload)


def test_identity_normalization_is_deterministic() -> None:
    assert normalize_doi(" DOI: https://doi.org/10.5555/EXAMPLE. ") == "10.5555/example"
    assert normalize_arxiv_id("https://arxiv.org/abs/2601.00001v2") == (
        "2601.00001",
        "v2",
    )
    with pytest.raises(ValueError):
        normalize_doi("not-a-doi")


def test_query_projector_rejects_private_context() -> None:
    query = _query(scientific_question="Inspect project_123456 and sample_abcdef")
    with pytest.raises(ScientificKnowledgeError) as error:
        LiteratureQueryProjector().project(query)
    assert error.value.code == "UNAUTHORIZED_EXTERNAL_QUERY"


def test_query_projector_allows_public_scientific_terms() -> None:
    projected = LiteratureQueryProjector().project(_query())
    assert projected.use_external_scientific_knowledge is True


def test_duplicate_provider_records_reconcile_by_doi() -> None:
    first = candidate_from_snapshot(_snapshot(provider=LiteratureProvider.CROSSREF))
    second = candidate_from_snapshot(
        _snapshot(provider=LiteratureProvider.OPENALEX)
    ).model_copy(update={"work": first.work.model_copy(update={"work_id": uuid4()})})
    merged = reconcile_candidates([first, second])
    assert len(merged) == 1
    assert len(merged[0].snapshots) == 2
    assert all(item.work_id == merged[0].work.work_id for item in merged[0].snapshots)


def test_same_title_without_strong_identity_is_not_silently_merged() -> None:
    first = candidate_from_snapshot(
        _snapshot(provider=LiteratureProvider.OPENALEX, doi=None)
    )
    second = candidate_from_snapshot(
        _snapshot(provider=LiteratureProvider.CROSSREF, doi=None).model_copy(
            update={
                "provider_record_id": "arxiv:2601.00002v1",
                "arxiv_id": "2601.00002v1",
            }
        )
    )
    merged = reconcile_candidates([first, second])
    assert len(merged) == 2


def test_abstract_only_evidence_must_be_a_retrieved_passage() -> None:
    candidate = candidate_from_snapshot(_snapshot())
    service = ScientificKnowledgeService({})
    with pytest.raises(ScientificKnowledgeError) as error:
        service.select_evidence(
            candidate=candidate,
            project_id="project",
            selected_by="user",
            purpose=LiteratureQueryPurpose.BACKGROUND,
            scope=LiteratureEvidenceScope.ABSTRACT_ONLY,
            support_type=LiteratureSupportType.SUPPORTING,
            passage="A passage not present in the abstract",
        )
    assert error.value.code == "ABSTRACT_SCOPE_VIOLATION"


def test_retracted_source_cannot_be_used_as_ordinary_support() -> None:
    candidate = candidate_from_snapshot(
        _snapshot(status=LiteraturePublicationStatus.RETRACTED)
    )
    with pytest.raises(ScientificKnowledgeError) as error:
        ScientificKnowledgeService({}).select_evidence(
            candidate=candidate,
            project_id="project",
            selected_by="user",
            purpose=LiteratureQueryPurpose.BACKGROUND,
            scope=LiteratureEvidenceScope.METADATA_ONLY,
            support_type=LiteratureSupportType.SUPPORTING,
        )
    assert error.value.code == "RETRACTED_SOURCE_SUPPORT_REJECTED"


def test_open_full_text_requires_open_access() -> None:
    candidate = candidate_from_snapshot(_snapshot())
    with pytest.raises(ScientificKnowledgeError) as error:
        ScientificKnowledgeService({}).select_evidence(
            candidate=candidate,
            project_id="project",
            selected_by="user",
            purpose=LiteratureQueryPurpose.BACKGROUND,
            scope=LiteratureEvidenceScope.OPEN_FULL_TEXT,
            support_type=LiteratureSupportType.BACKGROUND,
            passage="The diffusion coefficient is 1.2 cm^2/s.",
        )
    assert error.value.code == "OPEN_FULL_TEXT_ACCESS_NOT_AUTHORIZED"


def test_literature_numeric_comparison_discloses_condition_difference() -> None:
    result = compare_literature_numeric_claim(
        result_quantity="diffusion coefficient",
        result_value=1.0,
        result_unit="eV",
        result_conditions={"temperature": 800},
        literature_claim=LiteratureNumericClaim(
            quantity="diffusion coefficient",
            value=2.0,
            unit="meV",
            material_or_system="test",
            conditions={"temperature": 600},
        ),
    )
    assert result["status"] == "COMPARISON_LIMITED"
    assert "CONDITION_DIFFERS:temperature" in result["reasons"]


def test_search_is_bounded_and_provider_failures_are_typed() -> None:
    class FailingProvider:
        provider = LiteratureProvider.OPENALEX

        def search(self, query: LiteratureQuery) -> list:
            raise RuntimeError("offline")

        def lookup_doi(self, doi: str):
            return None

    outcome = ScientificKnowledgeService(
        {LiteratureProvider.OPENALEX: FailingProvider()}
    ).search(project_id="project", requested_by="user", query=_query())
    assert outcome.record.status.value == "EXTERNAL_KNOWLEDGE_UNAVAILABLE"
    assert outcome.record.provider_errors["OPENALEX"] == (
        "EXTERNAL_KNOWLEDGE_UNAVAILABLE"
    )
    assert outcome.record.provider_errors["CROSSREF"] == "PROVIDER_NOT_CONFIGURED"
    assert outcome.record.query.maximum_results <= 20


def test_openalex_adapter_uses_only_allowlisted_https_host() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "api.openalex.org"
        payload = {
            "results": [
                {
                    "id": "https://openalex.org/W1",
                    "display_name": "Diffusion in a model crystal",
                    "doi": "https://doi.org/10.5555/example",
                    "type": "article",
                    "publication_date": "2026-01-01",
                    "authorships": [],
                    "primary_location": {
                        "source": {"display_name": "Journal"},
                        "landing_page_url": "https://example.org/paper",
                    },
                    "open_access": {"is_oa": False},
                }
            ]
        }
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            content=json.dumps(payload).encode(),
            request=request,
        )

    candidates = OpenAlexProvider(transport=httpx.MockTransport(handler)).search(
        _query()
    )
    assert candidates[0].work.canonical_key == "doi:10.5555/example"


def test_provider_retries_rate_limit_once_with_bounded_delay(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(
                429,
                headers={
                    "content-type": "application/json",
                    "retry-after": "99",
                },
                json={"error": "rate limited"},
            )
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"results": []},
        )

    monkeypatch.setattr(
        "mdi_api.infrastructure.scientific_knowledge.providers.time.sleep",
        sleeps.append,
    )
    assert (
        OpenAlexProvider(transport=httpx.MockTransport(handler)).search(_query())
        == []
    )
    assert calls == 2
    assert sleeps == [5.0]


def test_crossref_adapter_normalizes_doi_and_relations() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = {
            "message": {
                "DOI": "10.5555/EXAMPLE",
                "title": ["Diffusion in a model crystal"],
                "type": "journal-article",
                "container-title": ["Journal"],
                "author": [{"given": "A", "family": "Researcher"}],
                "published": {"date-parts": [[2026, 1, 1]]},
                "relation": {"is-preprint-of": [{"id": "arxiv:2601.00001"}]},
            }
        }
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            content=json.dumps(payload).encode(),
            request=request,
        )

    candidate = CrossrefProvider(transport=httpx.MockTransport(handler)).lookup_doi(
        "10.5555/example"
    )
    assert candidate is not None
    assert candidate.work.doi == "10.5555/example"
    assert candidate.work.relations[0].relation_type.value == "PREPRINT_OF"


def test_persistence_reopens_exact_snapshot_without_refresh() -> None:
    engine = create_engine("sqlite://")
    metadata.create_all(
        engine,
        tables=[
            literature_works,
            literature_snapshots,
            literature_searches,
            literature_evidence,
        ],
    )
    repository = ScientificKnowledgeRepository(engine)
    candidate = candidate_from_snapshot(_snapshot())
    repository.save_candidate(candidate.model_dump(mode="python"))
    loaded = repository.get_candidate(candidate.candidate_id)
    assert loaded["work"]["canonical_key"] == "doi:10.5555/example"
    assert loaded["snapshots"][0]["raw_metadata_hash"] == "a" * 64
    assert loaded["snapshots"][0]["id"] == candidate.snapshots[0].snapshot_id


def test_literature_is_a_distinct_strategy_evidence_origin() -> None:
    candidate = candidate_from_snapshot(_snapshot())
    evidence = ScientificKnowledgeService({}).select_evidence(
        candidate=candidate,
        project_id="project",
        selected_by="user",
        purpose=LiteratureQueryPurpose.BACKGROUND,
        scope=LiteratureEvidenceScope.ABSTRACT_ONLY,
        support_type=LiteratureSupportType.BACKGROUND,
        passage="The diffusion coefficient is 1.2 cm^2/s.",
        claim_refs=["gap-literature"],
    )
    reference = literature_reference(evidence, candidate.preferred_snapshot)
    assert reference.evidence_id == evidence.evidence_id
    assert reference.publication_status == "PEER_REVIEWED_ARTICLE"


def test_existing_result_prevents_unnecessary_literature_search() -> None:
    result_id = uuid4()
    state = ResearchEvidenceState(
        project_id="project",
        objective="Estimate diffusion.",
        result_ids=[result_id],
        evidence_strength=EvidenceStrength.WELL_SUPPORTED,
    )
    gap = EvidenceGap(
        gap_id="gap-literature",
        question_id="question",
        gap_type=EvidenceGapType.PUBLISHED_COMPARISON_MISSING,
        statement="Published comparison is optional.",
        evidence_value=EvidenceValue.LOW,
        satisfied_by_result_ids=[result_id],
    )
    assert literature_search_needed(evidence_state=state, evidence_gap=gap) is False


def test_bibliography_is_rendered_from_snapshot_not_model_invention() -> None:
    snapshot = _snapshot()
    citation = render_literature_citation(snapshot)
    assert citation.doi == "10.5555/example"
    assert "Journal of Testable Science" in citation.display_text
    assert citation.snapshot_id == snapshot.snapshot_id


def test_numeric_claim_must_appear_with_unit_in_evidence_passage() -> None:
    candidate = candidate_from_snapshot(_snapshot())
    evidence = ScientificKnowledgeService({}).select_evidence(
        candidate=candidate,
        project_id="project",
        selected_by="user",
        purpose=LiteratureQueryPurpose.REFERENCE_VALUE,
        scope=LiteratureEvidenceScope.ABSTRACT_ONLY,
        support_type=LiteratureSupportType.SUPPORTING,
        passage="The diffusion coefficient is 1.2 cm^2/s.",
        numeric_claims=[
            LiteratureNumericClaim(
                quantity="diffusion coefficient",
                value=1.2,
                unit="cm^2/s",
                material_or_system="model crystal",
            )
        ],
    )
    assert validate_numeric_claim_grounding(evidence) == ()


def test_user_provided_full_text_requires_exact_content_hash() -> None:
    snapshot = _snapshot(
        provider=LiteratureProvider.USER_UPLOAD,
        access=LiteratureAccessStatus.USER_PROVIDED,
    ).model_copy(
        update={
            "provider_record_id": "upload:paper.pdf",
            "content_hash": "b" * 64,
            "retrieved_passages": ["The diffusion coefficient is 1.2 cm^2/s."],
        }
    )
    candidate = candidate_from_snapshot(snapshot)
    evidence = ScientificKnowledgeService({}).select_evidence(
        candidate=candidate,
        project_id="project",
        selected_by="user",
        purpose=LiteratureQueryPurpose.METHOD_CONTEXT,
        scope=LiteratureEvidenceScope.USER_PROVIDED_FULL_TEXT,
        support_type=LiteratureSupportType.BACKGROUND,
        passage="The diffusion coefficient is 1.2 cm^2/s.",
    )
    assert evidence.snapshot_id == candidate.preferred_snapshot.snapshot_id


def test_user_document_factory_preserves_exact_file_and_passage_identity() -> None:
    candidate = candidate_from_user_document(
        provider_record_id="file:paper-1",
        content_hash="d" * 64,
        title="Uploaded diffusion paper",
        authors=["A. Scientist"],
        parsed_passages=["A bounded parsed passage."],
    )
    snapshot = candidate.preferred_snapshot
    assert snapshot.provider == LiteratureProvider.USER_UPLOAD
    assert snapshot.content_hash == "d" * 64
    assert snapshot.retrieved_passages == ["A bounded parsed passage."]


def test_preprint_and_published_work_relation_remains_explicit() -> None:
    candidate = candidate_from_snapshot(_snapshot()).model_copy(
        update={
            "work": candidate_from_snapshot(_snapshot()).work.model_copy(
                update={
                    "relations": [
                        LiteratureRelation(
                            relation_type=LiteratureRelationType.PUBLISHED_VERSION_OF,
                            target_identity="arxiv:2601.00001v2",
                            provider=LiteratureProvider.CROSSREF,
                        )
                    ]
                }
            )
        }
    )
    assert candidate.work.relations[0].target_identity.endswith("v2")
    assert candidate.work.relations[0].relation_type.value == "PUBLISHED_VERSION_OF"


def test_literature_strategy_requires_gap_and_is_not_capability_execution() -> None:
    state = ResearchEvidenceState(
        project_id="project",
        objective="Compare with published diffusion values.",
        evidence_gaps=[
            EvidenceGap(
                gap_id="gap-literature",
                question_id="question",
                gap_type=EvidenceGapType.PUBLISHED_COMPARISON_MISSING,
                statement="Published comparison is missing.",
                evidence_value=EvidenceValue.HIGH,
            )
        ],
    )
    proposal = ProviderStrategyProposal(
        action=ResearchStrategyAction.SEARCH_LITERATURE,
        evidence_gap_id="gap-literature",
        literature_purpose="COMPARE_WITH_PUBLISHED_WORK",
        reason_codes=["PUBLISHED_COMPARISON_MISSING"],
    )
    assert (
        StrategyProposalValidator().validate(
            proposal=proposal,
            evidence_state=state,
            legal_requirement_ids=set(),
        )
        == proposal
    )
    with pytest.raises(StrategyValidationError, match="NOT_CAPABILITY"):
        StrategyProposalValidator().validate(
            proposal=proposal.model_copy(
                update={"capability_need": "trajectory.estimate_diffusion"}
            ),
            evidence_state=state,
            legal_requirement_ids={"trajectory.estimate_diffusion"},
        )


def test_literature_context_manifest_preserves_reported_non_result_authority() -> None:
    evidence_id = uuid4()
    manifest = build_operation_manifest(
        operation=ContextOperation.INTERPRETER,
        project_id="project",
        research_session_id="session",
        research_turn_id=uuid4(),
        context_fingerprint="c" * 64,
        items=[
            {
                "item_id": "literature_1",
                "kind": "LITERATURE_EVIDENCE",
                "authority_class": "SCIENTIFIC_EVIDENCE",
                "source_identity": str(evidence_id),
                "opaque_ref": "literature_1",
                "content": {
                    "scope": "ABSTRACT_ONLY",
                    "passage": "Reported diffusion is 1.2 cm^2/s.",
                },
                "selection_mode": "RETRIEVED",
            }
        ],
    )
    item = manifest.included_items[0]
    assert item.epistemic_status == "REPORTED"
    assert item.kind == "LITERATURE_EVIDENCE"
    assert item.authority_class == "SCIENTIFIC_EVIDENCE"


def test_literature_synthesis_rejects_invented_ref_and_numeric_claim() -> None:
    candidate = candidate_from_snapshot(_snapshot())
    evidence = ScientificKnowledgeService({}).select_evidence(
        candidate=candidate,
        project_id="project",
        selected_by="user",
        purpose=LiteratureQueryPurpose.REFERENCE_VALUE,
        scope=LiteratureEvidenceScope.ABSTRACT_ONLY,
        support_type=LiteratureSupportType.SUPPORTING,
        passage="The diffusion coefficient is 1.2 cm^2/s.",
    )
    output = LiteratureSynthesisOutput.model_validate(
        {
            "summary": "Published evidence is bounded.",
            "claims": [
                {
                    "claim_id": "claim_1",
                    "statement": "The value is 9.9 cm^2/s.",
                    "literature_evidence_refs": ["literature_99"],
                    "scientific_result_refs": [],
                    "epistemic_status": "REPORTED",
                    "claim_type": "DIRECT_OBSERVATION",
                    "support_status": "SUPPORTED_WITHIN_SCOPE",
                    "scope": "authorized abstract",
                    "limitations": [],
                }
            ],
            "contradictions": [],
            "limitations": [],
        }
    )
    with pytest.raises(LiteratureSynthesisValidationError) as error:
        validate_literature_synthesis(
            output,
            literature_evidence={"literature_1": evidence},
        )
    assert "INVENTED_LITERATURE_REF:claim_1" in error.value.codes
    assert "UNSUPPORTED_NUMERIC_CLAIM:claim_1" in error.value.codes


def test_literature_synthesis_allows_one_guided_repair() -> None:
    candidate = candidate_from_snapshot(_snapshot())
    evidence = ScientificKnowledgeService({}).select_evidence(
        candidate=candidate,
        project_id="project",
        selected_by="user",
        purpose=LiteratureQueryPurpose.REFERENCE_VALUE,
        scope=LiteratureEvidenceScope.ABSTRACT_ONLY,
        support_type=LiteratureSupportType.SUPPORTING,
        passage="The diffusion coefficient is 1.2 cm^2/s.",
    )

    class Provider:
        calls = 0
        inputs = []

        async def generate_structured(self, **kwargs):
            self.calls += 1
            self.inputs.append(kwargs)
            ref = "literature_99" if self.calls == 1 else "literature_1"
            return StructuredLLMResult(
                provider="fake",
                model="fake",
                parsed={
                    "summary": "Published evidence is bounded.",
                    "claims": [
                        {
                            "claim_id": "claim_1",
                            "statement": "The reported value is 1.2 cm^2/s.",
                            "literature_evidence_refs": [ref],
                            "scientific_result_refs": [],
                            "epistemic_status": "REPORTED",
                            "claim_type": "DIRECT_OBSERVATION",
                            "support_status": "SUPPORTED_WITHIN_SCOPE",
                            "scope": "authorized abstract",
                            "limitations": ["Abstract-only evidence."],
                        }
                    ],
                    "contradictions": [],
                    "limitations": ["Abstract-only evidence."],
                },
                latency_ms=1,
                repair_attempted=self.calls == 2,
                prompt_version="test",
            )

    provider = Provider()
    output, response = asyncio.run(
        BoundedLiteratureSynthesisProvider(provider).synthesize(
            research_question="What value is reported?",
            literature_evidence={"literature_1": evidence},
            literature_metadata={
                "literature_1": {
                    "title": candidate.preferred_snapshot.title,
                    "citation": render_literature_citation(
                        candidate.preferred_snapshot
                    ).display_text,
                    "publication_status": "PEER_REVIEWED_ARTICLE",
                }
            },
        )
    )
    assert output.claims[0].literature_evidence_refs == ["literature_1"]
    assert response.repair_attempted is True
    assert provider.calls == 2
    assert provider.inputs[0]["input_payload"]["constraints"][
        "authorized_numeric_tokens"
    ] == ["1.2", "2"]
    assert "remove every derived number" in provider.inputs[1]["request_context"][
        "repair"
    ]["numeric_repair"]


def test_literature_synthesis_rejects_derived_numbers_outside_claims() -> None:
    passage = "The reported values are 1.2 and 1.0 cm^2/s."
    candidate = candidate_from_snapshot(_snapshot(abstract=passage))
    evidence = ScientificKnowledgeService({}).select_evidence(
        candidate=candidate,
        project_id="project",
        selected_by="user",
        purpose=LiteratureQueryPurpose.REFERENCE_VALUE,
        scope=LiteratureEvidenceScope.ABSTRACT_ONLY,
        support_type=LiteratureSupportType.SUPPORTING,
        passage=passage,
    )
    output = LiteratureSynthesisOutput.model_validate(
        {
            "summary": "The values differ by 0.2 cm^2/s.",
            "claims": [
                {
                    "claim_id": "claim_1",
                    "statement": "The reported values are 1.2 and 1.0 cm^2/s.",
                    "literature_evidence_refs": ["literature_1"],
                    "scientific_result_refs": [],
                    "epistemic_status": "REPORTED",
                    "claim_type": "QUANTITATIVE_COMPARISON",
                    "support_status": "SUPPORTED_WITHIN_SCOPE",
                    "scope": "authorized abstract",
                    "limitations": ["The difference is 0.2 cm^2/s."],
                }
            ],
            "contradictions": ["The numeric difference is 0.2 cm^2/s."],
            "limitations": [],
        }
    )
    with pytest.raises(LiteratureSynthesisValidationError) as error:
        validate_literature_synthesis(
            output,
            literature_evidence={"literature_1": evidence},
        )
    assert "UNSUPPORTED_NUMERIC_CLAIM:summary" in error.value.codes
    assert "UNSUPPORTED_NUMERIC_CLAIM:contradiction_1" in error.value.codes
    assert (
        "UNSUPPORTED_NUMERIC_CLAIM:claim_1.limitation_1" in error.value.codes
    )


def test_report_literature_source_keeps_exact_snapshot_and_claim_link() -> None:
    candidate = candidate_from_snapshot(_snapshot())
    evidence = ScientificKnowledgeService({}).select_evidence(
        candidate=candidate,
        project_id="project",
        selected_by="user",
        purpose=LiteratureQueryPurpose.BACKGROUND,
        scope=LiteratureEvidenceScope.ABSTRACT_ONLY,
        support_type=LiteratureSupportType.BACKGROUND,
        passage="The diffusion coefficient is 1.2 cm^2/s.",
        claim_refs=["report_claim_1"],
    )
    source = ReportLiteratureSource(
        evidence_ref="literature_1",
        evidence_id=evidence.evidence_id,
        work_id=evidence.work_id,
        snapshot_id=evidence.snapshot_id,
        citation=render_literature_citation(
            candidate.preferred_snapshot
        ).display_text,
        evidence_scope=evidence.scope.value,
        support_type=evidence.support_type.value,
        publication_status=(
            candidate.preferred_snapshot.publication_status.value
        ),
        claim_refs=evidence.claim_refs,
    )
    assert source.snapshot_id == candidate.preferred_snapshot.snapshot_id
    assert source.claim_refs == ["report_claim_1"]
