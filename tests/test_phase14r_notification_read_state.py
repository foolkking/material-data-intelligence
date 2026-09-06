from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, insert, select, update
from sqlalchemy.pool import StaticPool

from mdi_api.db import (
    jobs,
    metadata,
    organizations,
    project_members,
    projects,
    user_configs,
    users,
)
from mdi_api.routers.auth import CurrentUser


def _engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    owner = CurrentUser(
        id="owner",
        email="owner@example.invalid",
        displayName="Owner",
        roles=[],
    )
    viewer = CurrentUser(
        id="viewer",
        email="viewer@example.invalid",
        displayName="Viewer",
        roles=[],
    )
    outsider = CurrentUser(
        id="outsider",
        email="outsider@example.invalid",
        displayName="Outsider",
        roles=[],
    )
    now = datetime(2026, 9, 5, 8, 0, tzinfo=timezone.utc)
    with engine.begin() as connection:
        connection.execute(
            insert(users),
            [
                {"id": user.id, "email": user.email, "display_name": user.displayName}
                for user in (owner, viewer, outsider)
            ],
        )
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(
            insert(projects),
            [
                {
                    "id": "visible",
                    "organization_id": "org",
                    "name": "Visible",
                    "created_by": owner.id,
                },
                {
                    "id": "private",
                    "organization_id": "org",
                    "name": "Private",
                    "created_by": outsider.id,
                },
            ],
        )
        connection.execute(
            insert(project_members),
            {"project_id": "visible", "user_id": viewer.id, "role": "viewer"},
        )
        connection.execute(
            insert(jobs),
            [
                {
                    "id": "job-visible",
                    "project_id": "visible",
                    "kind": "analysis",
                    "status": "completed",
                    "created_by": owner.id,
                    "updated_at": now,
                },
                {
                    "id": "job-private",
                    "project_id": "private",
                    "kind": "analysis",
                    "status": "completed",
                    "created_by": outsider.id,
                    "updated_at": now,
                },
            ],
        )
    return engine, owner, viewer, outsider


def test_notification_read_state_persists_per_user_and_exact_job_revision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from mdi_api.routers import secured_runtime

    engine, owner, viewer, _outsider = _engine()
    monkeypatch.setattr(
        secured_runtime,
        "create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    marked = secured_runtime.update_notification_read_state(
        "visible",
        "job-visible",
        secured_runtime.NotificationReadStateUpdate(read=True),
        viewer,
    )
    assert marked["read"] is True
    assert secured_runtime.list_notification_read_states(viewer)["items"] == [marked]
    assert secured_runtime.list_notification_read_states(owner)["items"] == []

    with engine.begin() as connection:
        connection.execute(
            update(jobs)
            .where(jobs.c.id == "job-visible")
            .values(updated_at=datetime(2026, 9, 5, 9, 0, tzinfo=timezone.utc))
        )
    assert secured_runtime.list_notification_read_states(viewer)["items"] == []

    secured_runtime.update_notification_read_state(
        "visible",
        "job-visible",
        secured_runtime.NotificationReadStateUpdate(read=True),
        viewer,
    )
    cleared = secured_runtime.update_notification_read_state(
        "visible",
        "job-visible",
        secured_runtime.NotificationReadStateUpdate(read=False),
        viewer,
    )
    assert cleared["read"] is False
    assert secured_runtime.list_notification_read_states(viewer)["items"] == []
    with engine.connect() as connection:
        assert connection.execute(
            select(user_configs).where(user_configs.c.user_id == viewer.id)
        ).mappings().all() == []


def test_notification_read_state_fails_closed_for_other_projects_and_jobs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from mdi_api.routers import secured_runtime

    engine, _owner, viewer, _outsider = _engine()
    monkeypatch.setattr(
        secured_runtime,
        "create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    with pytest.raises(HTTPException) as cross_project:
        secured_runtime.update_notification_read_state(
            "private",
            "job-private",
            secured_runtime.NotificationReadStateUpdate(read=True),
            viewer,
        )
    assert cross_project.value.status_code == 403

    with pytest.raises(HTTPException) as wrong_job_project:
        secured_runtime.update_notification_read_state(
            "visible",
            "job-private",
            secured_runtime.NotificationReadStateUpdate(read=True),
            viewer,
        )
    assert wrong_job_project.value.status_code == 404
