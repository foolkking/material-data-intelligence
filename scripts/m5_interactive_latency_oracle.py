"""Deterministic M5 interactive latency and workload verdict helpers."""

from __future__ import annotations

import math
from typing import Any


def evaluate_interactive_latency(
    measured_latency_seconds: float,
    criterion_seconds: float,
) -> dict[str, Any]:
    """Return the frozen hard-bound verdict for one interactive request."""
    measured = float(measured_latency_seconds)
    criterion = float(criterion_seconds)
    if not math.isfinite(measured) or measured < 0:
        raise ValueError("measured_latency_seconds must be finite and non-negative")
    if not math.isfinite(criterion) or criterion < 0:
        raise ValueError("criterion_seconds must be finite and non-negative")
    performance_pass = measured <= criterion
    return {
        "measured_latency_seconds": measured,
        "criterion_seconds": criterion,
        "performance_pass": performance_pass,
    }


def evaluate_workload_oracle(
    *,
    scientific_pass: bool,
    performance_pass: bool,
    provider_required: bool = False,
    provider_pass: bool | None = None,
) -> dict[str, bool | None]:
    """Keep scientific, performance, provider, and overall verdicts distinct."""
    if provider_required and provider_pass is None:
        raise ValueError("provider_pass is required for provider-backed workloads")
    effective_provider_pass = True if not provider_required else bool(provider_pass)
    overall_workload_pass = (
        bool(scientific_pass)
        and bool(performance_pass)
        and effective_provider_pass
    )
    return {
        "scientific_pass": bool(scientific_pass),
        "performance_pass": bool(performance_pass),
        "provider_pass": None if not provider_required else effective_provider_pass,
        "overall_workload_pass": overall_workload_pass,
    }
