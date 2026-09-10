"""Cross-registry validation and generated inventory for scientific capabilities.

The validator reads the existing Requirement, Capability Pack, Tool, Adapter,
Artifact-port, Result-projector and Viewer authorities.  It does not register
or execute scientific code and is intentionally unsuitable as a plugin loader.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from typing import Any, Iterable, Literal

from pydantic import BaseModel, ConfigDict, computed_field

from mdi_api.research_agent.capabilities.packs import capability_contract_fingerprint
from mdi_api.research_agent.capabilities.preconditions import build_default_precondition_registry
from mdi_api.research_agent.capabilities.versions import version_satisfies
from mdi_api.research_agent.schemas import (
    CapabilityPlannerVisibility,
    CapabilityStatus,
    CapabilitySurfaceSupport,
)
from mdi_tool_registry import (
    build_artifact_port_inventory,
    build_registry_snapshot,
    resolve_adapter_invocability,
)


IssueSeverity = Literal["ERROR", "WARNING", "INFO"]


class CapabilityExtensionIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    severity: IssueSeverity
    code: str
    message: str
    capability_id: str | None = None
    component_ref: str | None = None


class CapabilityInventoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability_id: str
    capability_version: str
    pack_id: str | None
    status: str
    completeness: Literal["VALID", "INCOMPLETE"]
    domain: str
    display_name: str
    requirements: list[str]
    input_types: list[str]
    result_types: list[str]
    tool_ids: list[str]
    adapter_names: list[str]
    artifact_types: list[str]
    artifact_port_support: str
    result_projector: str | None
    interpretation_support: str
    viewer_support: str
    viewer_ids: list[str]
    report_support: str
    planner_visibility: str
    resource_classes: list[str]
    expected_cost_classes: list[str]
    qualification_level: str
    qualification_evidence_refs: list[str]
    limitations: list[str]
    contract_fingerprint: str


class OrphanComponent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    component_kind: Literal["TOOL", "ADAPTER", "RESULT_PROJECTOR", "VIEWER", "PACK_ENTRY"]
    component_id: str
    classification: str
    reason: str


class CapabilityExtensionHealthReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    registry_version: str
    registry_snapshot_id: str | None
    capability_count: int
    valid_capability_count: int
    incomplete_capability_count: int
    active_capability_count: int
    experimental_capability_count: int
    deprecated_capability_count: int
    pack_count: int
    tool_count: int
    adapter_count: int | None
    result_projector_count: int
    viewer_descriptor_count: int
    duplicate_capability_authority_count: int
    issues: list[CapabilityExtensionIssue]
    capabilities: list[CapabilityInventoryEntry]
    orphans: list[OrphanComponent]
    inventory_fingerprint: str

    @computed_field
    @property
    def accepted(self) -> bool:
        return not any(item.severity == "ERROR" for item in self.issues)

    @computed_field
    @property
    def error_count(self) -> int:
        return sum(item.severity == "ERROR" for item in self.issues)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _issue(
    issues: list[CapabilityExtensionIssue],
    severity: IssueSeverity,
    code: str,
    message: str,
    *,
    capability_id: str | None = None,
    component_ref: str | None = None,
) -> None:
    issues.append(
        CapabilityExtensionIssue(
            severity=severity,
            code=code,
            message=message,
            capability_id=capability_id,
            component_ref=component_ref,
        )
    )


def _surface_binding_errors(
    *,
    capability: Any,
    support: CapabilitySurfaceSupport,
    bindings: list[str],
    surface: str,
    issues: list[CapabilityExtensionIssue],
) -> None:
    if support in {CapabilitySurfaceSupport.REQUIRED, CapabilitySurfaceSupport.SUPPORTED} and not bindings:
        _issue(
            issues,
            "ERROR",
            f"MISSING_{surface.upper()}_BINDING",
            f"{surface} support is {support.value} but no binding is declared.",
            capability_id=capability.capability_id,
        )
    if support == CapabilitySurfaceSupport.NONE and bindings:
        _issue(
            issues,
            "ERROR",
            f"UNEXPECTED_{surface.upper()}_BINDING",
            f"{surface} support is NONE but bindings are present.",
            capability_id=capability.capability_id,
        )


def validate_capability_extension_platform(
    registries: Any,
    tool_registry: Any,
    *,
    viewer_registry: Any | None = None,
    adapter_invocability: Any | None = None,
    adapter_names: Iterable[str] | None = None,
) -> CapabilityExtensionHealthReport:
    """Validate and inventory the live canonical scientific extension graph."""

    issues: list[CapabilityExtensionIssue] = []
    capabilities = list(registries.capabilities.list_all())
    tools = list(tool_registry.list_tools())
    tools_by_id = {item.toolId: item for item in tools}
    adapter_name_set = set(adapter_names) if adapter_names is not None else None
    adapter_port = adapter_invocability or resolve_adapter_invocability()
    preconditions = build_default_precondition_registry()
    produced_result_types = {
        output.result_type for capability in capabilities for output in capability.output_slots
    }

    capability_keys = [(item.capability_id, item.version) for item in capabilities]
    duplicate_authority_count = sum(
        count - 1 for count in Counter(capability_keys).values() if count > 1
    )
    if duplicate_authority_count:
        _issue(
            issues,
            "ERROR",
            "DUPLICATE_CAPABILITY_AUTHORITY",
            f"{duplicate_authority_count} duplicate capability identities are registered.",
        )

    pack_by_capability: dict[tuple[str, str], list[str]] = defaultdict(list)
    packs = []
    if registries.extension_registry is not None:
        packs = registries.extension_registry.list_packs()
        for pack in packs:
            result = registries.extension_registry.validate_pack(
                pack,
                allow_existing=True,
                requirements=registries.requirements,
                object_types=registries.object_types,
                tool_registry=tool_registry,
                result_projectors=registries.result_projectors,
                progress_projectors=registries.progress_projectors,
            )
            for error in result.errors:
                _issue(
                    issues,
                    "ERROR",
                    "INVALID_CAPABILITY_PACK",
                    error,
                    component_ref=f"{pack.pack_id}@{pack.pack_version}",
                )
            for item in pack.capabilities:
                key = (item.manifest.capability_id, item.manifest.version)
                pack_by_capability[key].append(pack.pack_id)

    for key, owners in sorted(pack_by_capability.items()):
        if len(owners) > 1:
            _issue(
                issues,
                "ERROR",
                "CAPABILITY_IN_MULTIPLE_PACKS",
                f"{key[0]}@{key[1]} is owned by multiple Packs: {', '.join(sorted(owners))}.",
                capability_id=key[0],
            )

    try:
        planner_snapshot, planner_metadata = build_registry_snapshot(
            tool_registry,
            adapter_invocability=adapter_port,
        )
    except Exception as exc:
        planner_snapshot = None
        planner_metadata = {}
        _issue(issues, "ERROR", "INVALID_PLANNER_METADATA", str(exc))

    try:
        port_inventory = build_artifact_port_inventory(tool_registry)
    except Exception as exc:
        port_inventory = {}
        _issue(issues, "ERROR", "INVALID_ARTIFACT_PORT_REGISTRY", str(exc))

    viewer_descriptors = viewer_registry.list() if viewer_registry is not None else []
    viewers_by_id = {item.viewer_id: item for item in viewer_descriptors}
    projector_ids = {item[0] for item in registries.result_projectors.fingerprint()}
    capability_entries: list[CapabilityInventoryEntry] = []
    capability_tool_ids: set[str] = set()
    capability_viewer_ids: set[str] = set()

    for capability in capabilities:
        before = len([item for item in issues if item.severity == "ERROR"])
        key = (capability.capability_id, capability.version)
        pack_owners = pack_by_capability.get(key, [])
        if registries.extension_registry is not None and not pack_owners:
            _issue(
                issues,
                "ERROR",
                "CAPABILITY_WITHOUT_PACK",
                "Registered capability is not owned by a Capability Pack.",
                capability_id=capability.capability_id,
            )

        for requirement_id in capability.satisfies_requirements:
            if not registries.requirements.contains(requirement_id):
                _issue(
                    issues,
                    "ERROR",
                    "UNKNOWN_REQUIREMENT",
                    f"Unknown scientific requirement: {requirement_id}.",
                    capability_id=capability.capability_id,
                    component_ref=requirement_id,
                )

        for slot in capability.input_slots:
            for object_type in slot.accepted_object_types:
                if (
                    registries.object_types.get(object_type) is None
                    and object_type not in produced_result_types
                ):
                    _issue(
                        issues,
                        "ERROR",
                        "UNKNOWN_SCIENTIFIC_INPUT_TYPE",
                        f"Input slot {slot.name} references unknown type {object_type}.",
                        capability_id=capability.capability_id,
                        component_ref=object_type,
                    )
        for slot in capability.output_slots:
            object_type = slot.scientific_object_type or slot.object_type
            if object_type is not None and registries.object_types.get(object_type) is None:
                _issue(
                    issues,
                    "ERROR",
                    "UNKNOWN_SCIENTIFIC_OUTPUT_TYPE",
                    f"Output slot {slot.name} references unknown type {object_type}.",
                    capability_id=capability.capability_id,
                    component_ref=object_type,
                )

        for precondition in capability.preconditions:
            if not preconditions.contains(precondition.predicate_id):
                _issue(
                    issues,
                    "ERROR",
                    "UNKNOWN_PRECONDITION",
                    f"Unknown deterministic precondition: {precondition.predicate_id}.",
                    capability_id=capability.capability_id,
                    component_ref=precondition.predicate_id,
                )

        if capability.status == CapabilityStatus.ACTIVE and not capability.tool_bindings:
            _issue(
                issues,
                "ERROR",
                "MISSING_TOOL_BINDING",
                "ACTIVE capability has no Tool binding.",
                capability_id=capability.capability_id,
            )

        bound_tools: list[Any] = []
        for binding in capability.tool_bindings:
            capability_tool_ids.add(binding.tool_id)
            tool = tools_by_id.get(binding.tool_id)
            if tool is None:
                _issue(
                    issues,
                    "ERROR",
                    "MISSING_TOOL",
                    f"Tool {binding.tool_id} is not registered.",
                    capability_id=capability.capability_id,
                    component_ref=binding.tool_id,
                )
                continue
            bound_tools.append(tool)
            if binding.conditions:
                _issue(
                    issues,
                    "ERROR",
                    "EXECUTABLE_CONDITION_FORBIDDEN",
                    "Tool bindings may not contain executable string conditions.",
                    capability_id=capability.capability_id,
                    component_ref=binding.tool_id,
                )
            if not version_satisfies(tool.version, binding.version_constraint):
                _issue(
                    issues,
                    "ERROR",
                    "TOOL_VERSION_UNAVAILABLE",
                    f"{binding.tool_id}@{tool.version} does not satisfy {binding.version_constraint}.",
                    capability_id=capability.capability_id,
                    component_ref=binding.tool_id,
                )
            if adapter_port is not None and not adapter_port.is_invocable(tool.adapter):
                _issue(
                    issues,
                    "ERROR",
                    "MISSING_ADAPTER",
                    f"Tool {binding.tool_id} references unavailable Adapter {tool.adapter}.",
                    capability_id=capability.capability_id,
                    component_ref=tool.adapter,
                )
            if binding.tool_id not in planner_metadata:
                _issue(
                    issues,
                    "ERROR",
                    "MISSING_PLANNER_METADATA",
                    f"Tool {binding.tool_id} has no validated planner metadata.",
                    capability_id=capability.capability_id,
                    component_ref=binding.tool_id,
                )

        if capability.result_support != CapabilitySurfaceSupport.NONE:
            if (
                not capability.result_projector
                or not registries.result_projectors.contains(capability.result_projector)
            ):
                _issue(
                    issues,
                    "ERROR",
                    "MISSING_RESULT_PROJECTOR",
                    f"Result projector {capability.result_projector} is not registered.",
                    capability_id=capability.capability_id,
                    component_ref=capability.result_projector,
                )
        if not registries.progress_projectors.contains(capability.progress_projector):
            _issue(
                issues,
                "ERROR",
                "MISSING_PROGRESS_PROJECTOR",
                f"Progress projector {capability.progress_projector} is not registered.",
                capability_id=capability.capability_id,
                component_ref=capability.progress_projector,
            )

        port_rows = [port_inventory.get(item.toolId) for item in bound_tools]
        port_rows = [item for item in port_rows if item is not None]
        has_ports = any(item.inputPorts or item.outputPorts for item in port_rows)
        has_input_ports = any(item.inputPorts for item in port_rows)
        if capability.artifact_port_support in {
            CapabilitySurfaceSupport.REQUIRED,
            CapabilitySurfaceSupport.SUPPORTED,
        } and not has_ports:
            _issue(
                issues,
                "ERROR",
                "MISSING_ARTIFACT_PORTS",
                "Capability declares typed Artifact-port support but bound Tools expose none.",
                capability_id=capability.capability_id,
            )
        produced_inputs = {
            object_type
            for slot in capability.input_slots
            for object_type in slot.accepted_object_types
            if object_type in produced_result_types
        }
        if (
            capability.artifact_port_support == CapabilitySurfaceSupport.REQUIRED
            and produced_inputs
            and not has_input_ports
        ):
            _issue(
                issues,
                "ERROR",
                "MISSING_REQUIRED_INPUT_PORT",
                "Derived-input capability requires a typed Artifact input port.",
                capability_id=capability.capability_id,
            )

        _surface_binding_errors(
            capability=capability,
            support=capability.viewer_support,
            bindings=capability.viewer_bindings,
            surface="viewer",
            issues=issues,
        )
        if viewer_registry is not None:
            for viewer_id in capability.viewer_bindings:
                capability_viewer_ids.add(viewer_id)
                if viewer_id not in viewers_by_id:
                    _issue(
                        issues,
                        "ERROR",
                        "UNKNOWN_VIEWER",
                        f"Viewer {viewer_id} is not registered.",
                        capability_id=capability.capability_id,
                        component_ref=viewer_id,
                    )

        report_bindings = [capability.report_projector] if capability.report_projector else []
        interpretation_bindings = (
            [capability.interpretation_profile]
            if capability.interpretation_profile
            else []
        )
        _surface_binding_errors(
            capability=capability,
            support=capability.interpretation_support,
            bindings=interpretation_bindings,
            surface="interpretation",
            issues=issues,
        )
        _surface_binding_errors(
            capability=capability,
            support=capability.report_support,
            bindings=report_bindings,
            surface="report",
            issues=issues,
        )

        if (
            capability.status == CapabilityStatus.DEPRECATED
            and capability.planner_visibility == CapabilityPlannerVisibility.VISIBLE
        ):
            _issue(
                issues,
                "WARNING",
                "DEPRECATED_CAPABILITY_PLANNER_VISIBLE",
                "Deprecated capability is excluded by catalog status filtering; mark it HIDDEN for explicitness.",
                capability_id=capability.capability_id,
            )
        if (
            capability.status == CapabilityStatus.EXPERIMENTAL
            and capability.qualification.level == "SCIENTIFICALLY_QUALIFIED"
        ):
            _issue(
                issues,
                "WARNING",
                "EXPERIMENTAL_CAPABILITY_QUALIFIED",
                "Experimental status and scientific qualification should be reviewed together.",
                capability_id=capability.capability_id,
            )

        adapters = sorted({item.adapter for item in bound_tools})
        artifact_types = sorted(
            {artifact.value for item in bound_tools for artifact in item.artifactTypes}
        )
        resource_classes = sorted(
            {
                capability.resource_profile.resource_class
                if capability.resource_profile.resource_class != "DERIVED_FROM_TOOL"
                else (
                    "GPU"
                    if item.resourceLimits.get("gpu", 0)
                    else "CPU"
                )
                for item in bound_tools
            }
        )
        expected_cost_classes = sorted(
            {
                capability.resource_profile.expected_cost_class
                if capability.resource_profile.expected_cost_class != "DERIVED_FROM_TOOL"
                else item.costLevel.upper()
                for item in bound_tools
            }
        )
        after = len([item for item in issues if item.severity == "ERROR"])
        capability_entries.append(
            CapabilityInventoryEntry(
                capability_id=capability.capability_id,
                capability_version=capability.version,
                pack_id=pack_owners[0] if len(pack_owners) == 1 else None,
                status=capability.status.value,
                completeness="VALID" if after == before else "INCOMPLETE",
                domain=capability.domain,
                display_name=capability.display_name,
                requirements=sorted(capability.satisfies_requirements),
                input_types=sorted(
                    {
                        object_type
                        for slot in capability.input_slots
                        for object_type in slot.accepted_object_types
                    }
                ),
                result_types=sorted({slot.result_type for slot in capability.output_slots}),
                tool_ids=sorted({item.toolId for item in bound_tools}),
                adapter_names=adapters,
                artifact_types=artifact_types,
                artifact_port_support=capability.artifact_port_support.value,
                result_projector=(
                    capability.result_projector
                    if capability.result_support != CapabilitySurfaceSupport.NONE
                    else None
                ),
                interpretation_support=capability.interpretation_support.value,
                viewer_support=capability.viewer_support.value,
                viewer_ids=sorted(capability.viewer_bindings),
                report_support=capability.report_support.value,
                planner_visibility=capability.planner_visibility.value,
                resource_classes=resource_classes,
                expected_cost_classes=expected_cost_classes,
                qualification_level=capability.qualification.level,
                qualification_evidence_refs=sorted(capability.qualification.evidence_refs),
                limitations=list(capability.limitations),
                contract_fingerprint=capability_contract_fingerprint(capability),
            )
        )

    orphans: list[OrphanComponent] = []
    for tool in sorted(tools, key=lambda item: item.toolId):
        if tool.toolId not in capability_tool_ids:
            classification = (
                "PUBLIC_LOW_LEVEL_TOOL"
                if tool.stage == "mvp"
                else "FUTURE_OR_EXPERIMENTAL_TOOL"
            )
            orphans.append(
                OrphanComponent(
                    component_kind="TOOL",
                    component_id=tool.toolId,
                    classification=classification,
                    reason="Registered executable Tool is not currently Agent Capability-reachable.",
                )
            )

    tool_adapter_names = {item.adapter for item in tools}
    if adapter_name_set is not None:
        for adapter_name in sorted(adapter_name_set - tool_adapter_names):
            orphans.append(
                OrphanComponent(
                    component_kind="ADAPTER",
                    component_id=adapter_name,
                    classification="INTERNAL_OR_COMPATIBILITY_ADAPTER",
                    reason="Adapter is registered but no current Tool manifest references it.",
                )
            )

    capability_projectors = {
        item.result_projector
        for item in capabilities
        if item.result_support != CapabilitySurfaceSupport.NONE and item.result_projector
    }
    for projector_id in sorted(projector_ids - capability_projectors):
        orphans.append(
            OrphanComponent(
                component_kind="RESULT_PROJECTOR",
                component_id=projector_id,
                classification="SHARED_OR_COMPATIBILITY_PROJECTOR",
                reason="Projector is registered but no current Capability manifest selects it.",
            )
        )

    relevant_types = {
        object_type
        for capability in capabilities
        for slot in capability.input_slots
        for object_type in slot.accepted_object_types
    } | {
        (slot.scientific_object_type or slot.object_type)
        for capability in capabilities
        for slot in capability.output_slots
        if slot.scientific_object_type or slot.object_type
    }
    for descriptor in sorted(viewer_descriptors, key=lambda item: item.viewer_id):
        if descriptor.viewer_id in capability_viewer_ids:
            continue
        classification = (
            "SOURCE_VIEWER"
            if descriptor.object_type in relevant_types
            else "PRESENTATION_EXTENSION"
        )
        orphans.append(
            OrphanComponent(
                component_kind="VIEWER",
                component_id=descriptor.viewer_id,
                classification=classification,
                reason=(
                    "Viewer is reached from a scientific source type rather than a Capability output binding."
                    if classification == "SOURCE_VIEWER"
                    else "Viewer descriptor is not currently reached by Capability input/output types."
                ),
            )
        )

    if registries.extension_registry is not None:
        registered_keys = set(capability_keys)
        for pack in packs:
            for item in pack.capabilities:
                key = (item.manifest.capability_id, item.manifest.version)
                if key not in registered_keys:
                    orphans.append(
                        OrphanComponent(
                            component_kind="PACK_ENTRY",
                            component_id=f"{pack.pack_id}:{key[0]}@{key[1]}",
                            classification="DEFECT",
                            reason="Capability Pack entry is not present in the canonical Capability Registry.",
                        )
                    )
                    _issue(
                        issues,
                        "ERROR",
                        "DEAD_CAPABILITY_PACK_ENTRY",
                        "Capability Pack contains an entry absent from the canonical registry.",
                        capability_id=key[0],
                        component_ref=pack.pack_id,
                    )

    issues = sorted(
        issues,
        key=lambda item: (
            {"ERROR": 0, "WARNING": 1, "INFO": 2}[item.severity],
            item.capability_id or "",
            item.code,
            item.component_ref or "",
        ),
    )
    capability_entries = sorted(
        capability_entries,
        key=lambda item: (item.capability_id, item.capability_version),
    )
    orphans = sorted(
        orphans,
        key=lambda item: (item.component_kind, item.component_id),
    )
    inventory_payload = {
        "registry_version": tool_registry.version,
        "registry_snapshot_id": planner_snapshot.snapshotId if planner_snapshot else None,
        "capabilities": [item.model_dump(mode="json") for item in capability_entries],
        "orphans": [item.model_dump(mode="json") for item in orphans],
    }
    statuses = Counter(item.status for item in capability_entries)
    valid_count = sum(item.completeness == "VALID" for item in capability_entries)
    return CapabilityExtensionHealthReport(
        registry_version=tool_registry.version,
        registry_snapshot_id=planner_snapshot.snapshotId if planner_snapshot else None,
        capability_count=len(capability_entries),
        valid_capability_count=valid_count,
        incomplete_capability_count=len(capability_entries) - valid_count,
        active_capability_count=statuses[CapabilityStatus.ACTIVE.value],
        experimental_capability_count=statuses[CapabilityStatus.EXPERIMENTAL.value],
        deprecated_capability_count=statuses[CapabilityStatus.DEPRECATED.value],
        pack_count=len(packs),
        tool_count=len(tools),
        adapter_count=len(adapter_name_set) if adapter_name_set is not None else None,
        result_projector_count=len(projector_ids),
        viewer_descriptor_count=len(viewer_descriptors),
        duplicate_capability_authority_count=duplicate_authority_count,
        issues=issues,
        capabilities=capability_entries,
        orphans=orphans,
        inventory_fingerprint=_fingerprint(inventory_payload),
    )


__all__ = [
    "CapabilityExtensionHealthReport",
    "CapabilityExtensionIssue",
    "CapabilityInventoryEntry",
    "OrphanComponent",
    "validate_capability_extension_platform",
]
