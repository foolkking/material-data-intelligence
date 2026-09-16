from __future__ import annotations

import ast
from pathlib import Path
from uuid import uuid4

import pytest

from mdi_api.research_agent.context.manifest import build_operation_manifest
from mdi_api.research_agent.context.policy import ContextOperation
from mdi_api.research_agent.context.provenance import (
    ContextRole,
    context_role_for_item,
    support_eligibility_for_item,
)
from mdi_api.research_agent.context.schemas import ReferenceCandidate, ReferenceCandidateSource


ROOT = Path(__file__).resolve().parents[1]


def _manifest_item(*, kind: str, authority_class: str, item_id: str) -> dict:
    return {
        "item_id": item_id,
        "kind": kind,
        "authority_class": authority_class,
        "source_identity": item_id,
        "opaque_ref": item_id,
        "content": {"item_id": item_id},
    }


def test_interpretation_is_a_presentation_projection_not_scientific_result() -> None:
    manifest = build_operation_manifest(
        operation=ContextOperation.REPORT,
        project_id="project",
        research_session_id="session",
        research_turn_id=uuid4(),
        context_fingerprint="a" * 64,
        items=[
            _manifest_item(
                kind="INTERPRETATION",
                authority_class="DERIVED_SUMMARY",
                item_id="validated_interpretation",
            )
        ],
    )

    item = manifest.included_items[0]
    assert item.kind == "INTERPRETATION"
    assert item.authority_class == "DERIVED_SUMMARY"
    assert item.source_class == "PRESENTATION_PROJECTION"
    assert item.epistemic_status == "INTERPRETED"


@pytest.mark.parametrize(
    ("kind", "authority_class"),
    [
        ("INTERPRETATION", "SCIENTIFIC_RESULT"),
        ("INTERPRETATION", "SCIENTIFIC_EVIDENCE"),
        ("RESEARCH_GOAL", "SCIENTIFIC_RESULT"),
        ("SCIENTIFIC_OBJECT", "SCIENTIFIC_EVIDENCE"),
        ("SCIENTIFIC_RESULT", "SCIENTIFIC_EVIDENCE"),
    ],
)
def test_manifest_rejects_non_authoritative_context_as_scientific_evidence(
    kind: str,
    authority_class: str,
) -> None:
    with pytest.raises(ValueError):
        build_operation_manifest(
            operation=ContextOperation.REPORT,
            project_id="project",
            research_session_id="session",
            research_turn_id=uuid4(),
            context_fingerprint="b" * 64,
            items=[_manifest_item(
                kind=kind,
                authority_class=authority_class,
                item_id="invalid_authority",
            )],
        )


def test_production_runtime_does_not_import_j_evaluation_lane() -> None:
    production_roots = [ROOT / "apps", ROOT / "services", ROOT / "packages"]
    forbidden_import_fragments = (
        "scientist_evaluation",
        "reviewer_scores",
        "reviewer_assignments",
        "human_review_cases",
    )
    violations: list[str] = []
    for root in production_roots:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if any(fragment in node.value for fragment in forbidden_import_fragments):
                        violations.append(f"{path}:{node.lineno}:{node.value}")
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    rendered = ast.unparse(node)
                    if any(fragment in rendered for fragment in forbidden_import_fragments):
                        violations.append(f"{path}:{node.lineno}:{rendered}")
    assert violations == []


def test_context_roles_are_fail_closed_for_scientific_support() -> None:
    assert context_role_for_item("SCIENTIFIC_RESULT", "SCIENTIFIC_KNOWLEDGE") == ContextRole.EVIDENCE
    assert context_role_for_item("SCIENTIFIC_FINDING", "SCIENTIFIC_EVIDENCE") == ContextRole.EVIDENCE
    assert context_role_for_item("LITERATURE_EVIDENCE", "SCIENTIFIC_EVIDENCE") == ContextRole.EVIDENCE
    assert context_role_for_item("SCIENTIFIC_OBJECT", "SCIENTIFIC_DATA") == ContextRole.SUBJECT
    assert context_role_for_item("INTERPRETATION", "DERIVED_SUMMARY") == ContextRole.CONTINUITY
    assert context_role_for_item("RESEARCH_GOAL", "USER_CONSTRAINT") == ContextRole.CONSTRAINT

    assert support_eligibility_for_item("SCIENTIFIC_RESULT", "SCIENTIFIC_KNOWLEDGE") is True
    assert support_eligibility_for_item("SCIENTIFIC_FINDING", "SCIENTIFIC_EVIDENCE") is True
    assert support_eligibility_for_item("LITERATURE_EVIDENCE", "SCIENTIFIC_EVIDENCE") is True
    assert support_eligibility_for_item("INTERPRETATION", "DERIVED_SUMMARY") is False
    assert support_eligibility_for_item("MEMORY", "MEMORY") is False


def test_reference_candidates_cannot_promote_non_evidence_to_support() -> None:
    candidate = ReferenceCandidate(
        candidate_key="finding_1",
        ref_type="SCIENTIFIC_FINDING",
        finding_ref="finding-1",
        source=ReferenceCandidateSource.PREVIOUS_TURN,
        display_label="historical interpretation",
        support_eligible=True,
        semantic_summary="derived prose",
        recency_rank=1,
    )
    assert candidate.support_eligible is True

    with pytest.raises(ValueError, match="support eligibility"):
        ReferenceCandidate(
            candidate_key="obj_1",
            ref_type="SCIENTIFIC_OBJECT",
            object_ref={
                "project_id": "project",
                "object_id": uuid4(),
                "version_id": uuid4(),
                "object_type": "structure",
                "display_name": "Structure",
            },
            source=ReferenceCandidateSource.PREVIOUS_TURN,
            display_label="structure",
            support_eligible=True,
            recency_rank=1,
        )
