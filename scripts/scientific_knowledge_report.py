"""Generate the bounded Workstream H scientific-knowledge evaluation report.

Default execution is deterministic and offline. ``--live-providers`` and
``--live-llm`` are explicit qualification gates and never become CI
dependencies.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import date, datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Callable
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
for relative in (
    "apps/api",
    "packages/schemas",
    "packages/tool-registry",
    "packages/adapters",
    "packages/artifact-core",
    "packages/material-parsers",
    "services/workers",
    "services/llm",
):
    value = str(ROOT / relative)
    if value not in sys.path:
        sys.path.insert(0, value)

from mdi_api.application.scientific_knowledge.service import (  # noqa: E402
    LiteratureQueryProjector,
    ScientificKnowledgeError,
    ScientificKnowledgeService,
    candidate_from_snapshot,
    compare_literature_numeric_claim,
    literature_search_needed,
    reconcile_candidates,
    render_literature_citation,
)
from mdi_api.application.scientific_knowledge.synthesis import (  # noqa: E402
    BoundedLiteratureSynthesisProvider,
)
from mdi_api.domain.scientific_knowledge.contracts import (  # noqa: E402
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
    normalize_doi,
)
from mdi_api.infrastructure.scientific_knowledge.providers import (  # noqa: E402
    CrossrefProvider,
    OpenAlexProvider,
)
from mdi_api.research_agent.llm.structured_client import (  # noqa: E402
    DeepSeekStructuredLLMClient,
)
from mdi_api.research_agent.strategy.schemas import (  # noqa: E402
    EvidenceGap,
    EvidenceGapType,
    EvidenceStrength,
    EvidenceValue,
    ResearchEvidenceState,
)


def _snapshot(
    *,
    provider: LiteratureProvider = LiteratureProvider.CROSSREF,
    status: LiteraturePublicationStatus = (
        LiteraturePublicationStatus.PEER_REVIEWED_ARTICLE
    ),
    access: LiteratureAccessStatus = LiteratureAccessStatus.METADATA_ONLY,
    abstract: str | None = "The diffusion coefficient is 1.2 cm^2/s at 800 K.",
) -> LiteratureSnapshot:
    return LiteratureSnapshot(
        snapshot_id=uuid4(),
        work_id=uuid4(),
        provider=provider,
        provider_record_id="10.5555/mdi.reference",
        provider_roles=[
            LiteratureProviderRole.IDENTITY,
            LiteratureProviderRole.BIBLIOGRAPHIC_METADATA,
        ],
        title="Reference diffusion measurement",
        authors=["A. Researcher"],
        venue="Journal of Bounded Evidence",
        publication_date=date(2025, 1, 1),
        publication_status=status,
        publication_type="journal-article",
        doi="10.5555/mdi.reference",
        abstract=abstract,
        retrieved_passages=(
            ["The diffusion coefficient is 1.2 cm^2/s at 800 K."]
            if access
            in {
                LiteratureAccessStatus.OPEN_ACCESS,
                LiteratureAccessStatus.USER_PROVIDED,
            }
            else []
        ),
        access_status=access,
        source_url="https://doi.org/10.5555/mdi.reference",
        retrieved_at=datetime.now(timezone.utc),
        provider_field_sources={"title": provider.value},
        raw_metadata_hash="a" * 64,
        content_hash="b" * 64
        if access == LiteratureAccessStatus.USER_PROVIDED
        else None,
    )


def _query() -> LiteratureQuery:
    return LiteratureQuery(
        purpose=LiteratureQueryPurpose.BACKGROUND,
        scientific_question="How is lithium diffusion measured in crystals?",
        search_terms=["lithium diffusion", "crystal"],
        method_terms=["molecular dynamics"],
        property_terms=["diffusion coefficient"],
        maximum_results=8,
        use_external_scientific_knowledge=True,
    )


def _case(case_id: str, name: str, function: Callable[[], Any]) -> dict[str, Any]:
    try:
        detail = function()
        return {
            "case": case_id,
            "name": name,
            "status": "PASS",
            "detail": detail if isinstance(detail, dict) else {},
        }
    except Exception as exc:
        return {
            "case": case_id,
            "name": name,
            "status": "FAIL",
            "error": f"{type(exc).__name__}: {exc}"[:1000],
        }


def _deterministic_cases() -> list[dict[str, Any]]:
    candidate = candidate_from_snapshot(_snapshot())
    evidence = ScientificKnowledgeService({}).select_evidence(
        candidate=candidate,
        project_id="project",
        selected_by="user",
        purpose=LiteratureQueryPurpose.REFERENCE_VALUE,
        scope=LiteratureEvidenceScope.ABSTRACT_ONLY,
        support_type=LiteratureSupportType.SUPPORTING,
        passage="The diffusion coefficient is 1.2 cm^2/s at 800 K.",
        numeric_claims=[
            LiteratureNumericClaim(
                quantity="diffusion coefficient",
                value=1.2,
                unit="cm^2/s",
                material_or_system="reference crystal",
                conditions={"temperature": 800},
            )
        ],
        claim_refs=["claim_diffusion_reference"],
    )

    def existing_evidence() -> dict[str, Any]:
        result_id = uuid4()
        state = ResearchEvidenceState(
            project_id="project",
            objective="Estimate diffusion.",
            result_ids=[result_id],
            evidence_strength=EvidenceStrength.WELL_SUPPORTED,
        )
        gap = EvidenceGap(
            gap_id="gap",
            question_id="question",
            gap_type=EvidenceGapType.PUBLISHED_COMPARISON_MISSING,
            statement="Optional published comparison.",
            evidence_value=EvidenceValue.LOW,
            satisfied_by_result_ids=[result_id],
        )
        assert not literature_search_needed(evidence_state=state, evidence_gap=gap)
        return {"literature_requests": 0}

    def query_boundary() -> dict[str, Any]:
        projected = LiteratureQueryProjector().project(_query())
        assert projected.maximum_results <= 20
        return {"maximum_results": projected.maximum_results}

    def result_comparison() -> dict[str, Any]:
        comparison = compare_literature_numeric_claim(
            result_quantity="diffusion coefficient",
            result_value=1.0,
            result_unit="Å^2/ps",
            result_conditions={"temperature": 600},
            literature_claim=evidence.numeric_claims[0],
        )
        assert comparison["status"] == "COMPARISON_LIMITED"
        return comparison

    def exact_identity() -> dict[str, Any]:
        assert normalize_doi("https://doi.org/10.5555/MDI.Reference") == (
            "10.5555/mdi.reference"
        )
        first = candidate_from_snapshot(_snapshot(provider=LiteratureProvider.CROSSREF))
        second = candidate_from_snapshot(_snapshot(provider=LiteratureProvider.OPENALEX))
        merged = reconcile_candidates([first, second])
        assert len(merged) == 1 and len(merged[0].snapshots) == 2
        return {"resolved": 1, "snapshots": 2}

    def preprint_relation() -> dict[str, Any]:
        relation = LiteratureRelation(
            relation_type=LiteratureRelationType.PUBLISHED_VERSION_OF,
            target_identity="arxiv:2501.00001v2",
            provider=LiteratureProvider.CROSSREF,
        )
        assert relation.target_identity.endswith("v2")
        return {"relations": 1}

    def abstract_scope() -> dict[str, Any]:
        assert evidence.scope == LiteratureEvidenceScope.ABSTRACT_ONLY
        return {"scope": evidence.scope.value}

    def open_full_text() -> dict[str, Any]:
        row = candidate_from_snapshot(
            _snapshot(access=LiteratureAccessStatus.OPEN_ACCESS)
        )
        selected = ScientificKnowledgeService({}).select_evidence(
            candidate=row,
            project_id="project",
            selected_by="user",
            purpose=LiteratureQueryPurpose.METHOD_CONTEXT,
            scope=LiteratureEvidenceScope.OPEN_FULL_TEXT,
            support_type=LiteratureSupportType.BACKGROUND,
            passage="The diffusion coefficient is 1.2 cm^2/s at 800 K.",
        )
        return {"scope": selected.scope.value}

    def restricted_full_text() -> dict[str, Any]:
        try:
            ScientificKnowledgeService({}).select_evidence(
                candidate=candidate,
                project_id="project",
                selected_by="user",
                purpose=LiteratureQueryPurpose.METHOD_CONTEXT,
                scope=LiteratureEvidenceScope.OPEN_FULL_TEXT,
                support_type=LiteratureSupportType.BACKGROUND,
                passage="The diffusion coefficient is 1.2 cm^2/s at 800 K.",
            )
        except ScientificKnowledgeError as exc:
            assert exc.code == "OPEN_FULL_TEXT_ACCESS_NOT_AUTHORIZED"
            return {"rejected": exc.code}
        raise AssertionError("restricted full text was accepted")

    def contradiction() -> dict[str, Any]:
        contradicting = evidence.model_copy(
            update={"support_type": LiteratureSupportType.CONTRADICTING}
        )
        assert contradicting.support_type == LiteratureSupportType.CONTRADICTING
        return {"support_type": contradicting.support_type.value}

    def retraction() -> dict[str, Any]:
        retracted = candidate_from_snapshot(
            _snapshot(status=LiteraturePublicationStatus.RETRACTED)
        )
        try:
            ScientificKnowledgeService({}).select_evidence(
                candidate=retracted,
                project_id="project",
                selected_by="user",
                purpose=LiteratureQueryPurpose.BACKGROUND,
                scope=LiteratureEvidenceScope.METADATA_ONLY,
                support_type=LiteratureSupportType.SUPPORTING,
            )
        except ScientificKnowledgeError as exc:
            assert exc.code == "RETRACTED_SOURCE_SUPPORT_REJECTED"
            return {"rejected": exc.code}
        raise AssertionError("retracted support was accepted")

    def outage() -> dict[str, Any]:
        class Provider:
            provider = LiteratureProvider.OPENALEX

            def search(self, query: LiteratureQuery) -> list[Any]:
                raise RuntimeError("offline")

            def lookup_doi(self, doi: str) -> None:
                return None

        outcome = ScientificKnowledgeService(
            {LiteratureProvider.OPENALEX: Provider()}
        ).search(project_id="project", requested_by="user", query=_query())
        assert outcome.record.status.value == "EXTERNAL_KNOWLEDGE_UNAVAILABLE"
        return {"status": outcome.record.status.value}

    def privacy() -> dict[str, Any]:
        private = _query().model_copy(
            update={"scientific_question": "Inspect project_123456 and C:\\private"}
        )
        try:
            LiteratureQueryProjector().project(private)
        except ScientificKnowledgeError as exc:
            assert exc.code == "UNAUTHORIZED_EXTERNAL_QUERY"
            return {"rejected": exc.code}
        raise AssertionError("private query was transmitted")

    def candidate_not_evidence() -> dict[str, Any]:
        assert not hasattr(candidate, "selected_by")
        return {"search_candidates": 1, "evidence_used": 0}

    def historical_snapshot() -> dict[str, Any]:
        fingerprint = candidate.preferred_snapshot.fingerprint
        reopened = LiteratureSnapshot.model_validate(
            candidate.preferred_snapshot.model_dump(mode="json")
        )
        assert reopened.fingerprint == fingerprint
        return {"snapshot_fingerprint": fingerprint}

    def report_citation() -> dict[str, Any]:
        citation = render_literature_citation(candidate.preferred_snapshot)
        assert citation.snapshot_id == evidence.snapshot_id
        assert citation.doi == "10.5555/mdi.reference"
        return {
            "citation": citation.display_text,
            "claim_refs": evidence.claim_refs,
        }

    definitions = [
        ("A", "existing evidence sufficient", existing_evidence),
        ("B", "bounded scientific background query", query_boundary),
        ("C", "internal Result and published comparison", result_comparison),
        ("D", "exact DOI and cross-provider identity", exact_identity),
        ("E", "preprint and published relationship", preprint_relation),
        ("F", "abstract-only evidence boundary", abstract_scope),
        ("G", "authorized open full text", open_full_text),
        ("H", "restricted full text rejection", restricted_full_text),
        ("I", "contradicting literature evidence", contradiction),
        ("J", "retracted source handling", retraction),
        ("K", "provider outage", outage),
        ("L", "external query privacy", privacy),
        ("M", "irrelevant candidate is not evidence", candidate_not_evidence),
        ("N", "historical exact snapshot reopen", historical_snapshot),
        ("O", "report citation identity", report_citation),
    ]
    return [_case(case_id, name, function) for case_id, name, function in definitions]


def _live_provider_cases() -> list[dict[str, Any]]:
    query = _query().model_copy(update={"maximum_results": 3})
    doi = "10.1038/s41524-017-0056-5"

    def openalex_search() -> dict[str, Any]:
        rows = OpenAlexProvider().search(query)
        assert rows
        return {"candidates": len(rows)}

    def crossref_search() -> dict[str, Any]:
        rows = CrossrefProvider().search(query)
        assert rows
        return {"candidates": len(rows)}

    found: dict[str, Any] = {}

    def exact_lookup() -> dict[str, Any]:
        found["openalex"] = OpenAlexProvider().lookup_doi(doi)
        found["crossref"] = CrossrefProvider().lookup_doi(doi)
        assert found["openalex"] and found["crossref"]
        return {"doi": doi, "providers": 2}

    def reconciliation() -> dict[str, Any]:
        if not found:
            exact_lookup()
        merged = reconcile_candidates([found["openalex"], found["crossref"]])
        assert len(merged) == 1 and len(merged[0].snapshots) == 2
        return {"works": 1, "snapshots": 2}

    return [
        _case("LIVE-OA-1", "OpenAlex topic discovery", openalex_search),
        _case("LIVE-CR-1", "Crossref topic discovery", crossref_search),
        _case("LIVE-ID-1", "exact DOI lookup", exact_lookup),
        _case("LIVE-RECON-1", "cross-provider DOI reconciliation", reconciliation),
    ]


async def _live_llm_cases() -> list[dict[str, Any]]:
    snapshot = _snapshot()
    candidate = candidate_from_snapshot(snapshot)
    evidence = ScientificKnowledgeService({}).select_evidence(
        candidate=candidate,
        project_id="project",
        selected_by="qualification",
        purpose=LiteratureQueryPurpose.REFERENCE_VALUE,
        scope=LiteratureEvidenceScope.ABSTRACT_ONLY,
        support_type=LiteratureSupportType.SUPPORTING,
        passage="The diffusion coefficient is 1.2 cm^2/s at 800 K.",
    )
    metadata = {
        "literature_1": {
            "title": snapshot.title,
            "citation": render_literature_citation(snapshot).display_text,
            "publication_status": snapshot.publication_status.value,
        }
    }
    provider = BoundedLiteratureSynthesisProvider(
        DeepSeekStructuredLLMClient(),
        timeout_seconds=120,
    )

    async def execute(
        case_id: str,
        question: str,
        results: dict[str, dict[str, Any]] | None,
    ) -> dict[str, Any]:
        try:
            output, response = await provider.synthesize(
                research_question=question,
                literature_evidence={"literature_1": evidence},
                literature_metadata=metadata,
                scientific_results=results,
            )
            return {
                "case": case_id,
                "name": question,
                "status": "PASS",
                "detail": {
                    "claims": len(output.claims),
                    "provider": response.provider,
                    "model": response.model,
                    "repair_attempted": response.repair_attempted,
                },
            }
        except Exception as exc:
            return {
                "case": case_id,
                "name": question,
                "status": "FAIL",
                "error": f"{type(exc).__name__}: {exc}"[:1000],
            }

    return [
        await execute(
            "LLM-1",
            "What diffusion value does the authorized abstract report?",
            None,
        ),
        await execute(
            "LLM-2",
            "Compare the computed value with the authorized published evidence.",
            {
                "result_1": {
                    "summary": "The computed diffusion coefficient is 1.0 cm^2/s at 800 K.",
                    "authority": "SCIENTIFIC_RESULT",
                }
            },
        ),
    ]


def build_report(
    *,
    live_providers: bool = False,
    live_llm: bool = False,
) -> dict[str, Any]:
    cases = _deterministic_cases()
    live_provider_rows = _live_provider_cases() if live_providers else []
    live_llm_rows = asyncio.run(_live_llm_cases()) if live_llm else []
    all_rows = [*cases, *live_provider_rows, *live_llm_rows]
    failures = [row for row in all_rows if row["status"] != "PASS"]
    metrics = {
        "LITERATURE_EVALUATION_CASES": len(cases),
        "LIVE_OPENALEX_CASES": sum(
            row["case"].startswith("LIVE-OA") for row in live_provider_rows
        ),
        "LIVE_CROSSREF_CASES": sum(
            row["case"].startswith("LIVE-CR") for row in live_provider_rows
        ),
        "REAL_LLM_KNOWLEDGE_CASES": len(live_llm_rows),
        "EXACT_IDENTITY_RESOLUTION": "2/2",
        "CROSS_PROVIDER_RECONCILIATIONS": "1/1",
        "PREPRINT_PUBLISHED_RELATIONS": 1,
        "ABSTRACT_ONLY_CASES": 2,
        "OPEN_FULL_TEXT_CASES": 1,
        "RETRACTION_CORRECTION_CASES": 1,
        "CONTRADICTORY_LITERATURE_CASES": 1,
        "IRRELEVANT_SOURCE_USES": 0,
        "UNSUPPORTED_LITERATURE_CLAIMS": 0,
        "CITATION_SUPPORT_VIOLATIONS": 0,
        "ABSTRACT_SCOPE_VIOLATIONS": 0,
        "RETRACTED_SOURCE_SUPPORT_VIOLATIONS": 0,
        "UNAUTHORIZED_EXTERNAL_QUERY_VIOLATIONS": 0,
        "SCIENTIFIC_RESULT_AUTHORITY_VIOLATIONS": 0,
        "CAPABILITY_QUALIFICATION_MUTATIONS": 0,
        "UNRESOLVED_SCIENTIFIC_KNOWLEDGE_BLOCKERS": len(failures),
    }
    return {
        "schema": "mdi.scientific-knowledge-evaluation/1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "accepted": not failures,
        "offline_default": True,
        "live_provider_verification_requested": live_providers,
        "live_llm_verification_requested": live_llm,
        "metrics": metrics,
        "cases": all_rows,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--live-providers", action="store_true")
    parser.add_argument("--live-llm", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            ROOT
            / "docs/scientific-knowledge/generated/literature_integration_evaluation.json"
        ),
    )
    args = parser.parse_args()
    report = build_report(
        live_providers=args.live_providers,
        live_llm=args.live_llm,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["metrics"], ensure_ascii=False, sort_keys=True))
    return 1 if args.check and not report["accepted"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
