from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from starlette.requests import Request
from sqlalchemy import create_engine, insert, select
from sqlalchemy.pool import StaticPool
from fastapi import HTTPException
from mdi_api.access import require_project_access
from mdi_api.db import audit_logs, datasets, jobs, metadata, organizations, project_configs, project_members, projects, research_session_runs, sessions, users
from mdi_api.routers.auth import CurrentUser
from mdi_api.routers.datasets import BulkDatasetActionRequest, UpdateDatasetRequest
from mdi_api.routers.projects import BulkProjectActionRequest, UpdateProjectRequest
from mdi_api.routers.research import ResearchSessionCreate, bind_research_session_run, create_session, get_session, validate_research_session_project


def test_project_access_accepts_owner_and_membership_and_rejects_other_user():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    owner = CurrentUser(id="user-owner", email="owner@example.invalid", displayName="Owner", roles=[])
    viewer = CurrentUser(id="user-viewer", email="viewer@example.invalid", displayName="Viewer", roles=[])
    stranger = CurrentUser(id="user-stranger", email="stranger@example.invalid", displayName="Stranger", roles=[])
    with engine.begin() as connection:
        connection.execute(insert(users), [
            {"id": owner.id, "email": owner.email, "display_name": owner.displayName, "is_active": True},
            {"id": viewer.id, "email": viewer.email, "display_name": viewer.displayName, "is_active": True},
            {"id": stranger.id, "email": stranger.email, "display_name": stranger.displayName, "is_active": True},
        ])
        connection.execute(insert(organizations), {"id": "org-1", "name": "Org"})
        connection.execute(insert(projects), {"id": "project-1", "organization_id": "org-1", "name": "Project", "created_by": owner.id})
        connection.execute(insert(project_members), {"project_id": "project-1", "user_id": viewer.id, "role": "viewer"})
        owner_access = require_project_access(connection, "project-1", owner)
        viewer_access = require_project_access(connection, "project-1", viewer)
        assert owner_access["id"] == "project-1"
        assert owner_access["access_role"] == "owner"
        assert viewer_access["id"] == "project-1"
        assert viewer_access["access_role"] == "viewer"
        try:
            require_project_access(connection, "project-1", stranger)
        except Exception as exc:
            assert getattr(exc, "status_code", None) == 403
        else:
            raise AssertionError("a non-member must not read a project")


def test_project_access_keeps_viewers_read_only_and_membership_scoped():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    owner = CurrentUser(id="owner", email="owner@example.invalid", displayName="Owner", roles=[])
    viewer = CurrentUser(id="viewer", email="viewer@example.invalid", displayName="Viewer", roles=[])
    stranger = CurrentUser(id="stranger", email="stranger@example.invalid", displayName="Stranger", roles=[])
    with engine.begin() as connection:
        connection.execute(insert(users), [
            {"id": user.id, "email": user.email, "display_name": user.displayName, "is_active": True}
            for user in (owner, viewer, stranger)
        ])
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(insert(projects), {"id": "project", "organization_id": "org", "name": "Project", "created_by": owner.id})
        connection.execute(insert(project_members), {"project_id": "project", "user_id": viewer.id, "role": "viewer"})

        assert require_project_access(connection, "project", viewer, write=False)["id"] == "project"
        try:
            require_project_access(connection, "project", viewer, write=True)
        except Exception as exc:
            assert getattr(exc, "status_code", None) == 403
        else:
            raise AssertionError("a viewer must not mutate a Project child resource")
        try:
            require_project_access(connection, "project", stranger)
        except Exception as exc:
            assert getattr(exc, "status_code", None) == 403
        else:
            raise AssertionError("membership must not leak across users")


def test_viewer_cannot_create_research_session(monkeypatch: pytest.MonkeyPatch):
    engine, _owner, viewer = _management_engine()
    monkeypatch.setattr("mdi_api.routers.research.create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr("mdi_api.routers.research.load_settings", lambda: SimpleNamespace())
    with pytest.raises(HTTPException) as exc_info:
        create_session("used", ResearchSessionCreate(title="Unauthorized research"), viewer)
    assert exc_info.value.status_code == 403


def test_research_run_binding_is_project_scoped_idempotent_and_projected(monkeypatch: pytest.MonkeyPatch):
    engine, owner, _viewer = _management_engine()
    monkeypatch.setattr("mdi_api.routers.research.create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr("mdi_api.routers.research.load_settings", lambda: SimpleNamespace())
    with engine.begin() as connection:
        connection.execute(insert(sessions), [
            {"id": "research-owner", "project_id": "used", "mode": "project", "status": "active", "created_by": owner.id},
            {"id": "research-other", "project_id": "empty", "mode": "project", "status": "active", "created_by": owner.id},
        ])
        connection.execute(insert(jobs), [
            {"id": "job-bound", "project_id": "used", "dataset_id": "dataset", "kind": "analysis", "status": "completed", "created_by": owner.id},
            {"id": "job-other", "project_id": "empty", "dataset_id": None, "kind": "analysis", "status": "completed", "created_by": owner.id},
        ])

    validate_research_session_project("research-owner", "used", owner)
    assert bind_research_session_run("research-owner", "job-bound", owner) == {
        "sessionId": "research-owner",
        "jobId": "job-bound",
        "bindingStatus": "bound",
    }
    assert bind_research_session_run("research-owner", "job-bound", owner)["jobId"] == "job-bound"
    view = get_session("research-owner", owner)
    assert view["runIds"] == ["job-bound"]
    assert view["runReferences"][0]["jobId"] == "job-bound"
    with engine.connect() as connection:
        assert connection.execute(select(research_session_runs.c.job_id)).scalars().all() == ["job-bound"]

    with pytest.raises(HTTPException) as exc_info:
        bind_research_session_run("research-owner", "job-other", owner)
    assert exc_info.value.status_code == 403


def test_research_run_cannot_be_reassigned_to_a_different_session(monkeypatch: pytest.MonkeyPatch):
    engine, owner, _viewer = _management_engine()
    monkeypatch.setattr("mdi_api.routers.research.create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr("mdi_api.routers.research.load_settings", lambda: SimpleNamespace())
    with engine.begin() as connection:
        connection.execute(insert(sessions), [
            {"id": "research-a", "project_id": "used", "mode": "project", "status": "active", "created_by": owner.id},
            {"id": "research-b", "project_id": "used", "mode": "project", "status": "active", "created_by": owner.id},
        ])
        connection.execute(insert(jobs), {
            "id": "job-once", "project_id": "used", "dataset_id": "dataset", "kind": "analysis", "status": "completed", "created_by": owner.id,
        })
    bind_research_session_run("research-a", "job-once", owner)
    with pytest.raises(HTTPException) as exc_info:
        bind_research_session_run("research-b", "job-once", owner)
    assert exc_info.value.status_code == 409


def test_project_listing_is_scoped_to_owner_or_membership(monkeypatch: pytest.MonkeyPatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    viewer = CurrentUser(id="viewer", email="viewer@example.invalid", displayName="Viewer", roles=[])
    with engine.begin() as connection:
        connection.execute(insert(users), {"id": viewer.id, "email": viewer.email, "display_name": viewer.displayName, "is_active": True})
        connection.execute(insert(users), [
            {"id": "owner-a", "email": "a@example.invalid", "display_name": "A", "is_active": True},
            {"id": "owner-b", "email": "b@example.invalid", "display_name": "B", "is_active": True},
        ])
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(insert(projects), [
            {"id": "shared", "organization_id": "org", "name": "Shared", "created_by": "owner-a"},
            {"id": "private", "organization_id": "org", "name": "Private", "created_by": "owner-b"},
        ])
        connection.execute(insert(project_members), {"project_id": "shared", "user_id": viewer.id, "role": "viewer"})

    import mdi_api.routers.secured_runtime as secured_runtime

    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())
    monkeypatch.setattr("mdi_api.phase2_runtime.list_phase2_projects", lambda: [])
    result = secured_runtime.list_projects_secured(viewer)
    assert [item["id"] for item in result] == ["shared"]
    assert result[0]["role"] == "viewer"


def test_expired_authenticated_session_is_rejected(monkeypatch: pytest.MonkeyPatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    with engine.begin() as connection:
        connection.execute(insert(users), {"id": "expired", "email": "expired@example.invalid", "display_name": "Expired", "is_active": True})
        connection.execute(__import__("mdi_api.db", fromlist=["auth_sessions"]).auth_sessions.insert().values(
            id="session-expired", user_id="expired", token_hash=__import__("hashlib").sha256(b"expired-token").hexdigest(),
            expires_at=now - timedelta(minutes=1),
        ))

    import mdi_api.routers.auth as auth

    monkeypatch.setattr(auth, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(auth, "load_settings", lambda: SimpleNamespace(auth_cookie_name="mdi_session", auth_required=True))
    request = Request({
        "type": "http",
        "method": "GET",
        "path": "/auth/me",
        "headers": [(b"cookie", b"mdi_session=expired-token")],
    })
    with pytest.raises(HTTPException) as exc_info:
        auth.get_current_user(request)
    assert exc_info.value.status_code == 401


def _management_engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    owner = CurrentUser(id="owner", email="owner@example.invalid", displayName="Owner", roles=[])
    viewer = CurrentUser(id="viewer", email="viewer@example.invalid", displayName="Viewer", roles=[])
    with engine.begin() as connection:
        connection.execute(insert(users), [
            {"id": owner.id, "email": owner.email, "display_name": owner.displayName, "is_active": True},
            {"id": viewer.id, "email": viewer.email, "display_name": viewer.displayName, "is_active": True},
        ])
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(insert(projects), [
            {"id": "empty", "organization_id": "org", "name": "Empty", "description": "", "created_by": owner.id},
            {"id": "used", "organization_id": "org", "name": "Used", "description": "Science", "created_by": owner.id},
        ])
        connection.execute(insert(project_members), [
            {"project_id": "empty", "user_id": viewer.id, "role": "viewer"},
            {"project_id": "used", "user_id": viewer.id, "role": "viewer"},
        ])
        connection.execute(insert(datasets), {
            "id": "dataset", "project_id": "used", "name": "materials", "status": "created", "created_by": owner.id,
        })
        connection.execute(insert(datasets), {
            "id": "empty-dataset", "project_id": "used", "name": "empty data", "status": "failed", "created_by": owner.id,
        })
    return engine, owner, viewer


def test_project_management_renames_archives_and_bulk_restores(monkeypatch: pytest.MonkeyPatch):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    updated = secured_runtime.update_project_secured(
        "empty", UpdateProjectRequest(name="Renamed", description="Updated", archived=True), owner
    )
    assert updated["name"] == "Renamed"
    assert updated["description"] == "Updated"
    assert updated["status"] == "archived"

    renamed = secured_runtime.update_project_secured("empty", UpdateProjectRequest(name="Still archived"), owner)
    assert renamed["status"] == "archived"

    restored = secured_runtime.bulk_project_action_secured(
        BulkProjectActionRequest(projectIds=["empty", "empty"], action="restore"), owner
    )
    assert restored == {"action": "restore", "projectIds": ["empty"], "count": 1}
    with engine.connect() as connection:
        config = connection.execute(
            select(project_configs.c.config_json).where(project_configs.c.project_id == "empty")
        ).scalar_one()
    assert config["archivedProject"] is False

    with pytest.raises(HTTPException) as exc_info:
        secured_runtime.update_project_secured("empty", UpdateProjectRequest(name="Denied"), viewer)
    assert exc_info.value.status_code == 403


def test_project_management_only_physically_deletes_empty_owner_project(monkeypatch: pytest.MonkeyPatch):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, _viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    with pytest.raises(HTTPException) as exc_info:
        secured_runtime.delete_empty_project_secured("used", owner)
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail["blockers"]["datasets"] == 2

    # Historical SQLite databases may predate the optional audit table. Empty
    # project deletion must remain available without weakening blocker checks.
    audit_logs.drop(engine)
    project_members.drop(engine)
    result = secured_runtime.delete_empty_project_secured("empty", owner)
    assert result == {"projectId": "empty", "deleted": True}
    with engine.connect() as connection:
        assert connection.execute(select(projects.c.id).where(projects.c.id == "empty")).scalar_one_or_none() is None
        assert connection.execute(select(projects.c.id).where(projects.c.id == "used")).scalar_one() == "used"


def test_dataset_management_preserves_pre_archive_status_and_deletes_only_empty(monkeypatch: pytest.MonkeyPatch):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    archived = secured_runtime.update_dataset_secured(
        "empty-dataset", UpdateDatasetRequest(name="renamed data", archived=True), owner
    )
    assert archived["name"] == "renamed data"
    assert archived["status"] == "archived"
    restored = secured_runtime.bulk_dataset_action_secured(
        BulkDatasetActionRequest(datasetIds=["empty-dataset"], action="restore"), owner
    )
    assert restored["count"] == 1
    with engine.connect() as connection:
        row = connection.execute(select(datasets).where(datasets.c.id == "empty-dataset")).mappings().one()
    assert row["status"] == "failed"
    assert "archivedPreviousStatus" not in dict(row["metadata_json"] or {})

    with pytest.raises(HTTPException) as exc_info:
        secured_runtime.update_dataset_secured("empty-dataset", UpdateDatasetRequest(name="denied"), viewer)
    assert exc_info.value.status_code == 403

    assert secured_runtime.delete_empty_dataset_secured("empty-dataset", owner)["deleted"] is True
    with engine.connect() as connection:
        assert connection.execute(select(datasets.c.id).where(datasets.c.id == "empty-dataset")).scalar_one_or_none() is None
