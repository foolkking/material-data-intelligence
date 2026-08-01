from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


NATURAL_LANGUAGE_EVIDENCE_SCHEMA_VERSION = "1.0"
NATURAL_LANGUAGE_EVIDENCE_MAX_RESOURCES = 32
NATURAL_LANGUAGE_EVIDENCE_MAX_TOOLS = 4
NATURAL_LANGUAGE_EVIDENCE_MAX_ARTIFACTS = 64
NATURAL_LANGUAGE_EVIDENCE_MAX_LINEAGE = 64
NATURAL_LANGUAGE_EVIDENCE_MAX_CLAIMS = 32
NATURAL_LANGUAGE_EVIDENCE_MAX_REFS = 64
NATURAL_LANGUAGE_EVIDENCE_MAX_SECURITY_MARKERS = 64
NATURAL_LANGUAGE_EVIDENCE_MAX_SERIALIZED_BYTES = 524_288
NATURAL_LANGUAGE_EVIDENCE_MAX_JSON_DEPTH = 14

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_INERT_TEXT = re.compile(r"(?:https?://|file://|javascript:|<script|authorization\s*:|bearer\s+)", re.IGNORECASE)


class StrictNaturalLanguageEvidenceModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class EvidenceRecordRef(StrictNaturalLanguageEvidenceModel):
    recordId: str = Field(min_length=1, max_length=128)
    recordHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    schemaVersion: str = Field(min_length=1, max_length=32)


class EvidenceResourceRef(StrictNaturalLanguageEvidenceModel):
    objectId: str = Field(min_length=1, max_length=128)
    objectType: str = Field(min_length=1, max_length=96)
    objectHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    kind: str = Field(min_length=1, max_length=96)


class EvidenceProviderRecord(StrictNaturalLanguageEvidenceModel):
    mode: Literal["DETERMINISTIC", "FAKE_DEEPSEEK", "REAL_DEEPSEEK"]
    provider: Literal["deterministic_mock", "deepseek"]
    model: str = Field(min_length=1, max_length=128)
    purposes: list[
        Literal[
            "INTENT_EXTRACTION",
            "CLARIFICATION_RESOLUTION",
            "CAPABILITY_PLAN_SELECTION",
            "MULTI_TOOL_COMPOSITION",
            "GROUNDED_INTERPRETATION",
            "PROVIDER_CONNECTION_TEST",
        ]
    ] = Field(default_factory=list, max_length=8)
    keySource: Literal["NONE", "DEEPSEEK_KEY"]
    realCallCount: int = Field(ge=0, le=12)
    promptHashes: list[str] = Field(default_factory=list, max_length=12)
    responseHashes: list[str] = Field(default_factory=list, max_length=12)

    @model_validator(mode="after")
    def validate_provider(self) -> "EvidenceProviderRecord":
        if self.mode == "REAL_DEEPSEEK":
            if self.provider != "deepseek" or self.keySource != "DEEPSEEK_KEY" or self.realCallCount < 1:
                raise ValueError("Real provider evidence must identify DeepSeek and DEEPSEEK_KEY.")
        elif self.realCallCount != 0 or self.keySource != "NONE":
            raise ValueError("Offline evidence cannot record a real key source or real call.")
        for value in [*self.promptHashes, *self.responseHashes]:
            if not _SHA256.fullmatch(value):
                raise ValueError("Provider hashes must be lowercase SHA-256 values.")
        return self


class EvidenceIntentRecord(StrictNaturalLanguageEvidenceModel):
    intentId: str = Field(min_length=1, max_length=128)
    intentHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    outcome: Literal["READY", "NEEDS_CLARIFICATION", "UNSUPPORTED"]
    clarificationRound: int = Field(ge=0, le=1)


class EvidenceSelectionRecord(StrictNaturalLanguageEvidenceModel):
    toolId: str = Field(min_length=1, max_length=160)
    toolVersion: str = Field(min_length=1, max_length=64)
    bindingHash: str = Field(pattern=r"^[0-9a-f]{64}$")


class EvidencePlanRecord(StrictNaturalLanguageEvidenceModel):
    planId: str = Field(min_length=1, max_length=128)
    planHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    schemaVersion: Literal["0.1", "0.2"]
    graphHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")


class EvidenceExecutionRef(StrictNaturalLanguageEvidenceModel):
    recordId: str = Field(min_length=1, max_length=128)
    state: str = Field(min_length=1, max_length=64)
    semanticHash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")


class EvidenceArtifactRef(StrictNaturalLanguageEvidenceModel):
    artifactId: str = Field(min_length=1, max_length=128)
    artifactType: str = Field(min_length=1, max_length=96)
    contentHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    sizeBytes: int = Field(ge=0, le=536_870_912)
    producerToolCallId: str = Field(min_length=1, max_length=128)


class EvidenceClaimLink(StrictNaturalLanguageEvidenceModel):
    claimId: str = Field(min_length=1, max_length=128)
    evidenceItemIds: list[str] = Field(min_length=1, max_length=8)


class EvidenceTokenUsage(StrictNaturalLanguageEvidenceModel):
    promptTokens: int = Field(default=0, ge=0, le=1_000_000)
    completionTokens: int = Field(default=0, ge=0, le=1_000_000)
    totalTokens: int = Field(default=0, ge=0, le=2_000_000)
    estimated: bool = False

    @model_validator(mode="after")
    def validate_total(self) -> "EvidenceTokenUsage":
        if self.totalTokens != self.promptTokens + self.completionTokens:
            raise ValueError("Token total must equal prompt plus completion tokens.")
        return self


class NaturalLanguageEvidenceCase(StrictNaturalLanguageEvidenceModel):
    schemaVersion: Literal["1.0"] = NATURAL_LANGUAGE_EVIDENCE_SCHEMA_VERSION
    caseSpecId: str = Field(min_length=1, max_length=128)
    caseSpecHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    title: str = Field(min_length=1, max_length=160)
    userText: str = Field(min_length=1, max_length=16_384)
    requiredCapabilityNeeds: list[str] = Field(min_length=1, max_length=16)
    acceptableToolIds: list[str] = Field(min_length=1, max_length=16)
    requiredOutputs: list[str] = Field(min_length=1, max_length=16)
    forbiddenFallbacks: list[str] = Field(default_factory=list, max_length=16)
    requiresClarification: bool = False
    requiresDependencyPlan: bool = False

    @model_validator(mode="after")
    def validate_identity(self) -> "NaturalLanguageEvidenceCase":
        _require_unique_sorted(self.requiredCapabilityNeeds, "requiredCapabilityNeeds")
        _require_unique_sorted(self.acceptableToolIds, "acceptableToolIds")
        _require_unique_sorted(self.requiredOutputs, "requiredOutputs")
        _require_unique_sorted(self.forbiddenFallbacks, "forbiddenFallbacks")
        _validate_inert(self.userText, allow_untrusted_goal=True)
        _verify_identity(self, "caseSpec", "caseSpecId", "caseSpecHash")
        validate_natural_language_evidence_bounds(self.model_dump(mode="json"))
        return self


class NaturalLanguageEvidenceRun(StrictNaturalLanguageEvidenceModel):
    schemaVersion: Literal["1.0"] = NATURAL_LANGUAGE_EVIDENCE_SCHEMA_VERSION
    runId: str = Field(min_length=1, max_length=128)
    runHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    caseSpecId: str = Field(min_length=1, max_length=128)
    caseSpecHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    userText: str = Field(min_length=1, max_length=16_384)
    resourceManifest: list[EvidenceResourceRef] = Field(default_factory=list, max_length=NATURAL_LANGUAGE_EVIDENCE_MAX_RESOURCES)
    provider: EvidenceProviderRecord
    profile: EvidenceRecordRef
    intent: EvidenceIntentRecord
    eligibility: EvidenceRecordRef | None = None
    selectedTools: list[EvidenceSelectionRecord] = Field(default_factory=list, max_length=NATURAL_LANGUAGE_EVIDENCE_MAX_TOOLS)
    plan: EvidencePlanRecord | None = None
    job: EvidenceExecutionRef | None = None
    toolCalls: list[EvidenceExecutionRef] = Field(default_factory=list, max_length=NATURAL_LANGUAGE_EVIDENCE_MAX_TOOLS)
    artifacts: list[EvidenceArtifactRef] = Field(default_factory=list, max_length=NATURAL_LANGUAGE_EVIDENCE_MAX_ARTIFACTS)
    executionOutcome: str = Field(min_length=1, max_length=64)
    lineage: list[EvidenceExecutionRef] = Field(default_factory=list, max_length=NATURAL_LANGUAGE_EVIDENCE_MAX_LINEAGE)
    evidenceBundle: EvidenceRecordRef | None = None
    interpretation: EvidenceRecordRef | None = None
    claimEvidenceLinks: list[EvidenceClaimLink] = Field(default_factory=list, max_length=NATURAL_LANGUAGE_EVIDENCE_MAX_CLAIMS)
    apiRefs: list[str] = Field(default_factory=list, max_length=NATURAL_LANGUAGE_EVIDENCE_MAX_REFS)
    browserRefs: list[str] = Field(default_factory=list, max_length=NATURAL_LANGUAGE_EVIDENCE_MAX_REFS)
    securityMarkers: list[str] = Field(default_factory=list, max_length=NATURAL_LANGUAGE_EVIDENCE_MAX_SECURITY_MARKERS)
    tokenUsage: EvidenceTokenUsage = Field(default_factory=EvidenceTokenUsage)
    elapsedMs: float = Field(ge=0)
    verdict: Literal["PASS", "FAIL", "BLOCKED"]
    createdAt: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_run(self) -> "NaturalLanguageEvidenceRun":
        if not math.isfinite(self.elapsedMs):
            raise ValueError("elapsedMs must be finite.")
        _require_unique_sorted([item.objectId for item in self.resourceManifest], "resourceManifest")
        _require_unique_sorted([item.toolId for item in self.selectedTools], "selectedTools")
        _require_unique_sorted([item.artifactId for item in self.artifacts], "artifacts")
        _require_unique_sorted([item.claimId for item in self.claimEvidenceLinks], "claimEvidenceLinks")
        _require_unique_sorted(self.apiRefs, "apiRefs")
        _require_unique_sorted(self.browserRefs, "browserRefs")
        _require_unique_sorted(self.securityMarkers, "securityMarkers")
        if self.intent.outcome != "READY" and any((self.plan, self.job, self.toolCalls, self.artifacts, self.lineage)):
            raise ValueError("Non-READY intent evidence cannot contain execution records.")
        if self.verdict == "PASS":
            if self.intent.outcome != "READY":
                raise ValueError("A passing run requires a READY intent.")
            if self.eligibility is None or not self.selectedTools:
                raise ValueError("A passing run requires eligibility and selected-tool records.")
            if self.plan is None or self.job is None or self.job.state != "completed":
                raise ValueError("A passing run requires an exact plan and completed job.")
            if not self.toolCalls or any(item.state != "completed" for item in self.toolCalls):
                raise ValueError("A passing run requires completed ToolCall records.")
            if not self.artifacts:
                raise ValueError("A passing run requires persisted artifact records.")
            if self.executionOutcome not in {"ALL_SUCCEEDED", "LEGACY_TERMINAL"}:
                raise ValueError("A passing run requires a successful terminal execution outcome.")
            if self.evidenceBundle is None or self.interpretation is None or not self.claimEvidenceLinks:
                raise ValueError("A passing run requires grounded evidence, interpretation, and claim links.")
            if not self.apiRefs:
                raise ValueError("A passing run requires canonical API references.")
        _verify_identity(self, "run", "runId", "runHash", exclude={"elapsedMs", "createdAt"})
        validate_natural_language_evidence_bounds(self.model_dump(mode="json"))
        return self


class DeepSeekVerificationRecord(StrictNaturalLanguageEvidenceModel):
    schemaVersion: Literal["1.0"] = NATURAL_LANGUAGE_EVIDENCE_SCHEMA_VERSION
    verificationId: str = Field(min_length=1, max_length=128)
    verificationHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    provider: Literal["deepseek"] = "deepseek"
    baseUrl: Literal["https://api.deepseek.com"] = "https://api.deepseek.com"
    keySource: Literal["DEEPSEEK_KEY"] = "DEEPSEEK_KEY"
    configured: bool
    model: Literal["deepseek-v4-flash", "deepseek-v4-pro"]
    purposes: list[str] = Field(min_length=1, max_length=8)
    realCallCount: int = Field(ge=0, le=12)
    otherRealProviderCalls: Literal[0] = 0
    runIds: list[str] = Field(default_factory=list, max_length=5)
    outcomes: list[str] = Field(default_factory=list, max_length=12)
    tokenUsage: EvidenceTokenUsage = Field(default_factory=EvidenceTokenUsage)
    sanitized: Literal[True] = True
    verdict: Literal["PASS", "FAIL", "BLOCKED"]
    createdAt: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_verification(self) -> "DeepSeekVerificationRecord":
        _require_unique_sorted(self.purposes, "purposes")
        _require_unique_sorted(self.runIds, "runIds")
        if self.verdict == "PASS" and (not self.configured or self.realCallCount < 3):
            raise ValueError("Passing live verification requires configuration and at least three real calls.")
        _verify_identity(self, "deepseek_verification", "verificationId", "verificationHash", exclude={"createdAt"})
        validate_natural_language_evidence_bounds(self.model_dump(mode="json"))
        return self


class DeepSeekCaseVerificationRef(StrictNaturalLanguageEvidenceModel):
    caseSpecId: str = Field(min_length=1, max_length=128)
    runId: str = Field(min_length=1, max_length=128)
    verificationId: str = Field(min_length=1, max_length=128)
    verificationHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    realCallCount: int = Field(ge=3, le=12)
    verdict: Literal["PASS"] = "PASS"


class DeepSeekVerificationSuite(StrictNaturalLanguageEvidenceModel):
    schemaVersion: Literal["1.0"] = NATURAL_LANGUAGE_EVIDENCE_SCHEMA_VERSION
    suiteId: str = Field(min_length=1, max_length=128)
    suiteHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    provider: Literal["deepseek"] = "deepseek"
    baseUrl: Literal["https://api.deepseek.com"] = "https://api.deepseek.com"
    keySource: Literal["DEEPSEEK_KEY"] = "DEEPSEEK_KEY"
    configured: Literal[True] = True
    model: Literal["deepseek-v4-flash", "deepseek-v4-pro"]
    cases: list[DeepSeekCaseVerificationRef] = Field(min_length=5, max_length=5)
    totalRealCallCount: int = Field(ge=15, le=60)
    otherRealProviderCalls: Literal[0] = 0
    tokenUsage: EvidenceTokenUsage = Field(default_factory=EvidenceTokenUsage)
    sanitized: Literal[True] = True
    verdict: Literal["PASS"] = "PASS"
    createdAt: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_suite(self) -> "DeepSeekVerificationSuite":
        case_ids = [item.caseSpecId for item in self.cases]
        run_ids = [item.runId for item in self.cases]
        verification_ids = [item.verificationId for item in self.cases]
        _require_unique_sorted(case_ids, "cases.caseSpecId")
        if len(run_ids) != len(set(run_ids)):
            raise ValueError("cases.runId must be unique.")
        if len(verification_ids) != len(set(verification_ids)):
            raise ValueError("cases.verificationId must be unique.")
        if self.totalRealCallCount != sum(item.realCallCount for item in self.cases):
            raise ValueError("Suite real-call total must equal its five per-case records.")
        _verify_identity(self, "deepseek_suite", "suiteId", "suiteHash", exclude={"createdAt"})
        validate_natural_language_evidence_bounds(self.model_dump(mode="json"))
        return self


class ClosureEvidenceEntry(StrictNaturalLanguageEvidenceModel):
    path: str = Field(min_length=1, max_length=320, pattern=r"^[A-Za-z0-9_./-]+$")
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bytes: int = Field(ge=0, le=536_870_912)


class Phase10LClosureManifest(StrictNaturalLanguageEvidenceModel):
    schemaVersion: Literal["1.0"] = NATURAL_LANGUAGE_EVIDENCE_SCHEMA_VERSION
    manifestId: str = Field(min_length=1, max_length=128)
    manifestHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    phase: Literal["10L"] = "10L"
    caseSpecIds: list[str] = Field(min_length=5, max_length=5)
    runIds: list[str] = Field(min_length=5, max_length=5)
    deepSeekVerificationId: str = Field(min_length=1, max_length=128)
    entries: list[ClosureEvidenceEntry] = Field(min_length=1, max_length=512)
    securityMarkers: list[str] = Field(min_length=1, max_length=NATURAL_LANGUAGE_EVIDENCE_MAX_SECURITY_MARKERS)
    verdict: Literal["PASS", "READY_WITH_EXPLICIT_LIMITS", "FAIL", "BLOCKED"]
    createdAt: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_manifest(self) -> "Phase10LClosureManifest":
        _require_unique_sorted(self.caseSpecIds, "caseSpecIds")
        _require_unique_sorted(self.runIds, "runIds")
        _require_unique_sorted([item.path for item in self.entries], "entries")
        _require_unique_sorted(self.securityMarkers, "securityMarkers")
        _verify_identity(self, "phase10l_closure", "manifestId", "manifestHash", exclude={"createdAt"})
        validate_natural_language_evidence_bounds(self.model_dump(mode="json"))
        return self


def canonical_natural_language_evidence_json(value: Any, *, exclude: set[str] | None = None) -> str:
    payload = _canonical_value(value)
    if isinstance(payload, dict):
        payload = {key: item for key, item in payload.items() if key not in (exclude or set())}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def natural_language_evidence_hash(value: Any, *, exclude: set[str] | None = None) -> str:
    return hashlib.sha256(canonical_natural_language_evidence_json(value, exclude=exclude).encode("utf-8")).hexdigest()


def deterministic_natural_language_evidence_id(prefix: str, semantic_hash: str) -> str:
    if not _SHA256.fullmatch(semantic_hash):
        raise ValueError("semantic_hash must be lowercase SHA-256.")
    return f"{prefix}_{semantic_hash[:32]}"


def strict_natural_language_evidence_json_loads(raw: str) -> Any:
    if len(raw.encode("utf-8")) > NATURAL_LANGUAGE_EVIDENCE_MAX_SERIALIZED_BYTES:
        raise ValueError("Natural-language evidence exceeds the serialized byte cap.")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(
        raw,
        object_pairs_hook=unique_object,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"Non-finite JSON value: {value}")),
    )
    validate_natural_language_evidence_bounds(value)
    return value


def validate_natural_language_evidence_bounds(value: Any) -> None:
    if _json_depth(value) > NATURAL_LANGUAGE_EVIDENCE_MAX_JSON_DEPTH:
        raise ValueError("Natural-language evidence exceeds the nesting cap.")
    if len(canonical_natural_language_evidence_json(value).encode("utf-8")) > NATURAL_LANGUAGE_EVIDENCE_MAX_SERIALIZED_BYTES:
        raise ValueError("Natural-language evidence exceeds the serialized byte cap.")


def _verify_identity(
    value: BaseModel,
    prefix: str,
    id_field: str,
    hash_field: str,
    *,
    exclude: set[str] | None = None,
) -> None:
    excluded = {id_field, hash_field, *(exclude or set())}
    semantic_hash = natural_language_evidence_hash(value, exclude=excluded)
    if getattr(value, hash_field) != semantic_hash:
        raise ValueError(f"{hash_field} does not match semantic content.")
    if getattr(value, id_field) != deterministic_natural_language_evidence_id(prefix, semantic_hash):
        raise ValueError(f"{id_field} does not match semantic content.")


def _require_unique_sorted(values: list[str], field: str) -> None:
    if values != sorted(set(values)):
        raise ValueError(f"{field} must be unique and sorted.")


def _validate_inert(value: str, *, allow_untrusted_goal: bool = False) -> None:
    if not allow_untrusted_goal and _INERT_TEXT.search(value):
        raise ValueError("Executable, URL, or authorization-shaped text is forbidden.")


def _canonical_value(value: Any) -> Any:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    if isinstance(value, dict):
        return {
            unicodedata.normalize("NFC", str(key)): _canonical_value(item)
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Non-finite values are forbidden.")
    return value


def _json_depth(value: Any) -> int:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    if isinstance(value, dict):
        return 1 + max((_json_depth(item) for item in value.values()), default=0)
    if isinstance(value, (list, tuple)):
        return 1 + max((_json_depth(item) for item in value), default=0)
    return 1
