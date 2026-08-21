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

from phase_bc_r1_contracts import (  # noqa: E402
    CASE_SCHEMA_VERSION,
    NEW_PACKAGE_NAME,
    OLD_PACKAGE_NAME,
    OLD_PACKAGE_SHA256,
    PLAN_STEP_CAP,
    ROOT_SCHEMA_VERSION,
)
from validate_phase_bc_r1_qualification_authority import (  # noqa: E402
    _renderer_map,
    _verify_case,
    validate_package,
)
from mdi_tool_registry import load_manifests  # noqa: E402
from mdi_tool_registry.planner_metadata import build_registry_snapshot  # noqa: E402


INPUTS = ROOT / "_qualification" / "inputs"
PACKAGE_ROOT = ROOT / "_qualification" / "work" / "phase_bc_r1" / "package"
EVIDENCE = ROOT / "_qualification" / "evidence" / "phase_bc_r1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_case(case_id: str) -> tuple[Path, dict]:
    case_path = next(PACKAGE_ROOT.glob(f"*_{case_id}/CASE.json"))
    return case_path.parent, json.loads(case_path.read_text(encoding="utf-8"))


def validator_authorities():
    registry = load_manifests()
    _, metadata = build_registry_snapshot(registry)
    return {tool.toolId: tool for tool in registry.tools}, metadata, _renderer_map()


def test_historical_package_is_immutable_and_superseded_by_new_identity() -> None:
    old_package = INPUTS / OLD_PACKAGE_NAME
    new_package = INPUTS / NEW_PACKAGE_NAME
    verification = json.loads((EVIDENCE / "NEW_PACKAGE_VERIFICATION.json").read_text(encoding="utf-8"))
    assert sha256(old_package) == OLD_PACKAGE_SHA256
    assert new_package.is_file()
    assert sha256(new_package) == verification["sha256"]
    assert verification["sha256"] != OLD_PACKAGE_SHA256
    assert verification["deterministicBuild1Sha256"] == verification["deterministicBuild2Sha256"]
    assert verification["entriesSorted"] is True


def test_historical_r1_package_exposes_the_report_alias_conflict() -> None:
    result = validate_package(PACKAGE_ROOT)
    assert result["status"] == "FAIL"
    assert result["caseCount"] == 16
    assert result["registryToolCount"] == 62
    assert result["analysisPlanStepCap"] == PLAN_STEP_CAP
    assert result["issueCounts"]["CONFLICTING_REPORT_REQUIREMENTS"] == 1
    assert result["issueCounts"]["REPOSITORY_AUTHORITY_FINGERPRINT_DRIFT"] == 1
    assert result["issueCounts"]["XRD_WAVELENGTH_INCOMPATIBILITY"] == 1
    manifest = json.loads((PACKAGE_ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == ROOT_SCHEMA_VERSION
    assert manifest["metrics"]["EXECUTION_READY_CASES"] == 16
    assert manifest["metrics"]["CASE_AUTHORITY_CONFLICTS"] == 0


def test_all_cases_have_reconciled_machine_readable_contracts() -> None:
    required_fields = {
        "caseId",
        "canonicalQuestion",
        "assets",
        "semanticDataKinds",
        "requiredProfileFacts",
        "requiredIntentFacts",
        "requiredExecutionTools",
        "allowedExecutionTools",
        "forbiddenExecutionTools",
        "campaignCoverageContributions",
        "requiredArtifacts",
        "requiredRenderers",
        "requiredLimitations",
        "requiredReportBehavior",
        "requiredRecipeBehavior",
        "currentPlanStepCap",
        "requiredExecutionToolCount",
        "executionReady",
        "authorityConflicts",
        "correctionsApplied",
        "sourceBytesChanged",
        "reason",
    }
    case_paths = sorted(PACKAGE_ROOT.glob("*/CASE.json"))
    assert len(case_paths) == 16
    for path in case_paths:
        case = json.loads(path.read_text(encoding="utf-8"))
        assert case["schemaVersion"] == CASE_SCHEMA_VERSION
        assert required_fields <= set(case)
        assert case["executionReady"] is True
        assert case["authorityConflicts"] == []
        assert case["sourceBytesChanged"] is False
        assert case["maximumRequiredToolsPerTurn"] <= PLAN_STEP_CAP
        assert case["expectedRecipe"]["recipeExecutionAuthorized"] is False


def test_confirmed_authority_conflict_is_reconciled_without_support_expansion() -> None:
    _, composition = load_case("Q-COMPOSITION-001")
    assert composition["semanticDataKinds"] == ["materials_tabular_dataset"]
    assert all(asset["containerFormat"] == "CSV" for asset in composition["assets"])
    assert "structure.composition_from_structure" not in composition["requiredExecutionTools"]
    assert "structure.composition_from_structure" in composition["forbiddenExecutionTools"]
    assert composition["requiredExecutionToolCount"] == 3

    _, atomic = load_case("Q-ATOMIC-VIEW-001")
    assert atomic["supportDisposition"] == "UNSUPPORTED"
    assert atomic["analysisExecutionExpected"] is False
    assert atomic["requiredExecutionTools"] == []
    assert atomic["requiredArtifacts"] == []

    _, trajectory = load_case("Q-TRAJECTORY-001")
    assert "full supplied time range" in trajectory["canonicalQuestion"]


def test_protected_scientific_source_and_provenance_bytes_are_unchanged() -> None:
    protected_names = {"LICENSE.txt", "PROVENANCE.json"}
    with zipfile.ZipFile(INPUTS / OLD_PACKAGE_NAME) as old_archive, zipfile.ZipFile(INPUTS / NEW_PACKAGE_NAME) as new_archive:
        old_names = {
            name
            for name in old_archive.namelist()
            if Path(name).name in protected_names or Path(name).name.startswith(("SOURCE_", "UPLOAD_"))
        }
        new_names = {
            name
            for name in new_archive.namelist()
            if Path(name).name in protected_names or Path(name).name.startswith(("SOURCE_", "UPLOAD_"))
        }
        assert old_names == new_names
        assert old_names
        for name in old_names:
            assert old_archive.read(name) == new_archive.read(name)


def test_static_validator_rejects_missing_tool_input_and_plan_overflow() -> None:
    tools, metadata, renderers = validator_authorities()
    composition_dir, composition = load_case("Q-COMPOSITION-001")
    invalid_input = deepcopy(composition)
    invalid_input["requiredExecutionTools"] = sorted(
        [*invalid_input["requiredExecutionTools"], "structure.composition_from_structure"]
    )
    invalid_input["forbiddenExecutionTools"].remove("structure.composition_from_structure")
    invalid_input["executionTurns"][0]["requiredExecutionTools"].append("structure.composition_from_structure")
    invalid_input["executionTurns"][0]["requiredExecutionTools"].sort()
    invalid_input["executionTurns"][0]["maxRequiredStepCount"] = 2
    input_codes = {
        issue["code"] for issue in _verify_case(composition_dir, invalid_input, tools, metadata, renderers)
    }
    assert "REQUIRED_TOOL_INPUT_KIND_ABSENT" in input_codes

    table_dir, table = load_case("Q-TABLE-001")
    over_cap = deepcopy(table)
    over_cap_tools = sorted([*over_cap["requiredExecutionTools"], "table.distribution_summary"])
    over_cap["requiredExecutionTools"] = over_cap_tools
    over_cap["allowedExecutionTools"].remove("table.distribution_summary")
    over_cap["executionTurns"] = [
        {
            "turnId": "invalid-over-cap",
            "question": "Require every table view in one Plan.",
            "requiredExecutionTools": over_cap_tools,
            "planVersionExpected": "0.1",
            "maxRequiredStepCount": len(over_cap_tools),
        }
    ]
    cap_codes = {issue["code"] for issue in _verify_case(table_dir, over_cap, tools, metadata, renderers)}
    assert "REQUIRED_TOOL_COUNT_OVER_PLAN_CAP" in cap_codes


def test_evidence_json_and_sha256_manifest_are_self_consistent() -> None:
    required = {
        "AUTHORITY_CONFLICT_RESOLUTION.json",
        "ALL_CASE_AUTHORITY_AUDIT.json",
        "CASE_EXECUTION_CONTRACT_MATRIX.json",
        "CAMPAIGN_COVERAGE_MODEL.json",
        "PLAN_CAP_VALIDATION.json",
        "ASSET_SEMANTIC_COMPATIBILITY.json",
        "ARTIFACT_RENDERER_CONTRACT_MATRIX.json",
        "REPOSITORY_AUTHORITY_FINGERPRINT.json",
        "PACKAGE_SUPERSESSION.json",
        "NEW_PACKAGE_VERIFICATION.json",
        "PHASE_BC_R1_RESULT.md",
        "SHA256SUMS.txt",
    }
    assert required <= {path.name for path in EVIDENCE.iterdir() if path.is_file()}
    for path in EVIDENCE.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    for line in (EVIDENCE / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        assert sha256(EVIDENCE / relative) == expected
