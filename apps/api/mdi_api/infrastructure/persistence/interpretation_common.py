"""Shared, domain-specific interpretation persistence primitives."""

from __future__ import annotations

from contextlib import contextmanager
from threading import Lock
from typing import Iterator

from mdi_schemas import (
    GroundedScientificInterpretation,
    InterpretationExecutionRecord,
    ScientificEvidenceBundle,
)


class _KeyedLockRegistry:
    def __init__(self) -> None:
        self._guard = Lock()
        self._entries: dict[tuple[str, ...], tuple[Lock, int]] = {}

    @contextmanager
    def guard(self, key: tuple[str, ...]) -> Iterator[None]:
        with self._guard:
            lock, users = self._entries.get(key, (Lock(), 0))
            self._entries[key] = (lock, users + 1)
        lock.acquire()
        try:
            yield
        finally:
            lock.release()
            with self._guard:
                current_lock, current_users = self._entries[key]
                if current_users == 1:
                    del self._entries[key]
                else:
                    self._entries[key] = (current_lock, current_users - 1)


def validate_interpretation_run_association(
    bundle: ScientificEvidenceBundle,
    execution: InterpretationExecutionRecord,
) -> None:
    expected = (
        execution.sourceBundleId == bundle.bundleId,
        execution.sourceBundleHash == bundle.bundleHash,
        execution.sourceJobId == bundle.jobId,
        execution.sourcePlanId == bundle.planId,
        execution.sourcePlanHash == bundle.planHash,
        execution.sourceGraphHash == bundle.graphHash,
        execution.evidenceItemCount == len(bundle.evidenceItems),
        execution.warningCount == len(bundle.bundleWarnings),
        execution.limitationCount == len(bundle.bundleLimitations),
    )
    if not all(expected):
        raise ValueError("Interpretation execution record does not match its evidence bundle")


def validate_interpretation_associations(
    bundle: ScientificEvidenceBundle,
    interpretation: GroundedScientificInterpretation,
    execution: InterpretationExecutionRecord,
) -> None:
    validate_interpretation_run_association(bundle, execution)
    expected = (
        interpretation.sourceBundleId == bundle.bundleId,
        interpretation.sourceBundleHash == bundle.bundleHash,
        interpretation.sourceJobId == bundle.jobId,
        interpretation.sourcePlanId == bundle.planId,
        interpretation.sourcePlanHash == bundle.planHash,
        interpretation.sourceGraphHash == bundle.graphHash,
        interpretation.executionRecordId == execution.executionRecordId,
        interpretation.mode == execution.mode,
        interpretation.provider == execution.provider,
        interpretation.providerVersion == execution.providerVersion,
        interpretation.repairCount == execution.repairCount,
        interpretation.outcome == execution.outcome,
        execution.claimCount == len(interpretation.claims),
    )
    if not all(expected):
        raise ValueError("Interpretation, execution, and evidence identities are inconsistent")
    evidence_ids = {item.evidenceItemId for item in bundle.evidenceItems}
    for claim in interpretation.claims:
        refs = set(
            claim.subjectEvidenceIds
            + claim.supportingEvidenceIds
            + claim.limitingEvidenceIds
            + claim.contradictingEvidenceIds
        )
        if not refs.issubset(evidence_ids):
            raise ValueError("Interpretation claim references evidence outside its bundle")


__all__ = [
    "_KeyedLockRegistry",
    "validate_interpretation_associations",
    "validate_interpretation_run_association",
]
