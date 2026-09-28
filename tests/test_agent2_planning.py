from __future__ import annotations

from uuid import uuid4
from datetime import datetime, timezone
import asyncio
import os
from types import SimpleNamespace

import pytest
from mdi_llm.providers import LLMProviderError
from sqlalchemy import create_engine, func, insert, select
from sqlalchemy.pool import StaticPool

from mdi_api.agent2_errors import CapabilityBindingFailed, CapabilityPlanInvalid, InvalidResearchTurnTransition
from mdi_api.research_agent.capabilities.defaults import build_default_capability_registry
from mdi_api.research_agent.capabilities.preconditions import build_default_precondition_registry
from mdi_api.research_agent.capabilities.resolver import CapabilityResolutionService
from mdi_api.research_agent.capabilities.schemas import CapabilityBindingKind, CapabilityInputBinding
from mdi_api.research_agent.orchestration.schemas import OrchestratorConfidence, ProposedRequirement, ResearchTurnDecision
from mdi_api.research_agent.planning.binder import CapabilityBinder
from mdi_api.research_agent.planning.deterministic import build_deterministic_capability_plan
from mdi_api.research_agent.planning.planner import requires_llm_planning
from mdi_api.research_agent.planning.planner import ScientificCapabilityPlanner
from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.research_agent.llm.structured_client import DeepSeekStructuredLLMClient
from mdi_api.research_agent.capabilities.schemas import CapabilityPlannerInput, PlannerCapabilityView, PlannerRequirementView, PlannerSourceRef
from mdi_api.unit_of_work import transaction_active
from mdi_api.research_agent.planning.validator import CapabilityPlanValidator
from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES, validate_agent2_registries
from mdi_api.research_agent.schemas import RequirementCriticality, ResearchAction, ResearchTurnStatus
from mdi_api.research_agent.turns.state_machine import ensure_transition
from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_tool_registry import load_manifests
from mdi_api.db import (
    analysis_plans, artifacts, data_profiles, datasets, jobs, metadata,
    organizations, projects,
    research_turns, sessions, tool_calls, users,
)
from mdi_api.research_agent.planning.processor import CapabilityPlanningProcessor
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.schemas import ScientificObjectKind, StorageRef
from mdi_api.scientific_objects.service import ScientificObjectService
from mdi_api.unit_of_work import RepositoryFactory


TOOLS = load_manifests()


def ref(object_type: str, name: str) -> ScientificObjectRef:
    return ScientificObjectRef(object_id=uuid4(), version_id=uuid4(), project_id="project", object_type=object_type, display_name=name)


def decision(requirements: list[tuple[str, list[str], dict]], objective: str = "Scientific objective") -> ResearchTurnDecision:
    keys = sorted({key for _, refs, _ in requirements for key in refs})
    return ResearchTurnDecision(
        contract_version="1.0", action=ResearchAction.ANALYZE, assistant_message="Prepare analysis.",
        research_objective=objective, selected_scope_ref_keys=keys,
        scientific_requirements=[ProposedRequirement(requirement_id=requirement, criticality=RequirementCriticality.REQUIRED, subject_ref_keys=refs, constraints=constraints) for requirement, refs, constraints in requirements],
        reusable_result_ref_keys=[], clarification=None, confidence=OrchestratorConfidence.HIGH,
    )


def resolve(decision_value: ResearchTurnDecision, refs: list[ScientificObjectRef]):
    snapshot = {"selection_refs_json": [item.model_dump(mode="json") for item in refs], "active_scope_refs_json": []}
    service = CapabilityResolutionService(DEFAULT_AGENT2_REGISTRIES.capabilities, DEFAULT_AGENT2_REGISTRIES.requirements, TOOLS, build_default_precondition_registry())
    resolution = service.resolve(turn={"id": uuid4(), "project_id": "project"}, decision=decision_value, context_snapshot=snapshot)
    return resolution, snapshot


def plan_and_bind(decision_value: ResearchTurnDecision, refs: list[ScientificObjectRef]):
    resolution, snapshot = resolve(decision_value, refs)
    plan = build_deterministic_capability_plan(decision=decision_value, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    CapabilityPlanValidator().validate(plan=plan, resolution=resolution, decision=decision_value, context=snapshot, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    profile = {"semanticColumns": [], "semanticGroups": []}
    if any(
        item.requirement_id == "ml.evaluate_regression"
        for item in decision_value.scientific_requirements
    ):
        profile = {
            "semanticColumns": [
                {
                    "objectId": "table_1",
                    "column": "y_true",
                    "dtype": "float64",
                    "roles": [
                        {
                            "role": "regression_target",
                            "authority": "canonical_name",
                            "groupId": "regression_1",
                        }
                    ],
                },
                {
                    "objectId": "table_1",
                    "column": "y_pred",
                    "dtype": "float64",
                    "roles": [
                        {
                            "role": "regression_prediction",
                            "authority": "canonical_name",
                            "groupId": "regression_1",
                        }
                    ],
                },
            ],
            "semanticGroups": [
                {
                    "groupId": "regression_1",
                    "kind": "regression",
                    "targetColumns": ["y_true"],
                    "predictionColumns": ["y_pred"],
                    "status": "COMPLETE",
                }
            ],
        }
    analysis_plan, _hash = CapabilityBinder(TOOLS).bind(capability_plan=plan, resolution=resolution, context={"dataset_id": "dataset", "profile_id": "profile", "profile": profile, "object_refs": {f"obj_{index}": value for index, value in enumerate(refs, 1)}}, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    return resolution, plan, analysis_plan


def test_phase3_state_model_distinguishes_plan_ready_from_queued():
    ensure_transition(ResearchTurnStatus.READY_TO_PLAN, ResearchTurnStatus.PLANNING)
    ensure_transition(ResearchTurnStatus.PLANNING, ResearchTurnStatus.PLAN_READY)
    ensure_transition(ResearchTurnStatus.PLAN_READY, ResearchTurnStatus.CANCELED)
    with pytest.raises(InvalidResearchTurnTransition):
        ensure_transition(ResearchTurnStatus.PLAN_READY, ResearchTurnStatus.RUNNING)
    with pytest.raises(InvalidResearchTurnTransition):
        ensure_transition(ResearchTurnStatus.PLANNING, ResearchTurnStatus.QUEUED)


def test_p3_c01_rdf_is_deterministic_and_binds_existing_plan_02():
    structure = ref("structure.crystal", "Si")
    resolution, plan, analysis = plan_and_bind(decision([("structure.compute_rdf", ["obj_1"], {})], "Compute RDF"), [structure])
    assert [(item.capability_id, item.eligibility.value) for item in resolution.candidates] == [("structure.rdf", "ELIGIBLE")]
    assert requires_llm_planning(resolution, decision([("structure.compute_rdf", ["obj_1"], {})])) is False
    assert len(plan.steps) == 1 and analysis.schemaVersion == "0.2" and analysis.steps[0].toolId == "structure.rdf"
    assert analysis.steps[0].inputRefs[0].ref == str(structure.version_id)


def test_p3_c02_xrd_has_real_conditional_dependency_and_valid_dag():
    structure, experimental = ref("structure.crystal", "Si"), ref("diffraction.xrd.experimental", "Measured XRD")
    request = decision([
        ("diffraction.generate_theoretical_pattern", ["obj_1"], {}),
        ("diffraction.compare_experimental_theoretical", ["obj_1", "obj_2"], {}),
    ], "Compare theoretical and experimental XRD")
    resolution, plan, analysis = plan_and_bind(request, [structure, experimental])
    states = {item.capability_id: item.eligibility.value for item in resolution.candidates}
    assert states == {"diffraction.experimental_theoretical_comparison": "CONDITIONAL", "diffraction.theoretical_xrd": "ELIGIBLE"}
    assert [step.toolId for step in analysis.steps] == ["structure.xrd", "structure.experimental_xrd_comparison"]
    assert len(analysis.dependencyBindings) == 1
    assert plan.steps[1].input_bindings["experimental"][0].source_ref_key == "obj_2"


def test_p3_c03_ml_regression_evaluation_binds_exact_dataset_version():
    dataset = ref("materials.dataset", "Regression dataset")
    resolution, plan, analysis = plan_and_bind(
        decision([("ml.evaluate_regression", ["obj_1"], {})], "Evaluate regression"),
        [dataset],
    )
    assert resolution.candidates[0].capability_id == "ml.regression_evaluation"
    assert plan.steps[0].input_bindings["dataset"][0].source_ref_key == "obj_1"
    assert [item.toolId for item in analysis.steps] == [
        "ml.basic_metrics",
        "ml.density_scatter",
        "ml.error_distribution",
        "ml.outlier_table",
        "ml.regression_evaluation",
    ]
    for step in analysis.steps:
        normalized = [
            item for item in step.inputRefs if item.refType == "normalized_object"
        ]
        assert normalized and normalized[0].ref == str(dataset.version_id)
    evaluation = next(
        item for item in analysis.steps if item.toolId == "ml.regression_evaluation"
    )
    assert [item.refType for item in evaluation.inputRefs] == [
        "profile",
        "normalized_object",
    ]
    assert evaluation.params["groupIds"] == ["regression_1"]
    for step in analysis.steps[:-1]:
        assert step.params["targetColumn"] == "y_true"
        assert step.params["predictionColumn"] == "y_pred"


def test_p3_c03_ml_regression_evaluation_accepts_promoted_materials_table():
    table = ref("materials.table", "Promoted regression table")
    resolution, plan, analysis = plan_and_bind(
        decision([("ml.evaluate_regression", ["obj_1"], {})], "Evaluate regression"),
        [table],
    )
    assert resolution.candidates[0].capability_id == "ml.regression_evaluation"
    assert resolution.candidates[0].eligibility.value == "ELIGIBLE"
    assert plan.steps[0].input_bindings["dataset"][0].source_ref_key == "obj_1"
    evaluation = next(
        item for item in analysis.steps if item.toolId == "ml.regression_evaluation"
    )
    assert [item.refType for item in evaluation.inputRefs] == [
        "profile",
        "normalized_object",
    ]
    assert evaluation.inputRefs[1].ref == str(table.version_id)


def test_mandatory_capability_tool_suites_bind_complete_stable_coverage():
    dataset = ref("materials.table", "profiled materials table")
    profile = {
        "semanticColumns": [
            {
                "objectId": "table_1",
                "column": "formula",
                "dtype": "string",
                "roles": [
                    {
                        "role": "material_formula",
                        "authority": "canonical_name",
                    }
                ],
            },
            {
                "objectId": "table_1",
                "column": "property_a",
                "dtype": "float64",
                "roles": [],
            },
            {
                "objectId": "table_1",
                "column": "property_b",
                "dtype": "float64",
                "roles": [],
            },
        ],
        "semanticGroups": [],
    }
    expected_by_requirement = {
        "data.analyze_composition": {
            "composition.chem_sys_sunburst",
            "composition.chem_sys_treemap",
            "composition.elements_hist",
            "composition.formula_statistics",
            "composition.ptable_heatmap",
            "composition.summary",
            "structure.composition_from_structure",
        },
        "data.analyze_table": {
            "table.distribution_summary",
            "table.numeric_summary",
            "viz.correlation",
            "viz.histogram",
            "viz.scatter",
        },
    }
    for requirement_id, expected_tools in expected_by_requirement.items():
        request = decision([(requirement_id, ["obj_1"], {})])
        resolution, snapshot = resolve(request, [dataset])
        first = build_deterministic_capability_plan(
            decision=request,
            resolution=resolution,
            registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
        )
        second = build_deterministic_capability_plan(
            decision=request,
            resolution=resolution,
            registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
        )
        assert first.model_dump(mode="json") == second.model_dump(mode="json")
        analyses = []
        for capability_plan in (first, second):
            analysis, _ = CapabilityBinder(TOOLS).bind(
                capability_plan=capability_plan,
                resolution=resolution,
                context={
                    "dataset_id": "dataset",
                    "profile_id": "profile",
                    "profile": profile,
                    "object_refs": {"obj_1": dataset},
                },
                registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
                decision=request,
            )
            analyses.append(analysis)
        tool_sets = [
            [step.toolId for step in analysis.steps] for analysis in analyses
        ]
        assert tool_sets[0] == tool_sets[1]
        assert set(tool_sets[0]) == expected_tools
        assert len(tool_sets[0]) == len(expected_tools)
        assert all(
            step.output["mandatoryCoverage"] is True
            for step in analyses[0].steps
        )
def test_p3_c04_trajectory_msd_diffusion_uses_real_planned_output():
    trajectory = ref("trajectory.atomic", "MD")
    request = decision([
        ("trajectory.compute_msd", ["obj_1"], {"species": "Li"}),
        (
            "trajectory.estimate_diffusion",
            ["obj_1"],
            {"fit_start_time_ps": 1.0, "fit_end_time_ps": 6.0},
        ),
    ])
    _resolution, _plan, analysis = plan_and_bind(request, [trajectory])
    assert [step.toolId for step in analysis.steps] == ["trajectory.msd", "trajectory.diffusion"]
    assert analysis.steps[0].params == {
        "drift_correction": "none",
        "max_lag_count": 512,
        "max_origins_per_lag": 4096,
        "origin_stride": 1,
        "species": "Li",
    }
    assert analysis.steps[1].params["fit_start_time_ps"] == 1.0
    assert analysis.steps[1].params["fit_end_time_ps"] == 6.0
    assert [item.refType for item in analysis.steps[0].inputRefs] == [
        "normalized_object"
    ]
    assert analysis.steps[1].inputRefs == []
    assert analysis.dependencyBindings[0].producerOutputPort == "trajectory-msd"
    assert analysis.dependencyBindings[0].consumerInputPort == "msd"


def test_p3_trajectory_diffusion_continuation_retains_transitive_msd_producer():
    trajectory = ref("trajectory.atomic", "MD")
    request = decision(
        [
            (
                "trajectory.estimate_diffusion",
                ["obj_1"],
                {"fit_start_time_ps": 1.0, "fit_end_time_ps": 6.0},
            ),
        ],
        "Continue the clarified trajectory analysis with the selected fit window.",
    ).model_copy(update={"action": ResearchAction.CONTINUE_ANALYSIS})

    resolution, plan, analysis = plan_and_bind(request, [trajectory])

    candidates = {
        item.capability_id: item
        for item in resolution.candidates
    }
    assert candidates["trajectory.diffusion"].eligibility.value == "CONDITIONAL"
    assert candidates["trajectory.diffusion"].missing_input_slots == ["msd"]
    assert candidates["trajectory.diffusion"].possible_producers == {
        "msd": ["trajectory.msd@1.0"],
    }
    assert candidates["trajectory.msd"].eligibility.value == "ELIGIBLE"
    assert candidates["trajectory.msd"].bound_source_ref_keys == {
        "trajectory": ["obj_1"],
    }
    assert [step.toolId for step in analysis.steps] == [
        "trajectory.msd",
        "trajectory.diffusion",
    ]
    assert plan.steps[1].input_bindings["msd"][0].kind == (
        CapabilityBindingKind.PLANNED_OUTPUT
    )
    assert analysis.dependencyBindings[0].producerOutputPort == "trajectory-msd"
    assert analysis.dependencyBindings[0].consumerInputPort == "msd"


def test_p3_c05_phonon_band_and_dos_bind_real_combined_ports():
    band = ref("phonon.band_structure", "Band")
    dos = ref("phonon.dos", "DOS")
    structure = ref("structure.crystal", "Structure")
    request = decision(
        [
            ("phonon.compose_band_dos", ["obj_1", "obj_2"], {}),
            ("structure.inspect_brillouin_zone", ["obj_3"], {}),
        ]
    )
    resolution, plan, analysis = plan_and_bind(
        request,
        [band, dos, structure],
    )
    candidates = {item.capability_id: item for item in resolution.candidates}
    assert set(candidates) >= {
        "phonon.band",
        "phonon.dos",
        "phonon.band_dos",
        "structure.brillouin_zone",
    }
    assert candidates["phonon.band_dos"].eligibility.value == "CONDITIONAL"
    assert candidates["phonon.band_dos"].missing_input_slots == ["band", "dos"]
    assert candidates["phonon.band_dos"].possible_producers == {
        "band": ["phonon.band@1.0"],
        "dos": ["phonon.dos@1.0"],
    }
    assert requires_llm_planning(resolution, request) is False
    assert [step.toolId for step in analysis.steps] == [
        "phonon.band",
        "phonon.dos",
        "phonon.band_dos",
        "structure.brillouin_zone",
    ]
    assert plan.steps[2].input_bindings["band"][0].kind == (
        CapabilityBindingKind.PLANNED_OUTPUT
    )
    assert plan.steps[2].input_bindings["dos"][0].kind == (
        CapabilityBindingKind.PLANNED_OUTPUT
    )
    assert {
        (
            item.producerOutputPort,
            item.consumerInputPort,
            item.artifactKind.value,
        )
        for item in analysis.dependencyBindings
    } == {
        ("canonical-band", "band", "phonon_band_json"),
        ("canonical-dos", "dos", "phonon_dos_json"),
    }
    assert analysis.steps[3].inputRefs[0].ref == str(structure.version_id)


def test_phonon_composite_rejects_raw_source_bindings_for_artifact_ports():
    band = ref("phonon.band_structure", "Band")
    dos = ref("phonon.dos", "DOS")
    request = decision(
        [("phonon.compose_band_dos", ["obj_1", "obj_2"], {})]
    )
    resolution, snapshot = resolve(request, [band, dos])
    deterministic = build_deterministic_capability_plan(
        decision=request,
        resolution=resolution,
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    combo = next(
        step
        for step in deterministic.steps
        if resolution.candidates[
            int(step.capability_ref_key.removeprefix("cap_")) - 1
        ].capability_id
        == "phonon.band_dos"
    )
    invalid_combo = combo.model_copy(
        update={
            "input_bindings": {
                "band": [
                    CapabilityInputBinding(
                        kind=CapabilityBindingKind.SOURCE_OBJECT,
                        source_ref_key="obj_1",
                    )
                ],
                "dos": [
                    CapabilityInputBinding(
                        kind=CapabilityBindingKind.SOURCE_OBJECT,
                        source_ref_key="obj_2",
                    )
                ],
            }
        }
    )
    invalid = deterministic.model_copy(
        update={
            "steps": [
                invalid_combo if step.step_id == combo.step_id else step
                for step in deterministic.steps
            ]
        }
    )
    with pytest.raises(CapabilityPlanInvalid) as caught:
        CapabilityPlanValidator().validate(
            plan=invalid,
            resolution=resolution,
            decision=request,
            context=snapshot,
            registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
        )
    assert caught.value.code == "CAPABILITY_PLAN_PORT_MISMATCH"


def test_p3_c06_c08_wrong_object_type_is_unsupported_before_planner():
    wrong = ref("electronic.dos", "Electronic DOS")
    resolution, _ = resolve(decision([("structure.compute_rdf", ["obj_1"], {})]), [wrong])
    assert resolution.unsatisfied_required_requirement_ids == ["structure.compute_rdf"]
    assert resolution.candidates == []


def test_p3_c07_explicit_cutoff_is_preserved_through_tool_binding():
    structure = ref("structure.crystal", "Si")
    _resolution, plan, analysis = plan_and_bind(decision([("structure.compute_rdf", ["obj_1"], {"cutoff_angstrom": 8.0})]), [structure])
    assert plan.steps[0].parameters == {"r_max_angstrom": 8.0}
    assert analysis.steps[0].params == {"r_max_angstrom": 8.0}


def test_p3_dataset_semantic_constraints_do_not_become_tool_params():
    dataset = ref("materials.dataset", "Materials")
    request = decision(
        [("data.explore_materials", ["obj_1"], {"property": "band_gap", "sample": "mat-2"})],
        "Analyze the selected Dataset sample.",
    )
    resolution, plan, analysis = plan_and_bind(request, [dataset])
    assert plan.steps[0].parameters == {"property": "band_gap", "sample": "mat-2"}
    assert analysis.steps[0].toolId == "dataset.materials_explorer"
    assert analysis.steps[0].params == {
        "tableObjectId": str(dataset.object_id),
    }


def test_p3_dataset_resource_id_binding_prefers_exact_normalized_resource():
    dataset = ref("materials.dataset", "Materials")
    request = decision(
        [("data.explore_materials", ["obj_1"], {})],
        "Explore the selected materials dataset.",
    )
    resolution, plan, _analysis = plan_and_bind(request, [dataset])
    analysis, _ = CapabilityBinder(TOOLS).bind(
        capability_plan=plan,
        resolution=resolution,
        context={
            "dataset_id": "dataset",
            "profile_id": "profile",
            "object_refs": {"obj_1": dataset},
            "resource_facts": {
                "obj_1": {
                    "object_id": str(dataset.object_id),
                    "resource_id": "dataset:obj_dataframe_exact",
                    "object_type": "materials.dataset",
                }
            },
        },
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
        decision=request,
    )
    assert analysis.steps[0].params == {
        "tableObjectId": "dataset:obj_dataframe_exact",
    }


def test_p3_dataset_unknown_executable_constraint_still_fails_closed():
    dataset = ref("materials.dataset", "Materials")
    request = decision(
        [("data.explore_materials", ["obj_1"], {"unsupported": "should-reject"})],
        "Analyze the selected Dataset.",
    )
    resolution, snapshot = resolve(request, [dataset])
    plan = build_deterministic_capability_plan(decision=request, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    with pytest.raises(CapabilityBindingFailed, match="validation"):
        CapabilityBinder(TOOLS).bind(
            capability_plan=plan,
            resolution=resolution,
            context={"dataset_id": "dataset", "profile_id": "profile", "object_refs": {"obj_1": dataset}},
            registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
        )


def test_p3_c13_current_result_reuses_exact_output_object_without_recomputation():
    experimental = ref("diffraction.xrd.experimental", "Measured XRD")
    theoretical = ref("diffraction.xrd.theoretical", "Persisted theoretical XRD")
    request = decision([("diffraction.compare_experimental_theoretical", ["obj_1"], {})], "Compare XRD")
    request = request.model_copy(update={"reusable_result_ref_keys": ["result_1"]})
    snapshot = {"selection_refs_json": [experimental.model_dump(mode="json")], "active_scope_refs_json": []}
    resolution = CapabilityResolutionService(
        DEFAULT_AGENT2_REGISTRIES.capabilities,
        DEFAULT_AGENT2_REGISTRIES.requirements,
        TOOLS,
        build_default_precondition_registry(),
    ).resolve(
        turn={"id": uuid4(), "project_id": "project"},
        decision=request,
        context_snapshot=snapshot,
        reusable_results={"result_1": {"usable": True, "output_object_refs": [theoretical]}},
    )
    candidate = resolution.candidates[0]
    assert candidate.eligibility.value == "ELIGIBLE"
    assert candidate.reusable_result_bindings == {"theoretical": ["result_1"]}
    plan = build_deterministic_capability_plan(decision=request, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    assert len(plan.steps) == 1
    assert plan.steps[0].input_bindings["theoretical"][0].kind == CapabilityBindingKind.PREVIOUS_RESULT
    analysis, _ = CapabilityBinder(TOOLS).bind(
        capability_plan=plan,
        resolution=resolution,
        context={
            "dataset_id": "dataset",
            "profile_id": "profile",
            "object_refs": {"obj_1": experimental},
            "result_object_refs": {"result_1": theoretical},
        },
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    assert len(analysis.steps) == 1
    assert {item.ref for item in analysis.steps[0].inputRefs} == {str(experimental.version_id), str(theoretical.version_id)}


def test_p3_c13_filters_display_artifact_when_consumer_requires_table(monkeypatch):
    monkeypatch.setattr(
        "mdi_api.research_agent.planning.binder.validate_dependency_plan",
        lambda *_args, **_kwargs: SimpleNamespace(ok=True, errors=[]),
    )
    monkeypatch.setattr(
        "mdi_api.research_agent.planning.binder.validate_plan",
        lambda *_args, **_kwargs: SimpleNamespace(ok=True, errors=[]),
    )
    experimental = ref("diffraction.xrd.experimental", "Measured XRD")
    theoretical = ref("diffraction.xrd.theoretical", "Persisted theoretical XRD")
    request = decision(
        [("diffraction.compare_experimental_theoretical", ["obj_1"], {})],
        "Compare XRD",
    ).model_copy(update={"reusable_result_ref_keys": ["result_1"]})
    snapshot = {
        "selection_refs_json": [experimental.model_dump(mode="json")],
        "active_scope_refs_json": [],
    }
    resolution = CapabilityResolutionService(
        DEFAULT_AGENT2_REGISTRIES.capabilities,
        DEFAULT_AGENT2_REGISTRIES.requirements,
        TOOLS,
        build_default_precondition_registry(),
    ).resolve(
        turn={"id": uuid4(), "project_id": "project"},
        decision=request,
        context_snapshot=snapshot,
        reusable_results={
            "result_1": {
                "usable": True,
                "output_object_refs": [],
                "result_types": ["diffraction.xrd.theoretical"],
                "artifact_ids_by_result_type": {
                    "diffraction.xrd.theoretical": ["plot", "table"],
                },
            },
        },
    )
    plan = build_deterministic_capability_plan(
        decision=request,
        resolution=resolution,
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    analysis, _ = CapabilityBinder(TOOLS).bind(
        capability_plan=plan,
        resolution=resolution,
        context={
            "dataset_id": "dataset",
            "profile_id": "profile",
            "object_refs": {"obj_1": experimental},
            "result_object_refs": {},
            "result_artifact_refs": {
                "result_1": {
                    "diffraction.xrd.theoretical": ["plot", "table"],
                },
            },
            "result_artifact_metadata_refs": {
                "result_1": {
                    "plot": {"type": "plotly_json"},
                    "table": {"type": "table_json"},
                },
            },
        },
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    assert [
        (item.refType, item.ref, item.fieldRole)
        for item in analysis.steps[0].inputRefs
        if item.refType == "artifact"
    ] == [("artifact", "table", "theoretical_xrd_artifact")]


def test_p3_autonomy_reuses_exact_persisted_msd_artifact_for_diffusion():
    artifact_id = str(uuid4())
    request = decision(
        [
            (
                "trajectory.estimate_diffusion",
                [],
                {"fit_start_time_ps": 1.0, "fit_end_time_ps": 6.0},
            )
        ],
        "Estimate diffusion from the existing MSD evidence.",
    ).model_copy(
        update={
            "action": ResearchAction.CONTINUE_ANALYSIS,
            "reusable_result_ref_keys": ["result_1"],
        }
    )
    reusable = {
        "result_1": {
            "usable": True,
            "output_object_refs": [],
            "result_types": ["trajectory.msd"],
            "artifact_ids_by_result_type": {"trajectory.msd": [artifact_id]},
        }
    }
    snapshot = {"selection_refs_json": [], "active_scope_refs_json": []}
    resolution = CapabilityResolutionService(
        DEFAULT_AGENT2_REGISTRIES.capabilities,
        DEFAULT_AGENT2_REGISTRIES.requirements,
        TOOLS,
        build_default_precondition_registry(),
    ).resolve(
        turn={"id": uuid4(), "project_id": "project"},
        decision=request,
        context_snapshot=snapshot,
        reusable_results=reusable,
    )

    candidate = next(
        item
        for item in resolution.candidates
        if item.capability_id == "trajectory.diffusion"
    )
    assert candidate.eligibility.value == "ELIGIBLE"
    assert candidate.reusable_result_bindings == {"msd": ["result_1"]}
    plan = build_deterministic_capability_plan(
        decision=request,
        resolution=resolution,
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    assert len(plan.steps) == 1
    assert plan.steps[0].input_bindings["msd"][0].kind == (
        CapabilityBindingKind.PREVIOUS_RESULT
    )

    analysis, _ = CapabilityBinder(TOOLS).bind(
        capability_plan=plan,
        resolution=resolution,
        context={
            "dataset_id": "dataset",
            "profile_id": "profile",
            "object_refs": {},
            "result_object_refs": {},
            "result_artifact_refs": {
                "result_1": {"trajectory.msd": [artifact_id]}
            },
        },
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )

    assert [step.toolId for step in analysis.steps] == ["trajectory.diffusion"]
    assert [
        (item.refType, item.ref, item.fieldRole)
        for item in analysis.steps[0].inputRefs
    ] == [("artifact", artifact_id, "msd_artifact")]


def test_p3_c09_c12_unknown_capability_and_required_omission_fail_closed():
    structure = ref("structure.crystal", "Si")
    request = decision([("structure.compute_rdf", ["obj_1"], {})])
    resolution, snapshot = resolve(request, [structure])
    plan = build_deterministic_capability_plan(decision=request, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    unknown = plan.model_copy(update={"steps": [plan.steps[0].model_copy(update={"capability_ref_key": "cap_999"})]})
    with pytest.raises(CapabilityPlanInvalid, match="unknown"):
        CapabilityPlanValidator().validate(plan=unknown, resolution=resolution, decision=request, context=snapshot, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    omitted = plan.model_copy(update={"steps": [plan.steps[0].model_copy(update={"satisfies_requirement_ids": []})]})
    with pytest.raises(CapabilityPlanInvalid, match="omitted"):
        CapabilityPlanValidator().validate(plan=omitted, resolution=resolution, decision=request, context=snapshot, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)


def test_p3_c11_planned_output_cycle_is_rejected():
    trajectory = ref("trajectory.atomic", "MD")
    request = decision([("trajectory.compute_msd", ["obj_1"], {}), ("trajectory.estimate_diffusion", ["obj_1"], {})])
    resolution, snapshot = resolve(request, [trajectory])
    plan = build_deterministic_capability_plan(decision=request, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    first = plan.steps[0].model_copy(update={"input_bindings": {"trajectory": [CapabilityInputBinding(kind=CapabilityBindingKind.PLANNED_OUTPUT, producer_step_id="step_2", producer_output_slot="diffusion")]}})
    cyclic = plan.model_copy(update={"steps": [first, plan.steps[1]]})
    with pytest.raises(CapabilityPlanInvalid):
        CapabilityPlanValidator().validate(plan=cyclic, resolution=resolution, decision=request, context=snapshot, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)


def test_p3_c10_planned_output_port_mismatch_is_rejected():
    trajectory = ref("trajectory.atomic", "MD")
    request = decision([("trajectory.compute_msd", ["obj_1"], {}), ("trajectory.estimate_diffusion", ["obj_1"], {})])
    resolution, snapshot = resolve(request, [trajectory])
    plan = build_deterministic_capability_plan(decision=request, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    invalid_binding = CapabilityInputBinding(
        kind=CapabilityBindingKind.PLANNED_OUTPUT,
        producer_step_id="step_1",
        producer_output_slot="unknown_output",
    )
    second = plan.steps[1].model_copy(update={"input_bindings": {**plan.steps[1].input_bindings, "msd": [invalid_binding]}})
    invalid = plan.model_copy(update={"steps": [plan.steps[0], second]})
    with pytest.raises(CapabilityPlanInvalid) as caught:
        CapabilityPlanValidator().validate(plan=invalid, resolution=resolution, decision=request, context=snapshot, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    assert caught.value.code == "CAPABILITY_PLAN_PORT_MISMATCH"


@pytest.mark.parametrize("relevance", ["STALE", "CURRENT_RECOMPUTE"])
def test_p3_c14_c15_recompute_or_stale_result_requires_fresh_producer(relevance):
    structure = ref("structure.crystal", "Si")
    experimental = ref("diffraction.xrd.experimental", "Measured XRD")
    theoretical = ref("diffraction.xrd.theoretical", "Historical theoretical XRD")
    request = decision([
        ("diffraction.generate_theoretical_pattern", ["obj_1"], {}),
        ("diffraction.compare_experimental_theoretical", ["obj_1", "obj_2"], {}),
    ], "Recompute and compare XRD")
    request = request.model_copy(update={"reusable_result_ref_keys": ["result_1"]})
    snapshot = {"selection_refs_json": [structure.model_dump(mode="json"), experimental.model_dump(mode="json")], "active_scope_refs_json": []}
    resolution = CapabilityResolutionService(
        DEFAULT_AGENT2_REGISTRIES.capabilities,
        DEFAULT_AGENT2_REGISTRIES.requirements,
        TOOLS,
        build_default_precondition_registry(),
    ).resolve(
        turn={"id": uuid4(), "project_id": "project"},
        decision=request,
        context_snapshot=snapshot,
        reusable_results={"result_1": {"usable": False, "relevance_status": relevance, "output_object_refs": [theoretical]}},
    )
    plan = build_deterministic_capability_plan(decision=request, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    assert len(plan.steps) == 2
    assert plan.steps[1].input_bindings["theoretical"][0].kind == CapabilityBindingKind.PLANNED_OUTPUT


def test_p3_c16_tool_version_mismatch_fails_closed():
    registry = build_default_capability_registry()
    manifest = registry.require("structure.rdf")
    manifest = manifest.model_copy(update={"tool_bindings": [manifest.tool_bindings[0].model_copy(update={"version_constraint": ">=9.0"})]})
    replacement = build_default_capability_registry()
    replacement._manifests[(manifest.capability_id, manifest.version)] = manifest
    structure = ref("structure.crystal", "Si")
    request = decision([("structure.compute_rdf", ["obj_1"], {})])
    resolution, snapshot = resolve(request, [structure])
    plan = build_deterministic_capability_plan(decision=request, resolution=resolution, registry=replacement)
    with pytest.raises(CapabilityBindingFailed, match="version"):
        CapabilityBinder(TOOLS).bind(capability_plan=plan, resolution=resolution, context={"dataset_id": "dataset", "profile_id": "profile"}, registry=replacement)


def test_p3_c19_existing_plan_validator_rejection_prevents_plan_ready(monkeypatch):
    structure = ref("structure.crystal", "Si")
    request = decision([("structure.compute_rdf", ["obj_1"], {})])
    resolution, _snapshot = resolve(request, [structure])
    plan = build_deterministic_capability_plan(decision=request, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    monkeypatch.setattr(
        "mdi_api.research_agent.planning.binder.validate_plan",
        lambda *_args, **_kwargs: SimpleNamespace(ok=False, errors=[SimpleNamespace(message="fixture rejection")]),
    )
    with pytest.raises(CapabilityBindingFailed) as caught:
        CapabilityBinder(TOOLS).bind(
            capability_plan=plan,
            resolution=resolution,
            context={"dataset_id": "dataset", "profile_id": "profile", "object_refs": {"obj_1": structure}},
            registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
        )
    assert caught.value.code == "ANALYSIS_PLAN_VALIDATION_FAILED"


def test_default_phase3_registry_startup_validation_passes():
    validate_agent2_registries(DEFAULT_AGENT2_REGISTRIES, TOOLS)


def test_bounded_llm_planner_repairs_once_outside_transaction(monkeypatch):
    band, dos = ref("phonon.band_structure", "Band"), ref("phonon.dos", "DOS")
    request = decision([("phonon.inspect_band", ["obj_1"], {}), ("phonon.inspect_dos", ["obj_2"], {})])
    resolution, snapshot = resolve(request, [band, dos])
    valid = {
        "contract_version": "1.0", "objective": request.research_objective,
        "steps": [
            {"step_id": "step_1", "capability_ref_key": "cap_1", "satisfies_requirement_ids": ["phonon.inspect_band"], "input_bindings": {"band": [{"kind": "SOURCE_OBJECT", "source_ref_key": "obj_1"}]}, "parameters": {}, "expected_outputs": [{"slot_name": "band", "result_type": "phonon.band", "scientific_object_type": "phonon.band_structure"}]},
                {"step_id": "step_2", "capability_ref_key": "cap_2", "satisfies_requirement_ids": ["phonon.inspect_dos"], "input_bindings": {"dos": [{"kind": "SOURCE_OBJECT", "source_ref_key": "obj_2"}]}, "parameters": {}, "expected_outputs": [{"slot_name": "dos", "result_type": "phonon.dos", "scientific_object_type": "phonon.dos"}]},
        ],
        "omitted_optional_requirement_ids": [], "planner_summary": "Normalize band and DOS inputs.",
    }
    invalid = {**valid, "steps": [{**valid["steps"][0], "capability_ref_key": "cap_999"}, valid["steps"][1]]}

    class Fake:
        def __init__(self): self.calls = []
        async def generate_structured(self, **kwargs):
            assert transaction_active() is False
            self.calls.append(kwargs)
            return StructuredLLMResult(provider="fake", model="fixture", parsed=invalid if len(self.calls) == 1 else valid, latency_ms=1, repair_attempted=len(self.calls) == 2, prompt_version="scientific-capability-planner/1.0")

    candidates = [PlannerCapabilityView(ref_key=f"cap_{index}", capability_id=item.capability_id, version=item.capability_version, eligibility=item.eligibility, satisfies_requirement_ids=item.satisfies_requirement_ids, input_slots=[], output_slots=[]) for index, item in enumerate(resolution.candidates, 1)]
    planner_input = CapabilityPlannerInput(research_objective=request.research_objective, requirements=[PlannerRequirementView(requirement_id=item.requirement_id, criticality=item.criticality.value, subject_ref_keys=item.subject_ref_keys, constraints=item.constraints) for item in request.scientific_requirements], candidates=candidates, source_bindings=[PlannerSourceRef(ref_key="obj_1", object_type=band.object_type, display_name="Band"), PlannerSourceRef(ref_key="obj_2", object_type=dos.object_type, display_name="DOS")], reusable_results=[], explicit_constraints=[])
    fake = Fake()
    monkeypatch.setattr(
        "mdi_api.research_agent.planning.planner.requires_llm_planning",
        lambda *_args, **_kwargs: True,
    )
    plan, mode, result = asyncio.run(ScientificCapabilityPlanner(registry=DEFAULT_AGENT2_REGISTRIES.capabilities, llm_client=fake).plan(decision=request, resolution=resolution, planner_input=planner_input, context=snapshot))
    assert mode == "LLM" and len(fake.calls) == 2 and result.repair_attempted is True
    assert [step.capability_ref_key for step in plan.steps] == ["cap_1", "cap_2"]
    repair_context = fake.calls[1]["request_context"]["repair"]
    assert repair_context["binding_contracts"]["PREVIOUS_RESULT"] == {
        "required_fields": ["kind", "result_ref_key"],
        "forbidden_fields": [
            "source_ref_key",
            "producer_step_id",
            "producer_output_slot",
        ],
    }


def test_bounded_llm_planner_repairs_mixed_binding_shape_and_stays_fail_closed(
    monkeypatch,
):
    band, dos = ref("phonon.band_structure", "Band"), ref("phonon.dos", "DOS")
    request = decision(
        [
            ("phonon.inspect_band", ["obj_1"], {}),
            ("phonon.inspect_dos", ["obj_2"], {}),
        ]
    )
    resolution, snapshot = resolve(request, [band, dos])
    valid = {
        "contract_version": "1.0",
        "objective": request.research_objective,
        "steps": [
            {
                "step_id": "step_1",
                "capability_ref_key": "cap_1",
                "satisfies_requirement_ids": ["phonon.inspect_band"],
                "input_bindings": {
                    "band": [{"kind": "SOURCE_OBJECT", "source_ref_key": "obj_1"}]
                },
                "parameters": {},
                "expected_outputs": [
                    {
                        "slot_name": "band",
                        "result_type": "phonon.band",
                        "scientific_object_type": "phonon.band_structure",
                    }
                ],
            },
            {
                "step_id": "step_2",
                "capability_ref_key": "cap_2",
                "satisfies_requirement_ids": ["phonon.inspect_dos"],
                "input_bindings": {
                    "dos": [{"kind": "SOURCE_OBJECT", "source_ref_key": "obj_2"}]
                },
                "parameters": {},
                "expected_outputs": [
                    {
                        "slot_name": "dos",
                        "result_type": "phonon.dos",
                        "scientific_object_type": "phonon.dos",
                    }
                ],
            },
        ],
        "omitted_optional_requirement_ids": [],
        "planner_summary": "Inspect the exact band and DOS sources.",
    }
    invalid = {
        **valid,
        "steps": [
            valid["steps"][0],
            {
                **valid["steps"][1],
                "input_bindings": {
                    "dos": [
                        {
                            "kind": "PREVIOUS_RESULT",
                            "result_ref_key": "result_1",
                            "producer_step_id": "step_1",
                            "producer_output_slot": "band",
                        }
                    ]
                },
            },
        ],
    }
    candidates = [
        PlannerCapabilityView(
            ref_key=f"cap_{index}",
            capability_id=item.capability_id,
            version=item.capability_version,
            eligibility=item.eligibility,
            satisfies_requirement_ids=item.satisfies_requirement_ids,
            input_slots=[],
            output_slots=[],
        )
        for index, item in enumerate(resolution.candidates, 1)
    ]
    planner_input = CapabilityPlannerInput(
        research_objective=request.research_objective,
        requirements=[
            PlannerRequirementView(
                requirement_id=item.requirement_id,
                criticality=item.criticality.value,
                subject_ref_keys=item.subject_ref_keys,
                constraints=item.constraints,
            )
            for item in request.scientific_requirements
        ],
        candidates=candidates,
        source_bindings=[
            PlannerSourceRef(
                ref_key="obj_1",
                object_type=band.object_type,
                display_name="Band",
            ),
            PlannerSourceRef(
                ref_key="obj_2",
                object_type=dos.object_type,
                display_name="DOS",
            ),
        ],
        reusable_results=[],
        explicit_constraints=[],
    )

    class RepairingFake:
        def __init__(self) -> None:
            self.calls: list[dict] = []

        async def generate_structured(self, **kwargs):
            self.calls.append(kwargs)
            parsed = invalid if len(self.calls) == 1 else valid
            return StructuredLLMResult(
                provider="fake",
                model="fixture",
                parsed=parsed,
                latency_ms=1,
                repair_attempted=False,
                prompt_version="scientific-capability-planner/1.1",
            )

    repairing = RepairingFake()
    monkeypatch.setattr(
        "mdi_api.research_agent.planning.planner.requires_llm_planning",
        lambda *_args, **_kwargs: True,
    )
    plan, mode, result = asyncio.run(
        ScientificCapabilityPlanner(
            registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
            llm_client=repairing,
        ).plan(
            decision=request,
            resolution=resolution,
            planner_input=planner_input,
            context=snapshot,
        )
    )
    assert mode == "LLM"
    assert len(repairing.calls) == 2
    assert result.repair_attempted is True
    assert plan.steps[1].input_bindings["dos"][0].kind == CapabilityBindingKind.SOURCE_OBJECT

    class AlwaysInvalidFake:
        async def generate_structured(self, **kwargs):
            return StructuredLLMResult(
                provider="fake",
                model="fixture",
                parsed=invalid,
                latency_ms=1,
                repair_attempted=bool(kwargs["request_context"]["repair_attempted"]),
                prompt_version="scientific-capability-planner/1.1",
            )

    with pytest.raises(CapabilityPlanInvalid, match="binding fields do not match binding kind"):
        asyncio.run(
            ScientificCapabilityPlanner(
                registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
                llm_client=AlwaysInvalidFake(),
            ).plan(
                decision=request,
                resolution=resolution,
                planner_input=planner_input,
                context=snapshot,
            )
        )


@pytest.mark.live_llm
@pytest.mark.skipif(
    os.getenv("MDI_RUN_AGENT2_LIVE") != "1" or not os.getenv("DEEPSEEK_KEY"),
    reason="Set MDI_RUN_AGENT2_LIVE=1 and DEEPSEEK_KEY for live qualification",
)
def test_live_deepseek_phase3_alternative_capability_planning():
    band, dos = ref("phonon.band_structure", "Band"), ref("phonon.dos", "DOS")
    request = decision(
        [("phonon.inspect_band", ["obj_1"], {}), ("phonon.inspect_dos", ["obj_2"], {})],
        "Prepare a compatible phonon band and density-of-states analysis.",
    )
    resolution, snapshot = resolve(request, [band, dos])
    planner_input = CapabilityPlanningProcessor._planner_input(
        request,
        resolution,
        snapshot,
        {},
        DEFAULT_AGENT2_REGISTRIES,
    )
    try:
        plan, mode, result = asyncio.run(ScientificCapabilityPlanner(
            registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
            llm_client=DeepSeekStructuredLLMClient(),
        ).plan(decision=request, resolution=resolution, planner_input=planner_input, context=snapshot))
    except LLMProviderError as exc:
        pytest.fail(f"live provider failed: code={exc.code}; status={exc.status_code}; safe_message={exc.safe_message}")
    assert mode == "LLM" and result is not None
    assert {item.requirement_id for item in request.scientific_requirements}.issubset({
        requirement_id
        for step in plan.steps
        for requirement_id in step.satisfies_requirement_ids
    })


def test_p3_c17_c18_c20_processor_is_idempotent_and_never_executes():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    with engine.begin() as connection:
        connection.execute(insert(users), {"id": "owner", "email": "owner@example.invalid", "display_name": "Owner", "is_active": True})
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(insert(projects), {"id": "project", "organization_id": "org", "name": "Project", "created_by": "owner"})
        connection.execute(insert(datasets), {"id": "dataset", "project_id": "project", "name": "Dataset", "status": "profile_ready", "metadata_json": {}, "created_by": "owner"})
        connection.execute(insert(data_profiles), {"id": "profile", "dataset_id": "dataset", "version": "2.0", "profile_json": {"id": "profile", "datasetId": "dataset"}})
        connection.execute(insert(sessions), {"id": "session", "project_id": "project", "mode": "project", "status": "active", "created_by": "owner"})
    factory = RepositoryFactory(engine)
    objects = ScientificObjectService(factory, build_default_object_type_registry())
    logical = objects.create_object(project_id="project", kind=ScientificObjectKind.STRUCTURE, object_type="structure.crystal", display_name="Si", created_by_user_id="owner")
    version = objects.create_version(logical["id"], object_type="structure.crystal", object_schema_version="1.0", source_resource_refs=[{"project_id": "project", "dataset_id": "dataset"}], parent_object_version_refs=[], normalized_payload_ref=StorageRef(storage_backend="minio", object_key="si.json", checksum="sha-si"), content_hash="content-si", semantic_hash="semantic-si", canonical_metadata={"summary": "Si"}, created_by_user_id="owner")
    object_reference = ScientificObjectRef(object_id=logical["id"], version_id=version["id"], project_id="project", object_type="structure.crystal", display_name="Si")
    turn_id, snapshot_id, decision_id = uuid4(), uuid4(), uuid4()
    decision_value = decision([("structure.compute_rdf", ["obj_1"], {})], "Compute RDF")
    with factory.unit_of_work() as unit:
        unit.agent2.research_turns.add_message({"id": "message", "session_id": "session", "role": "user", "content_summary": "Compute RDF", "payload_json": {}, "created_at": now})
        unit.agent2.research_turns.add({"id": turn_id, "project_id": "project", "research_session_id": "session", "sequence_no": 1, "user_message_id": "message", "action_type": "ANALYZE", "status": "READY_TO_PLAN", "row_version": 1, "created_at": now, "updated_at": now})
        unit.agent2.research_context_snapshots.add({"id": snapshot_id, "project_id": "project", "research_session_id": "session", "research_turn_id": turn_id, "snapshot_schema_version": "2.0", "active_scope_refs_json": [object_reference.model_dump(mode="json")], "selection_refs_json": [], "resolved_references_json": [], "referenced_result_refs_json": [], "relevant_finding_refs_json": [], "effective_constraints_json": [], "research_goal": "Compute RDF", "unresolved_questions_json": [], "context_fingerprint": "f" * 64, "compiler_version": "test/1.0", "created_at": now})
        unit.agent2.research_turn_decisions.add({"id": decision_id, "research_turn_id": turn_id, "contract_version": "1.0", "action": "ANALYZE", "decision_json": decision_value.model_dump(mode="json"), "input_context_fingerprint": "f" * 64, "prompt_version": "research-orchestrator/1.0", "provider": "fake", "model": "fixture", "provider_request_id": None, "repair_attempted": False, "validation_status": "VALIDATED", "action_dispatch_status": "READY_FOR_DOWNSTREAM", "created_at": now})
    processor = CapabilityPlanningProcessor(factory)
    first = processor.process(turn_id)
    second = processor.process(turn_id)
    assert first["status"] == "PLAN_READY" and second["status"] == "NOOP"
    with engine.connect() as connection:
        assert connection.execute(select(func.count()).select_from(analysis_plans)).scalar_one() == 1
        assert connection.execute(select(func.count()).select_from(jobs)).scalar_one() == 0
        assert connection.execute(select(func.count()).select_from(tool_calls)).scalar_one() == 0
        assert connection.execute(select(func.count()).select_from(artifacts)).scalar_one() == 0
        stored_turn = connection.execute(select(research_turns).where(research_turns.c.id == turn_id)).mappings().one()
        assert stored_turn["analysis_plan_id"] == first["analysis_plan_id"] and stored_turn["job_id"] is None
