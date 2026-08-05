"""Strict contracts for deterministic Workspace report and recipe composition."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


REPORT_COMPOSITION_SCHEMA_VERSION = "1.0"
REPORT_COMPOSITION_MAX_PANELS = 32
REPORT_COMPOSITION_MAX_ARTIFACTS = 64
REPORT_COMPOSITION_MAX_FIGURES = 32
REPORT_COMPOSITION_MAX_TABLES = 32
REPORT_COMPOSITION_MAX_CLAIMS = 32
REPORT_COMPOSITION_MAX_EVIDENCE = 256
REPORT_COMPOSITION_MAX_WARNINGS = 128
REPORT_COMPOSITION_MAX_LIMITATIONS = 64
REPORT_COMPOSITION_MAX_CAPTIONS = 64
REPORT_COMPOSITION_MAX_SECTION_ITEMS = 256
REPORT_COMPOSITION_MAX_JSON_DEPTH = 14
REPORT_COMPOSITION_MAX_REQUEST_BYTES = 524_288
REPORT_COMPOSITION_MAX_EXPORT_BYTES = 2_097_152
REPORT_COMPOSITION_MAX_TITLE_CHARS = 256
REPORT_COMPOSITION_MAX_CAPTION_CHARS = 2_048

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_KEYS = {"__proto__", "constructor", "prototype"}
_EXECUTABLE_TEXT = re.compile(
    r"(?:<\s*/?\s*(?:script|iframe|object|embed|svg|html)|javascript\s*:|data\s*:|file\s*:|https?\s*://|"
    r"(?:^|[\\/])\.\.(?:[\\/]|$)|\b(?:eval|new\s+function|import\s*\()\b)",
    re.IGNORECASE,
)


class StrictReportCompositionModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ReportSourceRole(StrEnum):
    REPORT_FIGURE_SOURCE = "REPORT_FIGURE_SOURCE"
    REPORT_TABLE_SOURCE = "REPORT_TABLE_SOURCE"
    REPORT_FINDING_SOURCE = "REPORT_FINDING_SOURCE"
    REPORT_EVIDENCE_SOURCE = "REPORT_EVIDENCE_SOURCE"
    REPORT_PROVENANCE_SOURCE = "REPORT_PROVENANCE_SOURCE"
    REPORT_DISCLOSURE_ONLY = "REPORT_DISCLOSURE_ONLY"
    REPORT_METADATA_ONLY = "REPORT_METADATA_ONLY"
    REPORT_UNSUPPORTED = "REPORT_UNSUPPORTED"


class ReportSourceState(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    MANDATORY = "MANDATORY"
    METADATA_ONLY = "METADATA_ONLY"
    UNAVAILABLE = "UNAVAILABLE"
    STALE = "STALE"
    UNSUPPORTED = "UNSUPPORTED"
    SOURCE_INTEGRITY_FAILED = "SOURCE_INTEGRITY_FAILED"


class ReportOutcome(StrEnum):
    REPORT_PREVIEW_READY = "REPORT_PREVIEW_READY"
    REPORT_READY = "REPORT_READY"
    REPORT_READY_WITH_LIMITS = "REPORT_READY_WITH_LIMITS"
    REPORT_NO_SCIENTIFIC_RESULTS = "REPORT_NO_SCIENTIFIC_RESULTS"
    REPORT_SOURCE_STALE = "REPORT_SOURCE_STALE"
    REPORT_SOURCE_INTEGRITY_FAILED = "REPORT_SOURCE_INTEGRITY_FAILED"
    REPORT_VALIDATION_FAILED = "REPORT_VALIDATION_FAILED"
    REPORT_CAP_EXCEEDED = "REPORT_CAP_EXCEEDED"
    REPORT_AUTHORIZATION_FAILED = "REPORT_AUTHORIZATION_FAILED"


class RecipeOutcome(StrEnum):
    RECIPE_READY = "RECIPE_READY"
    RECIPE_READY_WITH_LIMITS = "RECIPE_READY_WITH_LIMITS"
    RECIPE_SOURCE_INTEGRITY_FAILED = "RECIPE_SOURCE_INTEGRITY_FAILED"
    RECIPE_VALIDATION_FAILED = "RECIPE_VALIDATION_FAILED"


class ReportExportFormat(StrEnum):
    JSON = "json"
    MARKDOWN = "markdown"


class ReportSourceReference(StrictReportCompositionModel):
    sourceKind: str = Field(min_length=1, max_length=64)
    sourceId: str = Field(min_length=1, max_length=96)
    sourceHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    contract: str | None = Field(default=None, max_length=128)
    contractVersion: str | None = Field(default=None, max_length=32)
    projectId: str = Field(min_length=1, max_length=64)
    datasetId: str | None = Field(default=None, max_length=64)
    datasetVersion: str | None = Field(default=None, max_length=128)
    jobId: str = Field(min_length=1, max_length=64)
    toolCallId: str | None = Field(default=None, max_length=96)
    stepId: str | None = Field(default=None, max_length=96)
    panelId: str | None = Field(default=None, max_length=64)
    artifactId: str | None = Field(default=None, max_length=96)
    artifactChecksum: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    interpretationId: str | None = Field(default=None, max_length=96)
    claimId: str | None = Field(default=None, max_length=96)
    evidenceItemId: str | None = Field(default=None, max_length=96)
    role: ReportSourceRole
    state: ReportSourceState
    representation: Literal["STATIC_FIGURE", "BOUNDED_TABLE", "CLAIM", "EVIDENCE", "PROVENANCE", "DISCLOSURE", "METADATA", "NONE"]
    fallback: str | None = Field(default=None, max_length=512)
    reason: str | None = Field(default=None, max_length=512)

    @field_validator(
        "sourceId", "projectId", "datasetId", "jobId", "toolCallId", "stepId",
        "panelId", "artifactId", "interpretationId", "claimId", "evidenceItemId",
    )
    @classmethod
    def validate_ids(cls, value: str | None) -> str | None:
        if value is not None and not _ID.fullmatch(value):
            raise ValueError("Invalid stable identity")
        return value


class ReportCaption(StrictReportCompositionModel):
    sourceId: str = Field(min_length=1, max_length=96)
    text: str = Field(max_length=REPORT_COMPOSITION_MAX_CAPTION_CHARS)

    @field_validator("sourceId")
    @classmethod
    def validate_source_id(cls, value: str) -> str:
        if not _ID.fullmatch(value):
            raise ValueError("Invalid caption source identity")
        return value

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return _validate_inert_text(value, "caption")


class ReportCompositionRequest(StrictReportCompositionModel):
    schemaVersion: Literal["1.0"] = REPORT_COMPOSITION_SCHEMA_VERSION
    workspaceId: str = Field(min_length=1, max_length=96)
    expectedWorkspaceRevision: int = Field(ge=0)
    title: str = Field(min_length=1, max_length=REPORT_COMPOSITION_MAX_TITLE_CHARS)
    selectedPanelIds: tuple[str, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_PANELS)
    selectedArtifactIds: tuple[str, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_ARTIFACTS)
    selectedClaimIds: tuple[str, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_CLAIMS)
    selectedEvidenceItemIds: tuple[str, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_EVIDENCE)
    itemOrder: tuple[str, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_SECTION_ITEMS)
    captions: tuple[ReportCaption, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_CAPTIONS)
    exportFormats: tuple[ReportExportFormat, ...] = Field(default=(ReportExportFormat.JSON, ReportExportFormat.MARKDOWN), max_length=2)

    @field_validator("workspaceId")
    @classmethod
    def validate_workspace_id(cls, value: str) -> str:
        if not _ID.fullmatch(value):
            raise ValueError("Invalid Workspace identity")
        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return _validate_inert_text(value, "title")

    @field_validator("selectedPanelIds", "selectedArtifactIds", "selectedClaimIds", "selectedEvidenceItemIds", "itemOrder")
    @classmethod
    def validate_identity_lists(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if len(values) != len(set(values)):
            raise ValueError("Duplicate composition source identity")
        if any(not _ID.fullmatch(value) for value in values):
            raise ValueError("Invalid composition source identity")
        return values

    @model_validator(mode="after")
    def validate_request(self) -> "ReportCompositionRequest":
        if len({item.sourceId for item in self.captions}) != len(self.captions):
            raise ValueError("Duplicate caption source identity")
        if len(set(self.exportFormats)) != len(self.exportFormats):
            raise ValueError("Duplicate export format")
        known = set(self.selectedPanelIds + self.selectedArtifactIds + self.selectedClaimIds + self.selectedEvidenceItemIds)
        if set(self.itemOrder) != known:
            raise ValueError("itemOrder must contain every selected source exactly once")
        if any(item.sourceId not in known for item in self.captions):
            raise ValueError("Caption source is not selected")
        validate_report_composition_json_bounds(self.model_dump(mode="json"), max_bytes=REPORT_COMPOSITION_MAX_REQUEST_BYTES)
        return self


class ReportSection(StrictReportCompositionModel):
    sectionId: Literal[
        "TITLE", "ANALYSIS_GOAL", "DATASET_RESOURCE_SCOPE", "METHODS_PLAN",
        "EXECUTION_STATUS", "SELECTED_RESULTS", "GROUNDED_FINDINGS",
        "WARNINGS_LIMITATIONS", "FAILED_BLOCKED_MISSING", "EVIDENCE_PROVENANCE",
        "ENVIRONMENT_REFERENCES", "EXACT_RERUN_RECIPE",
    ]
    title: str = Field(min_length=1, max_length=128)
    status: Literal["READY", "LIMITED", "UNAVAILABLE", "EMPTY"]
    items: tuple[str, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_SECTION_ITEMS)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return _validate_inert_text(value, "section title")

    @field_validator("items")
    @classmethod
    def validate_items(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        for value in values:
            if len(value) > REPORT_COMPOSITION_MAX_CAPTION_CHARS:
                raise ValueError("Report section item exceeds text cap")
            _validate_inert_text(value, "section item")
        return values


class ReportCompositionSnapshot(StrictReportCompositionModel):
    schemaVersion: Literal["1.0"] = REPORT_COMPOSITION_SCHEMA_VERSION
    reportId: str = Field(min_length=1, max_length=96)
    reportHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    compositionHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    recipeId: str = Field(min_length=1, max_length=96)
    workspaceId: str = Field(min_length=1, max_length=96)
    workspaceRevision: int = Field(ge=0)
    projectId: str = Field(min_length=1, max_length=64)
    datasetId: str | None = Field(default=None, max_length=64)
    datasetVersion: str | None = Field(default=None, max_length=128)
    sourceJobId: str = Field(min_length=1, max_length=64)
    sourcePlanId: str | None = Field(default=None, max_length=96)
    sourcePlanHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    sourcePlanSchemaVersion: Literal["0.1", "0.2"] | None = None
    title: str = Field(min_length=1, max_length=REPORT_COMPOSITION_MAX_TITLE_CHARS)
    analysisGoal: str = Field(max_length=4096)
    outcome: ReportOutcome
    selectedSources: tuple[ReportSourceReference, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_SECTION_ITEMS)
    mandatoryDisclosures: tuple[ReportSourceReference, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_WARNINGS + REPORT_COMPOSITION_MAX_LIMITATIONS)
    sections: tuple[ReportSection, ...] = Field(min_length=12, max_length=12)
    warnings: tuple[str, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_WARNINGS)
    limitations: tuple[str, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_LIMITATIONS)
    executionAuthorized: Literal[False] = False
    scientificAuthority: Literal[False] = False
    createdAt: datetime

    @field_validator("reportId", "recipeId", "workspaceId", "projectId", "datasetId", "sourceJobId", "sourcePlanId")
    @classmethod
    def validate_ids(cls, value: str | None) -> str | None:
        if value is not None and not _ID.fullmatch(value):
            raise ValueError("Invalid snapshot identity")
        return value

    @field_validator("title", "analysisGoal")
    @classmethod
    def validate_inert_fields(cls, value: str) -> str:
        return _validate_inert_text(value, "report text")

    @model_validator(mode="after")
    def validate_snapshot(self) -> "ReportCompositionSnapshot":
        section_ids = tuple(section.sectionId for section in self.sections)
        if section_ids != REPORT_SECTION_ORDER:
            raise ValueError("Report sections must use the canonical mandatory order")
        semantic = self.model_dump(mode="json", exclude={"reportId", "reportHash", "recipeId", "createdAt"})
        if report_composition_semantic_hash(semantic) != self.reportHash:
            raise ValueError("reportHash does not match the immutable Report snapshot")
        validate_report_composition_json_bounds(self.model_dump(mode="json"), max_bytes=REPORT_COMPOSITION_MAX_EXPORT_BYTES)
        return self


class RecipeStep(StrictReportCompositionModel):
    stepId: str = Field(min_length=1, max_length=96)
    toolId: str = Field(min_length=1, max_length=128)
    toolVersion: str | None = Field(default=None, max_length=64)
    adapterVersion: str | None = Field(default=None, max_length=64)
    params: dict[str, Any] = Field(default_factory=dict)
    inputRefs: tuple[dict[str, Any], ...] = Field(default=(), max_length=16)
    expectedOutputContracts: tuple[str, ...] = Field(default=(), max_length=64)

    @field_validator("stepId")
    @classmethod
    def validate_step_id(cls, value: str) -> str:
        if not _ID.fullmatch(value):
            raise ValueError("Invalid Recipe step identity")
        return value


class RecipeReplayManifest(StrictReportCompositionModel):
    schemaVersion: Literal["1.0"] = REPORT_COMPOSITION_SCHEMA_VERSION
    recipeId: str = Field(min_length=1, max_length=96)
    recipeHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    compositionHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    sourceReportId: str = Field(min_length=1, max_length=96)
    sourceReportHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    workspaceId: str = Field(min_length=1, max_length=96)
    workspaceRevision: int = Field(ge=0)
    projectId: str = Field(min_length=1, max_length=64)
    datasetId: str | None = Field(default=None, max_length=64)
    datasetVersion: str | None = Field(default=None, max_length=128)
    datasetHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    profileId: str | None = Field(default=None, max_length=96)
    profileVersion: str | None = Field(default=None, max_length=32)
    profileHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    intentId: str | None = Field(default=None, max_length=96)
    intentHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    eligibilityResolutionId: str | None = Field(default=None, max_length=96)
    eligibilityResolutionHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    plannerDecisionId: str | None = Field(default=None, max_length=96)
    plannerDecisionHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    analysisPlanId: str = Field(min_length=1, max_length=96)
    analysisPlanHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    planSchemaVersion: Literal["0.1", "0.2"]
    dependencyModel: Literal["NONE_OR_SEQUENTIAL_INDEPENDENT", "TYPED_ARTIFACT_BINDINGS"]
    graphHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    steps: tuple[RecipeStep, ...] = Field(min_length=1, max_length=4)
    dependencyBindings: tuple[dict[str, Any], ...] = Field(default=(), max_length=6)
    sourceResourceBindings: tuple[dict[str, Any], ...] = Field(default=(), max_length=16)
    originalArtifacts: tuple[ReportSourceReference, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_ARTIFACTS)
    executionOutcome: str = Field(min_length=1, max_length=64)
    providerProvenance: dict[str, Any] | None = None
    environmentProvenance: dict[str, Any] = Field(default_factory=dict)
    warnings: tuple[str, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_WARNINGS)
    limitations: tuple[str, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_LIMITATIONS)
    outcome: RecipeOutcome
    executionAuthorized: Literal[False] = False
    planCreated: Literal[False] = False
    jobCreated: Literal[False] = False
    queueMessageCreated: Literal[False] = False
    automaticReplay: Literal[False] = False
    createdAt: datetime

    @field_validator(
        "recipeId", "sourceReportId", "workspaceId", "projectId", "datasetId", "profileId", "intentId",
        "eligibilityResolutionId", "plannerDecisionId", "analysisPlanId",
    )
    @classmethod
    def validate_ids(cls, value: str | None) -> str | None:
        if value is not None and not _ID.fullmatch(value):
            raise ValueError("Invalid Recipe identity")
        return value

    @model_validator(mode="after")
    def validate_recipe(self) -> "RecipeReplayManifest":
        if self.planSchemaVersion == "0.1" and (self.dependencyBindings or self.graphHash is not None or self.dependencyModel != "NONE_OR_SEQUENTIAL_INDEPENDENT"):
            raise ValueError("AnalysisPlan 0.1 cannot acquire dependency bindings")
        if self.planSchemaVersion == "0.2" and (
            self.dependencyModel != "TYPED_ARTIFACT_BINDINGS" or self.graphHash is None
        ):
            raise ValueError("AnalysisPlan 0.2 requires an exact graph hash and typed artifact dependency semantics")
        if len({step.stepId for step in self.steps}) != len(self.steps):
            raise ValueError("Duplicate Recipe step identity")
        semantic = self.model_dump(mode="json", exclude={"recipeId", "recipeHash", "createdAt"})
        if report_composition_semantic_hash(semantic) != self.recipeHash:
            raise ValueError("recipeHash does not match the immutable Recipe manifest")
        validate_report_composition_json_bounds(self.model_dump(mode="json"), max_bytes=REPORT_COMPOSITION_MAX_EXPORT_BYTES)
        return self


class ReportExportManifest(StrictReportCompositionModel):
    schemaVersion: Literal["1.0"] = REPORT_COMPOSITION_SCHEMA_VERSION
    exportId: str = Field(min_length=1, max_length=96)
    exportHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    reportId: str = Field(min_length=1, max_length=96)
    reportHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    recipeId: str = Field(min_length=1, max_length=96)
    recipeHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    workspaceId: str = Field(min_length=1, max_length=96)
    projectId: str = Field(min_length=1, max_length=64)
    format: ReportExportFormat
    rendererContract: Literal["report_export.v1"] = "report_export.v1"
    sourceReferences: tuple[ReportSourceReference, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_SECTION_ITEMS)
    contentChecksum: str = Field(pattern=r"^[0-9a-f]{64}$")
    byteSize: int = Field(ge=0, le=REPORT_COMPOSITION_MAX_EXPORT_BYTES)
    authorizationScope: str = Field(min_length=1, max_length=128)
    omittedPayloadReasons: tuple[str, ...] = Field(default=(), max_length=REPORT_COMPOSITION_MAX_SECTION_ITEMS)
    coverage: str = Field(min_length=1, max_length=512)
    executionAuthorized: Literal[False] = False
    generatedAt: datetime

    @field_validator("exportId", "reportId", "recipeId", "workspaceId", "projectId")
    @classmethod
    def validate_ids(cls, value: str) -> str:
        if not _ID.fullmatch(value):
            raise ValueError("Invalid export identity")
        return value

    @model_validator(mode="after")
    def validate_export(self) -> "ReportExportManifest":
        semantic = self.model_dump(mode="json", exclude={"exportId", "exportHash", "generatedAt"})
        if report_composition_semantic_hash(semantic) != self.exportHash:
            raise ValueError("exportHash does not match the export manifest")
        return self


REPORT_SECTION_ORDER = (
    "TITLE", "ANALYSIS_GOAL", "DATASET_RESOURCE_SCOPE", "METHODS_PLAN",
    "EXECUTION_STATUS", "SELECTED_RESULTS", "GROUNDED_FINDINGS",
    "WARNINGS_LIMITATIONS", "FAILED_BLOCKED_MISSING", "EVIDENCE_PROVENANCE",
    "ENVIRONMENT_REFERENCES", "EXACT_RERUN_RECIPE",
)


def canonical_report_composition_json(value: Any) -> str:
    return json.dumps(_json_value(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def report_composition_semantic_hash(value: Any) -> str:
    return hashlib.sha256(canonical_report_composition_json(value).encode("utf-8")).hexdigest()


def deterministic_report_composition_id(prefix: str, semantic_hash: str) -> str:
    if not _SHA256.fullmatch(semantic_hash):
        raise ValueError("Expected lowercase SHA-256")
    return f"{prefix}_{semantic_hash[:32]}"


def strict_report_composition_json_loads(raw: str, *, max_bytes: int = REPORT_COMPOSITION_MAX_REQUEST_BYTES) -> Any:
    if len(raw.encode("utf-8")) > max_bytes:
        raise ValueError("Report composition JSON exceeds serialized byte cap")

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            if key in _FORBIDDEN_KEYS:
                raise ValueError(f"Forbidden JSON key: {key}")
            result[key] = value
        return result

    parsed = json.loads(
        raw,
        object_pairs_hook=reject_duplicates,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"Non-finite JSON value: {value}")),
    )
    _validate_json_value(parsed, depth=1)
    return parsed


def validate_report_composition_json_bounds(value: Any, *, max_bytes: int) -> None:
    _validate_json_value(_json_value(value), depth=1)
    if len(canonical_report_composition_json(value).encode("utf-8")) > max_bytes:
        raise ValueError("Report composition serialized byte cap exceeded")


def _validate_inert_text(value: str, field_name: str) -> str:
    if any(ord(character) < 32 and character not in "\t\n\r" for character in value):
        raise ValueError(f"{field_name} contains control characters")
    if _EXECUTABLE_TEXT.search(value):
        raise ValueError(f"{field_name} contains executable or external-authority text")
    return value


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
    if depth > REPORT_COMPOSITION_MAX_JSON_DEPTH:
        raise ValueError("Report composition JSON depth cap exceeded")
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in _FORBIDDEN_KEYS:
                raise ValueError(f"Forbidden JSON key: {key}")
            _validate_json_value(item, depth=depth + 1)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _validate_json_value(item, depth=depth + 1)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Report composition JSON does not allow non-finite numbers")


__all__ = [name for name in globals() if name.startswith("REPORT_") or name in {
    "ReportCaption", "ReportCompositionRequest", "ReportCompositionSnapshot",
    "ReportExportFormat", "ReportExportManifest", "ReportOutcome", "ReportSection",
    "ReportSourceReference", "ReportSourceRole", "ReportSourceState", "RecipeOutcome",
    "RecipeReplayManifest", "RecipeStep", "canonical_report_composition_json",
    "deterministic_report_composition_id", "report_composition_semantic_hash",
    "strict_report_composition_json_loads", "validate_report_composition_json_bounds",
}]
