from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable
from uuid import UUID

from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.research_agent.strategy.schemas import (
    ComparisonCompatibility,
    ComparisonCompatibilityStatus,
    ContradictionKind,
    EvidenceContradiction,
    EvidenceLineage,
    EvidenceObservation,
    EvidenceStrength,
    LiteratureEvidenceReference,
    ResearchEvidenceState,
)
from mdi_api.domain.scientific_knowledge.contracts import (
    LiteratureEvidence,
    LiteratureSnapshot,
)


@dataclass(frozen=True)
class ResultEvidenceInput:
    """Bind a persisted Result snapshot identity to its authoritative bundle."""

    result_id: UUID
    bundle: ScientificResultBundle
    parent_result_ids: tuple[UUID, ...] = ()


_UNIT_SCALE: dict[str, tuple[str, float]] = {
    "ev": ("energy", 1.0),
    "mev": ("energy", 1e-3),
    "angstrom": ("length", 1.0),
    "å": ("length", 1.0),
    "nm": ("length", 10.0),
    "picosecond": ("time", 1.0),
    "ps": ("time", 1.0),
    "femtosecond": ("time", 1e-3),
    "fs": ("time", 1e-3),
    "degree": ("angle", 1.0),
    "degrees": ("angle", 1.0),
    "radian": ("angle", 180.0 / math.pi),
    "radians": ("angle", 180.0 / math.pi),
}


def _lineage_signature(item: ResultEvidenceInput) -> str:
    bundle = item.bundle
    payload = {
        "source_version_ids": sorted(
            {
                str(ref.version_id)
                for ref in [*bundle.source_object_refs, *bundle.output_object_refs]
            }
        ),
        "artifact_ids": sorted(set(bundle.provenance.artifact_ids)),
        "parent_result_ids": sorted(str(value) for value in item.parent_result_ids),
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _numeric(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def _normalized_numeric(value: Any, unit: str | None) -> tuple[float, str] | None:
    number = _numeric(value)
    if number is None:
        return None
    if not unit:
        return number, ""
    normalized = _UNIT_SCALE.get(unit.strip().lower())
    if normalized is None:
        return number, unit.strip().lower()
    dimension, scale = normalized
    return number * scale, dimension


def compare_observations(
    left: EvidenceObservation,
    right: EvidenceObservation,
) -> ComparisonCompatibility:
    reasons: list[str] = []
    if left.predicate != right.predicate:
        return ComparisonCompatibility(
            left_result_id=left.result_id,
            right_result_id=right.result_id,
            predicate=f"{left.predicate}|{right.predicate}",
            status=ComparisonCompatibilityStatus.NOT_COMPATIBLE,
            reason_codes=["QUANTITY_SEMANTICS_DIFFER"],
        )
    left_value = _normalized_numeric(left.value, left.unit)
    right_value = _normalized_numeric(right.value, right.unit)
    if left_value is None or right_value is None:
        status = (
            ComparisonCompatibilityStatus.COMPATIBLE
            if (left.unit or "") == (right.unit or "")
            else ComparisonCompatibilityStatus.INSUFFICIENT_METADATA
        )
        reasons.append(
            "NON_NUMERIC_SAME_SEMANTIC_QUANTITY"
            if status == ComparisonCompatibilityStatus.COMPATIBLE
            else "NON_NUMERIC_UNIT_SEMANTICS_UNAVAILABLE"
        )
        return ComparisonCompatibility(
            left_result_id=left.result_id,
            right_result_id=right.result_id,
            predicate=left.predicate,
            status=status,
            normalized_unit=left.unit if left.unit == right.unit else None,
            reason_codes=reasons,
        )
    if left_value[1] != right_value[1]:
        return ComparisonCompatibility(
            left_result_id=left.result_id,
            right_result_id=right.result_id,
            predicate=left.predicate,
            status=ComparisonCompatibilityStatus.NOT_COMPATIBLE,
            reason_codes=["UNIT_DIMENSIONS_DIFFER"],
        )
    same_lineage = left.lineage_signature == right.lineage_signature
    if same_lineage:
        reasons.append("COMMON_EVIDENCE_LINEAGE")
    if set(left.capability_ids) != set(right.capability_ids):
        reasons.append("METHODS_DIFFER")
    if (left.unit or "").strip().lower() != (right.unit or "").strip().lower():
        reasons.append("UNIT_NORMALIZATION_REQUIRED")
    return ComparisonCompatibility(
        left_result_id=left.result_id,
        right_result_id=right.result_id,
        predicate=left.predicate,
        status=(
            ComparisonCompatibilityStatus.CONDITIONALLY_COMPATIBLE
            if reasons
            else ComparisonCompatibilityStatus.COMPATIBLE
        ),
        normalized_unit=left_value[1] or left.unit or right.unit,
        reason_codes=reasons or ["SAME_QUANTITY_AND_UNIT"],
    )


class ResearchEvidenceStateProjector:
    """Derive bounded strategy evidence from authoritative Result bundles."""

    def project(
        self,
        *,
        objective: str,
        results: Iterable[ResultEvidenceInput],
        literature_evidence: Iterable[LiteratureEvidenceReference] = (),
        project_id: str | None = None,
    ) -> ResearchEvidenceState:
        rows = list(results)
        literature_rows = list(literature_evidence)
        if not rows and not literature_rows:
            raise ValueError("strategy evidence projection requires authoritative evidence")
        projects = {item.bundle.project_id for item in rows} | {
            item.project_id for item in literature_rows
        }
        if project_id is not None:
            projects.add(project_id)
        if len(projects) != 1:
            raise ValueError("strategy evidence may not cross project boundaries")
        lineages: list[EvidenceLineage] = []
        observations: list[EvidenceObservation] = []
        limitations: list[str] = []
        result_types: set[str] = set()
        capability_ids: set[str] = set()
        source_version_ids: set[UUID] = set()
        by_fact: dict[str, list[EvidenceObservation]] = defaultdict(list)
        for item in rows:
            bundle = item.bundle
            signature = _lineage_signature(item)
            methods = sorted({method.capability_id for method in bundle.methods})
            versions = sorted(
                {
                    ref.version_id
                    for ref in [*bundle.source_object_refs, *bundle.output_object_refs]
                },
                key=str,
            )
            artifacts = sorted(set(bundle.provenance.artifact_ids))
            lineages.append(
                EvidenceLineage(
                    result_id=item.result_id,
                    bundle_result_id=bundle.result_id,
                    capability_ids=methods,
                    source_version_ids=versions,
                    artifact_ids=artifacts,
                    parent_result_ids=list(item.parent_result_ids),
                    lineage_signature=signature,
                )
            )
            result_types.update(result.result_type for result in bundle.result_items)
            capability_ids.update(methods)
            source_version_ids.update(versions)
            limitations.extend(entry.message for entry in bundle.limitations)
            for fact in bundle.facts:
                observation = EvidenceObservation(
                    result_id=item.result_id,
                    bundle_result_id=bundle.result_id,
                    fact_id=fact.fact_id,
                    predicate=fact.predicate,
                    subject_ref=fact.subject_ref,
                    value=fact.value,
                    unit=fact.unit,
                    capability_ids=methods,
                    source_version_ids=versions,
                    lineage_signature=signature,
                )
                observations.append(observation)
                by_fact[fact.predicate].append(observation)

        comparisons: list[ComparisonCompatibility] = []
        contradictions: list[EvidenceContradiction] = []
        for predicate, candidates in sorted(by_fact.items()):
            counts_by_result: dict[UUID, int] = defaultdict(int)
            for candidate in candidates:
                counts_by_result[candidate.result_id] += 1
            # Repeated predicates within one Result commonly represent samples
            # or per-site values rather than contradictory scalar claims.
            if any(count != 1 for count in counts_by_result.values()):
                continue
            for index, left in enumerate(candidates):
                for right in candidates[index + 1 :]:
                    if left.result_id == right.result_id:
                        continue
                    comparison = compare_observations(left, right)
                    comparisons.append(comparison)
                    left_value = _normalized_numeric(left.value, left.unit)
                    right_value = _normalized_numeric(right.value, right.unit)
                    if comparison.status == ComparisonCompatibilityStatus.NOT_COMPATIBLE:
                        contradictions.append(
                            EvidenceContradiction(
                                contradiction_id=f"contradiction-{len(contradictions) + 1}",
                                predicate=predicate,
                                result_ids=[left.result_id, right.result_id],
                                kind=ContradictionKind.DIFFERENT_UNITS,
                                resolution="Values are not comparable under known unit semantics.",
                                unresolved=False,
                            )
                        )
                    elif left_value is not None and right_value is not None:
                        scale = max(abs(left_value[0]), abs(right_value[0]), 1.0)
                        if abs(left_value[0] - right_value[0]) > max(1e-9, 1e-6 * scale):
                            kind = (
                                ContradictionKind.DIFFERENT_METHODS
                                if set(left.capability_ids) != set(right.capability_ids)
                                else ContradictionKind.DIFFERENT_EXACT_VERSIONS
                                if set(left.source_version_ids)
                                != set(right.source_version_ids)
                                else ContradictionKind.GENUINE_UNRESOLVED
                            )
                            contradictions.append(
                                EvidenceContradiction(
                                    contradiction_id=(
                                        f"contradiction-{len(contradictions) + 1}"
                                    ),
                                    predicate=predicate,
                                    result_ids=[left.result_id, right.result_id],
                                    kind=kind,
                                    resolution=(
                                        "Retain both values with method/source provenance; "
                                        "do not silently prefer the latest Result."
                                    ),
                                    unresolved=True,
                                )
                            )

        if any(item.unresolved for item in contradictions):
            strength = EvidenceStrength.CONFLICTING
        elif any(item.bundle.execution_status.value == "PARTIAL" for item in rows):
            strength = EvidenceStrength.LIMITED
        elif observations:
            strength = EvidenceStrength.WELL_SUPPORTED
        elif literature_rows:
            strength = EvidenceStrength.QUALIFIED_METHOD_DEPENDENT
        else:
            strength = EvidenceStrength.QUALIFIED_METHOD_DEPENDENT
        return ResearchEvidenceState(
            project_id=next(iter(projects)),
            objective=objective,
            result_ids=[item.result_id for item in rows][-32:],
            exact_source_version_ids=sorted(source_version_ids, key=str),
            result_types=sorted(result_types),
            capability_ids=sorted(capability_ids),
            literature_evidence_ids=[
                item.evidence_id for item in literature_rows
            ][:24],
            literature_evidence=literature_rows[:24],
            observations=observations[:256],
            lineages=lineages[-32:],
            contradictions=contradictions[:16],
            comparisons=comparisons[:32],
            limitations=sorted(set(limitations))[:32],
            evidence_strength=strength,
        )


def literature_reference(
    evidence: LiteratureEvidence,
    snapshot: LiteratureSnapshot,
) -> LiteratureEvidenceReference:
    if evidence.snapshot_id != snapshot.snapshot_id:
        raise ValueError("literature evidence must reference the exact snapshot")
    payload = {
        "evidence_id": str(evidence.evidence_id),
        "work_id": str(evidence.work_id),
        "snapshot_id": str(evidence.snapshot_id),
        "claim_refs": sorted(evidence.claim_refs),
        "source_content_hash": evidence.source_content_hash,
    }
    return LiteratureEvidenceReference(
        evidence_id=evidence.evidence_id,
        project_id=evidence.project_id,
        work_id=evidence.work_id,
        snapshot_id=evidence.snapshot_id,
        evidence_scope=evidence.scope.value,
        support_type=evidence.support_type.value,
        publication_status=snapshot.publication_status.value,
        claim_refs=evidence.claim_refs,
        lineage_signature=hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    )


__all__ = [
    "ResearchEvidenceStateProjector",
    "ResultEvidenceInput",
    "compare_observations",
    "literature_reference",
]
