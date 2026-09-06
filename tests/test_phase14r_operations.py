from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, func, insert, select

from mdi_api import operations
from mdi_api.config import ApiSettings
from mdi_api.db import metadata, tool_calls


def test_operations_snapshot_is_ok_only_when_every_authority_is_healthy(monkeypatch):
    monkeypatch.setattr(
        operations,
        "_database_snapshot",
        lambda _settings, _thresholds: {"status": "ok", "backend": "postgresql"},
    )
    monkeypatch.setattr(
        operations,
        "_redis_snapshot",
        lambda _settings, _thresholds: {"status": "ok", "backend": "redis"},
    )
    monkeypatch.setattr(
        operations,
        "_minio_snapshot",
        lambda _settings: {"status": "ok", "backend": "minio"},
    )

    snapshot = operations.build_operations_snapshot(ApiSettings())

    assert snapshot["status"] == "ok"
    assert snapshot["schemaVersion"] == "phase14r-operations-snapshot/1.0"
    assert snapshot["resourceGovernance"]["schemaVersion"] == "phase14r-resource-governance/1.0"
    assert snapshot["resourceGovernance"]["research"]["maxActiveTurnsPerProject"] == 4
    assert snapshot["resourceGovernance"]["uploads"]["perFileBytes"] == 64 * 1024 * 1024
    assert snapshot["resourceGovernance"]["contextInputTokens"]["ORCHESTRATOR"] == 12_000
    assert "PROJECT_ACTIVE_RESEARCH_LIMIT" in snapshot["resourceGovernance"]["typedLimitErrors"]
    assert snapshot["alertsSchemaVersion"] == "phase14r-operations-alerts/1.1"
    assert snapshot["alerts"] == []
    assert snapshot["alertSummary"] == {
        "total": 0,
        "critical": 0,
        "warning": 0,
    }
    assert "database_url" not in str(snapshot)
    assert "redis_url" not in str(snapshot)


def test_operations_snapshot_surfaces_attention_without_secret_details(monkeypatch):
    monkeypatch.setattr(
        operations,
        "_database_snapshot",
        lambda _settings, _thresholds: {
            "status": "attention",
            "backend": "postgresql",
            "staleJobs": 1,
        },
    )
    monkeypatch.setattr(
        operations,
        "_redis_snapshot",
        lambda _settings, _thresholds: {"status": "ok", "backend": "redis"},
    )
    monkeypatch.setattr(
        operations,
        "_minio_snapshot",
        lambda _settings: {"status": "ok", "backend": "minio"},
    )

    snapshot = operations.build_operations_snapshot(ApiSettings())

    assert snapshot["status"] == "attention"
    assert snapshot["database"]["staleJobs"] == 1
    assert snapshot["alerts"] == [
        {
            "code": "OPS_STALE_JOBS",
            "severity": "CRITICAL",
            "component": "database",
            "observed": 1,
            "threshold": 0,
            "message": (
                "Jobs exceeded the queued/running age threshold "
                "of 15 minutes."
            ),
            "runbook": {
                "id": "OPS-RUNBOOK-STALE-JOBS",
                "reference": (
                    "docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md"
                    "#operations-alert-response"
                ),
                "operatorAction": (
                    "先核对 Job 年龄及其 ResearchTurn，再使用有界恢复命令；"
                    "不要直接删除持久记录。"
                ),
                "recheckCommand": (
                    "python scripts/phase14r_operations_snapshot.py "
                    "--same-stack --fail-on-attention --compact"
                ),
            },
        }
    ]
    assert snapshot["alertSummary"] == {
        "total": 1,
        "critical": 1,
        "warning": 0,
    }
    assert "password" not in str(snapshot).lower()
    assert "secret" not in str(snapshot).lower()


def test_operations_alerts_are_typed_redacted_and_stable(monkeypatch):
    monkeypatch.setattr(
        operations,
        "_database_snapshot",
        lambda _settings, _thresholds: {
            "status": "attention",
            "backend": "postgresql",
            "idleInTransaction": 2,
            "staleActiveResearchTurns": 3,
            "staleJobs": 4,
        },
    )
    monkeypatch.setattr(
        operations,
        "_redis_snapshot",
        lambda _settings, _thresholds: {
            "status": "attention",
            "backend": "redis",
            "totalQueued": 101,
            "workerCount": 4,
            "recentFailed": 1,
        },
    )
    monkeypatch.setattr(
        operations,
        "_minio_snapshot",
        lambda _settings: {
            "status": "attention",
            "backend": "minio",
            "reason": "EndpointConnectionError",
        },
    )

    snapshot = operations.build_operations_snapshot(
        ApiSettings(
            database_url="postgresql+psycopg://user:password@db.internal/mdi",
            redis_url="redis://:secret@redis.internal/13",
            minio_endpoint="https://storage.internal",
            minio_access_key="access-key",
            minio_secret_key="secret-key",
        )
    )

    assert [alert["code"] for alert in snapshot["alerts"]] == [
        "OPS_DATABASE_IDLE_IN_TRANSACTION",
        "OPS_STALE_RESEARCH_TURNS",
        "OPS_STALE_JOBS",
        "OPS_QUEUE_DEPTH_EXCEEDED",
        "OPS_WORKER_COUNT_BELOW_MINIMUM",
        "OPS_RECENT_QUEUE_FAILURES",
        "OPS_MINIO_UNAVAILABLE",
    ]
    assert all(
        {
            "code",
            "severity",
            "component",
            "observed",
            "threshold",
            "message",
        }.issubset(alert)
        for alert in snapshot["alerts"]
    )
    runbook_alerts = {
        alert["code"]: alert["runbook"]
        for alert in snapshot["alerts"]
        if "runbook" in alert
    }
    assert set(runbook_alerts) == {
        "OPS_STALE_JOBS",
        "OPS_QUEUE_DEPTH_EXCEEDED",
        "OPS_WORKER_COUNT_BELOW_MINIMUM",
    }
    assert {
        item["id"] for item in runbook_alerts.values()
    } == {
        "OPS-RUNBOOK-STALE-JOBS",
        "OPS-RUNBOOK-QUEUE-BACKLOG",
        "OPS-RUNBOOK-WORKER-HEALTH",
    }
    assert snapshot["alertSummary"] == {
        "total": 7,
        "critical": 6,
        "warning": 1,
    }
    serialized = json.dumps(snapshot, ensure_ascii=False).lower()
    for secret in (
        "password",
        "secret-key",
        "access-key",
        "db.internal",
        "redis.internal",
        "storage.internal",
    ):
        assert secret not in serialized


def test_incomplete_minio_capacity_scan_is_a_typed_read_only_warning(
    monkeypatch,
):
    monkeypatch.setattr(
        operations,
        "_database_snapshot",
        lambda _settings, _thresholds: {
            "status": "ok",
            "backend": "postgresql",
        },
    )
    monkeypatch.setattr(
        operations,
        "_redis_snapshot",
        lambda _settings, _thresholds: {
            "status": "ok",
            "backend": "redis",
        },
    )
    monkeypatch.setattr(
        operations,
        "_minio_snapshot",
        lambda _settings: {
            "status": "ok",
            "backend": "minio",
            "storageBytes": 123,
            "objectCount": 10_000,
            "usageScanComplete": False,
            "usageObjectLimit": 10_000,
            "usageReason": "MINIO_USAGE_SCAN_LIMIT_REACHED",
        },
    )

    snapshot = operations.build_operations_snapshot(ApiSettings())

    assert snapshot["status"] == "attention"
    assert snapshot["alertSummary"] == {
        "total": 1,
        "critical": 0,
        "warning": 1,
    }
    assert snapshot["alerts"] == [
        {
            "code": "OPS_MINIO_USAGE_SCAN_INCOMPLETE",
            "severity": "WARNING",
            "component": "artifactStorage",
            "observed": {
                "objectCountLowerBound": 10_000,
                "reason": "MINIO_USAGE_SCAN_LIMIT_REACHED",
            },
            "threshold": {
                "usageScanComplete": True,
                "usageObjectLimit": 10_000,
            },
            "message": (
                "The bounded MinIO capacity scan did not inspect the "
                "complete bucket; observed counts and bytes are lower bounds."
            ),
            "runbook": {
                "id": "OPS-RUNBOOK-MINIO-CAPACITY",
                "reference": (
                    "docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md"
                    "#operations-alert-response"
                ),
                "operatorAction": (
                    "当前对象数已达到有界扫描上限；先提高只读观测容量或使用"
                    "存储端聚合统计，不要删除科学 Artifact。"
                ),
                "recheckCommand": (
                    "python scripts/phase14r_operations_snapshot.py "
                    "--same-stack --fail-on-attention --compact"
                ),
            },
        }
    ]
    minio_budget = next(
        item
        for item in snapshot["storageBudgets"]["categories"]
        if item["category"] == "minio"
    )
    assert minio_budget["state"] == "unknown"
    assert minio_budget["scanComplete"] is False
    assert minio_budget["observedBytes"] == 123
    assert minio_budget["utilizationPercent"] is None


def test_minio_usage_scan_retries_transient_timeout_once(monkeypatch, tmp_path):
    import boto3

    class Client:
        calls = 0

        def head_bucket(self, **_request):
            return None

        def list_objects_v2(self, **_request):
            self.calls += 1
            if self.calls == 1:
                raise TimeoutError("transient")
            return {"Contents": [{"Size": 7}], "IsTruncated": False}

    client = Client()
    monkeypatch.setattr(boto3, "client", lambda *_args, **_kwargs: client)
    monkeypatch.setattr(
        operations,
        "_MINIO_OBSERVATION_CACHE_DIRECTORY",
        tmp_path,
    )

    snapshot = operations._minio_snapshot(
        ApiSettings(
            artifact_backend="minio",
            minio_endpoint="http://127.0.0.1:9000",
            minio_access_key="access",
            minio_secret_key="secret",
        )
    )

    assert snapshot["status"] == "ok"
    assert snapshot["storageBytes"] == 7
    assert snapshot["objectCount"] == 1
    assert snapshot["usageScanComplete"] is True
    assert snapshot["usageRetryCount"] == 1
    assert client.calls == 2


def test_minio_usage_scan_does_not_retry_non_retryable_failure(monkeypatch):
    import boto3
    from botocore.exceptions import ClientError

    class Client:
        calls = 0

        def head_bucket(self, **_request):
            return None

        def list_objects_v2(self, **_request):
            self.calls += 1
            raise ClientError(
                {"Error": {"Code": "AccessDenied"}},
                "ListObjectsV2",
            )

    client = Client()
    monkeypatch.setattr(boto3, "client", lambda *_args, **_kwargs: client)

    snapshot = operations._minio_snapshot(
        ApiSettings(
            artifact_backend="minio",
            minio_endpoint="http://127.0.0.1:9000",
            minio_access_key="access",
            minio_secret_key="secret",
        )
    )

    assert snapshot["usageScanComplete"] is False
    assert snapshot["usageReason"] == "ARTIFACT_STORAGE_AUTHENTICATION"
    assert snapshot["usageRetryCount"] == 0
    assert client.calls == 1


def test_minio_timeout_exposes_bounded_last_known_complete_without_promoting_it(
    monkeypatch,
    tmp_path,
):
    import boto3

    class Client:
        def __init__(self, *, fail: bool):
            self.fail = fail

        def head_bucket(self, **_request):
            return None

        def list_objects_v2(self, **_request):
            if self.fail:
                raise TimeoutError("transient timeout")
            return {"Contents": [{"Size": 11}], "IsTruncated": False}

    endpoint = "http://127.0.0.1:9000"
    settings = ApiSettings(
        artifact_backend="minio",
        minio_endpoint=endpoint,
        minio_bucket="cache-test",
        minio_access_key="access",
        minio_secret_key="secret",
    )
    cache_key = operations._minio_observation_cache_key(endpoint, "cache-test")
    monkeypatch.setattr(
        operations,
        "_MINIO_OBSERVATION_CACHE_DIRECTORY",
        tmp_path,
    )
    with operations._MINIO_LAST_KNOWN_COMPLETE_LOCK:
        operations._MINIO_LAST_KNOWN_COMPLETE.pop(cache_key, None)

    monkeypatch.setattr(boto3, "client", lambda *_args, **_kwargs: Client(fail=False))
    complete = operations._minio_snapshot(settings)
    assert complete["usageScanComplete"] is True
    assert complete["objectCount"] == 1

    monkeypatch.setattr(boto3, "client", lambda *_args, **_kwargs: Client(fail=True))
    timed_out = operations._minio_snapshot(settings)

    assert timed_out["usageScanComplete"] is False
    assert timed_out["usageReason"] == "ARTIFACT_STORAGE_TIMEOUT"
    assert timed_out["objectCount"] is None
    assert timed_out["storageBytes"] is None
    assert timed_out["lastKnownComplete"]["authoritative"] is False
    assert timed_out["lastKnownComplete"]["source"] == "api_process"
    assert timed_out["lastKnownComplete"]["objectCount"] == 1
    assert timed_out["lastKnownComplete"]["storageBytes"] == 11
    assert "password" not in json.dumps(timed_out).lower()



def test_minio_timeout_marks_expired_last_known_complete_without_using_it(
    monkeypatch,
    tmp_path,
):
    import boto3

    class Client:
        def head_bucket(self, **_request):
            return None

        def list_objects_v2(self, **_request):
            raise TimeoutError("timeout")

    endpoint = "http://127.0.0.1:9000"
    settings = ApiSettings(
        artifact_backend="minio",
        minio_endpoint=endpoint,
        minio_bucket="expired-cache-test",
        minio_access_key="access",
        minio_secret_key="secret",
    )
    cache_key = operations._minio_observation_cache_key(
        endpoint,
        "expired-cache-test",
    )
    with operations._MINIO_LAST_KNOWN_COMPLETE_LOCK:
        operations._MINIO_LAST_KNOWN_COMPLETE[cache_key] = {
            "capturedAt": datetime.now(timezone.utc)
            - timedelta(
                seconds=operations._MINIO_LAST_KNOWN_COMPLETE_TTL_SECONDS + 1
            ),
            "storageBytes": 99,
            "objectCount": 9,
        }
    monkeypatch.setattr(
        operations,
        "_MINIO_OBSERVATION_CACHE_DIRECTORY",
        tmp_path,
    )
    monkeypatch.setattr(boto3, "client", lambda *_args, **_kwargs: Client())

    timed_out = operations._minio_snapshot(settings)

    assert timed_out["usageScanComplete"] is False
    assert timed_out["lastKnownCompleteExpired"] is True
    assert "lastKnownComplete" not in timed_out
    assert timed_out["objectCount"] is None
    assert timed_out["storageBytes"] is None


def test_minio_observation_rejects_far_future_timestamp(monkeypatch, tmp_path):
    endpoint = "http://127.0.0.1:9000"
    bucket = "future-cache-test"
    cache_key = operations._minio_observation_cache_key(endpoint, bucket)
    monkeypatch.setattr(
        operations,
        "_MINIO_OBSERVATION_CACHE_DIRECTORY",
        tmp_path,
    )
    operations._minio_observation_path(cache_key).write_text(
        json.dumps(
            {
                "schemaVersion": "minio-observation-cache/1.0",
                "sourceFingerprint": cache_key,
                "capturedAt": (
                    datetime.now(timezone.utc) + timedelta(minutes=5)
                ).isoformat(),
                "storageBytes": 13,
                "objectCount": 1,
            }
        ),
        encoding="utf-8",
    )

    assert operations._read_minio_observation(cache_key) is None


def test_minio_timeout_uses_protected_runtime_file_after_process_restart(
    monkeypatch,
    tmp_path,
):
    import boto3

    class Client:
        def __init__(self, *, fail: bool):
            self.fail = fail

        def head_bucket(self, **_request):
            return None

        def list_objects_v2(self, **_request):
            if self.fail:
                raise TimeoutError("timeout")
            return {"Contents": [{"Size": 13}], "IsTruncated": False}

    endpoint = "http://127.0.0.1:9000"
    bucket = "runtime-file-cache"
    settings = ApiSettings(
        artifact_backend="minio",
        minio_endpoint=endpoint,
        minio_bucket=bucket,
        minio_access_key="access",
        minio_secret_key="secret",
    )
    cache_key = operations._minio_observation_cache_key(endpoint, bucket)
    monkeypatch.setattr(
        operations,
        "_MINIO_OBSERVATION_CACHE_DIRECTORY",
        tmp_path,
    )
    with operations._MINIO_LAST_KNOWN_COMPLETE_LOCK:
        operations._MINIO_LAST_KNOWN_COMPLETE.pop(cache_key, None)

    monkeypatch.setattr(
        boto3,
        "client",
        lambda *_args, **_kwargs: Client(fail=False),
    )
    assert operations._minio_snapshot(settings)["usageScanComplete"] is True
    with operations._MINIO_LAST_KNOWN_COMPLETE_LOCK:
        operations._MINIO_LAST_KNOWN_COMPLETE.pop(cache_key, None)

    monkeypatch.setattr(
        boto3,
        "client",
        lambda *_args, **_kwargs: Client(fail=True),
    )
    timed_out = operations._minio_snapshot(settings)

    assert timed_out["usageScanComplete"] is False
    assert timed_out["lastKnownComplete"]["source"] == "runtime_file"
    assert timed_out["lastKnownComplete"]["objectCount"] == 1
    assert timed_out["lastKnownComplete"]["storageBytes"] == 13
    cache_files = list(tmp_path.glob("usage-*.json"))
    assert len(cache_files) == 1
    raw = cache_files[0].read_text(encoding="utf-8")
    assert endpoint not in raw
    assert bucket not in raw
    assert "secret" not in raw


def test_resource_governance_violations_participate_in_operations_status(
    monkeypatch,
):
    monkeypatch.setattr(
        operations,
        "_database_snapshot",
        lambda _settings, _thresholds: {"status": "ok", "backend": "postgresql"},
    )
    monkeypatch.setattr(
        operations,
        "_redis_snapshot",
        lambda _settings, _thresholds: {"status": "ok", "backend": "redis"},
    )
    monkeypatch.setattr(
        operations,
        "_minio_snapshot",
        lambda _settings: {"status": "ok", "backend": "minio"},
    )
    monkeypatch.setattr(
        operations,
        "_resource_governance_snapshot",
        lambda _settings, _thresholds: {
            "status": "attention",
            "schemaVersion": "phase14r-resource-governance/1.0",
            "violations": [
                "RESOURCE_CONTEXT_LIMIT_INVALID",
                "RESOURCE_TYPED_LIMIT_CONTRACT_INCOMPLETE",
            ],
        },
    )

    snapshot = operations.build_operations_snapshot(ApiSettings())

    assert snapshot["status"] == "attention"
    assert [alert["code"] for alert in snapshot["alerts"]] == [
        "OPS_RESOURCE_CONTEXT_LIMIT_INVALID",
        "OPS_RESOURCE_TYPED_LIMIT_CONTRACT_INCOMPLETE",
    ]
    assert all(
        alert["component"] == "resourceGovernance"
        and alert["threshold"] == "valid bounded limit"
        for alert in snapshot["alerts"]
    )


def test_degraded_worker_health_uses_the_shared_worker_runbook(monkeypatch):
    monkeypatch.setattr(
        operations,
        "_database_snapshot",
        lambda _settings, _thresholds: {
            "status": "ok",
            "backend": "postgresql",
        },
    )
    monkeypatch.setattr(
        operations,
        "_redis_snapshot",
        lambda _settings, _thresholds: {
            "status": "attention",
            "backend": "redis",
            "totalQueued": 0,
            "workerCount": 6,
            "recentFailed": 0,
            "workerHealth": {
                "status": "attention",
                "unhealthyStateCount": 1,
                "staleHeartbeatCount": 2,
            },
        },
    )
    monkeypatch.setattr(
        operations,
        "_minio_snapshot",
        lambda _settings: {"status": "ok", "backend": "minio"},
    )

    snapshot = operations.build_operations_snapshot(ApiSettings())

    assert [alert["code"] for alert in snapshot["alerts"]] == [
        "OPS_WORKER_HEALTH_DEGRADED"
    ]
    assert snapshot["alerts"][0]["observed"] == {
        "unhealthyStateCount": 1,
        "staleHeartbeatCount": 2,
    }
    assert snapshot["alerts"][0]["runbook"]["id"] == (
        "OPS-RUNBOOK-WORKER-HEALTH"
    )


def test_resource_governance_validator_rejects_unbounded_or_incomplete_limits():
    violations = operations._resource_governance_violations(
        {
            "uploads": {"perFileBytes": 10, "totalRequestBytes": 5},
            "research": {
                "maxActiveTurnsPerProject": 0,
                "queueAttentionDepth": -1,
            },
            "reports": {"maxRequestBytes": 10, "maxExportBytes": 5},
            "contextInputTokens": {"ORCHESTRATOR": 0},
            "viewerPayloadBytes": {},
            "typedLimitErrors": ["PROJECT_ACTIVE_RESEARCH_LIMIT"],
        }
    )

    assert violations == [
        "RESOURCE_UPLOAD_LIMIT_INVALID",
        "RESOURCE_RESEARCH_CONCURRENCY_INVALID",
        "RESOURCE_QUEUE_THRESHOLD_INVALID",
        "RESOURCE_REPORT_LIMIT_INVALID",
        "RESOURCE_CONTEXT_LIMIT_INVALID",
        "RESOURCE_VIEWER_LIMIT_INVALID",
        "RESOURCE_TYPED_LIMIT_CONTRACT_INCOMPLETE",
    ]


def test_operations_timestamp_normalization_treats_rq_naive_time_as_utc():
    observed = operations._as_utc(datetime(2026, 8, 29, 1, 2, 3))

    assert observed == datetime(2026, 8, 29, 1, 2, 3, tzinfo=timezone.utc)


def test_worker_health_detects_non_serving_state_and_stale_heartbeat():
    now = datetime(2026, 9, 5, 8, 0, tzinfo=timezone.utc)
    snapshot = operations._worker_health_snapshot(
        [
            SimpleNamespace(
                state="idle",
                last_heartbeat=datetime(2026, 9, 5, 7, 59, tzinfo=timezone.utc),
            ),
            SimpleNamespace(
                state="busy",
                last_heartbeat=datetime(2026, 9, 5, 7, 30),
            ),
            SimpleNamespace(
                state="suspended",
                last_heartbeat=datetime(2026, 9, 5, 7, 59, tzinfo=timezone.utc),
            ),
        ],
        stale_minutes=15,
        now=now,
    )

    assert snapshot == {
        "schemaVersion": "phase14r-worker-health/1.0",
        "status": "attention",
        "healthyCount": 1,
        "unhealthyStateCount": 1,
        "staleHeartbeatCount": 1,
        "states": {"idle": 1, "busy": 1, "suspended": 1},
    }


def test_operations_and_recovery_share_the_bounded_qualification_classifier():
    assert operations.is_qualification_project(
        project_id="agent2-phase4-project-deadbeef",
        created_by="agent2-phase4-owner-deadbeef",
    )
    assert not operations.is_qualification_project(
        project_id="project_0002_1a0af866391f412d",
        created_by="user_local",
    )


def test_authority_consistency_scanner_detects_orphan_without_mutation():
    engine = create_engine("sqlite://", future=True)
    metadata.create_all(engine)
    try:
        with engine.begin() as connection:
            connection.execute(
                insert(tool_calls).values(
                    id="call_orphan",
                    job_id="job_missing",
                    step_id="step_01",
                    tool_id="structure.xrd",
                    idempotency_key="job_missing:step_01",
                    attempt=1,
                    status="planned",
                    params_json={},
                )
            )
            before = connection.execute(
                select(func.count()).select_from(tool_calls)
            ).scalar_one()
            snapshot = operations._authority_consistency_snapshot(connection)
            after = connection.execute(
                select(func.count()).select_from(tool_calls)
            ).scalar_one()

        assert snapshot["readOnly"] is True
        assert snapshot["status"] == "attention"
        assert snapshot["issueCount"] == 1
        assert snapshot["issues"] == [
            {
                "code": "ORPHAN_TOOL_CALL_JOB",
                "count": 1,
                "sampleIds": ["call_orphan"],
            }
        ]
        assert before == after == 1
    finally:
        engine.dispose()


@pytest.mark.integration
def test_same_stack_operations_snapshot_reports_read_only_authority_consistency():
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 for the live authority consistency probe")
    script = Path(__file__).parents[1] / "scripts" / "phase14r_operations_snapshot.py"
    result = subprocess.run(
        [sys.executable, str(script), "--same-stack", "--compact"],
        cwd=script.parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    snapshot = json.loads(result.stdout)
    consistency = snapshot["database"]["authorityConsistency"]
    assert consistency["schemaVersion"] == "phase14r-authority-consistency/1.0"
    assert consistency["readOnly"] is True
    assert consistency["status"] == "ok"
    assert consistency["issueCount"] == 0


def test_operations_snapshot_script_is_directly_invokable_without_pythonpath():
    script = Path(__file__).parents[1] / "scripts" / "phase14r_operations_snapshot.py"
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=script.parents[1],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Emit a redacted Phase 14-R" in result.stdout


def test_operations_snapshot_script_exposes_explicit_same_stack_mode():
    script = Path(__file__).parents[1] / "scripts" / "phase14r_operations_snapshot.py"
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=script.parents[1],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--same-stack" in result.stdout
    assert "--fail-on-attention" in result.stdout
    assert "--compact" in result.stdout


def test_operations_snapshot_cli_has_deterministic_diagnostic_and_gate_exit_codes(
    monkeypatch,
    capsys,
):
    script = Path(__file__).parents[1] / "scripts" / "phase14r_operations_snapshot.py"
    module = _load_operations_script(script)
    attention = {
        "schemaVersion": "phase14r-operations-snapshot/1.0",
        "status": "attention",
        "alerts": [
            {
                "code": "OPS_STALE_JOBS",
                "severity": "CRITICAL",
                "component": "database",
                "observed": 1,
                "threshold": 0,
                "message": "Stale Job.",
            }
        ],
    }
    monkeypatch.setattr(
        operations,
        "build_operations_snapshot",
        lambda **_kwargs: attention,
    )

    assert module.main(["--compact"]) == 0
    diagnostic = json.loads(capsys.readouterr().out)
    assert diagnostic["status"] == "attention"
    assert diagnostic["alerts"][0]["code"] == "OPS_STALE_JOBS"

    assert module.main(["--compact", "--fail-on-attention"]) == 2
    gated = json.loads(capsys.readouterr().out)
    assert gated == diagnostic

    monkeypatch.setattr(
        operations,
        "build_operations_snapshot",
        lambda **_kwargs: {
            "schemaVersion": "phase14r-operations-snapshot/1.0",
            "status": "ok",
            "alerts": [],
        },
    )
    assert module.main(["--compact", "--fail-on-attention"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "ok"


def _load_operations_script(script: Path):
    spec = importlib.util.spec_from_file_location(
        "phase14r_operations_snapshot_test_module",
        script,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
