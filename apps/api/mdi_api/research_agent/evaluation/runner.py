from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from pydantic import TypeAdapter, ValidationError

from mdi_api.agent2_errors import InvalidResearchTurnDecision
from mdi_api.research_agent.context.compiler import ResearchContextCompiler
from mdi_api.research_agent.context.resolver import DeterministicReferenceResolver
from mdi_api.research_agent.context.schemas import ReferenceCandidate, ResearchContextCandidateBundle
from mdi_api.research_agent.evaluation.schemas import AgentEvalCase
from mdi_api.research_agent.orchestration.schemas import (
    OrchestratorRequirementOption,
    ResearchOrchestratorInput,
    ResearchTurnDecision,
)
from mdi_api.research_agent.orchestration.validator import ResearchTurnDecisionValidator
from mdi_api.research_agent.llm.structured_client import (
    PROMPT_VERSION,
    StructuredLLMClient,
    load_research_orchestrator_prompt,
)
from mdi_api.research_agent.registry_validation import Agent2Registries
from mdi_api.research_agent.schemas import ResearchAction
from mdi_api.scientific_objects.schemas import ScientificObjectRef


_FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "phase2_p0.json"


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    passed: bool
    action: str | None
    validation_error_code: str | None
    detail: str


def load_phase2_p0_cases() -> list[AgentEvalCase]:
    payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    return TypeAdapter(list[AgentEvalCase]).validate_python(payload)


class AgentEvaluationRunner:
    """Runs schema/reference/semantic assertions without executing tools or plans."""

    def __init__(self, registries: Agent2Registries) -> None:
        self.registries = registries
        self.validator = ResearchTurnDecisionValidator(registries.requirements)
        self.compiler = ResearchContextCompiler()
        self.resolver = DeterministicReferenceResolver()

    def context_for(self, case: AgentEvalCase, *, message: str | None = None) -> tuple[ResearchContextCandidateBundle, ResearchOrchestratorInput]:
        objects = [ReferenceCandidate(
            candidate_key=item.key,
            ref_type="SCIENTIFIC_OBJECT",
            object_ref=ScientificObjectRef(
                object_id=uuid5(NAMESPACE_URL, f"{case.case_id}:{item.key}:object"),
                version_id=uuid5(NAMESPACE_URL, f"{case.case_id}:{item.key}:version"),
                project_id=item.project_id,
                object_type=item.object_type,
                display_name=item.display_name,
            ),
            source=item.source,
            display_label=item.display_name,
            semantic_summary=item.semantic_summary,
            recency_rank=0,
            stale=item.stale,
        ) for item in case.object_candidates]
        results = [ReferenceCandidate(
            candidate_key=item.key,
            ref_type="SCIENTIFIC_RESULT",
            result_id=uuid5(NAMESPACE_URL, f"{case.case_id}:{item.key}:result"),
            source="PREVIOUS_TURN_RESULT",
            display_label=item.display_name,
            semantic_summary=item.summary,
            recency_rank=0,
            stale=item.stale,
        ) for item in case.result_candidates]
        bundle = ResearchContextCandidateBundle(
            project_id="eval-project",
            research_session_id="eval-session",
            research_turn_id=uuid5(NAMESPACE_URL, f"{case.case_id}:turn"),
            active_object_candidates=objects,
            result_candidates=results,
            finding_candidates=[],
            explicit_constraints=[],
            current_research_goal=None,
            unresolved_questions=[],
            recent_messages=[],
        )
        compact = self.compiler.compile(turn={"id": bundle.research_turn_id}, candidates=bundle)
        orchestrator_input = ResearchOrchestratorInput(
            contract_version="1.0",
            user_message=message or case.message,
            research_context=compact,
            available_requirement_ids=[OrchestratorRequirementOption(
                requirement_id=item.requirement_id,
                display_name=item.display_name,
                description=item.description,
            ) for item in self.registries.requirements.list_active()],
            allowed_actions=list(ResearchAction),
        )
        return bundle, orchestrator_input

    def evaluate_fixture(self, case: AgentEvalCase) -> EvaluationResult:
        if case.expected.rejected_before_provider:
            try:
                self.context_for(case)
            except (ValidationError, ValueError):
                return EvaluationResult(case.case_id, True, None, None, "rejected before provider")
            return EvaluationResult(case.case_id, False, None, None, "unauthorized fixture was accepted")
        bundle, orchestrator_input = self.context_for(case)
        if case.expected.deterministic_clarification:
            resolution = self.resolver.resolve(bundle)
            passed = resolution.requires_clarification
            return EvaluationResult(case.case_id, passed, "CLARIFY" if passed else None, None, "deterministic ambiguity")
        try:
            decision = ResearchTurnDecision.model_validate(case.provider_decision)
            validated = self.validator.validate(
                decision=decision,
                input_context=orchestrator_input,
                candidate_bundle=bundle,
            )
        except (ValidationError, InvalidResearchTurnDecision) as exc:
            code = exc.code if isinstance(exc, InvalidResearchTurnDecision) else "ORCHESTRATOR_INVALID_OUTPUT"
            passed = code == case.expected.validation_error_code
            return EvaluationResult(case.case_id, passed, None, code, str(exc))
        return self.assert_expected(case, validated)

    async def evaluate_live(
        self,
        case: AgentEvalCase,
        client: StructuredLLMClient,
        *,
        message: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> EvaluationResult:
        if case.expected.rejected_before_provider or case.expected.validation_error_code:
            return self.evaluate_fixture(case)
        bundle, orchestrator_input = self.context_for(case, message=message)
        if case.expected.deterministic_clarification:
            return self.evaluate_fixture(case)
        first_error: Exception | None = None
        for attempt in range(2):
            try:
                result = await client.generate_structured(
                    role="research_turn_orchestrator",
                    system_prompt=load_research_orchestrator_prompt(),
                    input_payload=orchestrator_input.model_dump(mode="json"),
                    output_schema=ResearchTurnDecision.model_json_schema(),
                    timeout_seconds=timeout_seconds,
                    request_context={
                        "prompt_version": PROMPT_VERSION,
                        "repair_attempted": attempt == 1,
                        "repair": None if attempt == 0 else {
                            "validation_error": str(first_error)[:1000],
                            "legal_candidate_keys": [
                                item.candidate_key
                                for item in [
                                    *bundle.active_object_candidates,
                                    *bundle.result_candidates,
                                    *bundle.finding_candidates,
                                ]
                            ],
                            "registered_requirement_ids": [
                                item.requirement_id for item in self.registries.requirements.list_active()
                            ],
                        },
                    },
                )
                decision = ResearchTurnDecision.model_validate(result.parsed)
                validated = self.validator.validate(
                    decision=decision,
                    input_context=orchestrator_input,
                    candidate_bundle=bundle,
                )
                return self.assert_expected(case, validated)
            except (ValidationError, InvalidResearchTurnDecision, ValueError) as exc:
                first_error = exc
        return EvaluationResult(
            case.case_id,
            False,
            None,
            getattr(first_error, "code", "ORCHESTRATOR_INVALID_OUTPUT"),
            str(first_error),
        )

    @staticmethod
    def assert_expected(case: AgentEvalCase, decision: ResearchTurnDecision) -> EvaluationResult:
        expected = case.expected
        requirement_ids = [item.requirement_id for item in decision.scientific_requirements]
        constraints = {
            key: value
            for item in decision.scientific_requirements
            for key, value in item.constraints.items()
        }
        allowed_actions = set(expected.acceptable_actions or ([expected.action] if expected.action else []))
        passed = (
            decision.action in allowed_actions
            and all(key in decision.selected_scope_ref_keys for key in expected.selected_scope_ref_keys)
            and all(key in requirement_ids for key in expected.requirement_ids)
            and all(key in decision.reusable_result_ref_keys for key in expected.reusable_result_ref_keys)
            and all(constraints.get(key) == value for key, value in expected.constraint_subset.items())
            and decision.action not in expected.must_not_actions
        )
        detail = "expectation matched" if passed else (
            f"expected selected={expected.selected_scope_ref_keys}, requirements={expected.requirement_ids}, "
            f"results={expected.reusable_result_ref_keys}; actual selected={decision.selected_scope_ref_keys}, "
            f"requirements={requirement_ids}, results={decision.reusable_result_ref_keys}"
        )
        return EvaluationResult(case.case_id, passed, decision.action.value, None, detail)
