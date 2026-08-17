from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from mdi_tool_registry import load_manifests  # noqa: E402
from phase_bc_r1_7_cap_preflight import evaluate_tool_caps, old_trajectory_reproduction  # noqa: E402


CAP_FIXTURE = ROOT / "tests" / "fixtures" / "release_closure" / "trajectory_cap_metrics.json"


def cap_fixture() -> dict:
    return json.loads(CAP_FIXTURE.read_text(encoding="utf-8"))


def test_old_trajectory_is_rejected_by_released_caps_before_execution() -> None:
    registry = load_manifests()
    result = old_trajectory_reproduction(registry, metrics=cap_fixture()["historicalR16"])

    assert result["result"] == "PASS_OLD_FAILURE_REPRODUCED"
    assert "REQUIRED_TOOL_FRAME_CAP_EXCEEDED" in result["observedIssueCodes"]
    assert "REQUIRED_TOOL_PAIR_EVALUATION_CAP_EXCEEDED" in result["observedIssueCodes"]
    assert "SCIENTIFIC_PARAMETER_INCOMPATIBLE" in result["observedIssueCodes"]
    assert result["resourceMetrics"]["trajectoryFrames"] == 650
    assert result["resourceMetrics"]["trajectoryAtoms"] == 516


def test_r17_trajectory_passes_the_same_generic_cap_projection() -> None:
    registry = load_manifests()
    metrics = cap_fixture()["currentR17"]

    assert metrics["trajectoryFrames"] == 15
    assert metrics["trajectoryAtoms"] == 516
    assert metrics["trajectoryPositionWrapping"] == "unwrapped"
    assert metrics["trajectoryLatticeMode"] == "fixed"
    assert metrics["trajectoryPbc"] == [True, True, True]
    assert metrics["trajectoryTimes"] == [float(index * 75) for index in range(15)]

    for tool_id in ("trajectory.msd", "trajectory.diffusion", "trajectory.rdf"):
        result = evaluate_tool_caps(tool_id, registry.get_tool_by_id(tool_id).resourceLimits, metrics)
        assert result["status"] == "PASS"
        assert result["issues"] == []
        assert result["unpreflightableLimits"] == []


def test_resource_cap_projection_is_not_case_id_special_cased() -> None:
    source = (ROOT / "scripts" / "phase_bc_r1_7_cap_preflight.py").read_text(encoding="utf-8")
    assert "if caseId == \"Q-TRAJECTORY-001\"" not in source
    assert "caseSpecificBranches\": 0" in source
