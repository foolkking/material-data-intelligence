from __future__ import annotations

from typing import Protocol

from mdi_api.agent2_errors import RequirementNotRegistered
from mdi_api.research_agent.schemas import RequirementManifest


class ScientificRequirementRegistry(Protocol):
    def register(self, manifest: RequirementManifest) -> None: ...
    def require(self, requirement_id: str) -> RequirementManifest: ...
    def contains(self, requirement_id: str) -> bool: ...


class InMemoryScientificRequirementRegistry:
    def __init__(self) -> None:
        self._manifests: dict[str, RequirementManifest] = {}

    def register(self, manifest: RequirementManifest) -> None:
        if manifest.requirement_id in self._manifests:
            raise ValueError(f"Duplicate requirement: {manifest.requirement_id}")
        self._manifests[manifest.requirement_id] = manifest

    def require(self, requirement_id: str) -> RequirementManifest:
        try:
            return self._manifests[requirement_id]
        except KeyError as exc:
            raise RequirementNotRegistered(requirement_id) from exc

    def contains(self, requirement_id: str) -> bool:
        return requirement_id in self._manifests
