from __future__ import annotations

import json
from pathlib import Path

import pytest

from mdi_api import operations
from mdi_api.routers.platform_admin import _sanitize_operations
from mdi_api.storage_budget import (
    StorageBudgetPolicy,
    build_storage_budget_snapshot,
)


def test_storage_budget_projection_is_bounded_read_only_and_redacted(
    tmp_path: Path,
) -> None:
    (tmp_path / "apps").mkdir()
    (tmp_path / "apps" / "source.py").write_bytes(b"x" * 10)
    (tmp_path / ".phase14r-runtime-logs").mkdir()
    (tmp_path / ".phase14r-runtime-logs" / "api.log").write_bytes(b"y" * 5)
    (tmp_path / ".phase14r-test-browser-profile").mkdir()
    (tmp_path / ".phase14r-test-browser-profile" / "state").write_bytes(
        b"z" * 7
    )
    (tmp_path / ".cache").mkdir()
    (tmp_path / ".cache" / "build").write_bytes(b"c" * 11)
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    snapshot = build_storage_budget_snapshot(
        repository_root=tmp_path,
        database={"storageBytes": 13},
        artifact_storage={
            "storageBytes": 17,
            "objectCount": 2,
            "usageScanComplete": True,
        },
        policy=StorageBudgetPolicy(
            workspace_bytes=100,
            database_bytes=100,
            minio_bytes=100,
            logs_bytes=100,
            profiles_bytes=100,
            build_caches_bytes=100,
        ),
    )

    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    categories = {item["category"]: item for item in snapshot["categories"]}
    assert snapshot["schemaVersion"] == "phase14r-storage-budget/1.0"
    assert snapshot["status"] == "ok"
    assert snapshot["readOnly"] is True
    assert snapshot["redacted"] is True
    assert categories["database"]["observedBytes"] == 13
    assert categories["minio"]["observedBytes"] == 17
    assert categories["logs"]["observedBytes"] == 5
    assert categories["profiles"]["observedBytes"] == 7
    assert categories["buildCaches"]["observedBytes"] == 11
    assert before == after
    serialized = json.dumps(snapshot)
    assert str(tmp_path) not in serialized
    assert "api.log" not in serialized
    assert "phase14r-test-browser-profile" not in serialized


def test_incomplete_or_unavailable_storage_measurements_are_not_false_passes(
    tmp_path: Path,
) -> None:
    snapshot = build_storage_budget_snapshot(
        repository_root=tmp_path,
        database={},
        artifact_storage={
            "storageBytes": 8,
            "objectCount": 10_000,
            "usageScanComplete": False,
        },
        policy=StorageBudgetPolicy(
            workspace_bytes=100,
            database_bytes=100,
            minio_bytes=100,
            logs_bytes=100,
            profiles_bytes=100,
            build_caches_bytes=100,
        ),
    )

    categories = {item["category"]: item for item in snapshot["categories"]}
    assert snapshot["status"] == "partial"
    assert categories["database"]["state"] == "unknown"
    assert categories["minio"]["state"] == "unknown"
    assert categories["minio"]["observedBytes"] == 8
    assert categories["minio"]["utilizationPercent"] is None
    assert categories["minio"]["scanComplete"] is False


def test_exceeded_storage_budget_is_reported_without_deleting_content(
    tmp_path: Path,
) -> None:
    (tmp_path / "tests").mkdir()
    content = tmp_path / "tests" / "large.bin"
    content.write_bytes(b"x" * 12)

    snapshot = build_storage_budget_snapshot(
        repository_root=tmp_path,
        database={"storageBytes": 0},
        artifact_storage={
            "storageBytes": 0,
            "objectCount": 0,
            "usageScanComplete": True,
        },
        policy=StorageBudgetPolicy(
            workspace_bytes=10,
            database_bytes=10,
            minio_bytes=10,
            logs_bytes=10,
            profiles_bytes=10,
            build_caches_bytes=10,
        ),
    )

    workspace = snapshot["categories"][0]
    assert snapshot["status"] == "attention"
    assert workspace["state"] == "exceeded"
    assert workspace["observedBytes"] == 12
    assert content.read_bytes() == b"x" * 12


def test_minio_usage_scan_is_bounded_and_never_projects_object_keys() -> None:
    class Client:
        calls = 0

        def list_objects_v2(self, **request):
            self.calls += 1
            assert request["MaxKeys"] <= 1000
            return {
                "Contents": [
                    {"Key": f"secret/private/{self.calls}", "Size": 4}
                    for _ in range(request["MaxKeys"])
                ],
                "IsTruncated": True,
                "NextContinuationToken": f"token-{self.calls}",
            }

    client = Client()
    snapshot = operations._bounded_minio_usage(
        client,
        "private-bucket",
        maximum_objects=1500,
    )

    assert snapshot == {
        "storageBytes": 6000,
        "objectCount": 1500,
        "usageScanComplete": False,
        "usageObjectLimit": 1500,
        "usageReason": "MINIO_USAGE_SCAN_LIMIT_REACHED",
    }
    assert client.calls == 2
    serialized = json.dumps(snapshot)
    assert "secret/private" not in serialized
    assert "private-bucket" not in serialized


def test_minio_usage_scan_reports_missing_continuation_without_false_completion() -> None:
    class Client:
        def list_objects_v2(self, **_request):
            return {
                "Contents": [{"Key": "not-projected", "Size": 4}],
                "IsTruncated": True,
            }

    snapshot = operations._bounded_minio_usage(
        Client(),
        "private-bucket",
        maximum_objects=10,
    )

    assert snapshot == {
        "storageBytes": 4,
        "objectCount": 1,
        "usageScanComplete": False,
        "usageObjectLimit": 10,
        "usageReason": "MINIO_USAGE_SCAN_CONTINUATION_MISSING",
    }
    assert "not-projected" not in json.dumps(snapshot)


def test_invalid_storage_budget_environment_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MDI_STORAGE_BUDGET_LOGS_BYTES", "0")

    with pytest.raises(ValueError, match="positive integer"):
        StorageBudgetPolicy.from_environment()


def test_platform_admin_storage_projection_keeps_only_bounded_aggregates() -> None:
    sanitized = _sanitize_operations(
        {
            "storageBudgets": {
                "schemaVersion": "phase14r-storage-budget/1.0",
                "status": "ok",
                "readOnly": True,
                "redacted": True,
                "scanEntryLimit": 100_000,
                "categories": [
                    {
                        "category": "logs",
                        "scope": "repository-managed runtime logs",
                        "observedBytes": 10,
                        "budgetBytes": 100,
                        "utilizationPercent": 10.0,
                        "state": "within",
                        "itemCount": 2,
                        "scanComplete": True,
                        "inaccessibleCount": 0,
                        "path": "C:/secret/runtime",
                        "credential": "do-not-project",
                    }
                ],
            }
        }
    )

    serialized = json.dumps(sanitized)
    assert sanitized["storageBudgets"]["categories"][0]["observedBytes"] == 10
    assert "C:/secret/runtime" not in serialized
    assert "do-not-project" not in serialized
