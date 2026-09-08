from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from jsonschema import Draft202012Validator

from mdi_api.agent2_errors import RegistryValidationError
from mdi_api.research_agent.capabilities.registry import InMemoryCapabilityRegistry
from mdi_api.research_agent.capabilities.defaults import build_default_capability_registry
from mdi_api.research_agent.requirements.registry import InMemoryScientificRequirementRegistry, build_default_requirement_registry
from mdi_api.research_agent.schemas import CapabilityStatus
from mdi_api.research_agent.progress.registry import InMemoryScientificProgressProjectorRegistry
from mdi_api.scientific_objects.registry import InMemoryObjectTypeRegistry, build_default_object_type_registry
from mdi_api.application.scientific_results.projectors.registry import InMemoryScientificResultProjectorRegistry, build_default_result_projector_registry
from mdi_api.research_agent.capabilities.preconditions import build_default_precondition_registry
from mdi_api.research_agent.capabilities.versions import version_satisfies
from mdi_api.research_agent.execution.progress import GenericScientificProgressProjector
from mdi_api.research_agent.capabilities.packs import CapabilityExtensionRegistry, build_phase11_packs


@dataclass(frozen=True)
class Agent2Registries:
    object_types: InMemoryObjectTypeRegistry
    requirements: InMemoryScientificRequirementRegistry
    capabilities: InMemoryCapabilityRegistry
    result_projectors: InMemoryScientificResultProjectorRegistry
    progress_projectors: InMemoryScientificProgressProjectorRegistry
    extension_registry: CapabilityExtensionRegistry | None = None


def build_default_agent2_registries() -> Agent2Registries:
    result_projectors = build_default_result_projector_registry()
    progress_projectors = InMemoryScientificProgressProjectorRegistry()
    progress_projectors.register("agent2.fixture.progress", GenericScientificProgressProjector())
    capabilities = build_default_capability_registry()
    extension_registry = CapabilityExtensionRegistry(packs=build_phase11_packs(capabilities.list_all()))
    return Agent2Registries(
        object_types=build_default_object_type_registry(),
        requirements=build_default_requirement_registry(),
        capabilities=capabilities,
        result_projectors=result_projectors,
        progress_projectors=progress_projectors,
        extension_registry=extension_registry,
    )


DEFAULT_AGENT2_REGISTRIES = build_default_agent2_registries()



def validate_agent2_registries(registries: Agent2Registries, tool_registry: Any) -> None:
    """Validate only registered capability manifests; Phase 1 registers none by default."""

    for requirement in registries.requirements.list_active():
        for object_type in requirement.accepted_object_types:
            if registries.object_types.get(object_type) is None:
                raise RegistryValidationError(f"Unknown requirement object type: {object_type}")
        try:
            Draft202012Validator.check_schema(requirement.constraint_schema)
        except Exception as exc:
            raise RegistryValidationError(f"Invalid requirement constraint schema: {requirement.requirement_id}") from exc

    for capability in registries.capabilities.list_all():
        preconditions = build_default_precondition_registry()
        for requirement_id in capability.satisfies_requirements:
            if not registries.requirements.contains(requirement_id):
                raise RegistryValidationError(f"Unknown requirement: {requirement_id}")
        for slot in capability.input_slots:
            for object_type in slot.accepted_object_types:
                produced_result_types = {
                    output.result_type
                    for registered in registries.capabilities.list_all()
                    for output in registered.output_slots
                }
                if registries.object_types.get(object_type) is None and object_type not in produced_result_types:
                    raise RegistryValidationError(f"Unknown input object type: {object_type}")
        for slot in capability.output_slots:
            output_type = slot.scientific_object_type or slot.object_type
            if output_type is not None and registries.object_types.get(output_type) is None:
                raise RegistryValidationError(f"Unknown output object type: {slot.object_type}")
        if capability.status == CapabilityStatus.ACTIVE and not capability.tool_bindings:
            raise RegistryValidationError(f"ACTIVE capability has no ToolBinding: {capability.capability_id}")
        for binding in capability.tool_bindings:
            try:
                tool_registry.get_tool_by_id(binding.tool_id)
            except KeyError as exc:
                raise RegistryValidationError(f"Unknown ToolBinding tool_id: {binding.tool_id}") from exc
            if binding.conditions:
                raise RegistryValidationError(f"Executable string conditions are forbidden: {capability.capability_id}")
            if not version_satisfies(tool_registry.get_tool_by_id(binding.tool_id).version, binding.version_constraint):
                raise RegistryValidationError(f"Unsatisfied ToolBinding version: {binding.tool_id}@{binding.version_constraint}")
        for precondition in capability.preconditions:
            if not preconditions.contains(precondition.predicate_id):
                raise RegistryValidationError(f"Unknown precondition predicate: {precondition.predicate_id}")
        if not registries.result_projectors.contains(capability.result_projector):
            raise RegistryValidationError(f"Unknown result projector: {capability.result_projector}")
        if not registries.progress_projectors.contains(capability.progress_projector):
            raise RegistryValidationError(f"Unknown progress projector: {capability.progress_projector}")

    # Phase 11 extension boundary is validated against the same authorities as
    # the legacy registry.  Validation is all-or-nothing per Pack; the
    # resolver still consumes the existing CapabilityRegistry contract.
    if registries.extension_registry is not None:
        for pack in registries.extension_registry.list_packs():
            result = registries.extension_registry.validate_pack(
                pack,
                allow_existing=True,
                requirements=registries.requirements,
                object_types=registries.object_types,
                tool_registry=tool_registry,
                result_projectors=registries.result_projectors,
                progress_projectors=registries.progress_projectors,
            )
            if not result.accepted:
                raise RegistryValidationError("; ".join(result.errors))
