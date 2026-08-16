from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from mdi_llm.analysis_intent import AnalysisIntentError, ClarificationSubmission, DeterministicAnalysisIntentBuilder
from mdi_schemas import (
    ANALYSIS_INTENT_MAX_CLARIFICATION_ROUNDS,
    ANALYSIS_INTENT_MAX_QUESTIONS,
    ANALYSIS_INTENT_SUPPORTED_SCHEMA_VERSIONS,
    ClarificationAnswer,
)

from tests.test_phase10l1_analysis_intent import _profile, _request


ROOT = Path(__file__).resolve().parents[1]
SEAL = ROOT / "docs/phase13/evidence/phase13_0_release_scope_seal"
CORRECTION = ROOT / "docs/phase13/evidence/phase13_0_clarification_fact_correction"
OLD_FACT_HASH = "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
OLD_SCOPE_HASH = "8e8b4f659888635192d259eee90f3befdd655cacb292a78c5e13c20a5fdabdde"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_analysis_intent_one_round_authority_and_typed_second_round_failure() -> None:
    assert "1.0" in ANALYSIS_INTENT_SUPPORTED_SCHEMA_VERSIONS
    assert ANALYSIS_INTENT_MAX_CLARIFICATION_ROUNDS == 1
    assert ANALYSIS_INTENT_MAX_QUESTIONS == 3

    profile = _profile(targets=("formation_energy", "band_gap"))
    builder = DeterministicAnalysisIntentBuilder()
    initial = builder.build(_request("Analyze where the regression model predictions are wrong."), profile=profile)
    question = initial.clarification.questions[0]
    ready = builder.clarify(
        initial,
        ClarificationSubmission(
            intent_id=initial.intentId,
            expected_profile_semantic_hash=profile.semanticHash or "",
            answers=(ClarificationAnswer(questionId=question.questionId, selectedValues=[question.options[1].value]),),
        ),
        profile=profile,
    )
    assert ready.provenance.parentIntentId == initial.intentId
    with pytest.raises(AnalysisIntentError) as error:
        builder.clarify(
            ready,
            ClarificationSubmission(
                intent_id=ready.intentId,
                expected_profile_semantic_hash=profile.semanticHash or "",
                answers=(),
            ),
            profile=profile,
        )
    assert error.value.code == "CLARIFICATION_NOT_ALLOWED"


def test_all_seven_demo_contracts_inherit_production_clarification_authority() -> None:
    demos = _json(SEAL / "seven_demo_registry.json")["demos"]
    assert len(demos) == 7
    for demo in demos:
        assert demo["clarification"] == {
            "maxQuestionsPerRound": 3,
            "maxRounds": 1,
            "resolvedIntentInjection": False,
            "secondRoundBehavior": "TYPED_FAILURE",
            "secondRoundErrorCode": "CLARIFICATION_NOT_ALLOWED",
            "validOptions": "user-visible bounded choices",
            "whenRequired": True,
        }
        assert demo["executed"] is False
        assert demo["passClaim"] is False


def test_current_authority_has_no_two_round_projection_and_history_is_retained() -> None:
    generator = (ROOT / "scripts/generate_phase13_0_release_scope.py").read_text(encoding="utf-8")
    demos = (SEAL / "seven_demo_registry.json").read_text(encoding="utf-8")
    history = (ROOT / "results.md").read_text(encoding="utf-8")
    assert '"maxRounds": 2' not in generator
    assert '"maxRounds": 2' not in demos
    assert history.count("bounded to two rounds") >= 1


def test_hash_impact_and_determinism_are_explicit() -> None:
    fact = _json(SEAL / "initial_release_fact_model.json")
    scope = _json(SEAL / "initial_release_scope_baseline.json")
    assert fact["semanticHash"] == OLD_FACT_HASH
    assert scope["semanticHash"] != OLD_SCOPE_HASH
    assert _json(CORRECTION / "fact_model_hash_impact.json")["impact"] == "NO"
    assert _json(CORRECTION / "scope_baseline_hash_impact.json")["impact"] == "YES"
    assert _json(CORRECTION / "baseline_determinism.json")["scopeBaseline"] == "PASS"


def test_correction_manifest_is_complete_and_hash_valid() -> None:
    manifest = _json(CORRECTION / "manifest.json")
    assert manifest["missing"] == manifest["hashMismatch"] == manifest["unclassified"] == 0
    for entry in manifest["entries"]:
        assert hashlib.sha256((CORRECTION / entry["path"]).read_bytes()).hexdigest() == entry["sha256"]


def test_release_governance_stays_zero_gap_and_unexecuted() -> None:
    acceptance = _json(SEAL / "phase13_acceptance_registry.json")["records"]
    gaps = _json(SEAL / "release_gap_registry.json")
    assert len(acceptance) == 56
    assert sum(item["phase"] == "13-0" and item["status"] == "PASS" for item in acceptance) == 8
    assert gaps["releaseBlockers"] == gaps["releaseCriticalIntegrationGaps"] == gaps["unclassified"] == 0
    assert _json(CORRECTION / "phase13_2_contract_revalidation.json")["demosExecuted"] == 0


def test_platform_neutral_hash_verifier() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/verify_phase13_0_clarification_hash.py")],
        cwd=ROOT,
        check=True,
    )
