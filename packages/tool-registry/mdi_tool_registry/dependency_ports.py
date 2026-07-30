"""Strict planner-visible artifact ports for bounded dependency composition."""

from __future__ import annotations

from typing import Any

from mdi_artifact_core import (
    PHONON_BAND_DOS_SCHEMA_VERSION,
    PHONON_BAND_SCHEMA_VERSION,
    PHONON_DOS_SCHEMA_VERSION,
)
from mdi_schemas import (
    ArtifactCompatibilityMatrix,
    ArtifactInputPort,
    ArtifactOutputPort,
    ArtifactPortCompatibility,
    ArtifactType,
    DependencyDiagnostic,
    DependencyDiagnosticCode,
    ToolArtifactPortMetadata,
    dependency_semantic_hash,
    deterministic_dependency_id,
)

from .planner_metadata import build_registry_snapshot


_JSON_MEDIA = ["application/json"]
_PHONON_MAX_BYTES = 16_000_000
_PROVENANCE_FIELDS = ["schemaVersion", "structureIdentity", "toolCallId", "toolId"]


def build_tool_artifact_port_metadata(tool: Any) -> ToolArtifactPortMetadata:
    input_ports: list[ArtifactInputPort] = []
    output_ports: list[ArtifactOutputPort] = []
    if tool.toolId == "phonon.band":
        output_ports = [
            ArtifactOutputPort(
                portId="canonical-band",
                artifactKind=ArtifactType.phonon_band_json,
                contractFamily="phase10h.phonon_band",
                contractVersions=[PHONON_BAND_SCHEMA_VERSION],
                mediaTypes=_JSON_MEDIA,
                maxBytes=_PHONON_MAX_BYTES,
                requiredProvenanceFields=_PROVENANCE_FIELDS,
            )
        ]
    elif tool.toolId == "phonon.dos":
        output_ports = [
            ArtifactOutputPort(
                portId="canonical-dos",
                artifactKind=ArtifactType.phonon_dos_json,
                contractFamily="phase10h.phonon_dos",
                contractVersions=[PHONON_DOS_SCHEMA_VERSION],
                mediaTypes=_JSON_MEDIA,
                maxBytes=_PHONON_MAX_BYTES,
                requiredProvenanceFields=_PROVENANCE_FIELDS,
            )
        ]
    elif tool.toolId == "phonon.band_dos":
        input_ports = [
            ArtifactInputPort(
                portId="band",
                acceptedArtifactKinds=[ArtifactType.phonon_band_json],
                acceptedContractVersions=[PHONON_BAND_SCHEMA_VERSION],
                mediaTypes=_JSON_MEDIA,
                maxBytes=_PHONON_MAX_BYTES,
                requiredSemanticRoles=["phonon_band"],
                inputFieldRole="band",
                inputObjectType="PhononBand",
            ),
            ArtifactInputPort(
                portId="dos",
                acceptedArtifactKinds=[ArtifactType.phonon_dos_json],
                acceptedContractVersions=[PHONON_DOS_SCHEMA_VERSION],
                mediaTypes=_JSON_MEDIA,
                maxBytes=_PHONON_MAX_BYTES,
                requiredSemanticRoles=["phonon_dos"],
                inputFieldRole="dos",
                inputObjectType="PhononDos",
            ),
        ]
        output_ports = [
            ArtifactOutputPort(
                portId="combined-band-dos",
                artifactKind=ArtifactType.phonon_band_dos_json,
                contractFamily="phase10h.phonon_band_dos",
                contractVersions=[PHONON_BAND_DOS_SCHEMA_VERSION],
                mediaTypes=_JSON_MEDIA,
                maxBytes=_PHONON_MAX_BYTES,
                requiredProvenanceFields=_PROVENANCE_FIELDS,
            )
        ]
    return ToolArtifactPortMetadata(
        toolId=tool.toolId,
        toolVersion=tool.version,
        inputPorts=input_ports,
        outputPorts=output_ports,
        dependencyCompositionAllowed=bool(input_ports or output_ports),
    )


def validate_tool_artifact_port_metadata(tool: Any, metadata: ToolArtifactPortMetadata) -> None:
    if metadata.toolId != tool.toolId or metadata.toolVersion != tool.version:
        raise ValueError("Artifact-port metadata tool identity does not match the Registry tool.")
    declared_artifacts = {item.value for item in tool.artifactTypes}
    for port in metadata.outputPorts:
        if port.artifactKind.value not in declared_artifacts:
            raise ValueError(f"Output port exceeds registered artifacts for {tool.toolId}: {port.portId}")
        if not port.deterministic or port.contentTrust.value != "INERT_DATA":
            raise ValueError(f"Output port is not safe for dependency composition: {tool.toolId}:{port.portId}")
    accepted_options = [
        {item.value for item in option.requiredObjectTypes}
        for option in tool.inputSchema.inputOptions
    ]
    for port in metadata.inputPorts:
        if not any(port.inputObjectType in option for option in accepted_options):
            raise ValueError(f"Input port exceeds registered input contract for {tool.toolId}: {port.portId}")
        if port.contentTrust.value != "INERT_DATA":
            raise ValueError(f"Input port grants executable artifact authority: {tool.toolId}:{port.portId}")


def build_artifact_port_inventory(registry: Any) -> dict[str, ToolArtifactPortMetadata]:
    result: dict[str, ToolArtifactPortMetadata] = {}
    for tool in sorted(registry.tools, key=lambda item: (item.toolId, item.version)):
        metadata = build_tool_artifact_port_metadata(tool)
        validate_tool_artifact_port_metadata(tool, metadata)
        result[tool.toolId] = metadata
    return result


def build_artifact_compatibility_matrix(
    registry: Any,
    *,
    selected_tool_ids: list[str],
) -> ArtifactCompatibilityMatrix:
    if selected_tool_ids != sorted(set(selected_tool_ids)) or not 1 <= len(selected_tool_ids) <= 4:
        raise ValueError("Selected dependency tool identities must be unique, sorted, and bounded to four.")
    snapshot, _metadata = build_registry_snapshot(registry)
    ports = build_artifact_port_inventory(registry)
    tool_by_id = {item.toolId: item for item in registry.tools}
    if not set(selected_tool_ids).issubset(tool_by_id):
        raise ValueError("Dependency compatibility requested an unknown Registry tool.")
    pairs: list[ArtifactPortCompatibility] = []
    for producer_id in selected_tool_ids:
        producer_ports = ports[producer_id].outputPorts
        for consumer_id in selected_tool_ids:
            if producer_id == consumer_id:
                continue
            consumer_ports = ports[consumer_id].inputPorts
            for output_port in producer_ports:
                for input_port in consumer_ports:
                    pairs.append(
                        _compatibility_pair(
                            producer_id,
                            tool_by_id[producer_id].version,
                            output_port,
                            consumer_id,
                            tool_by_id[consumer_id].version,
                            input_port,
                        )
                    )
    pairs = sorted(
        pairs,
        key=lambda item: (
            item.producerToolId, item.producerOutputPort, item.consumerToolId, item.consumerInputPort
        ),
    )
    draft = {
        "schemaVersion": "1.0",
        "registrySnapshotId": snapshot.snapshotId,
        "registrySnapshotHash": snapshot.snapshotHash,
        "selectedToolIds": selected_tool_ids,
        "pairs": [item.model_dump(mode="json") for item in pairs],
        "portMetadataHashes": {
            tool_id: dependency_semantic_hash(ports[tool_id], identity_fields=())
            for tool_id in selected_tool_ids
        },
    }
    matrix_hash = dependency_semantic_hash(draft)
    return ArtifactCompatibilityMatrix(
        matrixId=deterministic_dependency_id("compatibility", matrix_hash),
        matrixHash=matrix_hash,
        registrySnapshotId=snapshot.snapshotId,
        registrySnapshotHash=snapshot.snapshotHash,
        selectedToolIds=selected_tool_ids,
        portMetadataHashes=draft["portMetadataHashes"],
        pairs=pairs,
    )


def _compatibility_pair(
    producer_id: str,
    producer_version: str,
    output_port: ArtifactOutputPort,
    consumer_id: str,
    consumer_version: str,
    input_port: ArtifactInputPort,
) -> ArtifactPortCompatibility:
    diagnostics: list[DependencyDiagnostic] = []
    common_kinds = sorted(
        set(input_port.acceptedArtifactKinds) & {output_port.artifactKind},
        key=lambda item: item.value,
    )
    common_versions = sorted(set(output_port.contractVersions) & set(input_port.acceptedContractVersions))
    common_media = sorted(set(output_port.mediaTypes) & set(input_port.mediaTypes))
    if not output_port.plannerVisible or not input_port.plannerVisible:
        diagnostics.append(_diagnostic(DependencyDiagnosticCode.port_not_planner_visible, "plannerVisible", "Both ports must be planner-visible."))
    if not common_kinds:
        diagnostics.append(_diagnostic(DependencyDiagnosticCode.artifact_kind_mismatch, "artifactKind", "Artifact kinds do not match."))
    if not common_versions:
        diagnostics.append(_diagnostic(DependencyDiagnosticCode.contract_version_mismatch, "contractVersion", "Artifact contract versions do not match."))
    if not common_media:
        diagnostics.append(_diagnostic(DependencyDiagnosticCode.media_type_mismatch, "mediaType", "Artifact media types do not match."))
    if output_port.cardinality.value != input_port.cardinality.value:
        diagnostics.append(_diagnostic(DependencyDiagnosticCode.cardinality_mismatch, "cardinality", "Artifact cardinality does not match."))
    if output_port.maxBytes > input_port.maxBytes:
        diagnostics.append(_diagnostic(DependencyDiagnosticCode.artifact_too_large, "maxBytes", "Producer output cap exceeds consumer input cap."))
    if not output_port.deterministic:
        diagnostics.append(_diagnostic(DependencyDiagnosticCode.non_deterministic_output_not_allowed, "deterministic", "Non-deterministic output is not dependency eligible."))
    if output_port.contentTrust.value != "INERT_DATA" or input_port.contentTrust.value != "INERT_DATA":
        diagnostics.append(_diagnostic(DependencyDiagnosticCode.untrusted_or_executable_artifact, "contentTrust", "Only inert data may cross a dependency binding."))
    compatible = not diagnostics
    semantic_pair = {
        "producerToolId": producer_id,
        "producerToolVersion": producer_version,
        "producerOutputPort": output_port.portId,
        "consumerToolId": consumer_id,
        "consumerToolVersion": consumer_version,
        "consumerInputPort": input_port.portId,
        "compatible": compatible,
        "artifactKind": common_kinds[0].value if compatible else None,
        "artifactContractVersion": common_versions[0] if compatible else None,
        "mediaType": common_media[0] if compatible else None,
    }
    return ArtifactPortCompatibility(
        pairId=deterministic_dependency_id("port_pair", dependency_semantic_hash(semantic_pair)),
        producerToolId=producer_id,
        producerToolVersion=producer_version,
        producerOutputPort=output_port.portId,
        consumerToolId=consumer_id,
        consumerToolVersion=consumer_version,
        consumerInputPort=input_port.portId,
        compatible=compatible,
        artifactKind=common_kinds[0] if compatible else None,
        artifactContractVersion=common_versions[0] if compatible else None,
        mediaType=common_media[0] if compatible else None,
        diagnostics=diagnostics,
    )


def _diagnostic(code: DependencyDiagnosticCode, field: str, message: str) -> DependencyDiagnostic:
    return DependencyDiagnostic(code=code, field=field, message=message)


__all__ = [
    "build_artifact_compatibility_matrix",
    "build_artifact_port_inventory",
    "build_tool_artifact_port_metadata",
    "validate_tool_artifact_port_metadata",
]
