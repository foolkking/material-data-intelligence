from __future__ import annotations

from uuid import uuid4

from mdi_api.domain.scientific_results.contracts import (
    FactSourceLocator,
    MethodRecord,
    ProvenanceRecord,
    ResultExecutionStatus,
    ResultRelevanceStatus,
    ScientificFact,
    ScientificResultBundle,
    ScientificResultItem,
    ScientificResultRole,
)
from mdi_api.research_agent.strategy.evaluation import StrategyEvaluationCase
from mdi_api.research_agent.strategy.schemas import ResearchStrategyAction
from mdi_api.scientific_objects.schemas import ScientificObjectRef


def synthetic_bundle(
    *,
    capability_id: str,
    result_type: str,
    source_type: str = "trajectory.atomic",
    source: ScientificObjectRef | None = None,
    execution_status: ResultExecutionStatus = ResultExecutionStatus.SUCCESS,
    numeric_fact: tuple[str, str, float, str | None] | None = None,
) -> ScientificResultBundle:
    source = source or ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id="strategy-fixture",
        object_type=source_type,
    )
    facts: list[ScientificFact] = []
    if result_type == "trajectory.msd":
        facts = [
            ScientificFact(
                fact_id="msd.lag-count",
                predicate="trajectory.msd_lag_count",
                subject_ref=str(source.version_id),
                value=6,
                unit="count",
                source=FactSourceLocator(artifact_locator="/coverage/validLags"),
            ),
            ScientificFact(
                fact_id="msd.first-lag",
                predicate="trajectory.msd_first_lag_time",
                subject_ref=str(source.version_id),
                value=1.0,
                unit="picosecond",
                source=FactSourceLocator(artifact_locator="/lagTimesPs/0"),
            ),
            ScientificFact(
                fact_id="msd.last-lag",
                predicate="trajectory.msd_last_lag_time",
                subject_ref=str(source.version_id),
                value=6.0,
                unit="picosecond",
                source=FactSourceLocator(artifact_locator="/lagTimesPs/5"),
            ),
        ]
    if numeric_fact is not None:
        predicate, fact_id, value, unit = numeric_fact
        facts.append(
            ScientificFact(
                fact_id=fact_id,
                predicate=predicate,
                subject_ref=str(source.version_id),
                value=value,
                unit=unit,
                source=FactSourceLocator(artifact_locator=f"/{predicate}"),
            )
        )
    result_id = uuid4()
    return ScientificResultBundle(
        schema_version="1.0",
        result_id=result_id,
        project_id=source.project_id,
        research_session_id="strategy-session",
        research_turn_id=uuid4(),
        research_question="strategy fixture",
        source_object_refs=[source],
        execution_status=execution_status,
        relevance_status=ResultRelevanceStatus.CURRENT,
        result_items=[
            ScientificResultItem(
                id=result_type,
                result_type=result_type,
                role=ScientificResultRole.PRIMARY,
                title=result_type,
                artifact_ids=[],
                scientific_object_refs=[],
                fact_refs=[fact.fact_id for fact in facts],
                evidence_refs=[],
            )
        ],
        facts=facts,
        figures=[],
        tables=[],
        output_object_refs=[],
        evidence=[],
        methods=[
            MethodRecord(
                method_id=f"method:{capability_id}:{result_id}",
                capability_id=capability_id,
                capability_version="1.0",
                source_object_refs=[source],
            )
        ],
        limitations=[],
        warnings=[],
        provenance=ProvenanceRecord(
            research_turn_id=uuid4(),
            source_object_version_ids=[source.version_id],
        ),
        projection_version="strategy.fixture/1.0",
    )


def golden_strategy_cases() -> tuple[StrategyEvaluationCase, ...]:
    trajectory_source = ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id="strategy-fixture",
        object_type="trajectory.atomic",
    )
    msd = synthetic_bundle(
        capability_id="trajectory.msd",
        result_type="trajectory.msd",
        source=trajectory_source,
    )
    diffusion = synthetic_bundle(
        capability_id="trajectory.diffusion",
        result_type="trajectory.diffusion",
        source=trajectory_source,
    )
    ml = synthetic_bundle(
        capability_id="ml.regression_evaluation",
        result_type="ml.regression.evaluation",
        source_type="materials.dataset",
    )
    theoretical = synthetic_bundle(
        capability_id="diffraction.theoretical_xrd",
        result_type="diffraction.xrd.theoretical",
        source_type="diffraction.xrd.experimental",
    )
    theoretical = theoretical.model_copy(
        update={
            "source_object_refs": [
                *theoretical.source_object_refs,
                ScientificObjectRef(
                    object_id=uuid4(),
                    version_id=uuid4(),
                    project_id="strategy-fixture",
                    object_type="structure.crystal",
                ),
            ]
        }
    )
    rdf = synthetic_bundle(
        capability_id="structure.rdf",
        result_type="structure.rdf",
        source_type="structure.crystal",
    )
    coordination = synthetic_bundle(
        capability_id="structure.coordination_hist",
        result_type="structure.coordination.hist",
        source=rdf.source_object_refs[0],
    )
    electronic = synthetic_bundle(
        capability_id="electronic.band_structure",
        result_type="electronic.band_structure",
        source_type="electronic.band_structure",
    )
    causal = synthetic_bundle(
        capability_id="trajectory.msd",
        result_type="trajectory.msd",
        source=trajectory_source,
    )
    partial = msd.model_copy(
        update={"execution_status": ResultExecutionStatus.PARTIAL}
    )
    generic = synthetic_bundle(
        capability_id="data.materials_explorer",
        result_type="data.materials_explorer",
        source_type="materials.dataset",
    )
    contradictory_a = synthetic_bundle(
        capability_id="trajectory.diffusion",
        result_type="trajectory.diffusion",
        source=trajectory_source,
        numeric_fact=("trajectory.diffusion_coefficient", "diffusion.a", 1.0, "angstrom^2/picosecond"),
    )
    contradictory_b = synthetic_bundle(
        capability_id="trajectory.diffusion",
        result_type="trajectory.diffusion",
        source=trajectory_source,
        numeric_fact=("trajectory.diffusion_coefficient", "diffusion.b", 2.0, "angstrom^2/picosecond"),
    )
    missing_xrd_source = theoretical.model_copy(update={"source_object_refs": []})
    cases = (
        ("trajectory-quantify", "Analyze diffusion behavior.", msd, (msd,), {"trajectory.msd"}, {ResearchStrategyAction.CONTINUE_ANALYSIS}, {"trajectory.diffusion"}, frozenset(), False, False),
        ("trajectory-explain", "Explain the diffusion transport behavior.", diffusion, (msd, diffusion), {"trajectory.msd", "trajectory.diffusion"}, {ResearchStrategyAction.TEST_HYPOTHESIS}, {"trajectory.rdf"}, frozenset(), False, True),
        ("dataset-chemistry", "Investigate model error and its chemistry pattern.", ml, (ml,), {"ml.regression_evaluation"}, {ResearchStrategyAction.COMPARE}, {"data.composition_space"}, frozenset(), False, False),
        ("xrd-compare", "Compare the experimental XRD agreement.", theoretical, (theoretical,), {"diffraction.theoretical_xrd"}, {ResearchStrategyAction.COMPARE}, {"diffraction.experimental_theoretical_comparison"}, frozenset(), False, False),
        ("structure-followup", "Explain the local structural environment.", rdf, (rdf,), {"structure.rdf"}, {ResearchStrategyAction.CONTINUE_ANALYSIS}, {"structure.coordination_hist"}, frozenset(), False, False),
        ("structure-baseline", "Is this local environment unusual?", coordination, (rdf, coordination), {"structure.rdf", "structure.coordination_hist"}, {ResearchStrategyAction.NEEDS_CLARIFICATION}, frozenset(), frozenset(), True, False),
        ("electronic-limit", "Inspect the electronic band gap.", electronic, (electronic,), {"electronic.band_structure"}, {ResearchStrategyAction.SYNTHESIZE}, frozenset(), frozenset(), True, False),
        ("causal-limit", "Prove this structure causes better transport.", causal, (causal,), {"trajectory.msd"}, {ResearchStrategyAction.STOP_WITH_LIMITATIONS}, frozenset(), frozenset(), True, False),
        ("partial-limit", "Analyze this trajectory.", partial, (partial,), {"trajectory.msd"}, {ResearchStrategyAction.STOP_WITH_LIMITATIONS}, frozenset(), frozenset(), True, False),
        ("existing-evidence", "Summarize the available dataset evidence.", generic, (generic,), {"data.materials_explorer"}, {ResearchStrategyAction.SYNTHESIZE}, frozenset(), frozenset(), True, False),
        ("contradiction", "Assess the diffusion coefficient.", contradictory_b, (contradictory_a, contradictory_b), {"trajectory.diffusion"}, {ResearchStrategyAction.CONFLICTING_EVIDENCE}, frozenset(), frozenset(), True, False),
        ("xrd-missing-source", "Compare the diffraction pattern.", missing_xrd_source, (missing_xrd_source,), {"diffraction.theoretical_xrd"}, {ResearchStrategyAction.NEEDS_CLARIFICATION}, frozenset(), frozenset(), True, False),
    )
    return tuple(
        StrategyEvaluationCase(
            case_id=case_id,
            objective=objective,
            current_result=current,
            completed_bundles=completed,
            completed_capability_ids=frozenset(capabilities),
            expected_actions=actions,
            allowed_capabilities=frozenset(allowed),
            forbidden_capabilities=frozenset(forbidden),
            expected_stop=expected_stop,
            expected_hypothesis=expected_hypothesis,
        )
        for (
            case_id,
            objective,
            current,
            completed,
            capabilities,
            actions,
            allowed,
            forbidden,
            expected_stop,
            expected_hypothesis,
        ) in cases
    )


__all__ = ["golden_strategy_cases", "synthetic_bundle"]
