"""Planning-specific persistence normalization and row mapping."""

from __future__ import annotations

from typing import Any, Mapping

from mdi_schemas import (
    AnalysisIntent,
    CapabilityPlanningDecision,
    EligibilityResolution,
    capability_semantic_hash,
    compute_analysis_intent_hash,
    deterministic_capability_id,
    deterministic_intent_id,
)

from mdi_api.infrastructure.persistence.base import _iso, _json_copy


def normalize_analysis_intent_record(record: Mapping[str, Any]) -> dict[str, Any]:
    source = _json_copy(record)
    intent_json = source.get("analysisIntent") or source.get("intentJson") or source.get("intent_json")
    if intent_json is None:
        raise ValueError("AnalysisIntent record is missing intent_json")
    parsed = AnalysisIntent.model_validate(intent_json)
    computed_hash = compute_analysis_intent_hash(parsed)
    if parsed.intentHash != computed_hash or parsed.intentId != deterministic_intent_id(computed_hash):
        raise ValueError("AnalysisIntent identity does not match canonical JSON")
    intent_id = str(source.get("id") or source.get("intentId") or parsed.intentId)
    if intent_id != parsed.intentId:
        raise ValueError("AnalysisIntent record id does not match contract identity")
    provided_hash = source.get("intentHash") or source.get("intent_hash")
    if provided_hash and str(provided_hash) != parsed.intentHash:
        raise ValueError("AnalysisIntent record hash does not match contract identity")
    payload = parsed.model_dump(mode="json")
    return {
        "id": intent_id,
        "intentId": intent_id,
        "projectId": str(source.get("projectId") or source.get("project_id") or ""),
        "datasetId": parsed.datasetId,
        "profileId": parsed.profileId,
        "schemaVersion": parsed.schemaVersion,
        "intentHash": parsed.intentHash,
        "outcome": parsed.outcome.value,
        "parentIntentId": parsed.provenance.parentIntentId,
        "clarificationRound": parsed.clarification.round,
        "provider": parsed.provenance.provider,
        "model": parsed.provenance.model,
        "promptVersion": parsed.provenance.promptVersion,
        "analysisIntent": payload,
        "intentJson": payload,
        "createdBy": str(source.get("createdBy") or source.get("created_by") or "user_local"),
        "createdAt": source.get("createdAt") or source.get("created_at") or parsed.provenance.createdAt,
    }


def analysis_intent_values(record: Mapping[str, Any]) -> dict[str, Any]:
    normalized = normalize_analysis_intent_record(record)
    if not normalized["projectId"]:
        raise ValueError("AnalysisIntent record is missing projectId")
    return {
        "id": normalized["intentId"],
        "project_id": normalized["projectId"],
        "dataset_id": normalized["datasetId"],
        "profile_id": normalized["profileId"],
        "schema_version": normalized["schemaVersion"],
        "intent_hash": normalized["intentHash"],
        "outcome": normalized["outcome"],
        "parent_intent_id": normalized["parentIntentId"],
        "clarification_round": normalized["clarificationRound"],
        "provider": normalized["provider"],
        "model": normalized["model"],
        "prompt_version": normalized["promptVersion"],
        "intent_json": _json_copy(normalized["analysisIntent"]),
        "created_by": normalized["createdBy"],
    }


def analysis_intent_from_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return _json_copy(normalize_analysis_intent_record(record))


def analysis_intent_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return analysis_intent_from_record(
        {
            "id": row["id"],
            "projectId": row["project_id"],
            "analysisIntent": _json_copy(row.get("intent_json") or {}),
            "createdBy": row["created_by"],
            "createdAt": _iso(row["created_at"]),
        }
    )


def intent_execution_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "intentId": row["intent_id"],
        "planId": row["plan_id"],
        "jobId": row["job_id"],
        "createdAt": _iso(row["created_at"]),
    }


def normalize_capability_resolution_record(record: Mapping[str, Any]) -> dict[str, Any]:
    source = _json_copy(record)
    payload = source.get("eligibilityResolution") or source.get("resolutionJson") or source.get("resolution_json")
    if payload is None:
        raise ValueError("Eligibility Resolution record is missing resolution_json")
    parsed = EligibilityResolution.model_validate(payload)
    computed_hash = capability_semantic_hash(parsed, identity_fields=("resolutionId", "resolutionHash"))
    if parsed.resolutionHash != computed_hash or parsed.resolutionId != deterministic_capability_id("resolution", computed_hash):
        raise ValueError("Eligibility Resolution identity does not match canonical JSON")
    return {
        "id": parsed.resolutionId,
        "resolutionId": parsed.resolutionId,
        "resolutionHash": parsed.resolutionHash,
        "intentId": parsed.intentId,
        "profileId": parsed.profileId,
        "profileSemanticHash": parsed.profileSemanticHash,
        "registrySnapshotId": parsed.registrySnapshotId,
        "registrySnapshotHash": parsed.registrySnapshotHash,
        "resolverVersion": parsed.provenance.resolverVersion,
        "eligibilityResolution": parsed.model_dump(mode="json"),
        "createdBy": str(source.get("createdBy") or source.get("created_by") or "user_local"),
        "createdAt": source.get("createdAt") or source.get("created_at"),
    }


def capability_resolution_values(record: Mapping[str, Any]) -> dict[str, Any]:
    normalized = normalize_capability_resolution_record(record)
    return {
        "id": normalized["resolutionId"],
        "resolution_hash": normalized["resolutionHash"],
        "intent_id": normalized["intentId"],
        "profile_id": normalized["profileId"],
        "profile_semantic_hash": normalized["profileSemanticHash"],
        "registry_snapshot_id": normalized["registrySnapshotId"],
        "registry_snapshot_hash": normalized["registrySnapshotHash"],
        "resolver_version": normalized["resolverVersion"],
        "resolution_json": _json_copy(normalized["eligibilityResolution"]),
        "created_by": normalized["createdBy"],
    }


def capability_resolution_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    record = normalize_capability_resolution_record(
        {
            "eligibilityResolution": _json_copy(row.get("resolution_json") or {}),
            "createdBy": row["created_by"],
            "createdAt": _iso(row["created_at"]),
        }
    )
    record["createdAt"] = _iso(row["created_at"])
    return record


def normalize_capability_decision_record(record: Mapping[str, Any]) -> dict[str, Any]:
    source = _json_copy(record)
    payload = source.get("capabilityDecision") or source.get("decisionJson") or source.get("decision_json")
    if payload is None:
        raise ValueError("Capability Planning Decision record is missing decision_json")
    parsed = CapabilityPlanningDecision.model_validate(payload)
    computed_hash = capability_semantic_hash(parsed, identity_fields=("decisionId", "decisionHash"))
    if parsed.decisionHash != computed_hash or parsed.decisionId != deterministic_capability_id("decision", computed_hash):
        raise ValueError("Capability Planning Decision identity does not match canonical JSON")
    return {
        "id": parsed.decisionId,
        "decisionId": parsed.decisionId,
        "decisionHash": parsed.decisionHash,
        "intentId": parsed.intentId,
        "resolutionId": parsed.resolutionId,
        "outcome": parsed.outcome.value,
        "provider": parsed.provenance.provider,
        "providerContractVersion": parsed.provenance.providerContractVersion,
        "model": parsed.provenance.model,
        "repairCount": parsed.provenance.repairCount,
        "capabilityDecision": parsed.model_dump(mode="json"),
        "createdBy": str(source.get("createdBy") or source.get("created_by") or "user_local"),
        "createdAt": source.get("createdAt") or source.get("created_at"),
    }


def capability_decision_values(record: Mapping[str, Any]) -> dict[str, Any]:
    normalized = normalize_capability_decision_record(record)
    return {
        "id": normalized["decisionId"],
        "decision_hash": normalized["decisionHash"],
        "intent_id": normalized["intentId"],
        "resolution_id": normalized["resolutionId"],
        "outcome": normalized["outcome"],
        "provider": normalized["provider"],
        "provider_contract_version": normalized["providerContractVersion"],
        "model": normalized["model"],
        "repair_count": normalized["repairCount"],
        "decision_json": _json_copy(normalized["capabilityDecision"]),
        "created_by": normalized["createdBy"],
    }


def capability_decision_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    record = normalize_capability_decision_record(
        {
            "capabilityDecision": _json_copy(row.get("decision_json") or {}),
            "createdBy": row["created_by"],
            "createdAt": _iso(row["created_at"]),
        }
    )
    record["createdAt"] = _iso(row["created_at"])
    return record


def capability_execution_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "decisionId": row["decision_id"],
        "intentId": row["intent_id"],
        "planId": row["plan_id"],
        "jobId": row["job_id"],
        "createdAt": _iso(row["created_at"]),
    }


__all__ = [
    "analysis_intent_from_record",
    "analysis_intent_from_row",
    "analysis_intent_values",
    "capability_decision_from_row",
    "capability_decision_values",
    "capability_execution_from_row",
    "capability_resolution_from_row",
    "capability_resolution_values",
    "intent_execution_from_row",
    "normalize_analysis_intent_record",
    "normalize_capability_decision_record",
    "normalize_capability_resolution_record",
]
