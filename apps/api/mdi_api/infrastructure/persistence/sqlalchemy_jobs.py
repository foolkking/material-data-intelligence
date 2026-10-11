from __future__ import annotations

from datetime import timedelta
from threading import Lock
from typing import Any, Mapping, Sequence

from sqlalchemy import and_, delete, func, insert, or_, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Connection, Engine

from mdi_schemas import AnalysisPlanV03, JobEvent, JobEventStatus, JobStatus, ToolCall
from mdi_api.db import (
    analysis_intent_executions,
    analysis_intents,
    analysis_plans,
    artifacts,
    capability_eligibility_resolutions,
    capability_planning_decisions,
    capability_planning_executions,
    data_profiles,
    dependency_execution_records,
    datasets,
    jobs,
    messages,
    research_turns,
    scientific_interpretations,
    scientific_workspaces,
    tool_calls,
    job_events,
)
from mdi_api.infrastructure.persistence.base import (
    _SqlAlchemyRepository,
    _enum_value,
    _iso,
    _json_copy,
    _model_to_record,
    _parse_iso,
    _required_id,
    _utc_now,
    _row_to_json_dict,
)
from mdi_api.infrastructure.persistence.sql_common import ensure_user
from mdi_api.state_machine import (
    validate_job_status,
    validate_job_transition,
    validate_tool_call_status,
    validate_tool_call_transition,
)
from mdi_api.application.jobs.leases import ExecutionLease, ExecutionLeaseLost


_JOB_TERMINAL = {"completed", "partial_success", "cancelled"}

class SqlAlchemyJobRepository(_SqlAlchemyRepository):
    def create(self, job: Mapping[str, Any]) -> dict[str, Any]:
        job_id = _required_id(job, "jobId")
        created_by = str(job.get("createdBy") or job.get("created_by") or "user_local")
        status = validate_job_status(job.get("status") or JobStatus.created.value)
        values = {
            "id": job_id,
            "project_id": str(job["projectId"]),
            "dataset_id": job.get("datasetId") or job.get("dataset_id"),
            "plan_id": job.get("planId") or job.get("plan_id"),
            "kind": str(job.get("kind") or "analysis"),
            "status": status,
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            existing = connection.execute(select(jobs.c.id).where(jobs.c.id == job_id)).scalar_one_or_none()
            if existing is not None:
                return
            ensure_user(connection, user_id=created_by)
            connection.execute(insert(jobs).values(**values))

        self._with_connection(run)
        return self.get(job_id)

    def save(self, job: Mapping[str, Any]) -> dict[str, Any]:
        job_id = _required_id(job, "jobId")
        created_by = str(job.get("createdBy") or job.get("created_by") or "user_local")
        status = validate_job_status(job.get("status") or JobStatus.created.value)
        values = {
            "id": job_id,
            "project_id": str(job["projectId"]),
            "dataset_id": job.get("datasetId"),
            "plan_id": job.get("planId") or job.get("plan_id"),
            "kind": str(job.get("kind") or "analysis"),
            "status": status,
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            ensure_user(connection, user_id=created_by)
            connection.execute(delete(jobs).where(jobs.c.id == job_id))
            connection.execute(insert(jobs).values(**values))

        self._with_connection(run)
        return self.get(job_id)

    def get(self, job_id: str) -> dict[str, Any]:
        return _job_from_row(self._fetch_one_dict(select(jobs).where(jobs.c.id == job_id)))

    def set_status(self, job_id: str, status: JobStatus | str) -> dict[str, Any]:
        def run(connection: Connection) -> None:
            current = connection.execute(select(jobs.c.status).where(jobs.c.id == job_id)).scalar_one_or_none()
            if current is None:
                raise LookupError(f"Unknown job id: {job_id}")
            next_status = validate_job_transition(current, status)
            connection.execute(jobs.update().where(jobs.c.id == job_id).values(status=next_status, updated_at=func.now()))

        self._with_connection(run)
        return self.get(job_id)

    def claim_execution(
        self,
        job_id: str,
        *,
        owner: str,
        lease_seconds: int,
    ) -> ExecutionLease | None:
        if not owner.strip():
            raise ValueError("execution owner is required")
        if lease_seconds < 1:
            raise ValueError("lease_seconds must be positive")

        def run(connection: Connection) -> ExecutionLease | None:
            row = connection.execute(
                select(jobs).where(jobs.c.id == job_id).with_for_update()
            ).mappings().first()
            if row is None:
                raise LookupError(f"Unknown job id: {job_id}")
            current = _row_to_json_dict(row)
            status = str(current["status"])
            server_now = connection.execute(select(func.now())).scalar_one()
            expires_at = current.get("lease_expires_at")
            if status in _JOB_TERMINAL or status in {"failed", "cancel_requested"}:
                return None
            if (
                status == "running"
                and expires_at is not None
                and expires_at > server_now
            ):
                return None
            reclaimed = status == "running"
            attempt = int(current.get("execution_attempt") or 0) + 1
            new_expiry = server_now + timedelta(seconds=lease_seconds)
            connection.execute(
                update(jobs)
                .where(jobs.c.id == job_id)
                .values(
                    status="running",
                    execution_owner=owner,
                    execution_attempt=attempt,
                    lease_claimed_at=server_now,
                    lease_renewed_at=server_now,
                    lease_expires_at=new_expiry,
                    updated_at=server_now,
                )
            )
            return ExecutionLease(
                job_id=job_id,
                owner=owner,
                attempt=attempt,
                claimed_at=_iso(server_now),
                renewed_at=_iso(server_now),
                expires_at=_iso(new_expiry),
                reclaimed=reclaimed,
            )

        return self._with_connection(run)

    def renew_execution(
        self,
        job_id: str,
        *,
        owner: str,
        attempt: int,
        lease_seconds: int,
    ) -> ExecutionLease:
        if lease_seconds < 1:
            raise ValueError("lease_seconds must be positive")

        def run(connection: Connection) -> ExecutionLease:
            server_now = connection.execute(select(func.now())).scalar_one()
            new_expiry = server_now + timedelta(seconds=lease_seconds)
            result = connection.execute(
                update(jobs)
                .where(
                    jobs.c.id == job_id,
                    jobs.c.status.in_(("running", "cancel_requested")),
                    jobs.c.execution_owner == owner,
                    jobs.c.execution_attempt == attempt,
                    jobs.c.lease_expires_at > server_now,
                )
                .values(
                    lease_renewed_at=server_now,
                    lease_expires_at=new_expiry,
                    updated_at=server_now,
                )
            )
            if result.rowcount != 1:
                raise ExecutionLeaseLost(
                    f"execution lease is no longer current for {job_id} attempt {attempt}"
                )
            row = connection.execute(
                select(jobs).where(jobs.c.id == job_id)
            ).mappings().one()
            return _execution_lease_from_row(row, reclaimed=False)

        return self._with_connection(run)

    def assert_current_execution(
        self,
        job_id: str,
        *,
        owner: str,
        attempt: int,
    ) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            server_now = connection.execute(select(func.now())).scalar_one()
            row = connection.execute(
                select(jobs).where(
                    jobs.c.id == job_id,
                    jobs.c.status.in_(("running", "cancel_requested")),
                    jobs.c.execution_owner == owner,
                    jobs.c.execution_attempt == attempt,
                    jobs.c.lease_expires_at > server_now,
                )
            ).mappings().first()
            if row is None:
                raise ExecutionLeaseLost(
                    f"execution lease is no longer current for {job_id} attempt {attempt}"
                )
            return _job_from_row(row)

        return self._with_connection(run)

    def set_status_for_execution(
        self,
        job_id: str,
        status: JobStatus | str,
        *,
        owner: str,
        attempt: int,
    ) -> dict[str, Any]:
        requested = validate_job_status(status)

        def run(connection: Connection) -> None:
            row = connection.execute(
                select(jobs).where(jobs.c.id == job_id).with_for_update()
            ).mappings().first()
            if row is None:
                raise LookupError(f"Unknown job id: {job_id}")
            current = _row_to_json_dict(row)
            server_now = connection.execute(select(func.now())).scalar_one()
            if (
                str(current.get("execution_owner") or "") != owner
                or int(current.get("execution_attempt") or 0) != attempt
                or current.get("lease_expires_at") is None
                or current["lease_expires_at"] <= server_now
            ):
                raise ExecutionLeaseLost(
                    f"stale authoritative write rejected for {job_id} attempt {attempt}"
                )
            current_status = str(current["status"])
            if current_status == "cancel_requested" and requested != "cancelled":
                raise ExecutionLeaseLost(
                    f"cancellation has precedence for {job_id} attempt {attempt}"
                )
            next_status = validate_job_transition(current_status, requested)
            terminal = next_status in _JOB_TERMINAL or next_status == "failed"
            values: dict[str, Any] = {
                "status": next_status,
                "updated_at": server_now,
            }
            if terminal:
                values.update(
                    terminal_at=server_now,
                    lease_expires_at=None,
                    execution_owner=None,
                )
            if next_status == "cancelled":
                values["cancel_acknowledged_at"] = server_now
            connection.execute(
                update(jobs).where(jobs.c.id == job_id).values(**values)
            )

        self._with_connection(run)
        return self.get(job_id)

    def expire_abandoned_execution(
        self, job_id: str, *, stale_after_seconds: int, cancel_requested: bool = False
    ) -> dict[str, Any] | None:
        """End an inactive queue wait or execution with no current database lease.

        Reclaim/renewal/completion and expiry serialize on the Job row. Failed
        Jobs require an explicit transition to queued before a new claim.
        """
        if stale_after_seconds < 1:
            raise ValueError("stale_after_seconds must be positive")

        def run(connection: Connection) -> dict[str, Any] | None:
            current = connection.execute(
                select(jobs).where(jobs.c.id == job_id).with_for_update()
            ).mappings().one()
            server_now = connection.execute(select(func.now())).scalar_one()
            if (
                current["status"] not in {"created", "queued", "running", "cancel_requested"}
                or current["updated_at"] > server_now - timedelta(seconds=stale_after_seconds)
                or (current["lease_expires_at"] is not None and current["lease_expires_at"] > server_now)
            ):
                return None
            cancelled = cancel_requested or current["status"] == "cancel_requested"
            values = dict(
                status="cancelled" if cancelled else "failed",
                execution_owner=None, lease_expires_at=None,
                terminal_at=server_now, updated_at=server_now,
            )
            if cancelled:
                values.update(
                    cancel_requested_at=current["cancel_requested_at"] or server_now,
                    cancel_acknowledged_at=server_now,
                )
            connection.execute(update(jobs).where(jobs.c.id == job_id).values(**values))
            return _job_from_row(connection.execute(select(jobs).where(jobs.c.id == job_id)).mappings().one())

        return self._with_connection(run)

    def request_cancel(self, job_id: str) -> dict[str, Any]:
        def run(connection: Connection) -> None:
            row = connection.execute(
                select(jobs).where(jobs.c.id == job_id).with_for_update()
            ).mappings().first()
            if row is None:
                raise LookupError(f"Unknown job id: {job_id}")
            current = _row_to_json_dict(row)
            status = str(current["status"])
            if status in _JOB_TERMINAL or status == "failed":
                return
            next_status = validate_job_transition(status, "cancel_requested")
            server_now = connection.execute(select(func.now())).scalar_one()
            connection.execute(
                update(jobs)
                .where(jobs.c.id == job_id)
                .values(
                    status=next_status,
                    cancel_requested_at=current.get("cancel_requested_at")
                    or server_now,
                    updated_at=server_now,
                )
            )

        self._with_connection(run)
        return self.get(job_id)

    def acknowledge_cancel(
        self,
        job_id: str,
        *,
        owner: str | None = None,
        attempt: int | None = None,
    ) -> dict[str, Any]:
        if owner is not None and attempt is not None:
            return self.set_status_for_execution(
                job_id, "cancelled", owner=owner, attempt=attempt
            )

        def run(connection: Connection) -> None:
            row = connection.execute(
                select(jobs).where(jobs.c.id == job_id).with_for_update()
            ).mappings().first()
            if row is None:
                raise LookupError(f"Unknown job id: {job_id}")
            current = _row_to_json_dict(row)
            if str(current["status"]) != "cancel_requested":
                return
            if current.get("execution_owner"):
                raise ExecutionLeaseLost(
                    "an active owner must acknowledge its own cancellation"
                )
            server_now = connection.execute(select(func.now())).scalar_one()
            connection.execute(
                update(jobs)
                .where(jobs.c.id == job_id)
                .values(
                    status="cancelled",
                    cancel_acknowledged_at=server_now,
                    terminal_at=server_now,
                    updated_at=server_now,
                )
            )

        self._with_connection(run)
        return self.get(job_id)

    def lifecycle_projection(self, job_id: str) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(
                select(jobs).where(jobs.c.id == job_id)
            ).mappings().first()
            if row is None:
                raise LookupError(f"Unknown job id: {job_id}")
            current = _row_to_json_dict(row)
            server_now = connection.execute(select(func.now())).scalar_one()
            expiry = current.get("lease_expires_at")
            status = str(current["status"])
            return {
                "executionState": status,
                "attempt": int(current.get("execution_attempt") or 0),
                "ownerPresent": bool(current.get("execution_owner")),
                "leaseStatus": (
                    "EXPIRED"
                    if status == "running" and expiry is not None and expiry <= server_now
                    else "ACTIVE"
                    if status == "running" and expiry is not None
                    else "NOT_APPLICABLE"
                ),
                "leaseExpiresAt": _iso(expiry) if expiry is not None else None,
                "cancelRequested": status == "cancel_requested"
                or current.get("cancel_requested_at") is not None,
                "cancelRequestedAt": _iso(current["cancel_requested_at"])
                if current.get("cancel_requested_at")
                else None,
                "cancelAcknowledgedAt": _iso(current["cancel_acknowledged_at"])
                if current.get("cancel_acknowledged_at")
                else None,
                "terminalAt": _iso(current["terminal_at"])
                if current.get("terminal_at")
                else None,
                "authority": "POSTGRESQL_JOB_ROW",
                "readOnly": True,
            }

        return self._with_connection(run)

    def update_status(self, job_id: str, status: JobStatus | str) -> dict[str, Any]:
        return self.set_status(job_id, status)

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        statement = select(jobs).where(jobs.c.project_id == project_id).order_by(jobs.c.created_at.desc(), jobs.c.id)
        return [_job_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_task_feed_projection(
        self,
        job_ids: Sequence[str],
    ) -> list[dict[str, Any]]:
        """Load page metadata, batching additional multi-dataset source names."""

        normalized_ids = tuple(dict.fromkeys(str(job_id) for job_id in job_ids if job_id))
        if not normalized_ids:
            return []

        fallback_plans = analysis_plans.alias("fallback_analysis_plans")
        fallback_plan_id = (
            select(fallback_plans.c.id)
            .where(fallback_plans.c.job_id == jobs.c.id)
            .order_by(fallback_plans.c.created_at.desc(), fallback_plans.c.id)
            .limit(1)
            .correlate(jobs)
            .scalar_subquery()
        )
        effective_plan_id = func.coalesce(jobs.c.plan_id, fallback_plan_id)
        artifact_count = (
            select(func.count())
            .select_from(artifacts)
            .where(artifacts.c.job_id == jobs.c.id)
            .scalar_subquery()
        )
        interpretation_count = (
            select(func.count())
            .select_from(scientific_interpretations)
            .where(scientific_interpretations.c.job_id == jobs.c.id)
            .scalar_subquery()
        )
        source = (
            jobs
            .outerjoin(datasets, datasets.c.id == jobs.c.dataset_id)
            .outerjoin(analysis_plans, analysis_plans.c.id == effective_plan_id)
            .outerjoin(data_profiles, data_profiles.c.id == analysis_plans.c.profile_id)
            .outerjoin(
                analysis_intent_executions,
                analysis_intent_executions.c.job_id == jobs.c.id,
            )
            .outerjoin(
                analysis_intents,
                analysis_intents.c.id == analysis_intent_executions.c.intent_id,
            )
            .outerjoin(
                capability_planning_executions,
                capability_planning_executions.c.job_id == jobs.c.id,
            )
            .outerjoin(
                capability_planning_decisions,
                capability_planning_decisions.c.id
                == capability_planning_executions.c.decision_id,
            )
            .outerjoin(
                capability_eligibility_resolutions,
                capability_eligibility_resolutions.c.id
                == capability_planning_decisions.c.resolution_id,
            )
            .outerjoin(
                dependency_execution_records,
                dependency_execution_records.c.job_id == jobs.c.id,
            )
            .outerjoin(research_turns, and_(
                research_turns.c.job_id == jobs.c.id,
                research_turns.c.project_id == jobs.c.project_id,
            ))
            .outerjoin(messages, and_(
                messages.c.id == research_turns.c.user_message_id,
                messages.c.session_id == research_turns.c.research_session_id,
            ))
            .outerjoin(
                scientific_workspaces,
                and_(
                    scientific_workspaces.c.project_id == jobs.c.project_id,
                    scientific_workspaces.c.source_job_id == jobs.c.id,
                ),
            )
        )
        statement = (
            select(
                jobs.c.id.label("job_id"),
                datasets.c.id.label("dataset_exists_id"),
                datasets.c.project_id.label("dataset_project_id"),
                datasets.c.name.label("dataset_name"),
                analysis_plans.c.id.label("plan_id"),
                analysis_plans.c.project_id.label("plan_project_id"),
                analysis_plans.c.dataset_id.label("plan_dataset_id"),
                analysis_plans.c.profile_id.label("plan_profile_id"),
                analysis_plans.c.analysis_plan_json.label("plan_json"),
                analysis_plans.c.plan_hash.label("plan_hash"),
                data_profiles.c.id.label("profile_id"),
                data_profiles.c.profile_json.label("profile_json"),
                analysis_intents.c.id.label("intent_id"),
                analysis_intents.c.intent_json.label("intent_json"),
                capability_eligibility_resolutions.c.id.label("resolution_id"),
                capability_eligibility_resolutions.c.resolution_json.label(
                    "resolution_json"
                ),
                capability_planning_decisions.c.id.label("decision_id"),
                capability_planning_decisions.c.decision_json.label("decision_json"),
                dependency_execution_records.c.record_json.label("dependency_json"),
                dependency_execution_records.c.outcome.label("dependency_outcome"),
                research_turns.c.id.label("research_turn_id"),
                research_turns.c.research_session_id.label("research_session_id"),
                messages.c.content_summary.label("research_question"),
                scientific_workspaces.c.workspace_id.label("workspace_id"),
                artifact_count.label("artifact_count"),
                interpretation_count.label("interpretation_count"),
            )
            .select_from(source)
            .where(jobs.c.id.in_(normalized_ids))
        )
        records = self._fetch_all_dicts(statement)
        multi_source_ids: dict[str, list[str]] = {}
        for record in records:
            try:
                plan = AnalysisPlanV03.model_validate(record.get("plan_json"))
            except (TypeError, ValueError):
                continue
            multi_source_ids[record["job_id"]] = [item.datasetId for item in plan.sourceContexts]
        dataset_ids = {dataset_id for ids in multi_source_ids.values() for dataset_id in ids}
        sources = self._fetch_all_dicts(
            select(datasets.c.id, datasets.c.project_id, datasets.c.name)
            .where(datasets.c.id.in_(dataset_ids))
        ) if dataset_ids else []
        sources_by_id = {
            item["id"]: {"datasetId": item["id"], "projectId": item["project_id"], "name": item["name"]}
            for item in sources
        }
        for record in records:
            if record["job_id"] in multi_source_ids:
                record["source_datasets"] = [
                    sources_by_id[dataset_id] for dataset_id in multi_source_ids[record["job_id"]]
                    if dataset_id in sources_by_id
                ]
            else:
                record["source_datasets"] = [{
                    "datasetId": record["dataset_exists_id"],
                    "projectId": record["dataset_project_id"],
                    "name": record["dataset_name"],
                }] if record["dataset_exists_id"] else []
        return records

class SqlAlchemyJobEventRepository(_SqlAlchemyRepository):
    POSTGRES_ADVISORY_LOCK_SQL = "SELECT pg_advisory_xact_lock(hashtext('mdi_job_events'), hashtext(:job_id))"

    def __init__(self, bind: Engine | Connection) -> None:
        super().__init__(bind)
        self._event_lock = Lock()

    def append_event(
        self,
        job_id: str,
        *,
        event_type: str,
        status: JobEventStatus | str,
        message: str,
        payload: Mapping[str, Any] | None = None,
        progress: float | None = None,
    ) -> JobEvent:
        def run(connection: Connection) -> JobEvent:
            _lock_job_event_sequence(connection, job_id)
            max_seq = connection.execute(select(func.max(job_events.c.seq)).where(job_events.c.job_id == job_id)).scalar()
            seq = int(max_seq or 0) + 1
            event = JobEvent(
                id=f"evt_{job_id}_{seq:04d}",
                jobId=job_id,
                seq=seq,
                eventType=event_type,
                status=JobEventStatus(_enum_value(status)),
                message=message,
                progress=progress,
                payload=dict(payload or {}),
                createdAt=_utc_now(),
            )
            connection.execute(insert(job_events).values(**_job_event_values(event)))
            return event

        with self._event_lock:
            return self._with_connection(run)

    def list_for_job(self, job_id: str) -> list[JobEvent]:
        return self.list_events_after_seq(job_id, 0)

    def list_events(self, job_id: str) -> list[JobEvent]:
        return self.list_for_job(job_id)

    def list_events_after_seq(self, job_id: str, after_seq: int) -> list[JobEvent]:
        statement = (
            select(job_events)
            .where(job_events.c.job_id == job_id, job_events.c.seq > after_seq)
            .order_by(job_events.c.seq)
        )
        return [_job_event_from_row(row) for row in self._fetch_all_dicts(statement)]

def _lock_job_event_sequence(connection: Connection, job_id: str) -> None:
    if connection.dialect.name.startswith("postgresql"):
        connection.execute(text(SqlAlchemyJobEventRepository.POSTGRES_ADVISORY_LOCK_SQL), {"job_id": job_id})

class SqlAlchemyToolCallRepository(_SqlAlchemyRepository):
    def save(self, tool_call: ToolCall | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(tool_call)
        tool_call_id = _required_id(record)
        job_id = str(record["jobId"])
        step_id = str(record["stepId"])
        idempotency_key = str(record.get("idempotencyKey") or record.get("idempotency_key") or f"{job_id}:{step_id}")
        status = validate_tool_call_status(record.get("status") or "planned")
        values = {
            "id": tool_call_id,
            "job_id": job_id,
            "step_id": step_id,
            "tool_id": str(record["toolId"]),
            "idempotency_key": idempotency_key,
            "attempt": int(record.get("attempt") or 1),
            "status": status,
            "params_json": _json_copy(record.get("params") or {}),
            "error_json": _json_copy(record.get("error")) if record.get("error") else None,
        }

        def run(connection: Connection) -> str:
            existing = connection.execute(
                select(tool_calls).where(
                    or_(
                        tool_calls.c.id == tool_call_id,
                        and_(tool_calls.c.job_id == job_id, tool_calls.c.step_id == step_id),
                        and_(tool_calls.c.job_id == job_id, tool_calls.c.idempotency_key == idempotency_key),
                    )
                )
            ).mappings().first()
            if existing is None:
                connection.execute(insert(tool_calls).values(**values))
                return tool_call_id
            existing_row = _row_to_json_dict(existing)
            existing_id = str(existing_row["id"])
            next_status = validate_tool_call_transition(existing_row.get("status") or "planned", status)
            update_values = {**values, "id": existing_id, "status": next_status, "attempt": max(int(existing_row.get("attempt") or 1), values["attempt"])}
            connection.execute(tool_calls.update().where(tool_calls.c.id == existing_id).values(**update_values, updated_at=func.now()))
            return existing_id

        try:
            stored_id = self._with_connection(run)
        except IntegrityError as exc:
            # Independent workers can race between the existence check and
            # INSERT.  The database uniqueness boundary is authoritative:
            # after the losing transaction rolls back, converge on the
            # committed ToolCall instead of surfacing a duplicate-delivery
            # error.  Re-raise unrelated integrity failures.
            existing = self._fetch_one_dict(
                select(tool_calls).where(
                    or_(
                        tool_calls.c.id == tool_call_id,
                        and_(tool_calls.c.job_id == job_id, tool_calls.c.step_id == step_id),
                        and_(tool_calls.c.job_id == job_id, tool_calls.c.idempotency_key == idempotency_key),
                    )
                )
            )
            if existing is None:
                raise
            existing_row = _row_to_json_dict(existing)
            if (
                str(existing_row.get("tool_id") or "") != str(record["toolId"])
                or str(existing_row.get("job_id") or "") != job_id
                or str(existing_row.get("step_id") or "") != step_id
            ):
                raise ValueError("ToolCall idempotency key is already bound to a different tool step.") from exc
            stored_id = str(existing_row["id"])
        return self.get(stored_id)

    def save_for_execution(
        self,
        tool_call: ToolCall | Mapping[str, Any],
        *,
        owner: str,
        attempt: int,
    ) -> dict[str, Any]:
        record = _model_to_record(tool_call)
        record["attempt"] = attempt
        job_id = str(record["jobId"])

        def run(connection: Connection) -> str:
            server_now = connection.execute(select(func.now())).scalar_one()
            job = connection.execute(
                select(jobs).where(
                    jobs.c.id == job_id,
                    jobs.c.status.in_(("running", "cancel_requested")),
                    jobs.c.execution_owner == owner,
                    jobs.c.execution_attempt == attempt,
                    jobs.c.lease_expires_at > server_now,
                )
            ).mappings().first()
            if job is None:
                raise ExecutionLeaseLost(
                    f"stale ToolCall write rejected for {job_id} attempt {attempt}"
                )
            return self._save_on_connection(connection, record, attempt=attempt)

        stored_id = self._with_connection(run)
        return self.get(stored_id)

    def _save_on_connection(
        self,
        connection: Connection,
        record: Mapping[str, Any],
        *,
        attempt: int,
    ) -> str:
        tool_call_id = _required_id(record)
        job_id = str(record["jobId"])
        step_id = str(record["stepId"])
        idempotency_key = str(
            record.get("idempotencyKey")
            or record.get("idempotency_key")
            or f"{job_id}:{step_id}"
        )
        status = validate_tool_call_status(record.get("status") or "planned")
        values = {
            "id": tool_call_id,
            "job_id": job_id,
            "step_id": step_id,
            "tool_id": str(record["toolId"]),
            "idempotency_key": idempotency_key,
            "attempt": attempt,
            "status": status,
            "params_json": _json_copy(record.get("params") or {}),
            "error_json": _json_copy(record.get("error"))
            if record.get("error")
            else None,
        }
        existing = connection.execute(
            select(tool_calls)
            .where(
                or_(
                    tool_calls.c.id == tool_call_id,
                    and_(
                        tool_calls.c.job_id == job_id,
                        tool_calls.c.step_id == step_id,
                    ),
                    and_(
                        tool_calls.c.job_id == job_id,
                        tool_calls.c.idempotency_key == idempotency_key,
                    ),
                )
            )
            .with_for_update()
        ).mappings().first()
        if existing is None:
            connection.execute(insert(tool_calls).values(**values))
            return tool_call_id
        existing_row = _row_to_json_dict(existing)
        existing_attempt = int(existing_row.get("attempt") or 1)
        if existing_attempt > attempt:
            raise ExecutionLeaseLost(
                f"stale ToolCall attempt {attempt} rejected; current is {existing_attempt}"
            )
        existing_id = str(existing_row["id"])
        if existing_attempt < attempt:
            next_status = status
        else:
            next_status = validate_tool_call_transition(
                existing_row.get("status") or "planned", status
            )
        connection.execute(
            update(tool_calls)
            .where(tool_calls.c.id == existing_id)
            .values(
                **{
                    **values,
                    "id": existing_id,
                    "status": next_status,
                    "attempt": attempt,
                },
                updated_at=func.now(),
            )
        )
        return existing_id

    def get(self, tool_call_id: str) -> dict[str, Any]:
        return _tool_call_from_row(self._fetch_one_dict(select(tool_calls).where(tool_calls.c.id == tool_call_id)))

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        statement = select(tool_calls).where(tool_calls.c.job_id == job_id).order_by(tool_calls.c.created_at, tool_calls.c.id)
        return [_tool_call_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_by_job(self, job_id: str) -> list[dict[str, Any]]:
        return self.list_for_job(job_id)

def _job_event_values(event: JobEvent) -> dict[str, Any]:
    return {
        "id": event.id,
        "job_id": event.jobId,
        "seq": event.seq,
        "event_type": event.eventType,
        "status": event.status.value,
        "message": event.message,
        "progress": event.progress,
        "payload_json": event.payload or {},
        "created_at": _parse_iso(event.createdAt),
    }

def _job_event_from_row(row: Mapping[str, Any]) -> JobEvent:
    return JobEvent(
        id=str(row["id"]),
        jobId=str(row["job_id"]),
        seq=int(row["seq"]),
        eventType=str(row["event_type"]),
        status=JobEventStatus(str(row["status"])),
        message=str(row["message"]),
        progress=row.get("progress"),
        payload=_json_copy(row.get("payload_json") or {}),
        createdAt=_iso(row["created_at"]),
    )

def _job_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "jobId": row["id"],
        "projectId": row["project_id"],
        "datasetId": row["dataset_id"],
        "planId": row.get("plan_id"),
        "kind": row["kind"],
        "status": row["status"],
        "executionOwner": row.get("execution_owner"),
        "executionAttempt": int(row.get("execution_attempt") or 0),
        "leaseClaimedAt": _iso(row["lease_claimed_at"])
        if row.get("lease_claimed_at")
        else None,
        "leaseRenewedAt": _iso(row["lease_renewed_at"])
        if row.get("lease_renewed_at")
        else None,
        "leaseExpiresAt": _iso(row["lease_expires_at"])
        if row.get("lease_expires_at")
        else None,
        "cancelRequestedAt": _iso(row["cancel_requested_at"])
        if row.get("cancel_requested_at")
        else None,
        "cancelAcknowledgedAt": _iso(row["cancel_acknowledged_at"])
        if row.get("cancel_acknowledged_at")
        else None,
        "terminalAt": _iso(row["terminal_at"]) if row.get("terminal_at") else None,
        "createdBy": row["created_by"],
        "createdAt": _iso(row["created_at"]),
        "updatedAt": _iso(row["updated_at"]),
    }


def _execution_lease_from_row(
    row: Mapping[str, Any], *, reclaimed: bool
) -> ExecutionLease:
    return ExecutionLease(
        job_id=str(row["id"]),
        owner=str(row["execution_owner"]),
        attempt=int(row["execution_attempt"]),
        claimed_at=_iso(row["lease_claimed_at"]),
        renewed_at=_iso(row["lease_renewed_at"]),
        expires_at=_iso(row["lease_expires_at"]),
        reclaimed=reclaimed,
    )

def _tool_call_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "jobId": row["job_id"],
        "stepId": row["step_id"],
        "toolId": row["tool_id"],
        "status": row["status"],
        "idempotencyKey": row.get("idempotency_key"),
        "attempt": row.get("attempt") or 1,
        "params": _json_copy(row.get("params_json") or {}),
        "error": _json_copy(row.get("error_json")) if row.get("error_json") else None,
    }

__all__ = ["SqlAlchemyJobEventRepository", "SqlAlchemyJobRepository", "SqlAlchemyToolCallRepository"]
