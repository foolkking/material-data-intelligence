from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.research_agent.autonomy.assessment import semantic_step_signature
from mdi_api.research_agent.autonomy.policy import CapabilityAutonomyPolicy
from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES
from mdi_api.research_agent.strategy.engine import ScientificResearchStrategyEngine
from mdi_api.research_agent.strategy.schemas import (
    ResearchStrategyAction,
)


@dataclass(frozen=True)
class StrategyEvaluationCase:
    """A bounded expectation over evidence, not an overfit tool sequence."""

    case_id: str
    objective: str
    current_result: ScientificResultBundle
    completed_bundles: tuple[ScientificResultBundle, ...] = ()
    completed_capability_ids: frozenset[str] = frozenset()
    expected_actions: frozenset[ResearchStrategyAction] = frozenset()
    allowed_capabilities: frozenset[str] = frozenset()
    forbidden_capabilities: frozenset[str] = frozenset()
    expected_stop: bool = False
    expected_hypothesis: bool = False
    existing_step_signatures: frozenset[str] = frozenset()


@dataclass(frozen=True)
class StrategyEvaluationReport:
    contract_version: str
    cases: tuple[dict[str, object], ...]
    strategy_evaluation_cases: int
    passed_cases: int
    cross_family_cases: int
    hypothesis_test_cases: int
    contradiction_cases: int
    irrelevant_capability_executions: int
    redundant_executions: int
    correct_scientific_stops: int
    expected_scientific_stops: int
    hypothesis_overclaim_violations: int
    comparison_compatibility_violations: int
    qualification_policy_violations: int = 0
    unsupported_claim_violations: int = 0

    @property
    def accepted(self) -> bool:
        return (
            self.passed_cases == self.strategy_evaluation_cases
            and self.irrelevant_capability_executions == 0
            and self.redundant_executions == 0
            and self.hypothesis_overclaim_violations == 0
            and self.comparison_compatibility_violations == 0
            and self.qualification_policy_violations == 0
            and self.unsupported_claim_violations == 0
            and self.correct_scientific_stops == self.expected_scientific_stops
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "accepted": self.accepted,
            "strategy_evaluation_cases": self.strategy_evaluation_cases,
            "passed_cases": self.passed_cases,
            "cross_family_cases": self.cross_family_cases,
            "hypothesis_test_cases": self.hypothesis_test_cases,
            "contradiction_cases": self.contradiction_cases,
            "irrelevant_capability_executions": self.irrelevant_capability_executions,
            "redundant_executions": self.redundant_executions,
            "correct_scientific_stops": self.correct_scientific_stops,
            "expected_scientific_stops": self.expected_scientific_stops,
            "hypothesis_overclaim_violations": self.hypothesis_overclaim_violations,
            "comparison_compatibility_violations": (
                self.comparison_compatibility_violations
            ),
            "qualification_policy_violations": self.qualification_policy_violations,
            "unsupported_claim_violations": self.unsupported_claim_violations,
            "cases": list(self.cases),
        }


def evaluate_strategy_cases(
    cases: Iterable[StrategyEvaluationCase],
    *,
    engine: ScientificResearchStrategyEngine | None = None,
) -> StrategyEvaluationReport:
    engine = engine or ScientificResearchStrategyEngine()
    rows: list[dict[str, object]] = []
    passed = 0
    cross_family = 0
    hypothesis_cases = 0
    contradiction_cases = 0
    irrelevant = 0
    redundant = 0
    correct_stops = 0
    expected_stops = 0
    overclaims = 0
    comparison_violations = 0
    qualification_violations = 0
    terminal_actions = {
        ResearchStrategyAction.SYNTHESIZE,
        ResearchStrategyAction.NEEDS_CLARIFICATION,
        ResearchStrategyAction.CONFLICTING_EVIDENCE,
        ResearchStrategyAction.STOP_WITH_LIMITATIONS,
    }

    for case in cases:
        state, decision = engine.decide(
            objective=case.objective,
            current=case.current_result,
            completed_bundles=case.completed_bundles,
            completed_capability_ids=set(case.completed_capability_ids),
        )
        selected = decision.selected_capability_id
        violations: list[str] = []
        if case.expected_actions and decision.action not in case.expected_actions:
            violations.append("UNEXPECTED_STRATEGY_ACTION")
        if selected and case.allowed_capabilities and selected not in case.allowed_capabilities:
            violations.append("CAPABILITY_NOT_ALLOWED_FOR_CASE")
        if selected and selected in case.forbidden_capabilities:
            irrelevant += 1
            violations.append("IRRELEVANT_CAPABILITY_SELECTED")
        if selected in case.completed_capability_ids:
            redundant += 1
            violations.append("REDUNDANT_CAPABILITY_SELECTED")
        if selected and decision.capability_need in {
            item.requirement_id for item in state.evidence_gaps if item.requirement_id
        }:
            pass
        if selected and case.existing_step_signatures:
            signature = semantic_step_signature(
                capability_id=selected,
                source_version_ids=[
                    str(value) for value in state.exact_source_version_ids
                ],
                parameters={},
            )
            if signature in case.existing_step_signatures:
                violations.append("DUPLICATE_SEMANTIC_STEP")
        if selected:
            try:
                manifest = DEFAULT_AGENT2_REGISTRIES.capabilities.require(
                    selected, "1.0"
                )
                qualification = CapabilityAutonomyPolicy().qualification_snapshot(
                    manifest
                )
                if not qualification.allowed_for_autonomy:
                    qualification_violations += 1
                    violations.append(qualification.reason_code)
            except Exception:
                qualification_violations += 1
                violations.append("CAPABILITY_QUALIFICATION_UNAVAILABLE")
        stopped = decision.action in terminal_actions
        if case.expected_stop:
            expected_stops += 1
            if stopped:
                correct_stops += 1
            else:
                violations.append("EXPECTED_STOP_NOT_OBSERVED")
        if case.expected_hypothesis:
            hypothesis_cases += 1
            if decision.hypothesis is None:
                violations.append("HYPOTHESIS_NOT_GROUNDED")
            elif decision.hypothesis.status.value not in {
                "PROPOSED",
                "PARTIALLY_SUPPORTED",
                "UNRESOLVED",
            }:
                overclaims += 1
                violations.append("HYPOTHESIS_OVERCLAIM")
        if decision.action == ResearchStrategyAction.CONFLICTING_EVIDENCE:
            contradiction_cases += 1
        if selected and "." in selected and state.capability_ids:
            current_family = next(iter(state.capability_ids)).split(".", 1)[0]
            if selected.split(".", 1)[0] != current_family:
                cross_family += 1
        if not violations:
            passed += 1
        rows.append(
            {
                "case_id": case.case_id,
                "objective": case.objective,
                "action": decision.action.value,
                "selected_capability_id": selected,
                "evidence_gap": (
                    decision.evidence_gap.gap_type.value
                    if decision.evidence_gap
                    else None
                ),
                "hypothesis_id": (
                    decision.hypothesis.hypothesis_id
                    if decision.hypothesis
                    else None
                ),
                "stop": stopped,
                "reason_codes": decision.reason_codes,
                "violations": violations,
                "passed": not violations,
            }
        )

    return StrategyEvaluationReport(
        contract_version="agent2.research-strategy-evaluation/1.0",
        cases=tuple(rows),
        strategy_evaluation_cases=len(rows),
        passed_cases=passed,
        cross_family_cases=cross_family,
        hypothesis_test_cases=hypothesis_cases,
        contradiction_cases=contradiction_cases,
        irrelevant_capability_executions=irrelevant,
        redundant_executions=redundant,
        correct_scientific_stops=correct_stops,
        expected_scientific_stops=expected_stops,
        hypothesis_overclaim_violations=overclaims,
        comparison_compatibility_violations=comparison_violations,
        qualification_policy_violations=qualification_violations,
    )


__all__ = [
    "StrategyEvaluationCase",
    "StrategyEvaluationReport",
    "evaluate_strategy_cases",
]
