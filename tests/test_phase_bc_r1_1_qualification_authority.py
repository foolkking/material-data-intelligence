from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import zipfile

import pytest


pytestmark = pytest.mark.qualification


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from mdi_tool_registry import load_manifests  # noqa: E402
from mdi_tool_registry.planner_metadata import build_registry_snapshot  # noqa: E402
from phase_bc_r1_contracts import PLAN_STEP_CAP  # noqa: E402
from validate_phase_bc_r1_qualification_authority import (  # noqa: E402
    _renderer_map,
    _verify_case,
    validate_package,
)


INPUTS = ROOT / "_qualification" / "inputs"
R1_PACKAGE = INPUTS / "Phase_BC_R1_Qualification_Authority_Reconciled.zip"
R11_PACKAGE = INPUTS / "Phase_BC_R1_1_Qualification_Authority_Reconciled.zip"
R1_SHA256 = "6a1e3f1100407fd70f2d689bb2022754ac3723f8c127c8963042b25db82dc3b3"
PACKAGE_ROOT = ROOT / "_qualification" / "work" / "phase_bc_r1_1" / "package"
HISTORICAL_ROOT = ROOT / "_qualification" / "work" / "phase_bc_r1_1" / "historical_r1_source"
EVIDENCE = ROOT / "_qualification" / "evidence" / "phase_bc_r1_1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_case(root: Path, case_id: str) -> tuple[Path, dict]:
    path = next(root.glob(f"*_{case_id}/CASE.json"))
    return path.parent, json.loads(path.read_text(encoding="utf-8"))


def validator_authorities():
    registry = load_manifests()
    _, metadata = build_registry_snapshot(registry)
    return {tool.toolId: tool for tool in registry.tools}, metadata, _renderer_map()


def test_historical_package_is_immutable_and_r11_is_distinct_deterministic_authority() -> None:
    verification = json.loads((EVIDENCE / "NEW_PACKAGE_VERIFICATION.json").read_text(encoding="utf-8"))
    assert sha256(R1_PACKAGE) == R1_SHA256
    assert sha256(R11_PACKAGE) == verification["sha256"]
    assert verification["sha256"] != R1_SHA256
    assert verification["deterministicBuild1Sha256"] == verification["deterministicBuild2Sha256"]
    assert verification["entriesSorted"] is True
    assert verification["caseHashMismatches"] == 0
    assert verification["rootHashMismatches"] == 0
    assert verification["missingFiles"] == 0


def test_historical_r11_is_superseded_by_current_transport_and_cuka_authority() -> None:
    result = validate_package(PACKAGE_ROOT)
    assert result["status"] == "FAIL"
    assert result["caseCount"] == 16
    assert result["issueCounts"] == {
        "REPOSITORY_AUTHORITY_FINGERPRINT_DRIFT": 1,
        "XRD_WAVELENGTH_INCOMPATIBILITY": 1,
    }
    audit = json.loads((EVIDENCE / "CROSS_FIELD_CONSISTENCY_AUDIT.json").read_text(encoding="utf-8"))
    assert audit["crossFieldContractConflicts"] == 0
    assert audit["executionTurnToolUnionMismatches"] == 0
    assert audit["requiredToolCountMismatches"] == 0
    assert audit["expectedRejectionExecutionContradictions"] == 0
    assert all(case["pass"] for case in audit["cases"])


def test_compatibility_aliases_exactly_mirror_canonical_requirements() -> None:
    policy = json.loads((PACKAGE_ROOT / "CONTRACT_ALIAS_POLICY.json").read_text(encoding="utf-8"))
    assert policy["policy"] == "REQUIRED_FIELDS_CANONICAL_EXPECTED_FIELDS_NORMATIVE_COMPATIBILITY_MIRRORS"
    assert all(row["exactMirrorRequired"] for row in policy["compatibilityAliases"])
    for path in sorted(PACKAGE_ROOT.glob("*/CASE.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        assert case["expectedReport"] == case["requiredReportBehavior"]
        assert case["expectedRecipe"] == case["requiredRecipeBehavior"]
        assert case["expectedLimitationAssertions"] == case["requiredLimitations"]


def test_atomic_view_remains_a_consistent_expected_pre_plan_rejection() -> None:
    _, case = load_case(PACKAGE_ROOT, "Q-ATOMIC-VIEW-001")
    assert case["caseType"] == "EXPECTED_REJECTION"
    assert case["supportDisposition"] == "UNSUPPORTED"
    assert case["analysisExecutionExpected"] is False
    assert case["requiredExecutionTools"] == []
    assert case["executionTurns"] == []
    assert case["requiredArtifacts"] == []
    assert case["requiredRenderers"] == []
    assert case["requiredReportBehavior"] == {
        "finalizeExpected": False,
        "previewExpected": False,
        "sourceEligible": False,
    }
    assert case["requiredRecipeBehavior"] == {
        "expected": False,
        "recipeExecutionAuthorized": False,
    }


def test_primary_submission_authority_preserves_multi_turn_and_rejection_semantics() -> None:
    payload = json.loads(
        (PACKAGE_ROOT / "PRIMARY_QUALIFICATION_EXECUTION_AUTHORITY.json").read_text(encoding="utf-8")
    )
    rows = {row["caseId"]: row for row in payload["cases"]}
    multi_turn = {
        "Q-DATASET-001",
        "Q-COMPOSITION-001",
        "Q-TABLE-001",
        "Q-STRUCTURE-001",
        "Q-COORD-001",
        "Q-TRAJECTORY-001",
    }
    assert len(rows) == 16
    for case_id, row in rows.items():
        _, case = load_case(PACKAGE_ROOT, case_id)
        if case_id == "Q-ATOMIC-VIEW-001":
            assert row["submissionMode"] == "CANONICAL_QUESTION_EXPECTED_PRE_PLAN_REJECTION"
            assert row["plannerSubmissionQuestions"] == [case["canonicalQuestion"]]
        elif case_id in multi_turn:
            assert row["submissionMode"] == "ORDERED_EXECUTION_TURNS"
            assert row["plannerSubmissionQuestions"] == [turn["question"] for turn in case["executionTurns"]]
        else:
            assert row["submissionMode"] == "SINGLE_EXECUTION_TURN"
            assert row["plannerSubmissionQuestions"] == [case["executionTurns"][0]["question"]]


def test_every_turn_and_required_tool_aggregate_respects_current_plan_contract() -> None:
    for path in sorted(PACKAGE_ROOT.glob("*/CASE.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        turn_union = sorted({tool for turn in case["executionTurns"] for tool in turn["requiredExecutionTools"]})
        assert turn_union == case["requiredExecutionTools"]
        assert case["requiredExecutionToolCount"] == len(set(case["requiredExecutionTools"]))
        for turn in case["executionTurns"]:
            assert len(set(turn["requiredExecutionTools"])) <= turn["maxRequiredStepCount"] <= PLAN_STEP_CAP


def test_hardened_validator_rejects_each_new_cross_field_contradiction_class() -> None:
    tools, metadata, renderers = validator_authorities()
    atomic_dir, atomic = load_case(PACKAGE_ROOT, "Q-ATOMIC-VIEW-001")

    invalid_report = deepcopy(atomic)
    invalid_report["expectedReport"]["previewExpected"] = True
    report_codes = {issue["code"] for issue in _verify_case(atomic_dir, invalid_report, tools, metadata, renderers)}
    assert "CONFLICTING_REPORT_REQUIREMENTS" in report_codes

    invalid_recipe = deepcopy(atomic)
    invalid_recipe["expectedRecipe"]["expected"] = True
    recipe_codes = {issue["code"] for issue in _verify_case(atomic_dir, invalid_recipe, tools, metadata, renderers)}
    assert "CONFLICTING_RECIPE_REQUIREMENTS" in recipe_codes

    invalid_limitations = deepcopy(atomic)
    invalid_limitations["expectedLimitationAssertions"] = []
    limitation_codes = {
        issue["code"] for issue in _verify_case(atomic_dir, invalid_limitations, tools, metadata, renderers)
    }
    assert "CONFLICTING_LIMITATION_REQUIREMENTS" in limitation_codes

    invalid_rejection = deepcopy(atomic)
    invalid_rejection["requiredArtifacts"] = ["analysis_plan_json"]
    rejection_codes = {
        issue["code"] for issue in _verify_case(atomic_dir, invalid_rejection, tools, metadata, renderers)
    }
    assert "EXPECTED_REJECTION_HAS_EXECUTION_REQUIREMENTS" in rejection_codes

    dataset_dir, dataset = load_case(PACKAGE_ROOT, "Q-DATASET-001")
    invalid_union = deepcopy(dataset)
    invalid_union["executionTurns"][0]["requiredExecutionTools"] = []
    union_codes = {
        issue["code"] for issue in _verify_case(dataset_dir, invalid_union, tools, metadata, renderers)
    }
    assert "EXECUTION_TURN_TOOL_UNION_MISMATCH" in union_codes

    invalid_count = deepcopy(dataset)
    invalid_count["requiredExecutionToolCount"] += 1
    count_codes = {
        issue["code"] for issue in _verify_case(dataset_dir, invalid_count, tools, metadata, renderers)
    }
    assert "REQUIRED_TOOL_COUNT_MISMATCH" in count_codes


def test_protected_scientific_source_and_provenance_bytes_are_unchanged() -> None:
    protected_names = {"LICENSE.txt", "PROVENANCE.json"}
    with zipfile.ZipFile(R1_PACKAGE) as r1_archive, zipfile.ZipFile(R11_PACKAGE) as r11_archive:
        r1_names = {
            name
            for name in r1_archive.namelist()
            if Path(name).name in protected_names or Path(name).name.startswith(("SOURCE_", "UPLOAD_"))
        }
        r11_names = {
            name
            for name in r11_archive.namelist()
            if Path(name).name in protected_names or Path(name).name.startswith(("SOURCE_", "UPLOAD_"))
        }
        assert r1_names == r11_names
        for name in r1_names:
            assert r1_archive.read(name) == r11_archive.read(name)


def test_r11_evidence_json_and_sha256_manifest_are_self_consistent() -> None:
    required = {
        "PHASE_BC_R1_1_RESULT.md",
        "CROSS_FIELD_CONSISTENCY_AUDIT.json",
        "ATOMIC_VIEW_CONTRACT_CORRECTION.json",
        "STATIC_VALIDATOR_HARDENING.json",
        "MULTI_TURN_EXECUTION_AUTHORITY.json",
        "PACKAGE_SUPERSESSION.json",
        "NEW_PACKAGE_VERIFICATION.json",
        "REGRESSION_CLASSIFICATION.json",
        "SHA256SUMS.txt",
    }
    assert required <= {path.name for path in EVIDENCE.iterdir() if path.is_file()}
    for path in EVIDENCE.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    for line in (EVIDENCE / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        assert sha256(EVIDENCE / relative) == expected
