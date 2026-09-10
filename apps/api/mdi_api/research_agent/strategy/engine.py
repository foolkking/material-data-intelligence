from __future__ import annotations

import math
from typing import Iterable
from uuid import UUID

from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.research_agent.strategy.evidence import (
    ResearchEvidenceStateProjector,
    ResultEvidenceInput,
)
from mdi_api.research_agent.strategy.schemas import (
    ComparisonCompatibilityStatus,
    EvidenceGap,
    EvidenceGapType,
    EvidenceStrength,
    EvidenceValue,
    ResearchEvidenceState,
    ResearchStrategyAction,
    ResearchStrategyDecision,
    ScientificHypothesis,
    ScientificHypothesisStatus,
    ScientificQuestion,
    ScientificQuestionStatus,
    ScientificQuestionType,
)


_DIFFUSION_TERMS = ("diffusion", "transport", "扩散", "输运", "传输")
_EXPLANATION_TERMS = ("why", "explain", "mechanism", "原因", "解释", "机制")
_LOCAL_ENV_TERMS = (
    "local environment",
    "coordination",
    "structure",
    "structural",
    "局域",
    "配位",
    "结构",
)
_DATA_PATTERN_TERMS = (
    "error",
    "poor",
    "model performance",
    "regression",
    "composition",
    "chemistry",
    "误差",
    "表现差",
    "模式",
    "组成",
    "化学",
)
_COMPARISON_TERMS = (
    "compare",
    "comparison",
    "agree",
    "agreement",
    "versus",
    "vs",
    "比较",
    "一致",
)
_UNUSUAL_TERMS = ("unusual", "abnormal", "anomal", "异常", "反常")
_CAUSAL_TERMS = ("prove", "causes", "causal", "证明", "导致", "因果")
_XRD_TERMS = ("xrd", "diffraction", "衍射")
_ELECTRONIC_TERMS = ("band", "band gap", "dos", "electronic", "能带", "带隙", "态密度")


def _has(text: str, terms: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _question(
    question_id: str,
    question_type: ScientificQuestionType,
    statement: str,
    *,
    status: ScientificQuestionStatus = ScientificQuestionStatus.OPEN,
    result_ids: Iterable[UUID] = (),
    gap_ids: Iterable[str] = (),
) -> ScientificQuestion:
    return ScientificQuestion(
        question_id=question_id,
        question_type=question_type,
        statement=statement,
        status=status,
        evidence_result_ids=list(result_ids),
        evidence_gap_ids=list(gap_ids),
    )


class ScientificResearchStrategyEngine:
    """Bounded, result-first scientific strategy over durable evidence."""

    max_questions = 4
    max_hypotheses = 2

    def build_state(
        self,
        *,
        objective: str,
        current: ScientificResultBundle,
        completed: Iterable[ScientificResultBundle] = (),
        result_ids: Iterable[UUID] | None = None,
        result_parent_ids: dict[UUID, tuple[UUID, ...]] | None = None,
    ) -> ResearchEvidenceState:
        bundles = list(completed)
        if not bundles or bundles[-1].result_id != current.result_id:
            bundles.append(current)
        supplied_ids = list(result_ids or [])
        if supplied_ids and len(supplied_ids) != len(bundles):
            supplied_ids = []
        rows = [
            ResultEvidenceInput(
                result_id=(
                    supplied_ids[index]
                    if supplied_ids
                    else bundle.result_id
                ),
                bundle=bundle,
                parent_result_ids=(
                    (result_parent_ids or {}).get(
                        supplied_ids[index] if supplied_ids else bundle.result_id,
                        (),
                    )
                ),
            )
            for index, bundle in enumerate(bundles)
        ]
        return ResearchEvidenceStateProjector().project(
            objective=objective,
            results=rows,
        )

    @staticmethod
    def _numeric_fact(
        state: ResearchEvidenceState, predicate: str
    ) -> float | None:
        values = [
            item.value
            for item in state.observations
            if item.predicate == predicate
            and isinstance(item.value, (int, float))
            and not isinstance(item.value, bool)
            and math.isfinite(float(item.value))
        ]
        if not values:
            return None
        return float(values[-1])

    @staticmethod
    def _source_types(bundles: Iterable[ScientificResultBundle]) -> set[str]:
        return {
            ref.object_type
            for bundle in bundles
            for ref in [*bundle.source_object_refs, *bundle.output_object_refs]
        }

    @staticmethod
    def _gap(
        gap_id: str,
        question_id: str,
        gap_type: EvidenceGapType,
        statement: str,
        value: EvidenceValue,
        requirement_id: str | None,
        result_types: Iterable[str] = (),
    ) -> EvidenceGap:
        return EvidenceGap(
            gap_id=gap_id,
            question_id=question_id,
            gap_type=gap_type,
            statement=statement,
            evidence_value=value,
            requirement_id=requirement_id,
            required_result_types=list(result_types),
        )

    @staticmethod
    def _decision(
        state: ResearchEvidenceState,
        *,
        action: ResearchStrategyAction,
        question_id: str | None,
        reason_codes: Iterable[str],
        gap: EvidenceGap | None = None,
        capability_id: str | None = None,
        hypothesis: ScientificHypothesis | None = None,
        evidence_value: EvidenceValue | None = None,
        limitations: Iterable[str] = (),
        comparison_status: ComparisonCompatibilityStatus | None = None,
    ) -> ResearchStrategyDecision:
        return ResearchStrategyDecision(
            action=action,
            objective=state.objective,
            current_question_id=question_id,
            evidence_gap=gap,
            evidence_result_ids=state.result_ids[-16:],
            capability_need=gap.requirement_id if gap else None,
            selected_capability_id=capability_id,
            hypothesis=hypothesis,
            evidence_value=evidence_value,
            reason_codes=list(reason_codes),
            limitations=sorted(set([*state.limitations, *limitations]))[:16],
            contradiction_ids=[
                item.contradiction_id
                for item in state.contradictions
                if item.unresolved
            ][:8],
            comparison_status=comparison_status,
            evidence_state_fingerprint=state.fingerprint,
        )

    def decide(
        self,
        *,
        objective: str,
        current: ScientificResultBundle,
        completed_bundles: Iterable[ScientificResultBundle] = (),
        completed_result_ids: Iterable[UUID] | None = None,
        result_parent_ids: dict[UUID, tuple[UUID, ...]] | None = None,
        completed_capability_ids: set[str] | None = None,
    ) -> tuple[ResearchEvidenceState, ResearchStrategyDecision]:
        bundles = list(completed_bundles)
        if not bundles or bundles[-1].result_id != current.result_id:
            bundles.append(current)
        state = self.build_state(
            objective=objective,
            current=current,
            completed=bundles,
            result_ids=completed_result_ids,
            result_parent_ids=result_parent_ids,
        )
        completed = set(completed_capability_ids or state.capability_ids)
        sources = self._source_types(bundles)
        questions: list[ScientificQuestion] = []
        gaps: list[EvidenceGap] = []
        hypotheses: list[ScientificHypothesis] = []

        if _has(objective, _CAUSAL_TERMS):
            question = _question(
                "q-causal-validity",
                ScientificQuestionType.VALIDATE,
                "Can the available computational evidence establish the requested causal claim?",
                status=ScientificQuestionStatus.LIMITED,
                result_ids=state.result_ids,
            )
            state = state.model_copy(update={"questions": [question]})
            return state, self._decision(
                state,
                action=ResearchStrategyAction.STOP_WITH_LIMITATIONS,
                question_id=question.question_id,
                reason_codes=("UNSUPPORTED_CAUSAL_INFERENCE",),
                limitations=(
                    "Available computational evidence may support association or "
                    "consistency, but it does not establish causality.",
                ),
            )

        unresolved = [item for item in state.contradictions if item.unresolved]
        if unresolved:
            question = _question(
                "q-consistency",
                ScientificQuestionType.CHECK_CONSISTENCY,
                "Can conflicting scientific Results be reconciled by source, method, or convention?",
                status=ScientificQuestionStatus.CONFLICTING,
                result_ids=state.result_ids,
            )
            gap = self._gap(
                "gap-contradictory-results",
                question.question_id,
                EvidenceGapType.CONTRADICTORY_RESULTS,
                "Current authoritative Results disagree after known unit normalization.",
                EvidenceValue.HIGH,
                None,
            )
            question = question.model_copy(update={"evidence_gap_ids": [gap.gap_id]})
            state = state.model_copy(
                update={"questions": [question], "evidence_gaps": [gap]}
            )
            return state, self._decision(
                state,
                action=ResearchStrategyAction.CONFLICTING_EVIDENCE,
                question_id=question.question_id,
                gap=gap,
                evidence_value=EvidenceValue.HIGH,
                reason_codes=("UNRESOLVED_AUTHORITATIVE_RESULT_CONTRADICTION",),
                limitations=(
                    "No Result was silently preferred; method and exact-version "
                    "provenance must remain visible.",
                ),
            )

        if current.execution_status.value == "PARTIAL":
            question = _question(
                "q-result-completeness",
                ScientificQuestionType.IDENTIFY_LIMITATION,
                "Is the available scientific Result complete enough to support another analysis?",
                status=ScientificQuestionStatus.LIMITED,
                result_ids=state.result_ids,
            )
            state = state.model_copy(update={"questions": [question]})
            return state, self._decision(
                state,
                action=ResearchStrategyAction.STOP_WITH_LIMITATIONS,
                question_id=question.question_id,
                reason_codes=("PARTIAL_RESULT_REQUIRES_BOUNDED_STOP",),
            )

        # Transport characterization: MSD and diffusion are the minimum
        # sufficient quantitative chain. Structural follow-up is conditional
        # on an explicit explanatory objective, not on capability availability.
        if _has(objective, _DIFFUSION_TERMS):
            q_transport = _question(
                "q-transport",
                ScientificQuestionType.QUANTIFY,
                "What transport behavior is supported by the selected trajectory?",
                result_ids=state.result_ids,
            )
            questions.append(q_transport)
            if "trajectory.msd" not in completed:
                gap = self._gap(
                    "gap-msd",
                    q_transport.question_id,
                    EvidenceGapType.TRANSPORT_METRIC_MISSING,
                    "Mean-squared displacement evidence is missing.",
                    EvidenceValue.HIGH,
                    "trajectory.compute_msd",
                    ("trajectory.msd",),
                )
                gaps.append(gap)
                questions[0] = q_transport.model_copy(
                    update={"evidence_gap_ids": [gap.gap_id]}
                )
                state = state.model_copy(
                    update={"questions": questions, "evidence_gaps": gaps}
                )
                return state, self._decision(
                    state,
                    action=ResearchStrategyAction.CONTINUE_ANALYSIS,
                    question_id=q_transport.question_id,
                    gap=gap,
                    capability_id="trajectory.msd",
                    evidence_value=EvidenceValue.HIGH,
                    reason_codes=("OBJECTIVE_REQUIRES_MSD_EVIDENCE",),
                )
            if "trajectory.diffusion" not in completed:
                gap = self._gap(
                    "gap-diffusion",
                    q_transport.question_id,
                    EvidenceGapType.PROPERTY_NOT_QUANTIFIED,
                    "A diffusion estimate grounded in the MSD fit range is missing.",
                    EvidenceValue.HIGH,
                    "trajectory.estimate_diffusion",
                    ("trajectory.diffusion",),
                )
                gaps.append(gap)
                questions[0] = q_transport.model_copy(
                    update={"evidence_gap_ids": [gap.gap_id]}
                )
                state = state.model_copy(
                    update={"questions": questions, "evidence_gaps": gaps}
                )
                return state, self._decision(
                    state,
                    action=ResearchStrategyAction.CONTINUE_ANALYSIS,
                    question_id=q_transport.question_id,
                    gap=gap,
                    capability_id="trajectory.diffusion",
                    evidence_value=EvidenceValue.HIGH,
                    reason_codes=(
                        "OBJECTIVE_REQUIRES_TRANSPORT_EVIDENCE",
                        "MSD_EVIDENCE_AVAILABLE",
                    ),
                )
            questions[0] = q_transport.model_copy(
                update={
                    "status": ScientificQuestionStatus.RESOLVED,
                    "evidence_result_ids": state.result_ids,
                }
            )
            if _has(objective, _EXPLANATION_TERMS):
                q_structure = _question(
                    "q-transport-structure",
                    ScientificQuestionType.TEST_HYPOTHESIS,
                    "Does local structural evidence help explain the observed transport behavior?",
                    result_ids=state.result_ids,
                )
                questions.append(q_structure)
                if "trajectory.rdf" not in completed:
                    gap = self._gap(
                        "gap-local-transport-structure",
                        q_structure.question_id,
                        EvidenceGapType.STRUCTURAL_CONTEXT_MISSING,
                        "Local pair-distribution evidence from the trajectory is missing.",
                        EvidenceValue.MEDIUM,
                        "trajectory.compute_rdf",
                        ("trajectory.rdf",),
                    )
                    hypothesis = ScientificHypothesis(
                        hypothesis_id="hypothesis-local-constraint",
                        question_id=q_structure.question_id,
                        statement=(
                            "The observed transport behavior may be associated with "
                            "a less constrained local atomic environment."
                        ),
                        status=ScientificHypothesisStatus.PROPOSED,
                        supporting_result_ids=state.result_ids[-2:],
                        testable_predictions=[
                            "Trajectory RDF should provide bounded local-distance evidence."
                        ],
                        known_assumptions=[
                            "Pair-distribution evidence alone cannot establish causality."
                        ],
                        evidence_gap_id=gap.gap_id,
                    )
                    gaps.append(gap)
                    hypotheses.append(hypothesis)
                    questions[-1] = q_structure.model_copy(
                        update={"evidence_gap_ids": [gap.gap_id]}
                    )
                    state = state.model_copy(
                        update={
                            "questions": questions[: self.max_questions],
                            "evidence_gaps": gaps,
                            "hypotheses": hypotheses[: self.max_hypotheses],
                        }
                    )
                    return state, self._decision(
                        state,
                        action=ResearchStrategyAction.TEST_HYPOTHESIS,
                        question_id=q_structure.question_id,
                        gap=gap,
                        capability_id="trajectory.rdf",
                        hypothesis=hypothesis,
                        evidence_value=EvidenceValue.MEDIUM,
                        reason_codes=(
                            "TRANSPORT_RESULT_AVAILABLE",
                            "OBJECTIVE_REQUESTS_STRUCTURAL_EXPLANATION",
                            "LOCAL_STRUCTURE_EVIDENCE_MISSING",
                        ),
                        limitations=(
                            "RDF can supply structural context but cannot establish "
                            "a causal transport mechanism.",
                        ),
                    )
                questions[-1] = q_structure.model_copy(
                    update={"status": ScientificQuestionStatus.RESOLVED}
                )
            state = state.model_copy(update={"questions": questions[: self.max_questions]})
            return state, self._decision(
                state,
                action=ResearchStrategyAction.SYNTHESIZE,
                question_id=questions[-1].question_id,
                reason_codes=("MINIMUM_SUFFICIENT_TRANSPORT_EVIDENCE_AVAILABLE",),
            )

        # Dataset/ML strategy: quantify model performance before asking whether
        # errors have a materials pattern. Composition analysis is not run for
        # a generic dataset summary objective.
        if _has(objective, _DATA_PATTERN_TERMS):
            q_model = _question(
                "q-model-performance",
                ScientificQuestionType.QUANTIFY,
                "What model-performance evidence is available?",
                result_ids=state.result_ids,
            )
            questions.append(q_model)
            if "ml.regression_evaluation" not in completed:
                gap = self._gap(
                    "gap-model-evaluation",
                    q_model.question_id,
                    EvidenceGapType.PROPERTY_NOT_QUANTIFIED,
                    "Regression evaluation metrics and bounded high-error samples are missing.",
                    EvidenceValue.HIGH,
                    "ml.evaluate_regression",
                    ("ml.regression.evaluation",),
                )
                questions[0] = q_model.model_copy(
                    update={"evidence_gap_ids": [gap.gap_id]}
                )
                state = state.model_copy(
                    update={"questions": questions, "evidence_gaps": [gap]}
                )
                return state, self._decision(
                    state,
                    action=ResearchStrategyAction.CONTINUE_ANALYSIS,
                    question_id=q_model.question_id,
                    gap=gap,
                    capability_id="ml.regression_evaluation",
                    evidence_value=EvidenceValue.HIGH,
                    reason_codes=("MODEL_PERFORMANCE_EVIDENCE_MISSING",),
                )
            questions[0] = q_model.model_copy(
                update={"status": ScientificQuestionStatus.RESOLVED}
            )
            chemistry_requested = _has(
                objective, ("composition", "chemistry", "chemical", "组成", "化学")
            )
            if chemistry_requested and "data.composition_space" not in completed:
                q_pattern = _question(
                    "q-error-chemistry",
                    ScientificQuestionType.COMPARE,
                    "Are model errors associated with a materials-composition pattern?",
                    result_ids=state.result_ids,
                )
                gap = self._gap(
                    "gap-error-composition",
                    q_pattern.question_id,
                    EvidenceGapType.MODEL_ERROR_PATTERN_UNEXPLAINED,
                    "Composition grouping evidence is missing for the observed errors.",
                    EvidenceValue.HIGH,
                    "data.explore_composition_space",
                    ("data.composition_space",),
                )
                questions.append(
                    q_pattern.model_copy(update={"evidence_gap_ids": [gap.gap_id]})
                )
                state = state.model_copy(
                    update={"questions": questions, "evidence_gaps": [gap]}
                )
                return state, self._decision(
                    state,
                    action=ResearchStrategyAction.COMPARE,
                    question_id=q_pattern.question_id,
                    gap=gap,
                    capability_id="data.composition_space",
                    evidence_value=EvidenceValue.HIGH,
                    reason_codes=(
                        "MODEL_ERROR_EVIDENCE_AVAILABLE",
                        "OBJECTIVE_REQUESTS_CHEMISTRY_PATTERN",
                    ),
                    limitations=(
                        "Composition-space evidence is descriptive and does not "
                        "establish a causal origin of model error.",
                    ),
                )
            state = state.model_copy(update={"questions": questions})
            return state, self._decision(
                state,
                action=ResearchStrategyAction.SYNTHESIZE,
                question_id=q_model.question_id,
                reason_codes=("MODEL_EVIDENCE_SUFFICIENT_FOR_REQUESTED_SCOPE",),
            )

        if _has(objective, _XRD_TERMS) and _has(objective, _COMPARISON_TERMS):
            question = _question(
                "q-diffraction-comparison",
                ScientificQuestionType.COMPARE,
                "Does the experimental diffraction pattern agree with the candidate structure prediction?",
                result_ids=state.result_ids,
            )
            questions.append(question)
            if "diffraction.xrd.comparison" in state.result_types:
                questions[0] = question.model_copy(
                    update={"status": ScientificQuestionStatus.RESOLVED}
                )
                state = state.model_copy(update={"questions": questions})
                return state, self._decision(
                    state,
                    action=ResearchStrategyAction.SYNTHESIZE,
                    question_id=question.question_id,
                    reason_codes=("DIFFRACTION_COMPARISON_EVIDENCE_AVAILABLE",),
                    limitations=(
                        "Peak agreement is not definitive phase confirmation and "
                        "remains sensitive to broadening and measurement conditions.",
                    ),
                )
            if "diffraction.xrd.theoretical" not in state.result_types:
                if "structure.crystal" not in sources:
                    gap = self._gap(
                        "gap-candidate-structure",
                        question.question_id,
                        EvidenceGapType.SOURCE_LIMITATION,
                        "An exact candidate crystal structure is required.",
                        EvidenceValue.HIGH,
                        None,
                    )
                    state = state.model_copy(
                        update={
                            "questions": [
                                question.model_copy(
                                    update={"evidence_gap_ids": [gap.gap_id]}
                                )
                            ],
                            "evidence_gaps": [gap],
                        }
                    )
                    return state, self._decision(
                        state,
                        action=ResearchStrategyAction.NEEDS_CLARIFICATION,
                        question_id=question.question_id,
                        gap=gap,
                        evidence_value=EvidenceValue.HIGH,
                        reason_codes=("CANDIDATE_STRUCTURE_REQUIRED_FOR_XRD",),
                    )
                gap = self._gap(
                    "gap-theoretical-xrd",
                    question.question_id,
                    EvidenceGapType.COMPARISON_MISSING,
                    "Theoretical diffraction evidence for the candidate structure is missing.",
                    EvidenceValue.HIGH,
                    "diffraction.generate_theoretical_pattern",
                    ("diffraction.xrd.theoretical",),
                )
                state = state.model_copy(
                    update={
                        "questions": [
                            question.model_copy(
                                update={"evidence_gap_ids": [gap.gap_id]}
                            )
                        ],
                        "evidence_gaps": [gap],
                    }
                )
                return state, self._decision(
                    state,
                    action=ResearchStrategyAction.CONTINUE_ANALYSIS,
                    question_id=question.question_id,
                    gap=gap,
                    capability_id="diffraction.theoretical_xrd",
                    evidence_value=EvidenceValue.HIGH,
                    reason_codes=("THEORETICAL_DIFFRACTION_EVIDENCE_MISSING",),
                )
            if "diffraction.xrd.experimental" not in sources:
                gap = self._gap(
                    "gap-experimental-xrd",
                    question.question_id,
                    EvidenceGapType.REFERENCE_BASELINE_MISSING,
                    "An exact experimental diffraction pattern is required for comparison.",
                    EvidenceValue.HIGH,
                    None,
                )
                state = state.model_copy(
                    update={
                        "questions": [
                            question.model_copy(
                                update={"evidence_gap_ids": [gap.gap_id]}
                            )
                        ],
                        "evidence_gaps": [gap],
                    }
                )
                return state, self._decision(
                    state,
                    action=ResearchStrategyAction.NEEDS_CLARIFICATION,
                    question_id=question.question_id,
                    gap=gap,
                    evidence_value=EvidenceValue.HIGH,
                    reason_codes=("EXPERIMENTAL_DIFFRACTION_REFERENCE_REQUIRED",),
                )
            gap = self._gap(
                "gap-xrd-comparison",
                question.question_id,
                EvidenceGapType.COMPARISON_MISSING,
                "Peak-matching comparison evidence is missing.",
                EvidenceValue.HIGH,
                "diffraction.compare_experimental_theoretical",
                ("diffraction.xrd.comparison",),
            )
            state = state.model_copy(
                update={
                    "questions": [
                        question.model_copy(update={"evidence_gap_ids": [gap.gap_id]})
                    ],
                    "evidence_gaps": [gap],
                }
            )
            return state, self._decision(
                state,
                action=ResearchStrategyAction.COMPARE,
                question_id=question.question_id,
                gap=gap,
                capability_id="diffraction.experimental_theoretical_comparison",
                evidence_value=EvidenceValue.HIGH,
                reason_codes=(
                    "EXPERIMENTAL_AND_THEORETICAL_DIFFRACTION_AVAILABLE",
                    "COMPARISON_EVIDENCE_MISSING",
                ),
            )

        if _has(objective, _LOCAL_ENV_TERMS):
            question = _question(
                "q-local-environment",
                ScientificQuestionType.CHARACTERIZE,
                "What local structural environment is supported by the selected structure?",
                result_ids=state.result_ids,
            )
            questions.append(question)
            if "structure.rdf" not in completed:
                gap = self._gap(
                    "gap-structure-rdf",
                    question.question_id,
                    EvidenceGapType.STRUCTURAL_CONTEXT_MISSING,
                    "Pair-distance evidence is missing.",
                    EvidenceValue.HIGH,
                    "structure.compute_rdf",
                    ("structure.rdf",),
                )
                state = state.model_copy(
                    update={
                        "questions": [
                            question.model_copy(
                                update={"evidence_gap_ids": [gap.gap_id]}
                            )
                        ],
                        "evidence_gaps": [gap],
                    }
                )
                return state, self._decision(
                    state,
                    action=ResearchStrategyAction.CONTINUE_ANALYSIS,
                    question_id=question.question_id,
                    gap=gap,
                    capability_id="structure.rdf",
                    evidence_value=EvidenceValue.HIGH,
                    reason_codes=("LOCAL_DISTANCE_EVIDENCE_MISSING",),
                )
            coordination = {
                "structure.coordination_hist",
                "structure.coordination_crystalnn",
                "structure.coordination_voronoinn",
            }
            if not completed.intersection(coordination):
                gap = self._gap(
                    "gap-coordination",
                    question.question_id,
                    EvidenceGapType.STRUCTURAL_CONTEXT_MISSING,
                    "Coordination-distribution evidence is missing.",
                    EvidenceValue.MEDIUM,
                    "structure.inspect_coordination_hist",
                    ("structure.coordination.hist",),
                )
                state = state.model_copy(
                    update={
                        "questions": [
                            question.model_copy(
                                update={"evidence_gap_ids": [gap.gap_id]}
                            )
                        ],
                        "evidence_gaps": [gap],
                    }
                )
                return state, self._decision(
                    state,
                    action=ResearchStrategyAction.CONTINUE_ANALYSIS,
                    question_id=question.question_id,
                    gap=gap,
                    capability_id="structure.coordination_hist",
                    evidence_value=EvidenceValue.MEDIUM,
                    reason_codes=(
                        "STRUCTURAL_DISTANCE_EVIDENCE_AVAILABLE",
                        "COORDINATION_EVIDENCE_MISSING",
                    ),
                )
            if _has(objective, _UNUSUAL_TERMS):
                distinct_sources = {
                    ref.version_id
                    for bundle in bundles
                    for ref in bundle.source_object_refs
                    if ref.object_type == "structure.crystal"
                }
                if len(distinct_sources) < 2:
                    gap = self._gap(
                        "gap-structure-reference",
                        question.question_id,
                        EvidenceGapType.REFERENCE_BASELINE_MISSING,
                        "Calling an environment unusual requires an explicit comparison baseline.",
                        EvidenceValue.HIGH,
                        None,
                    )
                    state = state.model_copy(
                        update={
                            "questions": [
                                question.model_copy(
                                    update={
                                        "status": ScientificQuestionStatus.LIMITED,
                                        "evidence_gap_ids": [gap.gap_id],
                                    }
                                )
                            ],
                            "evidence_gaps": [gap],
                        }
                    )
                    return state, self._decision(
                        state,
                        action=ResearchStrategyAction.NEEDS_CLARIFICATION,
                        question_id=question.question_id,
                        gap=gap,
                        evidence_value=EvidenceValue.HIGH,
                        reason_codes=("STRUCTURAL_COMPARISON_BASELINE_REQUIRED",),
                    )
            questions[0] = question.model_copy(
                update={"status": ScientificQuestionStatus.RESOLVED}
            )
            state = state.model_copy(update={"questions": questions})
            return state, self._decision(
                state,
                action=ResearchStrategyAction.SYNTHESIZE,
                question_id=question.question_id,
                reason_codes=("LOCAL_ENVIRONMENT_EVIDENCE_SUFFICIENT",),
            )

        if _has(objective, _ELECTRONIC_TERMS):
            question = _question(
                "q-electronic-feature",
                ScientificQuestionType.CHARACTERIZE,
                "What feature is present in the supplied electronic result?",
                result_ids=state.result_ids,
            )
            if completed.intersection({"electronic.band_structure", "electronic.dos"}):
                question = question.model_copy(
                    update={"status": ScientificQuestionStatus.RESOLVED}
                )
                state = state.model_copy(update={"questions": [question]})
                return state, self._decision(
                    state,
                    action=ResearchStrategyAction.SYNTHESIZE,
                    question_id=question.question_id,
                    reason_codes=("SUPPLIED_ELECTRONIC_RESULT_AVAILABLE",),
                    limitations=(
                        "The platform validates supplied-data integration and "
                        "semantics, not the underlying external electronic solver.",
                    ),
                )
            gap = self._gap(
                "gap-electronic-result",
                question.question_id,
                EvidenceGapType.SUPPLIED_RESULT_MISSING,
                "A supplied electronic Result is required; this platform does not run a new solver here.",
                EvidenceValue.HIGH,
                None,
            )
            state = state.model_copy(
                update={
                    "questions": [
                        question.model_copy(update={"evidence_gap_ids": [gap.gap_id]})
                    ],
                    "evidence_gaps": [gap],
                }
            )
            return state, self._decision(
                state,
                action=ResearchStrategyAction.STOP_WITH_LIMITATIONS,
                question_id=question.question_id,
                gap=gap,
                evidence_value=EvidenceValue.HIGH,
                reason_codes=("EXTERNAL_SOLVER_RESULT_NOT_AVAILABLE",),
            )

        question = _question(
            "q-requested-scope",
            ScientificQuestionType.CHARACTERIZE,
            "Does the available authoritative evidence address the requested scope?",
            status=(
                ScientificQuestionStatus.RESOLVED
                if state.evidence_strength
                in {
                    EvidenceStrength.WELL_SUPPORTED,
                    EvidenceStrength.QUALIFIED_METHOD_DEPENDENT,
                }
                else ScientificQuestionStatus.LIMITED
            ),
            result_ids=state.result_ids,
        )
        state = state.model_copy(update={"questions": [question]})
        return state, self._decision(
            state,
            action=(
                ResearchStrategyAction.SYNTHESIZE
                if question.status == ScientificQuestionStatus.RESOLVED
                else ResearchStrategyAction.STOP_WITH_LIMITATIONS
            ),
            question_id=question.question_id,
            reason_codes=(
                "EXISTING_EVIDENCE_ADDRESSES_REQUESTED_SCOPE"
                if question.status == ScientificQuestionStatus.RESOLVED
                else "AVAILABLE_EVIDENCE_INSUFFICIENT"
            ,),
        )


__all__ = ["ScientificResearchStrategyEngine"]
