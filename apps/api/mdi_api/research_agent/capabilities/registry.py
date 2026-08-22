from __future__ import annotations

from typing import Protocol

from mdi_api.agent2_errors import CapabilityNotRegistered
from mdi_api.research_agent.schemas import CapabilityManifest, CapabilityStatus


class CapabilityRegistry(Protocol):
    def register(self, manifest: CapabilityManifest) -> None: ...
    def require(self, capability_id: str, version: str | None = None) -> CapabilityManifest: ...
    def find_for_requirements(self, requirement_ids: list[str]) -> list[CapabilityManifest]: ...
    def list_active(self) -> list[CapabilityManifest]: ...


class InMemoryCapabilityRegistry:
    def __init__(self) -> None:
        self._manifests: dict[tuple[str, str], CapabilityManifest] = {}

    def register(self, manifest: CapabilityManifest) -> None:
        key = (manifest.capability_id, manifest.version)
        if key in self._manifests:
            raise ValueError(f"Duplicate capability: {manifest.capability_id}@{manifest.version}")
        self._manifests[key] = manifest

    def require(self, capability_id: str, version: str | None = None) -> CapabilityManifest:
        candidates = [item for (item_id, _), item in self._manifests.items() if item_id == capability_id]
        if version is not None:
            candidates = [item for item in candidates if item.version == version]
        if not candidates:
            raise CapabilityNotRegistered(f"{capability_id}@{version or 'latest'}")
        return sorted(candidates, key=lambda item: item.version)[-1]

    def find_for_requirements(self, requirement_ids: list[str]) -> list[CapabilityManifest]:
        required = set(requirement_ids)
        return sorted(
            (item for item in self._manifests.values() if required.issubset(set(item.satisfies_requirements))),
            key=lambda item: (item.capability_id, item.version),
        )

    def list_active(self) -> list[CapabilityManifest]:
        return sorted(
            (item for item in self._manifests.values() if item.status == CapabilityStatus.ACTIVE),
            key=lambda item: (item.capability_id, item.version),
        )

    def list_all(self) -> list[CapabilityManifest]:
        return sorted(self._manifests.values(), key=lambda item: (item.capability_id, item.version))
