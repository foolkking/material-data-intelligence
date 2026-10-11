"""Explicit registry authority for scientific tools that need no material."""

from __future__ import annotations

from typing import Iterable

from mdi_schemas import PlatformReferenceSource, RegisteredTool
from mdi_schemas.project_planning import PlatformReferenceDescription


def project_tool_references(tool: RegisteredTool) -> list[PlatformReferenceSource]:
    if tool.source.get("execution_scope") != "project":
        raise ValueError(f"Tool {tool.toolId} requires material scope.")
    if tool.inputSchema.inputOptions:
        raise ValueError("Project tools cannot declare material input options.")
    references = [PlatformReferenceSource.model_validate(item) for item in tool.source.get("reference_sources", [])]
    identities = [item.referenceId for item in references]
    if identities != sorted(set(identities)):
        raise ValueError("Tool platform references must be unique and sorted.")
    return references


def project_reference_inventory(tools: Iterable[RegisteredTool]) -> list[PlatformReferenceSource]:
    sources: dict[str, PlatformReferenceSource] = {}
    for tool in tools:
        for source in project_tool_references(tool):
            if source.referenceId in sources and sources[source.referenceId] != source:
                raise ValueError("Project tools declare conflicting platform reference versions.")
            sources[source.referenceId] = source
    return [sources[key] for key in sorted(sources)]


def project_reference_descriptions(tools: Iterable[RegisteredTool]) -> list[PlatformReferenceDescription]:
    from .element_reference import ELEMENT_REFERENCE_SOURCE, element_reference_description
    from .project_parameters import SI_REFERENCE_SOURCE, si_reference_description

    descriptions = []
    for source in project_reference_inventory(tools):
        if source == ELEMENT_REFERENCE_SOURCE:
            descriptions.append(element_reference_description())
        elif source == SI_REFERENCE_SOURCE:
            descriptions.append(si_reference_description())
        else:
            raise ValueError("The registered platform reference has no installed description.")
    return descriptions
