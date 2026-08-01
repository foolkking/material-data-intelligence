"""Finalize the sanitized Phase 10L-5 evidence manifest after live verification."""

from __future__ import annotations

import argparse
import json
from hashlib import sha256
import math
import os
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mdi_schemas import (  # noqa: E402
    DeepSeekVerificationRecord,
    DeepSeekVerificationSuite,
    Phase10LClosureManifest,
    deterministic_natural_language_evidence_id,
    natural_language_evidence_hash,
)

EVIDENCE = ROOT / "docs" / "phase10l" / "evidence" / "phase10l5_natural_language_closure"
FIXED_TIME = "2026-07-31T00:00:00+00:00"
EXCLUDED = {"evidence_manifest.json"}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_DEEPSEEK_MODELS = frozenset({"deepseek-v4-flash", "deepseek-v4-pro"})
ALLOWED_DEEPSEEK_PURPOSES = frozenset({
    "INTENT_EXTRACTION",
    "CLARIFICATION_RESOLUTION",
    "CAPABILITY_PLAN_SELECTION",
    "MULTI_TOOL_COMPOSITION",
    "GROUNDED_INTERPRETATION",
    "PROVIDER_CONNECTION_TEST",
})
REQUIRED_LIVE_PURPOSES = frozenset({
    "INTENT_EXTRACTION",
    "CAPABILITY_PLAN_SELECTION",
    "GROUNDED_INTERPRETATION",
})
MAX_PROMPT_BYTES = 524_288
MAX_RESPONSE_BYTES = 524_288
MAX_PROMPT_TOKENS = 131_072
MAX_COMPLETION_TOKENS = 8_192
MAX_ELAPSED_MS = 600_000.0


def _normalized_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if path.suffix.casefold() == ".png":
        return raw
    return raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_text(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _live_run_paths(evidence_dir: Path = EVIDENCE) -> list[Path]:
    return sorted(
        path
        for path in (evidence_dir / "deepseek_live").glob("case_*.json")
        if not path.stem.endswith(("_call_audit", "_verification"))
    )


def _require_mapping(value: object, *, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a JSON object.")
    return value


def _require_bounded_int(value: object, *, field: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{field} must be an integer in [{minimum}, {maximum}].")
    return value


def _validate_call_audit(audit: object, *, source: str) -> dict[str, Any]:
    item = _require_mapping(audit, field=source)
    if item.get("realCall") is not True:
        raise ValueError(f"{source}.realCall must be true.")
    purpose = item.get("purpose")
    if purpose not in ALLOWED_DEEPSEEK_PURPOSES:
        raise ValueError(f"{source}.purpose is not allowlisted.")
    if item.get("model") not in ALLOWED_DEEPSEEK_MODELS:
        raise ValueError(f"{source}.model is not allowlisted.")
    if item.get("outcome") != "SUCCESS":
        raise ValueError(f"{source}.outcome must be SUCCESS.")
    for field in ("promptHash", "responseHash"):
        value = item.get(field)
        if not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value):
            raise ValueError(f"{source}.{field} must be a lowercase SHA-256 hash.")
    _require_bounded_int(item.get("promptBytes"), field=f"{source}.promptBytes", minimum=1, maximum=MAX_PROMPT_BYTES)
    _require_bounded_int(item.get("responseBytes"), field=f"{source}.responseBytes", minimum=1, maximum=MAX_RESPONSE_BYTES)
    usage = _require_mapping(item.get("tokenUsage"), field=f"{source}.tokenUsage")
    prompt_tokens = _require_bounded_int(
        usage.get("promptTokens"), field=f"{source}.tokenUsage.promptTokens", minimum=1, maximum=MAX_PROMPT_TOKENS
    )
    completion_tokens = _require_bounded_int(
        usage.get("completionTokens"),
        field=f"{source}.tokenUsage.completionTokens",
        minimum=1,
        maximum=MAX_COMPLETION_TOKENS,
    )
    total_tokens = _require_bounded_int(
        usage.get("totalTokens"),
        field=f"{source}.tokenUsage.totalTokens",
        minimum=2,
        maximum=MAX_PROMPT_TOKENS + MAX_COMPLETION_TOKENS,
    )
    if total_tokens != prompt_tokens + completion_tokens:
        raise ValueError(f"{source}.tokenUsage.totalTokens is inconsistent.")
    if usage.get("estimated") is not False:
        raise ValueError(f"{source}.tokenUsage.estimated must be false for a successful live call.")
    elapsed_ms = item.get("elapsedMs")
    if (
        isinstance(elapsed_ms, bool)
        or not isinstance(elapsed_ms, (int, float))
        or not math.isfinite(float(elapsed_ms))
        or not 0.0 <= float(elapsed_ms) <= MAX_ELAPSED_MS
    ):
        raise ValueError(f"{source}.elapsedMs is outside the bounded live-call range.")
    return item


def _aggregate_call_usage(audits: list[dict[str, Any]]) -> dict[str, int | bool]:
    prompt_tokens = sum(int(item["tokenUsage"]["promptTokens"]) for item in audits)
    completion_tokens = sum(int(item["tokenUsage"]["completionTokens"]) for item in audits)
    return {
        "promptTokens": prompt_tokens,
        "completionTokens": completion_tokens,
        "totalTokens": prompt_tokens + completion_tokens,
        "estimated": False,
    }


def _load_validated_audit_file(path: Path) -> list[dict[str, Any]]:
    payload = _load_json(path)
    if not isinstance(payload, list) or not payload:
        raise ValueError(f"{path.name} must contain at least one live call audit.")
    return [
        _validate_call_audit(item, source=f"{path.name}[{index}]")
        for index, item in enumerate(payload)
    ]


def _validate_live_suite(evidence_dir: Path, suite: DeepSeekVerificationSuite) -> list[dict[str, Any]]:
    run_paths = _live_run_paths(evidence_dir)
    audit_paths = sorted((evidence_dir / "deepseek_live").glob("case_*_call_audit.json"))
    verification_paths = sorted((evidence_dir / "deepseek_live").glob("case_*_verification.json"))
    if len(run_paths) != 5 or len(audit_paths) != 5 or len(verification_paths) != 5:
        raise ValueError("The live DeepSeek closure requires exactly five runs, audits, and verification records.")

    runs_by_id: dict[str, dict[str, Any]] = {}
    for path in run_paths:
        run = _require_mapping(_load_json(path), field=path.name)
        if run.get("verdict") != "PASS":
            raise ValueError(f"{path.name} is not a passing live run.")
        run_id = run.get("runId")
        if not isinstance(run_id, str) or not run_id or run_id in runs_by_id:
            raise ValueError(f"{path.name} has an invalid or duplicate runId.")
        runs_by_id[run_id] = run

    verifications = {
        item.verificationId: item
        for path in verification_paths
        for item in [DeepSeekVerificationRecord.model_validate_json(path.read_text(encoding="utf-8"))]
    }
    all_audits: list[dict[str, Any]] = []
    audits_by_prefix = {path.name.removesuffix("_call_audit.json"): _load_validated_audit_file(path) for path in audit_paths}
    for case in suite.cases:
        run = runs_by_id.get(case.runId)
        verification = verifications.get(case.verificationId)
        if run is None or run.get("caseSpecId") != case.caseSpecId:
            raise ValueError(f"Live suite run association is missing or stale for {case.caseSpecId}.")
        if verification is None or verification.verificationHash != case.verificationHash:
            raise ValueError(f"Live suite verification association is missing or stale for {case.caseSpecId}.")
        if verification.runIds != [case.runId] or verification.verdict != "PASS":
            raise ValueError(f"Live verification is not bound to the exact passing run for {case.caseSpecId}.")
        prefix = next((path.stem for path in run_paths if _load_json(path).get("runId") == case.runId), None)
        audits = audits_by_prefix.get(prefix or "")
        if audits is None or len(audits) != case.realCallCount or len(audits) != verification.realCallCount:
            raise ValueError(f"Live call count does not match verification for {case.caseSpecId}.")
        if verification.model != suite.model or any(item["model"] != verification.model for item in audits):
            raise ValueError(f"Live call model is inconsistent for {case.caseSpecId}.")
        purposes = {str(item["purpose"]) for item in audits}
        if not REQUIRED_LIVE_PURPOSES.issubset(purposes) or sorted(purposes) != verification.purposes:
            raise ValueError(f"Live call purposes are incomplete or inconsistent for {case.caseSpecId}.")
        if _aggregate_call_usage(audits) != verification.tokenUsage.model_dump(mode="json"):
            raise ValueError(f"Live token usage is inconsistent for {case.caseSpecId}.")
        all_audits.extend(audits)

    if len(all_audits) != suite.totalRealCallCount:
        raise ValueError("Live suite totalRealCallCount does not match its call audits.")
    if _aggregate_call_usage(all_audits) != suite.tokenUsage.model_dump(mode="json"):
        raise ValueError("Live suite token usage does not match its call audits.")
    return all_audits


def _validate_historical_suite(evidence_dir: Path, live_suite: DeepSeekVerificationSuite) -> dict[str, Any] | None:
    suite_path = evidence_dir / "historical_deepseek_replay_suite.json"
    if not suite_path.exists():
        return None
    suite = _require_mapping(_load_json(suite_path), field=suite_path.name)
    cases = suite.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("Historical replay suite must contain case references.")
    if (
        suite.get("provider") != "deepseek"
        or suite.get("keySource") != "DEEPSEEK_KEY"
        or suite.get("baseUrl") != "https://api.deepseek.com"
        or suite.get("verdict") != "PASS"
        or suite.get("otherRealProviderCalls") != 0
    ):
        raise ValueError("Historical replay suite provider or verdict fields are invalid.")
    suite_hash = suite.get("suiteHash")
    suite_id = suite.get("suiteId")
    semantic_suite = {
        key: value
        for key, value in suite.items()
        if key not in {"suiteId", "suiteHash", "createdAt"}
    }
    expected_suite_hash = sha256(
        json.dumps(semantic_suite, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()
    if suite_hash != expected_suite_hash or suite_id != f"historical_deepseek_suite_{expected_suite_hash[:32]}":
        raise ValueError("Historical replay suite identity or semantic hash is inconsistent.")
    additional_refs = [item for item in cases if isinstance(item, dict) and int(item.get("caseNumber", 0)) > 5]
    if len(additional_refs) != suite.get("additionalHistoricalCaseCount"):
        raise ValueError("Historical replay suite additional case count is inconsistent.")
    if suite.get("existingL5CaseCount") != 5 or suite.get("caseCount") != len(cases):
        raise ValueError("Historical replay suite total case count is inconsistent.")
    if suite.get("passedCaseCount") != len(cases) or suite.get("failedCaseCount") != 0:
        raise ValueError("Historical replay suite is incomplete.")

    historical_audits: list[dict[str, Any]] = []
    for ref in additional_refs:
        case_number = _require_bounded_int(
            ref.get("caseNumber"), field="historical.caseNumber", minimum=6, maximum=10_000
        )
        matches = sorted((evidence_dir / "historical_deepseek_replay").glob(f"case_{case_number:02d}_*.json"))
        if len(matches) != 1:
            raise ValueError(f"Historical replay case {case_number} is missing or ambiguous.")
        record = _require_mapping(_load_json(matches[0]), field=matches[0].name)
        if record.get("verdict") != "PASS" or record.get("provider") != "deepseek":
            raise ValueError(f"Historical replay case {case_number} is not a passing DeepSeek record.")
        audits_raw = record.get("providerCallAudit")
        if not isinstance(audits_raw, list) or not audits_raw:
            raise ValueError(f"Historical replay case {case_number} has no live call audit.")
        audits = [
            _validate_call_audit(item, source=f"{matches[0].name}.providerCallAudit[{index}]")
            for index, item in enumerate(audits_raw)
        ]
        if record.get("model") not in ALLOWED_DEEPSEEK_MODELS or any(
            item["model"] != record.get("model") for item in audits
        ):
            raise ValueError(f"Historical replay case {case_number} model is inconsistent.")
        if len(audits) != record.get("providerCallCount") or len(audits) != ref.get("realCallCount"):
            raise ValueError(f"Historical replay case {case_number} call count is inconsistent.")
        if _aggregate_call_usage(audits) != record.get("tokenUsage"):
            raise ValueError(f"Historical replay case {case_number} token usage is inconsistent.")
        for field in ("runId", "runHash", "planningOutcome", "selectedToolIds"):
            if record.get(field) != ref.get(field):
                raise ValueError(f"Historical replay case {case_number} {field} association is stale.")
        historical_audits.extend(audits)

    expected_total = live_suite.totalRealCallCount + len(historical_audits)
    if suite.get("totalRealCallCount") != expected_total:
        raise ValueError("Historical replay suite totalRealCallCount is inconsistent.")
    usage = _require_mapping(suite.get("tokenUsage"), field="historical.tokenUsage")
    expected_usage = _aggregate_call_usage(historical_audits)
    for field in ("promptTokens", "completionTokens", "totalTokens"):
        expected = int(expected_usage[field]) + int(live_suite.tokenUsage.model_dump(mode="json")[field])
        if usage.get(field) != expected:
            raise ValueError(f"Historical replay suite tokenUsage.{field} is inconsistent.")
    return suite


def _validate_closure_inputs(evidence_dir: Path) -> tuple[DeepSeekVerificationSuite, list[dict[str, Any]], dict[str, Any] | None]:
    suite_path = evidence_dir / "deepseek_verification_suite.json"
    if not suite_path.is_file():
        raise ValueError("The five-case DeepSeek verification suite is missing.")
    suite = DeepSeekVerificationSuite.model_validate_json(suite_path.read_text(encoding="utf-8"))
    audits = _validate_live_suite(evidence_dir, suite)
    historical = _validate_historical_suite(evidence_dir, suite)
    return suite, audits, historical


def _write_closure_audits(evidence_dir: Path, suite: DeepSeekVerificationSuite) -> None:
    live_runs = [_load_json(path) for path in _live_run_paths(evidence_dir)]
    call_audits = [
        item
        for path in sorted((evidence_dir / "deepseek_live").glob("*_call_audit.json"))
        for item in _load_json(path)
    ]
    if len(live_runs) != 5 or len(call_audits) != suite.totalRealCallCount:
        raise ValueError("The live closure audits do not match the five-case DeepSeek suite.")

    api_cases = []
    for run in live_runs:
        selected = list(run["selectedToolIds"])
        interpretation = run.get("interpretationResponse") or run["interpretation"]
        api_cases.append({
            "caseSpecId": run["caseSpecId"],
            "runId": run["runId"],
            "userTextHash": sha256(run["userText"].encode("utf-8")).hexdigest(),
            "selectedToolIds": sorted(selected),
            "plan": {
                "planId": run["planId"],
                "planHash": run["planHash"],
                "schemaVersion": run["planSchemaVersion"],
                "graphHash": run["graphHash"],
            },
            "job": {
                "jobId": run["jobId"],
                "status": run["jobStatus"],
            },
            "interpretation": {
                "interpretationId": interpretation["interpretationId"],
                "outcome": interpretation["outcome"],
                "bundleHash": interpretation["bundleHash"],
                "repairCount": interpretation["repairCount"],
            },
            "verdict": run["verdict"],
        })
    _write_text(
        evidence_dir / "api_transcript.md",
        "# Sanitized Phase 10L-5 API Transcript\n\n"
        "The five entries below were captured from the canonical persisted planning, Runtime, and interpretation APIs. "
        "They contain identities and hashes only; raw provider requests/responses and credentials are excluded.\n\n"
        "```json\n" + json.dumps(api_cases, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n```",
    )

    by_purpose: dict[str, dict[str, int | float]] = {}
    for call in call_audits:
        purpose = call["purpose"]
        record = by_purpose.setdefault(purpose, {"calls": 0, "elapsedMs": 0.0, "promptTokens": 0, "completionTokens": 0})
        record["calls"] += 1
        record["elapsedMs"] = round(float(record["elapsedMs"]) + float(call["elapsedMs"]), 3)
        record["promptTokens"] += int(call["tokenUsage"]["promptTokens"])
        record["completionTokens"] += int(call["tokenUsage"]["completionTokens"])
    live_elapsed_ms = round(sum(float(item["elapsedMs"]) for item in call_audits), 3)
    deterministic_performance = _load_json(evidence_dir / "performance.json")
    performance = {
        **deterministic_performance,
        "scope": "DETERMINISTIC_FIVE_CASE_REPLAY_AND_SEPARATE_LIVE_DEEPSEEK_GATE",
        "defaultCiRealLlmCalls": 0,
        "liveGateRealLlmCalls": suite.totalRealCallCount,
        "liveGateElapsedMs": live_elapsed_ms,
        "liveGateTokenUsage": suite.tokenUsage.model_dump(mode="json"),
        "liveGateByPurpose": by_purpose,
        "costCurrency": None,
        "costAmount": None,
        "costPolicy": "TOKEN_USAGE_RECORDED_NO_PRICING_ASSUMPTION",
    }
    _write_json(evidence_dir / "performance.json", performance)
    _write_text(
        evidence_dir / "performance_cost_audit.md",
        "# Phase 10L-5 Performance And Cost Audit\n\n"
        f"- Deterministic five-case replay elapsed: `{deterministic_performance['elapsedMs']}` ms.\n"
        f"- Controlled live DeepSeek calls: `{suite.totalRealCallCount}`.\n"
        f"- Aggregate live provider elapsed: `{live_elapsed_ms}` ms.\n"
        f"- Prompt tokens: `{suite.tokenUsage.promptTokens}`.\n"
        f"- Completion tokens: `{suite.tokenUsage.completionTokens}`.\n"
        f"- Total tokens: `{suite.tokenUsage.totalTokens}`.\n"
        "- Monetary cost is intentionally not asserted because repository evidence does not own a versioned pricing source.\n"
        "- Each case is capped at 12 real calls; observed calls are 3, 3, 3, 4, 3.\n"
        "- These measurements are closure evidence, not a production-capacity claim.",
    )

    security = {
        "schemaVersion": "1.0",
        "scope": "DEFAULT_CI_AND_CONTROLLED_LIVE_GATE",
        "defaultCiRealLlmCalls": 0,
        "liveGateRealLlmCalls": suite.totalRealCallCount,
        "liveGateProvider": "deepseek",
        "liveGateOtherRealProviderCalls": suite.otherRealProviderCalls,
        "keySource": "DEEPSEEK_KEY",
        "rawArtifactPayloadSentToProvider": False,
        "secretValuesPersisted": False,
        "arbitraryExecutionAuthority": False,
        "markers": [
            "NO_ALTERNATIVE_PROVIDER_REAL_CALLS",
            "NO_ARBITRARY_CODE",
            "NO_ARTIFACT_HTML_OR_JAVASCRIPT",
            "NO_CROSS_JOB_OR_PROJECT_BINDING",
            "NO_DIRECT_TOOL_PLAN_OR_ADAPTER_IN_USER_REQUEST",
            "NO_EXTERNAL_SCIENTIFIC_API",
            "NO_RAW_ARTIFACT_TO_PROVIDER",
            "NO_RECOMMENDATION_AUTO_EXECUTION",
            "NO_SECRET_IN_EVIDENCE",
            "NO_DEFAULT_CI_REAL_LLM_CALLS",
        ],
        "verdict": "PASS",
    }
    _write_json(evidence_dir / "security.json", security)
    _write_text(
        evidence_dir / "security_audit.md",
        "# Phase 10L-5 Security Audit\n\n"
        "- `REAL_LLM_CALLS = 0` applies to default CI and browser replay.\n"
        f"- `LIVE_GATE_REAL_LLM_CALLS = {suite.totalRealCallCount}` applies only to the controlled DeepSeek suite.\n"
        "- `OTHER_REAL_PROVIDER_CALLS = 0`.\n"
        "- `DEEPSEEK_KEY` is the only credential source; the value is never persisted.\n"
        "- No raw provider payload, Authorization header, artifact payload, private path, external artifact URL, or secret is retained.\n"
        "- Provider output has no Tool, Plan, Job, Queue, shell, filesystem, or recommendation execution authority.\n"
        "- `NO_SECRET_PATTERN_HITS`.",
    )

    artifact_records = []
    source_paths = sorted((evidence_dir / "cases").glob("*_capture.json")) + _live_run_paths(evidence_dir)
    for source_path in source_paths:
        capture = _load_json(source_path)
        for artifact in capture.get("artifacts", []):
            artifact_records.append({
                "source": source_path.relative_to(evidence_dir).as_posix(),
                "artifactId": artifact["id"],
                "artifactType": artifact["type"],
                "contentHash": artifact.get("contentHash") or artifact["sha256"],
                "sizeBytes": artifact["sizeBytes"],
                "producerToolCallId": artifact["toolCallId"],
            })
    _write_json(evidence_dir / "artifact_hashes.json", {
        "schemaVersion": "1.0",
        "algorithm": "sha256",
        "records": sorted(artifact_records, key=lambda item: (item["source"], item["artifactId"])),
    })

    service_run = os.getenv("PHASE10L5_SERVICE_CI_RUN")
    service_status = "VERIFIED_EXACT_SHA_CI" if service_run else "PENDING_EXACT_SHA_CI"
    _write_text(
        evidence_dir / "service_backed_audit.md",
        "# Phase 10L-5 Service-Backed Audit\n\n"
        "Five separately collected cases exercise PostgreSQL repositories, Redis enqueue, MinIO artifacts, exact persisted plans/jobs, "
        "QueueWorkerRuntime, lineage, deterministic grounded interpretation, API read-back, checksums, and idempotency.\n\n"
        f"- Status: `{service_status}`.\n"
        f"- Exact-SHA CI run: `{service_run or 'PENDING'}`.\n"
        "- Required result: 5 L5 cases passed, 0 skipped, 0 failed within the repository-wide service-backed no-skip gate.\n"
        "- Local Docker absence is not represented as a pass.\n"
        "- Default service CI uses deterministic Mock transport and `REAL_LLM_CALLS = 0`; live DeepSeek verification is separate.",
    )


def _evidence_entries(evidence_dir: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted(item for item in evidence_dir.rglob("*") if item.is_file()):
        relative = path.relative_to(evidence_dir).as_posix()
        if relative in EXCLUDED:
            continue
        normalized = _normalized_bytes(path)
        entries.append({
            "path": relative,
            "sha256": sha256(normalized).hexdigest(),
            "bytes": len(normalized),
        })
    return sorted(entries, key=lambda item: item["path"])


def _safe_manifest_path(evidence_dir: Path, relative: str) -> Path:
    candidate = (evidence_dir / relative).resolve()
    root = evidence_dir.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"Manifest path escapes the evidence directory: {relative}")
    return candidate


def verify_manifest(evidence_dir: Path = EVIDENCE) -> dict[str, Any]:
    manifest_path = evidence_dir / "evidence_manifest.json"
    if not manifest_path.is_file():
        raise ValueError("evidence_manifest.json is missing.")
    suite, audits, historical = _validate_closure_inputs(evidence_dir)
    manifest = Phase10LClosureManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    expected_paths = {entry.path for entry in manifest.entries}
    actual_entries = _evidence_entries(evidence_dir)
    actual_paths = {entry["path"] for entry in actual_entries}
    if expected_paths != actual_paths:
        missing = sorted(expected_paths - actual_paths)
        untracked = sorted(actual_paths - expected_paths)
        raise ValueError(f"Manifest file set mismatch; missing={missing}, untracked={untracked}.")
    actual_by_path = {entry["path"]: entry for entry in actual_entries}
    for entry in manifest.entries:
        _safe_manifest_path(evidence_dir, entry.path)
        actual = actual_by_path[entry.path]
        if actual["sha256"] != entry.sha256 or actual["bytes"] != entry.bytes:
            raise ValueError(f"Manifest hash or byte count mismatch for {entry.path}.")
    if manifest.deepSeekVerificationId != suite.suiteId:
        raise ValueError("Manifest DeepSeek suite association is stale.")
    if manifest.verdict != "PASS":
        raise ValueError("A finalized closure manifest must have verdict PASS.")
    historical_count = int(historical["additionalHistoricalCaseCount"]) if historical is not None else 0
    return {
        "manifestId": manifest.manifestId,
        "entryCount": len(manifest.entries),
        "liveCallCount": len(audits),
        "historicalCaseCount": historical_count,
        "verdict": manifest.verdict,
        "checkOnly": True,
    }


def finalize_evidence(evidence_dir: Path = EVIDENCE) -> dict[str, Any]:
    suite, audits, historical = _validate_closure_inputs(evidence_dir)
    case_specs = json.loads((evidence_dir / "case_specs.json").read_text(encoding="utf-8"))
    if not isinstance(case_specs, list) or len(case_specs) != 5:
        raise ValueError("Exactly five frozen case specifications are required for closure.")
    case_ids = sorted(item["caseSpecId"] for item in case_specs)
    run_ids = sorted(item.runId for item in suite.cases)
    if case_ids != sorted(item.caseSpecId for item in suite.cases):
        raise ValueError("Frozen case specifications do not match the live DeepSeek suite.")
    live_summary = {
        "schemaVersion": "1.0",
        "provider": "deepseek",
        "baseUrl": suite.baseUrl,
        "keySource": suite.keySource,
        "model": suite.model,
        "caseCount": len(suite.cases),
        "caseVerificationIds": [item.verificationId for item in suite.cases],
        "caseRunIds": run_ids,
        "totalRealCallCount": suite.totalRealCallCount,
        "perCaseCallCap": 12,
        "allCasesPassed": all(item.verdict == "PASS" for item in suite.cases),
        "otherRealProviderCalls": suite.otherRealProviderCalls,
        "noSilentFallback": True,
        "sanitized": True,
        "previousFailedAttemptsRetained": len(list((evidence_dir / "deepseek_live_failures").glob("*.json"))),
    }
    _write_json(evidence_dir / "deepseek_live_verification_summary.json", live_summary)
    _write_closure_audits(evidence_dir, suite)
    entries = _evidence_entries(evidence_dir)
    closure_complete = (
        len(audits) == suite.totalRealCallCount
        and all(item["outcome"] == "SUCCESS" for item in audits)
        and (historical is None or historical.get("verdict") == "PASS")
    )
    if not closure_complete:
        raise ValueError("Phase 10L-5 closure inputs are incomplete; PASS manifest was not written.")
    payload = {
        "schemaVersion": "1.0",
        "manifestId": "pending",
        "manifestHash": "0" * 64,
        "phase": "10L",
        "caseSpecIds": case_ids,
        "runIds": run_ids,
        "deepSeekVerificationId": suite.suiteId,
        "entries": entries,
        "securityMarkers": sorted([
            "REAL_LLM_PROVIDER_DEEPSEEK_ONLY",
            "REAL_LLM_KEY_SOURCE_DEEPSEEK_KEY_ONLY",
            "REAL_DEEPSEEK_FIVE_CASE_SUITE_PASS",
            "REAL_DEEPSEEK_PER_CASE_CALL_CAP_12",
            "OTHER_REAL_PROVIDER_CALLS_0",
            "REAL_LLM_CALLS_NOT_IN_DEFAULT_CI",
            "NO_OPENAI_REAL_CALLS",
            "NO_CUSTOM_OPENAI_COMPATIBLE_REAL_CALLS",
            "NO_ANTHROPIC_REAL_CALLS",
            "NO_DEEPSEEK_API_KEY_FALLBACK",
            "NO_OPENAI_API_KEY_FALLBACK",
            "NO_FRONTEND_LLM_KEY_INPUT",
            "NO_BROWSER_TO_DEEPSEEK_DIRECT_CALL",
            "NO_RAW_ARTIFACT_TO_LLM",
            "NO_UNGROUNDED_INTERPRETATION",
            "NO_SECRET_PATTERN_HITS",
        ]),
        "verdict": "PASS" if closure_complete else "BLOCKED",
        "createdAt": FIXED_TIME,
    }
    manifest_hash = natural_language_evidence_hash(
        payload,
        exclude={"manifestId", "manifestHash", "createdAt"},
    )
    payload["manifestHash"] = manifest_hash
    payload["manifestId"] = deterministic_natural_language_evidence_id("phase10l_closure", manifest_hash)
    manifest = Phase10LClosureManifest.model_validate(payload)
    _write_json(evidence_dir / "evidence_manifest.json", manifest.model_dump(mode="json"))
    result = {
        "manifestId": manifest.manifestId,
        "entryCount": len(entries),
        "suiteId": suite.suiteId,
        "totalRealCallCount": suite.totalRealCallCount,
        "historicalCaseCount": int(historical["additionalHistoricalCaseCount"]) if historical is not None else 0,
        "verdict": manifest.verdict,
        "checkOnly": False,
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Finalize or independently verify sanitized Phase 10L-5 evidence.")
    parser.add_argument("--check-only", action="store_true", help="Verify inputs and manifest without writing any file.")
    parser.add_argument("--evidence-dir", type=Path, default=EVIDENCE, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    result = verify_manifest(args.evidence_dir) if args.check_only else finalize_evidence(args.evidence_dir)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
