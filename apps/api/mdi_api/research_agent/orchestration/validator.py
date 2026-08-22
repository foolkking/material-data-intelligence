from __future__ import annotations

import re
from typing import Any, Callable

from jsonschema import Draft202012Validator

from mdi_api.agent2_errors import InvalidResearchTurnDecision
from mdi_api.research_agent.context.schemas import ResearchContextCandidateBundle
from mdi_api.research_agent.context.resolver import candidate_source_priority
from mdi_api.research_agent.orchestration.schemas import ResearchOrchestratorInput, ResearchTurnDecision
from mdi_api.research_agent.requirements.registry import ScientificRequirementRegistry
from mdi_api.research_agent.schemas import ResearchAction, RequirementCriticality


_PRE_RUN_RESULT_CLAIMS = re.compile(
    r"(?:结果表明|分析显示|计算得到|我发现|the result shows|analysis shows|i found|we obtained)",
    re.IGNORECASE,
)


class ResearchTurnDecisionValidator:
    def __init__(
        self,
        requirements: ScientificRequirementRegistry,
        *,
        authorization_check: Callable[[ResearchTurnDecision, ResearchContextCandidateBundle], None] | None = None,
    ) -> None:
        self.requirements = requirements
        self.authorization_check = authorization_check

    def validate(
        self,
        *,
        decision: ResearchTurnDecision,
        input_context: ResearchOrchestratorInput,
        candidate_bundle: ResearchContextCandidateBundle,
        continuation_turn_available: bool = False,
    ) -> ResearchTurnDecision:
        object_candidates = {item.candidate_key: item for item in candidate_bundle.active_object_candidates}
        result_candidates = {item.candidate_key: item for item in candidate_bundle.result_candidates}
        finding_candidates = {item.candidate_key: item for item in candidate_bundle.finding_candidates}
        legal_keys = set(object_candidates) | set(result_candidates) | set(finding_candidates)
        used_keys = set(decision.selected_scope_ref_keys) | set(decision.reusable_result_ref_keys)
        used_keys.update(key for item in decision.scientific_requirements for key in item.subject_ref_keys)
        if decision.clarification:
            used_keys.update(decision.clarification.candidate_keys)
        unknown = sorted(used_keys - legal_keys)
        if unknown:
            raise InvalidResearchTurnDecision(
                f"Unknown reference keys: {', '.join(unknown)}",
                code="ORCHESTRATOR_INVALID_REFERENCE",
            )
        if any(key not in object_candidates for key in decision.selected_scope_ref_keys):
            raise InvalidResearchTurnDecision("selected_scope_ref_keys must reference objects", code="ORCHESTRATOR_INVALID_REFERENCE")
        if any(key not in result_candidates for key in decision.reusable_result_ref_keys):
            raise InvalidResearchTurnDecision("reusable_result_ref_keys must reference results", code="ORCHESTRATOR_INVALID_REFERENCE")
        if decision.selected_scope_ref_keys and object_candidates:
            highest_priority = min(candidate_source_priority(item.source) for item in object_candidates.values())
            lower_priority = [
                key for key in decision.selected_scope_ref_keys
                if candidate_source_priority(object_candidates[key].source) > highest_priority
            ]
            if lower_priority:
                raise InvalidResearchTurnDecision(
                    f"Selected object keys violate deterministic candidate priority: {', '.join(lower_priority)}",
                    code="ORCHESTRATOR_INVALID_REFERENCE",
                )

        action = decision.action
        if action == ResearchAction.ANSWER:
            self._require(bool(decision.assistant_message), "ANSWER requires assistant_message")
            self._require(decision.clarification is None and not decision.scientific_requirements, "ANSWER cannot clarify or request analysis")
        elif action == ResearchAction.CLARIFY:
            self._require(decision.clarification is not None, "CLARIFY requires clarification")
            self._require(not decision.scientific_requirements, "CLARIFY cannot request analysis")
            self._require(decision.assistant_message in {None, decision.clarification.question}, "CLARIFY must expose one question")
        elif action == ResearchAction.ANALYZE:
            self._validate_analysis(decision)
        elif action == ResearchAction.CONTINUE_ANALYSIS:
            self._validate_analysis(decision)
            self._require(bool(decision.reusable_result_ref_keys) or continuation_turn_available, "CONTINUE_ANALYSIS requires prior result or turn")
        elif action == ResearchAction.INTERPRET_RESULT:
            self._require(bool(decision.reusable_result_ref_keys), "INTERPRET_RESULT requires an existing result")
            self._require(not decision.scientific_requirements, "INTERPRET_RESULT cannot request recomputation")
        else:
            self._require(not decision.scientific_requirements, f"{action.value} is classification-only in Phase 2")
            if action == ResearchAction.OPEN_OBJECT:
                self._require(bool(decision.selected_scope_ref_keys), "OPEN_OBJECT requires an object ref")
            if action in {ResearchAction.CREATE_REPORT, ResearchAction.UPDATE_REPORT}:
                self._require(bool(decision.reusable_result_ref_keys), f"{action.value} requires a result ref")

        for proposed in decision.scientific_requirements:
            if not self.requirements.contains(proposed.requirement_id):
                raise InvalidResearchTurnDecision(
                    f"Unknown requirement: {proposed.requirement_id}",
                    code="ORCHESTRATOR_UNKNOWN_REQUIREMENT",
                )
            manifest = self.requirements.require(proposed.requirement_id)
            if manifest.status == "DEPRECATED":
                raise InvalidResearchTurnDecision(f"Deprecated requirement: {proposed.requirement_id}")
            for key in proposed.subject_ref_keys:
                candidate = object_candidates.get(key)
                if candidate is None:
                    raise InvalidResearchTurnDecision("Requirement subject must reference an object", code="ORCHESTRATOR_INVALID_REFERENCE")
                if manifest.accepted_object_types and candidate.object_ref.object_type not in manifest.accepted_object_types:
                    raise InvalidResearchTurnDecision(
                        f"Requirement {proposed.requirement_id} is incompatible with {candidate.object_ref.object_type}",
                        code="ORCHESTRATOR_INVALID_REFERENCE",
                    )
            errors = sorted(Draft202012Validator(manifest.constraint_schema).iter_errors(proposed.constraints), key=lambda item: list(item.path))
            if errors:
                raise InvalidResearchTurnDecision(f"Invalid constraints for {proposed.requirement_id}: {errors[0].message}")
        if action in {ResearchAction.ANALYZE, ResearchAction.CONTINUE_ANALYSIS} and decision.assistant_message:
            if _PRE_RUN_RESULT_CLAIMS.search(decision.assistant_message):
                raise InvalidResearchTurnDecision("Pre-run assistant message claims an unexecuted result")
        if self.authorization_check:
            self.authorization_check(decision, candidate_bundle)
        return decision

    def _validate_analysis(self, decision: ResearchTurnDecision) -> None:
        self._require(bool(decision.research_objective), f"{decision.action.value} requires research_objective")
        self._require(bool(decision.selected_scope_ref_keys), f"{decision.action.value} requires selected scope")
        self._require(bool(decision.scientific_requirements), f"{decision.action.value} requires scientific requirements")
        self._require(
            any(item.criticality == RequirementCriticality.REQUIRED for item in decision.scientific_requirements),
            f"{decision.action.value} requires at least one REQUIRED requirement",
        )

    @staticmethod
    def _require(condition: bool, message: str) -> None:
        if not condition:
            raise InvalidResearchTurnDecision(message)
