from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mdi_api.agent2_errors import RegistryValidationError
from mdi_api.research_agent.capabilities.registry import InMemoryCapabilityRegistry
from mdi_api.research_agent.requirements.registry import InMemoryScientificRequirementRegistry
from mdi_api.research_agent.schemas import CapabilityStatus
from mdi_api.research_agent.progress.registry import InMemoryScientificProgressProjectorRegistry
from mdi_api.scientific_objects.registry import InMemoryObjectTypeRegistry, build_default_object_type_registry
from mdi_api.scientific_results.projectors.registry import InMemoryScientificResultProjectorRegistry


@dataclass(frozen=True)
class Agent2Registries:
    object_types: InMemoryObjectTypeRegistry
    requirements: InMemoryScientificRequirementRegistry
    capabilities: InMemoryCapabilityRegistry
    result_projectors: InMemoryScientificResultProjectorRegistry
    progress_projectors: InMemoryScientificProgressProjectorRegistry


def build_default_agent2_registries() -> Agent2Registries:
    return Agent2Registries(
        object_types=build_default_object_type_registry(),
        requirements=InMemoryScientificRequirementRegistry(),
        capabilities=InMemoryCapabilityRegistry(),
        result_projectors=InMemoryScientificResultProjectorRegistry(),
        progress_projectors=InMemoryScientificProgressProjectorRegistry(),
    )


DEFAULT_AGENT2_REGISTRIES = build_default_agent2_registries()


def validate_agent2_registries(registries: Agent2Registries, tool_registry: Any) -> None:
    """Validate only registered capability manifests; Phase 1 registers none by default."""

    for capability in registries.capabilities.list_all():
        for requirement_id in capability.satisfies_requirements:
            if not registries.requirements.contains(requirement_id):
                raise RegistryValidationError(f"Unknown requirement: {requirement_id}")
        for slot in capability.input_slots:
            for object_type in slot.accepted_object_types:
                if registries.object_types.get(object_type) is None:
                    raise RegistryValidationError(f"Unknown input object type: {object_type}")
        for slot in capability.output_slots:
            if registries.object_types.get(slot.object_type) is None:
                raise RegistryValidationError(f"Unknown output object type: {slot.object_type}")
        if capability.status == CapabilityStatus.ACTIVE and not capability.tool_bindings:
            raise RegistryValidationError(f"ACTIVE capability has no ToolBinding: {capability.capability_id}")
        for binding in capability.tool_bindings:
            try:
                tool_registry.get_tool_by_id(binding.tool_id)
            except KeyError as exc:
                raise RegistryValidationError(f"Unknown ToolBinding tool_id: {binding.tool_id}") from exc
        if not registries.result_projectors.contains(capability.result_projector):
            raise RegistryValidationError(f"Unknown result projector: {capability.result_projector}")
        if not registries.progress_projectors.contains(capability.progress_projector):
            raise RegistryValidationError(f"Unknown progress projector: {capability.progress_projector}")
