from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import threading
import tempfile
import time
from typing import Any

from sqlalchemy import text

from mdi_api.config import ApiSettings, load_settings
from mdi_api.infrastructure.persistence.engine import create_engine_from_settings
from mdi_api.input_transport import MAX_FILE_BYTES, MAX_TOTAL_UPLOAD_BYTES
from mdi_api.infrastructure.reports.composition import REPORT_EXPORT_MAX_BYTES
from mdi_api.research_agent.recovery import is_qualification_project
from mdi_api.research_agent.context.policy import ContextOperation, context_budget_policy
from mdi_api.scientific_viewers import build_scientific_viewer_registry
from mdi_api.service_failures import (
    classify_service_failure,
    configuration_service_failure,
)
from mdi_api.storage_budget import build_storage_budget_snapshot
from mdi_schemas import REPORT_COMPOSITION_MAX_REQUEST_BYTES
from mdi_schemas.worker_queues import configured_worker_queue_names


_REQUIRED_TYPED_LIMIT_ERRORS = (
    "PROJECT_ACTIVE_RESEARCH_LIMIT",
    "TOOL_RESOURCE_LIMIT",
    "WORKSPACE_PAYLOAD_CAP_EXCEEDED",
    "REPORT_CAP_EXCEEDED",
    "EXPORT_SIZE_EXCEEDED",
)

_OPERATIONS_RUNBOOK_REFERENCE = (
    "README.md#runtime-topology"
)
_OPERATIONS_RECHECK_COMMAND = (
    "scripts/dev.ps1 status"
)
_MINIO_USAGE_SCAN_RETRY_ATTEMPTS = 1
_MINIO_USAGE_SCAN_RETRY_DELAY_SECONDS = 0.05
_MINIO_LAST_KNOWN_COMPLETE_TTL_SECONDS = 300
_MINIO_OBSERVATION_MAX_FUTURE_SKEW_SECONDS = 60
_MINIO_LAST_KNOWN_COMPLETE: dict[str, dict[str, Any]] = {}
_MINIO_LAST_KNOWN_COMPLETE_LOCK = threading.Lock()

def _default_external_root() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    return Path(os.getenv("MDI_LOCAL_ROOT", str(repo_root.parent / f"{repo_root.name}.local")))


_MINIO_OBSERVATION_CACHE_DIRECTORY = Path(
    os.getenv("MDI_CACHE_ROOT", str(_default_external_root() / "cache"))
) / "minio"
_RUNBOOK_ACTIONS = {
    "OPS_STALE_JOBS": (
        "OPS-RUNBOOK-STALE-JOBS",
        "先核对 Job 年龄及其 ResearchTurn，再使用有界恢复命令；不要直接删除持久记录。",
    ),
    "OPS_QUEUE_DEPTH_EXCEEDED": (
        "OPS-RUNBOOK-QUEUE-BACKLOG",
        "先检查各队列积压与 worker 消费状态，再决定扩容或重试。",
    ),
    "OPS_WORKER_COUNT_BELOW_MINIMUM": (
        "OPS-RUNBOOK-WORKER-HEALTH",
        "核对规范队列覆盖和 worker 注册，仅启动缺失的 worker 角色。",
    ),
    "OPS_WORKER_HEALTH_DEGRADED": (
        "OPS-RUNBOOK-WORKER-HEALTH",
        "替换进程前先检查过期心跳和非服务状态，避免重复消费队列任务。",
    ),
    "OPS_MINIO_USAGE_SCAN_INCOMPLETE": (
        "OPS-RUNBOOK-MINIO-CAPACITY",
        "当前对象数已达到有界扫描上限；先提高只读观测容量或使用存储端聚合统计，不要删除科学 Artifact。",
    ),
}


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
    storage_budgets = build_storage_budget_snapshot(
        repository_root=Path(__file__).resolve().parents[3],
        database=database,
        artifact_storage=storage,
    )
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
        "storageBudgets": storage_budgets,
    }
    alerts = _operations_alerts(snapshot)
    snapshot.update(
        {
            "status": "ok" if not alerts else "attention",
            "alertsSchemaVersion": "phase14r-operations-alerts/1.1",
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
            authority_consistency = _authority_consistency_snapshot(connection)
            storage_bytes = int(
                connection.scalar(
                    text("SELECT pg_database_size(current_database())")
                )
                or 0
            )
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
            "authorityConsistency": authority_consistency,
            "storageBytes": storage_bytes,
            "pool": pool_state,
        }
    except Exception as exc:
        failure = classify_service_failure("database", exc)
        return {
            "status": "attention",
            "backend": backend,
            "reason": failure.code,
            "failure": failure.as_dict(),
        }


def _authority_consistency_snapshot(connection: Any) -> dict[str, Any]:
    """Run bounded, read-only checks for orphaned scientific lineage rows."""
    probes = (
        (
            "ORPHAN_TOOL_CALL_JOB",
            "tool_calls tc",
            "jobs j ON j.id = tc.job_id",
            "j.id IS NULL",
        ),
        (
            "ORPHAN_ARTIFACT_JOB",
            "artifacts a",
            "jobs j ON j.id = a.job_id",
            "j.id IS NULL",
        ),
        (
            "ORPHAN_ARTIFACT_TOOL_CALL",
            "artifacts a",
            "tool_calls tc ON tc.id = a.tool_call_id",
            "a.tool_call_id IS NOT NULL AND tc.id IS NULL",
        ),
        (
            "ORPHAN_RESULT_TURN",
            "scientific_result_snapshots s",
            "research_turns rt ON rt.id = s.research_turn_id",
            "rt.id IS NULL",
        ),
        (
            "ORPHAN_RESULT_JOB",
            "scientific_result_snapshots s",
            "jobs j ON j.id = s.job_id",
            "s.job_id IS NOT NULL AND j.id IS NULL",
        ),
        (
            "ORPHAN_REPORT_JOB",
            "reports r",
            "jobs j ON j.id = r.job_id",
            "j.id IS NULL",
        ),
        (
            "ORPHAN_REPORT_RESULT",
            "agent2_scientific_report_snapshots rs",
            "scientific_result_snapshots s ON s.id = rs.scientific_result_snapshot_id",
            "s.id IS NULL",
        ),
        (
            "BROKEN_CURRENT_VERSION",
            "scientific_objects so",
            "scientific_object_versions sov ON sov.id = so.current_version_id",
            "so.current_version_id IS NOT NULL AND sov.id IS NULL",
        ),
    )
    issues: list[dict[str, Any]] = []
    for code, source, join, predicate in probes:
        count = int(
            connection.execute(
                text(f"SELECT COUNT(*) FROM {source} LEFT JOIN {join} WHERE {predicate}")
            ).scalar_one()
        )
        sample_rows = connection.execute(
            text(
                f"SELECT {source.split()[1]}.id "
                f"FROM {source} LEFT JOIN {join} WHERE {predicate} "
                "ORDER BY 1 LIMIT 20"
            )
        ).all()
        if count:
            issues.append(
                {
                    "code": code,
                    "count": count,
                    "sampleIds": [str(row[0]) for row in sample_rows],
                }
            )
    return {
        "schemaVersion": "phase14r-authority-consistency/1.0",
        "status": "ok" if not issues else "attention",
        "issueCount": len(issues),
        "issues": issues,
        "readOnly": True,
    }


def _redis_snapshot(settings: ApiSettings, thresholds: OperationsThresholds) -> dict[str, Any]:
    if settings.queue_backend != "redis":
        return {"status": "attention", "backend": settings.queue_backend, "reason": "REDIS_REQUIRED"}
    try:
        from redis import Redis
        from rq import Queue, Worker

        connection = Redis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=2)
        connection.ping()
        queue_names = configured_worker_queue_names(settings)
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
        worker_health = _worker_health_snapshot(
            workers,
            stale_minutes=thresholds.stale_minutes,
        )
        worker_states = worker_health["states"]
        status = (
            "ok"
            if total_depth <= thresholds.queue_depth
            and len(workers) >= thresholds.minimum_workers
            and recent_failed == 0
            and worker_health["status"] == "ok"
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
            "workerHealth": worker_health,
            "items": queues,
        }
    except Exception as exc:
        failure = classify_service_failure("redis", exc)
        return {
            "status": "attention",
            "backend": "redis",
            "reason": failure.code,
            "failure": failure.as_dict(),
        }


def _minio_snapshot(settings: ApiSettings) -> dict[str, Any]:
    if settings.artifact_backend != "minio":
        return {
            "status": "attention",
            "backend": settings.artifact_backend,
            "reason": "MINIO_REQUIRED",
        }
    if not settings.minio_access_key or not settings.minio_secret_key:
        failure = configuration_service_failure("artifactStorage")
        return {
            "status": "attention",
            "backend": "minio",
            "reason": failure.code,
            "failure": failure.as_dict(),
        }
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
        usage: dict[str, Any] | None = None
        retry_count = 0
        for attempt in range(_MINIO_USAGE_SCAN_RETRY_ATTEMPTS + 1):
            try:
                usage = _bounded_minio_usage(client, settings.minio_bucket)
                break
            except Exception as exc:
                failure = classify_service_failure("artifactStorage", exc)
                if not failure.retryable or attempt >= _MINIO_USAGE_SCAN_RETRY_ATTEMPTS:
                    usage = {
                        "storageBytes": None,
                        "objectCount": None,
                        "usageScanComplete": False,
                        "usageObjectLimit": 10_000,
                        "usageReason": failure.code,
                        "usageRetryCount": retry_count,
                    }
                    break
                retry_count += 1
                time.sleep(_MINIO_USAGE_SCAN_RETRY_DELAY_SECONDS)
        cache_key = _minio_observation_cache_key(
            settings.minio_endpoint,
            settings.minio_bucket,
        )
        if usage is not None and usage.get("usageScanComplete") is True:
            captured_at = datetime.now(timezone.utc)
            with _MINIO_LAST_KNOWN_COMPLETE_LOCK:
                _MINIO_LAST_KNOWN_COMPLETE[cache_key] = {
                    "capturedAt": captured_at,
                    "storageBytes": usage.get("storageBytes"),
                    "objectCount": usage.get("objectCount"),
                }
            _persist_minio_observation(
                cache_key,
                captured_at=captured_at,
                storage_bytes=usage.get("storageBytes"),
                object_count=usage.get("objectCount"),
            )
        if (
            usage is not None
            and usage.get("usageScanComplete") is False
            and usage.get("usageReason", "").endswith("TIMEOUT")
        ):
            with _MINIO_LAST_KNOWN_COMPLETE_LOCK:
                cached = _MINIO_LAST_KNOWN_COMPLETE.get(cache_key)
            cache_source = "api_process"
            if cached is None:
                cached = _read_minio_observation(cache_key)
                cache_source = "runtime_file"
            if cached is not None:
                age_seconds = (
                    datetime.now(timezone.utc) - cached["capturedAt"]
                ).total_seconds()
                if age_seconds <= _MINIO_LAST_KNOWN_COMPLETE_TTL_SECONDS:
                    usage["lastKnownComplete"] = {
                        "authoritative": False,
                        "source": cache_source,
                        "capturedAt": cached["capturedAt"].isoformat(),
                        "ageSeconds": round(max(0.0, age_seconds), 3),
                        "storageBytes": cached["storageBytes"],
                        "objectCount": cached["objectCount"],
                    }
                else:
                    usage["lastKnownCompleteExpired"] = True
                    with _MINIO_LAST_KNOWN_COMPLETE_LOCK:
                        _MINIO_LAST_KNOWN_COMPLETE.pop(cache_key, None)
                    if cache_source == "runtime_file":
                        _remove_minio_observation(cache_key)
        if retry_count and usage is not None:
            usage["usageRetryCount"] = retry_count
        return {
            "status": "ok",
            "backend": "minio",
            "bucket": settings.minio_bucket,
            **usage,
        }
    except Exception as exc:
        failure = classify_service_failure("artifactStorage", exc)
        return {
            "status": "attention",
            "backend": "minio",
            "reason": failure.code,
            "failure": failure.as_dict(),
        }


def _minio_observation_cache_key(endpoint: str, bucket: str) -> str:
    return hashlib.sha256(f"{endpoint}|{bucket}".encode("utf-8")).hexdigest()


def _minio_observation_path(cache_key: str) -> Path:
    return _MINIO_OBSERVATION_CACHE_DIRECTORY / f"usage-{cache_key}.json"


def _persist_minio_observation(
    cache_key: str,
    *,
    captured_at: datetime,
    storage_bytes: Any,
    object_count: Any,
) -> None:
    if (
        not isinstance(storage_bytes, int)
        or storage_bytes < 0
        or not isinstance(object_count, int)
        or object_count < 0
    ):
        return
    path = _minio_observation_path(cache_key)
    temporary_path: str | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_path = tempfile.mkstemp(
            prefix=".minio-usage-",
            suffix=".tmp",
            dir=path.parent,
            text=True,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(
                {
                    "schemaVersion": "minio-observation-cache/1.0",
                    "sourceFingerprint": cache_key,
                    "capturedAt": captured_at.isoformat(),
                    "storageBytes": storage_bytes,
                    "objectCount": object_count,
                },
                stream,
                separators=(",", ":"),
            )
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    except (OSError, TypeError, ValueError):
        return
    finally:
        if temporary_path:
            try:
                os.unlink(temporary_path)
            except OSError:
                pass


def _read_minio_observation(cache_key: str) -> dict[str, Any] | None:
    path = _minio_observation_path(cache_key)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if (
            payload.get("schemaVersion") != "minio-observation-cache/1.0"
            or payload.get("sourceFingerprint") != cache_key
            or not isinstance(payload.get("storageBytes"), int)
            or payload["storageBytes"] < 0
            or not isinstance(payload.get("objectCount"), int)
            or payload["objectCount"] < 0
        ):
            return None
        captured_at = datetime.fromisoformat(str(payload["capturedAt"]))
        if captured_at.tzinfo is None:
            captured_at = captured_at.replace(tzinfo=timezone.utc)
        captured_at = captured_at.astimezone(timezone.utc)
        if (
            captured_at - datetime.now(timezone.utc)
        ).total_seconds() > _MINIO_OBSERVATION_MAX_FUTURE_SKEW_SECONDS:
            return None
        return {
            "capturedAt": captured_at,
            "storageBytes": payload["storageBytes"],
            "objectCount": payload["objectCount"],
        }
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return None


def _remove_minio_observation(cache_key: str) -> None:
    try:
        _minio_observation_path(cache_key).unlink()
    except OSError:
        pass


def _bounded_minio_usage(
    client: Any,
    bucket: str,
    *,
    maximum_objects: int = 10_000,
) -> dict[str, Any]:
    """Measure a bounded bucket without returning object keys or metadata."""

    observed_bytes = 0
    object_count = 0
    continuation_token: str | None = None
    scan_complete = True
    incomplete_reason: str | None = None
    while object_count < maximum_objects:
        remaining = maximum_objects - object_count
        request: dict[str, Any] = {
            "Bucket": bucket,
            "MaxKeys": min(1000, remaining),
        }
        if continuation_token:
            request["ContinuationToken"] = continuation_token
        response = client.list_objects_v2(**request)
        contents = response.get("Contents") or []
        for item in contents:
            size = item.get("Size")
            if isinstance(size, int) and size >= 0:
                observed_bytes += size
            object_count += 1
        if not response.get("IsTruncated"):
            break
        continuation_token = response.get("NextContinuationToken")
        if object_count >= maximum_objects:
            scan_complete = False
            incomplete_reason = "MINIO_USAGE_SCAN_LIMIT_REACHED"
            break
        if not continuation_token:
            scan_complete = False
            incomplete_reason = "MINIO_USAGE_SCAN_CONTINUATION_MISSING"
            break
    snapshot = {
        "storageBytes": observed_bytes,
        "objectCount": object_count,
        "usageScanComplete": scan_complete,
        "usageObjectLimit": maximum_objects,
    }
    if incomplete_reason:
        snapshot["usageReason"] = incomplete_reason
    return snapshot


def _worker_health_snapshot(
    workers: list[Any],
    *,
    stale_minutes: int,
    now: datetime | None = None,
) -> dict[str, Any]:
    observed_at = now or datetime.now(timezone.utc)
    cutoff = observed_at - timedelta(minutes=max(1, stale_minutes))
    states: dict[str, int] = {}
    unhealthy_count = 0
    stale_heartbeat_count = 0
    degraded_count = 0
    healthy_states = {"idle", "busy"}
    for worker in workers:
        state = str(getattr(worker, "state", None) or "unknown").lower()
        states[state] = states.get(state, 0) + 1
        heartbeat = getattr(worker, "last_heartbeat", None)
        heartbeat_is_stale = (
            heartbeat is not None and _as_utc(heartbeat) < cutoff
        )
        if state not in healthy_states:
            unhealthy_count += 1
        if heartbeat_is_stale:
            stale_heartbeat_count += 1
        if state not in healthy_states or heartbeat_is_stale:
            degraded_count += 1
    return {
        "schemaVersion": "phase14r-worker-health/1.0",
        "status": "ok" if degraded_count == 0 else "attention",
        "healthyCount": max(0, len(workers) - degraded_count),
        "unhealthyStateCount": unhealthy_count,
        "staleHeartbeatCount": stale_heartbeat_count,
        "states": states,
    }


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
    consistency = database.get("authorityConsistency") or {}
    if consistency.get("status") != "ok" and consistency.get("issueCount", 0):
        alerts.append(
            _alert(
                code="OPS_AUTHORITY_CONSISTENCY",
                severity="CRITICAL",
                component="database",
                observed=consistency.get("issueCount"),
                threshold=0,
                message="Read-only scientific lineage consistency checks found orphaned references.",
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
    worker_health = queues.get("workerHealth") or {}
    if worker_health.get("status") == "attention":
        queue_codes.add("OPS_WORKER_HEALTH_DEGRADED")
        alerts.append(
            _alert(
                code="OPS_WORKER_HEALTH_DEGRADED",
                severity="CRITICAL",
                component="queues",
                observed={
                    "unhealthyStateCount": _as_non_negative_int(
                        worker_health.get("unhealthyStateCount")
                    ),
                    "staleHeartbeatCount": _as_non_negative_int(
                        worker_health.get("staleHeartbeatCount")
                    ),
                },
                threshold={
                    "unhealthyStateCount": 0,
                    "staleHeartbeatCount": 0,
                },
                message=(
                    "Canonical workers reported a non-serving state or stale "
                    "heartbeat."
                ),
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
    elif storage.get("usageScanComplete") is False:
        observed: dict[str, Any] = {
            "objectCountLowerBound": _as_non_negative_int(
                storage.get("objectCount")
            ),
            "reason": str(
                storage.get("usageReason")
                or "MINIO_USAGE_SCAN_INCOMPLETE"
            )[:96],
        }
        last_known = storage.get("lastKnownComplete")
        if isinstance(last_known, dict):
            observed["lastKnownCompleteAgeSeconds"] = last_known.get(
                "ageSeconds"
            )
        alerts.append(
            _alert(
                code="OPS_MINIO_USAGE_SCAN_INCOMPLETE",
                severity="WARNING",
                component="artifactStorage",
                observed=observed,
                threshold={
                    "usageScanComplete": True,
                    "usageObjectLimit": _as_non_negative_int(
                        storage.get("usageObjectLimit")
                    ),
                },
                message=(
                    "The bounded MinIO capacity scan did not inspect the "
                    "complete bucket; observed counts and bytes are lower "
                    "bounds."
                ),
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
    alert = {
        "code": code,
        "severity": severity,
        "component": component,
        "observed": observed,
        "threshold": threshold,
        "message": message,
    }
    runbook = _RUNBOOK_ACTIONS.get(code)
    if runbook:
        alert["runbook"] = {
            "id": runbook[0],
            "reference": _OPERATIONS_RUNBOOK_REFERENCE,
            "operatorAction": runbook[1],
            "recheckCommand": _OPERATIONS_RECHECK_COMMAND,
        }
    return alert


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
