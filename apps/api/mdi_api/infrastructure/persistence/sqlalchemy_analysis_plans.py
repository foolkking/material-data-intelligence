"""SQLAlchemy AnalysisPlan persistence implementation."""

from __future__ import annotations

from typing import Any, Mapping

from sqlalchemy import func, insert, select
from sqlalchemy.engine import Connection

from mdi_api.db import analysis_plans, jobs
from mdi_api.infrastructure.persistence.base import (
    _SqlAlchemyRepository,
    _json_copy,
    _required_id,
)
from mdi_api.infrastructure.persistence.planning_records import (
    _analysis_plan_from_row,
    _analysis_plan_values,
    _normalize_analysis_plan_record,
)
from mdi_api.infrastructure.persistence.sql_common import ensure_user

class SqlAlchemyAnalysisPlanRepository(_SqlAlchemyRepository):
    def save_plan(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_analysis_plan_record(record)
        plan_id = _required_id(normalized, "planId")
        values = _analysis_plan_values(normalized)

        def run(connection: Connection) -> None:
            ensure_user(connection, user_id=values["created_by"])
            existing = connection.execute(
                select(analysis_plans.c.plan_hash, analysis_plans.c.analysis_plan_json).where(analysis_plans.c.id == plan_id)
            ).mappings().first()
            if existing is None:
                connection.execute(insert(analysis_plans).values(**values))
            else:
                existing_schema = (_json_copy(existing["analysis_plan_json"]) or {}).get("schemaVersion")
                new_schema = normalized["analysisPlan"].get("schemaVersion")
                if "0.2" in {existing_schema, new_schema} and existing["plan_hash"] != normalized["planHash"]:
                    raise ValueError("AnalysisPlan 0.2 records are immutable")
                connection.execute(
                    analysis_plans.update()
                    .where(analysis_plans.c.id == plan_id)
                    .values(**{**values, "updated_at": func.now()})
                )

        self._with_connection(run)
        return self.get_plan(plan_id)

    def get_plan(self, plan_id: str) -> dict[str, Any]:
        return _analysis_plan_from_row(self._fetch_one_dict(select(analysis_plans).where(analysis_plans.c.id == plan_id)))

    def get_plan_for_job(self, job_id: str) -> dict[str, Any]:
        def run(connection: Connection) -> str:
            plan_id = connection.execute(select(jobs.c.plan_id).where(jobs.c.id == job_id)).scalar_one_or_none()
            if plan_id:
                return str(plan_id)
            fallback = connection.execute(select(analysis_plans.c.id).where(analysis_plans.c.job_id == job_id)).scalar_one_or_none()
            if fallback is None:
                raise LookupError(f"Unknown analysis plan for job id: {job_id}")
            return str(fallback)

        return self.get_plan(self._with_connection(run))

    def attach_plan_to_job(self, plan_id: str, job_id: str) -> dict[str, Any]:
        def run(connection: Connection) -> None:
            exists = connection.execute(select(analysis_plans.c.id).where(analysis_plans.c.id == plan_id)).scalar_one_or_none()
            if exists is None:
                raise LookupError(f"Unknown analysis plan id: {plan_id}")
            job_exists = connection.execute(select(jobs.c.id).where(jobs.c.id == job_id)).scalar_one_or_none()
            if job_exists is None:
                raise LookupError(f"Unknown job id: {job_id}")
            connection.execute(
                analysis_plans.update()
                .where(analysis_plans.c.id == plan_id)
                .values(job_id=job_id, updated_at=func.now())
            )
            connection.execute(jobs.update().where(jobs.c.id == job_id).values(plan_id=plan_id, updated_at=func.now()))

        self._with_connection(run)
        return self.get_plan(plan_id)

__all__ = ["SqlAlchemyAnalysisPlanRepository"]
