from __future__ import annotations

from copy import deepcopy

from mdi_api.research_agent.evaluation import (
    AgentEvaluationRunner,
    QualityEvaluationRunner,
    evaluate_report_quality,
    load_phase14r_quality_corpus,
)
from mdi_api.research_agent.registry_validation import build_default_agent2_registries


def test_phase14r_quality_corpus_is_versioned_representative_and_deterministic() -> None:
    corpus = load_phase14r_quality_corpus()
    assert corpus.contract_version == "phase14r.agent-quality-evaluation/1.0"
    assert corpus.corpus_id == "phase14r-r10-v1"
    assert len(corpus.cases) == 32
    assert {
        "structure",
        "diffraction",
        "trajectory",
        "phonon",
        "electronic",
        "dataset",
        "composition",
        "ml",
        "historical",
        "control",
        "conversation",
        "recovery",
    } <= {case.family for case in corpus.cases}
    assert {
        "query-only routing",
        "ambiguous source clarification",
        "exact Result reuse",
        "historical v1 after v2",
        "partial scientific result",
        "unsupported request",
        "wrong user assumption",
        "multi-result synthesis",
        "stop during orchestration",
        "stop queued execution",
        "edit latest message and branch",
        "rerun research",
        "re-interpret without recomputation",
        "retry failed report generation",
    } <= {case.scenario for case in corpus.cases}

    runner = QualityEvaluationRunner(
        AgentEvaluationRunner(build_default_agent2_registries())
    )
    results = [runner.evaluate(case) for case in corpus.cases]
    assert all(result.passed for result in results), [
        result for result in results if not result.passed
    ]


def test_phase14r_quality_corpus_covers_every_scientific_requirement_family() -> None:
    corpus = load_phase14r_quality_corpus()
    covered = {
        requirement_id
        for case in corpus.cases
        if case.expected is not None
        for requirement_id in case.expected.requirement_ids
    }
    # Query and Report are product actions with dedicated product-contract
    # cases; all execution-bearing requirement families remain represented.
    assert {
        "structure.inspect",
        "structure.inspect_coordination",
        "structure.inspect_coordination_crystalnn",
        "structure.inspect_coordination_voronoi",
        "structure.inspect_coordination_hist",
        "structure.compute_rdf",
        "diffraction.generate_theoretical_pattern",
        "diffraction.compare_experimental_theoretical",
        "trajectory.compute_rdf",
        "trajectory.compute_msd",
        "trajectory.estimate_diffusion",
        "phonon.inspect_band",
        "phonon.inspect_dos",
        "electronic.inspect_band",
        "electronic.inspect_dos",
        "data.explore_materials",
        "data.explore_composition_space",
        "ml.evaluate_regression",
    } <= covered


def _report_fixture() -> tuple[dict, dict]:
    result_id = "11111111-1111-4111-8111-111111111111"
    object_ref = {
        "object_id": "22222222-2222-4222-8222-222222222222",
        "version_id": "33333333-3333-4333-8333-333333333333",
        "project_id": "project_eval",
        "object_type": "trajectory.atomic",
    }
    bundle = {
        "result_id": result_id,
        "execution_status": "SUCCESS",
        "source_object_refs": [object_ref],
        "result_items": [{"id": "result.item", "fact_refs": ["fact.value"]}],
        "facts": [{"fact_id": "fact.value", "value": 1.25, "unit": "eV"}],
        "figures": [{"figure_id": "figure.value"}],
        "tables": [{"table_id": "table.value"}],
        "evidence": [{"evidence_id": "evidence.value"}],
        "methods": [{"method_id": "method.value"}],
        "limitations": [{"limitation_id": "limitation.value"}],
        "warnings": [],
    }
    snapshot = {
        "report_id": "agent2_report_eval",
        "scientific_result_snapshot_id": result_id,
        "grounding_status": "VALID",
        "report": {
            "title": "Evaluation report",
            "research_question": "What does the exact result show?",
            "summary": "The exact result is summarized.",
            "discussion": {
                "text": "The grounded result is discussed.",
                "fact_refs": ["fact.value"],
                "evidence_refs": ["evidence.value"],
            },
            "conclusion": {
                "text": "The grounded result supports the bounded conclusion.",
                "fact_refs": ["fact.value"],
                "evidence_refs": ["evidence.value"],
            },
            "next_steps": {
                "text": "Collect more authoritative data.",
                "fact_refs": [],
                "evidence_refs": [],
            },
            "main_findings": [{
                "statement": "The authoritative value is 1.25 eV.",
                "finding_refs": ["finding.value"],
                "fact_refs": ["fact.value"],
                "evidence_refs": ["evidence.value"],
            }],
            "primary_figures": [{
                "figure_ref": "figure.value",
                "caption": "Authoritative figure",
                "fact_refs": [],
                "evidence_refs": ["evidence.value"],
            }],
            "supporting_results": [],
            "method_summary": "The persisted method was used.",
            "limitations": [{
                "statement": "The source limitation is preserved.",
                "source_refs": ["limitation.value"],
            }],
            "data_sources": ["source_1"],
            "evidence_refs": ["evidence.value"],
            "reproducibility_summary": "Exact source and Result identities are retained.",
        },
    }
    return snapshot, bundle


def test_phase14r_report_quality_evaluator_passes_grounded_complete_report() -> None:
    snapshot, bundle = _report_fixture()
    assessment = evaluate_report_quality(
        snapshot,
        bundle,
        result_snapshot_id=snapshot["scientific_result_snapshot_id"],
    )
    assert assessment.quality_pass is True
    assert assessment.normalized_score == 100
    assert all(
        score == 2
        for score in assessment.criterion_scores.values()
        if score is not None
    )


def test_phase14r_report_quality_evaluator_fails_missing_authority_and_limits() -> None:
    snapshot, bundle = _report_fixture()
    broken = deepcopy(snapshot)
    broken["grounding_status"] = "REJECTED"
    broken["report"]["data_sources"] = []
    broken["report"]["evidence_refs"] = []
    broken["report"]["limitations"] = []
    assessment = evaluate_report_quality(
        broken,
        bundle,
        result_snapshot_id=snapshot["scientific_result_snapshot_id"],
    )
    assert assessment.quality_pass is False
    assert assessment.criterion_scores[3] == 0
    assert assessment.criterion_scores[9] == 0
    assert assessment.criterion_scores[12] == 0
    assert assessment.criterion_scores[19] == 0
