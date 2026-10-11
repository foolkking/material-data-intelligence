from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from mdi_api.agent2_errors import (
    CapabilityNotRegistered,
    RegistryValidationError,
    RequirementNotRegistered,
    ScientificObjectTypeNotRegistered,
)
from mdi_api.research_agent.capabilities.registry import InMemoryCapabilityRegistry
from mdi_api.research_agent.capabilities.defaults import build_default_capability_registry
from mdi_api.research_agent.progress.registry import InMemoryScientificProgressProjectorRegistry
from mdi_api.research_agent.registry_validation import Agent2Registries, validate_agent2_registries
from mdi_api.research_agent.requirements.registry import InMemoryScientificRequirementRegistry, build_default_requirement_registry
from mdi_api.research_agent.schemas import (
    CapabilityInputSlot,
    CapabilityManifest,
    CapabilityOutputSlot,
    CapabilityStatus,
    ContextResolutionStatus,
    RequirementManifest,
    ResolvedReference,
    ResolvedResearchContext,
    ScientificRequirement,
    ScientificRequirementSet,
    RequirementCriticality,
    RequirementOrigin,
    ToolBinding,
)
from mdi_api.research_agent.turns.state_machine import ALLOWED_TRANSITIONS, ensure_transition
from mdi_api.research_agent.schemas import ResearchTurnStatus
from mdi_api.scientific_objects.registry import InMemoryObjectTypeRegistry, build_default_object_type_registry
from mdi_api.scientific_objects.schemas import ObjectTypeManifest, ScientificObjectKind, ScientificObjectRef, StorageRef
from mdi_api.scientific_results.projectors.registry import InMemoryScientificResultProjectorRegistry
from mdi_api.scientific_results.schemas import (
    FactSourceLocator,
    ResultExecutionStatus,
    ResultRelevanceStatus,
    ScientificFact,
    ScientificResultBundle,
    ScientificResultItem,
    ScientificResultRole,
)
from mdi_tool_registry import ToolRegistry, list_tools
from jsonschema import Draft202012Validator


def object_ref(project_id: str = "project") -> ScientificObjectRef:
    return ScientificObjectRef(
        object_id=uuid4(), version_id=uuid4(), project_id=project_id,
        object_type="structure.crystal", display_name="Si",
    )


def capability(**overrides):
    values = {
        "capability_id": "agent2.fixture.structure",
        "version": "1.0",
        "domain": "structure",
        "display_name": "Fixture structure",
        "scientific_purpose": "Validate the Phase 1 registry boundary.",
        "satisfies_requirements": ["structure.inspect"],
        "input_slots": [CapabilityInputSlot(name="structure", accepted_object_types=["structure.crystal"])],
        "output_slots": [CapabilityOutputSlot(name="structure", object_type="structure.crystal")],
        "preconditions": [],
        "limitations": [],
        "tool_bindings": [ToolBinding(tool_id="structure.viewer_3d", version_constraint=">=0.1")],
        "viewer_bindings": [],
        "evidence_projector": None,
        "result_projector": "fixture.result",
        "report_projector": None,
        "progress_projector": "fixture.progress",
        "status": CapabilityStatus.ACTIVE,
    }
    values.update(overrides)
    return CapabilityManifest(**values)


def registries(manifest: CapabilityManifest | None = None) -> Agent2Registries:
    requirements = InMemoryScientificRequirementRegistry()
    requirements.register(RequirementManifest(requirement_id="structure.inspect", display_name="Inspect", description="Inspect a structure."))
    capabilities = InMemoryCapabilityRegistry()
    if manifest:
        capabilities.register(manifest)
    results = InMemoryScientificResultProjectorRegistry()
    results.register("fixture.result", lambda *_: None)
    progress = InMemoryScientificProgressProjectorRegistry()
    progress.register("fixture.progress", lambda *_: None)
    return Agent2Registries(build_default_object_type_registry(), requirements, capabilities, results, progress)


def test_contracts_forbid_extra_fields_and_invalid_values():
    with pytest.raises(ValidationError):
        ScientificObjectRef(**object_ref().model_dump(), extra_field=True)
    with pytest.raises(ValidationError):
        ScientificObjectRef(object_id="bad", version_id=uuid4(), project_id="p", object_type="structure.crystal")
    with pytest.raises(ValidationError):
        StorageRef(storage_backend="minio", object_key="x", checksum="abc", byte_size=-1)
    with pytest.raises(ValidationError):
        CapabilityInputSlot(name="x", accepted_object_types=["structure.crystal"], min_count=3, max_count=2)
    with pytest.raises(ValidationError):
        CapabilityManifest(**{**capability().model_dump(), "status": "UNKNOWN"})
    with pytest.raises(ValidationError):
        FactSourceLocator()


def test_resolved_context_enforces_ambiguity_authority_and_project_scope():
    ref = object_ref()
    with pytest.raises(ValidationError):
        ResolvedReference(phrase="it", candidate_ids=["a", "a"], selected_ref=None, status=ContextResolutionStatus.AMBIGUOUS)
    with pytest.raises(ValidationError):
        ResolvedReference(phrase="it", candidate_ids=["a"], selected_ref=ref, status=ContextResolutionStatus.UNAUTHORIZED)
    ambiguous = ResolvedReference(phrase="it", candidate_ids=["a", "b"], selected_ref=None, status=ContextResolutionStatus.AMBIGUOUS)
    with pytest.raises(ValidationError):
        ResolvedResearchContext(
            project_id="project", research_session_id="session", active_objects=[], selection_refs=[],
            resolved_references=[ambiguous], referenced_result_ids=[], research_goal=None,
            user_constraints=[], unresolved_questions=[], requires_clarification=False,
        )
    with pytest.raises(ValidationError):
        ResolvedResearchContext(
            project_id="other", research_session_id="session", active_objects=[ref], selection_refs=[],
            resolved_references=[], referenced_result_ids=[], research_goal=None,
            user_constraints=[], unresolved_questions=[], requires_clarification=False,
        )


def test_requirement_ids_duplicates_and_subject_projects_are_strict():
    requirement = ScientificRequirement(
        requirement_id="structure.inspect", criticality=RequirementCriticality.REQUIRED,
        subject_refs=[object_ref()], origin=RequirementOrigin.USER_EXPLICIT,
    )
    with pytest.raises(ValidationError):
        ScientificRequirementSet(objective="Inspect", requirements=[requirement, requirement], source_turn_id=uuid4())
    with pytest.raises(ValidationError):
        ScientificRequirementSet(
            objective="Inspect",
            requirements=[requirement, requirement.model_copy(update={"requirement_id": "structure.compare", "subject_refs": [object_ref("other")]})],
            source_turn_id=uuid4(),
        )


def test_result_bundle_keeps_execution_and_relevance_independent_and_validates_refs():
    ref = object_ref()
    fact = ScientificFact(
        fact_id="fact-1", predicate="has_value", subject_ref="Si", value=1.0,
        source=FactSourceLocator(scientific_object_ref=ref),
    )
    bundle = ScientificResultBundle(
        schema_version="1.0", result_id=uuid4(), project_id="project", research_session_id="session",
        research_turn_id=uuid4(), research_question="Inspect Si", source_object_refs=[ref],
        execution_status=ResultExecutionStatus.SUCCESS, relevance_status=ResultRelevanceStatus.STALE,
        result_items=[ScientificResultItem(
            id="item-1", result_type="fixture", role=ScientificResultRole.PRIMARY, title="Result",
            artifact_ids=[], scientific_object_refs=[ref], fact_refs=["fact-1"], evidence_refs=[],
        )],
        facts=[fact], figures=[], tables=[], output_object_refs=[], evidence=[], methods=[],
        limitations=[], warnings=[], provenance={}, projection_version="fixture/1.0",
    )
    assert bundle.execution_status == ResultExecutionStatus.SUCCESS
    assert bundle.relevance_status == ResultRelevanceStatus.STALE
    with pytest.raises(ValidationError):
        ScientificResultBundle.model_validate({**bundle.model_dump(), "result_items": [{**bundle.result_items[0].model_dump(), "fact_refs": ["missing"]}]})


def test_object_type_registry_and_startup_validation_fail_fast():
    object_types = InMemoryObjectTypeRegistry()
    manifest = ObjectTypeManifest(object_type="structure.crystal", kind=ScientificObjectKind.STRUCTURE, display_name="Crystal", schema_versions=["1.0"])
    object_types.register(manifest)
    with pytest.raises(ValueError):
        object_types.register(manifest)
    with pytest.raises(ScientificObjectTypeNotRegistered):
        object_types.require("structure.unknown")

    tools = ToolRegistry(version="test", tools=tuple(list_tools()))
    validate_agent2_registries(registries(capability()), tools)
    with pytest.raises(RegistryValidationError, match="Unknown requirement"):
        validate_agent2_registries(registries(capability(satisfies_requirements=["unknown.requirement"])), tools)
    with pytest.raises(RegistryValidationError, match="Unknown input object type"):
        validate_agent2_registries(registries(capability(input_slots=[CapabilityInputSlot(name="x", accepted_object_types=["unknown.object"])])), tools)
    with pytest.raises(RegistryValidationError, match="Unknown ToolBinding"):
        validate_agent2_registries(registries(capability(tool_bindings=[ToolBinding(tool_id="unknown.tool", version_constraint="1")])), tools)
    with pytest.raises(RegistryValidationError, match="no ToolBinding"):
        validate_agent2_registries(registries(capability(tool_bindings=[])), tools)
    validate_agent2_registries(registries(capability(status=CapabilityStatus.EXPERIMENTAL, tool_bindings=[])), tools)


def test_requirement_and_capability_registries_are_typed_and_fail_fast():
    requirements = InMemoryScientificRequirementRegistry()
    requirement = RequirementManifest(
        requirement_id="structure.inspect",
        display_name="Inspect",
        description="Inspect a structure.",
    )
    requirements.register(requirement)
    assert requirements.contains(requirement.requirement_id)
    with pytest.raises(ValueError, match="Duplicate requirement"):
        requirements.register(requirement)
    with pytest.raises(RequirementNotRegistered):
        requirements.require("structure.unknown")

    capabilities = InMemoryCapabilityRegistry()
    manifest = capability()
    capabilities.register(manifest)
    assert capabilities.require(manifest.capability_id, manifest.version) == manifest
    with pytest.raises(ValueError, match="Duplicate capability"):
        capabilities.register(manifest)
    with pytest.raises(CapabilityNotRegistered):
        capabilities.require("agent2.unknown")


def test_generic_coordination_requirement_is_covered_by_trusted_algorithm_capabilities():
    registry = build_default_capability_registry()
    crystalnn = registry.require("structure.coordination_crystalnn", "1.0")
    voronoi = registry.require("structure.coordination_voronoinn", "1.0")
    assert "structure.inspect_coordination" in crystalnn.satisfies_requirements
    assert "structure.inspect_coordination" in voronoi.satisfies_requirements


def test_dataset_requirements_accept_only_bounded_semantic_hints():
    manifest = build_default_requirement_registry().require("data.explore_materials")
    schema = manifest.constraint_schema
    assert set(schema["properties"]) == {"property", "sample"}
    assert not list(Draft202012Validator(schema).iter_errors({"property": "band_gap", "sample": "mat-2"}))
    assert list(Draft202012Validator(schema).iter_errors({"sql": "select * from materials"}))


def test_structure_rdf_requirement_preserves_bounded_range_and_bin_width():
    schema = build_default_requirement_registry().require("structure.compute_rdf").constraint_schema
    validator = Draft202012Validator(schema)
    for name in ("cutoff_angstrom", "r_max_angstrom"):
        assert not list(validator.iter_errors({name: 6.0, "bin_width_angstrom": 0.2}))
        for value in (0, 0.4, 31, "8", True):
            assert list(validator.iter_errors({name: value}))
    for value in (0, 0.009, 1.1, "0.2", True):
        assert list(validator.iter_errors({"bin_width_angstrom": value}))
    assert list(validator.iter_errors({"python": "arbitrary code"}))


def test_trajectory_requirements_accept_only_bounded_adapter_constraints():
    registry = build_default_requirement_registry()
    msd_schema = registry.require("trajectory.compute_msd").constraint_schema
    diffusion_schema = registry.require(
        "trajectory.estimate_diffusion"
    ).constraint_schema

    assert not list(
        Draft202012Validator(msd_schema).iter_errors(
            {"species": "Li", "drift_correction": "none"}
        )
    )
    assert list(
        Draft202012Validator(msd_schema).iter_errors(
            {"species": "Li", "python": "import os"}
        )
    )
    assert list(
        Draft202012Validator(msd_schema).iter_errors(
            {"species": "Li;rm -rf"}
        )
    )

    assert not list(
        Draft202012Validator(diffusion_schema).iter_errors(
            {
                "fit_start_time_ps": 1.0,
                "fit_end_time_ps": 6.0,
                "direction": "total",
                "minimum_r_squared": 0.9,
            }
        )
    )
    assert list(
        Draft202012Validator(diffusion_schema).iter_errors(
            {"fit_start_time_ps": -1.0, "fit_end_time_ps": 6.0}
        )
    )
    assert list(
        Draft202012Validator(diffusion_schema).iter_errors(
            {"fit_start_time_ps": 1.0, "fit_end_time_ps": 6.0, "sql": "SELECT 1"}
        )
    )


def test_state_machine_accepts_every_declared_edge_and_rejects_terminal_revival():
    for source, targets in ALLOWED_TRANSITIONS.items():
        for target in targets:
            ensure_transition(source, target)
    for source, target in (
        (ResearchTurnStatus.COMPLETED, ResearchTurnStatus.RUNNING),
        (ResearchTurnStatus.ANSWERED, ResearchTurnStatus.PLANNING),
        (ResearchTurnStatus.NEEDS_CLARIFICATION, ResearchTurnStatus.RUNNING),
    ):
        with pytest.raises(Exception):
            ensure_transition(source, target)

    for source in ResearchTurnStatus:
        for target in ResearchTurnStatus:
            if target not in ALLOWED_TRANSITIONS.get(source, frozenset()):
                with pytest.raises(Exception):
                    ensure_transition(source, target)
