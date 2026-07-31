"""Strict contracts for grounded post-execution scientific interpretation."""

from __future__ import annotations

from enum import Enum
import hashlib
import json
import math
import re
import unicodedata
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


SCIENTIFIC_EVIDENCE_SCHEMA_VERSION = "1.0"
GROUNDED_INTERPRETATION_SCHEMA_VERSION = "1.0"
INTERPRETATION_EXECUTION_SCHEMA_VERSION = "1.0"
INTERPRETATION_MAX_SOURCE_ARTIFACTS = 16
INTERPRETATION_MAX_UNSUPPORTED_ARTIFACTS = 128
INTERPRETATION_MAX_EVIDENCE_ITEMS = 256
INTERPRETATION_MAX_WARNINGS = 128
INTERPRETATION_MAX_LIMITATIONS = 64
INTERPRETATION_MAX_TABLE_ROWS = 64
INTERPRETATION_MAX_SERIES_SUMMARIES = 64
INTERPRETATION_MAX_EVIDENCE_REFS_PER_CLAIM = 8
INTERPRETATION_MAX_CLAIMS = 32
INTERPRETATION_MAX_RECOMMENDATIONS = 8
INTERPRETATION_MAX_JSON_DEPTH = 14
INTERPRETATION_MAX_BUNDLE_BYTES = 262_144
INTERPRETATION_MAX_PROVIDER_BYTES = 262_144
INTERPRETATION_MAX_RESULT_BYTES = 131_072
INTERPRETATION_MAX_TEXT = 2_048
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9_.:@+-]{1,160}$")


class StrictInterpretationModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class EvidenceKind(str, Enum):
    scalar = "SCALAR"
    range = "RANGE"
    category = "CATEGORY"
    count = "COUNT"
    boolean = "BOOLEAN"
    ordered_series_summary = "ORDERED_SERIES_SUMMARY"
    table_row = "TABLE_ROW"
    warning = "WARNING"
    limitation = "LIMITATION"
    execution_state = "EXECUTION_STATE"
    provenance = "PROVENANCE"


class EvidenceLinkRole(str, Enum):
    supporting = "SUPPORTING"
    limiting = "LIMITING"
    contradicting = "CONTRADICTING"


class ClaimType(str, Enum):
    observation = "OBSERVATION"
    comparison = "COMPARISON"
    anomaly = "ANOMALY"
    warning = "WARNING"
    limitation = "LIMITATION"
    recommendation = "RECOMMENDATION"
    no_supported_conclusion = "NO_SUPPORTED_CONCLUSION"


class ClaimPredicate(str, Enum):
    has_value = "HAS_VALUE"
    has_range = "HAS_RANGE"
    has_count = "HAS_COUNT"
    has_category = "HAS_CATEGORY"
    reports_warning = "REPORTS_WARNING"
    reports_limitation = "REPORTS_LIMITATION"
    differs_from = "DIFFERS_FROM"
    exceeds_declared_threshold = "EXCEEDS_DECLARED_THRESHOLD"
    is_missing = "IS_MISSING"
    is_partial = "IS_PARTIAL"
    suggests_follow_up = "SUGGESTS_FOLLOW_UP"
    no_supported_conclusion = "NO_SUPPORTED_CONCLUSION"


class ClaimConfidence(str, Enum):
    direct = "DIRECT"
    qualified = "QUALIFIED"
    limited = "LIMITED"


class GroundingStatus(str, Enum):
    grounded = "GROUNDED"
    rejected = "REJECTED"


class InterpretationMode(str, Enum):
    deterministic = "DETERMINISTIC"
    strict_provider = "STRICT_PROVIDER"


class InterpretationOutcome(str, Enum):
    ready = "INTERPRETATION_READY"
    ready_with_limits = "INTERPRETATION_READY_WITH_LIMITS"
    no_supported_evidence = "NO_SUPPORTED_EVIDENCE"
    source_not_terminal = "SOURCE_NOT_TERMINAL"
    source_integrity_failed = "SOURCE_INTEGRITY_FAILED"
    evidence_cap_exceeded = "EVIDENCE_CAP_EXCEEDED"
    provider_failed = "PROVIDER_FAILED"
    validation_failed = "VALIDATION_FAILED"


class BundleCompleteness(str, Enum):
    complete = "COMPLETE"
    partial = "PARTIAL"
    unsupported = "UNSUPPORTED"


class EvidenceFieldLocator(StrictInterpretationModel):
    fieldId: str = Field(min_length=1, max_length=160)
    semanticKey: str = Field(min_length=1, max_length=160)
    entityId: str | None = Field(default=None, max_length=160)

    @model_validator(mode="after")
    def validate_locator(self) -> "EvidenceFieldLocator":
        for value in (self.fieldId, self.semanticKey, self.entityId):
            if value is not None:
                _safe_identifier(value, "field locator")
        return self


class EvidenceValue(StrictInterpretationModel):
    scalar: bool | int | float | str | None = None
    minimum: float | None = None
    maximum: float | None = None
    values: list[bool | int | float | str] = Field(default_factory=list, max_length=64)

    @model_validator(mode="after")
    def validate_value(self) -> "EvidenceValue":
        numeric_values = [value for value in (self.scalar, self.minimum, self.maximum, *self.values) if isinstance(value, float)]
        if any(not math.isfinite(value) for value in numeric_values):
            raise ValueError("Evidence values must be finite.")
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("Evidence ranges must be ordered.")
        if self.scalar is None and self.minimum is None and self.maximum is None and not self.values:
            raise ValueError("EvidenceValue requires a scalar, range, or bounded values.")
        return self


class ScientificEvidenceItem(StrictInterpretationModel):
    schemaVersion: Literal["1.0"] = SCIENTIFIC_EVIDENCE_SCHEMA_VERSION
    evidenceItemId: str = Field(min_length=1, max_length=96)
    semanticRole: str = Field(min_length=1, max_length=96)
    evidenceKind: EvidenceKind
    subjectId: str = Field(min_length=1, max_length=160)
    valueKind: str = Field(min_length=1, max_length=64)
    normalizedValue: EvidenceValue
    displayValue: str = Field(min_length=1, max_length=512)
    unit: str | None = Field(default=None, max_length=64)
    unitAuthority: str | None = Field(default=None, max_length=96)
    referenceConvention: str | None = Field(default=None, max_length=160)
    sourceArtifactId: str = Field(min_length=1, max_length=96)
    sourceArtifactChecksum: str = Field(pattern=r"^[0-9a-f]{64}$")
    artifactContract: str = Field(min_length=1, max_length=160)
    artifactContractVersion: str = Field(min_length=1, max_length=128)
    sourceToolId: str = Field(min_length=1, max_length=160)
    sourceToolVersion: str = Field(min_length=1, max_length=64)
    producerStepId: str = Field(min_length=1, max_length=96)
    producerToolCallId: str = Field(min_length=1, max_length=96)
    fieldLocator: EvidenceFieldLocator
    datasetId: str = Field(min_length=1, max_length=160)
    datasetVersion: str = Field(min_length=1, max_length=128)
    resourceId: str | None = Field(default=None, max_length=160)
    warnings: list[str] = Field(default_factory=list, max_length=16)
    limitations: list[str] = Field(default_factory=list, max_length=16)
    projectorVersion: str = Field(min_length=1, max_length=64)
    providerSafe: bool = True

    @model_validator(mode="after")
    def validate_identity(self) -> "ScientificEvidenceItem":
        for value in (self.semanticRole, self.subjectId, self.valueKind, self.sourceArtifactId, self.sourceToolId, self.producerStepId, self.producerToolCallId, self.datasetId):
            _safe_identifier(value, "evidence identity")
        semantic = self.model_dump(mode="json", exclude={"evidenceItemId"})
        expected = deterministic_interpretation_id("evidence", interpretation_semantic_hash(semantic))
        if self.evidenceItemId != expected:
            raise ValueError("evidenceItemId does not match semantic content.")
        _validate_inert_text_collection(self.warnings + self.limitations)
        return self


class ScientificEvidenceRef(StrictInterpretationModel):
    schemaVersion: Literal["1.0"] = SCIENTIFIC_EVIDENCE_SCHEMA_VERSION
    evidenceItemId: str = Field(min_length=1, max_length=96)
    role: EvidenceLinkRole = EvidenceLinkRole.supporting


class ScientificEvidenceBundle(StrictInterpretationModel):
    schemaVersion: Literal["1.0"] = SCIENTIFIC_EVIDENCE_SCHEMA_VERSION
    bundleId: str = Field(min_length=1, max_length=96)
    bundleHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    projectId: str = Field(min_length=1, max_length=160)
    datasetId: str = Field(min_length=1, max_length=160)
    datasetVersion: str = Field(min_length=1, max_length=128)
    profileId: str | None = Field(default=None, max_length=160)
    profileSemanticHash: str | None = Field(default=None, max_length=128)
    intentId: str | None = Field(default=None, max_length=96)
    intentHash: str | None = Field(default=None, max_length=64)
    eligibilityResolutionId: str | None = Field(default=None, max_length=96)
    eligibilityResolutionHash: str | None = Field(default=None, max_length=64)
    selectionDecisionId: str | None = Field(default=None, max_length=96)
    selectionDecisionHash: str | None = Field(default=None, max_length=64)
    planId: str = Field(min_length=1, max_length=96)
    planHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    planSchemaVersion: Literal["0.1", "0.2"]
    graphHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    jobId: str = Field(min_length=1, max_length=96)
    sourceJobTerminalState: Literal["completed", "failed", "partial_success"]
    executionOutcome: Literal["ALL_SUCCEEDED", "PARTIAL_RESULTS", "ALL_FAILED", "VALIDATION_ABORTED", "LEGACY_TERMINAL"]
    allSucceeded: bool
    partialResults: bool
    supportedArtifactCount: int = Field(ge=0, le=INTERPRETATION_MAX_SOURCE_ARTIFACTS)
    unsupportedArtifactCount: int = Field(ge=0, le=INTERPRETATION_MAX_UNSUPPORTED_ARTIFACTS)
    failedStepCount: int = Field(ge=0, le=4)
    blockedStepCount: int = Field(ge=0, le=4)
    bundleCompleteness: BundleCompleteness
    bundleWarnings: list[str] = Field(default_factory=list, max_length=INTERPRETATION_MAX_WARNINGS)
    bundleLimitations: list[str] = Field(default_factory=list, max_length=INTERPRETATION_MAX_LIMITATIONS)
    sourceArtifactIds: list[str] = Field(default_factory=list, max_length=INTERPRETATION_MAX_SOURCE_ARTIFACTS)
    projectorVersions: dict[str, str] = Field(default_factory=dict, max_length=INTERPRETATION_MAX_SOURCE_ARTIFACTS)
    evidenceItems: list[ScientificEvidenceItem] = Field(default_factory=list, max_length=INTERPRETATION_MAX_EVIDENCE_ITEMS)

    @model_validator(mode="after")
    def validate_bundle(self) -> "ScientificEvidenceBundle":
        if self.sourceArtifactIds != sorted(set(self.sourceArtifactIds)):
            raise ValueError("sourceArtifactIds must be unique and sorted.")
        item_ids = [item.evidenceItemId for item in self.evidenceItems]
        if item_ids != sorted(set(item_ids)):
            raise ValueError("evidenceItems must be unique and sorted by evidenceItemId.")
        if set(self.projectorVersions) != set(self.sourceArtifactIds):
            raise ValueError("projectorVersions must identify every supported source artifact exactly.")
        if self.supportedArtifactCount != len(self.sourceArtifactIds):
            raise ValueError("supportedArtifactCount must match sourceArtifactIds.")
        if any(item.sourceArtifactId not in self.sourceArtifactIds for item in self.evidenceItems):
            raise ValueError("Every evidence item must belong to the current bundle.")
        semantic = self.model_dump(mode="json", exclude={"bundleId", "bundleHash"})
        expected_hash = interpretation_semantic_hash(semantic)
        if self.bundleHash != expected_hash or self.bundleId != deterministic_interpretation_id("bundle", expected_hash):
            raise ValueError("Evidence bundle identity is invalid.")
        validate_interpretation_json_bounds(self.model_dump(mode="json"), max_bytes=INTERPRETATION_MAX_BUNDLE_BYTES)
        return self


class ScientificClaim(StrictInterpretationModel):
    schemaVersion: Literal["1.0"] = GROUNDED_INTERPRETATION_SCHEMA_VERSION
    claimId: str = Field(min_length=1, max_length=96)
    claimType: ClaimType
    subjectEvidenceIds: list[str] = Field(min_length=1, max_length=INTERPRETATION_MAX_EVIDENCE_REFS_PER_CLAIM)
    supportingEvidenceIds: list[str] = Field(min_length=1, max_length=INTERPRETATION_MAX_EVIDENCE_REFS_PER_CLAIM)
    limitingEvidenceIds: list[str] = Field(default_factory=list, max_length=INTERPRETATION_MAX_EVIDENCE_REFS_PER_CLAIM)
    contradictingEvidenceIds: list[str] = Field(default_factory=list, max_length=INTERPRETATION_MAX_EVIDENCE_REFS_PER_CLAIM)
    semanticPredicate: ClaimPredicate
    qualifiers: list[str] = Field(default_factory=list, max_length=16)
    structuredPayload: dict[str, bool | int | float | str] = Field(default_factory=dict, max_length=16)
    renderedText: str = Field(min_length=1, max_length=INTERPRETATION_MAX_TEXT)
    scope: str = Field(min_length=1, max_length=160)
    confidenceClass: ClaimConfidence
    groundingStatus: GroundingStatus = GroundingStatus.grounded
    displayOrder: int = Field(ge=0, lt=INTERPRETATION_MAX_CLAIMS)

    @model_validator(mode="after")
    def validate_claim(self) -> "ScientificClaim":
        for values in (self.subjectEvidenceIds, self.supportingEvidenceIds, self.limitingEvidenceIds, self.contradictingEvidenceIds):
            if values != sorted(set(values)):
                raise ValueError("Claim evidence references must be unique and sorted.")
        if any(isinstance(value, float) and not math.isfinite(value) for value in self.structuredPayload.values()):
            raise ValueError("Claim payload numbers must be finite.")
        _validate_inert_text(self.renderedText)
        _validate_inert_text_collection(self.qualifiers)
        semantic = self.model_dump(mode="json", exclude={"claimId", "displayOrder"})
        expected = deterministic_interpretation_id("claim", interpretation_semantic_hash(semantic))
        if self.claimId != expected:
            raise ValueError("claimId does not match semantic content.")
        return self


class ScientificRecommendation(StrictInterpretationModel):
    recommendationId: str = Field(min_length=1, max_length=96)
    reasonEvidenceIds: list[str] = Field(min_length=1, max_length=INTERPRETATION_MAX_EVIDENCE_REFS_PER_CLAIM)
    suggestedGoalCategory: str = Field(min_length=1, max_length=96)
    expectedMissingEvidence: list[str] = Field(default_factory=list, max_length=8)
    limitation: str = Field(min_length=1, max_length=512)
    executionAuthorized: Literal[False] = False
    planCreated: Literal[False] = False
    jobCreated: Literal[False] = False


class GroundedScientificInterpretation(StrictInterpretationModel):
    schemaVersion: Literal["1.0"] = GROUNDED_INTERPRETATION_SCHEMA_VERSION
    interpretationId: str = Field(min_length=1, max_length=96)
    interpretationHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    sourceBundleId: str = Field(min_length=1, max_length=96)
    sourceBundleHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    sourceJobId: str = Field(min_length=1, max_length=96)
    sourcePlanId: str = Field(min_length=1, max_length=96)
    sourcePlanHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    sourceGraphHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    mode: InterpretationMode
    provider: str = Field(min_length=1, max_length=64)
    providerVersion: str = Field(min_length=1, max_length=64)
    claims: list[ScientificClaim] = Field(default_factory=list, max_length=INTERPRETATION_MAX_CLAIMS)
    globalWarnings: list[str] = Field(default_factory=list, max_length=INTERPRETATION_MAX_WARNINGS)
    globalLimitations: list[str] = Field(default_factory=list, max_length=INTERPRETATION_MAX_LIMITATIONS)
    recommendations: list[ScientificRecommendation] = Field(default_factory=list, max_length=INTERPRETATION_MAX_RECOMMENDATIONS)
    completeness: BundleCompleteness
    partialResultState: bool
    repairCount: int = Field(ge=0, le=1)
    outcome: InterpretationOutcome
    validationOutcome: Literal["VALID", "INVALID"]
    executionRecordId: str = Field(min_length=1, max_length=96)
    createdAt: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_interpretation(self) -> "GroundedScientificInterpretation":
        claim_ids = [claim.claimId for claim in self.claims]
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("Interpretation claims must be unique.")
        if self.outcome in {InterpretationOutcome.ready, InterpretationOutcome.ready_with_limits} and not self.claims:
            raise ValueError("Ready interpretation outcomes require grounded claims.")
        if self.outcome == InterpretationOutcome.ready_with_limits and not self.globalLimitations:
            raise ValueError("Ready-with-limits requires an explicit limitation.")
        semantic = self.model_dump(mode="json", exclude={"interpretationId", "interpretationHash", "createdAt"})
        expected_hash = interpretation_semantic_hash(semantic)
        if self.interpretationHash != expected_hash or self.interpretationId != deterministic_interpretation_id("interpretation", expected_hash):
            raise ValueError("Interpretation identity is invalid.")
        validate_interpretation_json_bounds(self.model_dump(mode="json"), max_bytes=INTERPRETATION_MAX_RESULT_BYTES)
        return self


class InterpretationExecutionRecord(StrictInterpretationModel):
    schemaVersion: Literal["1.0"] = INTERPRETATION_EXECUTION_SCHEMA_VERSION
    executionRecordId: str = Field(min_length=1, max_length=96)
    executionRecordHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    sourceJobId: str = Field(min_length=1, max_length=96)
    sourcePlanId: str = Field(min_length=1, max_length=96)
    sourcePlanHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    sourceGraphHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    sourceBundleId: str = Field(min_length=1, max_length=96)
    sourceBundleHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    mode: InterpretationMode
    provider: str = Field(min_length=1, max_length=64)
    providerVersion: str = Field(min_length=1, max_length=64)
    providerModel: str | None = Field(default=None, max_length=128)
    providerConfigHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    idempotencyKeyHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    promptProjectionHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    initialResponseHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    repairedResponseHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    responseHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    repairCount: int = Field(ge=0, le=1)
    evidenceItemCount: int = Field(ge=0, le=INTERPRETATION_MAX_EVIDENCE_ITEMS)
    claimCount: int = Field(ge=0, le=INTERPRETATION_MAX_CLAIMS)
    warningCount: int = Field(ge=0, le=INTERPRETATION_MAX_WARNINGS)
    limitationCount: int = Field(ge=0, le=INTERPRETATION_MAX_LIMITATIONS)
    outcome: InterpretationOutcome
    diagnostics: list[str] = Field(default_factory=list, max_length=INTERPRETATION_MAX_WARNINGS)
    caps: dict[str, int] = Field(default_factory=dict, max_length=16)
    elapsedMs: float = Field(ge=0)
    createdAt: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_record(self) -> "InterpretationExecutionRecord":
        if not math.isfinite(self.elapsedMs):
            raise ValueError("elapsedMs must be finite.")
        _validate_inert_text_collection(self.diagnostics)
        semantic = self.model_dump(mode="json", exclude={"executionRecordId", "executionRecordHash", "createdAt", "elapsedMs"})
        expected_hash = interpretation_semantic_hash(semantic)
        if self.executionRecordHash != expected_hash or self.executionRecordId != deterministic_interpretation_id("interpretation_execution", expected_hash):
            raise ValueError("Interpretation execution identity is invalid.")
        return self


def canonical_interpretation_json(value: Any) -> str:
    return json.dumps(_canonical_value(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def interpretation_semantic_hash(value: Any) -> str:
    return hashlib.sha256(canonical_interpretation_json(value).encode("utf-8")).hexdigest()


def deterministic_interpretation_id(prefix: str, semantic_hash: str) -> str:
    if not _SHA256.fullmatch(semantic_hash):
        raise ValueError("semantic_hash must be lowercase SHA-256.")
    return f"{prefix}_{semantic_hash[:32]}"


def strict_interpretation_json_loads(raw: str, *, max_bytes: int = INTERPRETATION_MAX_PROVIDER_BYTES) -> Any:
    if len(raw.encode("utf-8")) > max_bytes:
        raise ValueError("Interpretation JSON exceeds the serialized byte cap.")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(raw, object_pairs_hook=unique_object, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"Non-finite JSON value: {value}")))
    validate_interpretation_json_bounds(value, max_bytes=max_bytes)
    return value


def validate_interpretation_json_bounds(value: Any, *, max_bytes: int) -> None:
    if _json_depth(value) > INTERPRETATION_MAX_JSON_DEPTH:
        raise ValueError("Interpretation JSON exceeds the nesting cap.")
    if len(canonical_interpretation_json(value).encode("utf-8")) > max_bytes:
        raise ValueError("Interpretation JSON exceeds the serialized byte cap.")


def _canonical_value(value: Any) -> Any:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    if isinstance(value, dict):
        return {unicodedata.normalize("NFC", str(key)): _canonical_value(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Non-finite values are forbidden.")
    return value


def _json_depth(value: Any) -> int:
    if isinstance(value, dict):
        return 1 + max((_json_depth(item) for item in value.values()), default=0)
    if isinstance(value, list):
        return 1 + max((_json_depth(item) for item in value), default=0)
    return 1


def _safe_identifier(value: str, field: str) -> None:
    if not _SAFE_ID.fullmatch(value) or any(token in value.lower() for token in ("javascript:", "file:", "http:", "https:")):
        raise ValueError(f"{field} contains external or executable authority.")


def _validate_inert_text(value: str) -> None:
    lowered = value.lower()
    forbidden = ("<script", "javascript:", "file://", "http://", "https://", "```", "eval(", "new function")
    if any(token in lowered for token in forbidden):
        raise ValueError("Interpretation text contains executable or external authority.")


def _validate_inert_text_collection(values: list[str]) -> None:
    for value in values:
        if not value or len(value) > INTERPRETATION_MAX_TEXT:
            raise ValueError("Interpretation text must be bounded and non-empty.")
        _validate_inert_text(value)
