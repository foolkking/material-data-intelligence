"""SQLAlchemy planning persistence implementations."""

from __future__ import annotations

from typing import Any, Mapping

from sqlalchemy import insert, or_, select
from sqlalchemy.engine import Connection

from mdi_api.db import (
    analysis_intent_executions,
    analysis_intents,
    capability_eligibility_resolutions,
    capability_planning_decisions,
    capability_planning_executions,
)
from mdi_api.infrastructure.persistence.base import _SqlAlchemyRepository, _row_to_json_dict
from mdi_api.infrastructure.persistence.planning import (
    analysis_intent_from_row,
    analysis_intent_values,
    capability_decision_from_row,
    capability_decision_values,
    capability_execution_from_row,
    capability_resolution_from_row,
    capability_resolution_values,
    intent_execution_from_row,
    normalize_analysis_intent_record,
    normalize_capability_decision_record,
    normalize_capability_resolution_record,
)


class SqlAlchemyAnalysisIntentRepository(_SqlAlchemyRepository):
    def save_intent(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = normalize_analysis_intent_record(record)
        intent_id = str(normalized["intentId"])
        values = analysis_intent_values(normalized)

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(analysis_intents).where(analysis_intents.c.id == intent_id)
            ).mappings().first()
            if existing is None:
                connection.execute(insert(analysis_intents).values(**values))
                return
            current = analysis_intent_from_row(_row_to_json_dict(existing))
            if current["intentHash"] != normalized["intentHash"]:
                raise ValueError("AnalysisIntent records are immutable")

        self._with_connection(run)
        return self.get_intent(intent_id)

    def get_intent(self, intent_id: str) -> dict[str, Any]:
        return analysis_intent_from_row(
            self._fetch_one_dict(select(analysis_intents).where(analysis_intents.c.id == intent_id))
        )

    def attach_execution(self, intent_id: str, plan_id: str, job_id: str) -> dict[str, Any]:
        binding_id = f"intent_exec_{intent_id.removeprefix('intent_')[:12]}_{plan_id.removeprefix('plan_')[:12]}_{job_id.removeprefix('job_')[:12]}"

        def run(connection: Connection) -> None:
            exact = connection.execute(
                select(analysis_intent_executions).where(
                    analysis_intent_executions.c.intent_id == intent_id,
                    analysis_intent_executions.c.plan_id == plan_id,
                    analysis_intent_executions.c.job_id == job_id,
                )
            ).mappings().first()
            if exact is not None:
                return
            conflict = connection.execute(
                select(analysis_intent_executions).where(
                    or_(
                        analysis_intent_executions.c.plan_id == plan_id,
                        analysis_intent_executions.c.job_id == job_id,
                    )
                )
            ).mappings().first()
            if conflict is not None:
                raise ValueError("AnalysisIntent execution association is immutable")
            connection.execute(insert(analysis_intent_executions).values(
                id=binding_id, intent_id=intent_id, plan_id=plan_id, job_id=job_id,
            ))

        self._with_connection(run)
        result = self.get_execution_for_job(job_id)
        if result is None:
            raise LookupError(f"Unknown AnalysisIntent execution association: {intent_id}")
        return result

    def get_execution(self, intent_id: str) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            row = connection.execute(
                select(analysis_intent_executions).where(analysis_intent_executions.c.intent_id == intent_id)
            ).mappings().first()
            return intent_execution_from_row(_row_to_json_dict(row)) if row is not None else None

        return self._with_connection(run)

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            row = connection.execute(
                select(analysis_intent_executions).where(analysis_intent_executions.c.job_id == job_id)
            ).mappings().first()
            return intent_execution_from_row(_row_to_json_dict(row)) if row is not None else None

        return self._with_connection(run)


class SqlAlchemyCapabilityPlanningRepository(_SqlAlchemyRepository):
    def save_resolution(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = normalize_capability_resolution_record(record)
        resolution_id = normalized["resolutionId"]
        values = capability_resolution_values(normalized)

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(capability_eligibility_resolutions).where(
                    capability_eligibility_resolutions.c.id == resolution_id
                )
            ).mappings().first()
            if existing is None:
                connection.execute(insert(capability_eligibility_resolutions).values(**values))
                return
            if str(existing["resolution_hash"]) != normalized["resolutionHash"]:
                raise ValueError("Eligibility Resolution records are immutable")

        self._with_connection(run)
        return self.get_resolution(resolution_id)

    def get_resolution(self, resolution_id: str) -> dict[str, Any]:
        return capability_resolution_from_row(
            self._fetch_one_dict(
                select(capability_eligibility_resolutions).where(
                    capability_eligibility_resolutions.c.id == resolution_id
                )
            )
        )

    def save_decision(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = normalize_capability_decision_record(record)
        decision_id = normalized["decisionId"]
        values = capability_decision_values(normalized)

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(capability_planning_decisions).where(
                    capability_planning_decisions.c.id == decision_id
                )
            ).mappings().first()
            if existing is None:
                connection.execute(insert(capability_planning_decisions).values(**values))
                return
            if str(existing["decision_hash"]) != normalized["decisionHash"]:
                raise ValueError("Capability Planning Decision records are immutable")

        self._with_connection(run)
        return self.get_decision(decision_id)

    def get_decision(self, decision_id: str) -> dict[str, Any]:
        return capability_decision_from_row(
            self._fetch_one_dict(
                select(capability_planning_decisions).where(capability_planning_decisions.c.id == decision_id)
            )
        )

    def attach_execution(self, decision_id: str, intent_id: str, plan_id: str, job_id: str) -> dict[str, Any]:
        decision = self.get_decision(decision_id)
        if decision["intentId"] != intent_id or decision["outcome"] != "PLAN_READY":
            raise ValueError("Only a matching PLAN_READY decision can be attached to execution")
        binding_id = f"cap_exec_{decision_id.removeprefix('decision_')[:12]}_{plan_id.removeprefix('plan_')[:12]}_{job_id.removeprefix('job_')[:12]}"

        def run(connection: Connection) -> None:
            exact = connection.execute(
                select(capability_planning_executions).where(
                    capability_planning_executions.c.decision_id == decision_id,
                    capability_planning_executions.c.intent_id == intent_id,
                    capability_planning_executions.c.plan_id == plan_id,
                    capability_planning_executions.c.job_id == job_id,
                )
            ).mappings().first()
            if exact is not None:
                return
            conflict = connection.execute(
                select(capability_planning_executions).where(
                    or_(
                        capability_planning_executions.c.plan_id == plan_id,
                        capability_planning_executions.c.job_id == job_id,
                    )
                )
            ).mappings().first()
            if conflict is not None:
                raise ValueError("Capability Planning execution association is immutable")
            connection.execute(insert(capability_planning_executions).values(
                id=binding_id, decision_id=decision_id, intent_id=intent_id,
                plan_id=plan_id, job_id=job_id,
            ))

        self._with_connection(run)
        result = self.get_execution_for_job(job_id)
        if result is None:
            raise LookupError(f"Unknown Capability Planning execution association: {job_id}")
        return result

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            row = connection.execute(
                select(capability_planning_executions).where(capability_planning_executions.c.job_id == job_id)
            ).mappings().first()
            return capability_execution_from_row(_row_to_json_dict(row)) if row is not None else None

        return self._with_connection(run)


__all__ = ["SqlAlchemyAnalysisIntentRepository", "SqlAlchemyCapabilityPlanningRepository"]
