from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from mdi_adapters.registry import ADAPTER_CLASSES
from mdi_api.agent2_errors import CapabilityResolutionFailed
from mdi_api.research_agent.capabilities.extension_validation import (
    validate_capability_extension_platform,
)
from mdi_api.research_agent.capabilities.packs import (
    CapabilityExtensionRegistry,
    build_phase11_packs,
)
from mdi_api.research_agent.capabilities.registry import InMemoryCapabilityRegistry
from mdi_api.research_agent.capabilities.resolver import CapabilityResolutionService
from mdi_api.research_agent.orchestration.schemas import (
    OrchestratorConfidence,
    ProposedRequirement,
    ResearchTurnDecision,
)
from mdi_api.research_agent.registry_validation import (
    Agent2Registries,
    build_default_agent2_registries,
)
from mdi_api.research_agent.schemas import (
    CapabilityPrecondition,
    CapabilitySurfaceSupport,
    RequirementCriticality,
    ResearchAction,
)
from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_api.scientific_viewers.registry import build_scientific_viewer_registry
from mdi_tool_registry import (
    AdapterNameInvocability,
    ToolRegistry,
    build_artifact_compatibility_matrix,
    load_manifests,
)


TOOLS = load_manifests()


def _registries_with(capability_id: str, **updates: object) -> Agent2Registries:
    source = build_default_agent2_registries()
    capabilities = InMemoryCapabilityRegistry()
    for manifest in source.capabilities.list_all():
        capabilities.register(
            manifest.model_copy(update=updates)
            if manifest.capability_id == capability_id
            else manifest
        )
    extension = CapabilityExtensionRegistry(
        packs=build_phase11_packs(capabilities.list_all())
    )
    return Agent2Registries(
        object_types=source.object_types,
        requirements=source.requirements,
        capabilities=capabilities,
        result_projectors=source.result_projectors,
        progress_projectors=source.progress_projectors,
        extension_registry=extension,
    )


def _report(
    registries: Agent2Registries | None = None,
    tools: ToolRegistry = TOOLS,
    *,
    adapters: set[str] | None = None,
):
    names = set(ADAPTER_CLASSES) if adapters is None else adapters
    return validate_capability_extension_platform(
        registries or build_default_agent2_registries(),
        tools,
        viewer_registry=build_scientific_viewer_registry(),
        adapter_invocability=AdapterNameInvocability(names),
        adapter_names=names,
    )


def test_canonical_extension_graph_is_complete_and_inventory_is_registry_derived():
    report = _report()
    assert report.accepted
    assert report.error_count == 0
    assert report.capability_count == 27
    assert report.valid_capability_count == 27
    assert report.incomplete_capability_count == 0
    assert report.pack_count == 5
    assert report.tool_count == 62
    assert report.adapter_count == 50
    assert report.duplicate_capability_authority_count == 0
    assert len(report.inventory_fingerprint) == 64
    assert {
        "structure.rdf",
        "diffraction.theoretical_xrd",
        "trajectory.msd",
        "electronic.band_structure",
        "data.materials_explorer",
        "ml.regression_evaluation",
        "phonon.band",
    }.issubset({item.capability_id for item in report.capabilities})


def test_missing_tool_and_adapter_are_reported_as_structural_errors():
    missing_tool = _registries_with(
        "structure.rdf",
        tool_bindings=[
            build_default_agent2_registries()
            .capabilities.require("structure.rdf")
            .tool_bindings[0]
            .model_copy(update={"tool_id": "missing.tool"})
        ],
    )
    report = _report(missing_tool)
    assert not report.accepted
    assert "MISSING_TOOL" in {item.code for item in report.issues}

    target = TOOLS.get_tool_by_id("structure.rdf")
    broken_tools = ToolRegistry(
        version=TOOLS.version,
        tools=tuple(
            tool.model_copy(update={"adapter": "MissingScientificAdapter"})
            if tool.toolId == target.toolId
            else tool
            for tool in TOOLS.tools
        ),
    )
    report = _report(tools=broken_tools)
    assert not report.accepted
    assert "MISSING_ADAPTER" in {item.code for item in report.issues}


@pytest.mark.parametrize(
    ("updates", "expected_code"),
    [
        (
            {
                "input_slots": [
                    build_default_agent2_registries()
                    .capabilities.require("structure.rdf")
                    .input_slots[0]
                    .model_copy(update={"accepted_object_types": ["unknown.science"]})
                ]
            },
            "UNKNOWN_SCIENTIFIC_INPUT_TYPE",
        ),
        (
            {
                "preconditions": [
                    CapabilityPrecondition(predicate_id="unknown.precondition")
                ]
            },
            "UNKNOWN_PRECONDITION",
        ),
        ({"result_projector": "missing.projector"}, "MISSING_RESULT_PROJECTOR"),
        (
            {"artifact_port_support": CapabilitySurfaceSupport.REQUIRED},
            "MISSING_ARTIFACT_PORTS",
        ),
    ],
)
def test_extension_validator_fails_closed_on_incomplete_contracts(updates, expected_code):
    report = _report(_registries_with("structure.rdf", **updates))
    assert not report.accepted
    assert expected_code in {item.code for item in report.issues}


def test_optional_presentation_surfaces_are_explicit_and_consistent():
    manifest = build_default_agent2_registries().capabilities.require("structure.rdf")
    generic = manifest.model_copy(
        update={
            "viewer_support": CapabilitySurfaceSupport.GENERIC,
            "interpretation_support": CapabilitySurfaceSupport.GENERIC,
            "report_support": CapabilitySurfaceSupport.NONE,
        }
    )
    assert generic.viewer_bindings == []
    assert generic.interpretation_profile is None
    assert generic.report_projector is None

    with pytest.raises(ValidationError):
        type(manifest).model_validate(
            {
                **manifest.model_dump(mode="json"),
                "viewer_support": "REQUIRED",
                "viewer_bindings": [],
            }
        )
    with pytest.raises(ValidationError):
        type(manifest).model_validate(
            {
                **manifest.model_dump(mode="json"),
                "interpretation_support": "SUPPORTED",
                "interpretation_profile": None,
            }
        )
    with pytest.raises(ValidationError):
        type(manifest).model_validate(
            {
                **manifest.model_dump(mode="json"),
                "report_support": "REQUIRED",
                "report_projector": None,
            }
        )


def test_multistep_artifact_ports_validate_before_execution():
    matrix = build_artifact_compatibility_matrix(
        TOOLS,
        selected_tool_ids=["trajectory.diffusion", "trajectory.msd"],
    )
    compatible = [
        item
        for item in matrix.pairs
        if item.producerToolId == "trajectory.msd"
        and item.consumerToolId == "trajectory.diffusion"
    ]
    assert len(compatible) == 1
    assert compatible[0].compatible
    assert compatible[0].artifactContractVersion == "phase10n4.trajectory_msd.v1"


def test_planner_catalog_is_bounded_scientific_and_traceable():
    extension = build_default_agent2_registries().extension_registry
    assert extension is not None
    catalog = extension.eligible_catalog()
    assert len(catalog) == 27
    assert all(len(item["contract_fingerprint"]) == 64 for item in catalog)
    assert all("surface_support" in item for item in catalog)
    assert all("scientific_quality" in item for item in catalog)
    assert all(
        item["scientific_quality"]["level"] != "STRUCTURAL_ONLY"
        for item in catalog
    )
    assert all(
        "evidence_refs" not in item["scientific_quality"]
        and "test_node" not in item["scientific_quality"]
        for item in catalog
    )
    assert all("tool_bindings" not in item and "adapter" not in item for item in catalog)


def test_orphans_are_classified_without_becoming_cleanup_authority():
    report = _report()
    orphan_by_id = {item.component_id: item for item in report.orphans}
    assert orphan_by_id["structure.trajectory_import"].classification == "PUBLIC_LOW_LEVEL_TOOL"
    assert all(item.classification != "DEFECT" for item in report.orphans)


def test_capability_resolution_rejects_cross_project_source_before_planning():
    registries = build_default_agent2_registries()
    source = ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id="other-project",
        object_type="structure.crystal",
        display_name="Unauthorized",
    )
    decision = ResearchTurnDecision(
        contract_version="1.0",
        action=ResearchAction.ANALYZE,
        assistant_message="Prepare analysis.",
        research_objective="Compute RDF",
        selected_scope_ref_keys=["obj_1"],
        scientific_requirements=[
            ProposedRequirement(
                requirement_id="structure.compute_rdf",
                criticality=RequirementCriticality.REQUIRED,
                subject_ref_keys=["obj_1"],
                constraints={},
            )
        ],
        reusable_result_ref_keys=[],
        clarification=None,
        confidence=OrchestratorConfidence.HIGH,
    )
    service = CapabilityResolutionService(
        registries.capabilities,
        registries.requirements,
        TOOLS,
    )
    with pytest.raises(CapabilityResolutionFailed, match="project scope"):
        service.resolve(
            turn={"id": uuid4(), "project_id": "current-project"},
            decision=decision,
            context_snapshot={"selection_refs_json": [source.model_dump(mode="json")]},
        )
