from __future__ import annotations

import base64
from datetime import datetime
from enum import StrEnum
import hashlib
import json
import math
import re
from typing import Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


WORKSPACE_SCHEMA_VERSION = "1.0"
WORKSPACE_PANEL_SCHEMA_VERSION = "1.0"
WORKSPACE_SELECTION_SCHEMA_VERSION = "1.0"
WORKSPACE_LAYOUT_SCHEMA_VERSION = "1.0"

WORKSPACE_MAX_PANELS = 32
WORKSPACE_MAX_LAYOUT_REVISIONS = 128
WORKSPACE_MAX_SECONDARY_SELECTIONS = 16
WORKSPACE_MAX_SELECTION_URL_BYTES = 2_048
WORKSPACE_MAX_MUTATION_BYTES = 131_072
WORKSPACE_MAX_SNAPSHOT_BYTES = 524_288
WORKSPACE_MAX_JSON_DEPTH = 14
WORKSPACE_MAX_WARNINGS = 64
WORKSPACE_MAX_DIAGNOSTICS = 64

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}$")
_N2_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:,|@/-]{0,3071}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_CONTRACT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}$")
_MEDIA_TYPE = re.compile(r"^[a-z0-9][a-z0-9.+-]{0,63}/[a-z0-9][a-z0-9.+-]{0,63}$")
_FORBIDDEN_KEYS = {"__proto__", "prototype", "constructor"}
_EXECUTABLE_TEXT = re.compile(
    r"(?:<\s*(?:script|iframe|object|embed)|javascript\s*:|data\s*:\s*text/html|file\s*://|"
    r"https?\s*://|\\\\|(?:^|[\s\"'])(?:[A-Za-z]:\\|/etc/|/proc/|/home/))",
    re.IGNORECASE,
)
WORKSPACE_RENDERER_CONTRACTS = frozenset(
    {
        "workspace.overview/1.0",
        "workspace.data/1.0",
        "workspace.plan/1.0",
        "workspace.execution/1.0",
        "workspace.artifact-metadata/1.0",
        "workspace.findings/1.0",
        "workspace.evidence/1.0",
        "workspace.provenance/1.0",
        "workspace.report/1.0",
        "workspace.inert-fallback/1.0",
    }
)


class StrictWorkspaceModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=False)


class WorkspaceStatus(StrEnum):
    SOURCE_MISSING = "SOURCE_MISSING"
    UNSUPPORTED = "UNSUPPORTED"
    LEGACY_READ_ONLY = "LEGACY_READ_ONLY"
    STALE = "STALE"
    RUNNING = "RUNNING"
    PARTIAL_RESULTS = "PARTIAL_RESULTS"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    READY = "READY"
    INITIALIZING = "INITIALIZING"


class WorkspacePanelState(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    READY_NOT_RUN = "READY_NOT_RUN"
    LOADING = "LOADING"
    PRODUCED = "PRODUCED"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"
    FAILED = "FAILED"
    BLOCKED_BY_DEPENDENCY = "BLOCKED_BY_DEPENDENCY"
    STALE = "STALE"
    CAP_EXCEEDED = "CAP_EXCEEDED"
    CONTRACT_UNSUPPORTED = "CONTRACT_UNSUPPORTED"
    SOURCE_DELETED = "SOURCE_DELETED"
    PROFILE_AUTHORITY_UNAVAILABLE = "PROFILE_AUTHORITY_UNAVAILABLE"


class WorkspacePanelKind(StrEnum):
    OVERVIEW = "OVERVIEW"
    DATA = "DATA"
    PLAN = "PLAN"
    EXECUTION = "EXECUTION"
    SCIENTIFIC_RESULT = "SCIENTIFIC_RESULT"
    FINDINGS = "FINDINGS"
    EVIDENCE = "EVIDENCE"
    PROVENANCE = "PROVENANCE"
    REPORT = "REPORT"


class WorkspaceSelectionKind(StrEnum):
    DATASET_SAMPLE = "DATASET_SAMPLE"
    MATERIAL_OBJECT = "MATERIAL_OBJECT"
    STRUCTURE = "STRUCTURE"
    PERIODIC_SITE = "PERIODIC_SITE"
    LOCAL_ENVIRONMENT = "LOCAL_ENVIRONMENT"
    COORDINATION_POLYHEDRON = "COORDINATION_POLYHEDRON"
    POLYHEDRON_VERTEX = "POLYHEDRON_VERTEX"
    POLYHEDRON_FACE = "POLYHEDRON_FACE"
    EXPERIMENTAL_XRD_PEAK = "EXPERIMENTAL_XRD_PEAK"
    THEORETICAL_XRD_PEAK = "THEORETICAL_XRD_PEAK"
    XRD_MATCH = "XRD_MATCH"
    TRAJECTORY_ATOM = "TRAJECTORY_ATOM"
    TRAJECTORY_FRAME = "TRAJECTORY_FRAME"
    PHONON_Q_POINT = "PHONON_Q_POINT"
    PHONON_BRANCH = "PHONON_BRANCH"
    RECIPROCAL_POINT = "RECIPROCAL_POINT"
    VOLUMETRIC_FIELD = "VOLUMETRIC_FIELD"
    ARTIFACT = "ARTIFACT"
    EVIDENCE_ITEM = "EVIDENCE_ITEM"
    CLAIM = "CLAIM"


class WorkspaceSourceKind(StrEnum):
    PROJECT = "PROJECT"
    DATASET = "DATASET"
    PROFILE = "PROFILE"
    INTENT = "INTENT"
    ELIGIBILITY_RESOLUTION = "ELIGIBILITY_RESOLUTION"
    SELECTION_DECISION = "SELECTION_DECISION"
    PLAN = "PLAN"
    JOB = "JOB"
    TOOL_CALL = "TOOL_CALL"
    ARTIFACT = "ARTIFACT"
    DEPENDENCY_EXECUTION = "DEPENDENCY_EXECUTION"
    INTERPRETATION = "INTERPRETATION"
    EVIDENCE_BUNDLE = "EVIDENCE_BUNDLE"
    REPORT = "REPORT"
    RECIPE = "RECIPE"


class WorkspaceWarning(StrictWorkspaceModel):
    code: str = Field(min_length=1, max_length=96, pattern=r"^[A-Z][A-Z0-9_]*$")
    message: str = Field(min_length=1, max_length=512)
    sourceId: str | None = Field(default=None, max_length=96)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        return _validate_inert_text(value, "message")


class WorkspaceDurableMetadata(StrictWorkspaceModel):
    tags: tuple[str, ...] = Field(default_factory=tuple, max_length=16)
    note: str | None = Field(default=None, max_length=2_048)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(values)) != len(values):
            raise ValueError("Workspace tags must be unique")
        return tuple(_validate_inert_text(value, "tag", max_length=64) for value in values)

    @field_validator("note")
    @classmethod
    def validate_note(cls, value: str | None) -> str | None:
        return None if value is None else _validate_inert_text(value, "note")


class WorkspaceSourceRef(StrictWorkspaceModel):
    kind: WorkspaceSourceKind
    sourceId: str = Field(min_length=1, max_length=96)
    sourceHash: str | None = None
    contract: str | None = Field(default=None, max_length=128)
    contractVersion: str | None = Field(default=None, max_length=64)
    mediaType: str | None = Field(default=None, max_length=128)
    projectId: str = Field(min_length=1, max_length=64)
    jobId: str | None = Field(default=None, max_length=64)
    toolCallId: str | None = Field(default=None, max_length=64)
    stepId: str | None = Field(default=None, max_length=96)

    @field_validator("sourceId", "projectId", "jobId", "toolCallId", "stepId")
    @classmethod
    def validate_ids(cls, value: str | None) -> str | None:
        return _validate_id(value)

    @field_validator("sourceHash")
    @classmethod
    def validate_hash(cls, value: str | None) -> str | None:
        return _validate_hash(value)

    @field_validator("contract")
    @classmethod
    def validate_contract(cls, value: str | None) -> str | None:
        if value is not None and not _CONTRACT.fullmatch(value):
            raise ValueError("Invalid contract identity")
        return value

    @field_validator("mediaType")
    @classmethod
    def validate_media_type(cls, value: str | None) -> str | None:
        if value is not None and not _MEDIA_TYPE.fullmatch(value):
            raise ValueError("Invalid media type")
        return value


class WorkspacePanelLayout(StrictWorkspaceModel):
    region: Literal["PRIMARY", "SECONDARY", "DETAILS", "HIDDEN"] = "PRIMARY"
    order: int = Field(ge=0, le=31)
    width: int = Field(default=1, ge=1, le=12)
    height: int = Field(default=1, ge=1, le=12)
    collapsed: bool = False


class WorkspacePanelPlacement(StrictWorkspaceModel):
    panelId: str = Field(min_length=1, max_length=64)
    region: Literal["PRIMARY", "SECONDARY", "DETAILS", "HIDDEN"] = "PRIMARY"
    order: int = Field(ge=0, le=31)
    width: int = Field(default=1, ge=1, le=12)
    height: int = Field(default=1, ge=1, le=12)
    collapsed: bool = False

    @field_validator("panelId")
    @classmethod
    def validate_panel_id(cls, value: str) -> str:
        return _validate_id(value) or ""


class WorkspacePanel(StrictWorkspaceModel):
    schemaVersion: Literal["1.0"] = WORKSPACE_PANEL_SCHEMA_VERSION
    panelId: str = Field(min_length=1, max_length=64)
    workspaceId: str = Field(min_length=1, max_length=96)
    panelKind: WorkspacePanelKind
    title: str = Field(min_length=1, max_length=256)
    ordinal: int = Field(ge=0, le=31)
    visible: bool = True
    sourceRefs: tuple[WorkspaceSourceRef, ...] = Field(default_factory=tuple, max_length=32)
    sourceReferenceHash: str
    rendererContract: str = Field(min_length=1, max_length=128)
    state: WorkspacePanelState
    acceptedSelectionKinds: tuple[WorkspaceSelectionKind, ...] = Field(default_factory=tuple, max_length=20)
    emittedSelectionKinds: tuple[WorkspaceSelectionKind, ...] = Field(default_factory=tuple, max_length=20)
    evidenceRefs: tuple[str, ...] = Field(default_factory=tuple, max_length=32)
    provenanceRefs: tuple[str, ...] = Field(default_factory=tuple, max_length=32)
    capabilityRequirement: str | None = Field(default=None, max_length=96)
    layout: WorkspacePanelLayout
    mobilePresentationMode: Literal["STACKED", "FULL_WIDTH", "HIDDEN"] = "STACKED"
    accessibleName: str = Field(min_length=1, max_length=256)
    unsupportedReason: str | None = Field(default=None, max_length=512)
    panelStateHash: str
    contractProvenance: str = Field(default="workspace-projection/1.0", max_length=128)

    @field_validator("panelId", "workspaceId")
    @classmethod
    def validate_ids(cls, value: str) -> str:
        return _validate_id(value) or ""

    @field_validator("sourceReferenceHash", "panelStateHash")
    @classmethod
    def validate_hashes(cls, value: str) -> str:
        return _validate_hash(value) or ""

    @field_validator("rendererContract", "contractProvenance")
    @classmethod
    def validate_contracts(cls, value: str) -> str:
        if not _CONTRACT.fullmatch(value):
            raise ValueError("Invalid renderer or provenance contract")
        return value

    @field_validator("rendererContract")
    @classmethod
    def validate_renderer_allowlist(cls, value: str) -> str:
        if value not in WORKSPACE_RENDERER_CONTRACTS:
            raise ValueError("Renderer contract is not allowlisted for Workspace 1.0")
        return value

    @field_validator("title", "accessibleName", "unsupportedReason")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        return None if value is None else _validate_inert_text(value, "panel text")

    @model_validator(mode="after")
    def validate_panel(self) -> "WorkspacePanel":
        if len(set(self.acceptedSelectionKinds)) != len(self.acceptedSelectionKinds):
            raise ValueError("acceptedSelectionKinds contains duplicates")
        if len(set(self.emittedSelectionKinds)) != len(self.emittedSelectionKinds):
            raise ValueError("emittedSelectionKinds contains duplicates")
        if any(ref.projectId != self.sourceRefs[0].projectId for ref in self.sourceRefs[1:]):
            raise ValueError("Panel source references must remain in one project")
        expected_source_hash = workspace_semantic_hash([ref.model_dump(mode="json") for ref in self.sourceRefs])
        if self.sourceReferenceHash != expected_source_hash:
            raise ValueError("Panel sourceReferenceHash does not match source references")
        semantic = self.model_dump(mode="json", exclude={"panelStateHash"})
        expected = workspace_semantic_hash(semantic)
        if self.panelStateHash != expected:
            raise ValueError("panelStateHash does not match semantic content")
        return self


class WorkspaceSelectionRef(StrictWorkspaceModel):
    selectionSchemaVersion: Literal["1.0"] = WORKSPACE_SELECTION_SCHEMA_VERSION
    kind: WorkspaceSelectionKind
    sourceScopeHash: str
    projectId: str = Field(min_length=1, max_length=64)
    datasetId: str | None = Field(default=None, max_length=64)
    datasetVersion: str | None = Field(default=None, max_length=128)
    jobId: str | None = Field(default=None, max_length=64)
    objectId: str | None = Field(default=None, max_length=96)
    sampleRef: str | None = Field(default=None, max_length=96)
    structureId: str | None = Field(default=None, max_length=96)
    siteId: str | None = Field(default=None, max_length=96)
    environmentId: str | None = Field(default=None, max_length=96)
    polyhedronId: str | None = Field(default=None, max_length=96)
    vertexId: str | None = Field(default=None, max_length=1024)
    faceId: str | None = Field(default=None, max_length=3072)
    geometryReferenceId: str | None = Field(default=None, max_length=96)
    experimentalResourceId: str | None = Field(default=None, max_length=96)
    theoreticalArtifactId: str | None = Field(default=None, max_length=96)
    peakId: str | None = Field(default=None, max_length=96)
    matchId: str | None = Field(default=None, max_length=96)
    trajectoryId: str | None = Field(default=None, max_length=96)
    atomId: str | None = Field(default=None, max_length=96)
    frameId: str | None = Field(default=None, max_length=96)
    phononArtifactId: str | None = Field(default=None, max_length=96)
    qPointId: str | None = Field(default=None, max_length=96)
    branchId: str | None = Field(default=None, max_length=96)
    reciprocalArtifactId: str | None = Field(default=None, max_length=96)
    reciprocalPointId: str | None = Field(default=None, max_length=96)
    segmentId: str | None = Field(default=None, max_length=96)
    fieldId: str | None = Field(default=None, max_length=96)
    regionId: str | None = Field(default=None, max_length=96)
    artifactId: str | None = Field(default=None, max_length=96)
    artifactChecksum: str | None = None
    artifactContract: str | None = Field(default=None, max_length=128)
    artifactVersion: str | None = Field(default=None, max_length=64)
    toolCallId: str | None = Field(default=None, max_length=64)
    bundleId: str | None = Field(default=None, max_length=96)
    bundleHash: str | None = None
    evidenceItemId: str | None = Field(default=None, max_length=96)
    sourceArtifactId: str | None = Field(default=None, max_length=96)
    sourceArtifactChecksum: str | None = None
    fieldLocator: str | None = Field(default=None, max_length=160)
    interpretationId: str | None = Field(default=None, max_length=96)
    interpretationHash: str | None = None
    claimId: str | None = Field(default=None, max_length=96)

    @field_validator(
        "projectId", "datasetId", "jobId", "objectId", "sampleRef", "structureId", "siteId",
        "trajectoryId", "atomId", "frameId", "phononArtifactId", "qPointId", "branchId",
        "reciprocalArtifactId", "reciprocalPointId", "segmentId", "fieldId", "regionId",
        "artifactId", "toolCallId", "bundleId", "evidenceItemId", "sourceArtifactId",
        "interpretationId", "claimId",
        "environmentId", "polyhedronId", "geometryReferenceId",
        "experimentalResourceId", "theoreticalArtifactId", "peakId", "matchId",
    )
    @classmethod
    def validate_ids(cls, value: str | None) -> str | None:
        return _validate_id(value)

    @field_validator("vertexId", "faceId")
    @classmethod
    def validate_n2_ids(cls, value: str | None) -> str | None:
        if value is not None and not _N2_ID.fullmatch(value):
            raise ValueError("N2 selection identity is invalid")
        return value

    @field_validator("sourceScopeHash", "artifactChecksum", "bundleHash", "sourceArtifactChecksum", "interpretationHash")
    @classmethod
    def validate_hashes(cls, value: str | None) -> str | None:
        return _validate_hash(value)

    @field_validator("artifactContract")
    @classmethod
    def validate_artifact_contract(cls, value: str | None) -> str | None:
        if value is not None and not _CONTRACT.fullmatch(value):
            raise ValueError("Invalid artifact contract")
        return value

    @field_validator("fieldLocator")
    @classmethod
    def validate_locator(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}", value):
            raise ValueError("Field locator must be an exact checked identifier")
        return value

    @model_validator(mode="after")
    def validate_kind_fields(self) -> "WorkspaceSelectionRef":
        required: dict[WorkspaceSelectionKind, set[str]] = {
            WorkspaceSelectionKind.DATASET_SAMPLE: {"datasetId", "datasetVersion", "objectId", "sampleRef"},
            WorkspaceSelectionKind.MATERIAL_OBJECT: {"datasetId", "datasetVersion", "objectId"},
            WorkspaceSelectionKind.STRUCTURE: {"datasetId", "datasetVersion", "objectId", "structureId"},
            WorkspaceSelectionKind.PERIODIC_SITE: {"datasetId", "datasetVersion", "objectId", "structureId", "siteId"},
            WorkspaceSelectionKind.LOCAL_ENVIRONMENT: {"datasetId", "datasetVersion", "jobId", "objectId", "structureId", "siteId", "artifactId", "artifactChecksum", "sourceArtifactId", "sourceArtifactChecksum", "environmentId"},
            WorkspaceSelectionKind.COORDINATION_POLYHEDRON: {"datasetId", "datasetVersion", "jobId", "objectId", "structureId", "siteId", "artifactId", "artifactChecksum", "sourceArtifactId", "sourceArtifactChecksum", "environmentId", "polyhedronId"},
            WorkspaceSelectionKind.POLYHEDRON_VERTEX: {"datasetId", "datasetVersion", "jobId", "objectId", "structureId", "siteId", "artifactId", "artifactChecksum", "sourceArtifactId", "sourceArtifactChecksum", "polyhedronId", "vertexId"},
            WorkspaceSelectionKind.POLYHEDRON_FACE: {"datasetId", "datasetVersion", "jobId", "objectId", "structureId", "siteId", "artifactId", "artifactChecksum", "sourceArtifactId", "sourceArtifactChecksum", "polyhedronId", "faceId"},
            WorkspaceSelectionKind.EXPERIMENTAL_XRD_PEAK: {"datasetId", "datasetVersion", "jobId", "artifactId", "artifactChecksum", "experimentalResourceId", "peakId"},
            WorkspaceSelectionKind.THEORETICAL_XRD_PEAK: {"datasetId", "datasetVersion", "jobId", "artifactId", "artifactChecksum", "theoreticalArtifactId", "peakId"},
            WorkspaceSelectionKind.XRD_MATCH: {"datasetId", "datasetVersion", "jobId", "artifactId", "artifactChecksum", "experimentalResourceId", "theoreticalArtifactId", "matchId"},
            WorkspaceSelectionKind.TRAJECTORY_ATOM: {"datasetId", "datasetVersion", "trajectoryId", "atomId"},
            WorkspaceSelectionKind.TRAJECTORY_FRAME: {"datasetId", "datasetVersion", "trajectoryId", "frameId"},
            WorkspaceSelectionKind.PHONON_Q_POINT: {"datasetId", "datasetVersion", "phononArtifactId", "artifactChecksum", "qPointId"},
            WorkspaceSelectionKind.PHONON_BRANCH: {"datasetId", "datasetVersion", "phononArtifactId", "artifactChecksum", "branchId"},
            WorkspaceSelectionKind.RECIPROCAL_POINT: {"datasetId", "datasetVersion", "reciprocalArtifactId", "artifactChecksum", "reciprocalPointId"},
            WorkspaceSelectionKind.VOLUMETRIC_FIELD: {"datasetId", "datasetVersion", "fieldId", "artifactId", "artifactChecksum"},
            WorkspaceSelectionKind.ARTIFACT: {"jobId", "artifactId", "artifactChecksum", "artifactContract", "artifactVersion"},
            WorkspaceSelectionKind.EVIDENCE_ITEM: {"jobId", "bundleId", "bundleHash", "evidenceItemId", "sourceArtifactId", "sourceArtifactChecksum", "fieldLocator"},
            WorkspaceSelectionKind.CLAIM: {"jobId", "interpretationId", "interpretationHash", "claimId"},
        }
        missing = sorted(field for field in required[self.kind] if getattr(self, field) in {None, ""})
        if missing:
            raise ValueError(f"Selection {self.kind.value} is missing required fields: {', '.join(missing)}")
        common = {"selectionSchemaVersion", "kind", "sourceScopeHash", "projectId"}
        allowed: dict[WorkspaceSelectionKind, set[str]] = {
            WorkspaceSelectionKind.DATASET_SAMPLE: {"datasetId", "datasetVersion", "objectId", "sampleRef", "artifactId", "artifactChecksum"},
            WorkspaceSelectionKind.MATERIAL_OBJECT: {"datasetId", "datasetVersion", "objectId", "sampleRef", "artifactId", "artifactChecksum"},
            WorkspaceSelectionKind.STRUCTURE: {"datasetId", "datasetVersion", "objectId", "structureId", "artifactId", "artifactChecksum"},
            WorkspaceSelectionKind.PERIODIC_SITE: {"datasetId", "datasetVersion", "objectId", "structureId", "siteId", "artifactId", "artifactChecksum"},
            WorkspaceSelectionKind.LOCAL_ENVIRONMENT: {"datasetId", "datasetVersion", "jobId", "objectId", "structureId", "siteId", "artifactId", "artifactChecksum", "sourceArtifactId", "sourceArtifactChecksum", "environmentId", "geometryReferenceId"},
            WorkspaceSelectionKind.COORDINATION_POLYHEDRON: {"datasetId", "datasetVersion", "jobId", "objectId", "structureId", "siteId", "artifactId", "artifactChecksum", "sourceArtifactId", "sourceArtifactChecksum", "environmentId", "polyhedronId", "geometryReferenceId"},
            WorkspaceSelectionKind.POLYHEDRON_VERTEX: {"datasetId", "datasetVersion", "jobId", "objectId", "structureId", "siteId", "artifactId", "artifactChecksum", "sourceArtifactId", "sourceArtifactChecksum", "polyhedronId", "vertexId"},
            WorkspaceSelectionKind.POLYHEDRON_FACE: {"datasetId", "datasetVersion", "jobId", "objectId", "structureId", "siteId", "artifactId", "artifactChecksum", "sourceArtifactId", "sourceArtifactChecksum", "polyhedronId", "faceId"},
            WorkspaceSelectionKind.EXPERIMENTAL_XRD_PEAK: {"datasetId", "datasetVersion", "jobId", "artifactId", "artifactChecksum", "experimentalResourceId", "theoreticalArtifactId", "peakId"},
            WorkspaceSelectionKind.THEORETICAL_XRD_PEAK: {"datasetId", "datasetVersion", "jobId", "artifactId", "artifactChecksum", "experimentalResourceId", "theoreticalArtifactId", "peakId"},
            WorkspaceSelectionKind.XRD_MATCH: {"datasetId", "datasetVersion", "jobId", "artifactId", "artifactChecksum", "experimentalResourceId", "theoreticalArtifactId", "peakId", "matchId"},
            WorkspaceSelectionKind.TRAJECTORY_ATOM: {"datasetId", "datasetVersion", "trajectoryId", "atomId", "artifactId", "artifactChecksum"},
            WorkspaceSelectionKind.TRAJECTORY_FRAME: {"datasetId", "datasetVersion", "trajectoryId", "frameId", "artifactId", "artifactChecksum"},
            WorkspaceSelectionKind.PHONON_Q_POINT: {"datasetId", "datasetVersion", "phononArtifactId", "artifactChecksum", "qPointId", "branchId"},
            WorkspaceSelectionKind.PHONON_BRANCH: {"datasetId", "datasetVersion", "phononArtifactId", "artifactChecksum", "branchId", "qPointId"},
            WorkspaceSelectionKind.RECIPROCAL_POINT: {"datasetId", "datasetVersion", "reciprocalArtifactId", "artifactChecksum", "reciprocalPointId", "segmentId"},
            WorkspaceSelectionKind.VOLUMETRIC_FIELD: {"datasetId", "datasetVersion", "fieldId", "artifactId", "artifactChecksum", "regionId"},
            WorkspaceSelectionKind.ARTIFACT: {"jobId", "artifactId", "artifactChecksum", "artifactContract", "artifactVersion", "toolCallId"},
            WorkspaceSelectionKind.EVIDENCE_ITEM: {"jobId", "bundleId", "bundleHash", "evidenceItemId", "sourceArtifactId", "sourceArtifactChecksum", "fieldLocator", "claimId"},
            WorkspaceSelectionKind.CLAIM: {"jobId", "interpretationId", "interpretationHash", "claimId", "evidenceItemId"},
        }
        present = {
            name
            for name, value in self.model_dump(mode="json", exclude_none=True).items()
            if value not in {None, ""}
        }
        forbidden = sorted(present - common - allowed[self.kind])
        if forbidden:
            raise ValueError(f"Selection {self.kind.value} contains forbidden fields: {', '.join(forbidden)}")
        return self


class WorkspaceSelectionContext(StrictWorkspaceModel):
    schemaVersion: Literal["1.0"] = WORKSPACE_SELECTION_SCHEMA_VERSION
    sourceScopeHash: str
    primary: WorkspaceSelectionRef | None = None
    secondary: tuple[WorkspaceSelectionRef, ...] = Field(default_factory=tuple, max_length=WORKSPACE_MAX_SECONDARY_SELECTIONS)
    propagation: Literal["EXACT_COMPATIBLE_ONLY"] = "EXACT_COMPATIBLE_ONLY"
    compatibility: Literal["EXACT", "NOT_APPLICABLE", "STALE", "UNSUPPORTED"] = "EXACT"
    cleared: bool = False

    @field_validator("sourceScopeHash")
    @classmethod
    def validate_hash(cls, value: str) -> str:
        return _validate_hash(value) or ""

    @model_validator(mode="after")
    def validate_context(self) -> "WorkspaceSelectionContext":
        if self.cleared:
            if self.primary is not None or self.secondary:
                raise ValueError("Cleared selection context cannot retain selections")
            return self
        if self.primary is None and self.secondary:
            raise ValueError("Secondary selections require a primary selection")
        refs = (() if self.primary is None else (self.primary,)) + self.secondary
        if any(ref.sourceScopeHash != self.sourceScopeHash for ref in refs):
            raise ValueError("Selection source scope hash mismatch")
        if self.primary is not None:
            if any(ref.kind != self.primary.kind for ref in self.secondary):
                raise ValueError("Secondary selections must have the primary selection kind")
            if any(ref.projectId != self.primary.projectId for ref in self.secondary):
                raise ValueError("Selections cannot cross projects")
            if any(
                (ref.datasetId, ref.datasetVersion) != (self.primary.datasetId, self.primary.datasetVersion)
                for ref in self.secondary
            ):
                raise ValueError("Multi-selection must remain in one resource version")
        identities = [workspace_semantic_hash(ref) for ref in refs]
        if len(set(identities)) != len(identities):
            raise ValueError("Selection context contains duplicate identities")
        validate_workspace_json_bounds(self, max_bytes=WORKSPACE_MAX_MUTATION_BYTES)
        return self


class WorkspaceLayoutState(StrictWorkspaceModel):
    schemaVersion: Literal["1.0"] = WORKSPACE_LAYOUT_SCHEMA_VERSION
    activePanelId: str | None = Field(default=None, max_length=64)
    panelOrder: tuple[str, ...] = Field(default_factory=tuple, max_length=WORKSPACE_MAX_PANELS)
    visiblePanelIds: tuple[str, ...] = Field(default_factory=tuple, max_length=WORKSPACE_MAX_PANELS)
    panelLayouts: tuple[WorkspacePanelPlacement, ...] = Field(default_factory=tuple, max_length=WORKSPACE_MAX_PANELS)
    durableMetadata: WorkspaceDurableMetadata = Field(default_factory=WorkspaceDurableMetadata)

    @field_validator("activePanelId")
    @classmethod
    def validate_active_panel(cls, value: str | None) -> str | None:
        return _validate_id(value)

    @field_validator("panelOrder", "visiblePanelIds")
    @classmethod
    def validate_panel_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(_validate_id(value) or "" for value in values)
        if len(set(normalized)) != len(normalized):
            raise ValueError("Layout panel IDs must be unique")
        return normalized

    @model_validator(mode="after")
    def validate_layout(self) -> "WorkspaceLayoutState":
        panel_ids = set(self.panelOrder)
        if self.activePanelId is not None and self.activePanelId not in panel_ids:
            raise ValueError("activePanelId must belong to panelOrder")
        if not set(self.visiblePanelIds).issubset(panel_ids):
            raise ValueError("visiblePanelIds must belong to panelOrder")
        if len(self.panelLayouts) not in {0, len(self.panelOrder)}:
            raise ValueError("panelLayouts must be empty or describe every panel")
        placement_ids = [placement.panelId for placement in self.panelLayouts]
        if len(set(placement_ids)) != len(placement_ids):
            raise ValueError("panelLayouts contains duplicate panel identities")
        if self.panelLayouts and set(placement_ids) != panel_ids:
            raise ValueError("panelLayouts must describe the exact panelOrder identities")
        return self


class WorkspaceLayoutRevision(StrictWorkspaceModel):
    schemaVersion: Literal["1.0"] = WORKSPACE_LAYOUT_SCHEMA_VERSION
    workspaceId: str = Field(min_length=1, max_length=96)
    revision: int = Field(ge=0, le=WORKSPACE_MAX_LAYOUT_REVISIONS)
    layout: WorkspaceLayoutState
    selection: WorkspaceSelectionContext | None = None
    semanticHash: str
    createdBy: str = Field(min_length=1, max_length=64)
    createdAt: datetime

    @field_validator("workspaceId", "createdBy")
    @classmethod
    def validate_ids(cls, value: str) -> str:
        return _validate_id(value) or ""

    @field_validator("semanticHash")
    @classmethod
    def validate_hash(cls, value: str) -> str:
        return _validate_hash(value) or ""

    @model_validator(mode="after")
    def validate_semantic_hash(self) -> "WorkspaceLayoutRevision":
        expected = workspace_semantic_hash(
            self.model_dump(mode="json", exclude={"semanticHash", "createdAt"})
        )
        if self.semanticHash != expected:
            raise ValueError("Layout revision semanticHash mismatch")
        return self


class ScientificWorkspace(StrictWorkspaceModel):
    schemaVersion: Literal["1.0"] = WORKSPACE_SCHEMA_VERSION
    workspaceId: str = Field(min_length=1, max_length=96)
    projectId: str = Field(min_length=1, max_length=64)
    sourceJobId: str = Field(min_length=1, max_length=64)
    sourceReferenceHash: str
    datasetId: str | None = Field(default=None, max_length=64)
    datasetVersion: str | None = Field(default=None, max_length=128)
    profileId: str | None = Field(default=None, max_length=64)
    profileSemanticHash: str | None = None
    intentId: str | None = Field(default=None, max_length=96)
    intentSemanticHash: str | None = None
    planId: str | None = Field(default=None, max_length=96)
    planHash: str | None = None
    planSchemaVersion: Literal["0.1", "0.2"] | None = None
    title: str = Field(min_length=1, max_length=256)
    activePanelId: str | None = Field(default=None, max_length=64)
    pinnedSelection: WorkspaceSelectionContext | None = None
    durableMetadata: WorkspaceDurableMetadata = Field(default_factory=WorkspaceDurableMetadata)
    panelIds: tuple[str, ...] = Field(default_factory=tuple, max_length=WORKSPACE_MAX_PANELS)
    currentLayoutRevision: int = Field(ge=0, le=WORKSPACE_MAX_LAYOUT_REVISIONS)
    revision: int = Field(ge=0, le=WORKSPACE_MAX_LAYOUT_REVISIONS)
    projectedStatus: WorkspaceStatus
    historicalProjection: bool = False
    readOnly: bool = False
    warnings: tuple[WorkspaceWarning, ...] = Field(default_factory=tuple, max_length=WORKSPACE_MAX_WARNINGS)
    diagnostics: tuple[WorkspaceWarning, ...] = Field(default_factory=tuple, max_length=WORKSPACE_MAX_DIAGNOSTICS)
    artifactCount: int = Field(default=0, ge=0)
    toolCallCount: int = Field(default=0, ge=0)
    interpretationCount: int = Field(default=0, ge=0)
    reportCount: int = Field(default=0, ge=0)
    recipeCount: int = Field(default=0, ge=0)
    createdByKind: Literal["USER"]
    createdBy: str = Field(min_length=1, max_length=64)
    createdAt: datetime
    updatedAt: datetime
    executionAuthorized: Literal[False] = False
    scientificAuthority: Literal[False] = False

    @field_validator(
        "workspaceId", "projectId", "sourceJobId", "datasetId", "profileId", "intentId", "planId",
        "activePanelId", "createdBy",
    )
    @classmethod
    def validate_ids(cls, value: str | None) -> str | None:
        return _validate_id(value)

    @field_validator("sourceReferenceHash", "profileSemanticHash", "intentSemanticHash", "planHash")
    @classmethod
    def validate_hashes(cls, value: str | None) -> str | None:
        return _validate_hash(value)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return _validate_inert_text(value, "title")

    @field_validator("panelIds")
    @classmethod
    def validate_panel_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(_validate_id(value) or "" for value in values)
        if len(set(normalized)) != len(normalized):
            raise ValueError("Workspace panel IDs must be unique")
        return normalized

    @model_validator(mode="after")
    def validate_workspace(self) -> "ScientificWorkspace":
        if self.activePanelId is not None and self.activePanelId not in self.panelIds:
            raise ValueError("activePanelId must belong to the Workspace")
        if self.currentLayoutRevision != self.revision:
            raise ValueError("currentLayoutRevision must equal Workspace revision")
        if self.readOnly and self.projectedStatus not in {
            WorkspaceStatus.LEGACY_READ_ONLY,
            WorkspaceStatus.STALE,
            WorkspaceStatus.SOURCE_MISSING,
            WorkspaceStatus.UNSUPPORTED,
        }:
            raise ValueError("Read-only Workspace requires a read-only projected status")
        immutable = {
            "schemaVersion": self.schemaVersion,
            "workspaceId": self.workspaceId,
            "projectId": self.projectId,
            "sourceJobId": self.sourceJobId,
            "datasetId": self.datasetId,
            "datasetVersion": self.datasetVersion,
            "profileId": self.profileId,
            "profileSemanticHash": self.profileSemanticHash,
            "intentId": self.intentId,
            "intentSemanticHash": self.intentSemanticHash,
            "planId": self.planId,
            "planHash": self.planHash,
            "planSchemaVersion": self.planSchemaVersion,
        }
        if self.sourceReferenceHash != workspace_semantic_hash(immutable):
            raise ValueError("sourceReferenceHash does not match immutable Workspace sources")
        validate_workspace_json_bounds(self, max_bytes=WORKSPACE_MAX_SNAPSHOT_BYTES)
        return self


def canonical_workspace_payload(value: Any, *, exclude: set[str] | None = None) -> Any:
    if isinstance(value, BaseModel):
        payload = value.model_dump(mode="json", exclude=exclude or set(), exclude_none=False)
    elif isinstance(value, Mapping):
        payload = {str(key): _json_value(item) for key, item in value.items() if key not in (exclude or set())}
    elif isinstance(value, (list, tuple)):
        payload = [_json_value(item) for item in value]
    else:
        raise TypeError("Workspace canonical payload requires a model or mapping")
    _validate_json_value(payload, depth=1)
    return payload


def canonical_workspace_json(value: Any, *, exclude: set[str] | None = None) -> str:
    return json.dumps(
        canonical_workspace_payload(value, exclude=exclude),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def workspace_semantic_hash(value: Any, *, exclude: set[str] | None = None) -> str:
    return hashlib.sha256(canonical_workspace_json(value, exclude=exclude).encode("utf-8")).hexdigest()


def deterministic_workspace_id(project_id: str, source_job_id: str) -> str:
    _validate_id(project_id)
    _validate_id(source_job_id)
    digest = hashlib.sha256(f"{project_id}\x1f{source_job_id}".encode("utf-8")).hexdigest()
    return f"workspace_{digest[:32]}"


def deterministic_panel_id(workspace_id: str, panel_kind: WorkspacePanelKind | str, source_identity: str) -> str:
    _validate_id(workspace_id)
    digest = hashlib.sha256(f"{workspace_id}\x1f{panel_kind}\x1f{source_identity}".encode("utf-8")).hexdigest()
    return f"panel_{digest[:32]}"


def make_layout_revision(
    *,
    workspace_id: str,
    revision: int,
    layout: WorkspaceLayoutState,
    selection: WorkspaceSelectionContext | None,
    created_by: str,
    created_at: datetime,
) -> WorkspaceLayoutRevision:
    semantic = {
        "schemaVersion": WORKSPACE_LAYOUT_SCHEMA_VERSION,
        "workspaceId": workspace_id,
        "revision": revision,
        "layout": layout.model_dump(mode="json"),
        "selection": None if selection is None else selection.model_dump(mode="json"),
        "createdBy": created_by,
    }
    return WorkspaceLayoutRevision(
        **semantic,
        semanticHash=workspace_semantic_hash(semantic),
        createdAt=created_at,
    )


def encode_workspace_selection_url(context: WorkspaceSelectionContext) -> str:
    raw = canonical_workspace_json(context).encode("utf-8")
    token = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    if len(token.encode("ascii")) > WORKSPACE_MAX_SELECTION_URL_BYTES:
        raise ValueError("SELECTION_URL_CAP_EXCEEDED")
    return token


def decode_workspace_selection_url(token: str) -> WorkspaceSelectionContext:
    if len(token.encode("utf-8")) > WORKSPACE_MAX_SELECTION_URL_BYTES:
        raise ValueError("SELECTION_URL_CAP_EXCEEDED")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", token):
        raise ValueError("Selection URL token is not canonical base64url")
    padding = "=" * (-len(token) % 4)
    try:
        raw = base64.urlsafe_b64decode(token + padding)
    except Exception as exc:
        raise ValueError("Selection URL token is invalid") from exc
    parsed = strict_workspace_json_loads(raw.decode("utf-8"))
    context = WorkspaceSelectionContext.model_validate(parsed)
    if encode_workspace_selection_url(context) != token:
        raise ValueError("Selection URL token is not canonical")
    return context


def strict_workspace_json_loads(raw: str, *, max_bytes: int = WORKSPACE_MAX_SNAPSHOT_BYTES) -> Any:
    if len(raw.encode("utf-8")) > max_bytes:
        raise ValueError("Workspace JSON exceeds serialized byte cap")

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            if key in _FORBIDDEN_KEYS:
                raise ValueError(f"Forbidden JSON key: {key}")
            result[key] = value
        return result

    parsed = json.loads(raw, object_pairs_hook=reject_duplicates, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"Non-finite JSON value: {value}")))
    _validate_json_value(parsed, depth=1)
    return parsed


def validate_workspace_json_bounds(value: Any, *, max_bytes: int = WORKSPACE_MAX_SNAPSHOT_BYTES) -> None:
    encoded = canonical_workspace_json(value).encode("utf-8")
    if len(encoded) > max_bytes:
        raise ValueError("Workspace serialized byte cap exceeded")


def _json_value(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def _validate_json_value(value: Any, *, depth: int) -> None:
    if depth > WORKSPACE_MAX_JSON_DEPTH:
        raise ValueError("Workspace JSON depth cap exceeded")
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in _FORBIDDEN_KEYS:
                raise ValueError(f"Forbidden JSON key: {key}")
            _validate_json_value(item, depth=depth + 1)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _validate_json_value(item, depth=depth + 1)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Workspace JSON does not allow non-finite numbers")


def _validate_id(value: str | None) -> str | None:
    if value is not None and not _ID.fullmatch(value):
        raise ValueError("Invalid stable identity")
    return value


def _validate_hash(value: str | None) -> str | None:
    if value is not None and not _SHA256.fullmatch(value):
        raise ValueError("Expected lowercase SHA-256")
    return value


def _validate_inert_text(value: str, field_name: str, *, max_length: int | None = None) -> str:
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"{field_name} exceeds length cap")
    if any(ord(character) < 32 and character not in "\t\n\r" for character in value):
        raise ValueError(f"{field_name} contains control characters")
    if _EXECUTABLE_TEXT.search(value):
        raise ValueError(f"{field_name} contains executable or external-authority text")
    return value
