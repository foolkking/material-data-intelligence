"""In-memory scientific interpretation persistence."""

from __future__ import annotations

from typing import Any, ContextManager, Mapping

from mdi_schemas import (
    GroundedScientificInterpretation,
    InterpretationExecutionRecord,
    ScientificEvidenceBundle,
)
from mdi_api.infrastructure.persistence.base import _InMemoryRecordRepository, _json_copy
from mdi_api.infrastructure.persistence.interpretation_common import (
    _KeyedLockRegistry,
    validate_interpretation_associations as _validate_interpretation_associations,
    validate_interpretation_run_association as _validate_interpretation_run_association,
)


class InMemoryScientificInterpretationRepository(_InMemoryRecordRepository):
    def __init__(self) -> None:
        super().__init__()
        self.bundles: dict[str, dict[str, Any]] = {}
        self.runs: dict[str, dict[str, Any]] = {}
        self._idempotency_locks = _KeyedLockRegistry()

    def idempotency_guard(self, job_id: str, mode: str, idempotency_key_hash: str) -> ContextManager[None]:
        return self._idempotency_locks.guard((job_id, mode, idempotency_key_hash))

    def save_bundle(self, bundle: ScientificEvidenceBundle | Mapping[str, Any]) -> dict[str, Any]:
        parsed = ScientificEvidenceBundle.model_validate(
            bundle.model_dump(mode="json") if isinstance(bundle, ScientificEvidenceBundle) else bundle
        )
        record = parsed.model_dump(mode="json")
        existing = self.bundles.get(parsed.bundleId)
        if existing is not None and existing["bundleHash"] != parsed.bundleHash:
            raise ValueError("Scientific evidence bundles are immutable")
        self.bundles.setdefault(parsed.bundleId, record)
        return _json_copy(self.bundles[parsed.bundleId])

    def get_bundle(self, bundle_id: str) -> dict[str, Any]:
        try:
            return _json_copy(self.bundles[bundle_id])
        except KeyError as exc:
            raise LookupError(f"Unknown evidence bundle: {bundle_id}") from exc

    def save_run(
        self,
        bundle: ScientificEvidenceBundle | Mapping[str, Any],
        execution: InterpretationExecutionRecord | Mapping[str, Any],
        *,
        interpretation_id: str | None = None,
    ) -> dict[str, Any]:
        parsed_bundle = ScientificEvidenceBundle.model_validate(
            bundle.model_dump(mode="json") if isinstance(bundle, ScientificEvidenceBundle) else bundle
        )
        parsed = InterpretationExecutionRecord.model_validate(
            execution.model_dump(mode="json") if isinstance(execution, InterpretationExecutionRecord) else execution
        )
        self.save_bundle(parsed_bundle)
        _validate_interpretation_run_association(parsed_bundle, parsed)
        record = {
            "execution": parsed.model_dump(mode="json"),
            "bundleId": parsed_bundle.bundleId,
            "jobId": parsed_bundle.jobId,
            "mode": parsed.mode.value,
            "idempotencyKeyHash": parsed.idempotencyKeyHash,
            "interpretationId": interpretation_id,
        }
        existing = self.runs.get(parsed.executionRecordId)
        if existing is not None:
            if existing["execution"]["executionRecordHash"] != parsed.executionRecordHash:
                raise ValueError("Scientific interpretation runs are immutable")
            if existing.get("interpretationId") != interpretation_id:
                raise ValueError("Scientific interpretation run association is immutable")
        for other in self.runs.values():
            if parsed.idempotencyKeyHash and (
                other["jobId"], other["mode"], other["idempotencyKeyHash"]
            ) == (parsed_bundle.jobId, parsed.mode.value, parsed.idempotencyKeyHash) and other["execution"]["executionRecordHash"] != parsed.executionRecordHash:
                raise ValueError("Scientific interpretation idempotency key is already bound to another run")
        self.runs.setdefault(parsed.executionRecordId, record)
        return _json_copy(self.runs[parsed.executionRecordId])

    def get_run_by_idempotency(self, job_id: str, mode: str, idempotency_key_hash: str) -> dict[str, Any] | None:
        for record in self.runs.values():
            if (record["jobId"], record["mode"], record["idempotencyKeyHash"]) == (job_id, mode, idempotency_key_hash):
                return _json_copy(record)
        return None

    def get_run(self, execution_record_id: str) -> dict[str, Any]:
        try:
            return _json_copy(self.runs[execution_record_id])
        except KeyError as exc:
            raise LookupError(f"Unknown interpretation run: {execution_record_id}") from exc

    def list_runs_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for _id, record in sorted(self.runs.items()) if record["jobId"] == job_id]

    def save_interpretation(
        self,
        bundle: ScientificEvidenceBundle | Mapping[str, Any],
        interpretation: GroundedScientificInterpretation | Mapping[str, Any],
        execution: InterpretationExecutionRecord | Mapping[str, Any],
    ) -> dict[str, Any]:
        parsed_bundle = ScientificEvidenceBundle.model_validate(
            bundle.model_dump(mode="json") if isinstance(bundle, ScientificEvidenceBundle) else bundle
        )
        parsed = GroundedScientificInterpretation.model_validate(
            interpretation.model_dump(mode="json")
            if isinstance(interpretation, GroundedScientificInterpretation)
            else interpretation
        )
        execution_record = InterpretationExecutionRecord.model_validate(
            execution.model_dump(mode="json") if isinstance(execution, InterpretationExecutionRecord) else execution
        )
        _validate_interpretation_associations(parsed_bundle, parsed, execution_record)
        record = {
            "interpretation": parsed.model_dump(mode="json"),
            "execution": execution_record.model_dump(mode="json"),
            "bundleId": parsed.sourceBundleId,
            "jobId": parsed.sourceJobId,
        }
        existing = self.records.get(parsed.interpretationId)
        if existing is not None and existing["interpretation"]["interpretationHash"] != parsed.interpretationHash:
            raise ValueError("Scientific interpretations are immutable")
        existing_bundle = self.bundles.get(parsed_bundle.bundleId)
        if existing_bundle is not None and existing_bundle["bundleHash"] != parsed_bundle.bundleHash:
            raise ValueError("Scientific evidence bundles are immutable")
        existing_run = self.runs.get(execution_record.executionRecordId)
        if existing_run is not None and (
            existing_run["execution"]["executionRecordHash"] != execution_record.executionRecordHash
            or existing_run.get("interpretationId") != parsed.interpretationId
        ):
            raise ValueError("Scientific interpretation run association is immutable")
        self.save_bundle(parsed_bundle)
        self.save_run(parsed_bundle, execution_record, interpretation_id=parsed.interpretationId)
        self.records.setdefault(parsed.interpretationId, record)
        return _json_copy(self.records[parsed.interpretationId])

    def get_interpretation(self, interpretation_id: str) -> dict[str, Any]:
        return self._get(interpretation_id)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [
            _json_copy(record)
            for _record_id, record in sorted(self.records.items())
            if record.get("jobId") == job_id
        ]

__all__ = ["InMemoryScientificInterpretationRepository"]
