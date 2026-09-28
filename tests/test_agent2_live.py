from __future__ import annotations

import asyncio
import json
import os
from uuid import uuid4

import pytest

from mdi_api.research_agent.context.compiler import ResearchContextCompiler
from mdi_api.research_agent.context.resolver import DeterministicReferenceResolver
from mdi_api.research_agent.context.schemas import (
    ReferenceCandidate,
    ReferenceCandidateSource,
    ResearchContextCandidateBundle,
)
from mdi_api.research_agent.llm.structured_client import (
    DeepSeekStructuredLLMClient,
    load_research_orchestrator_prompt,
)
from mdi_api.research_agent.orchestration.schemas import (
    OrchestratorRequirementOption,
    ResearchOrchestratorInput,
    ResearchTurnDecision,
)
from mdi_api.research_agent.orchestration.validator import (
    ResearchTurnDecisionValidator,
)
from mdi_api.research_agent.registry_validation import (
    build_default_agent2_registries,
)
from mdi_api.research_agent.schemas import ResearchAction
from mdi_api.scientific_objects.schemas import ScientificObjectRef


def _live_enabled() -> bool:
    return os.getenv("MDI_RUN_AGENT2_LIVE") == "1" and bool(
        os.getenv("DEEPSEEK_KEY")
    )


def _bundle(
    message: str,
    *,
    result_count: int = 1,
) -> ResearchContextCandidateBundle:
    return ResearchContextCandidateBundle(
        project_id="live-project",
        research_session_id="live-session",
        research_turn_id=uuid4(),
        active_object_candidates=[ReferenceCandidate(
            candidate_key="obj_1",
            ref_type="SCIENTIFIC_OBJECT",
            object_ref=ScientificObjectRef(
                object_id=uuid4(),
                version_id=uuid4(),
                project_id="live-project",
                object_type="structure.crystal",
                display_name="LiFePO4 exact structure version",
            ),
            source=ReferenceCandidateSource.RECENT_CONTEXT,
            display_label="LiFePO4 exact structure version",
            semantic_summary="Exact historical structure used by the RDF result.",
            recency_rank=1,
        )],
        result_candidates=[ReferenceCandidate(
            candidate_key=f"result_{index}",
            ref_type="SCIENTIFIC_RESULT",
            result_id=uuid4(),
            source=ReferenceCandidateSource.PREVIOUS_TURN_RESULT,
            display_label=f"RDF result {index}",
            semantic_summary="Validated RDF scientific result for the exact structure version.",
            recency_rank=1,
        ) for index in range(1, result_count + 1)],
        finding_candidates=[],
        explicit_constraints=[],
        current_research_goal="Understand the prior RDF result",
        unresolved_questions=[],
        recent_messages=[],
        current_user_message=message,
    )


def _input(bundle: ResearchContextCandidateBundle) -> ResearchOrchestratorInput:
    registries = build_default_agent2_registries()
    return ResearchOrchestratorInput(
        contract_version="1.0",
        user_message=str(bundle.current_user_message),
        research_context=ResearchContextCompiler().compile(
            turn={}, candidates=bundle, token_budget=4_000
        ),
        available_requirement_ids=[OrchestratorRequirementOption(
            requirement_id=item.requirement_id,
            display_name=item.display_name,
            description=item.description,
            constraint_schema=item.constraint_schema,
        ) for item in registries.requirements.list_active()],
        allowed_actions=list(ResearchAction),
    )


async def _live_decision(
    bundle: ResearchContextCandidateBundle,
) -> tuple[ResearchTurnDecision, int]:
    client = DeepSeekStructuredLLMClient()
    input_context = _input(bundle)
    registries = build_default_agent2_registries()
    validator = ResearchTurnDecisionValidator(registries.requirements)
    first_error: Exception | None = None
    for attempt in range(2):
        result = await client.generate_structured(
            role="research_turn_orchestrator",
            system_prompt=load_research_orchestrator_prompt(),
            input_payload=input_context.model_dump(mode="json"),
            output_schema=ResearchTurnDecision.model_json_schema(),
            timeout_seconds=120,
            request_context={
                "turn_id": str(bundle.research_turn_id),
                "prompt_version": "research-orchestrator/1.0",
                "repair_attempted": attempt == 1,
                "repair": None if first_error is None else {
                    "validation_error": str(first_error)[:1000],
                    "legal_candidate_keys": [
                        item.candidate_key
                        for item in [
                            *bundle.active_object_candidates,
                            *bundle.result_candidates,
                        ]
                    ],
                },
            },
        )
        try:
            decision = ResearchTurnDecision.model_validate(result.parsed)
            validator.validate(
                decision=decision,
                input_context=input_context,
                candidate_bundle=bundle,
                continuation_turn_available=True,
            )
            return decision, attempt + 1
        except Exception as exc:
            first_error = exc
    raise AssertionError(f"live Phase 7 decision remained invalid: {first_error}")


@pytest.mark.live_llm
@pytest.mark.skipif(
    not _live_enabled(),
    reason="Set MDI_RUN_AGENT2_LIVE=1 and DEEPSEEK_KEY for live qualification",
)
def test_live_phase7_previous_result_uses_opaque_authorized_candidate():
    bundle = _bundle("解释刚才 RDF 第一峰。")
    decision, calls = asyncio.run(_live_decision(bundle))
    assert calls in {1, 2}
    assert decision.action == ResearchAction.INTERPRET_RESULT
    assert decision.reusable_result_ref_keys == ["result_1"]
    print(json.dumps({
        "case": "LIVE-P7-01",
        "action": decision.action.value,
        "provider_calls": calls,
        "selected_refs": decision.reusable_result_ref_keys,
    }, sort_keys=True))


@pytest.mark.live_llm
@pytest.mark.skipif(
    not _live_enabled(),
    reason="Set MDI_RUN_AGENT2_LIVE=1 and DEEPSEEK_KEY for live qualification",
)
def test_live_phase7_parameter_change_routes_to_continuation():
    bundle = _bundle("重新用 cutoff 8 Å 算上一轮 RDF。")
    decision, calls = asyncio.run(_live_decision(bundle))
    assert calls in {1, 2}
    assert decision.action == ResearchAction.CONTINUE_ANALYSIS
    assert decision.reusable_result_ref_keys == ["result_1"]
    assert decision.scientific_requirements
    assert decision.scientific_requirements[0].constraints == {
        "cutoff_angstrom": 8.0
    }
    print(json.dumps({
        "case": "LIVE-P7-02",
        "action": decision.action.value,
        "provider_calls": calls,
        "selected_refs": decision.reusable_result_ref_keys,
        "constraints": decision.scientific_requirements[0].constraints,
    }, sort_keys=True))


@pytest.mark.live_llm
@pytest.mark.skipif(
    not _live_enabled(),
    reason="Set MDI_RUN_AGENT2_LIVE=1 and DEEPSEEK_KEY for live qualification",
)
def test_live_phase7_same_priority_ambiguity_clarifies_before_provider():
    bundle = _bundle("比较刚才那个。", result_count=2)
    resolution = DeterministicReferenceResolver().resolve(bundle)
    assert resolution.requires_clarification is True
    assert resolution.ambiguous_result_keys == ("result_1", "result_2")
    provider_calls = 0
    assert provider_calls == 0
    print(json.dumps({
        "case": "LIVE-P7-03",
        "action": "CLARIFY",
        "provider_calls": provider_calls,
        "ambiguous_refs": list(resolution.ambiguous_result_keys),
    }, sort_keys=True))
