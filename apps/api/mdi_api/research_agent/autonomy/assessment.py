from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Iterable

from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.research_agent.autonomy.schemas import AutonomyProgressOutcome


@dataclass(frozen=True)
class ProposedAutonomyStep:
    outcome: AutonomyProgressOutcome
    reason_codes: tuple[str, ...]
    capability_id: str | None = None
    requirement_id: str | None = None
    parameters: tuple[tuple[str, float], ...] = ()
    limitations: tuple[str, ...] = ()

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
    """Conservative deterministic follow-up rules for validated golden families.

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
    ) -> ProposedAutonomyStep:
        lowered = objective.lower()
        result_types = {item.result_type for item in current.result_items}
        capability_ids = {item.capability_id for item in current.methods}

        if any(term in lowered for term in self._CAUSAL_TERMS):
            return ProposedAutonomyStep(
                outcome=AutonomyProgressOutcome.STOP_WITH_LIMITATIONS,
                reason_codes=("UNSUPPORTED_CAUSAL_INFERENCE",),
                limitations=(
                    "Available computational evidence does not establish causality.",
                ),
            )

        if (
            any(term in lowered for term in self._DIFFUSION_TERMS)
            and (
                "trajectory.msd" in result_types
                or "trajectory.msd" in capability_ids
            )
            and "trajectory.diffusion" not in completed_capability_ids
        ):
            parameters, refusal = self._diffusion_parameters(current)
            if refusal is not None:
                return refusal
            assert parameters is not None
            return ProposedAutonomyStep(
                outcome=AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS,
                capability_id="trajectory.diffusion",
                requirement_id="trajectory.estimate_diffusion",
                parameters=tuple(sorted(parameters.items())),
                reason_codes=(
                    "OBJECTIVE_REQUIRES_TRANSPORT_EVIDENCE",
                    "MSD_EVIDENCE_AVAILABLE",
                    "FIT_WINDOW_GROUNDED_IN_MSD_RESULT",
                ),
            )

        if (
            any(term in lowered for term in self._DATA_PATTERN_TERMS)
            and completed_capability_ids.intersection(
                {"ml.regression_evaluation", "data.materials_explorer"}
            )
            and "data.composition_space" not in completed_capability_ids
        ):
            return ProposedAutonomyStep(
                outcome=AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS,
                capability_id="data.composition_space",
                requirement_id="data.explore_composition_space",
                reason_codes=(
                    "OBJECTIVE_REQUIRES_MATERIAL_PATTERN_EVIDENCE",
                    "DATASET_EVIDENCE_AVAILABLE",
                ),
            )

        if (
            any(term in lowered for term in self._LOCAL_ENV_TERMS)
            and "structure.rdf" in completed_capability_ids
            and not completed_capability_ids.intersection(
                {
                    "structure.coordination_hist",
                    "structure.coordination_crystalnn",
                    "structure.coordination_voronoinn",
                }
            )
        ):
            return ProposedAutonomyStep(
                outcome=AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS,
                capability_id="structure.coordination_hist",
                requirement_id="structure.inspect_coordination_hist",
                reason_codes=(
                    "OBJECTIVE_REQUIRES_LOCAL_COORDINATION_EVIDENCE",
                    "STRUCTURAL_DISTANCE_EVIDENCE_AVAILABLE",
                ),
            )

        if current.execution_status.value == "PARTIAL":
            return ProposedAutonomyStep(
                outcome=AutonomyProgressOutcome.STOP_WITH_LIMITATIONS,
                reason_codes=("PARTIAL_RESULT_REQUIRES_BOUNDED_STOP",),
                limitations=tuple(item.message for item in current.limitations[:8]),
            )

        return ProposedAutonomyStep(
            outcome=AutonomyProgressOutcome.GOAL_SATISFIED,
            reason_codes=("NO_ADDITIONAL_MATERIAL_EVIDENCE_REQUIRED",),
        )


__all__ = [
    "ProposedAutonomyStep",
    "ResearchProgressAssessor",
    "semantic_step_signature",
]
