from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from mdi_api.agent2_errors import CapabilityBindingFailed
from mdi_api.research_agent.capabilities.preconditions import build_default_precondition_registry
from mdi_api.research_agent.capabilities.resolver import CapabilityResolutionService
from mdi_api.research_agent.orchestration.schemas import OrchestratorConfidence, ProposedRequirement, ResearchTurnDecision
from mdi_api.research_agent.planning.binder import CapabilityBinder
from mdi_api.research_agent.planning.deterministic import build_deterministic_capability_plan
from mdi_api.research_agent.planning.processor import CapabilityPlanningProcessor
from mdi_api.research_agent.planning.validator import CapabilityPlanValidator
from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES, validate_agent2_registries
from mdi_api.research_agent.schemas import RequirementCriticality, ResearchAction
from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_api.scientific_results.projectors.base import ScientificResultProjectionContext
from mdi_api.scientific_results.projectors.canonical import build_canonical_result_projectors
from mdi_tool_registry import load_manifests


TOOLS = load_manifests()
NEW_CAPABILITIES = {
    "structure.coordination_hist",
    "structure.coordination_crystalnn",
    "structure.coordination_voronoinn",
    "trajectory.rdf",
    "electronic.band_structure",
    "electronic.dos",
    "ml.uncertainty_evaluation",
    "ml.classification_evaluation",
    "structure.summary",
    "structure.viewer_scene",
    "trajectory.viewer_scene",
    "data.composition_space",
    "data.materials_explorer",
    "volumetric.data",
    "structure.brillouin_zone",
}


def ref(object_type: str, name: str = "fixture") -> ScientificObjectRef:
    return ScientificObjectRef(object_id=uuid4(), version_id=uuid4(), project_id="project", object_type=object_type, display_name=name)


def request(requirements: list[tuple[str, str]], *, objective: str = "Natural scientific request") -> ResearchTurnDecision:
    return ResearchTurnDecision(
        contract_version="1.0", action=ResearchAction.ANALYZE, assistant_message="Prepare analysis.",
        research_objective=objective, selected_scope_ref_keys=[f"obj_{index + 1}" for index in range(len(requirements))],
        scientific_requirements=[
            ProposedRequirement(requirement_id=req, criticality=RequirementCriticality.REQUIRED, subject_ref_keys=[f"obj_{index + 1}"], constraints={})
            for index, (req, _kind) in enumerate(requirements)
        ], reusable_result_ref_keys=[], clarification=None, confidence=OrchestratorConfidence.HIGH,
    )


def resolve(decision: ResearchTurnDecision, refs: list[ScientificObjectRef]):
    snapshot = {"selection_refs_json": [item.model_dump(mode="json") for item in refs], "active_scope_refs_json": []}
    service = CapabilityResolutionService(
        DEFAULT_AGENT2_REGISTRIES.capabilities, DEFAULT_AGENT2_REGISTRIES.requirements, TOOLS, build_default_precondition_registry()
    )
    return service.resolve(turn={"id": uuid4(), "project_id": "project"}, decision=decision, context_snapshot=snapshot), snapshot


def _context(payload: dict, projector_id: str) -> ScientificResultProjectionContext:
    source = ref("electronic.band_structure")
    artifact_id = "phase10-artifact-1"
    companion_tool_ids = {
        "agent2.structure.summary": (
            "structure.lattice_summary",
            "structure.preview_metadata",
            "structure.spacegroup_summary",
        ),
        "agent2.structure.viewer_scene": (
            "structure.structure_3d",
            "structure.viewer_3d",
        ),
    }.get(projector_id, ())
    tool_calls = tuple(
        {
            "id": f"phase10-tool-call-{index}",
            "toolId": tool_id,
            "state": "COMPLETED",
        }
        for index, tool_id in enumerate(companion_tool_ids, start=1)
    )
    companion_artifacts = tuple(
        {
            "id": f"phase10-companion-{index}",
            "contentType": "application/json",
            "filename": f"{tool_id.replace('.', '_')}.json",
            "toolCallId": f"phase10-tool-call-{index}",
        }
        for index, tool_id in enumerate(companion_tool_ids, start=1)
    )
    artifacts = (
        {
            "id": artifact_id,
            "contentType": "application/json",
            "filename": "phase10.json",
        },
    ) + companion_artifacts
    artifact_payloads = {artifact_id: payload}
    artifact_payloads.update(
        {
            artifact["id"]: {
                "toolId": tool_id,
                "status": "COMPLETED",
                "payload": {"bounded": True},
            }
            for artifact, tool_id in zip(
                companion_artifacts,
                companion_tool_ids,
                strict=True,
            )
        }
    )
    return ScientificResultProjectionContext(
        project_id="project", research_session_id="session", research_turn_id=str(uuid4()), research_question="Inspect this data",
        execution_summary={"outcome": "SUCCESS", "job_id": "job-1", "analysis_plan_id": "plan-1"},
        capability_plan={"steps": [{"step_id": "step_1", "capability_id": projector_id.removeprefix("agent2."), "capability_version": "1.0", "parameters": {}}]},
        analysis_plan={"schemaVersion": "0.2"},
        tool_calls=tool_calls,
        artifacts=artifacts,
        artifact_payloads=artifact_payloads,
        source_object_refs=(source,),
    )


def test_p10_c01_batch_is_frozen_and_spans_families():
    manifests = DEFAULT_AGENT2_REGISTRIES.capabilities.list_all()
    assert NEW_CAPABILITIES.issubset({item.capability_id for item in manifests})
    assert len(NEW_CAPABILITIES) == 15
    assert {item.domain for item in manifests if item.capability_id in NEW_CAPABILITIES} >= {"structure", "trajectory", "electronic", "data", "ml", "volumetric"}


def test_p10_c02_registry_and_tool_bindings_validate():
    validate_agent2_registries(DEFAULT_AGENT2_REGISTRIES, TOOLS)
    for capability_id in NEW_CAPABILITIES:
        manifest = DEFAULT_AGENT2_REGISTRIES.capabilities.require(capability_id)
        assert manifest.tool_bindings[0].tool_id in {item.toolId for item in TOOLS.tools}
        assert manifest.result_projector.startswith("agent2.")


@pytest.mark.parametrize(
    ("requirement", "object_type", "capability"),
    [
        ("structure.inspect_coordination_hist", "structure.crystal", "structure.coordination_hist"),
        ("structure.inspect_coordination_crystalnn", "structure.crystal", "structure.coordination_crystalnn"),
        ("structure.inspect_coordination_voronoi", "structure.crystal", "structure.coordination_voronoinn"),
        ("trajectory.compute_rdf", "trajectory.atomic", "trajectory.rdf"),
        ("electronic.inspect_band", "electronic.band_structure", "electronic.band_structure"),
        ("electronic.inspect_dos", "electronic.dos", "electronic.dos"),
        ("ml.evaluate_uncertainty", "materials.table", "ml.uncertainty_evaluation"),
        ("ml.evaluate_classification", "materials.table", "ml.classification_evaluation"),
        ("structure.inspect", "structure.crystal", "structure.summary"),
        ("structure.inspect_view", "structure.crystal", "structure.viewer_scene"),
        ("trajectory.inspect_view", "trajectory.atomic", "trajectory.viewer_scene"),
        ("data.explore_composition_space", "materials.dataset", "data.composition_space"),
        ("data.explore_materials", "materials.dataset", "data.materials_explorer"),
        ("volumetric.inspect", "volumetric.field", "volumetric.data"),
        (
            "structure.inspect_brillouin_zone",
            "structure.crystal",
            "structure.brillouin_zone",
        ),
    ],
)
def test_p10_c03_natural_requirement_resolves_to_deterministic_capability(requirement, object_type, capability):
    decision = request([(requirement, object_type)])
    resolution, snapshot = resolve(decision, [ref(object_type)])
    eligible = [item for item in resolution.candidates if item.capability_id == capability]
    assert len(eligible) == 1 and eligible[0].eligibility.value == "ELIGIBLE"
    plan = build_deterministic_capability_plan(decision=decision, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    CapabilityPlanValidator().validate(plan=plan, resolution=resolution, decision=decision, context=snapshot, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    context = {
        "dataset_id": "d",
        "profile_id": "p",
        "object_refs": {"obj_1": ref(object_type)},
        "resource_facts": {
            "obj_1": {
                "object_id": "table-object",
                "object_type": "DataFrame",
            }
        },
        "profile": {
            "semanticColumns": [
                {
                    "objectId": "table-object",
                    "column": "y_true",
                    "dtype": "float64",
                    "roles": [{"role": "regression_target"}],
                },
                {
                    "objectId": "table-object",
                    "column": "y_pred",
                    "dtype": "float64",
                    "roles": [{"role": "regression_prediction"}],
                },
                {
                    "objectId": "table-object",
                    "column": "uncertainty",
                    "dtype": "float64",
                    "roles": [{"role": "prediction_uncertainty"}],
                },
                {
                    "objectId": "table-object",
                    "column": "class_true",
                    "dtype": "string",
                    "roles": [{"role": "classification_target"}],
                },
                {
                    "objectId": "table-object",
                    "column": "class_pred",
                    "dtype": "string",
                    "roles": [{"role": "classification_prediction"}],
                },
                {
                    "objectId": "table-object",
                    "column": "probability",
                    "dtype": "float64",
                    "roles": [{"role": "class_probability"}],
                },
            ],
            "semanticGroups": [
                {
                    "groupId": "regression-group",
                    "kind": "regression",
                    "status": "COMPLETE",
                },
                {
                    "groupId": "classification-group",
                    "kind": "classification",
                    "status": "COMPLETE",
                },
            ],
        },
    }
    analysis, _ = CapabilityBinder(TOOLS).bind(
        capability_plan=plan,
        resolution=resolution,
        context=context,
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    assert analysis.schemaVersion == "0.2"
    assert analysis.steps[0].toolId == DEFAULT_AGENT2_REGISTRIES.capabilities.require(capability).tool_bindings[0].tool_id
    assert all(item.objectType != "RawUnsupported" for item in analysis.steps[0].inputRefs)


@pytest.mark.parametrize("wrong_type", ["electronic.dos", "materials.dataset", "trajectory.atomic"])
def test_p10_c12_wrong_object_type_fails_closed(wrong_type):
    resolution, _ = resolve(request([("electronic.inspect_band", wrong_type)]), [ref(wrong_type)])
    assert resolution.unsatisfied_required_requirement_ids == ["electronic.inspect_band"]
    assert resolution.candidates == []


@pytest.mark.parametrize("method,producer", [("crystalnn", "structure.coordination_crystalnn"), ("voronoi", "structure.coordination_voronoinn")])
def test_local_environment_requirement_binds_exact_neighbor_dependency(method, producer):
    source = ref("structure.crystal")
    decision = request([(f"structure.inspect_local_environment_{method}", "structure.crystal")])
    decision.scientific_requirements[0].constraints = {"site_indices": [0, 3]}
    resolution, snapshot = resolve(decision, [source])
    plan = build_deterministic_capability_plan(decision=decision, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    CapabilityPlanValidator().validate(plan=plan, resolution=resolution, decision=decision, context=snapshot, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    analysis, _ = CapabilityBinder(TOOLS).bind(
        capability_plan=plan, resolution=resolution, decision=decision,
        context={"dataset_id": "d", "profile_id": "p", "object_refs": {"obj_1": source}},
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    assert [step.toolId for step in analysis.steps] == [producer, "structure.local_environment_polyhedra"]
    assert "site_indices" not in analysis.steps[0].params
    assert analysis.steps[1].params["site_indices"] == [0, 3]
    assert all(step.inputRefs[0].ref == str(source.version_id) for step in analysis.steps)
    assert len(analysis.dependencyBindings) == 1
    dependency = analysis.dependencyBindings[0]
    assert dependency.producerStepId == analysis.steps[0].stepId
    assert dependency.consumerStepId == analysis.steps[1].stepId
    assert dependency.producerOutputPort == "coordination-table"
    assert dependency.consumerInputPort == "coordination"


@pytest.mark.parametrize("method", ["crystalnn", "voronoi"])
def test_polyhedron_request_coalesces_only_its_identical_coordination_scope(method):
    from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor
    decision = request([(f"structure.inspect_coordination_{method}", "structure.crystal"),
                        (f"structure.inspect_local_environment_{method}", "structure.crystal")])
    decision.scientific_requirements[1].subject_ref_keys = ["obj_1"]
    decision.selected_scope_ref_keys = ["obj_1"]
    decision.scientific_requirements[1].constraints = {"site_indices": [0]}
    before = decision.model_dump()
    normalized = AgentTurnProcessor._coalesce_local_environment_requirements(decision)
    assert decision.model_dump() == before
    assert [item.requirement_id for item in normalized.scientific_requirements] == [f"structure.inspect_local_environment_{method}"]
    resolution, snapshot = resolve(normalized, [ref("structure.crystal")])
    plan = build_deterministic_capability_plan(decision=normalized, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    assert len(plan.steps) == 1
    assert plan.steps[0].parameters == {"site_indices": [0]}
    for change in ("source", "constraints", "optional", "method"):
        separate = decision.model_copy(deep=True)
        if change == "source": separate.scientific_requirements[0].subject_ref_keys = ["obj_2"]
        elif change == "constraints": separate.scientific_requirements[0].constraints = {"cutoff": 3}
        elif change == "optional": separate.scientific_requirements[1].criticality = RequirementCriticality.OPTIONAL
        else: separate.scientific_requirements[0].requirement_id = f"structure.inspect_coordination_{'voronoi' if method == 'crystalnn' else 'crystalnn'}"
        assert AgentTurnProcessor._coalesce_local_environment_requirements(separate) == separate


def test_p10_c15_multi_capability_plan_keeps_exact_versions_and_typed_steps():
    band, dos = ref("electronic.band_structure", "band"), ref("electronic.dos", "dos")
    decision = ResearchTurnDecision(
        contract_version="1.0", action=ResearchAction.ANALYZE, assistant_message="Prepare analysis.", research_objective="Inspect electronic data",
        selected_scope_ref_keys=["obj_1", "obj_2"], scientific_requirements=[
            ProposedRequirement(requirement_id="electronic.inspect_band", criticality=RequirementCriticality.REQUIRED, subject_ref_keys=["obj_1"], constraints={}),
            ProposedRequirement(requirement_id="electronic.inspect_dos", criticality=RequirementCriticality.REQUIRED, subject_ref_keys=["obj_2"], constraints={}),
        ], reusable_result_ref_keys=[], clarification=None, confidence=OrchestratorConfidence.HIGH,
    )
    resolution, snapshot = resolve(decision, [band, dos])
    plan = build_deterministic_capability_plan(decision=decision, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    CapabilityPlanValidator().validate(plan=plan, resolution=resolution, decision=decision, context=snapshot, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    assert {resolution.candidates[int(step.capability_ref_key.removeprefix("cap_")) - 1].capability_id for step in plan.steps} == {"electronic.band_structure", "electronic.dos"}
    assert {step.input_bindings[next(iter(step.input_bindings))][0].source_ref_key for step in plan.steps} == {"obj_1", "obj_2"}


def _two_structure_rdf_request():
    decision = request([("structure.compute_rdf", "structure.crystal")])
    decision.selected_scope_ref_keys = ["obj_1", "obj_2"]
    decision.scientific_requirements[0].subject_ref_keys = ["obj_1", "obj_2"]
    sources = [ref("structure.crystal", "A"), ref("structure.crystal", "B")]
    resolution, snapshot = resolve(decision, sources)
    return decision, sources, resolution, snapshot


def test_multi_material_resolution_retains_every_requested_source():
    _decision, sources, resolution, _snapshot = _two_structure_rdf_request()
    candidate = next(item for item in resolution.candidates if item.capability_id == "structure.rdf")
    assert candidate.bound_source_ref_keys["structure"] == ["obj_1", "obj_2"]
    assert candidate.bound_source_inputs["structure"] == sources


def test_multi_material_plan_runs_each_exact_structure_separately():
    decision, sources, resolution, snapshot = _two_structure_rdf_request()
    plan = build_deterministic_capability_plan(decision=decision, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    assert len(plan.steps) == 2
    assert [step.input_bindings["structure"][0].source_ref_key for step in plan.steps] == ["obj_1", "obj_2"]
    CapabilityPlanValidator().validate(plan=plan, resolution=resolution, decision=decision, context=snapshot, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    analysis, _ = CapabilityBinder(TOOLS).bind(capability_plan=plan, resolution=resolution,
        context={"dataset_id": "d", "profile_id": "p", "object_refs": dict(zip(["obj_1", "obj_2"], sources))},
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    assert [step.inputRefs[0].ref for step in analysis.steps] == [str(source.version_id) for source in sources]


def test_planner_rejects_omitted_material_even_when_requirement_id_is_present():
    from mdi_api.agent2_errors import CapabilityPlanInvalid
    decision, _sources, resolution, snapshot = _two_structure_rdf_request()
    plan = build_deterministic_capability_plan(decision=decision, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    partial = plan.model_copy(update={"steps": plan.steps[:1]})
    with pytest.raises(CapabilityPlanInvalid, match="subject"):
        CapabilityPlanValidator().validate(plan=partial, resolution=resolution, decision=decision, context=snapshot, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)


def test_capability_sources_follow_their_requirement_not_another_same_type_source():
    decision = request([("structure.compute_rdf", "structure.crystal"), ("structure.inspect_coordination_hist", "structure.crystal")])
    resolution, _snapshot = resolve(decision, [ref("structure.crystal", "A"), ref("structure.crystal", "B")])
    rdf = next(item for item in resolution.candidates if item.capability_id == "structure.rdf")
    coordination = next(item for item in resolution.candidates if item.capability_id == "structure.coordination_hist")
    assert rdf.bound_source_ref_keys["structure"] == ["obj_1"]
    assert coordination.bound_source_ref_keys["structure"] == ["obj_2"]


def test_p10_c16_unknown_tool_is_not_agent_authority():
    assert not any(item.capability_id == "composition.formula_statistics" for item in DEFAULT_AGENT2_REGISTRIES.capabilities.list_all())
    assert "composition.formula_statistics" in {item.toolId for item in TOOLS.tools}


def test_p10_c04_trajectory_viewer_is_agent2_reachable_without_question_matching():
    decision = request([("trajectory.inspect_view", "trajectory.atomic")])
    resolution, snapshot = resolve(decision, [ref("trajectory.atomic")])
    candidate = next(
        item
        for item in resolution.candidates
        if item.capability_id == "trajectory.viewer_scene"
    )
    assert candidate.eligibility.value == "ELIGIBLE"
    plan = build_deterministic_capability_plan(
        decision=decision,
        resolution=resolution,
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    CapabilityPlanValidator().validate(
        plan=plan,
        resolution=resolution,
        decision=decision,
        context=snapshot,
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    analysis, _ = CapabilityBinder(TOOLS).bind(
        capability_plan=plan,
        resolution=resolution,
        context={
            "dataset_id": "d",
            "profile_id": "p",
            "object_refs": {"obj_1": ref("trajectory.atomic")},
        },
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    assert analysis.steps[0].toolId == "structure.trajectory_viewer"
    assert set(analysis.steps[0].output["artifactTypes"]) == {
        "trajectory_json",
        "trajectory_summary_json",
        "trajectory_report_json",
        "trajectory_manifest_json",
    }
    assert {item.type.value for item in analysis.expectedArtifacts} == {
        "trajectory_json",
        "trajectory_summary_json",
        "trajectory_report_json",
        "trajectory_manifest_json",
    }


def _trajectory_diffusion_plan(
    *,
    constraints: dict | None = None,
) -> tuple[ResearchTurnDecision, object, object, ScientificObjectRef]:
    trajectory = ref("trajectory.atomic", "canonical trajectory")
    decision = ResearchTurnDecision(
        contract_version="1.0",
        action=ResearchAction.ANALYZE,
        assistant_message="Prepare trajectory analysis.",
        research_objective="Calculate MSD and estimate diffusion over the supplied trajectory.",
        selected_scope_ref_keys=["obj_1"],
        scientific_requirements=[
            ProposedRequirement(
                requirement_id="trajectory.compute_msd",
                criticality=RequirementCriticality.REQUIRED,
                subject_ref_keys=["obj_1"],
                constraints={},
            ),
            ProposedRequirement(
                requirement_id="trajectory.estimate_diffusion",
                criticality=RequirementCriticality.REQUIRED,
                subject_ref_keys=["obj_1"],
                constraints=constraints or {},
            ),
        ],
        reusable_result_ref_keys=[],
        clarification=None,
        confidence=OrchestratorConfidence.HIGH,
    )
    resolution, snapshot = resolve(decision, [trajectory])
    plan = build_deterministic_capability_plan(
        decision=decision,
        resolution=resolution,
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    CapabilityPlanValidator().validate(
        plan=plan,
        resolution=resolution,
        decision=decision,
        context=snapshot,
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    return decision, resolution, plan, trajectory


def test_plan_context_projects_only_registered_exact_version_resource_facts():
    trajectory = ref("trajectory.atomic", "canonical trajectory")
    version = {
        "source_resource_refs_json": [
            {"project_id": "project", "dataset_id": "dataset"}
        ],
        "canonical_metadata_json": {
            "timeStartPs": 0.0,
            "timeEndPs": 48.675,
            "frameCount": 650,
            "payload": {"must": "not escape"},
        },
    }
    unit = SimpleNamespace(
        agent2=SimpleNamespace(
            scientific_objects=SimpleNamespace(
                get_version=lambda version_id: version
            )
        ),
        repositories=SimpleNamespace(
            datasets=SimpleNamespace(
                list_for_project=lambda project_id: [{"id": "dataset"}]
            ),
            data_profiles=SimpleNamespace(
                list_for_dataset=lambda dataset_id: [{"id": "profile", "datasetId": dataset_id}]
            ),
        ),
    )

    context = CapabilityPlanningProcessor(
        repository_factory=object(),
        tool_registry=TOOLS,
    )._plan_context(unit, "project", {"obj_1": trajectory})

    assert context["dataset_id"] == "dataset"
    assert context["profile_id"] == "profile"
    assert context["resource_facts"]["obj_1"] == {
        "object_id": str(trajectory.object_id),
        "version_id": str(trajectory.version_id),
        "object_type": "trajectory.atomic",
        "resource_id": None,
        "facts": {},
    }


def test_full_source_times_do_not_silently_bind_diffusion_fit_window():
    decision, resolution, plan, trajectory = _trajectory_diffusion_plan()
    with pytest.raises(CapabilityBindingFailed) as exc:
        CapabilityBinder(TOOLS).bind(
            capability_plan=plan,
            resolution=resolution,
            context={
                "dataset_id": "dataset",
                "profile_id": "profile",
                "object_refs": {"obj_1": trajectory},
                "resource_facts": {
                    "obj_1": {
                        "object_id": str(trajectory.object_id),
                        "version_id": str(trajectory.version_id),
                        "object_type": trajectory.object_type,
                        "facts": {"timeStartPs": 0.0, "timeEndPs": 48.675},
                    }
                },
            },
            registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
            decision=decision,
        )
    assert exc.value.code == "ANALYSIS_PLAN_VALIDATION_FAILED"


def test_explicit_diffusion_constraints_override_registered_resource_facts():
    decision, resolution, plan, trajectory = _trajectory_diffusion_plan(
        constraints={
            "fit_start_time_ps": 5.0,
            "fit_end_time_ps": 20.0,
        }
    )
    analysis, _ = CapabilityBinder(TOOLS).bind(
        capability_plan=plan,
        resolution=resolution,
        context={
            "dataset_id": "dataset",
            "profile_id": "profile",
            "object_refs": {"obj_1": trajectory},
            "resource_facts": {
                "obj_1": {
                    "object_id": str(trajectory.object_id),
                    "version_id": str(trajectory.version_id),
                    "object_type": trajectory.object_type,
                    "facts": {
                        "timeStartPs": 0.0,
                        "timeEndPs": 48.675,
                    },
                }
            },
        },
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
        decision=decision,
    )

    diffusion = next(
        step for step in analysis.steps if step.toolId == "trajectory.diffusion"
    )
    assert diffusion.params["fit_start_time_ps"] == 5.0
    assert diffusion.params["fit_end_time_ps"] == 20.0
    provenance = {item.parameter: item for item in diffusion.parameterProvenance}
    assert provenance["fit_start_time_ps"].origin == "USER_SPECIFIED"
    assert provenance["fit_end_time_ps"].origin == "USER_SPECIFIED"


def test_diffusion_without_explicit_fit_window_remains_fail_closed():
    decision, resolution, plan, trajectory = _trajectory_diffusion_plan()
    with pytest.raises(
        CapabilityBindingFailed,
    ) as exc:
        CapabilityBinder(TOOLS).bind(
            capability_plan=plan,
            resolution=resolution,
            context={
                "dataset_id": "dataset",
                "profile_id": "profile",
                "object_refs": {"obj_1": trajectory},
                "resource_facts": {
                    "obj_1": {
                        "object_id": str(trajectory.object_id),
                        "version_id": str(trajectory.version_id),
                        "object_type": trajectory.object_type,
                        "facts": {"timeStartPs": 0.0},
                    }
                },
            },
            registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
            decision=decision,
        )
    assert exc.value.code == "ANALYSIS_PLAN_VALIDATION_FAILED"


def test_structure_summary_and_view_request_plans_distinct_authoritative_steps() -> None:
    structure = ref("structure.crystal")
    decision = ResearchTurnDecision(
        contract_version="1.0",
        action=ResearchAction.ANALYZE,
        assistant_message="Prepare structure summary and viewer.",
        research_objective="Summarize the lattice and symmetry, then show the supported 3D viewer.",
        selected_scope_ref_keys=["obj_1"],
        scientific_requirements=[
            ProposedRequirement(
                requirement_id="structure.inspect",
                criticality=RequirementCriticality.REQUIRED,
                subject_ref_keys=["obj_1"],
                constraints={},
            ),
            ProposedRequirement(
                requirement_id="structure.inspect_view",
                criticality=RequirementCriticality.REQUIRED,
                subject_ref_keys=["obj_1"],
                constraints={},
            ),
        ],
        reusable_result_ref_keys=[],
        clarification=None,
        confidence=OrchestratorConfidence.HIGH,
    )
    resolution, snapshot = resolve(decision, [structure])

    summary = next(
        item
        for item in resolution.candidates
        if item.capability_id == "structure.summary"
    )
    viewer = next(
        item
        for item in resolution.candidates
        if item.capability_id == "structure.viewer_scene"
    )
    assert summary.satisfies_requirement_ids == ["structure.inspect"]
    assert viewer.satisfies_requirement_ids == ["structure.inspect_view"]

    plan = build_deterministic_capability_plan(
        decision=decision,
        resolution=resolution,
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    CapabilityPlanValidator().validate(
        plan=plan,
        resolution=resolution,
        decision=decision,
        context=snapshot,
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )
    analysis, _ = CapabilityBinder(TOOLS).bind(
        capability_plan=plan,
        resolution=resolution,
        context={
            "dataset_id": "d",
            "profile_id": "p",
            "object_refs": {"obj_1": structure},
        },
        registry=DEFAULT_AGENT2_REGISTRIES.capabilities,
    )

    assert [step.toolId for step in analysis.steps] == [
        "structure.summary",
        "structure.viewer_3d",
    ]
    assert {item.type.value for item in analysis.expectedArtifacts} == {"structure_json"}
    assert len(analysis.steps) == 2
    assert all(step.inputRefs for step in analysis.steps)


@pytest.mark.parametrize(
    ("projector_id", "payload"),
    [
        ("agent2.structure.coordination_hist", {"artifactType": "structure.coordination_hist", "schema_version": "phase10e1.coordination_hist.v1", "histogram": {"total_sites": 4}}),
        ("agent2.structure.coordination_crystalnn", {"artifactType": "structure.coordination_crystalnn", "schema_version": "phase10n1.crystalnn_coordination.v1", "coverage": {"successfulSites": 2}}),
        ("agent2.structure.coordination_voronoinn", {"artifactType": "structure.coordination_voronoinn", "schema_version": "phase10n1.voronoinn_coordination.v1", "coverage": {"successfulSites": 2}}),
        ("agent2.trajectory.rdf", {"artifactType": "trajectory.rdf", "schema_version": "phase10n4.trajectory_rdf.v1"}),
        ("agent2.electronic.band_structure", {"artifactType": "electronic.band_structure", "schemaVersion": "phase10n5.electronic_band_structure.v1", "energy": {"reference": "source_absolute"}, "spin": {"mode": "non_spin_polarized"}, "gap": {"valueEv": 1.2}, "coverage": {"kpointCount": 4}}),
        ("agent2.electronic.dos", {"artifactType": "electronic.dos", "schemaVersion": "phase10n5.electronic_dos.v1", "energy": {"reference": "source_absolute"}, "spin": {"mode": "non_spin_polarized"}, "dosUnitSemantic": "states_per_ev", "projectionCompleteness": "total_only", "coverage": {"energyPointCount": 8}}),
        (
            "agent2.structure.summary",
            {
                "schemaVersion": "phase10c1.structure_summary.v2",
                "artifactType": "structure.summary",
                "structureCount": 1,
                "structures": [
                    {
                        "structureId": "NaCl",
                        "formula": "Na1 Cl1",
                        "reducedFormula": "NaCl",
                        "numSites": 2,
                        "lattice": {
                            "a": 5.64,
                            "b": 5.64,
                            "c": 5.64,
                            "alpha": 90,
                            "beta": 90,
                            "gamma": 90,
                            "volume": 179.4,
                        },
                        "symmetry": {
                            "engine": "pymatgen/spglib",
                            "symprecAngstrom": 0.01,
                            "angleToleranceDegrees": 5.0,
                            "spacegroupNumber": 225,
                            "spacegroupSymbol": "Fm-3m",
                            "crystalSystem": "cubic",
                        },
                    }
                ],
            },
        ),
        ("agent2.data.composition_space", {"artifactType": "dataset.composition_space", "schemaVersion": "phase10k4.composition_space.v1"}),
        ("agent2.data.materials_explorer", {"artifactType": "dataset.materials_explorer", "schemaVersion": "phase10k2.dataset_materials_explorer.v1"}),
        ("agent2.volumetric.data", {"schema_version": "phase10j.volumetric_field.v1", "field_name": "scalar"}),
    ],
)
def test_p10_c17_new_projectors_require_verified_schema_and_preserve_exact_source(projector_id, payload):
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == projector_id)
    bundle = projector.project(_context(payload, projector_id)).bundle
    assert bundle.source_object_refs[0].version_id
    assert bundle.result_items and bundle.evidence


def test_p10_composition_space_projects_bounded_scalar_facts() -> None:
    projector = next(
        item
        for item in build_canonical_result_projectors()
        if item.projector_id == "agent2.data.composition_space"
    )
    payload = {
        "artifactType": "dataset.composition_space",
        "schemaVersion": "phase10k4.composition_space.v1",
        "coverage": {
            "selectedRows": 576,
            "validCompositionSamples": 576,
            "invalidCompositionSamples": 0,
        },
        "featureRepresentation": {"featureDimensions": 3},
        "projection": {
            "dimensions": 2,
            "rank": 2,
            "cumulativeExplainedVarianceRatio": 0.91,
        },
    }

    bundle = projector.project(_context(payload, projector.projector_id)).bundle

    facts = {item.predicate: item for item in bundle.facts}
    assert facts["composition.selected_row_count"].value == 576
    assert facts["composition.valid_sample_count"].value == 576
    assert facts["composition.invalid_sample_count"].value == 0
    assert facts["composition.feature_dimension_count"].value == 3
    assert facts["composition.projection_dimension_count"].value == 2
    assert facts["composition.projection_rank"].value == 2
    assert facts["composition.cumulative_explained_variance_ratio"].value == 0.91
    assert set(bundle.result_items[0].fact_refs) == {item.fact_id for item in bundle.facts}
    assert set(bundle.evidence[0].supports_fact_refs) == {item.fact_id for item in bundle.facts}


def test_structure_summary_projects_authoritative_lattice_and_symmetry_facts() -> None:
    projector = next(
        item
        for item in build_canonical_result_projectors()
        if item.projector_id == "agent2.structure.summary"
    )
    payload = {
        "schemaVersion": "phase10c1.structure_summary.v2",
        "artifactType": "structure.summary",
        "structureCount": 1,
        "structures": [
            {
                "structureId": "magnetite",
                "formula": "Fe24 O32",
                "reducedFormula": "Fe3O4",
                "numSites": 56,
                "lattice": {
                    "a": 8.394,
                    "b": 8.394,
                    "c": 8.394,
                    "alpha": 90.0,
                    "beta": 90.0,
                    "gamma": 90.0,
                    "volume": 591.456,
                },
                "symmetry": {
                    "engine": "pymatgen/spglib",
                    "symprecAngstrom": 0.01,
                    "angleToleranceDegrees": 5.0,
                    "spacegroupNumber": 227,
                    "spacegroupSymbol": "Fd-3m",
                    "crystalSystem": "cubic",
                },
            }
        ],
    }

    from dataclasses import replace
    context = _context(payload, projector.projector_id)
    # The authoritative summary must stand alone, without redundant companion tools.
    context = replace(context, artifacts=context.artifacts[:1], tool_calls=())
    bundle = projector.project(context).bundle
    facts = {item.predicate: item for item in bundle.facts}

    assert facts["structure.reduced_formula"].value == "Fe3O4"
    assert facts["structure.site_count"].value == 56
    assert facts["structure.lattice_a"].value == 8.394
    assert facts["structure.lattice_volume"].unit == "angstrom^3"
    assert facts["structure.spacegroup_number"].value == 227
    assert facts["structure.spacegroup_symbol"].value == "Fd-3m"
    assert facts["structure.crystal_system"].value == "cubic"
    assert set(bundle.result_items[0].fact_refs) == {
        item.fact_id for item in bundle.facts
    }
    assert set(bundle.evidence[0].supports_fact_refs) == {
        item.fact_id for item in bundle.facts
    }


def test_p10_c25_malformed_new_schema_fails_closed():
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.electronic.band_structure")
    with pytest.raises(Exception):
        projector.project(_context({"artifactType": "wrong", "schemaVersion": "phase10n5.electronic_band_structure.v1"}, projector.projector_id))
