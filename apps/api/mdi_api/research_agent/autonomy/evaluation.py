from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.research_agent.autonomy.assessment import (
    ResearchProgressAssessor,
    semantic_step_signature,
)
from mdi_api.research_agent.autonomy.policy import CapabilityAutonomyPolicy
from mdi_api.research_agent.autonomy.schemas import AutonomyProgressOutcome
from mdi_api.research_agent.capabilities.registry import CapabilityRegistry
from mdi_api.research_agent.schemas import CapabilityManifest


@dataclass(frozen=True)
class GoldenAutonomyCase:
    """One bounded scientific-autonomy expectation.

    Cases describe required evidence and forbidden work rather than forcing an
    arbitrary tool sequence when more than one scientifically valid path exists.
    """

    case_id: str
    goal: str
    current_result: ScientificResultBundle
    completed_capability_ids: frozenset[str]
    expected_outcomes: frozenset[AutonomyProgressOutcome]
    manifests: Mapping[str, CapabilityManifest] | CapabilityRegistry
    allowed_next_capabilities: frozenset[str] = frozenset()
    forbidden_capabilities: frozenset[str] = frozenset()
    existing_result_capability_ids: frozenset[str] = frozenset()
    existing_semantic_step_signatures: frozenset[str] = frozenset()
    expected_stop: bool = False
    unsupported_claim_case: bool = False


@dataclass(frozen=True)
class AutonomyEvaluationReport:
    contract_version: str
    golden_autonomy_cases: int
    passed_cases: int
    qualified_capability_selection_violations: int
    redundant_executions: int
    loop_prevention_events: int
    correct_scientific_stops: int
    expected_scientific_stops: int
    unsupported_claim_violations: int
    cases: tuple[dict[str, object], ...] = field(default_factory=tuple)

    @property
    def accepted(self) -> bool:
        return (
            self.passed_cases == self.golden_autonomy_cases
            and self.qualified_capability_selection_violations == 0
            and self.redundant_executions == 0
            and self.unsupported_claim_violations == 0
            and self.correct_scientific_stops == self.expected_scientific_stops
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "accepted": self.accepted,
            "golden_autonomy_cases": self.golden_autonomy_cases,
            "passed_cases": self.passed_cases,
            "qualified_capability_selection_violations": (
                self.qualified_capability_selection_violations
            ),
            "redundant_executions": self.redundant_executions,
            "loop_prevention_events": self.loop_prevention_events,
            "correct_scientific_stops": self.correct_scientific_stops,
            "expected_scientific_stops": self.expected_scientific_stops,
            "unsupported_claim_violations": self.unsupported_claim_violations,
            "cases": list(self.cases),
        }


def evaluate_golden_cases(
    cases: Iterable[GoldenAutonomyCase],
    *,
    assessor: ResearchProgressAssessor | None = None,
    capability_policy: CapabilityAutonomyPolicy | None = None,
) -> AutonomyEvaluationReport:
    assessor = assessor or ResearchProgressAssessor()
    capability_policy = capability_policy or CapabilityAutonomyPolicy()
    rows: list[dict[str, object]] = []
    passed_cases = 0
    qualification_violations = 0
    redundant_executions = 0
    loop_prevention_events = 0
    correct_stops = 0
    expected_stops = 0
    unsupported_claim_violations = 0

    def resolve_manifest(
        source: Mapping[str, CapabilityManifest] | CapabilityRegistry,
        capability_id: str,
    ) -> CapabilityManifest | None:
        if isinstance(source, Mapping):
            return source.get(capability_id)
        try:
            return source.require(capability_id)
        except Exception:
            return None

    terminal_outcomes = {
        AutonomyProgressOutcome.GOAL_SATISFIED,
        AutonomyProgressOutcome.NEEDS_CLARIFICATION,
        AutonomyProgressOutcome.NO_QUALIFIED_CAPABILITY,
        AutonomyProgressOutcome.CONFLICTING_EVIDENCE,
        AutonomyProgressOutcome.BUDGET_EXHAUSTED,
        AutonomyProgressOutcome.NON_PROGRESS,
        AutonomyProgressOutcome.STOP_WITH_LIMITATIONS,
        AutonomyProgressOutcome.CANCELLED,
    }

    for case in cases:
        proposal = assessor.assess(
            objective=case.goal,
            current=case.current_result,
            completed_capability_ids=set(case.completed_capability_ids),
        )
        violations: list[str] = []
        selected = proposal.capability_id
        actual_outcome = proposal.outcome
        reason_codes = list(proposal.reason_codes)
        if selected is not None:
            signature = semantic_step_signature(
                capability_id=selected,
                source_version_ids=[
                    str(ref.version_id)
                    for ref in case.current_result.source_object_refs
                ],
                parameters=proposal.parameter_dict,
            )
            if signature in case.existing_semantic_step_signatures:
                actual_outcome = AutonomyProgressOutcome.NON_PROGRESS
                reason_codes = ["DUPLICATE_SEMANTIC_STEP_PREVENTED"]
                selected = None
        qualification: dict[str, object] | None = None

        if actual_outcome not in case.expected_outcomes:
            violations.append("UNEXPECTED_OUTCOME")
        if selected is not None:
            if (
                case.allowed_next_capabilities
                and selected not in case.allowed_next_capabilities
            ):
                violations.append("CAPABILITY_NOT_ALLOWED_FOR_CASE")
            if selected in case.forbidden_capabilities:
                violations.append("FORBIDDEN_IRRELEVANT_CAPABILITY")
            if (
                selected in case.existing_result_capability_ids
                or selected in case.completed_capability_ids
            ):
                redundant_executions += 1
                violations.append("REDUNDANT_EXECUTION")
            manifest = resolve_manifest(case.manifests, selected)
            if manifest is None:
                qualification_violations += 1
                violations.append("SELECTED_CAPABILITY_MANIFEST_MISSING")
            else:
                snapshot = capability_policy.qualification_snapshot(manifest)
                qualification = snapshot.model_dump(mode="json")
                if not snapshot.allowed_for_autonomy:
                    qualification_violations += 1
                    violations.append(snapshot.reason_code)

        stopped = actual_outcome in terminal_outcomes
        if case.expected_stop:
            expected_stops += 1
            if stopped:
                correct_stops += 1
            else:
                violations.append("EXPECTED_STOP_NOT_OBSERVED")
        if case.unsupported_claim_case and not (
            actual_outcome == AutonomyProgressOutcome.STOP_WITH_LIMITATIONS
            and "UNSUPPORTED_CAUSAL_INFERENCE" in reason_codes
        ):
            unsupported_claim_violations += 1
            violations.append("UNSUPPORTED_CLAIM_NOT_STOPPED")
        if actual_outcome == AutonomyProgressOutcome.NON_PROGRESS:
            loop_prevention_events += 1

        passed = not violations
        if passed:
            passed_cases += 1
        rows.append(
            {
                "case_id": case.case_id,
                "goal": case.goal,
                "expected_outcomes": sorted(
                    outcome.value for outcome in case.expected_outcomes
                ),
                "actual_outcome": actual_outcome.value,
                "selected_capability_id": selected,
                "qualification": qualification,
                "reason_codes": reason_codes,
                "limitations": list(proposal.limitations),
                "violations": violations,
                "passed": passed,
            }
        )

    return AutonomyEvaluationReport(
        contract_version="agent2.autonomy-evaluation/1.0",
        golden_autonomy_cases=len(rows),
        passed_cases=passed_cases,
        qualified_capability_selection_violations=qualification_violations,
        redundant_executions=redundant_executions,
        loop_prevention_events=loop_prevention_events,
        correct_scientific_stops=correct_stops,
        expected_scientific_stops=expected_stops,
        unsupported_claim_violations=unsupported_claim_violations,
        cases=tuple(rows),
    )


__all__ = [
    "AutonomyEvaluationReport",
    "GoldenAutonomyCase",
    "evaluate_golden_cases",
]
