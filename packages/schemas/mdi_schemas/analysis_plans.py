"""Version dispatch for persisted and executable analysis plans."""

from __future__ import annotations

from typing import Any, Mapping, TypeAlias

from .dependency_planning import AnalysisPlanV02
from .models import AnalysisPlan
from .multi_source_planning import AnalysisPlanV03
from .project_planning import AnalysisPlanV04


ExecutableAnalysisPlan: TypeAlias = AnalysisPlan | AnalysisPlanV02 | AnalysisPlanV03 | AnalysisPlanV04


def parse_analysis_plan(value: ExecutableAnalysisPlan | Mapping[str, Any]) -> ExecutableAnalysisPlan:
    # Revalidate models as well: frozen models can still contain mutable lists
    # and dictionaries, including the source inventory and step parameters.
    payload = value.model_dump(mode="json") if isinstance(value, (AnalysisPlan, AnalysisPlanV02)) else dict(value)
    version = payload.get("schemaVersion", "0.1")
    if version == "0.4":
        return AnalysisPlanV04.model_validate(payload)
    if any(key in payload for key in ("scope", "projectId", "referenceSources")):
        raise ValueError("Project-scoped scientific authority requires AnalysisPlan 0.4.")
    if version == "0.3":
        return AnalysisPlanV03.model_validate(payload)
    if "sourceContexts" in payload or "sourceVersions" in payload:
        raise ValueError("Explicit multi-source authority requires AnalysisPlan 0.3.")
    if version == "0.2":
        return AnalysisPlanV02.model_validate(payload)
    if version == "0.1":
        return AnalysisPlan.model_validate(payload)
    raise ValueError(f"Unsupported AnalysisPlan schema version: {version}")


def parse_dependency_plan(value: AnalysisPlanV02 | Mapping[str, Any]) -> AnalysisPlanV02:
    plan = parse_analysis_plan(value)
    if not isinstance(plan, AnalysisPlanV02):
        raise ValueError("Dependency execution requires AnalysisPlan 0.2, 0.3 or 0.4.")
    return plan


__all__ = ["ExecutableAnalysisPlan", "parse_analysis_plan", "parse_dependency_plan"]
