from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from mdi_api import operations
from mdi_api.config import ApiSettings


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
    assert snapshot["alertsSchemaVersion"] == "phase14r-operations-alerts/1.0"
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
        set(alert)
        == {
            "code",
            "severity",
            "component",
            "observed",
            "threshold",
            "message",
        }
        for alert in snapshot["alerts"]
    )
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


def test_operations_and_recovery_share_the_bounded_qualification_classifier():
    assert operations.is_qualification_project(
        project_id="agent2-phase4-project-deadbeef",
        created_by="agent2-phase4-owner-deadbeef",
    )
    assert not operations.is_qualification_project(
        project_id="project_0002_1a0af866391f412d",
        created_by="user_local",
    )


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
