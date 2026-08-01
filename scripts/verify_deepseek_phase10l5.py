from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any
from unittest.mock import patch
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import (
    PlannerInterpretationRequest,
    PlannerJobsRequest,
    create_planner_job_interpretation,
    get_planner_analysis_plan,
    get_planner_interpretation_evidence,
    get_planner_job,
    get_planner_job_artifacts,
    get_planner_job_dependencies,
    get_planner_job_events,
    get_planner_job_result,
    get_planner_job_tool_calls,
    planner_jobs,
)
from mdi_llm import (
    DEEPSEEK_ALLOWED_MODELS,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_DEFAULT_MODEL,
    DeepSeekProvider,
    LLMProviderError,
    redact_credential_values,
)
from mdi_schemas import (
    DeepSeekVerificationSuite,
    DeepSeekVerificationRecord,
    deterministic_natural_language_evidence_id,
    natural_language_evidence_hash,
)
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime

from scripts.generate_phase10l5_natural_language_closure_evidence import (
    EVIDENCE,
    FIXED_TIME,
    _inputs,
    _sanitize,
    case_specs,
)


MAX_REAL_CALLS = 12
CASE_SLUGS = ("dataset", "structure", "materials_ml", "phonon", "volumetric")
MAX_PERSISTED_ERROR_BYTES = 2_048
_SAFE_ERROR_CODE = re.compile(r"^[A-Z][A-Z0-9_]{0,127}$")
_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")
_LOCAL_PATH = re.compile(
    r"(?i)(?:(?<![a-z])[a-z]:(?:\\|/(?!/))[^\r\n\t\"']+|file://[^\s\"']+|/(?:tmp|var/tmp)/[^\s\"']+)"
)
_EXTERNAL_URL = re.compile(r"(?i)https?://[^\s\"']+")
_SENSITIVE_RECORD_KEYS = {
    "apikey",
    "artifactroot",
    "authorization",
    "bucket",
    "filesystempath",
    "localpath",
    "messages",
    "objectstorekey",
    "providerrequest",
    "providerresponse",
    "rawjson",
    "rawproviderresponse",
    "rawresponse",
    "requestbody",
    "responsebody",
    "secret",
    "storagekey",
}
_REQUIRED_LIVE_CHAIN_RECORDS = (
    "profile",
    "intent",
    "eligibilityResolution",
    "capabilityDecision",
    "analysisPlan",
    "job",
    "events",
    "toolCalls",
    "artifacts",
    "evidenceBundle",
    "interpretation",
)


def _write_json(relative: str, value: Any) -> None:
    target = EVIDENCE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    sanitized = _sanitize_live_payload(value)
    target.write_text(
        json.dumps(sanitized, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _sanitize_live_payload(value: Any) -> Any:
    """Remove transport authority, credentials, and machine-local paths before persistence."""

    def visit(item: Any) -> Any:
        if isinstance(item, dict):
            return {
                str(key): visit(child)
                for key, child in item.items()
                if re.sub(r"[^a-z0-9]", "", str(key).lower()) not in _SENSITIVE_RECORD_KEYS
            }
        if isinstance(item, list):
            return [visit(child) for child in item]
        if isinstance(item, tuple):
            return [visit(child) for child in item]
        if isinstance(item, str):
            redacted = redact_credential_values(item)
            if redacted == DEEPSEEK_BASE_URL:
                return redacted
            redacted = _EXTERNAL_URL.sub("***REDACTED_URL***", redacted)
            return _LOCAL_PATH.sub("***REDACTED_PATH***", redacted)
        return item

    return visit(_sanitize(value))


def _repository_execution_counts(repositories: InMemoryRepositoryBundle, runtime: QueueWorkerRuntime) -> dict[str, int]:
    queue_backend = runtime.queue_backend
    return {
        "planCount": len(getattr(repositories.analysis_plans, "records", {})),
        "jobCount": len(getattr(repositories.jobs, "records", {})),
        "toolCallCount": len(getattr(repositories.tool_calls, "records", {})),
        "artifactCount": len(getattr(repositories.artifacts, "records", {})),
        "plannedBindingCount": sum(
            len(value) for value in getattr(repositories.dependency_execution, "plan_bindings", {}).values()
        ),
        "bindingResolutionCount": len(
            getattr(repositories.dependency_execution, "binding_resolutions", {})
        ),
        "dependencyExecutionCount": len(getattr(repositories.dependency_execution, "executions", {})),
        "lineageCount": len(getattr(repositories.dependency_execution, "lineage", {})),
        "queueMessageCount": len(getattr(queue_backend, "_queued", [])),
    }


def _assert_non_ready_created_nothing(
    planned: Any,
    *,
    repositories: InMemoryRepositoryBundle,
    runtime: QueueWorkerRuntime,
) -> dict[str, int]:
    counts = _repository_execution_counts(repositories, runtime)
    response_has_execution = any(
        (
            planned.plan,
            planned.plan_id,
            planned.plan_hash,
            planned.job_id,
            planned.enqueued,
            planned.executed,
            planned.dependency_bindings,
            planned.topological_order,
        )
    )
    if response_has_execution or any(counts.values()):
        raise RuntimeError(
            "LIVE_NON_READY_CREATED_EXECUTION:"
            + json.dumps(counts, sort_keys=True, separators=(",", ":"))
        )
    return counts


def _assert_selected_tools_are_eligible(planned: Any, selected_tools: list[str]) -> tuple[list[str], list[str]]:
    resolution = planned.eligibility_resolution or {}
    decision = planned.capability_decision or {}
    eligible_tools = sorted(set(resolution.get("eligibleToolIds") or []))
    provider_visible_tools = sorted(set(planned.provider_visible_tool_ids or []))
    selected = sorted(set(selected_tools))
    decision_selected = sorted(
        {
            item.get("toolId")
            for item in decision.get("selections", [])
            if isinstance(item, dict) and item.get("toolId")
        }
    )
    if not eligible_tools:
        raise RuntimeError("LIVE_ELIGIBLE_TOOL_SET_MISSING")
    if provider_visible_tools != eligible_tools:
        raise RuntimeError("LIVE_PROVIDER_VISIBLE_TOOLS_DIFFER_FROM_ELIGIBLE")
    if not set(selected).issubset(eligible_tools):
        raise RuntimeError("LIVE_SELECTED_TOOL_NOT_ELIGIBLE")
    if decision_selected != selected:
        raise RuntimeError("LIVE_DECISION_PLAN_SELECTION_MISMATCH")
    return eligible_tools, provider_visible_tools


def _assert_provider_call_audit(audit: tuple[dict[str, Any], ...]) -> None:
    if not 3 <= len(audit) <= MAX_REAL_CALLS:
        raise RuntimeError("DEEPSEEK_REAL_CALL_AUDIT_INVALID")
    for item in audit:
        usage = item.get("tokenUsage") or {}
        if (
            item.get("realCall") is not True
            or not _SHA256_HEX.fullmatch(str(item.get("promptHash") or ""))
            or not _SHA256_HEX.fullmatch(str(item.get("responseHash") or ""))
            or item.get("outcome") != "SUCCESS"
            or not isinstance(usage.get("promptTokens"), int)
            or not isinstance(usage.get("completionTokens"), int)
            or usage.get("totalTokens") != usage.get("promptTokens") + usage.get("completionTokens")
            or int(item.get("promptBytes") or 0) <= 0
            or int(item.get("responseBytes") or 0) <= 0
        ):
            raise RuntimeError("DEEPSEEK_REAL_CALL_AUDIT_INVALID")


def _assert_complete_live_record(record: dict[str, Any]) -> None:
    missing = [key for key in _REQUIRED_LIVE_CHAIN_RECORDS if not record.get(key)]
    if missing:
        raise RuntimeError(f"LIVE_PERSISTED_CHAIN_INCOMPLETE:{','.join(missing)}")
    selected = set(record.get("selectedToolIds") or [])
    eligible = set(record.get("eligibleToolIds") or [])
    if not selected or not selected.issubset(eligible):
        raise RuntimeError("LIVE_SELECTED_TOOL_NOT_ELIGIBLE")
    lineage = record.get("artifactLineage") or []
    artifacts = record.get("artifacts") or []
    if not lineage and any(not item.get("provenance") for item in artifacts):
        raise RuntimeError("LIVE_ARTIFACT_LINEAGE_OR_PROVENANCE_MISSING")
    _assert_provider_call_audit(tuple(record.get("providerCallAudit") or []))


def _identified(payload: dict[str, Any]) -> DeepSeekVerificationRecord:
    semantic_hash = natural_language_evidence_hash(
        payload,
        exclude={"verificationId", "verificationHash", "createdAt"},
    )
    identified = {
        **payload,
        "verificationId": deterministic_natural_language_evidence_id("deepseek_verification", semantic_hash),
        "verificationHash": semantic_hash,
    }
    return DeepSeekVerificationRecord.model_validate(identified)


def _identified_suite(payload: dict[str, Any]) -> DeepSeekVerificationSuite:
    semantic_hash = natural_language_evidence_hash(
        payload,
        exclude={"suiteId", "suiteHash", "createdAt"},
    )
    return DeepSeekVerificationSuite.model_validate({
        **payload,
        "suiteId": deterministic_natural_language_evidence_id("deepseek_suite", semantic_hash),
        "suiteHash": semantic_hash,
    })


def _stable_uuid_iter(seed: str):
    for index in range(16):
        yield UUID(hex=sha256(f"phase10l5-live:{seed}:{index}".encode("utf-8")).hexdigest()[:32])


def _run_live_case(
    *,
    case_index: int,
    provider: DeepSeekProvider,
    model: str,
    artifact_root: Path,
) -> dict[str, Any]:
    spec = case_specs()[case_index]
    profile, object_store, selected_resources = _inputs(spec.title)
    repositories = InMemoryRepositoryBundle.create()
    repositories.data_profiles.save(profile)
    registry = load_manifests()
    runtime = QueueWorkerRuntime(
        repositories=repositories,
        registry=registry,
        artifact_root=artifact_root,
    )
    request = PlannerJobsRequest(
        userPrompt=spec.userText,
        projectId=f"project_phase10l5_live_{spec.caseSpecHash[:8]}",
        datasetId=profile.datasetId,
        profileId=profile.profileId,
        intentSchemaVersion="1.0",
        selectedResourceIds=selected_resources,
        provider="deepseek",
        model=model,
        temperature=0,
        maxTokens=8192,
        timeoutSeconds=120,
        enqueue=False,
    )
    first_call_index = len(provider.call_audit)
    uuids = iter(_stable_uuid_iter(spec.caseSpecHash))
    with patch("mdi_api.routers.planner.uuid.uuid4", side_effect=lambda: next(uuids)):
        planned = planner_jobs(
            request,
            provider=provider,
            repositories=repositories,
            queue_runtime=runtime,
            registry=registry,
        )
    if len(provider.call_audit) > MAX_REAL_CALLS:
        raise RuntimeError("DEEPSEEK_CALL_CAP_EXCEEDED")
    if not planned.ok or planned.capability_outcome != "PLAN_READY" or not planned.plan or not planned.job_id:
        side_effect_counts = _assert_non_ready_created_nothing(
            planned,
            repositories=repositories,
            runtime=runtime,
        )
        diagnostics = [item.get("code") for item in planned.validation_errors]
        diagnostic_messages = [
            _bounded_utf8(redact_credential_values(str(item.get("message") or "")), 512)
            for item in planned.validation_errors[:16]
        ]
        outcome = planned.error_code or planned.capability_outcome or planned.intent_outcome or "UNKNOWN"
        intent = planned.intent or {}
        resolution = planned.eligibility_resolution or {}
        safe_context = {
            "outcome": outcome,
            "diagnostics": diagnostics,
            "diagnosticMessages": diagnostic_messages,
            "scientificIntents": intent.get("scientificIntents", []),
            "requiredCapabilityNeeds": intent.get("requiredCapabilityNeeds", []),
            "desiredOutputs": intent.get("desiredOutputs", []),
            "resourceBindings": [
                {
                    "objectId": item.get("objectId"),
                    "kind": item.get("kind"),
                    "origin": item.get("origin"),
                }
                for item in (intent.get("dataScope", {}).get("resourceRefs") or [])
                if isinstance(item, dict)
            ],
            "targetSemanticIds": [
                item.get("semanticId")
                for item in (intent.get("targetSemantics") or [])
                if isinstance(item, dict) and item.get("semanticId")
            ],
            "eligibleToolIds": resolution.get("eligibleToolIds", []),
            "rejectionCodes": sorted({
                diagnostic.get("code")
                for diagnostic in resolution.get("diagnostics", [])
                if diagnostic.get("code")
            }),
            "executionSideEffects": side_effect_counts,
        }
        raise RuntimeError(f"LIVE_PLAN_NOT_READY:{json.dumps(safe_context, sort_keys=True, separators=(',', ':'))}")
    selected_tools = [step["toolId"] for step in planned.plan["steps"]]
    eligible_tools, provider_visible_tools = _assert_selected_tools_are_eligible(planned, selected_tools)
    if not set(selected_tools).issubset(spec.acceptableToolIds):
        raise RuntimeError(f"LIVE_SELECTION_ESCAPED_APPROVED_DOMAIN:{selected_tools}")
    if set(selected_tools).intersection(spec.forbiddenFallbacks):
        raise RuntimeError(f"LIVE_SELECTION_USED_FORBIDDEN_FALLBACK:{selected_tools}")
    if spec.requiresDependencyPlan and planned.plan_schema_version != "0.2":
        raise RuntimeError("LIVE_DEPENDENCY_PLAN_REQUIRED")

    completed = runtime.handle_job(planned.job_id, object_store=object_store)
    if completed.status != "completed":
        raise RuntimeError(f"LIVE_RUNTIME_FAILED:{completed.status}")
    interpreted = create_planner_job_interpretation(
        planned.job_id,
        PlannerInterpretationRequest(
            mode="STRICT_PROVIDER",
            expectedPlanHash=planned.plan_hash or "",
            idempotencyKey=f"phase10l5-live-{spec.caseSpecHash[:24]}",
            provider="deepseek",
            model=model,
            temperature=0,
            maxTokens=8192,
            timeoutSeconds=120,
        ),
        repositories=repositories,
        queue_runtime=runtime,
        provider=provider,
    )
    if len(provider.call_audit) > MAX_REAL_CALLS:
        raise RuntimeError("DEEPSEEK_CALL_CAP_EXCEEDED")
    if interpreted.get("outcome") not in {"INTERPRETATION_READY", "INTERPRETATION_READY_WITH_LIMITS"}:
        safe_context = {
            "outcome": interpreted.get("outcome"),
            "diagnostics": interpreted.get("diagnostics", []),
            "repairCount": (interpreted.get("execution") or {}).get("repairCount"),
            "evidenceItemCount": len((interpreted.get("evidenceBundle") or {}).get("evidenceItems", [])),
        }
        raise RuntimeError(
            f"LIVE_INTERPRETATION_FAILED:{json.dumps(safe_context, sort_keys=True, separators=(',', ':'))}"
        )
    interpretation_id = interpreted.get("interpretationId")
    if not interpretation_id:
        raise RuntimeError("LIVE_INTERPRETATION_ID_MISSING")
    evidence = get_planner_interpretation_evidence(interpretation_id, repositories=repositories)
    if not interpreted.get("claims") or not evidence.get("evidenceItems"):
        raise RuntimeError("LIVE_GROUNDED_CLAIMS_MISSING")

    profile_record = repositories.data_profiles.get(profile.profileId)
    plan_record = get_planner_analysis_plan(planned.plan_id, repositories=repositories)
    job_record = get_planner_job(planned.job_id, repositories=repositories)
    intent_record = job_record.get("analysisIntent") or {}
    eligibility_record = job_record.get("eligibilityResolution") or {}
    decision_record = job_record.get("capabilityDecision") or {}
    interpretation_record = repositories.interpretations.get_interpretation(interpretation_id)
    evidence_bundle = repositories.interpretations.get_bundle(interpreted["bundleId"])
    tool_calls = get_planner_job_tool_calls(planned.job_id, repositories=repositories)
    events = get_planner_job_events(planned.job_id, repositories=repositories)
    artifacts = get_planner_job_artifacts(planned.job_id, repositories=repositories)
    dependencies = get_planner_job_dependencies(planned.job_id, repositories=repositories)
    result = get_planner_job_result(planned.job_id, repositories=repositories)
    call_audit = tuple(provider.call_audit[first_call_index:])
    _assert_provider_call_audit(call_audit)

    if intent_record != (planned.intent or {}):
        raise RuntimeError("LIVE_PERSISTED_INTENT_MISMATCH")
    if eligibility_record.get("resolutionHash") != (planned.eligibility_resolution or {}).get("resolutionHash"):
        raise RuntimeError("LIVE_PERSISTED_ELIGIBILITY_MISMATCH")
    if decision_record.get("decisionHash") != (planned.capability_decision or {}).get("decisionHash"):
        raise RuntimeError("LIVE_PERSISTED_DECISION_MISMATCH")
    if plan_record.get("analysisPlan") != planned.plan or plan_record.get("planHash") != planned.plan_hash:
        raise RuntimeError("LIVE_PERSISTED_PLAN_MISMATCH")
    if job_record.get("planId") != planned.plan_id or job_record.get("planHash") != planned.plan_hash:
        raise RuntimeError("LIVE_PERSISTED_JOB_MISMATCH")
    if not tool_calls or any(item.get("status") != "completed" for item in tool_calls):
        raise RuntimeError("LIVE_TOOLCALL_RECORDS_INCOMPLETE")
    if not events:
        raise RuntimeError("LIVE_JOB_EVENTS_MISSING")
    if not artifacts:
        raise RuntimeError("LIVE_ARTIFACT_RECORDS_MISSING")
    if evidence_bundle.get("bundleHash") != evidence.get("bundleHash"):
        raise RuntimeError("LIVE_EVIDENCE_BUNDLE_MISMATCH")
    if interpretation_record.get("interpretation") != interpreted.get("interpretation"):
        raise RuntimeError("LIVE_INTERPRETATION_RECORD_MISMATCH")

    semantic_payload = {
        "caseSpecId": spec.caseSpecId,
        "intentHash": (planned.intent or {}).get("intentHash"),
        "resolutionHash": (planned.eligibility_resolution or {}).get("resolutionHash"),
        "decisionHash": (planned.capability_decision or {}).get("decisionHash"),
        "planHash": planned.plan_hash,
        "jobId": planned.job_id,
        "interpretationHash": interpreted["interpretation"]["interpretationHash"],
    }
    run_hash = sha256(json.dumps(semantic_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    live_record = {
        "schemaVersion": "1.0",
        "runId": f"live_run_{run_hash[:32]}",
        "runHash": run_hash,
        "caseSpecId": spec.caseSpecId,
        "userText": spec.userText,
        "provider": "deepseek",
        "model": model,
        "profile": profile_record,
        "intent": intent_record,
        "eligibilityResolution": eligibility_record,
        "capabilityDecision": decision_record,
        "eligibleToolIds": eligible_tools,
        "providerVisibleToolIds": provider_visible_tools,
        "selectedToolIds": selected_tools,
        "planSchemaVersion": planned.plan_schema_version,
        "planId": planned.plan_id,
        "planHash": planned.plan_hash,
        "graphHash": planned.graph_hash,
        "jobId": planned.job_id,
        "jobStatus": completed.status,
        "analysisPlan": plan_record,
        "job": job_record,
        "events": events,
        "toolCalls": tool_calls,
        "artifacts": artifacts,
        "dependencies": dependencies,
        "artifactLineage": dependencies.get("artifactLineage", []),
        "result": result,
        "evidenceBundle": evidence_bundle,
        "evidence": evidence,
        "interpretation": interpretation_record,
        "interpretationResponse": interpreted,
        "providerCallAudit": list(call_audit),
        "invariants": {
            "rawGoalPreserved": (planned.intent or {}).get("rawGoal") == spec.userText,
            "providerIsDeepSeek": planned.planner_provider == "deepseek",
            "selectionWithinApprovedDomain": set(selected_tools).issubset(spec.acceptableToolIds),
            "providerVisibleEqualsEligible": provider_visible_tools == eligible_tools,
            "selectedSubsetEligible": set(selected_tools).issubset(eligible_tools),
            "persistedChainComplete": all(
                (
                    profile_record,
                    intent_record,
                    eligibility_record,
                    decision_record,
                    plan_record,
                    job_record,
                    events,
                    tool_calls,
                    artifacts,
                    evidence_bundle,
                    interpretation_record,
                )
            ),
            "runtimeUsedPersistedPlan": True,
            "claimsHaveEvidence": all(item.get("supportingEvidenceIds") for item in interpreted["claims"]),
            "noFallback": True,
        },
        "verdict": "PASS",
    }
    _assert_complete_live_record(live_record)
    return live_record


def _aggregate_usage(audit: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    return {
        "promptTokens": sum(item["tokenUsage"]["promptTokens"] for item in audit),
        "completionTokens": sum(item["tokenUsage"]["completionTokens"] for item in audit),
        "totalTokens": sum(item["tokenUsage"]["totalTokens"] for item in audit),
        "estimated": any(item["tokenUsage"]["estimated"] for item in audit),
    }


def _case_prefix(case_index: int) -> str:
    return f"case_{case_index + 1:02d}_{CASE_SLUGS[case_index]}"


def _bounded_utf8(value: str, max_bytes: int) -> str:
    encoded = value.encode("utf-8")
    if len(encoded) <= max_bytes:
        return value
    return encoded[:max_bytes].decode("utf-8", errors="ignore")


def _safe_exception_summary(exc: Exception) -> tuple[str, str]:
    if isinstance(exc, LLMProviderError):
        error_code = exc.code
        details = exc.safe_message
    else:
        details = redact_credential_values(str(exc))
        candidate = details.split(":", 1)[0]
        error_code = candidate if _SAFE_ERROR_CODE.fullmatch(candidate) else "LIVE_VERIFICATION_FAILED"
    return error_code[:128], _bounded_utf8(redact_credential_values(details), MAX_PERSISTED_ERROR_BYTES)


def _write_live_failure(*, case_index: int, model: str, provider: DeepSeekProvider, started: float, exc: Exception) -> None:
    error_code, safe_details = _safe_exception_summary(exc)
    failures = EVIDENCE / "deepseek_live_failures"
    failures.mkdir(parents=True, exist_ok=True)
    attempt = len(list(failures.glob(f"{_case_prefix(case_index)}_attempt_*.json"))) + 1
    payload = {
        "caseIndex": case_index,
        "caseSpecId": case_specs()[case_index].caseSpecId,
        "configured": True,
        "model": model,
        "baseUrl": DEEPSEEK_BASE_URL,
        "keySource": "DEEPSEEK_KEY",
        "errorType": type(exc).__name__,
        "errorCode": error_code,
        "safeDetails": safe_details,
        "realCallCount": len(provider.call_audit),
        "callAudit": list(provider.call_audit),
        "elapsedMs": round((perf_counter() - started) * 1000, 3),
        "sanitized": True,
        "verdict": "FAIL",
        "createdAt": FIXED_TIME,
    }
    _write_json(f"deepseek_live_failures/{_case_prefix(case_index)}_attempt_{attempt:02d}.json", payload)
    _write_json("deepseek_live_failure.json", payload)


def _run_and_record_case(*, case_index: int, model: str, artifact_root: Path) -> tuple[dict[str, Any], DeepSeekVerificationRecord]:
    provider = DeepSeekProvider()
    started = perf_counter()
    prefix = _case_prefix(case_index)
    for suffix in (".json", "_verification.json", "_call_audit.json"):
        stale = EVIDENCE / "deepseek_live" / f"{prefix}{suffix}"
        if stale.exists():
            stale.unlink()
    try:
        live = _run_live_case(
            case_index=case_index,
            provider=provider,
            model=model,
            artifact_root=artifact_root,
        )
        audit = provider.call_audit
        _assert_provider_call_audit(audit)
        required_purposes = {"INTENT_EXTRACTION", "CAPABILITY_PLAN_SELECTION", "GROUNDED_INTERPRETATION"}
        if not required_purposes.issubset({item["purpose"] for item in audit}):
            raise RuntimeError("DEEPSEEK_REQUIRED_PURPOSES_MISSING")
        verification = _identified({
            "schemaVersion": "1.0",
            "verificationId": "pending",
            "verificationHash": "0" * 64,
            "provider": "deepseek",
            "baseUrl": DEEPSEEK_BASE_URL,
            "keySource": "DEEPSEEK_KEY",
            "configured": True,
            "model": model,
            "purposes": sorted({item["purpose"] for item in audit}),
            "realCallCount": len(audit),
            "otherRealProviderCalls": 0,
            "runIds": [live["runId"]],
            "outcomes": [
                f"CASE_{case_index + 1}_PLAN_READY",
                f"CASE_{case_index + 1}_RUNTIME_COMPLETED",
                f"CASE_{case_index + 1}_INTERPRETATION_READY",
            ],
            "tokenUsage": _aggregate_usage(audit),
            "sanitized": True,
            "verdict": "PASS",
            "createdAt": datetime.now(timezone.utc).isoformat(),
        })
        _write_json(f"deepseek_live/{prefix}.json", live)
        _write_json(f"deepseek_live/{prefix}_call_audit.json", list(audit))
        _write_json(f"deepseek_live/{prefix}_verification.json", verification)
        return live, verification
    except Exception as exc:
        _write_live_failure(case_index=case_index, model=model, provider=provider, started=started, exc=exc)
        raise


def _build_suite(model: str) -> DeepSeekVerificationSuite:
    refs: list[dict[str, Any]] = []
    usage_records: list[dict[str, Any]] = []
    for case_index in range(5):
        prefix = _case_prefix(case_index)
        live = json.loads((EVIDENCE / "deepseek_live" / f"{prefix}.json").read_text(encoding="utf-8"))
        verification = DeepSeekVerificationRecord.model_validate_json(
            (EVIDENCE / "deepseek_live" / f"{prefix}_verification.json").read_text(encoding="utf-8")
        )
        if verification.model != model or verification.runIds != [live["runId"]]:
            raise RuntimeError(f"DEEPSEEK_CASE_VERIFICATION_STALE:{case_index}")
        refs.append({
            "caseSpecId": case_specs()[case_index].caseSpecId,
            "runId": live["runId"],
            "verificationId": verification.verificationId,
            "verificationHash": verification.verificationHash,
            "realCallCount": verification.realCallCount,
            "verdict": "PASS",
        })
        usage_records.append(verification.tokenUsage.model_dump(mode="json"))
    refs.sort(key=lambda item: item["caseSpecId"])
    total_usage = {
        "promptTokens": sum(item["promptTokens"] for item in usage_records),
        "completionTokens": sum(item["completionTokens"] for item in usage_records),
        "totalTokens": sum(item["totalTokens"] for item in usage_records),
        "estimated": any(item["estimated"] for item in usage_records),
    }
    return _identified_suite({
        "schemaVersion": "1.0",
        "suiteId": "pending",
        "suiteHash": "0" * 64,
        "provider": "deepseek",
        "baseUrl": DEEPSEEK_BASE_URL,
        "keySource": "DEEPSEEK_KEY",
        "configured": True,
        "model": model,
        "cases": refs,
        "totalRealCallCount": sum(item["realCallCount"] for item in refs),
        "otherRealProviderCalls": 0,
        "tokenUsage": total_usage,
        "sanitized": True,
        "verdict": "PASS",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    })


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the five frozen Phase 10L-5 cases through real DeepSeek.")
    parser.add_argument("--case-index", action="append", type=int, choices=range(5))
    parser.add_argument("--finalize-only", action="store_true")
    args = parser.parse_args(argv)
    if args.finalize_only and args.case_index:
        parser.error("--finalize-only cannot be combined with --case-index")
    requested = [] if args.finalize_only else sorted(set(args.case_index if args.case_index is not None else range(5)))
    require_suite = args.case_index is None
    configured = bool(os.environ.get("DEEPSEEK_KEY"))
    model = os.environ.get("DEEPSEEK_MODEL") or DEEPSEEK_DEFAULT_MODEL
    if not configured:
        _write_json("deepseek_live_failure.json", {
            "configured": False,
            "errorCode": "DEEPSEEK_NOT_CONFIGURED",
            "keySource": "DEEPSEEK_KEY",
            "verdict": "BLOCKED",
        })
        print(json.dumps({"configured": False, "errorCode": "DEEPSEEK_NOT_CONFIGURED"}))
        return 2
    if model not in DEEPSEEK_ALLOWED_MODELS:
        _write_json("deepseek_live_failure.json", {
            "configured": True,
            "model": model,
            "errorCode": "DEEPSEEK_MODEL_NOT_ALLOWED",
            "verdict": "BLOCKED",
        })
        print(json.dumps({"configured": True, "errorCode": "DEEPSEEK_MODEL_NOT_ALLOWED"}))
        return 2

    started = perf_counter()
    failures: list[dict[str, Any]] = []
    passed: list[dict[str, Any]] = []
    with TemporaryDirectory(prefix="mdi-phase10l5-deepseek-") as directory:
        root = Path(directory)
        for case_index in requested:
            try:
                live, verification = _run_and_record_case(
                    case_index=case_index,
                    model=model,
                    artifact_root=root / _case_prefix(case_index),
                )
                passed.append({
                    "caseIndex": case_index,
                    "runId": live["runId"],
                    "realCallCount": verification.realCallCount,
                })
            except Exception as exc:
                error_code, _safe_details = _safe_exception_summary(exc)
                failures.append({
                    "caseIndex": case_index,
                    "errorCode": error_code,
                })
    if failures:
        print(json.dumps({
            "configured": True,
            "model": model,
            "passed": passed,
            "failures": failures,
            "elapsedMs": round((perf_counter() - started) * 1000, 3),
            "verdict": "FAIL",
        }))
        return 1
    if require_suite:
        try:
            suite = _build_suite(model)
        except Exception as exc:
            error_code, _safe_details = _safe_exception_summary(exc)
            print(json.dumps({"configured": True, "model": model, "errorCode": error_code, "verdict": "FAIL"}))
            return 1
        _write_json("deepseek_verification_suite.json", suite)
        _write_json("deepseek_verification.json", suite)
        _write_json("deepseek_real_verification.json", suite)
        latest_failure = EVIDENCE / "deepseek_live_failure.json"
        if latest_failure.exists():
            latest_failure.unlink()
        suite_id = suite.suiteId
        total_calls = suite.totalRealCallCount
    else:
        suite_id = None
        total_calls = sum(item["realCallCount"] for item in passed)
    print(json.dumps({
        "configured": True,
        "model": model,
        "passed": passed,
        "suiteId": suite_id,
        "totalRealCallCount": total_calls,
        "otherRealProviderCalls": 0,
        "elapsedMs": round((perf_counter() - started) * 1000, 3),
        "verdict": "PASS",
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
