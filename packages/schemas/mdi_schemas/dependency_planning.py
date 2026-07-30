"""Strict Phase 10L-3 dependency-planning and execution contracts."""

from __future__ import annotations

from collections import defaultdict
from enum import Enum
import hashlib
import json
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import AnalysisStep, ArtifactType, ExpectedArtifact


ANALYSIS_PLAN_02_SCHEMA_VERSION = "0.2"
ARTIFACT_PORT_METADATA_SCHEMA_VERSION = "1.1"
DEPENDENCY_EXECUTION_SCHEMA_VERSION = "1.0"
ARTIFACT_LINEAGE_SCHEMA_VERSION = "1.0"
DEPENDENCY_MAX_STEPS = 4
DEPENDENCY_MAX_BINDINGS = 6
DEPENDENCY_MAX_DEPTH = 4
DEPENDENCY_MAX_INCOMING = 3
DEPENDENCY_MAX_OUTGOING = 3
DEPENDENCY_MAX_DIAGNOSTICS = 128
DEPENDENCY_MAX_PORTS_PER_TOOL = 16
DEPENDENCY_MAX_SERIALIZED_BYTES = 524_288
DEPENDENCY_MAX_JSON_DEPTH = 14
_MEDIA_TYPE = re.compile(r"^[a-z0-9][a-z0-9.+-]{0,63}/[a-z0-9][a-z0-9.+-]{0,63}$")


class StrictDependencyModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ArtifactCardinality(str, Enum):
    exactly_one = "EXACTLY_ONE"


class ArtifactContentTrust(str, Enum):
    inert_data = "INERT_DATA"


class IdentityCompatibility(str, Enum):
    exact_plan_job_dataset_resource = "EXACT_PLAN_JOB_DATASET_RESOURCE"


class DependencyDiagnosticCode(str, Enum):
    output_port_not_declared = "OUTPUT_PORT_NOT_DECLARED"
    input_port_not_declared = "INPUT_PORT_NOT_DECLARED"
    artifact_kind_mismatch = "ARTIFACT_KIND_MISMATCH"
    contract_version_mismatch = "CONTRACT_VERSION_MISMATCH"
    media_type_mismatch = "MEDIA_TYPE_MISMATCH"
    cardinality_mismatch = "CARDINALITY_MISMATCH"
    identity_scope_mismatch = "IDENTITY_SCOPE_MISMATCH"
    resource_version_mismatch = "RESOURCE_VERSION_MISMATCH"
    artifact_too_large = "ARTIFACT_TOO_LARGE"
    non_deterministic_output_not_allowed = "NON_DETERMINISTIC_OUTPUT_NOT_ALLOWED"
    untrusted_or_executable_artifact = "UNTRUSTED_OR_EXECUTABLE_ARTIFACT"
    consumer_requires_unavailable_base_resource = "CONSUMER_REQUIRES_UNAVAILABLE_BASE_RESOURCE"
    port_not_planner_visible = "PORT_NOT_PLANNER_VISIBLE"
    dependency_composition_not_allowed = "DEPENDENCY_COMPOSITION_NOT_ALLOWED"
    cycle_would_be_created = "CYCLE_WOULD_BE_CREATED"
    graph_cap_exceeded = "GRAPH_CAP_EXCEEDED"
    unknown_step = "UNKNOWN_STEP"
    duplicate_binding = "DUPLICATE_BINDING"
    duplicate_consumer_port = "DUPLICATE_CONSUMER_PORT"
    selected_tool_mismatch = "SELECTED_TOOL_MISMATCH"
    binding_identity_invalid = "BINDING_IDENTITY_INVALID"
    graph_identity_invalid = "GRAPH_IDENTITY_INVALID"
    external_authority_rejected = "EXTERNAL_AUTHORITY_REJECTED"


class DependencyDiagnostic(StrictDependencyModel):
    code: DependencyDiagnosticCode
    field: str = Field(min_length=1, max_length=160)
    message: str = Field(min_length=1, max_length=1024)
    bindingId: str | None = Field(default=None, max_length=96)
    stepId: str | None = Field(default=None, max_length=96)


def _safe_identifier(value: str, *, field: str) -> str:
    lowered = value.lower()
    forbidden = ("/", "\\", "..", "://", "file:", "javascript:", "<", ">", "${", "$(")
    if not value or len(value) > 160 or any(item in lowered for item in forbidden):
        raise ValueError(f"{field} contains external or executable authority.")
    return value


class ArtifactOutputPort(StrictDependencyModel):
    portId: str = Field(min_length=1, max_length=96)
    artifactKind: ArtifactType
    contractFamily: str = Field(min_length=1, max_length=128)
    contractVersions: list[str] = Field(min_length=1, max_length=8)
    mediaTypes: list[str] = Field(min_length=1, max_length=8)
    cardinality: Literal[ArtifactCardinality.exactly_one] = ArtifactCardinality.exactly_one
    maxBytes: int = Field(gt=0, le=268_435_456)
    deterministic: bool = True
    requiredProvenanceFields: list[str] = Field(default_factory=list, max_length=16)
    identityPolicy: Literal[IdentityCompatibility.exact_plan_job_dataset_resource] = IdentityCompatibility.exact_plan_job_dataset_resource
    contentTrust: Literal[ArtifactContentTrust.inert_data] = ArtifactContentTrust.inert_data
    plannerVisible: bool = True

    @model_validator(mode="after")
    def validate_port(self) -> "ArtifactOutputPort":
        _safe_identifier(self.portId, field="portId")
        _validate_unique_sorted(self.contractVersions, "contractVersions")
        _validate_media_types(self.mediaTypes)
        _validate_unique_sorted(self.requiredProvenanceFields, "requiredProvenanceFields")
        if not self.deterministic and self.plannerVisible:
            raise ValueError("Non-deterministic outputs cannot be planner-visible dependency ports.")
        return self


class ArtifactInputPort(StrictDependencyModel):
    portId: str = Field(min_length=1, max_length=96)
    acceptedArtifactKinds: list[ArtifactType] = Field(min_length=1, max_length=8)
    acceptedContractVersions: list[str] = Field(min_length=1, max_length=8)
    mediaTypes: list[str] = Field(min_length=1, max_length=8)
    cardinality: Literal[ArtifactCardinality.exactly_one] = ArtifactCardinality.exactly_one
    maxBytes: int = Field(gt=0, le=268_435_456)
    identityPolicy: Literal[IdentityCompatibility.exact_plan_job_dataset_resource] = IdentityCompatibility.exact_plan_job_dataset_resource
    requiredSemanticRoles: list[str] = Field(min_length=1, max_length=8)
    materializationPermitted: bool = True
    baseResourceRequired: bool = False
    inputFieldRole: str = Field(min_length=1, max_length=64)
    inputObjectType: str = Field(min_length=1, max_length=64)
    plannerVisible: bool = True
    contentTrust: Literal[ArtifactContentTrust.inert_data] = ArtifactContentTrust.inert_data

    @model_validator(mode="after")
    def validate_port(self) -> "ArtifactInputPort":
        _safe_identifier(self.portId, field="portId")
        if self.acceptedArtifactKinds != sorted(set(self.acceptedArtifactKinds), key=lambda item: item.value):
            raise ValueError("acceptedArtifactKinds must be unique and sorted.")
        _validate_unique_sorted(self.acceptedContractVersions, "acceptedContractVersions")
        _validate_media_types(self.mediaTypes)
        _validate_unique_sorted(self.requiredSemanticRoles, "requiredSemanticRoles")
        _safe_identifier(self.inputFieldRole, field="inputFieldRole")
        _safe_identifier(self.inputObjectType, field="inputObjectType")
        return self


class ToolArtifactPortMetadata(StrictDependencyModel):
    schemaVersion: Literal["1.1"] = ARTIFACT_PORT_METADATA_SCHEMA_VERSION
    toolId: str = Field(min_length=1, max_length=160)
    toolVersion: str = Field(min_length=1, max_length=64)
    inputPorts: list[ArtifactInputPort] = Field(default_factory=list, max_length=DEPENDENCY_MAX_PORTS_PER_TOOL)
    outputPorts: list[ArtifactOutputPort] = Field(default_factory=list, max_length=DEPENDENCY_MAX_PORTS_PER_TOOL)
    dependencyCompositionAllowed: bool = False

    @model_validator(mode="after")
    def validate_ports(self) -> "ToolArtifactPortMetadata":
        _safe_identifier(self.toolId, field="toolId")
        for values, field in ((self.inputPorts, "inputPorts"), (self.outputPorts, "outputPorts")):
            ids = [item.portId for item in values]
            if ids != sorted(set(ids)):
                raise ValueError(f"{field} must have unique stable ordering.")
        if (self.inputPorts or self.outputPorts) and not self.dependencyCompositionAllowed:
            raise ValueError("Artifact ports require dependencyCompositionAllowed.")
        return self


class DependencyBinding(StrictDependencyModel):
    bindingId: str = Field(min_length=1, max_length=96)
    producerStepId: str = Field(min_length=1, max_length=96)
    producerOutputPort: str = Field(min_length=1, max_length=96)
    consumerStepId: str = Field(min_length=1, max_length=96)
    consumerInputPort: str = Field(min_length=1, max_length=96)
    artifactKind: ArtifactType
    artifactContractVersion: str = Field(min_length=1, max_length=128)
    mediaType: str = Field(min_length=1, max_length=128)
    cardinality: Literal[ArtifactCardinality.exactly_one] = ArtifactCardinality.exactly_one

    @model_validator(mode="after")
    def validate_binding(self) -> "DependencyBinding":
        for field in ("producerStepId", "producerOutputPort", "consumerStepId", "consumerInputPort"):
            _safe_identifier(getattr(self, field), field=field)
        if self.producerStepId == self.consumerStepId:
            raise ValueError("Dependency bindings cannot form a self-cycle.")
        expected = deterministic_binding_id(self.model_dump(mode="json", exclude={"bindingId"}))
        if self.bindingId != expected:
            raise ValueError("bindingId does not match deterministic semantic identity.")
        return self


class AnalysisPlanV02(StrictDependencyModel):
    schemaVersion: Literal["0.2"] = ANALYSIS_PLAN_02_SCHEMA_VERSION
    goal: str = Field(min_length=1, max_length=16_384)
    datasetId: str = Field(min_length=1, max_length=160)
    profileId: str = Field(min_length=1, max_length=160)
    toolRegistryVersion: str = Field(min_length=1, max_length=64)
    graphHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    assumptions: list[str] = Field(default_factory=list, max_length=32)
    warnings: list[str] = Field(default_factory=list, max_length=32)
    steps: list[AnalysisStep] = Field(min_length=1, max_length=DEPENDENCY_MAX_STEPS)
    dependencyBindings: list[DependencyBinding] = Field(default_factory=list, max_length=DEPENDENCY_MAX_BINDINGS)
    expectedArtifacts: list[ExpectedArtifact] = Field(default_factory=list, max_length=64)

    @model_validator(mode="after")
    def validate_graph(self) -> "AnalysisPlanV02":
        step_ids = [item.stepId for item in self.steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("AnalysisPlan 0.2 step IDs must be unique.")
        if any(ref.refType == "artifact" for step in self.steps for ref in step.inputRefs):
            raise ValueError("AnalysisPlan 0.2 artifact dependencies are represented only by dependencyBindings.")
        expected = compute_dependency_graph_hash(self.dependencyBindings)
        if self.graphHash != expected:
            raise ValueError("graphHash does not match dependencyBindings.")
        topological_order(self.steps, self.dependencyBindings)
        validate_dependency_json_bounds(self.model_dump(mode="json"))
        return self


class ArtifactPortCompatibility(StrictDependencyModel):
    pairId: str = Field(min_length=1, max_length=96)
    producerToolId: str
    producerToolVersion: str
    producerOutputPort: str
    consumerToolId: str
    consumerToolVersion: str
    consumerInputPort: str
    compatible: bool
    artifactKind: ArtifactType | None = None
    artifactContractVersion: str | None = None
    mediaType: str | None = None
    diagnostics: list[DependencyDiagnostic] = Field(default_factory=list, max_length=16)

    @model_validator(mode="after")
    def validate_pair_identity(self) -> "ArtifactPortCompatibility":
        semantic = self.model_dump(mode="json", exclude={"pairId", "diagnostics"})
        expected = deterministic_dependency_id("port_pair", dependency_semantic_hash(semantic))
        if self.pairId != expected:
            raise ValueError("pairId does not match the exact artifact-port compatibility pair.")
        return self


class DependencyCompositionProposal(StrictDependencyModel):
    """The complete authority an optional provider receives for dependency composition."""

    schemaVersion: Literal["1.0"] = "1.0"
    matrixId: str = Field(min_length=1, max_length=96)
    selectedPairIds: list[str] = Field(default_factory=list, max_length=DEPENDENCY_MAX_BINDINGS)

    @model_validator(mode="after")
    def validate_pair_selection(self) -> "DependencyCompositionProposal":
        _safe_identifier(self.matrixId, field="matrixId")
        if self.selectedPairIds != sorted(set(self.selectedPairIds)):
            raise ValueError("selectedPairIds must be unique and deterministically sorted.")
        for value in self.selectedPairIds:
            _safe_identifier(value, field="selectedPairIds")
        return self


class ArtifactCompatibilityMatrix(StrictDependencyModel):
    schemaVersion: Literal["1.0"] = "1.0"
    matrixId: str
    matrixHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    registrySnapshotId: str
    registrySnapshotHash: str
    selectedToolIds: list[str] = Field(min_length=1, max_length=DEPENDENCY_MAX_STEPS)
    portMetadataHashes: dict[str, str] = Field(max_length=DEPENDENCY_MAX_STEPS)
    pairs: list[ArtifactPortCompatibility] = Field(max_length=256)

    @model_validator(mode="after")
    def validate_identity(self) -> "ArtifactCompatibilityMatrix":
        if sorted(self.portMetadataHashes) != self.selectedToolIds:
            raise ValueError("Compatibility matrix port metadata must cover selected tools exactly.")
        payload = self.model_dump(mode="json", exclude={"matrixId", "matrixHash"})
        expected = dependency_semantic_hash(payload)
        if self.matrixHash != expected or self.matrixId != deterministic_dependency_id("compatibility", expected):
            raise ValueError("Compatibility matrix semantic identity is invalid.")
        return self


class StepExecutionState(str, Enum):
    pending = "PENDING"
    ready = "READY"
    running = "RUNNING"
    succeeded = "SUCCEEDED"
    failed = "FAILED"
    blocked_dependency = "BLOCKED_DEPENDENCY"
    not_started = "NOT_STARTED"


class BindingExecutionState(str, Enum):
    pending = "PENDING"
    resolved = "RESOLVED"
    failed_producer = "FAILED_PRODUCER"
    missing_artifact = "MISSING_ARTIFACT"
    contract_mismatch = "CONTRACT_MISMATCH"
    scope_mismatch = "SCOPE_MISMATCH"
    checksum_mismatch = "CHECKSUM_MISMATCH"
    size_rejected = "SIZE_REJECTED"
    consumer_not_run = "CONSUMER_NOT_RUN"


class DependencyExecutionOutcome(str, Enum):
    all_succeeded = "ALL_SUCCEEDED"
    partial_results = "PARTIAL_RESULTS"
    all_failed = "ALL_FAILED"
    validation_aborted = "VALIDATION_ABORTED"


class DependencyStepExecution(StrictDependencyModel):
    stepId: str
    toolId: str
    state: StepExecutionState
    toolCallId: str | None = None
    artifactIds: list[str] = Field(default_factory=list, max_length=64)
    blockedByStepIds: list[str] = Field(default_factory=list, max_length=DEPENDENCY_MAX_STEPS)
    errorCode: str | None = Field(default=None, max_length=96)
    errorMessage: str | None = Field(default=None, max_length=1024)


class DependencyBindingExecution(StrictDependencyModel):
    bindingId: str
    state: BindingExecutionState
    producerToolCallId: str | None = None
    artifactId: str | None = None
    artifactChecksum: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    consumerToolCallId: str | None = None
    errorCode: str | None = Field(default=None, max_length=96)


class DependencyExecutionRecord(StrictDependencyModel):
    schemaVersion: Literal["1.0"] = DEPENDENCY_EXECUTION_SCHEMA_VERSION
    executionId: str
    executionHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    planId: str
    planHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    jobId: str
    graphHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    topologicalOrder: list[str] = Field(min_length=1, max_length=DEPENDENCY_MAX_STEPS)
    steps: list[DependencyStepExecution] = Field(min_length=1, max_length=DEPENDENCY_MAX_STEPS)
    bindings: list[DependencyBindingExecution] = Field(default_factory=list, max_length=DEPENDENCY_MAX_BINDINGS)
    succeededCount: int = Field(ge=0, le=DEPENDENCY_MAX_STEPS)
    failedCount: int = Field(ge=0, le=DEPENDENCY_MAX_STEPS)
    blockedCount: int = Field(ge=0, le=DEPENDENCY_MAX_STEPS)
    notStartedCount: int = Field(ge=0, le=DEPENDENCY_MAX_STEPS)
    partialArtifactIds: list[str] = Field(default_factory=list, max_length=256)
    outcome: DependencyExecutionOutcome
    runtimeVersion: str
    createdAt: str
    updatedAt: str


class ResolvedArtifactInputRef(StrictDependencyModel):
    schemaVersion: Literal["1.0"] = "1.0"
    bindingId: str
    planId: str
    planHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    jobId: str
    producerStepId: str
    producerToolCallId: str
    artifactId: str
    artifactKind: ArtifactType
    artifactContractVersion: str
    mediaType: str
    sizeBytes: int = Field(ge=0)
    checksum: str = Field(pattern=r"^[0-9a-f]{64}$")
    consumerStepId: str
    consumerInputPort: str
    materializedObjectRef: str


class ArtifactLineageRecord(StrictDependencyModel):
    schemaVersion: Literal["1.0"] = ARTIFACT_LINEAGE_SCHEMA_VERSION
    lineageId: str
    lineageHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    projectId: str
    datasetId: str | None = None
    datasetVersion: str | None = None
    profileId: str | None = None
    profileSemanticHash: str | None = None
    intentId: str | None = None
    intentHash: str | None = None
    resolutionId: str | None = None
    resolutionHash: str | None = None
    decisionId: str | None = None
    decisionHash: str | None = None
    planId: str
    planHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    planSchemaVersion: Literal["0.2"] = "0.2"
    graphHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    jobId: str
    producerStepId: str
    producerToolCallId: str
    producerToolId: str
    producerToolVersion: str
    outputPort: str
    artifactId: str
    artifactKind: ArtifactType
    artifactContractVersion: str
    mediaType: str
    contentHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    upstreamArtifactIds: list[str] = Field(default_factory=list, max_length=DEPENDENCY_MAX_BINDINGS)
    upstreamArtifactHashes: list[str] = Field(default_factory=list, max_length=DEPENDENCY_MAX_BINDINGS)
    bindingIds: list[str] = Field(default_factory=list, max_length=DEPENDENCY_MAX_BINDINGS)
    adapterVersion: str | None = None
    runtimeVersion: str
    warnings: list[str] = Field(default_factory=list, max_length=32)
    caps: dict[str, int] = Field(default_factory=dict)
    createdAt: str


def _validate_unique_sorted(values: list[str], field: str) -> None:
    if values != sorted(set(values)):
        raise ValueError(f"{field} must be unique and sorted.")
    for value in values:
        _safe_identifier(value, field=field)


def _validate_media_types(values: list[str]) -> None:
    if values != sorted(set(values)) or any(_MEDIA_TYPE.fullmatch(value) is None for value in values):
        raise ValueError("mediaTypes must be unique, sorted, and use bounded MIME syntax.")


def canonical_dependency_json(value: BaseModel | dict[str, Any]) -> str:
    payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    validate_dependency_json_bounds(payload)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def dependency_semantic_hash(value: BaseModel | dict[str, Any], *, identity_fields: tuple[str, ...] = ()) -> str:
    payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else dict(value)
    payload = {key: item for key, item in payload.items() if key not in identity_fields}
    return hashlib.sha256(canonical_dependency_json(payload).encode("utf-8")).hexdigest()


def deterministic_dependency_id(prefix: str, semantic_hash: str) -> str:
    return f"{prefix}_{semantic_hash[:32]}"


def deterministic_binding_id(fields: BaseModel | dict[str, Any]) -> str:
    return deterministic_dependency_id("binding", dependency_semantic_hash(fields, identity_fields=("bindingId",)))


def make_dependency_binding(**fields: Any) -> DependencyBinding:
    draft = dict(fields)
    draft["bindingId"] = deterministic_binding_id(draft)
    return DependencyBinding.model_validate(draft)


def _binding_sort_key(binding: DependencyBinding) -> tuple[str, ...]:
    return (
        binding.producerStepId,
        binding.producerOutputPort,
        binding.consumerStepId,
        binding.consumerInputPort,
        binding.bindingId,
    )


def compute_dependency_graph_hash(bindings: list[DependencyBinding]) -> str:
    ordered = [item.model_dump(mode="json") for item in sorted(bindings, key=_binding_sort_key)]
    return dependency_semantic_hash({"dependencyBindings": ordered})


def compute_analysis_plan_02_hash(plan: AnalysisPlanV02 | dict[str, Any]) -> str:
    parsed = plan if isinstance(plan, AnalysisPlanV02) else AnalysisPlanV02.model_validate(plan)
    return dependency_semantic_hash(parsed)


def topological_order(steps: list[AnalysisStep], bindings: list[DependencyBinding]) -> list[str]:
    step_ids = {item.stepId for item in steps}
    incoming: dict[str, set[str]] = {item: set() for item in step_ids}
    outgoing: dict[str, set[str]] = defaultdict(set)
    incoming_bindings: dict[str, int] = defaultdict(int)
    outgoing_bindings: dict[str, int] = defaultdict(int)
    consumer_ports: set[tuple[str, str]] = set()
    binding_ids: set[str] = set()
    for binding in bindings:
        if binding.bindingId in binding_ids:
            raise ValueError("Duplicate dependency binding.")
        binding_ids.add(binding.bindingId)
        if binding.producerStepId not in step_ids or binding.consumerStepId not in step_ids:
            raise ValueError("Dependency binding references an unknown step.")
        port_key = (binding.consumerStepId, binding.consumerInputPort)
        if port_key in consumer_ports:
            raise ValueError("A consumer input port may be bound only once.")
        consumer_ports.add(port_key)
        incoming[binding.consumerStepId].add(binding.producerStepId)
        outgoing[binding.producerStepId].add(binding.consumerStepId)
        incoming_bindings[binding.consumerStepId] += 1
        outgoing_bindings[binding.producerStepId] += 1
    if any(value > DEPENDENCY_MAX_INCOMING for value in incoming_bindings.values()):
        raise ValueError("Incoming dependency binding cap exceeded.")
    if any(value > DEPENDENCY_MAX_OUTGOING for value in outgoing_bindings.values()):
        raise ValueError("Outgoing dependency binding cap exceeded.")

    ready = sorted(item for item, parents in incoming.items() if not parents)
    result: list[str] = []
    depth: dict[str, int] = {item: 1 for item in ready}
    remaining = {item: set(parents) for item, parents in incoming.items()}
    while ready:
        current = ready.pop(0)
        result.append(current)
        for child in sorted(outgoing.get(current, set())):
            remaining[child].discard(current)
            depth[child] = max(depth.get(child, 1), depth[current] + 1)
            if not remaining[child] and child not in result and child not in ready:
                ready.append(child)
                ready.sort()
    if len(result) != len(step_ids):
        raise ValueError("Dependency graph contains a cycle.")
    if max(depth.values(), default=0) > DEPENDENCY_MAX_DEPTH:
        raise ValueError("Dependency graph depth cap exceeded.")
    return result


def validate_dependency_json_bounds(value: Any) -> None:
    def walk(item: Any, depth: int) -> None:
        if depth > DEPENDENCY_MAX_JSON_DEPTH:
            raise ValueError("Dependency JSON depth cap exceeded.")
        if isinstance(item, dict):
            for key, child in item.items():
                if not isinstance(key, str):
                    raise ValueError("Dependency JSON object keys must be strings.")
                walk(child, depth + 1)
        elif isinstance(item, list):
            for child in item:
                walk(child, depth + 1)
        elif isinstance(item, float) and (item != item or item in {float("inf"), float("-inf")}):
            raise ValueError("Dependency JSON cannot contain non-finite numbers.")

    walk(value, 1)
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(encoded) > DEPENDENCY_MAX_SERIALIZED_BYTES:
        raise ValueError("Dependency JSON serialized byte cap exceeded.")


__all__ = [name for name in globals() if name.startswith("DEPENDENCY_") or name.startswith("ANALYSIS_PLAN_") or name.startswith("ARTIFACT_")] + [
    "AnalysisPlanV02", "ArtifactCardinality", "ArtifactCompatibilityMatrix", "ArtifactContentTrust",
    "ArtifactInputPort", "ArtifactLineageRecord", "ArtifactOutputPort", "ArtifactPortCompatibility",
    "BindingExecutionState", "DependencyBinding", "DependencyBindingExecution", "DependencyCompositionProposal", "DependencyDiagnostic",
    "DependencyDiagnosticCode", "DependencyExecutionOutcome", "DependencyExecutionRecord", "DependencyStepExecution",
    "IdentityCompatibility", "ResolvedArtifactInputRef", "StepExecutionState", "ToolArtifactPortMetadata",
    "canonical_dependency_json", "compute_analysis_plan_02_hash", "compute_dependency_graph_hash",
    "dependency_semantic_hash", "deterministic_binding_id", "deterministic_dependency_id", "make_dependency_binding",
    "topological_order", "validate_dependency_json_bounds",
]
