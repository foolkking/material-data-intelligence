"""SQLAlchemy dependency execution persistence implementation."""

from __future__ import annotations

from typing import Any, Mapping

from sqlalchemy import and_, insert, select
from sqlalchemy.engine import Connection

from mdi_schemas import ArtifactLineageRecord, DependencyBinding, DependencyExecutionRecord
from mdi_api.db import (
    analysis_plans,
    artifact_lineage_records,
    dependency_execution_records,
    plan_dependency_bindings,
    runtime_artifact_binding_resolutions,
)
from mdi_api.infrastructure.persistence.base import _SqlAlchemyRepository, _row_to_json_dict
from mdi_api.infrastructure.persistence.planning_records import (
    _analysis_plan_from_row,
    _artifact_lineage_from_row,
    _artifact_lineage_values,
    _binding_resolution_from_row,
    _binding_resolution_values,
    _dependency_execution_from_row,
    _dependency_execution_values,
    _normalize_artifact_lineage_record,
    _normalize_binding_resolution_record,
    _normalize_dependency_execution_record,
    _normalize_plan_bindings,
    _planned_binding_from_row,
    _planned_binding_values,
)

class SqlAlchemyDependencyExecutionRepository(_SqlAlchemyRepository):
    def save_plan_bindings(
        self, plan_id: str, plan_hash: str, graph_hash: str, bindings: list[DependencyBinding | Mapping[str, Any]]
    ) -> list[dict[str, Any]]:
        plan_row = self._fetch_one_dict(select(analysis_plans).where(analysis_plans.c.id == plan_id))
        normalized = _normalize_plan_bindings(
            _analysis_plan_from_row(plan_row), plan_id, plan_hash, graph_hash, bindings
        )

        def run(connection: Connection) -> None:
            rows = [
                _planned_binding_from_row(_row_to_json_dict(row))
                for row in connection.execute(
                    select(plan_dependency_bindings)
                    .where(plan_dependency_bindings.c.plan_id == plan_id)
                    .order_by(plan_dependency_bindings.c.binding_id)
                ).mappings().all()
            ]
            if rows:
                if rows != sorted(normalized, key=lambda item: item["bindingId"]):
                    raise ValueError("Planned dependency binding records are immutable")
                return
            for item in normalized:
                connection.execute(insert(plan_dependency_bindings).values(**_planned_binding_values(item)))

        self._with_connection(run)
        return self.list_plan_bindings(plan_id)

    def list_plan_bindings(self, plan_id: str) -> list[dict[str, Any]]:
        statement = (
            select(plan_dependency_bindings)
            .where(plan_dependency_bindings.c.plan_id == plan_id)
            .order_by(plan_dependency_bindings.c.binding_id)
        )
        return [_planned_binding_from_row(item) for item in self._fetch_all_dicts(statement)]

    def save_binding_resolution(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_binding_resolution_record(record)
        values = _binding_resolution_values(normalized)

        def run(connection: Connection) -> None:
            row = connection.execute(
                select(runtime_artifact_binding_resolutions).where(
                    and_(
                        runtime_artifact_binding_resolutions.c.job_id == normalized["jobId"],
                        runtime_artifact_binding_resolutions.c.binding_id == normalized["bindingId"],
                    )
                )
            ).mappings().first()
            if row is not None:
                existing = _binding_resolution_from_row(_row_to_json_dict(row))
                if existing["recordHash"] != normalized["recordHash"]:
                    raise ValueError("Runtime artifact binding resolution records are immutable")
                return
            connection.execute(insert(runtime_artifact_binding_resolutions).values(**values))

        self._with_connection(run)
        return next(
            item for item in self.list_binding_resolutions(normalized["jobId"])
            if item["bindingId"] == normalized["bindingId"]
        )

    def list_binding_resolutions(self, job_id: str) -> list[dict[str, Any]]:
        statement = (
            select(runtime_artifact_binding_resolutions)
            .where(runtime_artifact_binding_resolutions.c.job_id == job_id)
            .order_by(runtime_artifact_binding_resolutions.c.binding_id)
        )
        return [_binding_resolution_from_row(item) for item in self._fetch_all_dicts(statement)]

    def save_execution(self, record: DependencyExecutionRecord | Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_dependency_execution_record(record)
        values = _dependency_execution_values(normalized)

        def run(connection: Connection) -> None:
            row = connection.execute(
                select(dependency_execution_records).where(dependency_execution_records.c.job_id == normalized["jobId"])
            ).mappings().first()
            if row is not None:
                existing = _dependency_execution_from_row(_row_to_json_dict(row))
                if existing["executionHash"] != normalized["executionHash"]:
                    raise ValueError("Dependency execution records are immutable")
                return
            connection.execute(insert(dependency_execution_records).values(**values))

        self._with_connection(run)
        return self.get_execution_for_job(normalized["jobId"]) or normalized

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            row = connection.execute(
                select(dependency_execution_records).where(dependency_execution_records.c.job_id == job_id)
            ).mappings().first()
            return _dependency_execution_from_row(_row_to_json_dict(row)) if row is not None else None

        return self._with_connection(run)

    def save_lineage(self, record: ArtifactLineageRecord | Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_artifact_lineage_record(record)
        values = _artifact_lineage_values(normalized)

        def run(connection: Connection) -> None:
            row = connection.execute(
                select(artifact_lineage_records).where(artifact_lineage_records.c.artifact_id == normalized["artifactId"])
            ).mappings().first()
            if row is not None:
                existing = _artifact_lineage_from_row(_row_to_json_dict(row))
                if existing["lineageHash"] != normalized["lineageHash"]:
                    raise ValueError("Artifact lineage records are immutable")
                return
            connection.execute(insert(artifact_lineage_records).values(**values))

        self._with_connection(run)
        return self.get_lineage_for_artifact(normalized["artifactId"]) or normalized

    def list_lineage_for_job(self, job_id: str) -> list[dict[str, Any]]:
        statement = (
            select(artifact_lineage_records)
            .where(artifact_lineage_records.c.job_id == job_id)
            .order_by(artifact_lineage_records.c.artifact_id)
        )
        return [_artifact_lineage_from_row(item) for item in self._fetch_all_dicts(statement)]

    def get_lineage_for_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            row = connection.execute(
                select(artifact_lineage_records).where(artifact_lineage_records.c.artifact_id == artifact_id)
            ).mappings().first()
            return _artifact_lineage_from_row(_row_to_json_dict(row)) if row is not None else None

        return self._with_connection(run)

__all__ = ["SqlAlchemyDependencyExecutionRepository"]
