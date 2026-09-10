from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Iterable

from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.research_agent.autonomy.schemas import AutonomyProgressOutcome
from mdi_api.research_agent.strategy.engine import ScientificResearchStrategyEngine
from mdi_api.research_agent.strategy.schemas import (
    ResearchStrategyAction,
    ResearchStrategyDecision,
    ResearchStrategySummary,
)


@dataclass(frozen=True)
class ProposedAutonomyStep:
    outcome: AutonomyProgressOutcome
    reason_codes: tuple[str, ...]
    capability_id: str | None = None
    requirement_id: str | None = None
    parameters: tuple[tuple[str, float], ...] = ()
    limitations: tuple[str, ...] = ()
    strategy_decision: ResearchStrategyDecision | None = None
    strategy_summary: ResearchStrategySummary | None = None

    @property
    def parameter_dict(self) -> dict[str, float]:
        return dict(self.parameters)


def semantic_step_signature(
    *,
    capability_id: str,
    source_version_ids: Iterable[str],
    parameters: dict | None = None,
) -> str:
    payload = {
        "capability_id": capability_id,
        "source_version_ids": sorted({str(value) for value in source_version_ids}),
        "parameters": parameters or {},
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


class ResearchProgressAssessor:
    """Compatibility entry point over bounded scientific strategy.

    The assessor chooses only a scientific need. Registry eligibility,
    qualification, authorization, binding, and execution remain separate
    deterministic authorities.
    """

    _DIFFUSION_TERMS = ("diffusion", "transport", "扩散", "输运", "传输")
    _DATA_PATTERN_TERMS = (
        "error",
        "poor",
        "pattern",
        "composition",
        "chemistry",
        "误差",
        "表现差",
        "模式",
        "组成",
        "化学",
    )
    _LOCAL_ENV_TERMS = (
        "local environment",
        "coordination",
        "局域",
        "配位",
    )
    _CAUSAL_TERMS = ("prove", "causes", "causal", "证明", "导致", "因果")

    def __init__(
        self,
        strategy_engine: ScientificResearchStrategyEngine | None = None,
    ) -> None:
        self.strategy_engine = strategy_engine or ScientificResearchStrategyEngine()

    @staticmethod
    def _numeric_fact(
        current: ScientificResultBundle, predicate: str
    ) -> float | None:
        values = [
            fact.value
            for fact in current.facts
            if fact.predicate == predicate
            and isinstance(fact.value, (int, float))
            and not isinstance(fact.value, bool)
            and math.isfinite(float(fact.value))
        ]
        if len(values) != 1:
            return None
        return float(values[0])

    def _diffusion_parameters(
        self, current: ScientificResultBundle
    ) -> tuple[dict[str, float] | None, ProposedAutonomyStep | None]:
        start = self._numeric_fact(current, "trajectory.msd_first_lag_time")
        end = self._numeric_fact(current, "trajectory.msd_last_lag_time")
        lag_count = self._numeric_fact(current, "trajectory.msd_lag_count")
        if start is None or end is None:
            return None, ProposedAutonomyStep(
                outcome=AutonomyProgressOutcome.NEEDS_CLARIFICATION,
                reason_codes=("AUTHORITATIVE_DIFFUSION_FIT_WINDOW_UNAVAILABLE",),
                limitations=(
                    "Diffusion requires an explicit fit interval grounded in the "
                    "persisted MSD Result; no interval was guessed.",
                ),
            )
        if start < 0 or start >= end:
            return None, ProposedAutonomyStep(
                outcome=AutonomyProgressOutcome.STOP_WITH_LIMITATIONS,
                reason_codes=("INVALID_PERSISTED_MSD_LAG_RANGE",),
                limitations=(
                    "The persisted MSD lag-time boundaries do not define a valid "
                    "diffusion fit interval.",
                ),
            )
        if lag_count is not None and lag_count < 5:
            return None, ProposedAutonomyStep(
                outcome=AutonomyProgressOutcome.STOP_WITH_LIMITATIONS,
                reason_codes=("INSUFFICIENT_MSD_POINTS_FOR_DIFFUSION_FIT",),
                limitations=(
                    "The persisted MSD Result contains fewer than five lag points, "
                    "so autonomous diffusion fitting was not attempted.",
                ),
            )
        return {
            "fit_start_time_ps": start,
            "fit_end_time_ps": end,
        }, None

    def assess(
        self,
        *,
        objective: str,
        current: ScientificResultBundle,
        completed_capability_ids: set[str],
        completed_bundles: Iterable[ScientificResultBundle] = (),
        completed_result_ids: Iterable[str] | None = None,
        result_parent_ids: dict[str, tuple[str, ...]] | None = None,
    ) -> ProposedAutonomyStep:
        from uuid import UUID

        result_ids = (
            [UUID(str(value)) for value in completed_result_ids]
            if completed_result_ids is not None
            else None
        )
        state, strategy = self.strategy_engine.decide(
            objective=objective,
            current=current,
            completed_bundles=completed_bundles,
            completed_result_ids=result_ids,
            result_parent_ids={
                UUID(str(result_id)): tuple(UUID(str(value)) for value in parents)
                for result_id, parents in (result_parent_ids or {}).items()
            },
            completed_capability_ids=completed_capability_ids,
        )
        summary = ResearchStrategySummary.from_state(state, strategy)
        action_outcomes = {
            ResearchStrategyAction.SYNTHESIZE: AutonomyProgressOutcome.GOAL_SATISFIED,
            ResearchStrategyAction.CONTINUE_ANALYSIS: AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS,
            ResearchStrategyAction.REUSE_RESULT: AutonomyProgressOutcome.REUSE_EXISTING_RESULT,
            ResearchStrategyAction.TEST_HYPOTHESIS: AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS,
            ResearchStrategyAction.COMPARE: AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS,
            ResearchStrategyAction.NEEDS_CLARIFICATION: AutonomyProgressOutcome.NEEDS_CLARIFICATION,
            ResearchStrategyAction.CONFLICTING_EVIDENCE: AutonomyProgressOutcome.CONFLICTING_EVIDENCE,
            ResearchStrategyAction.STOP_WITH_LIMITATIONS: AutonomyProgressOutcome.STOP_WITH_LIMITATIONS,
        }
        parameters: dict[str, float] = {}
        limitations = list(strategy.limitations)
        if strategy.selected_capability_id == "trajectory.diffusion":
            parameters, refusal = self._diffusion_parameters(current)
            if refusal is not None:
                return ProposedAutonomyStep(
                    outcome=refusal.outcome,
                    reason_codes=refusal.reason_codes,
                    limitations=refusal.limitations,
                    strategy_decision=strategy,
                    strategy_summary=summary,
                )
            limitations.append(
                "The diffusion fit interval is grounded in persisted MSD facts."
            )
        return ProposedAutonomyStep(
            outcome=action_outcomes[strategy.action],
            reason_codes=tuple(strategy.reason_codes),
            capability_id=strategy.selected_capability_id,
            requirement_id=strategy.capability_need,
            parameters=tuple(sorted(parameters.items())),
            limitations=tuple(sorted(set(limitations))),
            strategy_decision=strategy,
            strategy_summary=summary,
        )


__all__ = [
    "ProposedAutonomyStep",
    "ResearchProgressAssessor",
    "semantic_step_signature",
]
