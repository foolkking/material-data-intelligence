from __future__ import annotations

import time
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, insert
from sqlalchemy.pool import StaticPool

from mdi_api.application.jobs.leases import ExecutionLeaseLost
from mdi_api.db import (
    artifacts,
    datasets,
    jobs,
    metadata,
    organizations,
    projects,
    users,
)
from mdi_api.infrastructure.persistence.bundles import SqlAlchemyRepositoryBundle


def _repos() -> SqlAlchemyRepositoryBundle:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    with engine.begin() as connection:
        connection.execute(
            insert(users),
            {
                "id": "m1-owner",
                "email": "m1-owner@local.invalid",
                "display_name": "M1 Owner",
                "is_active": True,
            },
        )
        connection.execute(insert(organizations), {"id": "m1-org", "name": "M1"})
        connection.execute(
            insert(projects),
            {
                "id": "m1-project",
                "organization_id": "m1-org",
                "name": "M1",
                "created_by": "m1-owner",
            },
        )
        connection.execute(
            insert(datasets),
            {
                "id": "m1-dataset",
                "project_id": "m1-project",
                "name": "M1",
                "status": "profile_ready",
                "metadata_json": {},
                "created_by": "m1-owner",
            },
        )
        connection.execute(
            insert(jobs),
            {
                "id": "m1-job",
                "project_id": "m1-project",
                "dataset_id": "m1-dataset",
                "kind": "analysis",
                "status": "queued",
                "created_by": "m1-owner",
                "created_at": now,
                "updated_at": now,
            },
        )
    return SqlAlchemyRepositoryBundle.create(engine)


def test_claim_renew_expire_reclaim_and_late_renewal_fencing() -> None:
    repos = _repos()
    first = repos.jobs.claim_execution(
        "m1-job", owner="worker-a", lease_seconds=1
    )
    assert first is not None
    assert first.attempt == 1
    assert repos.jobs.claim_execution(
        "m1-job", owner="worker-b", lease_seconds=1
    ) is None
    renewed = repos.jobs.renew_execution(
        "m1-job", owner="worker-a", attempt=1, lease_seconds=1
    )
    assert renewed.attempt == 1
    time.sleep(1.1)
    second = repos.jobs.claim_execution(
        "m1-job", owner="worker-b", lease_seconds=10
    )
    assert second is not None
    assert second.reclaimed is True
    assert second.attempt == 2
    with pytest.raises(ExecutionLeaseLost):
        repos.jobs.renew_execution(
            "m1-job", owner="worker-a", attempt=1, lease_seconds=10
        )
    with pytest.raises(ExecutionLeaseLost):
        repos.jobs.set_status_for_execution(
            "m1-job", "completed", owner="worker-a", attempt=1
        )


def test_stale_toolcall_and_artifact_publication_are_rejected() -> None:
    repos = _repos()
    first = repos.jobs.claim_execution(
        "m1-job", owner="worker-a", lease_seconds=1
    )
    assert first is not None
    repos.tool_calls.save_for_execution(
        {
            "id": "call-m1",
            "jobId": "m1-job",
            "stepId": "step-1",
            "toolId": "structure.summary",
            "status": "running",
            "params": {},
        },
        owner="worker-a",
        attempt=1,
    )
    time.sleep(1.1)
    second = repos.jobs.claim_execution(
        "m1-job", owner="worker-b", lease_seconds=10
    )
    assert second is not None
    repos.tool_calls.save_for_execution(
        {
            "id": "call-m1",
            "jobId": "m1-job",
            "stepId": "step-1",
            "toolId": "structure.summary",
            "status": "running",
            "params": {},
        },
        owner="worker-b",
        attempt=2,
    )
    with pytest.raises(ExecutionLeaseLost):
        repos.tool_calls.save_for_execution(
            {
                "id": "call-m1",
                "jobId": "m1-job",
                "stepId": "step-1",
                "toolId": "structure.summary",
                "status": "completed",
                "params": {},
            },
            owner="worker-a",
            attempt=1,
        )
    with pytest.raises(ExecutionLeaseLost):
        repos.artifacts.save_for_execution(
            {
                "id": "artifact-m1",
                "projectId": "m1-project",
                "datasetId": "m1-dataset",
                "jobId": "m1-job",
                "toolCallId": "call-m1",
                "type": "metrics_json",
                "name": "stale.json",
                "storageKey": "attempts/1/stale.json",
                "contentHash": "a" * 64,
                "sha256": "a" * 64,
                "sizeBytes": 1,
                "metadata": {},
            },
            owner="worker-a",
            attempt=1,
        )
    assert repos.artifacts.list_for_job("m1-job") == []


def test_cancel_precedes_uncommitted_completion_and_projection_is_read_only() -> None:
    repos = _repos()
    lease = repos.jobs.claim_execution(
        "m1-job", owner="worker-a", lease_seconds=10
    )
    assert lease is not None
    repos.jobs.request_cancel("m1-job")
    projection = repos.jobs.lifecycle_projection("m1-job")
    assert projection["authority"] == "POSTGRESQL_JOB_ROW"
    assert projection["readOnly"] is True
    assert projection["cancelRequested"] is True
    with pytest.raises(ExecutionLeaseLost):
        repos.jobs.set_status_for_execution(
            "m1-job", "completed", owner="worker-a", attempt=1
        )
    cancelled = repos.jobs.acknowledge_cancel(
        "m1-job", owner="worker-a", attempt=1
    )
    assert cancelled["status"] == "cancelled"
    with pytest.raises(ExecutionLeaseLost):
        repos.jobs.renew_execution(
            "m1-job", owner="worker-a", attempt=1, lease_seconds=10
        )
