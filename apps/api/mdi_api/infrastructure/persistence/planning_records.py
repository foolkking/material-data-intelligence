"""Planning persistence normalization and row mapping helpers."""

from __future__ import annotations

from typing import Any, Mapping

from mdi_schemas import (
    AnalysisPlanV03,
    AnalysisPlanV04,
    ArtifactLineageRecord,
    DependencyBinding,
    DependencyExecutionRecord,
    ResolvedArtifactInputRef,
    parse_analysis_plan,
    parse_dependency_plan,
    dependency_semantic_hash,
    deterministic_dependency_id,
)

from mdi_api.application.research.planning.integrity import compute_plan_hash
from mdi_api.infrastructure.persistence.base import _enum_value, _iso, _json_copy, _parse_iso, _utc_now
from mdi_schemas.multi_source_planning import parse_artifact_lineage

def _normalize_plan_bindings(
    plan_record: Mapping[str, Any],
    plan_id: str,
    plan_hash: str,
    graph_hash: str,
    bindings: list[DependencyBinding | Mapping[str, Any]],
) -> list[dict[str, Any]]:
    payload = plan_record.get("analysisPlan") or plan_record.get("analysisPlanJson") or {}
    plan = parse_dependency_plan(payload)
    if str(plan_record.get("planId") or plan_record.get("id")) != plan_id:
        raise ValueError("Planned dependency binding plan identity is invalid")
    if compute_plan_hash(plan) != plan_hash or str(plan_record.get("planHash")) != plan_hash:
        raise ValueError("Planned dependency binding plan hash is invalid")
    if plan.graphHash != graph_hash:
        raise ValueError("Planned dependency binding graph hash is invalid")
    parsed = [item if isinstance(item, DependencyBinding) else DependencyBinding.model_validate(item) for item in bindings]
    expected = sorted((item.model_dump(mode="json") for item in plan.dependencyBindings), key=lambda item: item["bindingId"])
    actual = sorted((item.model_dump(mode="json") for item in parsed), key=lambda item: item["bindingId"])
    if actual != expected:
        raise ValueError("Planned dependency bindings must exactly match the persisted AnalysisPlan")
    records: list[dict[str, Any]] = []
    for binding in actual:
        semantic = {
            "planId": plan_id,
            "planHash": plan_hash,
            "graphHash": graph_hash,
            "dependencyBinding": binding,
        }
        records.append(
            {
                **semantic,
                **binding,
                "semanticRecordHash": dependency_semantic_hash(semantic),
            }
        )
    return records


def _planned_binding_values(record: Mapping[str, Any]) -> dict[str, Any]:
    binding = DependencyBinding.model_validate(record["dependencyBinding"])
    return {
        "plan_id": record["planId"],
        "binding_id": binding.bindingId,
        "plan_hash": record["planHash"],
        "graph_hash": record["graphHash"],
        "producer_step_id": binding.producerStepId,
        "producer_output_port": binding.producerOutputPort,
        "consumer_step_id": binding.consumerStepId,
        "consumer_input_port": binding.consumerInputPort,
        "artifact_kind": binding.artifactKind.value,
        "artifact_contract_version": binding.artifactContractVersion,
        "media_type": binding.mediaType,
        "cardinality": binding.cardinality.value,
        "binding_json": binding.model_dump(mode="json"),
        "semantic_record_hash": record["semanticRecordHash"],
    }


def _planned_binding_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    binding = DependencyBinding.model_validate(_json_copy(row["binding_json"]))
    semantic = {
        "planId": row["plan_id"],
        "planHash": row["plan_hash"],
        "graphHash": row["graph_hash"],
        "dependencyBinding": binding.model_dump(mode="json"),
    }
    record = {
        **semantic,
        **binding.model_dump(mode="json"),
        "semanticRecordHash": row["semantic_record_hash"],
    }
    if record["semanticRecordHash"] != dependency_semantic_hash(semantic):
        raise ValueError("Persisted dependency binding record hash is invalid")
    return record


def _normalize_binding_resolution_record(record: Mapping[str, Any]) -> dict[str, Any]:
    source = _json_copy(record)
    resolved_payload = source.get("resolvedArtifactInputRef") or source.get("resolved_ref_json")
    resolved = ResolvedArtifactInputRef.model_validate(resolved_payload) if resolved_payload is not None else None

    def field(camel: str, snake: str, default: Any = None) -> Any:
        if source.get(camel) is not None:
            return source[camel]
        if source.get(snake) is not None:
            return source[snake]
        if resolved is not None and hasattr(resolved, camel):
            return getattr(resolved, camel)
        return default

    semantic = {
        "planId": str(field("planId", "plan_id") or ""),
        "planHash": str(field("planHash", "plan_hash") or ""),
        "jobId": str(field("jobId", "job_id") or ""),
        "bindingId": str(field("bindingId", "binding_id") or ""),
        "producerToolCallId": field("producerToolCallId", "producer_tool_call_id"),
        "producerStepId": str(field("producerStepId", "producer_step_id") or ""),
        "artifactId": field("artifactId", "artifact_id"),
        "artifactChecksum": field("artifactChecksum", "artifact_checksum", field("checksum", "checksum")),
        "artifactKind": _enum_value(field("artifactKind", "artifact_kind")) if field("artifactKind", "artifact_kind") else None,
        "artifactContractVersion": field("artifactContractVersion", "artifact_contract_version"),
        "mediaType": field("mediaType", "media_type"),
        "consumerToolCallId": field("consumerToolCallId", "consumer_tool_call_id"),
        "consumerStepId": str(field("consumerStepId", "consumer_step_id") or ""),
        "consumerInputPort": str(field("consumerInputPort", "consumer_input_port") or ""),
        "validationOutcome": str(field("validationOutcome", "validation_outcome") or ""),
        "errorCode": field("errorCode", "error_code"),
        "resolvedArtifactInputRef": resolved.model_dump(mode="json") if resolved is not None else None,
    }
    for required in ("planId", "planHash", "jobId", "bindingId", "producerStepId", "consumerStepId", "consumerInputPort", "validationOutcome"):
        if not semantic[required]:
            raise ValueError(f"Runtime artifact binding resolution is missing {required}")
    if len(semantic["planHash"]) != 64:
        raise ValueError("Runtime artifact binding resolution planHash is invalid")
    if resolved is not None:
        for key in ("planId", "planHash", "jobId", "bindingId", "producerStepId", "consumerStepId", "consumerInputPort"):
            if semantic[key] != getattr(resolved, key):
                raise ValueError("Resolved artifact input identity conflicts with binding resolution")
    computed_hash = dependency_semantic_hash(semantic)
    provided_hash = source.get("recordHash") or source.get("record_hash")
    if provided_hash and str(provided_hash) != computed_hash:
        raise ValueError("Runtime artifact binding resolution hash is invalid")
    record_id = str(source.get("id") or deterministic_dependency_id("binding_resolution", computed_hash))
    return {
        "id": record_id,
        "recordHash": computed_hash,
        **semantic,
        "resolvedAt": source.get("resolvedAt") or source.get("resolved_at") or _utc_now(),
    }


def _binding_resolution_values(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": record["id"],
        "record_hash": record["recordHash"],
        "plan_id": record["planId"],
        "plan_hash": record["planHash"],
        "job_id": record["jobId"],
        "binding_id": record["bindingId"],
        "producer_tool_call_id": record["producerToolCallId"],
        "producer_step_id": record["producerStepId"],
        "artifact_id": record["artifactId"],
        "artifact_checksum": record["artifactChecksum"],
        "artifact_kind": record["artifactKind"],
        "artifact_contract_version": record["artifactContractVersion"],
        "media_type": record["mediaType"],
        "consumer_tool_call_id": record["consumerToolCallId"],
        "consumer_step_id": record["consumerStepId"],
        "consumer_input_port": record["consumerInputPort"],
        "validation_outcome": record["validationOutcome"],
        "error_code": record["errorCode"],
        "resolved_ref_json": _json_copy(record["resolvedArtifactInputRef"]),
        "resolved_at": _parse_iso(str(record["resolvedAt"])),
    }


def _binding_resolution_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return _normalize_binding_resolution_record(
        {
            "id": row["id"],
            "recordHash": row["record_hash"],
            "planId": row["plan_id"],
            "planHash": row["plan_hash"],
            "jobId": row["job_id"],
            "bindingId": row["binding_id"],
            "producerToolCallId": row.get("producer_tool_call_id"),
            "producerStepId": row["producer_step_id"],
            "artifactId": row.get("artifact_id"),
            "artifactChecksum": row.get("artifact_checksum"),
            "artifactKind": row.get("artifact_kind"),
            "artifactContractVersion": row.get("artifact_contract_version"),
            "mediaType": row.get("media_type"),
            "consumerToolCallId": row.get("consumer_tool_call_id"),
            "consumerStepId": row["consumer_step_id"],
            "consumerInputPort": row["consumer_input_port"],
            "validationOutcome": row["validation_outcome"],
            "errorCode": row.get("error_code"),
            "resolvedArtifactInputRef": _json_copy(row.get("resolved_ref_json")),
            "resolvedAt": _iso(row["resolved_at"]),
        }
    )


def _normalize_dependency_execution_record(record: DependencyExecutionRecord | Mapping[str, Any]) -> dict[str, Any]:
    source = record.model_dump(mode="json") if isinstance(record, DependencyExecutionRecord) else _json_copy(record)
    payload = source.get("dependencyExecutionRecord") or source.get("recordJson") or source.get("record_json") or source
    parsed = DependencyExecutionRecord.model_validate(payload)
    semantic_hash = dependency_semantic_hash(
        parsed.model_dump(mode="json"), identity_fields=("executionId", "executionHash", "createdAt", "updatedAt")
    )
    expected_id = deterministic_dependency_id("execution", semantic_hash)
    if parsed.executionHash != semantic_hash or parsed.executionId != expected_id:
        raise ValueError("Dependency execution record identity is invalid")
    parsed_json = parsed.model_dump(mode="json")
    return {
        **parsed_json,
        "id": parsed.executionId,
        "executionId": parsed.executionId,
        "executionHash": parsed.executionHash,
        "planId": parsed.planId,
        "planHash": parsed.planHash,
        "jobId": parsed.jobId,
        "graphHash": parsed.graphHash,
        "outcome": parsed.outcome.value,
        "dependencyExecutionRecord": parsed_json,
        "createdAt": parsed.createdAt,
        "updatedAt": parsed.updatedAt,
    }


def _dependency_execution_values(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "execution_id": record["executionId"],
        "execution_hash": record["executionHash"],
        "plan_id": record["planId"],
        "plan_hash": record["planHash"],
        "job_id": record["jobId"],
        "graph_hash": record["graphHash"],
        "outcome": record["outcome"],
        "record_json": _json_copy(record["dependencyExecutionRecord"]),
        "created_at": _parse_iso(record["createdAt"]),
        "updated_at": _parse_iso(record["updatedAt"]),
    }


def _dependency_execution_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return _normalize_dependency_execution_record(_json_copy(row["record_json"]))


def _normalize_artifact_lineage_record(record: ArtifactLineageRecord | Mapping[str, Any]) -> dict[str, Any]:
    source = record.model_dump(mode="json") if isinstance(record, ArtifactLineageRecord) else _json_copy(record)
    payload = source.get("artifactLineageRecord") or source.get("recordJson") or source.get("record_json") or source
    parsed = parse_artifact_lineage(payload)
    semantic_hash = dependency_semantic_hash(
        parsed.model_dump(mode="json"), identity_fields=("lineageId", "lineageHash", "createdAt")
    )
    expected_id = deterministic_dependency_id("lineage", semantic_hash)
    if parsed.lineageHash != semantic_hash or parsed.lineageId != expected_id:
        raise ValueError("Artifact lineage record identity is invalid")
    parsed_json = parsed.model_dump(mode="json")
    return {
        **parsed_json,
        "id": parsed.lineageId,
        "lineageId": parsed.lineageId,
        "lineageHash": parsed.lineageHash,
        "artifactId": parsed.artifactId,
        "jobId": parsed.jobId,
        "planId": parsed.planId,
        "planHash": parsed.planHash,
        "graphHash": parsed.graphHash,
        "producerToolCallId": parsed.producerToolCallId,
        "producerStepId": parsed.producerStepId,
        "outputPort": parsed.outputPort,
        "artifactLineageRecord": parsed_json,
        "createdAt": parsed.createdAt,
    }


def _artifact_lineage_values(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "lineage_id": record["lineageId"],
        "lineage_hash": record["lineageHash"],
        "artifact_id": record["artifactId"],
        "job_id": record["jobId"],
        "plan_id": record["planId"],
        "plan_hash": record["planHash"],
        "graph_hash": record["graphHash"],
        "producer_tool_call_id": record["producerToolCallId"],
        "producer_step_id": record["producerStepId"],
        "output_port": record["outputPort"],
        "record_json": _json_copy(record["artifactLineageRecord"]),
        "created_at": _parse_iso(record["createdAt"]),
    }


def _artifact_lineage_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return _normalize_artifact_lineage_record(_json_copy(row["record_json"]))


def _normalize_analysis_plan_record(record: Mapping[str, Any]) -> dict[str, Any]:
    source = _json_copy(record)
    plan_json = (
        source.get("analysisPlan")
        or source.get("analysisPlanJson")
        or source.get("analysis_plan_json")
        or source.get("plan")
    )
    if plan_json is None:
        raise ValueError("AnalysisPlan record is missing analysis_plan_json")
    parsed_plan = parse_analysis_plan(plan_json)
    if isinstance(parsed_plan, AnalysisPlanV04):
        if str(source.get("projectId") or source.get("project_id") or "") != parsed_plan.projectId:
            raise ValueError("Project Plan ownership differs from its persisted project.")
        if any(source.get(field) is not None for field in ("datasetId", "dataset_id", "profileId", "profile_id")):
            raise ValueError("Project Plans cannot acquire a dataset or profile routing context.")
    if isinstance(parsed_plan, AnalysisPlanV03):
        for field, alternate in (("datasetId", "dataset_id"), ("profileId", "profile_id")):
            supplied = source.get(field) or source.get(alternate)
            if supplied is not None and str(supplied) != getattr(parsed_plan, field):
                raise ValueError("AnalysisPlan record routing context differs from its exact plan binding")
    plan_payload = parsed_plan.model_dump(mode="json")
    _reject_credential_keys(plan_payload)
    computed_hash = compute_plan_hash(parsed_plan)
    provided_hash = source.get("planHash") or source.get("plan_hash")
    if provided_hash and str(provided_hash) != computed_hash:
        raise ValueError("AnalysisPlan planHash does not match canonical AnalysisPlan JSON")
    plan_hash = computed_hash
    plan_id = str(source.get("id") or source.get("planId") or source.get("plan_id") or f"plan_{plan_hash[:24]}")
    validation_status = str(source.get("validationStatus") or source.get("validation_status") or "validated")
    if validation_status != "validated":
        raise ValueError("Only validated AnalysisPlan records may be persisted")
    return {
        "id": plan_id,
        "planId": plan_id,
        "projectId": str(source.get("projectId") or source.get("project_id") or ""),
        "datasetId": source.get("datasetId") or source.get("dataset_id") or parsed_plan.datasetId,
        "profileId": source.get("profileId") or source.get("profile_id") or parsed_plan.profileId,
        "jobId": source.get("jobId") or source.get("job_id"),
        "planSource": str(source.get("planSource") or source.get("plan_source") or "llm"),
        "plannerProvider": source.get("plannerProvider") or source.get("planner_provider"),
        "analysisPlan": plan_payload,
        "analysisPlanJson": plan_payload,
        "analysis_plan_json": plan_payload,
        "planHash": plan_hash,
        "plan_hash": plan_hash,
        "validationStatus": validation_status,
        "createdBy": str(source.get("createdBy") or source.get("created_by") or "user_local"),
        "createdAt": source.get("createdAt") or source.get("created_at") or _utc_now(),
        "updatedAt": source.get("updatedAt") or source.get("updated_at") or _utc_now(),
    }


def _analysis_plan_values(record: Mapping[str, Any]) -> dict[str, Any]:
    normalized = _normalize_analysis_plan_record(record)
    if not normalized["projectId"]:
        raise ValueError("AnalysisPlan record is missing projectId")
    return {
        "id": normalized["id"],
        "project_id": normalized["projectId"],
        "dataset_id": normalized.get("datasetId"),
        "profile_id": normalized.get("profileId"),
        "job_id": normalized.get("jobId"),
        "plan_source": normalized["planSource"],
        "planner_provider": normalized.get("plannerProvider"),
        "analysis_plan_json": _json_copy(normalized["analysisPlan"]),
        "plan_hash": normalized["planHash"],
        "validation_status": normalized["validationStatus"],
        "created_by": normalized["createdBy"],
    }


def _analysis_plan_from_record(record: Mapping[str, Any]) -> dict[str, Any]:
    normalized = _normalize_analysis_plan_record(record)
    return _json_copy(normalized)


def _analysis_plan_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    plan_payload = _json_copy(row.get("analysis_plan_json") or {})
    return _analysis_plan_from_record(
        {
            "id": row["id"],
            "projectId": row["project_id"],
            "datasetId": row.get("dataset_id"),
            "profileId": row.get("profile_id"),
            "jobId": row.get("job_id"),
            "planSource": row["plan_source"],
            "plannerProvider": row.get("planner_provider"),
            "analysisPlan": plan_payload,
            "planHash": row["plan_hash"],
            "validationStatus": row["validation_status"],
            "createdBy": row["created_by"],
            "createdAt": _iso(row["created_at"]),
            "updatedAt": _iso(row["updated_at"]),
        }
    )


def _reject_credential_keys(value: Any) -> None:
    credential_keys = {"api_key", "apikey", "api-key", "token", "password", "secret", "credential", "authorization"}
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).lower().replace("_", "").replace("-", "")
            if normalized in credential_keys:
                raise ValueError(f"AnalysisPlan JSON contains credential-like key: {key}")
            _reject_credential_keys(nested)
    elif isinstance(value, list):
        for item in value:
            _reject_credential_keys(item)


__all__ = []
