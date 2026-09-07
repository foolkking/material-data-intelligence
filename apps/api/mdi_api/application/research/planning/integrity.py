"""Canonical AnalysisPlan integrity helpers."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from mdi_schemas import AnalysisPlan, AnalysisPlanV02, canonical_dependency_json


def canonical_analysis_plan_json(plan: AnalysisPlan | AnalysisPlanV02 | Mapping[str, Any]) -> str:
    if isinstance(plan, AnalysisPlanV02):
        return canonical_dependency_json(plan)
    if isinstance(plan, AnalysisPlan):
        return json.dumps(plan.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if str(plan.get("schemaVersion") or "") == "0.2":
        return canonical_dependency_json(AnalysisPlanV02.model_validate(plan))
    parsed = AnalysisPlan.model_validate(plan)
    return json.dumps(parsed.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compute_plan_hash(plan: AnalysisPlan | AnalysisPlanV02 | Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_analysis_plan_json(plan).encode("utf-8")).hexdigest()


__all__ = ["canonical_analysis_plan_json", "compute_plan_hash"]
