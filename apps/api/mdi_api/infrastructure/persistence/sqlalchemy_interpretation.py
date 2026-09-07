"""SQLAlchemy scientific interpretation persistence."""

from __future__ import annotations

import hashlib
from contextlib import contextmanager
from typing import Any, Iterator, Mapping

from sqlalchemy import and_, insert, select, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import IntegrityError

from mdi_schemas import (
    GroundedScientificInterpretation,
    InterpretationExecutionRecord,
    ScientificEvidenceBundle,
)
from mdi_api.db import (
    scientific_evidence_bundles,
    scientific_interpretation_claims,
    scientific_interpretation_evidence_links,
    scientific_interpretation_runs,
    scientific_interpretations,
)
from mdi_api.infrastructure.persistence.base import _SqlAlchemyRepository
from mdi_api.infrastructure.persistence.base import _row_to_json_dict
from mdi_api.infrastructure.persistence.interpretation_common import (
    _KeyedLockRegistry,
    validate_interpretation_associations as _validate_interpretation_associations,
    validate_interpretation_run_association as _validate_interpretation_run_association,
)

_SQL_INTERPRETATION_LOCKS = _KeyedLockRegistry()


class SqlAlchemyScientificInterpretationRepository(_SqlAlchemyRepository):
    @contextmanager
    def idempotency_guard(self, job_id: str, mode: str, idempotency_key_hash: str) -> Iterator[None]:
        identity = f"{job_id}\x1f{mode}\x1f{idempotency_key_hash}"
        dialect = self.bind.dialect.name
        if dialect != "postgresql":
            with _SQL_INTERPRETATION_LOCKS.guard((dialect, identity)):
                yield
            return

        advisory_key = int.from_bytes(hashlib.sha256(identity.encode("utf-8")).digest()[:8], "big", signed=True)
        if isinstance(self.bind, Engine):
            with self.bind.connect() as connection:
                connection.execute(text("SELECT pg_advisory_lock(:key)"), {"key": advisory_key})
                try:
                    yield
                finally:
                    connection.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": advisory_key})
            return

        self.bind.execute(text("SELECT pg_advisory_lock(:key)"), {"key": advisory_key})
        try:
            yield
        finally:
            self.bind.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": advisory_key})

    def save_bundle(self, bundle: ScientificEvidenceBundle | Mapping[str, Any]) -> dict[str, Any]:
        parsed = ScientificEvidenceBundle.model_validate(
            bundle.model_dump(mode="json") if isinstance(bundle, ScientificEvidenceBundle) else bundle
        )
        record = parsed.model_dump(mode="json")
        values = {
            "id": parsed.bundleId,
            "bundle_hash": parsed.bundleHash,
            "project_id": parsed.projectId,
            "dataset_id": parsed.datasetId,
            "job_id": parsed.jobId,
            "plan_id": parsed.planId,
            "plan_hash": parsed.planHash,
            "schema_version": parsed.schemaVersion,
            "execution_outcome": parsed.executionOutcome,
            "evidence_item_count": len(parsed.evidenceItems),
            "warning_count": len(parsed.bundleWarnings),
            "limitation_count": len(parsed.bundleLimitations),
            "bundle_json": record,
        }

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(scientific_evidence_bundles.c.bundle_hash).where(scientific_evidence_bundles.c.id == parsed.bundleId)
            ).scalar_one_or_none()
            if existing is not None:
                if existing != parsed.bundleHash:
                    raise ValueError("Scientific evidence bundles are immutable")
                return
            connection.execute(insert(scientific_evidence_bundles).values(**values))

        self._with_connection(run)
        return self.get_bundle(parsed.bundleId)

    def get_bundle(self, bundle_id: str) -> dict[str, Any]:
        row = self._fetch_one_dict(select(scientific_evidence_bundles).where(scientific_evidence_bundles.c.id == bundle_id))
        return ScientificEvidenceBundle.model_validate(row["bundle_json"]).model_dump(mode="json")

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
        values = {
            "id": parsed.executionRecordId,
            "execution_record_hash": parsed.executionRecordHash,
            "bundle_id": parsed_bundle.bundleId,
            "project_id": parsed_bundle.projectId,
            "dataset_id": parsed_bundle.datasetId,
            "job_id": parsed_bundle.jobId,
            "plan_id": parsed_bundle.planId,
            "mode": parsed.mode.value,
            "provider": parsed.provider,
            "provider_model": parsed.providerModel,
            "provider_config_hash": parsed.providerConfigHash,
            "idempotency_key_hash": parsed.idempotencyKeyHash,
            "repair_count": parsed.repairCount,
            "outcome": parsed.outcome.value,
            "interpretation_id": interpretation_id,
            "execution_json": parsed.model_dump(mode="json"),
        }

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(scientific_interpretation_runs).where(scientific_interpretation_runs.c.id == parsed.executionRecordId)
            ).mappings().first()
            if existing is not None:
                if existing["execution_record_hash"] != parsed.executionRecordHash:
                    raise ValueError("Scientific interpretation runs are immutable")
                if existing["interpretation_id"] != interpretation_id:
                    raise ValueError("Scientific interpretation run association is immutable")
                return
            if parsed.idempotencyKeyHash:
                bound = connection.execute(
                    select(scientific_interpretation_runs.c.execution_record_hash).where(
                        and_(
                            scientific_interpretation_runs.c.job_id == parsed_bundle.jobId,
                            scientific_interpretation_runs.c.mode == parsed.mode.value,
                            scientific_interpretation_runs.c.idempotency_key_hash == parsed.idempotencyKeyHash,
                        )
                    )
                ).scalar_one_or_none()
                if bound is not None and bound != parsed.executionRecordHash:
                    raise ValueError("Scientific interpretation idempotency key is already bound to another run")
            connection.execute(insert(scientific_interpretation_runs).values(**values))

        try:
            self._with_connection(run)
        except IntegrityError as exc:
            if parsed.idempotencyKeyHash:
                existing = self.get_run_by_idempotency(
                    parsed_bundle.jobId,
                    parsed.mode.value,
                    parsed.idempotencyKeyHash,
                )
                if existing is not None:
                    if (
                        existing["execution"]["executionRecordHash"] != parsed.executionRecordHash
                        or existing.get("interpretationId") != interpretation_id
                    ):
                        raise ValueError(
                            "Scientific interpretation idempotency key is already bound to another run"
                        ) from exc
                    return existing
            raise
        return self.get_run(parsed.executionRecordId)

    def get_run(self, execution_record_id: str) -> dict[str, Any]:
        row = self._fetch_one_dict(
            select(scientific_interpretation_runs).where(scientific_interpretation_runs.c.id == execution_record_id)
        )
        return {
            "execution": InterpretationExecutionRecord.model_validate(row["execution_json"]).model_dump(mode="json"),
            "bundleId": row["bundle_id"],
            "jobId": row["job_id"],
            "mode": row["mode"],
            "idempotencyKeyHash": row["idempotency_key_hash"],
            "interpretationId": row["interpretation_id"],
        }

    def get_run_by_idempotency(self, job_id: str, mode: str, idempotency_key_hash: str) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            row = connection.execute(
                select(scientific_interpretation_runs).where(
                    and_(
                        scientific_interpretation_runs.c.job_id == job_id,
                        scientific_interpretation_runs.c.mode == mode,
                        scientific_interpretation_runs.c.idempotency_key_hash == idempotency_key_hash,
                    )
                )
            ).mappings().first()
            if row is None:
                return None
            normalized = _row_to_json_dict(row)
            return {
                "execution": InterpretationExecutionRecord.model_validate(normalized["execution_json"]).model_dump(mode="json"),
                "bundleId": normalized["bundle_id"],
                "jobId": normalized["job_id"],
                "mode": normalized["mode"],
                "idempotencyKeyHash": normalized["idempotency_key_hash"],
                "interpretationId": normalized["interpretation_id"],
            }
        return self._with_connection(run)

    def list_runs_for_job(self, job_id: str) -> list[dict[str, Any]]:
        rows = self._fetch_all_dicts(
            select(scientific_interpretation_runs)
            .where(scientific_interpretation_runs.c.job_id == job_id)
            .order_by(scientific_interpretation_runs.c.created_at, scientific_interpretation_runs.c.id)
        )
        return [
            {
                "execution": InterpretationExecutionRecord.model_validate(row["execution_json"]).model_dump(mode="json"),
                "bundleId": row["bundle_id"],
                "jobId": row["job_id"],
                "mode": row["mode"],
                "idempotencyKeyHash": row["idempotency_key_hash"],
                "interpretationId": row["interpretation_id"],
            }
            for row in rows
        ]
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
        evidence = {item.evidenceItemId: item for item in parsed_bundle.evidenceItems}
        interpretation_values = {
            "id": parsed.interpretationId,
            "interpretation_hash": parsed.interpretationHash,
            "bundle_id": parsed.sourceBundleId,
            "project_id": parsed_bundle.projectId,
            "dataset_id": parsed_bundle.datasetId,
            "job_id": parsed.sourceJobId,
            "plan_id": parsed.sourcePlanId,
            "mode": parsed.mode.value,
            "provider": parsed.provider,
            "repair_count": parsed.repairCount,
            "outcome": parsed.outcome.value,
            "execution_record_id": execution_record.executionRecordId,
            "interpretation_json": parsed.model_dump(mode="json"),
            "execution_json": execution_record.model_dump(mode="json"),
        }

        def run(connection: Connection) -> None:
            scoped = SqlAlchemyScientificInterpretationRepository(connection)
            scoped.save_bundle(parsed_bundle)
            scoped.save_run(parsed_bundle, execution_record, interpretation_id=parsed.interpretationId)
            existing = connection.execute(
                select(scientific_interpretations).where(scientific_interpretations.c.id == parsed.interpretationId)
            ).mappings().first()
            if existing is not None:
                if (
                    existing["interpretation_hash"] != parsed.interpretationHash
                    or existing["execution_record_id"] != execution_record.executionRecordId
                    or existing["bundle_id"] != parsed_bundle.bundleId
                ):
                    raise ValueError("Scientific interpretations are immutable")
                return
            connection.execute(insert(scientific_interpretations).values(**interpretation_values))
            for claim in parsed.claims:
                connection.execute(insert(scientific_interpretation_claims).values(
                    interpretation_id=parsed.interpretationId,
                    claim_id=claim.claimId,
                    claim_type=claim.claimType.value,
                    predicate=claim.semanticPredicate.value,
                    confidence_class=claim.confidenceClass.value,
                    grounding_status=claim.groundingStatus.value,
                    display_order=claim.displayOrder,
                    claim_json=claim.model_dump(mode="json"),
                ))
                roles = {
                    "SUPPORTING": set(claim.subjectEvidenceIds + claim.supportingEvidenceIds),
                    "LIMITING": set(claim.limitingEvidenceIds),
                    "CONTRADICTING": set(claim.contradictingEvidenceIds),
                }
                for role, evidence_ids in roles.items():
                    for evidence_id in sorted(evidence_ids):
                        item = evidence[evidence_id]
                        connection.execute(insert(scientific_interpretation_evidence_links).values(
                            interpretation_id=parsed.interpretationId,
                            claim_id=claim.claimId,
                            evidence_item_id=evidence_id,
                            role=role,
                            source_artifact_id=item.sourceArtifactId,
                            source_artifact_hash=item.sourceArtifactChecksum,
                            field_locator_json=item.fieldLocator.model_dump(mode="json"),
                        ))

        self._with_connection(run)
        return self.get_interpretation(parsed.interpretationId)

    def get_interpretation(self, interpretation_id: str) -> dict[str, Any]:
        row = self._fetch_one_dict(
            select(scientific_interpretations).where(scientific_interpretations.c.id == interpretation_id)
        )
        return {
            "interpretation": GroundedScientificInterpretation.model_validate(row["interpretation_json"]).model_dump(mode="json"),
            "execution": InterpretationExecutionRecord.model_validate(row["execution_json"]).model_dump(mode="json"),
            "bundleId": row["bundle_id"],
            "jobId": row["job_id"],
        }

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        rows = self._fetch_all_dicts(
            select(scientific_interpretations)
            .where(scientific_interpretations.c.job_id == job_id)
            .order_by(scientific_interpretations.c.created_at, scientific_interpretations.c.id)
        )
        return [
            {
                "interpretation": GroundedScientificInterpretation.model_validate(row["interpretation_json"]).model_dump(mode="json"),
                "execution": InterpretationExecutionRecord.model_validate(row["execution_json"]).model_dump(mode="json"),
                "bundleId": row["bundle_id"],
                "jobId": row["job_id"],
            }
            for row in rows
        ]

__all__ = ["SqlAlchemyScientificInterpretationRepository"]
