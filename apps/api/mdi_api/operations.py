from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import text

from mdi_api.config import ApiSettings, load_settings
from mdi_api.database import create_engine_from_settings
from mdi_api.input_transport import MAX_FILE_BYTES, MAX_TOTAL_UPLOAD_BYTES
from mdi_api.report_composition import REPORT_EXPORT_MAX_BYTES
from mdi_api.research_agent.recovery import is_qualification_project
from mdi_api.research_agent.context.policy import ContextOperation, context_budget_policy
from mdi_api.scientific_viewers import build_scientific_viewer_registry
from mdi_schemas import REPORT_COMPOSITION_MAX_REQUEST_BYTES


_REQUIRED_TYPED_LIMIT_ERRORS = (
    "PROJECT_ACTIVE_RESEARCH_LIMIT",
    "TOOL_RESOURCE_LIMIT",
    "WORKSPACE_PAYLOAD_CAP_EXCEEDED",
    "REPORT_CAP_EXCEEDED",
    "EXPORT_SIZE_EXCEEDED",
)


@dataclass(frozen=True)
class OperationsThresholds:
    stale_minutes: int = 15
    queue_depth: int = 100
    minimum_workers: int = 5


def build_operations_snapshot(
    settings: ApiSettings | None = None,
    *,
    thresholds: OperationsThresholds | None = None,
) -> dict[str, Any]:
    active = settings or load_settings()
    limits = thresholds or OperationsThresholds()
    database = _database_snapshot(active, limits)
    queues = _redis_snapshot(active, limits)
    storage = _minio_snapshot(active)
    resource_governance = _resource_governance_snapshot(active, limits)
    snapshot = {
        "schemaVersion": "phase14r-operations-snapshot/1.0",
        "capturedAt": datetime.now(timezone.utc).isoformat(),
        "thresholds": {
            "staleMinutes": limits.stale_minutes,
            "queueDepth": limits.queue_depth,
            "minimumWorkers": limits.minimum_workers,
        },
        "database": database,
        "queues": queues,
        "artifactStorage": storage,
        "resourceGovernance": resource_governance,
    }
    alerts = _operations_alerts(snapshot)
    snapshot.update(
        {
            "status": "ok" if not alerts else "attention",
            "alertsSchemaVersion": "phase14r-operations-alerts/1.0",
            "alerts": alerts,
            "alertSummary": {
                "total": len(alerts),
                "critical": sum(
                    alert["severity"] == "CRITICAL" for alert in alerts
                ),
                "warning": sum(
                    alert["severity"] == "WARNING" for alert in alerts
                ),
            },
        }
    )
    return snapshot


def _database_snapshot(settings: ApiSettings, thresholds: OperationsThresholds) -> dict[str, Any]:
    backend = "postgresql" if "postgres" in settings.database_url else "sqlite"
    if backend != "postgresql":
        return {"status": "attention", "backend": backend, "reason": "POSTGRESQL_REQUIRED"}
    try:
        engine = create_engine_from_settings(settings)
        with engine.connect() as connection:
            activity = {
                str(row.state or "active"): int(row.count)
                for row in connection.execute(
                    text(
                        """
                        SELECT COALESCE(state, 'active') AS state, COUNT(*) AS count
                        FROM pg_stat_activity
                        WHERE datname = current_database()
                        GROUP BY COALESCE(state, 'active')
                        """
                    )
                )
            }
            stale_turn_rows = list(
                connection.execute(
                    text(
                        """
                        SELECT rt.status, rt.project_id, p.created_by
                        FROM research_turns rt
                        JOIN projects p ON p.id = rt.project_id
                        WHERE rt.status IN (
                            'RECEIVED', 'RESOLVING_CONTEXT', 'ORCHESTRATING',
                            'READY_TO_PLAN', 'PLANNING', 'PLAN_READY', 'QUEUED',
                            'RUNNING', 'CANCELING', 'RESULT_PENDING',
                            'RESULT_READY', 'INTERPRETING'
                        )
                        AND rt.updated_at < now() - (:minutes * interval '1 minute')
                        """
                    ),
                    {"minutes": thresholds.stale_minutes},
                )
            )
            stale_turn_states: dict[str, int] = {}
            retained_turn_states: dict[str, int] = {}
            for row in stale_turn_rows:
                target = retained_turn_states if is_qualification_project(
                    project_id=str(row.project_id),
                    created_by=str(row.created_by),
                ) else stale_turn_states
                status_key = str(row.status)
                target[status_key] = target.get(status_key, 0) + 1
            stale_active_turns = sum(
                stale_turn_states.get(status, 0)
                for status in (
                    "RESOLVING_CONTEXT",
                    "ORCHESTRATING",
                    "PLANNING",
                    "QUEUED",
                    "RUNNING",
                    "CANCELING",
                    "INTERPRETING",
                )
            )
            stale_waiting_turns = sum(stale_turn_states.values()) - stale_active_turns
            stale_job_rows = list(
                connection.execute(
                    text(
                        """
                        SELECT j.project_id, p.created_by
                        FROM jobs j
                        JOIN projects p ON p.id = j.project_id
                        WHERE j.status IN ('queued', 'running', 'cancel_requested')
                        AND j.updated_at < now() - (:minutes * interval '1 minute')
                        """
                    ),
                    {"minutes": thresholds.stale_minutes},
                )
            )
            stale_jobs = sum(
                1 for row in stale_job_rows
                if not is_qualification_project(
                    project_id=str(row.project_id),
                    created_by=str(row.created_by),
                )
            )
            retained_jobs = len(stale_job_rows) - stale_jobs
        pool = engine.pool
        pool_state = {
            "size": _safe_pool_metric(pool, "size"),
            "checkedOut": _safe_pool_metric(pool, "checkedout"),
            "overflow": _safe_pool_metric(pool, "overflow"),
        }
        idle_in_transaction = int(activity.get("idle in transaction", 0))
        status = "ok" if not stale_active_turns and not stale_jobs and not idle_in_transaction else "attention"
        return {
            "status": status,
            "backend": backend,
            "connections": activity,
            "idleInTransaction": idle_in_transaction,
            "staleResearchTurns": sum(stale_turn_states.values()),
            "staleActiveResearchTurns": stale_active_turns,
            "staleWaitingResearchTurns": stale_waiting_turns,
            "staleTurnStates": stale_turn_states,
            "staleJobs": stale_jobs,
            "retainedQualificationResearchTurns": sum(retained_turn_states.values()),
            "retainedQualificationTurnStates": retained_turn_states,
            "retainedQualificationJobs": retained_jobs,
            "pool": pool_state,
        }
    except Exception as exc:
        return {"status": "attention", "backend": backend, "reason": exc.__class__.__name__}


def _redis_snapshot(settings: ApiSettings, thresholds: OperationsThresholds) -> dict[str, Any]:
    if settings.queue_backend != "redis":
        return {"status": "attention", "backend": settings.queue_backend, "reason": "REDIS_REQUIRED"}
    try:
        from redis import Redis
        from rq import Queue, Worker

        connection = Redis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=2)
        connection.ping()
        queue_names = tuple(
            dict.fromkeys(
                (
                    settings.agent2_queue_name,
                    "mdi-agent-plans",
                    "mdi-jobs",
                    settings.agent2_result_queue_name,
                    settings.agent2_interpretation_queue_name,
                    settings.agent2_report_queue_name,
                )
            )
        )
        queues = []
        total_depth = 0
        total_started = 0
        total_failed = 0
        recent_failed = 0
        failed_cutoff = datetime.now(timezone.utc) - timedelta(minutes=thresholds.stale_minutes)
        for queue_name in queue_names:
            queue = Queue(queue_name, connection=connection)
            depth = int(queue.count)
            started = int(queue.started_job_registry.count)
            failed = int(queue.failed_job_registry.count)
            queue_recent_failed = 0
            for job_id in queue.failed_job_registry.get_job_ids(start=0, end=99, desc=True):
                job = queue.fetch_job(job_id)
                ended_at = getattr(job, "ended_at", None)
                if ended_at is None or _as_utc(ended_at) >= failed_cutoff:
                    queue_recent_failed += 1
            total_depth += depth
            total_started += started
            total_failed += failed
            recent_failed += queue_recent_failed
            queues.append(
                {
                    "name": queue_name,
                    "queued": depth,
                    "started": started,
                    "failed": failed,
                    "recentFailed": queue_recent_failed,
                }
            )
        workers = Worker.all(connection=connection)
        worker_states: dict[str, int] = {}
        for worker in workers:
            state = str(getattr(worker, "state", None) or "unknown")
            worker_states[state] = worker_states.get(state, 0) + 1
        status = (
            "ok"
            if total_depth <= thresholds.queue_depth
            and len(workers) >= thresholds.minimum_workers
            and recent_failed == 0
            else "attention"
        )
        return {
            "status": status,
            "backend": "redis",
            "totalQueued": total_depth,
            "totalStarted": total_started,
            "totalFailed": total_failed,
            "recentFailed": recent_failed,
            "workerCount": len(workers),
            "workerStates": worker_states,
            "items": queues,
        }
    except Exception as exc:
        return {"status": "attention", "backend": "redis", "reason": exc.__class__.__name__}


def _minio_snapshot(settings: ApiSettings) -> dict[str, Any]:
    if settings.artifact_backend != "minio":
        return {
            "status": "attention",
            "backend": settings.artifact_backend,
            "reason": "MINIO_REQUIRED",
        }
    if not settings.minio_access_key or not settings.minio_secret_key:
        return {"status": "attention", "backend": "minio", "reason": "MINIO_NOT_CONFIGURED"}
    try:
        import boto3
        from botocore.config import Config

        client = boto3.client(
            "s3",
            endpoint_url=settings.minio_endpoint,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            region_name=settings.s3_region,
            use_ssl=settings.minio_secure,
            config=Config(connect_timeout=2, read_timeout=2, retries={"max_attempts": 0}),
        )
        client.head_bucket(Bucket=settings.minio_bucket)
        return {"status": "ok", "backend": "minio", "bucket": settings.minio_bucket}
    except Exception as exc:
        return {"status": "attention", "backend": "minio", "reason": exc.__class__.__name__}


def _resource_governance_snapshot(
    settings: ApiSettings,
    thresholds: OperationsThresholds,
) -> dict[str, Any]:
    viewer_limits = {
        item.object_type: item.maximum_payload_bytes
        for item in build_scientific_viewer_registry().list()
    }
    context_limits = {
        operation.value: context_budget_policy(operation).effective_input_budget
        for operation in ContextOperation
    }
    snapshot = {
        "schemaVersion": "phase14r-resource-governance/1.0",
        "uploads": {
            "perFileBytes": MAX_FILE_BYTES,
            "totalRequestBytes": MAX_TOTAL_UPLOAD_BYTES,
        },
        "research": {
            "maxActiveTurnsPerProject": settings.agent2_max_active_turns_per_project,
            "queueAttentionDepth": thresholds.queue_depth,
        },
        "reports": {
            "maxRequestBytes": REPORT_COMPOSITION_MAX_REQUEST_BYTES,
            "maxExportBytes": REPORT_EXPORT_MAX_BYTES,
        },
        "contextInputTokens": context_limits,
        "viewerPayloadBytes": viewer_limits,
        "typedLimitErrors": list(_REQUIRED_TYPED_LIMIT_ERRORS),
    }
    violations = _resource_governance_violations(snapshot)
    return {
        **snapshot,
        "status": "ok" if not violations else "attention",
        "violations": violations,
    }


def _resource_governance_violations(snapshot: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    uploads = snapshot.get("uploads") or {}
    per_file = _as_non_negative_int(uploads.get("perFileBytes"))
    total_request = _as_non_negative_int(uploads.get("totalRequestBytes"))
    if per_file <= 0 or total_request < per_file:
        violations.append("RESOURCE_UPLOAD_LIMIT_INVALID")

    research = snapshot.get("research") or {}
    if _as_non_negative_int(research.get("maxActiveTurnsPerProject")) <= 0:
        violations.append("RESOURCE_RESEARCH_CONCURRENCY_INVALID")
    if _as_int(research.get("queueAttentionDepth")) < 0:
        violations.append("RESOURCE_QUEUE_THRESHOLD_INVALID")

    reports = snapshot.get("reports") or {}
    report_request = _as_non_negative_int(reports.get("maxRequestBytes"))
    report_export = _as_non_negative_int(reports.get("maxExportBytes"))
    if report_request <= 0 or report_export < report_request:
        violations.append("RESOURCE_REPORT_LIMIT_INVALID")

    context_limits = snapshot.get("contextInputTokens") or {}
    expected_contexts = {operation.value for operation in ContextOperation}
    if (
        set(context_limits) != expected_contexts
        or any(_as_non_negative_int(value) <= 0 for value in context_limits.values())
    ):
        violations.append("RESOURCE_CONTEXT_LIMIT_INVALID")

    viewer_limits = snapshot.get("viewerPayloadBytes") or {}
    if not viewer_limits or any(
        _as_non_negative_int(value) <= 0 for value in viewer_limits.values()
    ):
        violations.append("RESOURCE_VIEWER_LIMIT_INVALID")

    typed_errors = {
        str(value)
        for value in snapshot.get("typedLimitErrors") or []
        if str(value)
    }
    if not set(_REQUIRED_TYPED_LIMIT_ERRORS).issubset(typed_errors):
        violations.append("RESOURCE_TYPED_LIMIT_CONTRACT_INCOMPLETE")
    return violations


def _operations_alerts(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    thresholds = snapshot.get("thresholds") or {}
    stale_minutes = _as_non_negative_int(thresholds.get("staleMinutes"))
    queue_depth_limit = _as_non_negative_int(thresholds.get("queueDepth"))
    minimum_workers = _as_non_negative_int(thresholds.get("minimumWorkers"))

    database = snapshot.get("database") or {}
    database_codes: set[str] = set()
    if database.get("backend") != "postgresql":
        database_codes.add("OPS_DATABASE_BACKEND_REQUIRED")
        alerts.append(
            _alert(
                code="OPS_DATABASE_BACKEND_REQUIRED",
                severity="CRITICAL",
                component="database",
                observed=str(database.get("backend") or "unknown"),
                threshold="postgresql",
                message="Operations qualification requires PostgreSQL.",
            )
        )
    idle_in_transaction = _as_non_negative_int(database.get("idleInTransaction"))
    if "idleInTransaction" in database and idle_in_transaction > 0:
        database_codes.add("OPS_DATABASE_IDLE_IN_TRANSACTION")
        alerts.append(
            _alert(
                code="OPS_DATABASE_IDLE_IN_TRANSACTION",
                severity="CRITICAL",
                component="database",
                observed=idle_in_transaction,
                threshold=0,
                message="Idle-in-transaction database connections were observed.",
            )
        )
    stale_turns = _as_non_negative_int(database.get("staleActiveResearchTurns"))
    if "staleActiveResearchTurns" in database and stale_turns > 0:
        database_codes.add("OPS_STALE_RESEARCH_TURNS")
        alerts.append(
            _alert(
                code="OPS_STALE_RESEARCH_TURNS",
                severity="CRITICAL",
                component="database",
                observed=stale_turns,
                threshold=0,
                message=(
                    "ResearchTurns exceeded the active-stage age threshold "
                    f"of {stale_minutes} minutes."
                ),
            )
        )
    stale_jobs = _as_non_negative_int(database.get("staleJobs"))
    if "staleJobs" in database and stale_jobs > 0:
        database_codes.add("OPS_STALE_JOBS")
        alerts.append(
            _alert(
                code="OPS_STALE_JOBS",
                severity="CRITICAL",
                component="database",
                observed=stale_jobs,
                threshold=0,
                message=(
                    "Jobs exceeded the queued/running age threshold "
                    f"of {stale_minutes} minutes."
                ),
            )
        )
    if database.get("status") != "ok" and not database_codes:
        alerts.append(
            _alert(
                code="OPS_DATABASE_UNAVAILABLE",
                severity="CRITICAL",
                component="database",
                observed=_bounded_reason(database),
                threshold="reachable",
                message="The PostgreSQL operations probe needs attention.",
            )
        )

    queues = snapshot.get("queues") or {}
    queue_codes: set[str] = set()
    if queues.get("backend") != "redis":
        queue_codes.add("OPS_REDIS_BACKEND_REQUIRED")
        alerts.append(
            _alert(
                code="OPS_REDIS_BACKEND_REQUIRED",
                severity="CRITICAL",
                component="queues",
                observed=str(queues.get("backend") or "unknown"),
                threshold="redis",
                message="Operations qualification requires Redis-backed queues.",
            )
        )
    total_queued = _as_non_negative_int(queues.get("totalQueued"))
    if "totalQueued" in queues and total_queued > queue_depth_limit:
        queue_codes.add("OPS_QUEUE_DEPTH_EXCEEDED")
        alerts.append(
            _alert(
                code="OPS_QUEUE_DEPTH_EXCEEDED",
                severity="WARNING",
                component="queues",
                observed=total_queued,
                threshold=queue_depth_limit,
                message="Canonical queue depth exceeded the attention threshold.",
            )
        )
    worker_count = _as_non_negative_int(queues.get("workerCount"))
    if "workerCount" in queues and worker_count < minimum_workers:
        queue_codes.add("OPS_WORKER_COUNT_BELOW_MINIMUM")
        alerts.append(
            _alert(
                code="OPS_WORKER_COUNT_BELOW_MINIMUM",
                severity="CRITICAL",
                component="queues",
                observed=worker_count,
                threshold=minimum_workers,
                message="Fewer canonical workers are available than required.",
            )
        )
    recent_failed = _as_non_negative_int(queues.get("recentFailed"))
    if "recentFailed" in queues and recent_failed > 0:
        queue_codes.add("OPS_RECENT_QUEUE_FAILURES")
        alerts.append(
            _alert(
                code="OPS_RECENT_QUEUE_FAILURES",
                severity="CRITICAL",
                component="queues",
                observed=recent_failed,
                threshold=0,
                message="Recent canonical queue failures were observed.",
            )
        )
    if queues.get("status") != "ok" and not queue_codes:
        alerts.append(
            _alert(
                code="OPS_REDIS_UNAVAILABLE",
                severity="CRITICAL",
                component="queues",
                observed=_bounded_reason(queues),
                threshold="reachable",
                message="The Redis queue probe needs attention.",
            )
        )

    storage = snapshot.get("artifactStorage") or {}
    if storage.get("backend") != "minio":
        alerts.append(
            _alert(
                code="OPS_MINIO_BACKEND_REQUIRED",
                severity="CRITICAL",
                component="artifactStorage",
                observed=str(storage.get("backend") or "unknown"),
                threshold="minio",
                message="Operations qualification requires MinIO artifact storage.",
            )
        )
    elif storage.get("status") != "ok":
        alerts.append(
            _alert(
                code="OPS_MINIO_UNAVAILABLE",
                severity="CRITICAL",
                component="artifactStorage",
                observed=_bounded_reason(storage),
                threshold="reachable",
                message="The MinIO artifact-storage probe needs attention.",
            )
        )

    resource_governance = snapshot.get("resourceGovernance") or {}
    for violation in resource_governance.get("violations") or []:
        alerts.append(
            _alert(
                code=f"OPS_{violation}",
                severity="CRITICAL",
                component="resourceGovernance",
                observed=str(violation),
                threshold="valid bounded limit",
                message="A configured resource-governance contract is invalid.",
            )
        )
    if resource_governance.get("status") != "ok" and not (
        resource_governance.get("violations") or []
    ):
        alerts.append(
            _alert(
                code="OPS_RESOURCE_GOVERNANCE_INVALID",
                severity="CRITICAL",
                component="resourceGovernance",
                observed="attention",
                threshold="ok",
                message="The resource-governance projection needs attention.",
            )
        )
    return alerts


def _alert(
    *,
    code: str,
    severity: str,
    component: str,
    observed: Any,
    threshold: Any,
    message: str,
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "component": component,
        "observed": observed,
        "threshold": threshold,
        "message": message,
    }


def _bounded_reason(component: dict[str, Any]) -> str:
    reason = str(component.get("reason") or "ATTENTION")
    return reason[:96]


def _as_non_negative_int(value: Any) -> int:
    return max(0, _as_int(value))


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _safe_pool_metric(pool: Any, name: str) -> int | None:
    value = getattr(pool, name, None)
    if not callable(value):
        return None
    try:
        return int(value())
    except (TypeError, ValueError):
        return None


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


__all__ = ["OperationsThresholds", "build_operations_snapshot"]
