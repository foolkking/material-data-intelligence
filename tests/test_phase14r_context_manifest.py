from __future__ import annotations

from uuid import uuid4

from mdi_api.research_agent.schemas import ResolvedResearchContext, ScientificSelectionContext
from mdi_api.research_agent.context.schemas import ContextManifest
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.scientific_objects.schemas import ScientificObjectRef


def test_context_manifest_is_bounded_and_preserves_exact_scientific_identity() -> None:
    object_id = uuid4()
    version_id = uuid4()
    turn_id = uuid4()
    ref = ScientificObjectRef(
        object_id=object_id,
        version_id=version_id,
        project_id="project",
        object_type="structure.crystal",
        display_name="Silicon",
    )
    context = ResolvedResearchContext(
        project_id="project",
        research_session_id="session",
        active_objects=[ref],
        selection_refs=[ref],
        scientific_selections=[
            ScientificSelectionContext(
                object_ref=ref,
                viewer_id="structure.viewer",
                selection_type="SITE",
                semantic_locator={"site_id": 14},
                display_label="Site 14",
            )
        ],
        resolved_references=[],
        referenced_result_ids=[uuid4()],
        research_goal="Inspect coordination",
        user_constraints=["CrystalNN"],
        unresolved_questions=[],
        requires_clarification=False,
    )
    manifest = ResearchTurnService._build_context_manifest(
        turn_id=turn_id,
        context=context,
        context_fingerprint="a" * 64,
    )

    assert isinstance(manifest, ContextManifest)
    assert manifest.research_turn_id == turn_id
    assert manifest.project_id == "project"
    assert manifest.policy_version == "agent2.context-policy/2.0"
    assert manifest.context_fingerprint == "a" * 64
    assert manifest.included_items
    scientific_items = [
        item for item in manifest.included_items
        if item.kind in {"SCIENTIFIC_OBJECT", "SCIENTIFIC_SELECTION"}
    ]
    assert all(item.authorization_checked for item in scientific_items)
    assert all(item.exact_object_id == str(object_id) for item in scientific_items)
    assert all(item.exact_object_version_id == str(version_id) for item in scientific_items)
    assert all(len(item.content_fingerprint) == 64 for item in manifest.included_items)
    assert manifest.estimated_input_tokens == sum(item.estimated_tokens for item in manifest.included_items)
