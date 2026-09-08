from __future__ import annotations

from typing import Any, Iterable

from mdi_api.domain.scientific_objects.contracts import ScientificObjectAvailability
from mdi_api.domain.scientific_results.contracts import ResultRelevanceStatus, ScientificObjectRef


class ScientificResultRelevanceEvaluator:
    """Evaluate current source health without mutating an immutable snapshot."""

    def evaluate(self, source_refs: Iterable[ScientificObjectRef], *, objects: dict[str, dict[str, Any]] | None = None, versions: dict[str, dict[str, Any]] | None = None) -> ResultRelevanceStatus:
        statuses: list[ResultRelevanceStatus] = []
        objects = objects or {}
        versions = versions or {}
        for ref in source_refs:
            logical = objects.get(str(ref.object_id))
            version = versions.get(str(ref.version_id))
            if version is None:
                statuses.append(ResultRelevanceStatus.SOURCE_MISSING)
                continue
            availability = str(version.get("availability_status") or version.get("availabilityStatus") or "AVAILABLE")
            lifecycle = str((logical or {}).get("lifecycle_status") or (logical or {}).get("lifecycleStatus") or "ACTIVE")
            if availability == ScientificObjectAvailability.INVALID.value or lifecycle == "INVALIDATED":
                statuses.append(ResultRelevanceStatus.INVALIDATED)
            elif availability == ScientificObjectAvailability.SOURCE_MISSING.value:
                statuses.append(ResultRelevanceStatus.SOURCE_MISSING)
            elif logical is not None and str(logical.get("current_version_id") or logical.get("currentVersionId") or "") != str(ref.version_id):
                statuses.append(ResultRelevanceStatus.STALE)
            else:
                statuses.append(ResultRelevanceStatus.CURRENT)
        if not statuses:
            return ResultRelevanceStatus.CURRENT
        return max(statuses, key={
            ResultRelevanceStatus.CURRENT: 0,
            ResultRelevanceStatus.STALE: 1,
            ResultRelevanceStatus.SOURCE_MISSING: 2,
            ResultRelevanceStatus.INVALIDATED: 3,
        }.get)
