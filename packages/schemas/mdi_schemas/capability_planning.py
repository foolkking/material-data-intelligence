from __future__ import annotations

import hashlib
import json
import math
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .analysis_intent import CapabilityNeed, DesiredOutput, ScientificIntent


CAPABILITY_PLANNING_SCHEMA_VERSION = "1.0"
CAPABILITY_PLANNING_MAX_REGISTRY_TOOLS = 64
CAPABILITY_PLANNING_MAX_ELIGIBLE_TOOLS = 32
CAPABILITY_PLANNING_MAX_DIAGNOSTICS = 256
CAPABILITY_PLANNING_MAX_BINDING_VALUES = 64
CAPABILITY_PLANNING_MAX_SELECTED_TOOLS = 4
CAPABILITY_PLANNING_MAX_JSON_DEPTH = 14
CAPABILITY_PLANNING_MAX_SERIALIZED_BYTES = 524_288


class StrictCapabilityModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class PlannerAvailability(str, Enum):
    available = "AVAILABLE"
    deployment_unavailable = "DEPLOYMENT_UNAVAILABLE"
    future = "FUTURE"
    not_planned = "NOT_PLANNED"


class PlannerBindingSource(str, Enum):
    resource_id = "RESOURCE_ID"
    target_column = "TARGET_COLUMN"
    target_group_ids = "TARGET_GROUP_IDS"
    semantic_columns = "SEMANTIC_COLUMNS"
    profile_id = "PROFILE_ID"
    resource_fact = "RESOURCE_FACT"
    literal = "LITERAL"


class CapabilityPlanningOutcome(str, Enum):
    plan_ready = "PLAN_READY"
    needs_clarification = "NEEDS_CLARIFICATION"
    unsupported = "UNSUPPORTED"
    capability_mismatch = "CAPABILITY_MISMATCH"
    validation_failed = "VALIDATION_FAILED"


class PlannerParameterBinding(StrictCapabilityModel):
    parameter: str = Field(min_length=1, max_length=128)
    source: PlannerBindingSource
    required: bool = True
    targetRoles: list[str] = Field(default_factory=list, max_length=16)
    objectTypes: list[str] = Field(default_factory=list, max_length=16)
    factKeys: list[str] = Field(default_factory=list, max_length=8)
    literalValue: str | int | float | bool | list[str] | None = None
    multiple: bool = False

    @model_validator(mode="after")
    def validate_binding_source(self) -> "PlannerParameterBinding":
        if self.source is PlannerBindingSource.literal and self.literalValue is None:
            raise ValueError("Literal planner bindings require a literal value.")
        if self.source is PlannerBindingSource.resource_fact and not self.factKeys:
            raise ValueError("Resource-fact planner bindings require fact keys.")
        if self.source in {PlannerBindingSource.target_column, PlannerBindingSource.semantic_columns} and not self.targetRoles:
            raise ValueError("Column planner bindings require semantic roles.")
        if isinstance(self.literalValue, float) and not math.isfinite(self.literalValue):
            raise ValueError("Planner literal values must be finite.")
        return self


class ToolPlannerMetadata(StrictCapabilityModel):
    schemaVersion: Literal["1.0"] = CAPABILITY_PLANNING_SCHEMA_VERSION
    toolId: str = Field(min_length=1, max_length=160)
    toolName: str = Field(min_length=1, max_length=160)
    toolVersion: str = Field(min_length=1, max_length=64)
    availability: PlannerAvailability
    scientificIntents: list[ScientificIntent] = Field(min_length=1, max_length=16)
    capabilityNeeds: list[CapabilityNeed] = Field(default_factory=list, max_length=16)
    desiredOutputs: list[DesiredOutput] = Field(min_length=1, max_length=16)
    acceptedObjectTypes: list[str] = Field(min_length=1, max_length=16)
    inputObjectTypeOptions: list[list[str]] = Field(min_length=1, max_length=16)
    requiredProfileCapabilities: list[str] = Field(default_factory=list, max_length=16)
    requiredTargetRoles: list[str] = Field(default_factory=list, max_length=16)
    minInputs: int = Field(default=1, ge=1, le=32)
    maxInputs: int = Field(default=1, ge=1, le=32)
    minTargets: int = Field(default=0, ge=0, le=32)
    maxTargets: int = Field(default=32, ge=0, le=32)
    parameterBindings: list[PlannerParameterBinding] = Field(default_factory=list, max_length=32)
    declaredArtifactTypes: list[str] = Field(min_length=1, max_length=32)
    costClass: Literal[1, 2, 3]
    independentComposable: bool = True
    collisionGroup: str | None = Field(default=None, max_length=96)
    executionBoundary: Literal["REGISTERED_ADAPTER_ONLY"] = "REGISTERED_ADAPTER_ONLY"

    @model_validator(mode="after")
    def validate_metadata(self) -> "ToolPlannerMetadata":
        if self.minInputs > self.maxInputs or self.minTargets > self.maxTargets:
            raise ValueError("Planner metadata cardinality is impossible.")
        collections = (
            self.scientificIntents,
            self.capabilityNeeds,
            self.desiredOutputs,
            self.acceptedObjectTypes,
            self.requiredProfileCapabilities,
            self.requiredTargetRoles,
            [item.parameter for item in self.parameterBindings],
            self.declaredArtifactTypes,
        )
        if any(len(items) != len(set(items)) for items in collections):
            raise ValueError("Planner metadata collections must contain unique values.")
        if any(not option or len(option) != len(set(option)) for option in self.inputObjectTypeOptions):
            raise ValueError("Planner input options must be non-empty and contain unique object types.")
        if sorted({item for option in self.inputObjectTypeOptions for item in option}) != sorted(self.acceptedObjectTypes):
            raise ValueError("Planner input options must exactly cover accepted object types.")
        if self.availability is not PlannerAvailability.available and self.independentComposable:
            raise ValueError("Unavailable planner metadata cannot be selectable/composable.")
        return self


class RegistrySnapshotEntry(StrictCapabilityModel):
    toolId: str
    toolVersion: str
    metadataHash: str = Field(pattern=r"^[0-9a-f]{64}$")


class PlannerRegistrySnapshot(StrictCapabilityModel):
    schemaVersion: Literal["1.0"] = CAPABILITY_PLANNING_SCHEMA_VERSION
    snapshotId: str
    snapshotHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    registryVersion: str
    tools: list[RegistrySnapshotEntry] = Field(max_length=CAPABILITY_PLANNING_MAX_REGISTRY_TOOLS)

    @model_validator(mode="after")
    def validate_tools(self) -> "PlannerRegistrySnapshot":
        identities = [(item.toolId, item.toolVersion) for item in self.tools]
        if identities != sorted(set(identities)):
            raise ValueError("Registry snapshot tools must be unique and sorted.")
        return self


class CapabilityDiagnostic(StrictCapabilityModel):
    code: str = Field(min_length=1, max_length=96)
    field: str = Field(min_length=1, max_length=160)
    message: str = Field(min_length=1, max_length=512)
    toolId: str | None = Field(default=None, max_length=160)
    repairable: bool = False


class PlannerBindingValue(StrictCapabilityModel):
    valueId: str = Field(min_length=1, max_length=192)
    value: str | int | float | bool | list[str]
    source: PlannerBindingSource
    sourceIdentity: str = Field(min_length=1, max_length=256)

    @model_validator(mode="after")
    def validate_finite_value(self) -> "PlannerBindingValue":
        if isinstance(self.value, float) and not math.isfinite(self.value):
            raise ValueError("Planner binding values must be finite.")
        return self


class PlannerBindingDomain(StrictCapabilityModel):
    parameter: str = Field(min_length=1, max_length=128)
    required: bool
    values: list[PlannerBindingValue] = Field(max_length=CAPABILITY_PLANNING_MAX_BINDING_VALUES)


class PlannerResourceIdentity(StrictCapabilityModel):
    objectId: str = Field(min_length=1, max_length=128)
    objectType: str = Field(min_length=1, max_length=96)
    objectHash: str = Field(min_length=1, max_length=128)
    kind: str = Field(min_length=1, max_length=96)


class EvaluatedToolCandidate(StrictCapabilityModel):
    toolId: str
    toolName: str
    toolVersion: str
    eligible: bool
    matchedScientificIntents: list[ScientificIntent] = Field(default_factory=list, max_length=16)
    matchedCapabilityNeeds: list[CapabilityNeed] = Field(default_factory=list, max_length=16)
    matchedDesiredOutputs: list[DesiredOutput] = Field(default_factory=list, max_length=16)
    acceptedResourceIds: list[str] = Field(default_factory=list, max_length=32)
    satisfiedProfileCapabilities: list[str] = Field(default_factory=list, max_length=16)
    unsatisfiedProfileCapabilities: list[str] = Field(default_factory=list, max_length=16)
    targetSemanticIds: list[str] = Field(default_factory=list, max_length=32)
    bindingDomains: list[PlannerBindingDomain] = Field(default_factory=list, max_length=32)
    reasons: list[CapabilityDiagnostic] = Field(default_factory=list, max_length=32)
    rankFacts: list[int | str] = Field(default_factory=list, max_length=16)
    costClass: Literal[1, 2, 3]
    independentComposable: bool
    collisionGroup: str | None = None


class EligibilityResolutionProvenance(StrictCapabilityModel):
    resolver: Literal["deterministic_eligibility_resolver"] = "deterministic_eligibility_resolver"
    resolverVersion: Literal["1.0"] = "1.0"


class EligibilityResolution(StrictCapabilityModel):
    schemaVersion: Literal["1.0"] = CAPABILITY_PLANNING_SCHEMA_VERSION
    resolutionId: str
    resolutionHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    intentId: str
    intentHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    profileId: str
    profileContractVersion: str
    profileSemanticHash: str
    datasetId: str
    datasetVersion: str
    registrySnapshotId: str
    registrySnapshotHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    resourceIdentities: list[PlannerResourceIdentity] = Field(max_length=32)
    evaluatedCandidates: list[EvaluatedToolCandidate] = Field(max_length=CAPABILITY_PLANNING_MAX_REGISTRY_TOOLS)
    eligibleToolIds: list[str] = Field(max_length=CAPABILITY_PLANNING_MAX_ELIGIBLE_TOOLS)
    rejectedToolIds: list[str] = Field(max_length=CAPABILITY_PLANNING_MAX_REGISTRY_TOOLS)
    diagnostics: list[CapabilityDiagnostic] = Field(default_factory=list, max_length=CAPABILITY_PLANNING_MAX_DIAGNOSTICS)
    warnings: list[CapabilityDiagnostic] = Field(default_factory=list, max_length=32)
    provenance: EligibilityResolutionProvenance = Field(default_factory=EligibilityResolutionProvenance)

    @model_validator(mode="after")
    def validate_partition(self) -> "EligibilityResolution":
        evaluated = [item.toolId for item in self.evaluatedCandidates]
        if evaluated != sorted(set(evaluated)):
            raise ValueError("Evaluated candidate identities must be unique and sorted.")
        if self.eligibleToolIds != sorted(set(self.eligibleToolIds)):
            raise ValueError("Eligible tool identities must be unique and sorted.")
        if self.rejectedToolIds != sorted(set(self.rejectedToolIds)):
            raise ValueError("Rejected tool identities must be unique and sorted.")
        if set(self.eligibleToolIds) & set(self.rejectedToolIds):
            raise ValueError("Eligible and rejected tools must be disjoint.")
        if set(evaluated) != set(self.eligibleToolIds) | set(self.rejectedToolIds):
            raise ValueError("Eligibility partition must cover every evaluated candidate.")
        return self


class ProjectedCandidate(StrictCapabilityModel):
    toolId: str
    toolName: str
    toolVersion: str
    matchedScientificIntents: list[ScientificIntent]
    matchedCapabilityNeeds: list[CapabilityNeed]
    matchedDesiredOutputs: list[DesiredOutput]
    acceptedResourceIds: list[str]
    targetSemanticIds: list[str]
    bindingDomains: list[PlannerBindingDomain]
    costClass: Literal[1, 2, 3]
    independentComposable: bool
    collisionGroup: str | None = None
    rankFacts: list[int | str] = Field(default_factory=list, max_length=16)


class EligibleCandidateProjection(StrictCapabilityModel):
    schemaVersion: Literal["1.0"] = CAPABILITY_PLANNING_SCHEMA_VERSION
    resolutionId: str
    resolutionHash: str
    candidates: list[ProjectedCandidate] = Field(max_length=CAPABILITY_PLANNING_MAX_ELIGIBLE_TOOLS)

    @model_validator(mode="after")
    def validate_candidates(self) -> "EligibleCandidateProjection":
        ids = [item.toolId for item in self.candidates]
        if ids != sorted(set(ids)):
            raise ValueError("Projected candidates must be unique and sorted.")
        return self


class CapabilitySelectionProposal(StrictCapabilityModel):
    schemaVersion: Literal["1.0"] = CAPABILITY_PLANNING_SCHEMA_VERSION
    resolutionId: str
    selectedToolIds: list[str] = Field(min_length=1, max_length=CAPABILITY_PLANNING_MAX_SELECTED_TOOLS)

    @model_validator(mode="after")
    def validate_selection(self) -> "CapabilitySelectionProposal":
        if self.selectedToolIds != sorted(set(self.selectedToolIds)):
            raise ValueError("Selected tool identities must be unique and deterministically ordered.")
        return self


class BoundParameter(StrictCapabilityModel):
    parameter: str
    value: str | int | float | bool | list[str]
    valueId: str
    source: PlannerBindingSource
    sourceIdentity: str


class SelectedCapability(StrictCapabilityModel):
    toolId: str
    toolName: str
    toolVersion: str
    coveredScientificIntents: list[ScientificIntent]
    coveredCapabilityNeeds: list[CapabilityNeed]
    coveredDesiredOutputs: list[DesiredOutput]
    inputResourceIds: list[str]
    targetSemanticIds: list[str]
    boundParameters: list[BoundParameter]
    artifactTypes: list[str]
    rankFacts: list[int | str]


class CapabilityDecisionProvenance(StrictCapabilityModel):
    provider: Literal["deterministic_mock", "openai_compatible"]
    providerContractVersion: Literal["1.0"] = "1.0"
    model: str
    repairCount: Literal[0, 1] = 0
    initialDecisionHash: str | None = None
    repairDiagnostics: list[CapabilityDiagnostic] = Field(default_factory=list, max_length=32)


class CapabilityPlanningDecision(StrictCapabilityModel):
    schemaVersion: Literal["1.0"] = CAPABILITY_PLANNING_SCHEMA_VERSION
    decisionId: str
    decisionHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    intentId: str
    intentHash: str
    profileId: str
    profileSemanticHash: str
    registrySnapshotId: str
    registrySnapshotHash: str
    resolutionId: str
    resolutionHash: str
    outcome: CapabilityPlanningOutcome
    selections: list[SelectedCapability] = Field(default_factory=list, max_length=CAPABILITY_PLANNING_MAX_SELECTED_TOOLS)
    unfulfilledDesiredOutputs: list[DesiredOutput] = Field(default_factory=list, max_length=16)
    diagnostics: list[CapabilityDiagnostic] = Field(default_factory=list, max_length=CAPABILITY_PLANNING_MAX_DIAGNOSTICS)
    warnings: list[CapabilityDiagnostic] = Field(default_factory=list, max_length=32)
    provenance: CapabilityDecisionProvenance

    @model_validator(mode="after")
    def validate_outcome(self) -> "CapabilityPlanningDecision":
        if self.outcome is CapabilityPlanningOutcome.plan_ready:
            if not self.selections or self.diagnostics:
                raise ValueError("PLAN_READY requires selections without blocking diagnostics.")
        elif self.selections:
            raise ValueError("Non-ready capability decisions cannot retain executable selections.")
        return self


def canonical_capability_json(value: BaseModel | dict[str, Any], *, identity_fields: tuple[str, ...]) -> str:
    payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else json.loads(json.dumps(value))
    for field in identity_fields:
        payload.pop(field, None)
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def capability_semantic_hash(value: BaseModel | dict[str, Any], *, identity_fields: tuple[str, ...]) -> str:
    return hashlib.sha256(canonical_capability_json(value, identity_fields=identity_fields).encode("utf-8")).hexdigest()


def deterministic_capability_id(prefix: str, value_hash: str) -> str:
    if len(value_hash) != 64 or any(char not in "0123456789abcdef" for char in value_hash):
        raise ValueError("Capability identity requires lowercase SHA-256 hex.")
    return f"{prefix}_{value_hash[:24]}"


def validate_capability_json_bounds(value: Any) -> None:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False).encode("utf-8")
    if len(encoded) > CAPABILITY_PLANNING_MAX_SERIALIZED_BYTES:
        raise ValueError("Capability planning payload exceeds the serialized byte cap.")

    def visit(node: Any, depth: int) -> None:
        if depth > CAPABILITY_PLANNING_MAX_JSON_DEPTH:
            raise ValueError("Capability planning payload exceeds the JSON nesting cap.")
        if isinstance(node, dict):
            for child in node.values():
                visit(child, depth + 1)
        elif isinstance(node, list):
            for child in node:
                visit(child, depth + 1)

    visit(value, 1)


__all__ = [name for name in globals() if name.startswith("CAPABILITY_") or name in {
    "BoundParameter", "CapabilityDecisionProvenance", "CapabilityDiagnostic",
    "CapabilityPlanningDecision", "CapabilityPlanningOutcome", "CapabilitySelectionProposal",
    "EligibilityResolution", "EligibilityResolutionProvenance", "EligibleCandidateProjection",
    "EvaluatedToolCandidate", "PlannerAvailability", "PlannerBindingDomain",
    "PlannerBindingSource", "PlannerBindingValue", "PlannerParameterBinding",
    "PlannerRegistrySnapshot", "PlannerResourceIdentity", "ProjectedCandidate", "RegistrySnapshotEntry",
    "SelectedCapability", "ToolPlannerMetadata", "canonical_capability_json",
    "capability_semantic_hash", "deterministic_capability_id", "validate_capability_json_bounds",
}]
