from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from mdi_schemas import (
    DeepSeekVerificationRecord,
    DeepSeekVerificationSuite,
    DesiredOutput,
    EvidenceExecutionRef,
    EvidenceIntentRecord,
    EvidencePlanRecord,
    EvidenceProviderRecord,
    EvidenceRecordRef,
    EvidenceResourceRef,
    NaturalLanguageEvidenceCase,
    NaturalLanguageEvidenceRun,
    Phase10LClosureManifest,
    deterministic_natural_language_evidence_id,
    natural_language_evidence_hash,
    strict_natural_language_evidence_json_loads,
)
from mdi_llm import AnalysisIntentRequest, DeterministicAnalysisIntentBuilder
from tests.test_phase10l1_analysis_intent import _profile
from scripts.generate_phase10l5_natural_language_closure_evidence import (
    OFFLINE_MANAGED_FILES,
    _clean_offline_outputs,
    _run_case,
    case_specs,
    main as generate_evidence_main,
)
from scripts.finalize_phase10l5_evidence import (
    _validate_call_audit,
    finalize_evidence,
    main as finalize_evidence_main,
)


ROOT = Path(__file__).resolve().parents[1]
FROZEN_PROMPTS = [
    "分析这批材料的组成分布和异常样本。",
    "看看这个晶体结构是否合理。",
    "分析这个机器学习模型表现。",
    "分析这个 phonon calculation。",
    "查看这个 charge density，并解释主要特征。",
]


def _identified(payload: dict, *, prefix: str, id_field: str, hash_field: str, exclude: set[str] | None = None) -> dict:
    excluded = {id_field, hash_field, *(exclude or set())}
    semantic_hash = natural_language_evidence_hash(payload, exclude=excluded)
    return {
        **payload,
        id_field: deterministic_natural_language_evidence_id(prefix, semantic_hash),
        hash_field: semantic_hash,
    }


def _case() -> NaturalLanguageEvidenceCase:
    payload = {
        "schemaVersion": "1.0",
        "caseSpecId": "pending",
        "caseSpecHash": "0" * 64,
        "title": "Dataset composition",
        "userText": "分析这批材料的组成分布和异常样本。",
        "requiredCapabilityNeeds": ["composition_data", "tabular_data"],
        "acceptableToolIds": ["dataset.materials_explorer"],
        "requiredOutputs": ["linked_samples", "summary"],
        "forbiddenFallbacks": ["ml.basic_metrics", "structure.summary"],
        "requiresClarification": False,
        "requiresDependencyPlan": False,
    }
    return NaturalLanguageEvidenceCase.model_validate(
        _identified(payload, prefix="caseSpec", id_field="caseSpecId", hash_field="caseSpecHash")
    )


def _run(case: NaturalLanguageEvidenceCase, *, ready: bool = True) -> NaturalLanguageEvidenceRun:
    payload = {
        "schemaVersion": "1.0",
        "runId": "pending",
        "runHash": "0" * 64,
        "caseSpecId": case.caseSpecId,
        "caseSpecHash": case.caseSpecHash,
        "userText": case.userText,
        "resourceManifest": [
            {"objectId": "table_1", "objectType": "DataFrame", "objectHash": "a" * 64, "kind": "table"}
        ],
        "provider": {
            "mode": "DETERMINISTIC",
            "provider": "deterministic_mock",
            "model": "bounded-rules-v1",
            "purposes": [],
            "keySource": "NONE",
            "realCallCount": 0,
            "promptHashes": [],
            "responseHashes": [],
        },
        "profile": {"recordId": "profile_1", "recordHash": "b" * 64, "schemaVersion": "2.0"},
        "intent": {
            "intentId": "intent_1",
            "intentHash": "c" * 64,
            "outcome": "READY" if ready else "NEEDS_CLARIFICATION",
            "clarificationRound": 0,
        },
        "eligibility": {"recordId": "resolution_1", "recordHash": "d" * 64, "schemaVersion": "1.0"} if ready else None,
        "selectedTools": [{"toolId": "dataset.materials_explorer", "toolVersion": "0.1.0", "bindingHash": "e" * 64}] if ready else [],
        "plan": {"planId": "plan_1", "planHash": "f" * 64, "schemaVersion": "0.1", "graphHash": None} if ready else None,
        "job": {"recordId": "job_1", "state": "completed", "semanticHash": None} if ready else None,
        "toolCalls": [{"recordId": "call_1", "state": "completed", "semanticHash": None}] if ready else [],
        "artifacts": [
            {
                "artifactId": "artifact_1",
                "artifactType": "materials_explorer_summary_json",
                "contentHash": "1" * 64,
                "sizeBytes": 128,
                "producerToolCallId": "call_1",
            }
        ] if ready else [],
        "executionOutcome": "ALL_SUCCEEDED" if ready else "NOT_EXECUTED",
        "lineage": [],
        "evidenceBundle": {"recordId": "bundle_1", "recordHash": "2" * 64, "schemaVersion": "1.0"} if ready else None,
        "interpretation": {"recordId": "interpretation_1", "recordHash": "3" * 64, "schemaVersion": "1.0"} if ready else None,
        "claimEvidenceLinks": [{"claimId": "claim_1", "evidenceItemIds": ["evidence_1"]}] if ready else [],
        "apiRefs": ["api/case1.json"],
        "browserRefs": [],
        "securityMarkers": ["NO_SECRET_PATTERN_HITS"],
        "tokenUsage": {"promptTokens": 0, "completionTokens": 0, "totalTokens": 0, "estimated": False},
        "elapsedMs": 1.25,
        "verdict": "PASS" if ready else "BLOCKED",
        "createdAt": "2026-07-31T00:00:00Z",
    }
    return NaturalLanguageEvidenceRun.model_validate(
        _identified(
            payload,
            prefix="run",
            id_field="runId",
            hash_field="runHash",
            exclude={"elapsedMs", "createdAt"},
        )
    )


def test_case_and_run_have_deterministic_unicode_identity() -> None:
    case = _case()
    replay = _case()
    assert case.caseSpecId == replay.caseSpecId
    assert case.caseSpecHash == replay.caseSpecHash
    run = _run(case)
    replay_run = _run(replay)
    assert run.runId == replay_run.runId
    assert run.runHash == replay_run.runHash
    assert run.intent.outcome == "READY"


def test_non_ready_run_cannot_hide_plan_job_or_tool_execution() -> None:
    run = _run(_case(), ready=False)
    payload = run.model_dump(mode="json")
    payload["plan"] = {"planId": "plan_bad", "planHash": "f" * 64, "schemaVersion": "0.1", "graphHash": None}
    payload = _identified(
        payload,
        prefix="run",
        id_field="runId",
        hash_field="runHash",
        exclude={"elapsedMs", "createdAt"},
    )
    with pytest.raises(ValidationError, match="Non-READY"):
        NaturalLanguageEvidenceRun.model_validate(payload)


@pytest.mark.parametrize(
    ("field", "replacement", "message"),
    [
        ("artifacts", [], "artifact"),
        ("toolCalls", [], "ToolCall"),
        ("evidenceBundle", None, "grounded evidence"),
        ("interpretation", None, "grounded evidence"),
        ("claimEvidenceLinks", [], "grounded evidence"),
        ("apiRefs", [], "API references"),
        ("executionOutcome", "NOT_EXECUTED", "terminal execution"),
    ],
)
def test_passing_run_requires_complete_execution_and_grounding(
    field: str,
    replacement: object,
    message: str,
) -> None:
    payload = _run(_case()).model_dump(mode="json")
    payload[field] = replacement
    payload = _identified(
        payload,
        prefix="run",
        id_field="runId",
        hash_field="runHash",
        exclude={"elapsedMs", "createdAt"},
    )
    with pytest.raises(ValidationError, match=message):
        NaturalLanguageEvidenceRun.model_validate(payload)


def test_contracts_reject_unknown_fields_duplicate_keys_and_nonfinite_values() -> None:
    payload = _case().model_dump(mode="json")
    payload["unknown"] = True
    with pytest.raises(ValidationError):
        NaturalLanguageEvidenceCase.model_validate(payload)
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        strict_natural_language_evidence_json_loads('{"schemaVersion":"1.0","schemaVersion":"1.0"}')
    with pytest.raises(ValueError, match="Non-finite"):
        strict_natural_language_evidence_json_loads('{"value":NaN}')


def test_deepseek_verification_requires_three_real_calls_for_pass() -> None:
    payload = {
        "schemaVersion": "1.0",
        "verificationId": "pending",
        "verificationHash": "0" * 64,
        "provider": "deepseek",
        "baseUrl": "https://api.deepseek.com",
        "keySource": "DEEPSEEK_KEY",
        "configured": True,
        "model": "deepseek-v4-flash",
        "purposes": ["CAPABILITY_PLAN_SELECTION", "GROUNDED_INTERPRETATION"],
        "realCallCount": 2,
        "otherRealProviderCalls": 0,
        "runIds": [],
        "outcomes": ["PLAN_READY"],
        "tokenUsage": {"promptTokens": 0, "completionTokens": 0, "totalTokens": 0, "estimated": True},
        "sanitized": True,
        "verdict": "PASS",
        "createdAt": "2026-07-31T00:00:00Z",
    }
    identified = _identified(
        payload,
        prefix="deepseek_verification",
        id_field="verificationId",
        hash_field="verificationHash",
        exclude={"createdAt"},
    )
    with pytest.raises(ValidationError, match="at least three real calls"):
        DeepSeekVerificationRecord.model_validate(identified)


def test_checked_in_json_schema_and_typescript_surface_match() -> None:
    checked_in = json.loads((ROOT / "packages/schemas/json/natural-language-evidence-v1.schema.json").read_text(encoding="utf-8"))
    assert checked_in == {
        "naturalLanguageEvidenceCase": NaturalLanguageEvidenceCase.model_json_schema(),
        "naturalLanguageEvidenceRun": NaturalLanguageEvidenceRun.model_json_schema(),
        "deepSeekVerificationRecord": DeepSeekVerificationRecord.model_json_schema(),
        "deepSeekVerificationSuite": DeepSeekVerificationSuite.model_json_schema(),
        "phase10LClosureManifest": Phase10LClosureManifest.model_json_schema(),
    }
    source = (ROOT / "packages/schemas/src/index.ts").read_text(encoding="utf-8")
    for name in (
        "NaturalLanguageEvidenceCase",
        "NaturalLanguageEvidenceRun",
        "DeepSeekVerificationRecord",
        "DeepSeekVerificationSuite",
        "Phase10LClosureManifest",
    ):
        assert f"export type {name}" in source


def test_generic_ml_goal_uses_the_only_exact_profile_science_kind() -> None:
    profile = _profile(targets=("formation_energy",), uncertainty=False)
    intent = DeterministicAnalysisIntentBuilder().build(
        AnalysisIntentRequest(
            raw_goal="分析这个机器学习模型表现。",
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            selected_resource_ids=("table_1",),
        ),
        profile=profile,
    )
    assert intent.outcome.value == "READY"
    assert [item.value for item in intent.scientificIntents] == ["ml_regression_evaluation"]
    assert [item.value for item in intent.requiredCapabilityNeeds] == ["regression_semantics"]


def test_structure_reasonableness_goal_requests_groundable_facts_not_a_viewer() -> None:
    profile = _profile(
        resources=[{
            "objectId": "structure_exact",
            "objectType": "Structure",
            "objectHash": "e" * 64,
            "kind": "structure",
            "capabilities": ["structure"],
        }],
        targets=(),
        uncertainty=False,
    )
    intent = DeterministicAnalysisIntentBuilder().build(
        AnalysisIntentRequest(
            raw_goal="看看这个结构是否合理。",
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            selected_resource_ids=("structure_exact",),
        ),
        profile=profile,
    )
    assert intent.outcome.value == "READY"
    assert [item.value for item in intent.scientificIntents] == ["structure_analysis"]
    assert DesiredOutput.three_dimensional_view not in intent.desiredOutputs


def test_frozen_case_specs_preserve_exact_natural_language_prompts() -> None:
    assert [item.userText for item in case_specs()] == FROZEN_PROMPTS


def test_offline_cleanup_preserves_live_historical_browser_and_unknown_evidence(tmp_path: Path) -> None:
    for relative in OFFLINE_MANAGED_FILES:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("stale offline output", encoding="utf-8")
    preserved = [
        tmp_path / "deepseek_live" / "case_1.json",
        tmp_path / "historical_deepseek_replay" / "case_6.json",
        tmp_path / "browser" / "chromium.json",
        tmp_path / "screenshots" / "mobile.png",
        tmp_path / "operator_note.txt",
        tmp_path / "cases" / "manual_fixture.json",
    ]
    for target in preserved:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"preserve-me")

    _clean_offline_outputs(tmp_path)

    assert all(not (tmp_path / relative).exists() for relative in OFFLINE_MANAGED_FILES)
    assert all(target.read_bytes() == b"preserve-me" for target in preserved)


def test_generator_help_is_non_destructive(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    sentinels = [
        tmp_path / "deepseek_live" / "verification.json",
        tmp_path / "historical_deepseek_replay" / "matrix.json",
        tmp_path / "browser" / "dom_snapshot.json",
    ]
    for sentinel in sentinels:
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        sentinel.write_text("unchanged", encoding="utf-8")

    with pytest.raises(SystemExit) as raised:
        generate_evidence_main(["--output-dir", str(tmp_path), "--help"])

    assert raised.value.code == 0
    assert "Generate deterministic offline Phase 10L-5 evidence" in capsys.readouterr().out
    assert all(sentinel.read_text(encoding="utf-8") == "unchanged" for sentinel in sentinels)
    assert not any((tmp_path / relative).exists() for relative in OFFLINE_MANAGED_FILES)


@pytest.mark.parametrize("case_index", range(5))
def test_each_frozen_case_closes_the_canonical_runtime_and_interpretation_path(
    case_index: int,
    tmp_path: Path,
) -> None:
    spec = case_specs()[case_index]
    run, capture = _run_case(spec, tmp_path / f"case_{case_index}")
    selected = {item.toolId for item in run.selectedTools}
    assert run.verdict == "PASS"
    assert run.userText == FROZEN_PROMPTS[case_index]
    assert selected.issubset(spec.acceptableToolIds)
    assert not selected.intersection(spec.forbiddenFallbacks)
    assert run.job is not None and run.job.state == "completed"
    assert run.evidenceBundle is not None
    assert run.interpretation is not None
    assert capture["invariants"] == {
        "rawUserTextPreserved": True,
        "selectedToolsWithinApprovedDomain": True,
        "noForbiddenFallback": True,
        "providerVisibleEqualsEligible": True,
        "selectedSubsetEligible": True,
        "claimsHaveEvidence": True,
        "recommendationsNonExecutable": True,
    }
    assert run.plan is not None
    assert run.plan.schemaVersion == ("0.2" if spec.requiresDependencyPlan else "0.1")


def test_canonical_evidence_run_identity_is_stable_across_replay(tmp_path: Path) -> None:
    spec = case_specs()[0]
    first, _ = _run_case(spec, tmp_path / "first")
    second, _ = _run_case(spec, tmp_path / "second")
    assert first.runId == second.runId
    assert first.runHash == second.runHash
    assert first.plan == second.plan
    assert first.job == second.job
    assert first.toolCalls == second.toolCalls
    assert first.artifacts == second.artifacts


def test_committed_deepseek_suite_contains_all_real_case_verifications() -> None:
    suite_path = ROOT / "docs" / "phase10l" / "evidence" / "phase10l5_natural_language_closure" / "deepseek_verification_suite.json"
    suite = DeepSeekVerificationSuite.model_validate_json(suite_path.read_text(encoding="utf-8"))
    assert suite.provider == "deepseek"
    assert suite.keySource == "DEEPSEEK_KEY"
    assert suite.model == "deepseek-v4-flash"
    assert suite.verdict == "PASS"
    assert len(suite.cases) == 5
    assert suite.otherRealProviderCalls == 0
    assert suite.totalRealCallCount == 16
    assert sum(item.realCallCount for item in suite.cases) == suite.totalRealCallCount
    assert all(item.verdict == "PASS" for item in suite.cases)
    for case in suite.cases:
        matching = [
            path for path in (suite_path.parent / "deepseek_live").glob("*_verification.json")
            if json.loads(path.read_text(encoding="utf-8"))["verificationId"] == case.verificationId
        ]
        assert len(matching) == 1
        verification = json.loads(matching[0].read_text(encoding="utf-8"))
        run_path = matching[0].with_name(matching[0].name.replace("_verification.json", ".json"))
        run = json.loads(run_path.read_text(encoding="utf-8"))
        assert run["caseSpecId"] == case.caseSpecId
        assert run["runId"] == case.runId
        assert verification["runIds"] == [case.runId]
        assert verification["verificationHash"] == case.verificationHash


def _write_test_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _live_call_audit(*, purpose: str, salt: int = 0) -> dict[str, object]:
    return {
        "purpose": purpose,
        "model": "deepseek-v4-flash",
        "realCall": True,
        "promptHash": f"{salt + 1:064x}",
        "responseHash": f"{salt + 2:064x}",
        "promptBytes": 128,
        "responseBytes": 256,
        "tokenUsage": {
            "promptTokens": 10,
            "completionTokens": 5,
            "totalTokens": 15,
            "estimated": False,
        },
        "elapsedMs": 12.5,
        "outcome": "SUCCESS",
    }


def _write_live_closure_fixture(evidence_dir: Path, *, historical: bool = False) -> None:
    purposes = ["CAPABILITY_PLAN_SELECTION", "GROUNDED_INTERPRETATION", "INTENT_EXTRACTION"]
    case_specs_payload: list[dict[str, str]] = []
    suite_refs: list[dict[str, object]] = []
    for index in range(1, 6):
        case_id = f"case_spec_{index}"
        run_id = f"run_{index}"
        case_specs_payload.append({"caseSpecId": case_id})
        audits = [_live_call_audit(purpose=purpose, salt=index * 10 + offset) for offset, purpose in enumerate(purposes)]
        usage = {
            "promptTokens": 30,
            "completionTokens": 15,
            "totalTokens": 45,
            "estimated": False,
        }
        verification_payload = _identified(
            {
                "schemaVersion": "1.0",
                "verificationId": "pending",
                "verificationHash": "0" * 64,
                "provider": "deepseek",
                "baseUrl": "https://api.deepseek.com",
                "keySource": "DEEPSEEK_KEY",
                "configured": True,
                "model": "deepseek-v4-flash",
                "purposes": purposes,
                "realCallCount": 3,
                "otherRealProviderCalls": 0,
                "runIds": [run_id],
                "outcomes": ["PLAN_READY"],
                "tokenUsage": usage,
                "sanitized": True,
                "verdict": "PASS",
                "createdAt": "2026-07-31T00:00:00Z",
            },
            prefix="deepseek_verification",
            id_field="verificationId",
            hash_field="verificationHash",
            exclude={"createdAt"},
        )
        prefix = f"case_{index}"
        _write_test_json(evidence_dir / "deepseek_live" / f"{prefix}_call_audit.json", audits)
        _write_test_json(evidence_dir / "deepseek_live" / f"{prefix}_verification.json", verification_payload)
        _write_test_json(
            evidence_dir / "deepseek_live" / f"{prefix}.json",
            {
                "caseSpecId": case_id,
                "runId": run_id,
                "runHash": f"{index:064x}",
                "userText": f"case {index}",
                "selectedToolIds": ["dataset.materials_explorer"],
                "planId": f"plan_{index}",
                "planHash": f"{index + 10:064x}",
                "planSchemaVersion": "0.1",
                "graphHash": None,
                "jobId": f"job_{index}",
                "jobStatus": "completed",
                "interpretation": {
                    "interpretationId": f"interpretation_{index}",
                    "outcome": "INTERPRETATION_READY",
                    "bundleHash": f"{index + 20:064x}",
                    "repairCount": 0,
                },
                "artifacts": [],
                "verdict": "PASS",
            },
        )
        suite_refs.append(
            {
                "caseSpecId": case_id,
                "runId": run_id,
                "verificationId": verification_payload["verificationId"],
                "verificationHash": verification_payload["verificationHash"],
                "realCallCount": 3,
                "verdict": "PASS",
            }
        )
    suite_payload = _identified(
        {
            "schemaVersion": "1.0",
            "suiteId": "pending",
            "suiteHash": "0" * 64,
            "provider": "deepseek",
            "baseUrl": "https://api.deepseek.com",
            "keySource": "DEEPSEEK_KEY",
            "configured": True,
            "model": "deepseek-v4-flash",
            "cases": suite_refs,
            "totalRealCallCount": 15,
            "otherRealProviderCalls": 0,
            "tokenUsage": {
                "promptTokens": 150,
                "completionTokens": 75,
                "totalTokens": 225,
                "estimated": False,
            },
            "sanitized": True,
            "verdict": "PASS",
            "createdAt": "2026-07-31T00:00:00Z",
        },
        prefix="deepseek_suite",
        id_field="suiteId",
        hash_field="suiteHash",
        exclude={"createdAt"},
    )
    _write_test_json(evidence_dir / "deepseek_verification_suite.json", suite_payload)
    _write_test_json(evidence_dir / "case_specs.json", case_specs_payload)
    _write_test_json(evidence_dir / "performance.json", {"elapsedMs": 1.0})

    if historical:
        historical_audit = _live_call_audit(purpose="INTENT_EXTRACTION", salt=100)
        historical_ref = {
            "caseNumber": 6,
            "runId": "historical_run_6",
            "runHash": "a" * 64,
            "planningOutcome": "PLAN_READY",
            "selectedToolIds": ["dataset.materials_explorer"],
            "realCallCount": 1,
            "verdict": "PASS",
        }
        _write_test_json(
            evidence_dir / "historical_deepseek_replay" / "case_06_dataset.json",
            {
                **historical_ref,
                "provider": "deepseek",
                "model": "deepseek-v4-flash",
                "providerCallCount": 1,
                "providerCallAudit": [historical_audit],
                "tokenUsage": historical_audit["tokenUsage"],
                "verdict": "PASS",
            },
        )
        historical_suite = {
            "schemaVersion": "1.0",
            "provider": "deepseek",
            "keySource": "DEEPSEEK_KEY",
            "baseUrl": "https://api.deepseek.com",
            "caseCount": 6,
            "passedCaseCount": 6,
            "failedCaseCount": 0,
            "existingL5CaseCount": 5,
            "additionalHistoricalCaseCount": 1,
            "totalRealCallCount": 16,
            "otherRealProviderCalls": 0,
            "tokenUsage": {
                "promptTokens": 160,
                "completionTokens": 80,
                "totalTokens": 240,
                "estimated": False,
            },
            "cases": [
                {"caseNumber": index, "runId": f"run_{index}", "realCallCount": 3, "verdict": "PASS"}
                for index in range(1, 6)
            ] + [historical_ref],
            "verdict": "PASS",
        }
        historical_hash = natural_language_evidence_hash(historical_suite)
        historical_suite["suiteHash"] = historical_hash
        historical_suite["suiteId"] = f"historical_deepseek_suite_{historical_hash[:32]}"
        _write_test_json(evidence_dir / "historical_deepseek_replay_suite.json", historical_suite)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("realCall", False, "realCall"),
        ("purpose", "ARBITRARY_RESEARCH", "purpose"),
        ("outcome", "DEEPSEEK_RESPONSE_INVALID", "outcome"),
        ("promptHash", "not-a-hash", "promptHash"),
        ("responseBytes", 524_289, "responseBytes"),
    ],
)
def test_finalizer_rejects_invalid_live_call_audit(field: str, value: object, message: str) -> None:
    audit = _live_call_audit(purpose="INTENT_EXTRACTION")
    audit[field] = value
    with pytest.raises(ValueError, match=message):
        _validate_call_audit(audit, source="test-audit")


def test_finalizer_rejects_inconsistent_or_estimated_live_usage() -> None:
    inconsistent = _live_call_audit(purpose="INTENT_EXTRACTION")
    inconsistent["tokenUsage"] = {"promptTokens": 10, "completionTokens": 5, "totalTokens": 14, "estimated": False}
    with pytest.raises(ValueError, match="inconsistent"):
        _validate_call_audit(inconsistent, source="test-audit")

    estimated = _live_call_audit(purpose="INTENT_EXTRACTION")
    estimated["tokenUsage"] = {"promptTokens": 10, "completionTokens": 5, "totalTokens": 15, "estimated": True}
    with pytest.raises(ValueError, match="estimated"):
        _validate_call_audit(estimated, source="test-audit")


def test_check_only_recomputes_manifest_without_writing_and_validates_historical_suite(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    evidence_dir = tmp_path / "evidence"
    _write_live_closure_fixture(evidence_dir, historical=True)
    finalized = finalize_evidence(evidence_dir)
    assert finalized["verdict"] == "PASS"
    assert finalized["historicalCaseCount"] == 1

    before = {path.relative_to(evidence_dir).as_posix(): path.read_bytes() for path in evidence_dir.rglob("*") if path.is_file()}
    assert finalize_evidence_main(["--check-only", "--evidence-dir", str(evidence_dir)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["checkOnly"] is True
    assert output["liveCallCount"] == 15
    assert output["historicalCaseCount"] == 1
    after = {path.relative_to(evidence_dir).as_posix(): path.read_bytes() for path in evidence_dir.rglob("*") if path.is_file()}
    assert after == before


def test_check_only_detects_lf_normalized_text_and_raw_png_tampering(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "evidence"
    _write_live_closure_fixture(evidence_dir)
    png_path = evidence_dir / "raw.png"
    png_path.write_bytes(b"raw-png-bytes-v1")
    finalize_evidence(evidence_dir)

    text_path = evidence_dir / "performance_cost_audit.md"
    original_text = text_path.read_text(encoding="utf-8")
    text_path.write_bytes(original_text.replace("\n", "\r\n").encode("utf-8"))
    assert finalize_evidence_main(["--check-only", "--evidence-dir", str(evidence_dir)]) == 0

    text_path.write_text(original_text.replace("Phase 10L-5", "Phase 10L-5 changed", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="hash or byte count mismatch"):
        finalize_evidence_main(["--check-only", "--evidence-dir", str(evidence_dir)])

    text_path.write_text(original_text, encoding="utf-8", newline="\n")
    png_path.write_bytes(b"raw-png-bytes-v2")
    with pytest.raises(ValueError, match="hash or byte count mismatch"):
        finalize_evidence_main(["--check-only", "--evidence-dir", str(evidence_dir)])


def test_finalizer_does_not_write_pass_manifest_when_live_inputs_are_incomplete(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "evidence"
    _write_live_closure_fixture(evidence_dir)
    audit_path = evidence_dir / "deepseek_live" / "case_3_call_audit.json"
    audit_path.unlink()

    with pytest.raises(ValueError, match="exactly five"):
        finalize_evidence(evidence_dir)
    assert not (evidence_dir / "evidence_manifest.json").exists()


def test_finalizer_rejects_tampered_historical_call_audit(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "evidence"
    _write_live_closure_fixture(evidence_dir, historical=True)
    case_path = evidence_dir / "historical_deepseek_replay" / "case_06_dataset.json"
    record = json.loads(case_path.read_text(encoding="utf-8"))
    record["providerCallAudit"][0]["realCall"] = False
    _write_test_json(case_path, record)

    with pytest.raises(ValueError, match="realCall"):
        finalize_evidence(evidence_dir)
    assert not (evidence_dir / "evidence_manifest.json").exists()
