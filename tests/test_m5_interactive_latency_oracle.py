from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "m5_interactive_latency_oracle.py"
)
SPEC = importlib.util.spec_from_file_location("m5_interactive_latency_oracle", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
ORACLE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORACLE)


@pytest.mark.parametrize(
    ("measured", "expected"),
    [
        (0.20, True),
        (0.25, True),
        (0.26, False),
        (0.64, False),
    ],
)
def test_interactive_latency_hard_boundary(measured: float, expected: bool) -> None:
    verdict = ORACLE.evaluate_interactive_latency(measured, 0.25)
    assert verdict["performance_pass"] is expected


def test_scientific_success_cannot_override_performance_failure() -> None:
    verdict = ORACLE.evaluate_workload_oracle(
        scientific_pass=True,
        performance_pass=False,
    )
    assert verdict == {
        "scientific_pass": True,
        "performance_pass": False,
        "provider_pass": None,
        "overall_workload_pass": False,
    }


@pytest.mark.parametrize("value", [-0.01, float("inf"), float("nan")])
def test_interactive_latency_rejects_invalid_measurements(value: float) -> None:
    with pytest.raises(ValueError):
        ORACLE.evaluate_interactive_latency(value, 0.25)
