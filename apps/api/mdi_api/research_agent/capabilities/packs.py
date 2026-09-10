"""Trusted declarative Capability Pack boundary.

Packs are repository-owned data contracts.  They describe existing
CapabilityManifest values and deterministic bindings; they never load code,
imports, prompts, or user supplied executables.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mdi_api.agent2_errors import RegistryValidationError
from mdi_api.research_agent.capabilities.registry import InMemoryCapabilityRegistry
from mdi_api.research_agent.capabilities.versions import version_satisfies
from mdi_api.research_agent.schemas import CapabilityManifest, CapabilityStatus


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]{2,127}$")
_EXECUTABLE_UI_BINDING = re.compile(
    r"(?:https?://|^//|[<>]|javascript:|data:text/html|"
    r"(?:^|[._-])(?:component|import|module|script|html|css|url|remote)(?:$|[._-]))",
    re.IGNORECASE,
)


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


class CapabilityPackCapability(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    manifest: CapabilityManifest
    contract_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    binding_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def fingerprints_match(self) -> "CapabilityPackCapability":
        expected_contract = capability_contract_fingerprint(self.manifest)
        expected_binding = capability_binding_fingerprint(self.manifest)
        if self.contract_fingerprint != expected_contract:
            raise ValueError("contract fingerprint mismatch")
        if self.binding_fingerprint != expected_binding:
            raise ValueError("binding fingerprint mismatch")
        return self


class CapabilityPackManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    pack_id: str = Field(pattern=_IDENTIFIER.pattern)
    pack_version: str = Field(min_length=1, max_length=32)
    manifest_schema_version: str = Field(default="1.0", pattern=r"^1\.0$")
    display_metadata: dict[str, str] = Field(default_factory=dict)
    capabilities: list[CapabilityPackCapability] = Field(min_length=1)
    provenance_metadata: dict[str, str] = Field(default_factory=dict)
    compatibility: dict[str, str] = Field(default_factory=dict)


def capability_contract_fingerprint(manifest: CapabilityManifest) -> str:
    payload = manifest.model_dump(mode="json", exclude={"tool_bindings", "viewer_bindings", "result_projector", "progress_projector"})
    return _digest(payload)


def capability_binding_fingerprint(manifest: CapabilityManifest) -> str:
    payload = {
        "tool_bindings": [item.model_dump(mode="json") for item in manifest.tool_bindings],
        "result_projector": manifest.result_projector,
        "progress_projector": manifest.progress_projector,
        "viewer_bindings": list(manifest.viewer_bindings),
    }
    return _digest(payload)


def make_pack_capability(manifest: CapabilityManifest) -> CapabilityPackCapability:
    return CapabilityPackCapability(
        manifest=manifest,
        contract_fingerprint=capability_contract_fingerprint(manifest),
        binding_fingerprint=capability_binding_fingerprint(manifest),
    )


class PackValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    accepted: bool
    pack_id: str
    pack_version: str
    fingerprint: str
    errors: list[str] = Field(default_factory=list)


class CapabilityExtensionRegistry:
    """Atomic registry snapshot for trusted repository capability packs."""

    def __init__(self, *, packs: Iterable[CapabilityPackManifest] = ()) -> None:
        self._packs: dict[tuple[str, str], CapabilityPackManifest] = {}
        self._capabilities: dict[tuple[str, str], CapabilityManifest] = {}
        for pack in packs:
            self.register_pack(pack)

    @staticmethod
    def pack_fingerprint(pack: CapabilityPackManifest) -> str:
        return _digest(pack.model_dump(mode="json", exclude_none=True))

    def validate_pack(
        self,
        pack: CapabilityPackManifest,
        *,
        allow_existing: bool = False,
        requirements: Any | None = None,
        object_types: Any | None = None,
        tool_registry: Any | None = None,
        result_projectors: Any | None = None,
        progress_projectors: Any | None = None,
    ) -> PackValidationResult:
        errors: list[str] = []
        key = (pack.pack_id, pack.pack_version)
        if key in self._packs and (not allow_existing or self._packs[key] is not pack):
            errors.append("DUPLICATE_PACK_VERSION")
        seen: set[tuple[str, str]] = set()
        for item in pack.capabilities:
            manifest = item.manifest
            capability_key = (manifest.capability_id, manifest.version)
            existing_manifest = self._capabilities.get(capability_key)
            if capability_key in seen or (existing_manifest is not None and (not allow_existing or existing_manifest is not manifest)):
                errors.append(f"DUPLICATE_CAPABILITY:{manifest.capability_id}@{manifest.version}")
            seen.add(capability_key)
            if requirements is not None:
                for requirement_id in manifest.satisfies_requirements:
                    if not requirements.contains(requirement_id):
                        errors.append(f"UNKNOWN_REQUIREMENT:{requirement_id}")
            if object_types is not None:
                for slot in [*manifest.input_slots, *manifest.output_slots]:
                    for object_type in (slot.accepted_object_types if hasattr(slot, "accepted_object_types") else [slot.scientific_object_type or slot.object_type]):
                        produced_types = {
                            output.result_type
                            for registered in self._capabilities.values()
                            for output in registered.output_slots
                        }
                        if object_type and object_types.get(object_type) is None and object_type not in produced_types:
                            errors.append(f"UNKNOWN_OBJECT_TYPE:{object_type}")
            if tool_registry is not None:
                if manifest.status == CapabilityStatus.ACTIVE and not manifest.tool_bindings:
                    errors.append(f"MISSING_TOOL_BINDING:{manifest.capability_id}")
                for binding in manifest.tool_bindings:
                    try:
                        tool = tool_registry.get_tool_by_id(binding.tool_id)
                    except KeyError:
                        errors.append(f"UNKNOWN_TOOL:{binding.tool_id}")
                        continue
                    if binding.conditions:
                        errors.append(f"EXECUTABLE_CONDITION_FORBIDDEN:{manifest.capability_id}")
                    elif not version_satisfies(tool.version, binding.version_constraint):
                        errors.append(f"TOOL_VERSION_UNAVAILABLE:{binding.tool_id}")
            if (
                result_projectors is not None
                and manifest.result_support.value != "NONE"
                and (
                    not manifest.result_projector
                    or not result_projectors.contains(manifest.result_projector)
                )
            ):
                errors.append(f"UNKNOWN_RESULT_PROJECTOR:{manifest.result_projector}")
            if progress_projectors is not None and not progress_projectors.contains(manifest.progress_projector):
                errors.append(f"UNKNOWN_PROGRESS_PROJECTOR:{manifest.progress_projector}")
            for viewer_binding in manifest.viewer_bindings:
                if (
                    not _IDENTIFIER.fullmatch(viewer_binding)
                    or _EXECUTABLE_UI_BINDING.search(viewer_binding)
                ):
                    errors.append(
                        f"EXECUTABLE_VIEWER_BINDING_FORBIDDEN:{manifest.capability_id}"
                    )
        return PackValidationResult(
            accepted=not errors,
            pack_id=pack.pack_id,
            pack_version=pack.pack_version,
            fingerprint=self.pack_fingerprint(pack),
            errors=sorted(set(errors)),
        )

    def register_pack(self, pack: CapabilityPackManifest, **validation_kwargs: Any) -> PackValidationResult:
        result = self.validate_pack(pack, allow_existing=False, **validation_kwargs)
        if not result.accepted:
            raise RegistryValidationError("; ".join(result.errors))
        # Commit only after the complete pack has validated.
        self._packs[(pack.pack_id, pack.pack_version)] = pack
        for item in pack.capabilities:
            self._capabilities[(item.manifest.capability_id, item.manifest.version)] = item.manifest
        return result

    def list_packs(self) -> list[CapabilityPackManifest]:
        return [self._packs[key] for key in sorted(self._packs)]

    def list_capabilities(self) -> list[CapabilityManifest]:
        return [self._capabilities[key] for key in sorted(self._capabilities)]

    def require(self, capability_id: str, version: str | None = None) -> CapabilityManifest:
        candidates = [item for (item_id, item_version), item in self._capabilities.items() if item_id == capability_id and (version is None or item_version == version)]
        if not candidates:
            raise RegistryValidationError(f"Capability not registered: {capability_id}@{version or 'latest'}")
        return sorted(candidates, key=lambda item: item.version)[-1]

    def as_capability_registry(self) -> InMemoryCapabilityRegistry:
        registry = InMemoryCapabilityRegistry()
        for manifest in self.list_capabilities():
            registry.register(manifest)
        return registry

    def eligible_catalog(self, manifests: Iterable[CapabilityManifest] | None = None) -> list[dict[str, Any]]:
        """Compact Agent-facing catalog; binding implementation details stay out."""
        source = list(manifests) if manifests is not None else self.list_capabilities()
        return [
            {
                "capability_id": item.capability_id,
                "version": item.version,
                "domain": item.domain,
                "display_name": item.display_name,
                "scientific_purpose": item.scientific_purpose,
                "satisfies_requirements": sorted(item.satisfies_requirements),
                "input_slots": [slot.model_dump(mode="json") for slot in item.input_slots],
                "output_slots": [slot.model_dump(mode="json") for slot in item.output_slots],
                "limitations": list(item.limitations),
                "planner_visibility": item.planner_visibility.value,
                "surface_support": {
                    "result": item.result_support.value,
                    "artifact_ports": item.artifact_port_support.value,
                    "interpretation": item.interpretation_support.value,
                    "viewer": item.viewer_support.value,
                    "report": item.report_support.value,
                },
                "resource_profile": item.resource_profile.model_dump(mode="json"),
                "scientific_quality": {
                    "level": item.qualification.level,
                    "validated_domains": list(item.qualification.validated_domains),
                    "known_limitations": list(item.qualification.known_limitations[:3]),
                    "reproducibility": item.qualification.reproducibility,
                    "evidence_version": item.qualification.evidence_version,
                },
                "contract_fingerprint": capability_contract_fingerprint(item),
            }
            for item in source
            if item.status == CapabilityStatus.ACTIVE and item.planner_visibility.value == "VISIBLE"
        ]


def build_phase11_packs(manifests: Iterable[CapabilityManifest]) -> list[CapabilityPackManifest]:
    groups: dict[str, list[CapabilityManifest]] = {"core.structure": [], "core.electronic": [], "core.data": [], "core.trajectory": [], "core.other": []}
    for manifest in manifests:
        if manifest.domain == "structure":
            groups["core.structure"].append(manifest)
        elif manifest.domain == "electronic":
            groups["core.electronic"].append(manifest)
        elif manifest.domain == "data":
            groups["core.data"].append(manifest)
        elif manifest.domain == "trajectory":
            groups["core.trajectory"].append(manifest)
        else:
            groups["core.other"].append(manifest)
    return [
        CapabilityPackManifest(
            pack_id=pack_id,
            pack_version="1.0",
            display_metadata={"name": pack_id, "trust": "repository"},
            capabilities=[make_pack_capability(item) for item in items],
            provenance_metadata={"source": "agent2.phase10", "loader": "repository-defaults"},
        )
        for pack_id, items in sorted(groups.items())
        if items
    ]
