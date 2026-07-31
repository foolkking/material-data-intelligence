"""Read-only evidence projection and grounded scientific interpretation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import time
from types import MappingProxyType
from typing import Any, Callable, Mapping

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from mdi_artifact_core import (
    PHONON_BAND_DOS_SCHEMA_VERSION,
    PHONON_BAND_DOS_SUMMARY_SCHEMA_VERSION,
    PHONON_BAND_SCHEMA_VERSION,
    PHONON_DOS_SUMMARY_SCHEMA_VERSION,
    PHONON_DOS_SCHEMA_VERSION,
    PHONON_SUMMARY_SCHEMA_VERSION,
    VOLUMETRIC_FIELD_SCHEMA_VERSION,
    validate_phonon_band,
    validate_phonon_band_dos,
    validate_phonon_band_dos_summary,
    validate_phonon_dos,
    validate_phonon_dos_summary,
    validate_phonon_summary,
    validate_volumetric_field,
)
from mdi_schemas import (
    BundleCompleteness,
    ClaimConfidence,
    ClaimPredicate,
    ClaimType,
    EvidenceFieldLocator,
    EvidenceKind,
    EvidenceValue,
    GroundedScientificInterpretation,
    GroundingStatus,
    InterpretationExecutionRecord,
    InterpretationMode,
    InterpretationOutcome,
    INTERPRETATION_MAX_UNSUPPORTED_ARTIFACTS,
    ScientificClaim,
    ScientificEvidenceBundle,
    ScientificEvidenceItem,
    ScientificRecommendation,
    deterministic_interpretation_id,
    interpretation_semantic_hash,
    strict_interpretation_json_loads,
    validate_interpretation_json_bounds,
)


PROJECTOR_VERSION = "phase10l4.projectors.v1"
DETERMINISTIC_INTERPRETER_VERSION = "phase10l4.deterministic.v1"
STRICT_PROVIDER_CONTRACT_VERSION = "phase10l4.provider.v1"
TERMINAL_JOB_STATES = {"completed", "failed", "partial_success"}


@dataclass(frozen=True)
class ArtifactProjectorContract:
    tool_id: str
    artifact_type: str
    contract_family: str
    accepted_versions: tuple[str, ...]
    media_types: tuple[str, ...] = ("application/json",)
    projector_version: str = PROJECTOR_VERSION


ARTIFACT_PROJECTOR_CONTRACTS: Mapping[tuple[str, str], ArtifactProjectorContract] = MappingProxyType({
    (contract.tool_id, contract.artifact_type): contract
    for contract in (
        ArtifactProjectorContract("table.numeric_summary", "table_json", "platform.table.numeric_summary", ("platform.table.numeric_summary.v1",)),
        ArtifactProjectorContract("ml.basic_metrics", "metrics_json", "platform.ml.basic_metrics", ("platform.ml.basic_metrics.v1",)),
        ArtifactProjectorContract("structure.summary", "structure_json", "platform.structure.summary", ("platform.structure.summary.v1",)),
        ArtifactProjectorContract("phonon.band", "phonon_band_json", "phase10h.phonon", (PHONON_BAND_SCHEMA_VERSION,)),
        ArtifactProjectorContract("phonon.band", "phonon_summary_json", "phase10h.phonon", (PHONON_SUMMARY_SCHEMA_VERSION,)),
        ArtifactProjectorContract("phonon.dos", "phonon_dos_json", "phase10h.phonon", (PHONON_DOS_SCHEMA_VERSION,)),
        ArtifactProjectorContract("phonon.dos", "phonon_summary_json", "phase10h.phonon", (PHONON_DOS_SUMMARY_SCHEMA_VERSION,)),
        ArtifactProjectorContract("phonon.band_dos", "phonon_band_dos_json", "phase10h.phonon_band_dos", (PHONON_BAND_DOS_SCHEMA_VERSION,)),
        ArtifactProjectorContract("phonon.band_dos", "phonon_summary_json", "phase10h.phonon_band_dos", (PHONON_BAND_DOS_SUMMARY_SCHEMA_VERSION,)),
        ArtifactProjectorContract("structure.volumetric_data", "volumetric_field_json", "phase10j.volumetric", (VOLUMETRIC_FIELD_SCHEMA_VERSION,)),
    )
})
SUPPORTED_ARTIFACT_TYPES = frozenset(artifact_type for _, artifact_type in ARTIFACT_PROJECTOR_CONTRACTS)
FORBIDDEN_CONCLUSIONS = (
    "material is stable",
    "material is unstable",
    "phase confirmed",
    "structure correct",
    "structure is correct",
    "production-ready",
    "production ready",
    "generalizes",
    "causal",
    "bader charge",
    "charge transfer",
    "industrial value",
    "best material",
    "chemical bond",
)
_NUMBER = re.compile(r"(?<![A-Za-z0-9_])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][-+]?\d+)?%?")
_PATH_OR_URL = re.compile(r"(?:https?://|file://|javascript:|[A-Za-z]:\\|(?:^|\s)/(?:home|tmp|var|etc)/)", re.IGNORECASE)
_PROMPT_INJECTION = re.compile(
    r"(?:ignore\s+(?:all\s+)?previous\s+instructions|call\s+another\s+tool|read\s+secrets?|"
    r"open\s+(?:a\s+)?file|fetch\s+(?:https?|external)|system\s+prompt|developer\s+message)",
    re.IGNORECASE,
)
_CREDENTIAL_SHAPED = re.compile(
    r"(?:api[_-]?key|access[_-]?token|authorization|bearer|password|secret)\s*[:=]\s*\S+",
    re.IGNORECASE,
)
_CHEMICAL_FORMULA = re.compile(r"^(?:[A-Z][a-z]?(?:\d+(?:\.\d+)?)?)+(?:[+-]\d*)?$")


class InterpretationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class InterpretationSource:
    project_id: str
    dataset_id: str
    dataset_version: str
    profile_id: str | None
    profile_semantic_hash: str | None
    intent_id: str | None
    intent_hash: str | None
    resolution_id: str | None
    resolution_hash: str | None
    decision_id: str | None
    decision_hash: str | None
    plan_id: str
    plan_hash: str
    plan_schema_version: str
    graph_hash: str | None
    job_id: str
    job_status: str
    execution_outcome: str
    failed_step_count: int
    blocked_step_count: int


@dataclass(frozen=True)
class ArtifactProjectionInput:
    artifact: Mapping[str, Any]
    payload: Any
    tool_call: Mapping[str, Any]
    lineage: Mapping[str, Any] | None
    raw_checksum: str
    raw_size_bytes: int


@dataclass(frozen=True)
class InterpretationResult:
    outcome: InterpretationOutcome
    bundle: ScientificEvidenceBundle | None
    interpretation: GroundedScientificInterpretation | None
    execution_record: InterpretationExecutionRecord | None
    diagnostics: tuple[str, ...] = ()


class _StrictProposalModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProviderClaimProposal(_StrictProposalModel):
    claimType: ClaimType
    semanticPredicate: ClaimPredicate
    subjectEvidenceIds: list[str] = Field(min_length=1, max_length=8)
    supportingEvidenceIds: list[str] = Field(min_length=1, max_length=8)
    limitingEvidenceIds: list[str] = Field(default_factory=list, max_length=8)
    contradictingEvidenceIds: list[str] = Field(default_factory=list, max_length=8)
    qualifiers: list[str] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def validate_refs(self) -> "ProviderClaimProposal":
        for values in (self.subjectEvidenceIds, self.supportingEvidenceIds, self.limitingEvidenceIds, self.contradictingEvidenceIds):
            if values != sorted(set(values)):
                raise ValueError("Provider evidence references must be unique and sorted.")
        return self


class ProviderInterpretationProposal(_StrictProposalModel):
    schemaVersion: str = Field(pattern=r"^1\.0$")
    claims: list[ProviderClaimProposal] = Field(default_factory=list, max_length=32)
    recommendations: list[dict[str, Any]] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def reject_unstructured_recommendations(self) -> "ProviderInterpretationProposal":
        if self.recommendations:
            raise ValueError("Provider-created recommendations are not accepted in Phase 10L-4.")
        return self


def build_scientific_evidence_bundle(
    source: InterpretationSource,
    artifacts: list[ArtifactProjectionInput],
    *,
    unsupported_artifact_count: int = 0,
) -> ScientificEvidenceBundle:
    if source.job_status not in TERMINAL_JOB_STATES:
        raise InterpretationError("SOURCE_NOT_TERMINAL", "Interpretation requires a terminal job.")
    if (
        unsupported_artifact_count < 0
        or len(artifacts) > 16
        or unsupported_artifact_count > INTERPRETATION_MAX_UNSUPPORTED_ARTIFACTS
    ):
        raise InterpretationError("EVIDENCE_CAP_EXCEEDED", "Source artifact count exceeds 16.")
    if not re.fullmatch(r"[0-9a-f]{64}", source.plan_hash):
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Plan hash is invalid.")

    items: list[ScientificEvidenceItem] = []
    supported_ids: list[str] = []
    projector_versions: dict[str, str] = {}
    unsupported = unsupported_artifact_count
    bundle_warnings: set[str] = set()
    for candidate in sorted(artifacts, key=lambda value: _artifact_id(value.artifact)):
        _validate_source_artifact(source, candidate)
        projected = project_artifact(source, candidate)
        if not projected:
            unsupported += 1
            if unsupported > INTERPRETATION_MAX_UNSUPPORTED_ARTIFACTS:
                raise InterpretationError(
                    "EVIDENCE_CAP_EXCEEDED",
                    "Unsupported artifact count exceeds the interpretation evidence cap.",
                )
            continue
        artifact_id = _artifact_id(candidate.artifact)
        supported_ids.append(artifact_id)
        projector_versions[artifact_id] = PROJECTOR_VERSION
        items.extend(projected)
        for item in projected:
            bundle_warnings.update(item.warnings)
    if len(items) > 256:
        raise InterpretationError("EVIDENCE_CAP_EXCEEDED", "Evidence item count exceeds 256.")

    partial = source.execution_outcome == "PARTIAL_RESULTS" or source.job_status == "partial_success"
    limitations: list[str] = []
    if partial:
        limitations.append(
            f"Execution was partial: {source.failed_step_count} failed step(s) and {source.blocked_step_count} blocked step(s); only successful artifacts are interpreted."
        )
    if unsupported:
        limitations.append(f"{unsupported} artifact(s) have no approved structured evidence projector.")
    completeness = BundleCompleteness.partial if partial or unsupported else BundleCompleteness.complete
    if not supported_ids:
        completeness = BundleCompleteness.unsupported
    payload = {
        "schemaVersion": "1.0",
        "bundleId": "",
        "bundleHash": "0" * 64,
        "projectId": source.project_id,
        "datasetId": source.dataset_id,
        "datasetVersion": source.dataset_version,
        "profileId": source.profile_id,
        "profileSemanticHash": source.profile_semantic_hash,
        "intentId": source.intent_id,
        "intentHash": source.intent_hash,
        "eligibilityResolutionId": source.resolution_id,
        "eligibilityResolutionHash": source.resolution_hash,
        "selectionDecisionId": source.decision_id,
        "selectionDecisionHash": source.decision_hash,
        "planId": source.plan_id,
        "planHash": source.plan_hash,
        "planSchemaVersion": source.plan_schema_version,
        "graphHash": source.graph_hash,
        "jobId": source.job_id,
        "sourceJobTerminalState": source.job_status,
        "executionOutcome": source.execution_outcome,
        "allSucceeded": source.execution_outcome in {"ALL_SUCCEEDED", "LEGACY_TERMINAL"} and source.job_status == "completed",
        "partialResults": partial,
        "supportedArtifactCount": len(supported_ids),
        "unsupportedArtifactCount": unsupported,
        "failedStepCount": source.failed_step_count,
        "blockedStepCount": source.blocked_step_count,
        "bundleCompleteness": completeness.value,
        "bundleWarnings": sorted(bundle_warnings),
        "bundleLimitations": limitations,
        "sourceArtifactIds": sorted(supported_ids),
        "projectorVersions": dict(sorted(projector_versions.items())),
        "evidenceItems": sorted((item.model_dump(mode="json") for item in items), key=lambda item: item["evidenceItemId"]),
    }
    semantic = {key: value for key, value in payload.items() if key not in {"bundleId", "bundleHash"}}
    payload["bundleHash"] = interpretation_semantic_hash(semantic)
    payload["bundleId"] = deterministic_interpretation_id("bundle", payload["bundleHash"])
    try:
        return ScientificEvidenceBundle.model_validate(payload)
    except ValidationError as exc:
        if "serialized byte cap" in str(exc):
            raise InterpretationError("EVIDENCE_CAP_EXCEEDED", "ScientificEvidenceBundle exceeds 262,144 bytes.") from exc
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Projected evidence does not satisfy the bundle contract.") from exc


def project_artifact(source: InterpretationSource, candidate: ArtifactProjectionInput) -> list[ScientificEvidenceItem]:
    artifact_type = str(candidate.artifact.get("type") or "")
    payload = candidate.payload
    tool_id = str(candidate.tool_call.get("toolId") or candidate.tool_call.get("tool_id") or "")
    if (tool_id, artifact_type) not in ARTIFACT_PROJECTOR_CONTRACTS or not isinstance(payload, dict):
        return []
    if artifact_type == "table_json" and tool_id == "table.numeric_summary":
        return _project_numeric_summary(source, candidate)
    if artifact_type == "metrics_json" and tool_id == "ml.basic_metrics":
        return _project_ml_metrics(source, candidate)
    if artifact_type == "structure_json" and tool_id == "structure.summary":
        return _project_structure_summary(source, candidate)
    if artifact_type in {"phonon_band_json", "phonon_dos_json", "phonon_band_dos_json", "phonon_summary_json"} and tool_id in {"phonon.band", "phonon.dos", "phonon.band_dos"}:
        return _project_phonon_summary(source, candidate)
    if artifact_type == "volumetric_field_json" and tool_id == "structure.volumetric_data":
        return _project_volumetric_field(source, candidate)
    return []


def deterministic_interpret(
    bundle: ScientificEvidenceBundle,
    *,
    idempotency_key_hash: str | None = None,
) -> InterpretationResult:
    started = time.perf_counter()
    if not bundle.evidenceItems:
        return _terminal_result(
            bundle,
            InterpretationMode.deterministic,
            InterpretationOutcome.no_supported_evidence,
            started,
            idempotency_key_hash=idempotency_key_hash,
        )
    claims: list[ScientificClaim] = []
    seen: set[tuple[str, str, str]] = set()
    ordered = sorted(bundle.evidenceItems, key=lambda item: (item.evidenceKind.value, item.semanticRole, item.subjectId, item.evidenceItemId))
    for item in ordered:
        if len(claims) >= 32:
            raise InterpretationError("EVIDENCE_CAP_EXCEEDED", "Claim count exceeds 32.")
        predicate, claim_type = _claim_semantics(item)
        dedupe = (predicate.value, item.subjectId, item.displayValue)
        if dedupe in seen:
            continue
        seen.add(dedupe)
        confidence = ClaimConfidence.limited if bundle.partialResults or item.limitations else ClaimConfidence.direct
        text = _render_item_claim(item, predicate)
        claims.append(_make_claim(item, claim_type, predicate, text, confidence, len(claims), limiting=[]))
    return _finalize_interpretation(
        bundle,
        mode=InterpretationMode.deterministic,
        provider="deterministic",
        provider_version=DETERMINISTIC_INTERPRETER_VERSION,
        claims=claims,
        repair_count=0,
        started=started,
        prompt_projection_hash=None,
        response_hash=None,
        idempotency_key_hash=idempotency_key_hash,
    )


def strict_provider_interpret(
    bundle: ScientificEvidenceBundle,
    provider: Callable[[dict[str, Any], bool], str],
    *,
    provider_identity: str = "openai_compatible",
    provider_model: str | None = None,
    provider_config_hash: str | None = None,
    idempotency_key_hash: str | None = None,
) -> InterpretationResult:
    started = time.perf_counter()
    projection = provider_safe_projection(bundle)
    projection_hash = interpretation_semantic_hash(projection)
    initial_hash: str | None = None
    repaired_hash: str | None = None
    diagnostics: list[str] = []
    try:
        raw = provider(projection, False)
    except Exception as exc:
        diagnostics.append(f"STRICT_PROVIDER_TRANSPORT_FAILED:{type(exc).__name__}")
        record = _execution_record(
            bundle,
            mode=InterpretationMode.strict_provider,
            provider=provider_identity,
            provider_version=STRICT_PROVIDER_CONTRACT_VERSION,
            provider_model=provider_model,
            provider_config_hash=provider_config_hash,
            idempotency_key_hash=idempotency_key_hash,
            prompt_projection_hash=projection_hash,
            initial_response_hash=None,
            repaired_response_hash=None,
            response_hash=None,
            repair_count=0,
            outcome=InterpretationOutcome.provider_failed,
            diagnostics=diagnostics,
            claim_count=0,
            started=started,
        )
        return InterpretationResult(InterpretationOutcome.provider_failed, bundle, None, record, tuple(diagnostics))
    initial_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    try:
        proposal = ProviderInterpretationProposal.model_validate(strict_interpretation_json_loads(raw))
    except Exception as exc:
        diagnostics.append(f"STRICT_PROVIDER_PARSE_FAILED:{type(exc).__name__}")
        repair_projection = {
            **projection,
            "invalidResponseHash": initial_hash,
            "diagnostics": diagnostics,
            "repairBudgetRemaining": 1,
        }
        try:
            repaired_raw = provider(repair_projection, True)
            repaired_hash = hashlib.sha256(repaired_raw.encode("utf-8")).hexdigest()
            proposal = ProviderInterpretationProposal.model_validate(strict_interpretation_json_loads(repaired_raw))
        except Exception as repair_exc:
            diagnostics.append(f"REPAIR_FAILED:{type(repair_exc).__name__}")
            record = _execution_record(
                bundle,
                mode=InterpretationMode.strict_provider,
                provider=provider_identity,
                provider_version=STRICT_PROVIDER_CONTRACT_VERSION,
                provider_model=provider_model,
                provider_config_hash=provider_config_hash,
                idempotency_key_hash=idempotency_key_hash,
                prompt_projection_hash=projection_hash,
                initial_response_hash=initial_hash,
                repaired_response_hash=repaired_hash,
                response_hash=repaired_hash or initial_hash,
                repair_count=1,
                outcome=InterpretationOutcome.validation_failed,
                diagnostics=diagnostics,
                claim_count=0,
                started=started,
            )
            return InterpretationResult(InterpretationOutcome.validation_failed, bundle, None, record, tuple(diagnostics))
        repair_count_start = 1
    else:
        repair_count_start = 0
    for repair_count in range(repair_count_start, 2):
        try:
            claims = _claims_from_proposal(bundle, proposal)
            return _finalize_interpretation(
                bundle,
                mode=InterpretationMode.strict_provider,
                provider=provider_identity,
                provider_version=STRICT_PROVIDER_CONTRACT_VERSION,
                provider_model=provider_model,
                provider_config_hash=provider_config_hash,
                idempotency_key_hash=idempotency_key_hash,
                claims=claims,
                repair_count=repair_count,
                started=started,
                prompt_projection_hash=projection_hash,
                initial_response_hash=initial_hash,
                repaired_response_hash=repaired_hash,
                response_hash=repaired_hash or initial_hash,
            )
        except InterpretationError as exc:
            if repair_count == 1:
                diagnostics.append(exc.code)
                record = _execution_record(
                    bundle,
                    mode=InterpretationMode.strict_provider,
                    provider=provider_identity,
                    provider_version=STRICT_PROVIDER_CONTRACT_VERSION,
                    provider_model=provider_model,
                    provider_config_hash=provider_config_hash,
                    idempotency_key_hash=idempotency_key_hash,
                    prompt_projection_hash=projection_hash,
                    initial_response_hash=initial_hash,
                    repaired_response_hash=repaired_hash,
                    response_hash=repaired_hash or initial_hash,
                    repair_count=1,
                    outcome=InterpretationOutcome.validation_failed,
                    diagnostics=diagnostics,
                    claim_count=0,
                    started=started,
                )
                return InterpretationResult(InterpretationOutcome.validation_failed, bundle, None, record, tuple(diagnostics))
            diagnostics.append(exc.code)
            repair_projection = {**projection, "invalidProposal": proposal.model_dump(mode="json"), "diagnostics": [exc.code], "repairBudgetRemaining": 1}
            try:
                repaired_raw = provider(repair_projection, True)
                repaired_hash = hashlib.sha256(repaired_raw.encode("utf-8")).hexdigest()
                proposal = ProviderInterpretationProposal.model_validate(strict_interpretation_json_loads(repaired_raw))
            except Exception as repair_exc:
                diagnostics.append(f"REPAIR_FAILED:{type(repair_exc).__name__}")
                record = _execution_record(
                    bundle,
                    mode=InterpretationMode.strict_provider,
                    provider=provider_identity,
                    provider_version=STRICT_PROVIDER_CONTRACT_VERSION,
                    provider_model=provider_model,
                    provider_config_hash=provider_config_hash,
                    idempotency_key_hash=idempotency_key_hash,
                    prompt_projection_hash=projection_hash,
                    initial_response_hash=initial_hash,
                    repaired_response_hash=repaired_hash,
                    response_hash=repaired_hash,
                    repair_count=1,
                    outcome=InterpretationOutcome.validation_failed,
                    diagnostics=diagnostics,
                    claim_count=0,
                    started=started,
                )
                return InterpretationResult(InterpretationOutcome.validation_failed, bundle, None, record, tuple(diagnostics))
    raise AssertionError("interpretation repair loop must terminate")


def provider_safe_projection(bundle: ScientificEvidenceBundle) -> dict[str, Any]:
    items = [
        {
            "evidenceItemId": item.evidenceItemId,
            "semanticRole": item.semanticRole,
            "evidenceKind": item.evidenceKind.value,
            "subjectId": item.subjectId,
            "valueKind": item.valueKind,
            "normalizedValue": item.normalizedValue.model_dump(mode="json"),
            "displayValue": item.displayValue,
            "unit": item.unit,
            "referenceConvention": item.referenceConvention,
            "warnings": item.warnings,
            "limitations": item.limitations,
        }
        for item in bundle.evidenceItems
        if item.providerSafe and _provider_safe_evidence_item(item)
    ]
    projection = {
        "schemaVersion": "1.0",
        "bundleId": bundle.bundleId,
        "bundleHash": bundle.bundleHash,
        "partialResults": bundle.partialResults,
        "bundleWarnings": bundle.bundleWarnings,
        "bundleLimitations": bundle.bundleLimitations,
        "allowedClaimTypes": [item.value for item in ClaimType],
        "allowedPredicates": [item.value for item in ClaimPredicate],
        "evidenceItems": items,
        "providerVisibleEvidenceIds": sorted(item["evidenceItemId"] for item in items),
        "rules": {
            "rawArtifactsAvailable": False,
            "pathsOrUrlsAvailable": False,
            "toolExecutionAuthorized": False,
            "planMutationAuthorized": False,
            "recommendationsExecutable": False,
            "freeTextClaimsAccepted": False,
        },
    }
    raw = json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(raw) > 262_144:
        raise InterpretationError("EVIDENCE_CAP_EXCEEDED", "Provider-visible evidence exceeds 262144 bytes.")
    if _PATH_OR_URL.search(raw.decode("utf-8")):
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Provider projection contains a path or URL.")
    return projection


def no_supported_evidence_result(
    bundle: ScientificEvidenceBundle,
    *,
    mode: InterpretationMode,
    provider_identity: str,
    provider_model: str | None = None,
    provider_config_hash: str | None = None,
    idempotency_key_hash: str | None = None,
) -> InterpretationResult:
    started = time.perf_counter()
    record = _execution_record(
        bundle,
        mode=mode,
        provider=provider_identity,
        provider_version=DETERMINISTIC_INTERPRETER_VERSION if mode == InterpretationMode.deterministic else STRICT_PROVIDER_CONTRACT_VERSION,
        provider_model=provider_model,
        provider_config_hash=provider_config_hash,
        idempotency_key_hash=idempotency_key_hash,
        prompt_projection_hash=None,
        initial_response_hash=None,
        repaired_response_hash=None,
        response_hash=None,
        repair_count=0,
        outcome=InterpretationOutcome.no_supported_evidence,
        diagnostics=["NO_APPROVED_STRUCTURED_EVIDENCE"],
        claim_count=0,
        started=started,
    )
    return InterpretationResult(
        InterpretationOutcome.no_supported_evidence,
        bundle,
        None,
        record,
        ("NO_APPROVED_STRUCTURED_EVIDENCE",),
    )


def validate_grounded_interpretation(
    bundle: ScientificEvidenceBundle,
    interpretation: GroundedScientificInterpretation,
) -> None:
    if interpretation.sourceBundleId != bundle.bundleId or interpretation.sourceBundleHash != bundle.bundleHash:
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Interpretation references a different evidence bundle.")
    evidence = {item.evidenceItemId: item for item in bundle.evidenceItems}
    if bundle.partialResults and not interpretation.globalLimitations:
        raise InterpretationError("PARTIAL_LIMITATION_REQUIRED", "Partial results require a global limitation.")
    for claim in interpretation.claims:
        refs = set(claim.subjectEvidenceIds + claim.supportingEvidenceIds + claim.limitingEvidenceIds + claim.contradictingEvidenceIds)
        if not refs or not refs.issubset(evidence):
            raise InterpretationError("INVENTED_EVIDENCE_ID", "Claim references evidence outside the current bundle.")
        subjects = {evidence[item].subjectId for item in claim.subjectEvidenceIds}
        if claim.semanticPredicate == ClaimPredicate.differs_from:
            _validate_comparison_claim(claim, evidence)
        elif len(subjects) != 1:
            raise InterpretationError("ENTITY_SCOPE_MISMATCH", "Claim subject identities are inconsistent.")
        _validate_claim_semantics(claim, evidence, bundle=bundle)
        _validate_claim_text(claim, [evidence[item] for item in refs])
        if claim.semanticPredicate == ClaimPredicate.exceeds_declared_threshold and "threshold" not in claim.structuredPayload:
            raise InterpretationError("INVENTED_THRESHOLD", "Threshold predicates require exact threshold evidence.")
        if bundle.partialResults and claim.confidenceClass != ClaimConfidence.limited:
            raise InterpretationError("PARTIAL_CONFIDENCE_INVALID", "Partial result claims must remain LIMITED.")


def _project_numeric_summary(source: InterpretationSource, candidate: ArtifactProjectionInput) -> list[ScientificEvidenceItem]:
    payload = candidate.payload
    required = {"rowCount", "columns", "numericColumns", "categoricalColumns"}
    if not isinstance(payload, dict) or set(payload) != required or not isinstance(payload["rowCount"], int) or isinstance(payload["rowCount"], bool) or payload["rowCount"] < 0:
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Numeric summary contract is invalid.")
    if not isinstance(payload["columns"], list) or not isinstance(payload["numericColumns"], dict) or not isinstance(payload["categoricalColumns"], dict):
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Numeric summary collections are invalid.")
    columns: dict[str, dict[str, Any]] = {}
    for column in payload["columns"]:
        if not isinstance(column, dict) or set(column) != {"name", "dtype", "missingCount", "nonNullCount"}:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Numeric summary column metadata is invalid.")
        name = column.get("name")
        missing = column.get("missingCount")
        non_null = column.get("nonNullCount")
        if (
            not isinstance(name, str) or not name or name in columns
            or not isinstance(column.get("dtype"), str) or not column["dtype"]
            or not _nonnegative_int(missing) or not _nonnegative_int(non_null)
            or missing + non_null != payload["rowCount"]
        ):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Numeric summary column counts are inconsistent.")
        columns[name] = column
    if not set(payload["numericColumns"]).issubset(columns) or not set(payload["categoricalColumns"]).issubset(columns):
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Summary fields reference unknown columns.")
    items = [_item(source, candidate, "dataset.row_count", EvidenceKind.count, "dataset", "count", payload["rowCount"], field="rowCount")]
    for column in sorted(payload["numericColumns"]):
        stats = payload["numericColumns"][column]
        if not isinstance(stats, dict) or set(stats) != {"count", "mean", "std", "min", "median", "max"}:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Numeric column summary is invalid.")
        if not _nonnegative_int(stats["count"]) or stats["count"] > columns[column]["nonNullCount"]:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Numeric column count is invalid.")
        values = [stats[key] for key in ("mean", "std", "min", "median", "max")]
        if stats["count"] == 0:
            if any(value is not None for value in values):
                raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Empty numeric summaries cannot contain statistics.")
        elif any(not _finite(value) for value in values):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Numeric statistics must be finite.")
        if stats["std"] is not None and stats["std"] < 0:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Numeric standard deviation cannot be negative.")
        if stats["min"] is not None and not (stats["min"] <= stats["median"] <= stats["max"] and stats["min"] <= stats["mean"] <= stats["max"]):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Numeric range statistics are inconsistent.")
        if stats["min"] is not None and stats["max"] is not None:
            items.append(_item(source, candidate, "property.range", EvidenceKind.range, f"column:{column}", "numeric_range", None, minimum=stats["min"], maximum=stats["max"], field=f"numericColumns.{column}.range", entity=column))
    for column, stats in payload["categoricalColumns"].items():
        if not isinstance(stats, dict) or set(stats) != {"count", "unique", "valueCounts"}:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Categorical column summary is invalid.")
        if not _nonnegative_int(stats["count"]) or not _nonnegative_int(stats["unique"]) or stats["count"] > columns[column]["nonNullCount"] or stats["unique"] > stats["count"]:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Categorical summary counts are inconsistent.")
        if not isinstance(stats["valueCounts"], dict) or any(not isinstance(key, str) or not _nonnegative_int(value) for key, value in stats["valueCounts"].items()):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Categorical value counts are invalid.")
        if sum(stats["valueCounts"].values()) > stats["count"]:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Categorical value counts exceed the observed count.")
    missing = sum(column["missingCount"] for column in payload["columns"])
    items.append(_item(source, candidate, "dataset.missing_count", EvidenceKind.count, "dataset", "count", missing, field="columns.missingCount"))
    return items


def _project_ml_metrics(source: InterpretationSource, candidate: ArtifactProjectionInput) -> list[ScientificEvidenceItem]:
    payload = candidate.payload
    if not isinstance(payload, dict) or set(payload) != {"metrics", "targetColumn", "predictionColumn"} or not isinstance(payload["metrics"], dict):
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "ML metrics contract is invalid.")
    metrics = payload["metrics"]
    metric_fields = (
        ("n", "n", EvidenceKind.count),
        ("mae", "mae", EvidenceKind.scalar),
        ("rmse", "rmse", EvidenceKind.scalar),
        ("r2", "r2", EvidenceKind.scalar),
        ("mean_error", "meanError", EvidenceKind.scalar),
        ("max_abs_error", "maxAbsError", EvidenceKind.scalar),
    )
    required = {payload_key for _, payload_key, _ in metric_fields}
    if (
        set(metrics) != required
        or not _nonnegative_int(metrics.get("n"))
        or metrics["n"] == 0
        or any(not _finite(metrics[key]) for key in required - {"n"})
    ):
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "ML metrics contain missing or non-finite values.")
    if (
        metrics["mae"] < 0
        or metrics["rmse"] < 0
        or metrics["maxAbsError"] < 0
        or metrics["rmse"] + 1e-12 < metrics["mae"]
        or metrics["maxAbsError"] + 1e-12 < metrics["rmse"]
        or abs(metrics["meanError"]) > metrics["maxAbsError"] + 1e-12
    ):
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "ML error metrics are inconsistent.")
    if not _safe_semantic_name(payload.get("targetColumn")) or not _safe_semantic_name(payload.get("predictionColumn")) or payload["targetColumn"] == payload["predictionColumn"]:
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "ML target and prediction identities are invalid.")
    subject = f"target:{payload['targetColumn']}"
    return [
        _item(
            source,
            candidate,
            f"ml.{semantic_key}",
            evidence_kind,
            subject,
            "count" if payload_key == "n" else "metric",
            metrics[payload_key],
            field=f"metrics.{payload_key}",
            entity=str(payload["targetColumn"]),
        )
        for semantic_key, payload_key, evidence_kind in metric_fields
    ]


def _project_structure_summary(source: InterpretationSource, candidate: ArtifactProjectionInput) -> list[ScientificEvidenceItem]:
    payload = candidate.payload
    if not isinstance(payload, dict) or set(payload) != {"artifactType", "structureCount", "structures", "warnings"} or payload.get("artifactType") != "structure.summary":
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Structure summary contract is invalid.")
    if not _nonnegative_int(payload.get("structureCount")) or not isinstance(payload.get("structures"), list) or payload["structureCount"] != len(payload["structures"]):
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Structure summary counts are inconsistent.")
    items = [_item(source, candidate, "structure.count", EvidenceKind.count, "dataset", "count", payload["structureCount"], field="structureCount")]
    seen_structure_ids: set[str] = set()
    for record in payload["structures"]:
        if not isinstance(record, dict) or not {"structureId", "numSites", "reducedFormula", "lattice"}.issubset(record):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Structure record is invalid.")
        structure_id = record.get("structureId")
        if not _safe_semantic_name(structure_id) or structure_id in seen_structure_ids or not _nonnegative_int(record.get("numSites")):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Structure identity or site count is invalid.")
        seen_structure_ids.add(structure_id)
        if (
            not isinstance(record.get("reducedFormula"), str)
            or not _CHEMICAL_FORMULA.fullmatch(record["reducedFormula"])
            or not isinstance(record.get("lattice"), dict)
        ):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Structure semantic fields are invalid.")
        subject = f"structure:{record['structureId']}"
        items.append(_item(source, candidate, "structure.site_count", EvidenceKind.count, subject, "count", record["numSites"], field="structures.numSites", entity=str(record["structureId"])))
        items.append(_item(source, candidate, "structure.formula", EvidenceKind.category, subject, "formula", str(record["reducedFormula"]), field="structures.reducedFormula", entity=str(record["structureId"])))
        lattice = record["lattice"]
        if any(not _finite(lattice.get(key)) or lattice[key] <= 0 for key in ("a", "b", "c", "volume")):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Structure lattice lengths and volume must be positive.")
        if any(not _finite(lattice.get(key)) or not 0 < lattice[key] < 180 for key in ("alpha", "beta", "gamma")):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Structure lattice angles are invalid.")
        for key, unit in (("a", "angstrom"), ("b", "angstrom"), ("c", "angstrom"), ("volume", "angstrom^3")):
            if key in lattice and _finite(lattice[key]):
                items.append(_item(source, candidate, f"structure.lattice.{key}", EvidenceKind.scalar, subject, "lattice_parameter", lattice[key], unit=unit, field=f"structures.lattice.{key}", entity=str(record["structureId"])))
    return items


def _project_phonon_summary(source: InterpretationSource, candidate: ArtifactProjectionInput) -> list[ScientificEvidenceItem]:
    payload = candidate.payload
    version = payload.get("schema_version")
    if version == PHONON_BAND_SCHEMA_VERSION:
        if not validate_phonon_band(payload, raw_size_bytes=candidate.raw_size_bytes).valid:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Phonon band contract is invalid.")
        subject = f"structure:{payload['structure_identity']}"
        return [
            _item(source, candidate, "phonon.atom_count", EvidenceKind.count, subject, "count", payload["atom_count"], field="atom_count", entity=payload["structure_identity"]),
            _item(source, candidate, "phonon.frequency_unit", EvidenceKind.category, subject, "unit", payload["frequency_unit"], field="frequency_unit", entity=payload["structure_identity"]),
            _item(source, candidate, "phonon.reciprocal_convention", EvidenceKind.category, subject, "reference", payload["reciprocal_convention"], field="reciprocal_convention", entity=payload["structure_identity"]),
        ]
    if version == PHONON_DOS_SCHEMA_VERSION:
        if not validate_phonon_dos(payload, raw_size_bytes=candidate.raw_size_bytes).valid:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Phonon DOS contract is invalid.")
        subject = f"structure:{payload['structure_identity']}"
        integration = payload["integration"]
        return [
            _item(source, candidate, "phonon.dos_integral", EvidenceKind.scalar, subject, "mode_count", integration["observed_integral"], field="integration.observed_integral", entity=payload["structure_identity"]),
            _item(source, candidate, "phonon.dos_integration_status", EvidenceKind.category, subject, "category", integration["status"], field="integration.status", entity=payload["structure_identity"]),
            _item(source, candidate, "phonon.dos_density_unit", EvidenceKind.category, subject, "unit", payload["density_unit"], field="density_unit", entity=payload["structure_identity"]),
        ]
    if version == PHONON_BAND_DOS_SCHEMA_VERSION:
        if not validate_phonon_band_dos(payload).valid:
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Combined phonon band-DOS contract is invalid.")
        subject = f"structure:{payload['structure_identity']}"
        axis = payload["frequency_axis"]
        return [
            _item(source, candidate, "phonon.frequency_range", EvidenceKind.range, subject, "frequency_range", None, minimum=axis["minimum"], maximum=axis["maximum"], unit=axis["unit"], field="frequency_axis.range", entity=payload["structure_identity"]),
            _item(source, candidate, "phonon.compatibility_status", EvidenceKind.category, subject, "category", payload["compatibility"]["status"], field="compatibility.status", entity=payload["structure_identity"]),
        ]
    validators = {
        PHONON_SUMMARY_SCHEMA_VERSION: validate_phonon_summary,
        PHONON_DOS_SUMMARY_SCHEMA_VERSION: validate_phonon_dos_summary,
        PHONON_BAND_DOS_SUMMARY_SCHEMA_VERSION: validate_phonon_band_dos_summary,
    }
    validator = validators.get(version)
    if validator is None or not validator(payload).valid:
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Phonon summary contract is invalid or unsupported.")
    subject = f"structure:{payload['structure_identity']}"
    minimum = payload.get("frequency_min")
    maximum = payload.get("frequency_max")
    if minimum is None or maximum is None:
        domain = payload.get("frequency_domain") or {}
        union = domain.get("union") if isinstance(domain, dict) else None
        minimum, maximum = union if isinstance(union, list) and len(union) == 2 else (None, None)
    items: list[ScientificEvidenceItem] = []
    if _finite(minimum) and _finite(maximum):
        items.append(_item(source, candidate, "phonon.frequency_range", EvidenceKind.range, subject, "frequency_range", None, minimum=minimum, maximum=maximum, unit="terahertz", field="frequency_range", entity=payload["structure_identity"]))
    for key in ("atom_count", "branch_count", "qpoint_count", "segment_count", "imaginary_mode_count", "near_zero_mode_count", "projection_count"):
        if isinstance(payload.get(key), int):
            role = f"phonon.{key}"
            items.append(_item(source, candidate, role, EvidenceKind.count, subject, "count", payload[key], field=key, entity=payload["structure_identity"]))
    status = payload.get("compatibility_status") or payload.get("normalization_status")
    if isinstance(status, str):
        items.append(_item(source, candidate, "phonon.status", EvidenceKind.category, subject, "category", status, field="status", entity=payload["structure_identity"]))
    return items


def _project_volumetric_field(source: InterpretationSource, candidate: ArtifactProjectionInput) -> list[ScientificEvidenceItem]:
    payload = candidate.payload
    if payload.get("schema_version") != VOLUMETRIC_FIELD_SCHEMA_VERSION or not validate_volumetric_field(payload).valid:
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Volumetric field contract is invalid.")
    subject = f"field:{payload['field_id']}"
    unit = payload["unit"]["canonical_unit"]
    items = [_item(source, candidate, "volumetric.quantity", EvidenceKind.category, subject, "quantity", payload["quantity"], field="quantity", entity=payload["field_id"])]
    for index, stats in enumerate(payload["statistics"]["stored_components"]):
        items.append(_item(source, candidate, "volumetric.scalar_range", EvidenceKind.range, subject, "scalar_range", None, minimum=stats["minimum"], maximum=stats["maximum"], unit=unit, field=f"statistics.component_{index}.range", entity=payload["field_id"]))
    reference = payload.get("potential_reference")
    if isinstance(reference, dict):
        items.append(_item(source, candidate, "volumetric.reference", EvidenceKind.category, subject, "reference", reference["kind"], field="potential_reference.kind", entity=payload["field_id"]))
    return items


def _item(
    source: InterpretationSource,
    candidate: ArtifactProjectionInput,
    semantic_role: str,
    kind: EvidenceKind,
    subject: str,
    value_kind: str,
    scalar: Any,
    *,
    minimum: Any = None,
    maximum: Any = None,
    unit: str | None = None,
    field: str,
    entity: str | None = None,
) -> ScientificEvidenceItem:
    artifact = candidate.artifact
    lineage = candidate.lineage or {}
    checksum = str(artifact.get("sha256") or artifact.get("contentHash") or "")
    contract = str(candidate.payload.get("schema_version") or lineage.get("artifactContractVersion") or _fallback_contract(candidate))
    normalized = EvidenceValue(scalar=scalar, minimum=minimum, maximum=maximum)
    display = _display_value(normalized, unit)
    reference = candidate.payload.get("reference_convention") or candidate.payload.get("normalization")
    reference_convention = reference if _safe_semantic_name(reference) else "artifact_contract"
    payload = {
        "schemaVersion": "1.0",
        "evidenceItemId": "",
        "semanticRole": semantic_role,
        "evidenceKind": kind.value,
        "subjectId": subject,
        "valueKind": value_kind,
        "normalizedValue": normalized.model_dump(mode="json"),
        "displayValue": display,
        "unit": unit,
        "unitAuthority": "artifact_contract" if unit else None,
        "referenceConvention": reference_convention,
        "sourceArtifactId": _artifact_id(artifact),
        "sourceArtifactChecksum": checksum,
        "artifactContract": _contract_family(candidate),
        "artifactContractVersion": contract,
        "sourceToolId": str(candidate.tool_call.get("toolId") or candidate.tool_call.get("tool_id")),
        "sourceToolVersion": str(lineage.get("producerToolVersion") or "0.1.0"),
        "producerStepId": str(candidate.tool_call.get("stepId") or lineage.get("producerStepId")),
        "producerToolCallId": str(candidate.tool_call.get("id") or lineage.get("producerToolCallId")),
        "fieldLocator": {"fieldId": field.replace("[", ".").replace("]", ""), "semanticKey": semantic_role, "entityId": entity},
        "datasetId": source.dataset_id,
        "datasetVersion": source.dataset_version,
        "resourceId": entity,
        "warnings": _safe_messages(candidate.payload.get("warnings")),
        "limitations": [],
        "projectorVersion": PROJECTOR_VERSION,
        "providerSafe": False,
    }
    payload["providerSafe"] = _provider_safe_value(
        {
            "semanticRole": semantic_role,
            "subjectId": subject,
            "valueKind": value_kind,
            "normalizedValue": payload["normalizedValue"],
            "displayValue": display,
            "unit": unit,
            "referenceConvention": reference_convention,
            "resourceId": entity,
            "warnings": payload["warnings"],
            "limitations": payload["limitations"],
        }
    )
    semantic = {key: value for key, value in payload.items() if key != "evidenceItemId"}
    payload["evidenceItemId"] = deterministic_interpretation_id("evidence", interpretation_semantic_hash(semantic))
    return ScientificEvidenceItem.model_validate(payload)


def _make_claim(
    item: ScientificEvidenceItem,
    claim_type: ClaimType,
    predicate: ClaimPredicate,
    text: str,
    confidence: ClaimConfidence,
    order: int,
    *,
    limiting: list[str],
    subject_ids: list[str] | None = None,
    supporting_ids: list[str] | None = None,
    contradicting_ids: list[str] | None = None,
    qualifiers: list[str] | None = None,
    structured_payload: dict[str, bool | int | float | str] | None = None,
    scope: str | None = None,
) -> ScientificClaim:
    payload = {
        "schemaVersion": "1.0",
        "claimId": "",
        "claimType": claim_type.value,
        "subjectEvidenceIds": subject_ids or [item.evidenceItemId],
        "supportingEvidenceIds": supporting_ids or [item.evidenceItemId],
        "limitingEvidenceIds": sorted(limiting),
        "contradictingEvidenceIds": sorted(contradicting_ids or []),
        "semanticPredicate": predicate.value,
        "qualifiers": sorted(set(item.limitations if qualifiers is None else qualifiers)),
        "structuredPayload": structured_payload or {"displayValue": item.displayValue, "subjectId": item.subjectId},
        "renderedText": text,
        "scope": scope or item.subjectId,
        "confidenceClass": confidence.value,
        "groundingStatus": GroundingStatus.grounded.value,
        "displayOrder": order,
    }
    semantic = {key: value for key, value in payload.items() if key not in {"claimId", "displayOrder"}}
    payload["claimId"] = deterministic_interpretation_id("claim", interpretation_semantic_hash(semantic))
    return ScientificClaim.model_validate(payload)


def _claims_from_proposal(bundle: ScientificEvidenceBundle, proposal: ProviderInterpretationProposal) -> list[ScientificClaim]:
    evidence = {item.evidenceItemId: item for item in bundle.evidenceItems}
    claims: list[ScientificClaim] = []
    for index, proposed in enumerate(proposal.claims):
        ids = set(proposed.subjectEvidenceIds + proposed.supportingEvidenceIds + proposed.limitingEvidenceIds + proposed.contradictingEvidenceIds)
        if not ids.issubset(evidence):
            raise InterpretationError("INVENTED_EVIDENCE_ID", "Provider selected an evidence ID outside the projection.")
        subject_items = [evidence[item] for item in proposed.subjectEvidenceIds]
        subject = subject_items[0]
        if proposed.semanticPredicate == ClaimPredicate.differs_from:
            _validate_comparable_evidence(subject_items)
            text = (
                f"{subject_items[0].subjectId} and {subject_items[1].subjectId} report different "
                f"{subject_items[0].semanticRole}: {subject_items[0].displayValue} versus {subject_items[1].displayValue}."
            )
            structured_payload = {
                "leftEvidenceId": subject_items[0].evidenceItemId,
                "rightEvidenceId": subject_items[1].evidenceItemId,
            }
            scope = "comparison"
        else:
            if any(item.subjectId != subject.subjectId for item in subject_items):
                raise InterpretationError("ENTITY_SCOPE_MISMATCH", "Provider combined incompatible subjects.")
            text = _render_item_claim(subject, proposed.semanticPredicate)
            structured_payload = {"displayValue": subject.displayValue, "subjectId": subject.subjectId}
            scope = subject.subjectId
        allowed_qualifiers = set(bundle.bundleWarnings + bundle.bundleLimitations)
        for evidence_id in ids:
            allowed_qualifiers.update(evidence[evidence_id].warnings)
            allowed_qualifiers.update(evidence[evidence_id].limitations)
        if any(qualifier not in allowed_qualifiers for qualifier in proposed.qualifiers):
            raise InterpretationError("UNGROUNDED_QUALIFIER", "Provider qualifier is absent from the evidence bundle.")
        confidence = ClaimConfidence.limited if bundle.partialResults or proposed.limitingEvidenceIds else ClaimConfidence.qualified
        claim = _make_claim(
            subject,
            proposed.claimType,
            proposed.semanticPredicate,
            text,
            confidence,
            index,
            limiting=proposed.limitingEvidenceIds,
            subject_ids=proposed.subjectEvidenceIds,
            supporting_ids=proposed.supportingEvidenceIds,
            contradicting_ids=proposed.contradictingEvidenceIds,
            qualifiers=proposed.qualifiers,
            structured_payload=structured_payload,
            scope=scope,
        )
        _validate_claim_semantics(claim, evidence, bundle=bundle)
        claims.append(claim)
    return claims


def _finalize_interpretation(
    bundle: ScientificEvidenceBundle,
    *,
    mode: InterpretationMode,
    provider: str,
    provider_version: str,
    claims: list[ScientificClaim],
    repair_count: int,
    started: float,
    prompt_projection_hash: str | None,
    response_hash: str | None,
    provider_model: str | None = None,
    provider_config_hash: str | None = None,
    idempotency_key_hash: str | None = None,
    initial_response_hash: str | None = None,
    repaired_response_hash: str | None = None,
) -> InterpretationResult:
    if not claims:
        record = _execution_record(
            bundle,
            mode=mode,
            provider=provider,
            provider_version=provider_version,
            provider_model=provider_model,
            provider_config_hash=provider_config_hash,
            idempotency_key_hash=idempotency_key_hash,
            prompt_projection_hash=prompt_projection_hash,
            initial_response_hash=initial_response_hash,
            repaired_response_hash=repaired_response_hash,
            response_hash=response_hash,
            repair_count=repair_count,
            outcome=InterpretationOutcome.no_supported_evidence,
            diagnostics=["PROVIDER_RETURNED_NO_CLAIMS"] if mode == InterpretationMode.strict_provider else [],
            claim_count=0,
            started=started,
        )
        return InterpretationResult(
            InterpretationOutcome.no_supported_evidence,
            bundle,
            None,
            record,
            tuple(record.diagnostics),
        )
    outcome = InterpretationOutcome.ready_with_limits if bundle.partialResults or bundle.bundleLimitations else InterpretationOutcome.ready
    record = _execution_record(
        bundle,
        mode=mode,
        provider=provider,
        provider_version=provider_version,
        provider_model=provider_model,
        provider_config_hash=provider_config_hash,
        idempotency_key_hash=idempotency_key_hash,
        prompt_projection_hash=prompt_projection_hash,
        initial_response_hash=initial_response_hash,
        repaired_response_hash=repaired_response_hash,
        response_hash=response_hash,
        repair_count=repair_count,
        outcome=outcome,
        diagnostics=[],
        claim_count=len(claims),
        started=started,
    )
    record_id = record.executionRecordId
    interpretation_payload = {
        "schemaVersion": "1.0",
        "interpretationId": "",
        "interpretationHash": "0" * 64,
        "sourceBundleId": bundle.bundleId,
        "sourceBundleHash": bundle.bundleHash,
        "sourceJobId": bundle.jobId,
        "sourcePlanId": bundle.planId,
        "sourcePlanHash": bundle.planHash,
        "sourceGraphHash": bundle.graphHash,
        "mode": mode.value,
        "provider": provider,
        "providerVersion": provider_version,
        "claims": [claim.model_dump(mode="json") for claim in claims],
        "globalWarnings": bundle.bundleWarnings,
        "globalLimitations": bundle.bundleLimitations,
        "recommendations": [],
        "completeness": bundle.bundleCompleteness.value,
        "partialResultState": bundle.partialResults,
        "repairCount": repair_count,
        "outcome": outcome.value,
        "validationOutcome": "VALID",
        "executionRecordId": record_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    semantic = {key: value for key, value in interpretation_payload.items() if key not in {"interpretationId", "interpretationHash", "createdAt"}}
    interpretation_payload["interpretationHash"] = interpretation_semantic_hash(semantic)
    interpretation_payload["interpretationId"] = deterministic_interpretation_id("interpretation", interpretation_payload["interpretationHash"])
    interpretation = GroundedScientificInterpretation.model_validate(interpretation_payload)
    validate_grounded_interpretation(bundle, interpretation)
    return InterpretationResult(outcome, bundle, interpretation, record)


def _terminal_result(
    bundle: ScientificEvidenceBundle,
    mode: InterpretationMode,
    outcome: InterpretationOutcome,
    started: float,
    *,
    idempotency_key_hash: str | None = None,
) -> InterpretationResult:
    provider = "deterministic" if mode == InterpretationMode.deterministic else "openai_compatible"
    record = _execution_record(
        bundle,
        mode=mode,
        provider=provider,
        provider_version=DETERMINISTIC_INTERPRETER_VERSION if mode == InterpretationMode.deterministic else STRICT_PROVIDER_CONTRACT_VERSION,
        provider_model=None,
        provider_config_hash=None,
        idempotency_key_hash=idempotency_key_hash,
        prompt_projection_hash=None,
        initial_response_hash=None,
        repaired_response_hash=None,
        response_hash=None,
        repair_count=0,
        outcome=outcome,
        diagnostics=[],
        claim_count=0,
        started=started,
    )
    return InterpretationResult(outcome, bundle, None, record)


def _execution_record(
    bundle: ScientificEvidenceBundle,
    *,
    mode: InterpretationMode,
    provider: str,
    provider_version: str,
    provider_model: str | None,
    provider_config_hash: str | None,
    idempotency_key_hash: str | None,
    prompt_projection_hash: str | None,
    initial_response_hash: str | None,
    repaired_response_hash: str | None,
    response_hash: str | None,
    repair_count: int,
    outcome: InterpretationOutcome,
    diagnostics: list[str],
    claim_count: int,
    started: float,
) -> InterpretationExecutionRecord:
    semantic = {
        "schemaVersion": "1.0",
        "sourceJobId": bundle.jobId,
        "sourcePlanId": bundle.planId,
        "sourcePlanHash": bundle.planHash,
        "sourceGraphHash": bundle.graphHash,
        "sourceBundleId": bundle.bundleId,
        "sourceBundleHash": bundle.bundleHash,
        "mode": mode.value,
        "provider": provider,
        "providerVersion": provider_version,
        "providerModel": provider_model,
        "providerConfigHash": provider_config_hash,
        "idempotencyKeyHash": idempotency_key_hash,
        "promptProjectionHash": prompt_projection_hash,
        "initialResponseHash": initial_response_hash,
        "repairedResponseHash": repaired_response_hash,
        "responseHash": response_hash,
        "repairCount": repair_count,
        "evidenceItemCount": len(bundle.evidenceItems),
        "claimCount": claim_count,
        "warningCount": len(bundle.bundleWarnings),
        "limitationCount": len(bundle.bundleLimitations),
        "outcome": outcome.value,
        "diagnostics": sorted(set(diagnostics)),
        "caps": {"artifacts": 16, "evidenceItems": 256, "claims": 32, "repair": 1},
    }
    record_hash = interpretation_semantic_hash(semantic)
    return InterpretationExecutionRecord.model_validate({
        **semantic,
        "executionRecordId": deterministic_interpretation_id("interpretation_execution", record_hash),
        "executionRecordHash": record_hash,
        "elapsedMs": round((time.perf_counter() - started) * 1000, 6),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    })


def _validate_source_artifact(source: InterpretationSource, candidate: ArtifactProjectionInput) -> None:
    artifact = candidate.artifact
    if str(artifact.get("projectId")) != source.project_id or str(artifact.get("jobId")) != source.job_id:
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Artifact belongs to a different project or job.")
    if artifact.get("datasetId") not in {None, source.dataset_id}:
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Artifact belongs to a different dataset.")
    expected = str(artifact.get("sha256") or artifact.get("contentHash") or "")
    expected_size = int(artifact.get("sizeBytes") or artifact.get("size_bytes") or 0)
    if candidate.raw_checksum != expected or candidate.raw_size_bytes != expected_size:
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Artifact payload checksum does not match repository metadata.")
    if candidate.tool_call.get("status") != "completed":
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Only successful ToolCalls may provide scientific evidence.")
    if source.plan_schema_version == "0.2" and not candidate.lineage:
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "AnalysisPlan 0.2 artifacts require exact persisted lineage.")
    if candidate.lineage:
        lineage = candidate.lineage
        checks = (
            lineage.get("artifactId") == _artifact_id(artifact),
            lineage.get("projectId") == source.project_id,
            lineage.get("datasetId") in {None, source.dataset_id},
            lineage.get("jobId") == source.job_id,
            lineage.get("planId") == source.plan_id,
            lineage.get("planHash") == source.plan_hash,
            lineage.get("planSchemaVersion") == source.plan_schema_version,
            lineage.get("graphHash") == source.graph_hash,
            lineage.get("producerToolCallId") == candidate.tool_call.get("id"),
            lineage.get("producerStepId") == candidate.tool_call.get("stepId"),
            lineage.get("producerToolId") == candidate.tool_call.get("toolId"),
            lineage.get("artifactKind") == artifact.get("type"),
            lineage.get("contentHash") == expected,
        )
        if not all(checks):
            raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Artifact lineage does not match the source job and plan.")


def _claim_semantics(item: ScientificEvidenceItem) -> tuple[ClaimPredicate, ClaimType]:
    if item.evidenceKind == EvidenceKind.range:
        return ClaimPredicate.has_range, ClaimType.observation
    if item.evidenceKind == EvidenceKind.count:
        return ClaimPredicate.has_count, ClaimType.observation
    if item.evidenceKind == EvidenceKind.category:
        return ClaimPredicate.has_category, ClaimType.observation
    if item.evidenceKind == EvidenceKind.warning:
        return ClaimPredicate.reports_warning, ClaimType.warning
    if item.evidenceKind == EvidenceKind.limitation:
        return ClaimPredicate.reports_limitation, ClaimType.limitation
    return ClaimPredicate.has_value, ClaimType.observation


def _render_item_claim(item: ScientificEvidenceItem, predicate: ClaimPredicate) -> str:
    labels = {
        ClaimPredicate.has_range: "reported range",
        ClaimPredicate.has_count: "reported count",
        ClaimPredicate.has_category: "reported category",
        ClaimPredicate.has_value: "reported value",
        ClaimPredicate.reports_warning: "reported warning",
        ClaimPredicate.reports_limitation: "reported limitation",
        ClaimPredicate.is_partial: "partial result",
        ClaimPredicate.no_supported_conclusion: "supported conclusion",
    }
    label = labels.get(predicate, "reported result")
    return f"{item.subjectId} {label}: {item.displayValue}."


def _validate_claim_text(claim: ScientificClaim, evidence: list[ScientificEvidenceItem]) -> None:
    semantic_text = " ".join(
        [claim.renderedText, *claim.qualifiers, *(str(value) for value in claim.structuredPayload.values())]
    )
    lowered = semantic_text.lower()
    if any(phrase in lowered for phrase in FORBIDDEN_CONCLUSIONS):
        raise InterpretationError("UNSUPPORTED_SCIENTIFIC_CONCLUSION", "Claim contains a forbidden unsupported scientific conclusion.")
    if _PATH_OR_URL.search(semantic_text) or "<" in semantic_text or ">" in semantic_text:
        raise InterpretationError("EXECUTABLE_OR_EXTERNAL_TEXT", "Claim contains external or executable text.")
    allowed_numbers = set()
    for item in evidence:
        allowed_numbers.update(_normalized_numeric_tokens(item.displayValue))
        value = item.normalizedValue
        for raw in (value.scalar, value.minimum, value.maximum, *value.values):
            if isinstance(raw, (int, float)) and not isinstance(raw, bool):
                allowed_numbers.update(_number_variants(float(raw)))
    for token in _NUMBER.findall(semantic_text):
        normalized = token.replace(",", "").rstrip("%")
        try:
            number = float(normalized)
        except ValueError:
            raise InterpretationError("UNGROUNDED_NUMERIC_CLAIM", "Claim contains an invalid number.")
        if not any(math.isclose(number, allowed, rel_tol=1e-9, abs_tol=1e-12) for allowed in allowed_numbers):
            raise InterpretationError("UNGROUNDED_NUMERIC_CLAIM", "Claim contains a number absent from its evidence.")
    known_units = {
        "angstrom",
        "angstrom^3",
        "terahertz",
        "thz",
        "electron/angstrom^3",
        "elementary_charge/angstrom^3",
        "electronvolt",
    }
    claim_units = {unit for unit in known_units if unit in lowered}
    evidence_unit_text = " ".join(
        f"{item.unit or ''} {item.displayValue}".lower()
        for item in evidence
    )
    supported_units = {unit for unit in known_units if unit in evidence_unit_text}
    if not claim_units.issubset(supported_units):
        raise InterpretationError("UNGROUNDED_UNIT_CLAIM", "Claim contains a unit absent from its evidence.")


def _validate_claim_semantics(
    claim: ScientificClaim,
    evidence: Mapping[str, ScientificEvidenceItem],
    *,
    bundle: ScientificEvidenceBundle,
) -> None:
    subject_items = [evidence[item] for item in claim.subjectEvidenceIds]
    supporting_items = [evidence[item] for item in claim.supportingEvidenceIds]
    predicate_contract = {
        ClaimPredicate.has_value: (ClaimType.observation, {EvidenceKind.scalar, EvidenceKind.boolean, EvidenceKind.ordered_series_summary, EvidenceKind.table_row}),
        ClaimPredicate.has_range: (ClaimType.observation, {EvidenceKind.range}),
        ClaimPredicate.has_count: (ClaimType.observation, {EvidenceKind.count}),
        ClaimPredicate.has_category: (ClaimType.observation, {EvidenceKind.category}),
        ClaimPredicate.reports_warning: (ClaimType.warning, {EvidenceKind.warning}),
        ClaimPredicate.reports_limitation: (ClaimType.limitation, {EvidenceKind.limitation}),
        ClaimPredicate.is_partial: (ClaimType.limitation, {EvidenceKind.execution_state, EvidenceKind.limitation}),
        ClaimPredicate.no_supported_conclusion: (ClaimType.no_supported_conclusion, {EvidenceKind.limitation}),
    }
    if claim.semanticPredicate == ClaimPredicate.differs_from:
        if claim.claimType != ClaimType.comparison:
            raise InterpretationError("CLAIM_PREDICATE_MISMATCH", "DIFFERS_FROM requires a COMPARISON claim.")
        _validate_comparable_evidence(subject_items)
        if not set(claim.subjectEvidenceIds).issubset(claim.supportingEvidenceIds):
            raise InterpretationError("COMPARISON_SUPPORT_MISMATCH", "Comparison support must include both compared evidence items.")
        expected_text = (
            f"{subject_items[0].subjectId} and {subject_items[1].subjectId} report different "
            f"{subject_items[0].semanticRole}: {subject_items[0].displayValue} versus {subject_items[1].displayValue}."
        )
        expected_payload = {
            "leftEvidenceId": subject_items[0].evidenceItemId,
            "rightEvidenceId": subject_items[1].evidenceItemId,
        }
        if claim.renderedText != expected_text or claim.structuredPayload != expected_payload or claim.scope != "comparison":
            raise InterpretationError("COMPARISON_RENDERING_MISMATCH", "Comparison rendering is not the canonical evidence rendering.")
    elif claim.semanticPredicate in predicate_contract:
        expected_type, kinds = predicate_contract[claim.semanticPredicate]
        if claim.claimType != expected_type or len(subject_items) != 1 or subject_items[0].evidenceKind not in kinds:
            raise InterpretationError("CLAIM_PREDICATE_MISMATCH", "Claim type, predicate, and evidence kind are inconsistent.")
        subject = subject_items[0]
        if any(item.subjectId != subject.subjectId or item.semanticRole != subject.semanticRole for item in supporting_items):
            raise InterpretationError("CLAIM_SUPPORT_MISMATCH", "Claim support is not semantically aligned with its subject evidence.")
        expected_payload = {"displayValue": subject.displayValue, "subjectId": subject.subjectId}
        if (
            claim.renderedText != _render_item_claim(subject, claim.semanticPredicate)
            or claim.structuredPayload != expected_payload
            or claim.scope != subject.subjectId
        ):
            raise InterpretationError("CLAIM_RENDERING_MISMATCH", "Claim rendering is not the canonical evidence rendering.")
    else:
        raise InterpretationError("CLAIM_PREDICATE_UNSUPPORTED", "This predicate has no approved Phase 10L-4 evidence contract.")

    allowed_qualifiers = set(bundle.bundleWarnings + bundle.bundleLimitations)
    for item in [*subject_items, *supporting_items]:
        allowed_qualifiers.update(item.warnings)
        allowed_qualifiers.update(item.limitations)
    if any(value not in allowed_qualifiers for value in claim.qualifiers):
        raise InterpretationError("UNGROUNDED_QUALIFIER", "Claim qualifier is absent from the evidence bundle.")


def _validate_comparison_claim(claim: ScientificClaim, evidence: Mapping[str, ScientificEvidenceItem]) -> None:
    _validate_comparable_evidence([evidence[item] for item in claim.subjectEvidenceIds])


def _validate_comparable_evidence(items: list[ScientificEvidenceItem]) -> None:
    if len(items) != 2 or items[0].subjectId == items[1].subjectId:
        raise InterpretationError("COMPARISON_SCOPE_INVALID", "A comparison requires two distinct subjects.")
    comparable_fields = (
        "semanticRole",
        "evidenceKind",
        "valueKind",
        "unit",
        "referenceConvention",
        "datasetId",
        "datasetVersion",
    )
    if any(getattr(items[0], field) != getattr(items[1], field) for field in comparable_fields):
        raise InterpretationError("COMPARISON_NOT_COMPARABLE", "Comparison evidence has incompatible semantics, units, references, or scope.")
    if items[0].normalizedValue == items[1].normalizedValue:
        raise InterpretationError("COMPARISON_NO_DIFFERENCE", "DIFFERS_FROM cannot describe equal evidence values.")


def _normalized_numeric_tokens(value: str) -> set[float]:
    result: set[float] = set()
    for token in _NUMBER.findall(value):
        try:
            result.add(float(token.replace(",", "").rstrip("%")))
        except ValueError:
            pass
    return result


def _number_variants(value: float) -> set[float]:
    return {value, float(f"{value:.6g}"), round(value, 6)}


def _artifact_id(artifact: Mapping[str, Any]) -> str:
    value = artifact.get("artifactId") or artifact.get("id")
    if not isinstance(value, str) or not value:
        raise InterpretationError("SOURCE_INTEGRITY_FAILED", "Artifact identity is missing.")
    return value


def _contract_family(candidate: ArtifactProjectionInput) -> str:
    tool_id = str(candidate.tool_call.get("toolId") or candidate.tool_call.get("tool_id"))
    artifact_type = str(candidate.artifact.get("type") or "")
    contract = ARTIFACT_PROJECTOR_CONTRACTS.get((tool_id, artifact_type))
    return contract.contract_family if contract is not None else "unsupported"


def _fallback_contract(candidate: ArtifactProjectionInput) -> str:
    tool_id = str(candidate.tool_call.get("toolId") or candidate.tool_call.get("tool_id"))
    artifact_type = str(candidate.artifact.get("type") or "")
    contract = ARTIFACT_PROJECTOR_CONTRACTS.get((tool_id, artifact_type))
    if contract is not None:
        return contract.accepted_versions[0]
    return str(candidate.artifact.get("version") or "1")


def _display_value(value: EvidenceValue, unit: str | None) -> str:
    suffix = f" {unit}" if unit else ""
    if value.minimum is not None and value.maximum is not None:
        return f"{_format_number(value.minimum)} to {_format_number(value.maximum)}{suffix}"
    if isinstance(value.scalar, float):
        return f"{_format_number(value.scalar)}{suffix}"
    return f"{value.scalar}{suffix}"


def _format_number(value: float) -> str:
    return f"{float(value):.6g}"


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _safe_semantic_name(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and len(value) <= 160
        and not _PATH_OR_URL.search(value)
        and not _PROMPT_INJECTION.search(value)
        and "<" not in value
        and ">" not in value
        and not _CREDENTIAL_SHAPED.search(value)
    )


def _provider_safe_value(value: Any, *, depth: int = 0) -> bool:
    if depth > 8:
        return False
    if value is None or isinstance(value, bool):
        return True
    if isinstance(value, (int, float)):
        return not isinstance(value, float) or math.isfinite(value)
    if isinstance(value, str):
        return (
            len(value) <= 1024
            and not _PATH_OR_URL.search(value)
            and not _PROMPT_INJECTION.search(value)
            and not _CREDENTIAL_SHAPED.search(value)
            and "<" not in value
            and ">" not in value
            and all(character >= " " or character in "\t\n" for character in value)
        )
    if isinstance(value, list):
        return len(value) <= 32 and all(_provider_safe_value(item, depth=depth + 1) for item in value)
    if isinstance(value, dict):
        return len(value) <= 32 and all(
            _safe_semantic_name(key) and _provider_safe_value(item, depth=depth + 1)
            for key, item in value.items()
        )
    return False


def _provider_safe_evidence_item(item: ScientificEvidenceItem) -> bool:
    return _provider_safe_value(
        {
            "semanticRole": item.semanticRole,
            "subjectId": item.subjectId,
            "valueKind": item.valueKind,
            "normalizedValue": item.normalizedValue.model_dump(mode="json"),
            "displayValue": item.displayValue,
            "unit": item.unit,
            "referenceConvention": item.referenceConvention,
            "resourceId": item.resourceId,
            "warnings": item.warnings,
            "limitations": item.limitations,
        }
    )


def _safe_messages(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        if (
            isinstance(item, str)
            and 0 < len(item) <= 512
            and not _PATH_OR_URL.search(item)
            and not _PROMPT_INJECTION.search(item)
            and not _CREDENTIAL_SHAPED.search(item)
            and "<" not in item
            and ">" not in item
        ):
            result.append(item)
    result = sorted(set(result))
    if len(result) > 16:
        raise InterpretationError("EVIDENCE_CAP_EXCEEDED", "Artifact warning count exceeds the per-item cap of 16.")
    return result


__all__ = [
    "ArtifactProjectionInput",
    "InterpretationError",
    "InterpretationResult",
    "InterpretationSource",
    "ProviderInterpretationProposal",
    "build_scientific_evidence_bundle",
    "deterministic_interpret",
    "no_supported_evidence_result",
    "project_artifact",
    "provider_safe_projection",
    "strict_provider_interpret",
    "validate_grounded_interpretation",
]
