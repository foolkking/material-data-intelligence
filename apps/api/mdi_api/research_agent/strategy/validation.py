from __future__ import annotations

from mdi_api.research_agent.strategy.schemas import (
    ProviderStrategyProposal,
    ResearchEvidenceState,
    ResearchStrategyAction,
)


class StrategyValidationError(ValueError):
    def __init__(self, codes: tuple[str, ...]) -> None:
        self.codes = codes
        super().__init__("; ".join(codes))

    def __str__(self) -> str:
        return "; ".join(self.codes)


class StrategyProposalValidator:
    """Fail closed before a provider proposal can influence execution."""

    def validate(
        self,
        *,
        proposal: ProviderStrategyProposal,
        evidence_state: ResearchEvidenceState,
        legal_requirement_ids: set[str],
        repeated_requirement_ids: set[str] | None = None,
    ) -> ProviderStrategyProposal:
        errors: list[str] = []
        repeated_requirement_ids = repeated_requirement_ids or set()
        question_ids = {item.question_id for item in evidence_state.questions}
        gap_ids = {item.gap_id for item in evidence_state.evidence_gaps}
        hypothesis_ids = {item.hypothesis_id for item in evidence_state.hypotheses}
        result_ids = set(evidence_state.result_ids)
        if proposal.current_question_id and proposal.current_question_id not in question_ids:
            errors.append("UNKNOWN_QUESTION_REF")
        if proposal.evidence_gap_id and proposal.evidence_gap_id not in gap_ids:
            errors.append("UNKNOWN_EVIDENCE_GAP_REF")
        if proposal.hypothesis_id and proposal.hypothesis_id not in hypothesis_ids:
            errors.append("UNKNOWN_HYPOTHESIS_REF")
        if not set(proposal.evidence_result_ids).issubset(result_ids):
            errors.append("UNAUTHORIZED_OR_INVENTED_RESULT_REF")
        continuing = proposal.action in {
            ResearchStrategyAction.CONTINUE_ANALYSIS,
            ResearchStrategyAction.TEST_HYPOTHESIS,
            ResearchStrategyAction.COMPARE,
        }
        if continuing and not proposal.capability_need:
            errors.append("CONTINUATION_REQUIRES_EVIDENCE_NEED")
        if (
            proposal.capability_need
            and proposal.capability_need not in legal_requirement_ids
        ):
            errors.append("UNKNOWN_CAPABILITY_NEED")
        if proposal.capability_need in repeated_requirement_ids:
            errors.append("DUPLICATE_STRATEGY_STEP")
        if proposal.action == ResearchStrategyAction.TEST_HYPOTHESIS:
            if not proposal.hypothesis_id:
                errors.append("HYPOTHESIS_TEST_REQUIRES_HYPOTHESIS")
        elif proposal.hypothesis_id:
            errors.append("HYPOTHESIS_REF_NOT_ALLOWED_FOR_ACTION")
        if errors:
            raise StrategyValidationError(tuple(sorted(set(errors))))
        return proposal


__all__ = ["StrategyProposalValidator", "StrategyValidationError"]
