from __future__ import annotations

from uuid import uuid4

import pytest

from mdi_api.research_agent.capabilities.preconditions import build_default_precondition_registry
from mdi_api.research_agent.capabilities.resolver import CapabilityResolutionService
from mdi_api.research_agent.orchestration.schemas import OrchestratorConfidence, ProposedRequirement, ResearchTurnDecision
from mdi_api.research_agent.planning.binder import CapabilityBinder
from mdi_api.research_agent.planning.deterministic import build_deterministic_capability_plan
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
    "data.composition_space",
    "data.materials_explorer",
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
    return ScientificResultProjectionContext(
        project_id="project", research_session_id="session", research_turn_id=str(uuid4()), research_question="Inspect this data",
        execution_summary={"outcome": "SUCCESS", "job_id": "job-1", "analysis_plan_id": "plan-1"},
        capability_plan={"steps": [{"step_id": "step_1", "capability_id": projector_id.removeprefix("agent2."), "capability_version": "1.0", "parameters": {}}]},
        analysis_plan={"schemaVersion": "0.2"}, tool_calls=(),
        artifacts=({"id": artifact_id, "contentType": "application/json", "filename": "phase10.json"},),
        artifact_payloads={artifact_id: payload}, source_object_refs=(source,),
    )


def test_p10_c01_batch_is_frozen_and_spans_families():
    manifests = DEFAULT_AGENT2_REGISTRIES.capabilities.list_all()
    assert NEW_CAPABILITIES.issubset({item.capability_id for item in manifests})
    assert len(NEW_CAPABILITIES) == 8
    assert {item.domain for item in manifests if item.capability_id in NEW_CAPABILITIES} >= {"structure", "trajectory", "electronic", "data"}


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
        ("data.explore_composition_space", "materials.dataset", "data.composition_space"),
        ("data.explore_materials", "materials.dataset", "data.materials_explorer"),
    ],
)
def test_p10_c03_natural_requirement_resolves_to_deterministic_capability(requirement, object_type, capability):
    decision = request([(requirement, object_type)])
    resolution, snapshot = resolve(decision, [ref(object_type)])
    eligible = [item for item in resolution.candidates if item.capability_id == capability]
    assert len(eligible) == 1 and eligible[0].eligibility.value == "ELIGIBLE"
    plan = build_deterministic_capability_plan(decision=decision, resolution=resolution, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    CapabilityPlanValidator().validate(plan=plan, resolution=resolution, decision=decision, context=snapshot, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    analysis, _ = CapabilityBinder(TOOLS).bind(capability_plan=plan, resolution=resolution, context={"dataset_id": "d", "profile_id": "p", "object_refs": {"obj_1": ref(object_type)}}, registry=DEFAULT_AGENT2_REGISTRIES.capabilities)
    assert analysis.schemaVersion == "0.2"
    assert analysis.steps[0].toolId == DEFAULT_AGENT2_REGISTRIES.capabilities.require(capability).tool_bindings[0].tool_id


@pytest.mark.parametrize("wrong_type", ["electronic.dos", "materials.dataset", "trajectory.atomic"])
def test_p10_c12_wrong_object_type_fails_closed(wrong_type):
    resolution, _ = resolve(request([("electronic.inspect_band", wrong_type)]), [ref(wrong_type)])
    assert resolution.unsatisfied_required_requirement_ids == ["electronic.inspect_band"]
    assert resolution.candidates == []


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


def test_p10_c16_unknown_tool_is_not_agent_authority():
    assert not any(item.capability_id == "composition.formula_statistics" for item in DEFAULT_AGENT2_REGISTRIES.capabilities.list_all())
    assert "composition.formula_statistics" in {item.toolId for item in TOOLS.tools}


@pytest.mark.parametrize(
    ("projector_id", "payload"),
    [
        ("agent2.structure.coordination_hist", {"artifactType": "structure.coordination_hist", "schema_version": "phase10e1.coordination_hist.v1", "histogram": {"total_sites": 4}}),
        ("agent2.structure.coordination_crystalnn", {"artifactType": "structure.coordination_crystalnn", "schema_version": "phase10n1.crystalnn_coordination.v1", "coverage": {"successfulSites": 2}}),
        ("agent2.structure.coordination_voronoinn", {"artifactType": "structure.coordination_voronoinn", "schema_version": "phase10n1.voronoinn_coordination.v1", "coverage": {"successfulSites": 2}}),
        ("agent2.trajectory.rdf", {"artifactType": "trajectory.rdf", "schema_version": "phase10n4.trajectory_rdf.v1"}),
        ("agent2.electronic.band_structure", {"artifactType": "electronic.band_structure", "schemaVersion": "phase10n5.electronic_band_structure.v1", "gap": {"valueEv": 1.2}, "coverage": {"kpointCount": 4}}),
        ("agent2.electronic.dos", {"artifactType": "electronic.dos", "schemaVersion": "phase10n5.electronic_dos.v1", "coverage": {"energyPointCount": 8}}),
        ("agent2.data.composition_space", {"artifactType": "dataset.composition_space", "schemaVersion": "phase10k4.composition_space.v1"}),
        ("agent2.data.materials_explorer", {"artifactType": "dataset.materials_explorer", "schemaVersion": "phase10k2.dataset_materials_explorer.v1"}),
    ],
)
def test_p10_c17_new_projectors_require_verified_schema_and_preserve_exact_source(projector_id, payload):
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == projector_id)
    bundle = projector.project(_context(payload, projector_id)).bundle
    assert bundle.source_object_refs[0].version_id
    assert bundle.result_items and bundle.evidence


def test_p10_c25_malformed_new_schema_fails_closed():
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.electronic.band_structure")
    with pytest.raises(Exception):
        projector.project(_context({"artifactType": "wrong", "schemaVersion": "phase10n5.electronic_band_structure.v1"}, projector.projector_id))
