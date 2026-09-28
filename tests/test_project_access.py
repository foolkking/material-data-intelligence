from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from starlette.requests import Request
from sqlalchemy import create_engine, delete, insert, select, update
from sqlalchemy.pool import StaticPool
from fastapi import HTTPException
from mdi_api.access import require_project_access
from mdi_api.database import RepositoryFactory
from mdi_api.db import (
    agent2_scientific_report_snapshots,
    audit_logs,
    datasets,
    jobs,
    metadata,
    organizations,
    project_configs,
    project_members,
    projects,
    reports,
    research_session_runs,
    research_turns,
    scientific_objects,
    scientific_object_versions,
    scientific_result_snapshots,
    agent2_scientific_interpretations,
    sessions,
    user_configs,
    users,
    messages,
)
from mdi_api.routers.auth import CurrentUser
from mdi_api.routers.datasets import BulkDatasetActionRequest, UpdateDatasetRequest
from mdi_api.routers.projects import BulkProjectActionRequest, UpdateProjectRequest
from mdi_api.routers.research import (
    ResearchSessionBulkActionRequest,
    ResearchSessionCreate,
    ResearchSessionUpdate,
    bind_research_session_run,
    bulk_update_sessions,
    create_session,
    get_session,
    get_session_dependency_impact,
    reconcile_research_run_projection,
    update_session,
    validate_research_session_project,
)
from mdi_api.routers.scientific_reports import (
    ScientificReportBulkLifecycleRequest,
    ScientificReportOrganizationRequest,
    ScientificReportRevisionRequest,
    bulk_update_scientific_report_lifecycle,
    create_scientific_report_revision,
    update_scientific_report_organization,
)


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


def test_project_role_matrix_preserves_one_owner_and_bounded_member_authority():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    people = {
        role: CurrentUser(
            id=f"user-{role}",
            email=f"{role}@example.invalid",
            displayName=role.title(),
            roles=[role],
            platformRole="PLATFORM_ADMIN" if role == "platform-admin" else "USER",
        )
        for role in (
            "owner",
            "admin",
            "researcher",
            "viewer",
            "legacy-owner",
            "platform-admin",
        )
    }
    with engine.begin() as connection:
        connection.execute(
            insert(users),
            [
                {
                    "id": user.id,
                    "email": user.email,
                    "display_name": user.displayName,
                    "platform_role": user.platformRole,
                    "is_active": True,
                }
                for user in people.values()
            ],
        )
        connection.execute(insert(organizations), {"id": "org-role-matrix", "name": "Role matrix"})
        connection.execute(
            insert(projects),
            {
                "id": "project-role-matrix",
                "organization_id": "org-role-matrix",
                "name": "Role matrix",
                "created_by": people["owner"].id,
            },
        )
        connection.execute(
            insert(project_members),
            [
                {
                    "project_id": "project-role-matrix",
                    "user_id": people[role].id,
                    "role": persisted_role,
                }
                for role, persisted_role in (
                    ("admin", "admin"),
                    ("researcher", "researcher"),
                    ("viewer", "viewer"),
                    ("legacy-owner", "owner"),
                )
            ],
        )

        expected = {
            "owner": ("owner", True),
            "admin": ("admin", True),
            "researcher": ("researcher", True),
            "viewer": ("viewer", False),
            # A historical duplicate owner membership retains write access but
            # cannot acquire the immutable owner's purge identity.
            "legacy-owner": ("admin", True),
        }
        for role, (projected_role, can_write) in expected.items():
            assert require_project_access(
                connection,
                "project-role-matrix",
                people[role],
            )["access_role"] == projected_role
            if can_write:
                assert require_project_access(
                    connection,
                    "project-role-matrix",
                    people[role],
                    write=True,
                )["access_role"] == projected_role
            else:
                with pytest.raises(HTTPException) as denied:
                    require_project_access(
                        connection,
                        "project-role-matrix",
                        people[role],
                        write=True,
                    )
                assert denied.value.status_code == 403

        # Platform administration is operational authority, not implicit
        # membership in every scientific Project.
        with pytest.raises(HTTPException) as platform_admin_denied:
            require_project_access(
                connection,
                "project-role-matrix",
                people["platform-admin"],
            )
        assert platform_admin_denied.value.status_code == 403


def test_viewer_cannot_create_research_session(monkeypatch: pytest.MonkeyPatch):
    engine, _owner, viewer = _management_engine()
    monkeypatch.setattr("mdi_api.routers.research.create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr("mdi_api.routers.research.load_settings", lambda: SimpleNamespace())
    with pytest.raises(HTTPException) as exc_info:
        create_session("used", ResearchSessionCreate(title="Unauthorized research"), viewer)
    assert exc_info.value.status_code == 403


def test_report_organization_requires_project_write_access(monkeypatch: pytest.MonkeyPatch):
    engine, owner, viewer = _management_engine()
    recorded: list[dict[str, object]] = []

    class FakeReportService:
        def __init__(self, _factory):
            pass

        @staticmethod
        def get_by_report_id(_report_id: str):
            return {"project_id": "used"}

        @staticmethod
        def set_organization(report_id: str, changes: dict[str, object]):
            recorded.append({"report_id": report_id, **changes})
            return {"report_id": report_id, "project_id": "used", **changes}

    monkeypatch.setattr(
        "mdi_api.routers.scientific_reports.create_repository_factory",
        lambda: RepositoryFactory(engine),
    )
    monkeypatch.setattr(
        "mdi_api.routers.scientific_reports.ScientificReportService",
        FakeReportService,
    )

    with pytest.raises(HTTPException) as denied:
        update_scientific_report_organization(
            "report-1",
            ScientificReportOrganizationRequest(title="只读用户不能重命名"),
            viewer,
        )
    assert denied.value.status_code == 403
    assert recorded == []

    updated = update_scientific_report_organization(
        "report-1",
        ScientificReportOrganizationRequest(title="授权报告名称", pinned=True),
        owner,
    )
    assert updated["title"] == "授权报告名称"
    assert updated["pinned"] is True
    assert recorded == [
        {"report_id": "report-1", "title": "授权报告名称", "pinned": True},
    ]


def test_report_revision_requires_project_write_access(
    monkeypatch: pytest.MonkeyPatch,
):
    engine, owner, viewer = _management_engine()
    recorded: list[dict[str, object]] = []

    class FakeReportService:
        def __init__(self, _factory):
            pass

        @staticmethod
        def get_by_report_id(_report_id: str):
            return {"project_id": "used"}

        @staticmethod
        def create_revision(
            report_id: str,
            *,
            created_by: str,
            reason: str,
            title: str | None,
        ):
            recorded.append(
                {
                    "report_id": report_id,
                    "created_by": created_by,
                    "reason": reason,
                    "title": title,
                }
            )
            return {
                "report_id": "report-revision",
                "project_id": "used",
                "revision_number": 2,
            }

    monkeypatch.setattr(
        "mdi_api.routers.scientific_reports.create_repository_factory",
        lambda: RepositoryFactory(engine),
    )
    monkeypatch.setattr(
        "mdi_api.routers.scientific_reports.ScientificReportService",
        FakeReportService,
    )

    request = ScientificReportRevisionRequest(
        reason="USER_REVISION",
        title="授权修订",
    )
    with pytest.raises(HTTPException) as denied:
        create_scientific_report_revision("report-1", request, viewer)
    assert denied.value.status_code == 403
    assert recorded == []

    created = create_scientific_report_revision("report-1", request, owner)
    assert created["revision_number"] == 2
    assert recorded == [
        {
            "report_id": "report-1",
            "created_by": owner.id,
            "reason": "USER_REVISION",
            "title": "授权修订",
        }
    ]


def test_report_bulk_lifecycle_requires_project_write_access(
    monkeypatch: pytest.MonkeyPatch,
):
    engine, owner, viewer = _management_engine()
    recorded: list[dict[str, object]] = []

    class FakeReportService:
        def __init__(self, _factory):
            pass

        @staticmethod
        def bulk_set_lifecycle(
            project_id: str,
            report_ids: list[str],
            lifecycle: str,
        ):
            recorded.append(
                {
                    "project_id": project_id,
                    "report_ids": report_ids,
                    "lifecycle": lifecycle,
                }
            )
            return {
                "lifecycle": lifecycle,
                "reportIds": report_ids,
                "count": len(report_ids),
                "items": [],
            }

    monkeypatch.setattr(
        "mdi_api.routers.scientific_reports.create_repository_factory",
        lambda: RepositoryFactory(engine),
    )
    monkeypatch.setattr(
        "mdi_api.routers.scientific_reports.ScientificReportService",
        FakeReportService,
    )
    request = ScientificReportBulkLifecycleRequest(
        reportIds=["report-1", "report-2"],
        lifecycle="ARCHIVED",
    )
    with pytest.raises(HTTPException) as denied:
        bulk_update_scientific_report_lifecycle("used", request, viewer)
    assert denied.value.status_code == 403
    assert recorded == []

    updated = bulk_update_scientific_report_lifecycle("used", request, owner)
    assert updated["count"] == 2
    assert recorded == [
        {
            "project_id": "used",
            "report_ids": ["report-1", "report-2"],
            "lifecycle": "ARCHIVED",
        }
    ]


def test_research_session_lifecycle_is_recoverable_and_preserves_history(monkeypatch: pytest.MonkeyPatch):
    engine, owner, viewer = _management_engine()
    stranger = CurrentUser(id="stranger", email="stranger@example.invalid", displayName="Stranger", roles=[])
    monkeypatch.setattr("mdi_api.routers.research.create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr("mdi_api.routers.research.load_settings", lambda: SimpleNamespace())
    now = datetime.now(timezone.utc)
    with engine.begin() as connection:
        connection.execute(insert(sessions), {
            "id": "research-lifecycle",
            "project_id": "used",
            "mode": "project",
            "status": "active",
            "created_by": owner.id,
            "created_at": now,
        })
        connection.execute(insert(messages), {
            "id": "research-lifecycle-message",
            "session_id": "research-lifecycle",
            "role": "user",
            "content_summary": "保留历史研究",
            "created_at": now,
        })

    trashed = update_session(
        "research-lifecycle",
        ResearchSessionUpdate(lifecycle="TRASHED"),
        owner,
    )
    assert trashed["status"] == "trashed"
    assert trashed["messages"][0]["content"] == "保留历史研究"
    assert trashed["retentionPolicy"]["manualPurge"] == "NOT_SUPPORTED_FOR_ENTITY"
    impact = get_session_dependency_impact("research-lifecycle", owner)
    assert impact["entity"] == "research_session"
    assert impact["dependencyCount"] >= 1
    assert any(item["kind"] == "messages" and item["count"] == 1 for item in impact["dependencies"])
    assert impact["canDelete"] is False
    assert impact["retentionPolicy"]["manualPurge"] == "NOT_SUPPORTED_FOR_ENTITY"
    assert get_session_dependency_impact("research-lifecycle", viewer)["entityId"] == "research-lifecycle"
    with pytest.raises(HTTPException) as impact_stranger_error:
        get_session_dependency_impact("research-lifecycle", stranger)
    assert impact_stranger_error.value.status_code == 403
    with pytest.raises(HTTPException) as write_error:
        from mdi_api.routers.research import ResearchMessageCreate, create_message
        create_message("research-lifecycle", ResearchMessageCreate(content="不应写入"), owner)
    assert write_error.value.status_code == 409

    with pytest.raises(HTTPException) as viewer_error:
        update_session(
            "research-lifecycle",
            ResearchSessionUpdate(lifecycle="ACTIVE"),
            viewer,
        )
    assert viewer_error.value.status_code == 403

    restored = update_session(
        "research-lifecycle",
        ResearchSessionUpdate(lifecycle="ACTIVE"),
        owner,
    )
    assert restored["status"] == "active"
    assert get_session("research-lifecycle", owner)["messages"][0]["content"] == "保留历史研究"

    organized = update_session(
        "research-lifecycle",
        ResearchSessionUpdate(title="硅结构历史研究", pinned=True),
        owner,
    )
    assert organized["title"] == "硅结构历史研究"
    assert organized["pinned"] is True

    archived = update_session(
        "research-lifecycle",
        ResearchSessionUpdate(lifecycle="ARCHIVED"),
        owner,
    )
    assert archived["status"] == "archived"
    trashed_from_archive = update_session(
        "research-lifecycle",
        ResearchSessionUpdate(lifecycle="TRASHED"),
        owner,
    )
    assert trashed_from_archive["status"] == "trashed"
    restored_to_archive = update_session(
        "research-lifecycle",
        ResearchSessionUpdate(lifecycle="ACTIVE"),
        owner,
    )
    assert restored_to_archive["status"] == "archived"
    assert restored_to_archive["title"] == "硅结构历史研究"
    assert restored_to_archive["pinned"] is True


def test_research_session_bulk_actions_are_project_scoped_and_atomic(
    monkeypatch: pytest.MonkeyPatch,
):
    engine, owner, viewer = _management_engine()
    monkeypatch.setattr(
        "mdi_api.routers.research.create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(
        "mdi_api.routers.research.load_settings", lambda: SimpleNamespace()
    )
    now = datetime.now(timezone.utc)
    turn_id = uuid4()
    with engine.begin() as connection:
        connection.execute(
            insert(sessions),
            [
                {
                    "id": "bulk-research-one",
                    "project_id": "used",
                    "mode": "project",
                    "status": "active",
                    "is_pinned": False,
                    "created_by": owner.id,
                    "created_at": now,
                },
                {
                    "id": "bulk-research-two",
                    "project_id": "used",
                    "mode": "project",
                    "status": "active",
                    "is_pinned": False,
                    "created_by": owner.id,
                    "created_at": now,
                },
                {
                    "id": "bulk-research-foreign",
                    "project_id": "empty",
                    "mode": "project",
                    "status": "active",
                    "is_pinned": False,
                    "created_by": owner.id,
                    "created_at": now,
                },
            ],
        )
        connection.execute(
            insert(messages),
            {
                "id": "bulk-research-message",
                "session_id": "bulk-research-two",
                "role": "user",
                "content_summary": "仍在运行的研究",
                "created_at": now,
            },
        )
        connection.execute(
            insert(research_turns),
            {
                "id": turn_id,
                "project_id": "used",
                "research_session_id": "bulk-research-two",
                "sequence_no": 1,
                "user_message_id": "bulk-research-message",
                "action_type": "ANALYZE",
                "status": "RUNNING",
            },
        )

    selection = ["bulk-research-one", "bulk-research-two"]
    with pytest.raises(HTTPException) as active_turn_error:
        bulk_update_sessions(
            "used",
            ResearchSessionBulkActionRequest(
                sessionIds=selection, action="ARCHIVE"
            ),
            owner,
        )
    assert active_turn_error.value.status_code == 409
    with engine.connect() as connection:
        statuses = connection.execute(
            select(sessions.c.id, sessions.c.status)
            .where(sessions.c.id.in_(selection))
            .order_by(sessions.c.id)
        ).all()
    assert statuses == [
        ("bulk-research-one", "active"),
        ("bulk-research-two", "active"),
    ]

    with engine.begin() as connection:
        connection.execute(
            update(research_turns)
            .where(research_turns.c.id == turn_id)
            .values(status="COMPLETED")
        )
    trashed = bulk_update_sessions(
        "used",
        ResearchSessionBulkActionRequest(
            sessionIds=[*selection, "bulk-research-one"], action="TRASH"
        ),
        owner,
    )
    assert trashed == {
        "action": "TRASH",
        "sessionIds": selection,
        "count": 2,
    }
    restored = bulk_update_sessions(
        "used",
        ResearchSessionBulkActionRequest(sessionIds=selection, action="RESTORE"),
        owner,
    )
    assert restored["count"] == 2

    with pytest.raises(HTTPException) as viewer_error:
        bulk_update_sessions(
            "used",
            ResearchSessionBulkActionRequest(
                sessionIds=selection, action="PIN"
            ),
            viewer,
        )
    assert viewer_error.value.status_code == 403

    with pytest.raises(HTTPException) as cross_project_error:
        bulk_update_sessions(
            "used",
            ResearchSessionBulkActionRequest(
                sessionIds=["bulk-research-one", "bulk-research-foreign"],
                action="PIN",
            ),
            owner,
        )
    assert cross_project_error.value.status_code == 403
    with engine.connect() as connection:
        state = connection.execute(
            select(
                sessions.c.id,
                sessions.c.status,
                sessions.c.is_pinned,
                sessions.c.pre_trash_status,
            )
            .where(sessions.c.id.in_(selection))
            .order_by(sessions.c.id)
        ).all()
    assert state == [
        ("bulk-research-one", "active", False, None),
        ("bulk-research-two", "active", False, None),
    ]


def test_research_run_binding_is_project_scoped_idempotent_and_projected(monkeypatch: pytest.MonkeyPatch):
    engine, owner, _viewer = _management_engine()
    monkeypatch.setattr("mdi_api.routers.research.create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr("mdi_api.routers.research.load_settings", lambda: SimpleNamespace())
    with engine.begin() as connection:
        connection.execute(insert(sessions), [
            {"id": "research-owner", "project_id": "used", "mode": "project", "status": "active", "created_by": owner.id},
            {"id": "research-other", "project_id": "empty", "mode": "project", "status": "active", "created_by": owner.id},
        ])
        connection.execute(insert(messages), {
            "id": "message-bound",
            "session_id": "research-owner",
            "role": "user",
            "content_summary": "分析绑定结果",
            "created_at": datetime.now(timezone.utc),
        })
        connection.execute(insert(jobs), [
            {"id": "job-bound", "project_id": "used", "dataset_id": "dataset", "kind": "analysis", "status": "completed", "created_by": owner.id},
            {"id": "job-other", "project_id": "empty", "dataset_id": None, "kind": "analysis", "status": "completed", "created_by": owner.id},
        ])
        bound_turn_id = uuid4()
        connection.execute(insert(research_turns), {
            "id": bound_turn_id,
            "project_id": "used",
            "research_session_id": "research-owner",
            "sequence_no": 1,
            "user_message_id": "message-bound",
            "action_type": "ANALYZE",
            "status": "COMPLETED",
            "job_id": "job-bound",
        })

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
    assert view["runReferences"][0]["researchTurnId"] == str(bound_turn_id)
    with engine.connect() as connection:
        assert connection.execute(select(research_session_runs.c.job_id)).scalars().all() == ["job-bound"]

    with pytest.raises(HTTPException) as exc_info:
        bind_research_session_run("research-owner", "job-other", owner)
    assert exc_info.value.status_code == 403


def test_session_projection_includes_direct_turn_without_legacy_binding(monkeypatch: pytest.MonkeyPatch):
    engine, owner, _viewer = _management_engine()
    monkeypatch.setattr("mdi_api.routers.research.create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr("mdi_api.routers.research.load_settings", lambda: SimpleNamespace())
    started_at = datetime(2026, 8, 28, 9, 0, tzinfo=timezone.utc)
    turn_id = uuid4()
    with engine.begin() as connection:
        connection.execute(insert(sessions), {
            "id": "research-direct",
            "project_id": "used",
            "mode": "project",
            "status": "active",
            "created_by": owner.id,
            "created_at": started_at,
        })
        connection.execute(insert(messages), {
            "id": "message-direct",
            "session_id": "research-direct",
            "role": "user",
            "content_summary": "恢复现代研究会话",
            "created_at": started_at + timedelta(minutes=1),
        })
        connection.execute(insert(jobs), {
            "id": "job-modern-direct",
            "project_id": "used",
            "dataset_id": "dataset",
            "kind": "analysis",
            "status": "completed",
            "created_by": owner.id,
            "created_at": started_at + timedelta(minutes=2),
        })
        connection.execute(insert(research_turns), {
            "id": turn_id,
            "project_id": "used",
            "research_session_id": "research-direct",
            "sequence_no": 1,
            "user_message_id": "message-direct",
            "action_type": "ANALYZE",
            "status": "COMPLETED",
            "job_id": "job-modern-direct",
            "created_at": started_at + timedelta(minutes=2),
        })

    view = get_session("research-direct", owner)
    assert view["runIds"] == ["job-modern-direct"]
    assert view["runReferences"] == [{
        "jobId": "job-modern-direct",
        "createdAt": (started_at + timedelta(minutes=2)).replace(tzinfo=None).isoformat(),
        "researchTurnId": str(turn_id),
    }]


def test_projection_reconciliation_prefers_direct_turn_relation(monkeypatch: pytest.MonkeyPatch):
    engine, owner, _viewer = _management_engine()
    monkeypatch.setattr("mdi_api.routers.research.create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr("mdi_api.routers.research.load_settings", lambda: SimpleNamespace())
    captured: dict[str, object] = {}

    def capture(session_id: str, request, current_user):
        captured.update({"session_id": session_id, "request": request, "user": current_user})
        return {"ok": True}

    monkeypatch.setattr("mdi_api.routers.research.create_assistant_projection", capture)
    turn_id = uuid4()
    with engine.begin() as connection:
        connection.execute(insert(sessions), {
            "id": "research-projection",
            "project_id": "used",
            "mode": "project",
            "status": "active",
            "created_by": owner.id,
        })
        connection.execute(insert(jobs), {
            "id": "job-projection-direct",
            "project_id": "used",
            "dataset_id": "dataset",
            "kind": "analysis",
            "status": "completed",
            "created_by": owner.id,
        })
        connection.execute(insert(messages), {
            "id": "message-projection-direct",
            "session_id": "research-projection",
            "role": "user",
            "content_summary": "生成结果解释",
        })
        connection.execute(insert(research_turns), {
            "id": turn_id,
            "project_id": "used",
            "research_session_id": "research-projection",
            "sequence_no": 1,
            "user_message_id": "message-projection-direct",
            "status": "COMPLETED",
            "job_id": "job-projection-direct",
        })

    assert reconcile_research_run_projection("job-projection-direct", owner) == {"ok": True}
    assert captured["session_id"] == "research-projection"
    assert captured["user"] is owner


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


def test_product_search_is_bounded_and_project_scoped(monkeypatch: pytest.MonkeyPatch):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    dataset_results = secured_runtime.search_product_secured(q="materials", current_user=viewer)
    assert dataset_results["count"] == 1
    assert dataset_results["items"][0]["kind"] == "dataset"
    assert dataset_results["items"][0]["projectId"] == "used"
    assert dataset_results["items"][0]["href"] == "/projects/used/data?dataset=dataset"

    project_results = secured_runtime.search_product_secured(q="Science", kind="project", current_user=viewer)
    assert project_results["count"] == 1
    assert project_results["items"][0]["id"] == "used"

    bounded = secured_runtime.search_product_secured(q="", limit=1, current_user=viewer)
    assert len(bounded["items"]) == 1
    assert bounded["count"] >= 2
    assert bounded["truncated"] is True

    with pytest.raises(HTTPException) as exc_info:
        secured_runtime.search_product_secured(q="materials", project_id="private", current_user=owner)
    assert exc_info.value.status_code == 404


def test_saved_product_searches_are_user_owned_bounded_and_reauthorized(
    monkeypatch: pytest.MonkeyPatch,
):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, viewer = _management_engine()
    monkeypatch.setattr(
        secured_runtime,
        "create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(
        secured_runtime, "load_settings", lambda: SimpleNamespace()
    )

    saved = secured_runtime.create_saved_product_search(
        secured_runtime.SavedProductSearchCreate(
            name="  已归档结构  ",
            query="  silicon  ",
            type="scientific_object",
            project="used",
            status="archived",
        ),
        owner,
    )
    assert saved["name"] == "已归档结构"
    assert saved["query"] == "silicon"
    assert saved["project"] == "used"
    assert saved["type"] == "scientific_object"
    with engine.connect() as connection:
        stored = connection.execute(
            select(user_configs.c.user_id, user_configs.c.config_json).where(
                user_configs.c.id == saved["id"]
            )
        ).mappings().one()
    assert stored["user_id"] == owner.id
    assert set(stored["config_json"]) == {
        "configKind",
        "schemaVersion",
        "name",
        "query",
        "type",
        "project",
        "status",
        "createdAt",
        "updatedAt",
    }
    assert not {
        "items",
        "results",
        "contextManifest",
        "scientificFacts",
    }.intersection(stored["config_json"])

    with pytest.raises(HTTPException) as other_user_update:
        secured_runtime.update_saved_product_search(
            saved["id"],
            secured_runtime.SavedProductSearchUpdate(name="越权修改"),
            viewer,
        )
    assert other_user_update.value.status_code == 404

    updated = secured_runtime.update_saved_product_search(
        saved["id"],
        secured_runtime.SavedProductSearchUpdate(
            name="数据检索",
            query="materials",
            type="dataset",
            status="all",
        ),
        owner,
    )
    assert updated["name"] == "数据检索"
    assert updated["status"] == "all"
    assert [item["id"] for item in secured_runtime.list_saved_product_searches(owner)] == [
        saved["id"]
    ]
    executed = secured_runtime.execute_saved_product_search(
        saved["id"],
        secured_runtime.SavedProductSearchExecute(limit=10),
        owner,
    )
    assert executed["savedSearch"]["id"] == saved["id"]
    assert executed["query"] == "materials"
    assert executed["count"] == 1
    assert executed["items"][0]["projectId"] == "used"
    assert executed["items"][0]["kind"] == "dataset"
    with pytest.raises(HTTPException) as other_user_execute:
        secured_runtime.execute_saved_product_search(
            saved["id"],
            secured_runtime.SavedProductSearchExecute(),
            viewer,
        )
    assert other_user_execute.value.status_code == 404

    cleared = secured_runtime.update_saved_product_search(
        saved["id"],
        secured_runtime.SavedProductSearchUpdate(type=None, project=None),
        owner,
    )
    assert cleared["type"] is None
    assert cleared["project"] is None
    with pytest.raises(ValueError):
        secured_runtime.SavedProductSearchUpdate(status=None)

    viewer_saved = secured_runtime.create_saved_product_search(
        secured_runtime.SavedProductSearchCreate(
            name="共享项目数据", query="materials", project="used"
        ),
        viewer,
    )
    with engine.begin() as connection:
        connection.execute(
            delete(project_members).where(
                project_members.c.project_id == "used",
                project_members.c.user_id == viewer.id,
            )
        )
    assert secured_runtime.list_saved_product_searches(viewer) == []
    with pytest.raises(HTTPException) as revoked_search:
        secured_runtime.execute_saved_product_search(
            viewer_saved["id"],
            secured_runtime.SavedProductSearchExecute(),
            viewer,
        )
    assert revoked_search.value.status_code == 404

    deleted = secured_runtime.delete_saved_product_search(saved["id"], owner)
    assert deleted == {"id": saved["id"], "deleted": True}
    assert secured_runtime.list_saved_product_searches(owner) == []


def test_product_search_matches_authorized_project_organization_tags(monkeypatch: pytest.MonkeyPatch):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, _viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())
    with engine.begin() as connection:
        connection.execute(
            insert(project_configs),
            {"project_id": "used", "config_json": {"projectTags": ["XRD", "待复核"]}},
        )

    result = secured_runtime.search_product_secured(q="xrd", kind="project", current_user=owner)

    assert result["count"] == 1
    assert result["items"][0]["id"] == "used"
    assert "XRD" in result["items"][0]["subtitle"]


def test_product_search_matches_authoritative_dataset_object_and_result_semantics(
    monkeypatch: pytest.MonkeyPatch,
):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, _viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    object_id = uuid4()
    version_id = uuid4()
    turn_id = uuid4()
    interpretation_id = uuid4()
    with engine.begin() as connection:
        connection.execute(
            update(datasets)
            .where(datasets.c.id == "dataset")
            .values(
                metadata_json={
                    "sampleIdentity": "sample_id",
                    "rows": [
                        {"sample_id": "mat-2", "formula": "SiO2", "band_gap": 2.4},
                    ],
                    "semanticDescription": "band gap screening dataset",
                }
            ),
        )
        connection.execute(
            insert(scientific_objects),
            {
                "id": object_id,
                "project_id": "used",
                "kind": "structure",
                "object_type": "structure",
                "display_name": "Silicon oxide structure",
                "lifecycle_status": "ACTIVE",
                "current_version_id": None,
                "created_by_user_id": owner.id,
            },
        )
        connection.execute(
            insert(scientific_object_versions),
            {
                "id": version_id,
                "scientific_object_id": object_id,
                "version_no": 1,
                "object_type": "structure",
                "object_schema_version": "2.0",
                "source_resource_refs_json": [],
                "parent_object_version_refs_json": [],
                "semantic_profile_ref_json": None,
                "normalized_payload_ref_json": {"storageKey": "objects/structure.json"},
                "content_hash": "c" * 64,
                "semantic_hash": "s" * 64,
                "canonical_metadata_json": {
                    "formula": "SiO2",
                    "space_group": "Pnma",
                    "sample_id": "structure-7",
                },
                "availability_status": "AVAILABLE",
                "created_by_user_id": owner.id,
            },
        )
        connection.execute(
            update(scientific_objects)
            .where(scientific_objects.c.id == object_id)
            .values(current_version_id=version_id),
        )
        connection.execute(
            insert(sessions),
            {
                "id": "search-semantic-session",
                "project_id": "used",
                "dataset_id": "dataset",
                "mode": "project",
                "status": "active",
                "created_by": owner.id,
            },
        )
        connection.execute(
            insert(messages),
            {
                "id": "search-semantic-message",
                "session_id": "search-semantic-session",
                "role": "user",
                "content_summary": "分析 mat-2 的 band gap",
                "payload_json": {},
            },
        )
        connection.execute(
            insert(research_turns),
            {
                "id": turn_id,
                "project_id": "used",
                "research_session_id": "search-semantic-session",
                "sequence_no": 1,
                "user_message_id": "search-semantic-message",
                "action_type": "ANALYZE",
                "status": "COMPLETED",
            },
        )
        connection.execute(
            insert(scientific_result_snapshots),
            {
                "id": uuid4(),
                "project_id": "used",
                "research_turn_id": turn_id,
                "job_id": None,
                "schema_version": "1.0",
                "projection_version": "test/1.0",
                "execution_status": "SUCCESS",
                "relevance_status": "CURRENT",
                "source_fingerprint": "r" * 64,
                "bundle_json": {
                    "research_question": "What is the band gap of mat-2?",
                    "result_items": [
                        {"id": "dataset.item.mat-2", "title": "Band gap for mat-2"}
                    ],
                    "facts": [
                        {
                            "fact_id": "dataset.band_gap.mat-2",
                            "predicate": "band_gap",
                            "subject_ref": "mat-2",
                            "value": 2.4,
                            "unit": "eV",
                        }
                    ],
                },
            },
        )
        result_id = connection.execute(
            select(scientific_result_snapshots.c.id).where(
                scientific_result_snapshots.c.research_turn_id == turn_id
            )
        ).scalar_one()
        connection.execute(
            insert(agent2_scientific_interpretations),
            {
                "id": interpretation_id,
                "research_turn_id": turn_id,
                "result_snapshot_id": result_id,
                "project_id": "used",
                "contract_version": "1.0",
                "prompt_version": "test",
                "provider": "test",
                "model": "test",
                "provider_request_id": None,
                "repair_attempted": False,
                "input_fingerprint": "i" * 64,
                "grounding_status": "VALID",
                "output_json": {
                    "answer_lead": "mat-2 的 band gap 为 2.4 eV。",
                    "primary_findings": [
                        {
                            "finding_id": "finding.mat-2.band-gap",
                            "statement": "mat-2 的 band gap 为 2.4 eV。",
                        }
                    ],
                },
            },
        )

    dataset_sample = secured_runtime.search_product_secured(
        q="mat-2", kind="dataset", current_user=owner
    )
    assert dataset_sample["count"] == 1
    assert dataset_sample["items"][0]["id"] == "dataset"

    dataset_formula = secured_runtime.search_product_secured(
        q="SiO2", kind="dataset", current_user=owner
    )
    assert dataset_formula["count"] == 1
    assert dataset_formula["items"][0]["id"] == "dataset"

    object_metadata = secured_runtime.search_product_secured(
        q="Pnma", kind="scientific_object", current_user=owner
    )
    assert object_metadata["count"] == 1
    assert object_metadata["items"][0]["id"] == str(object_id)

    result_fact = secured_runtime.search_product_secured(
        q="2.4", kind="result", current_user=owner
    )
    assert result_fact["count"] == 1
    assert result_fact["items"][0]["id"] == str(result_id)

    result_finding = secured_runtime.search_product_secured(
        q="为", kind="result", current_user=owner
    )
    assert result_finding["count"] == 1
    assert result_finding["items"][0]["id"] == str(result_id)
    assert result_finding["items"][0]["title"] == "What is the band gap of mat-2?"
    assert result_finding["items"][0]["subtitle"].startswith("结果 ")


def test_product_search_projects_human_research_title_instead_of_internal_session_id(
    monkeypatch: pytest.MonkeyPatch,
):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, _viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())
    with engine.begin() as connection:
        connection.execute(insert(sessions), {
            "id": "research_internal_123",
            "project_id": "used",
            "mode": "project",
            "status": "active",
            "title_override": "mat-2 组成空间复核",
            "is_pinned": True,
            "created_by": owner.id,
        })
        connection.execute(insert(messages), {
            "id": "message_search_title",
            "session_id": "research_internal_123",
            "role": "user",
            "content_summary": "比较 mat-2 的带隙与组成空间位置",
        })

    result = secured_runtime.search_product_secured(
        q="mat-2",
        kind="research",
        current_user=owner,
    )

    assert result["count"] == 1
    assert result["items"][0] == {
        "kind": "research",
        "id": "research_internal_123",
        "projectId": "used",
        "title": "mat-2 组成空间复核",
        "subtitle": "研究会话",
        "href": "/projects/used/research/research_internal_123",
        "researchTurnId": None,
        "researchSessionId": None,
        "objectVersionId": None,
        "objectType": None,
        "status": "active",
        "updatedAt": result["items"][0]["updatedAt"],
    }


def test_dataset_object_store_missing_payload_fails_closed_with_recovery_guidance(
    monkeypatch: pytest.MonkeyPatch,
):
    import mdi_api.phase2_runtime as phase2_runtime
    import mdi_api.routers.datasets as dataset_routes
    import mdi_api.routers.secured_runtime as secured_runtime

    owner = CurrentUser(id="owner", email="owner@example.invalid", displayName="Owner", roles=["researcher"])
    monkeypatch.setattr(secured_runtime, "_authorize_dataset", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        phase2_runtime,
        "get_phase2_dataset",
        lambda _dataset_id: {
            "datasetId": "dataset_xrd",
            "fileCount": 1,
            "objectCount": 1,
        },
    )

    def unavailable(_dataset_id: str):
        raise ValueError("Durable normalized source metadata is unavailable.")

    monkeypatch.setattr(dataset_routes, "get_dataset_object_store", unavailable)

    with pytest.raises(HTTPException) as exc_info:
        secured_runtime.get_dataset_object_store_secured("dataset_xrd", owner)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == {
        "code": "SOURCE_RESOURCE_UNAVAILABLE",
        "message": "此数据的解析资源暂时无法读取。源文件与数据记录仍然保留，可重试加载或重新导入源文件。",
        "retryable": True,
    }


def test_empty_dataset_object_store_is_a_valid_empty_state(
    monkeypatch: pytest.MonkeyPatch,
):
    import mdi_api.phase2_runtime as phase2_runtime
    import mdi_api.routers.secured_runtime as secured_runtime

    owner = CurrentUser(id="owner", email="owner@example.invalid", displayName="Owner", roles=["researcher"])
    monkeypatch.setattr(secured_runtime, "_authorize_dataset", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        phase2_runtime,
        "get_phase2_dataset",
        lambda _dataset_id: {"datasetId": "dataset_empty", "fileCount": 0, "objectCount": 0},
    )

    assert secured_runtime.get_dataset_object_store_secured("dataset_empty", owner) == {
        "datasetId": "dataset_empty",
        "resources": [],
        "availability": "EMPTY",
    }


def test_result_search_prefers_authoritative_turn_route():
    from mdi_api.routers.secured_runtime import _result_search_href

    assert _result_search_href("project", "snapshot", "turn-1") == "/projects/project/research?turn=turn-1"
    assert _result_search_href("project", "snapshot", "turn-1", "session-1") == "/projects/project/research/session-1?turn=turn-1"
    assert _result_search_href("project", "snapshot", job_id="job-1") == "/projects/project/research?run=job-1"
    assert _result_search_href("project", "snapshot") == "/projects/project/research"


def test_product_search_filters_archived_lifecycle_without_cross_project_leak(monkeypatch: pytest.MonkeyPatch):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, _viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())
    with engine.begin() as connection:
        connection.execute(insert(project_configs), {
            "project_id": "used",
            "config_json": {"archivedProject": True},
        })
    archived = secured_runtime.search_product_secured(q="used", kind="project", status="archived", current_user=owner)
    active = secured_runtime.search_product_secured(q="used", kind="project", status="active", current_user=owner)
    assert archived["count"] == 1
    assert archived["items"][0]["projectId"] == "used"
    assert archived["items"][0]["status"] == "archived"
    assert active["count"] == 0
    assert secured_runtime.search_product_secured(q="used", status="trashed", current_user=owner)["count"] == 0

    trashed_project = secured_runtime.update_project_secured(
        "used", UpdateProjectRequest(lifecycle="TRASHED"), owner
    )
    assert trashed_project["status"] == "trashed"
    trashed = secured_runtime.search_product_secured(q="used", kind="project", status="trashed", current_user=owner)
    assert trashed["count"] == 1
    assert trashed["items"][0]["projectId"] == "used"
    assert trashed["items"][0]["status"] == "trashed"
    assert secured_runtime.search_product_secured(q="used", status="archived", current_user=owner)["count"] == 0

    with pytest.raises(HTTPException) as exc_info:
        secured_runtime.search_product_secured(q="used", status="purged", current_user=owner)
    assert exc_info.value.status_code == 422


def test_product_search_reports_respects_modern_report_lifecycle(monkeypatch: pytest.MonkeyPatch):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, _viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())
    report_id = "report-modern-search"
    with engine.begin() as connection:
        connection.execute(insert(jobs), {
            "id": "job-search",
            "project_id": "used",
            "dataset_id": "dataset",
            "kind": "analysis",
            "status": "completed",
            "created_by": owner.id,
        })
        connection.execute(insert(reports), {
            "id": report_id,
            "project_id": "used",
            "dataset_id": "dataset",
            "job_id": "job-search",
            "version": "1",
            "title": "归档结构报告",
            "created_by": owner.id,
        })
        connection.execute(insert(agent2_scientific_report_snapshots), {
            "id": uuid4(),
            "report_id": report_id,
            "project_id": "used",
            "research_session_id": None,
            "research_turn_id": uuid4(),
            "scientific_result_snapshot_id": uuid4(),
            "scientific_interpretation_id": uuid4(),
            "contract_version": "2.0",
            "composer_version": "test",
            "prompt_version": "test",
            "source_fingerprint": "fingerprint",
            "relevance_at_generation": "CURRENT",
            "grounding_status": "VALID",
            "report_json": {"title": "归档结构报告"},
            "created_by": owner.id,
        })
        connection.execute(insert(project_configs), {
            "project_id": "used",
            "config_json": {
                "scientificReportLifecycle": {report_id: "ARCHIVED"},
                "scientificReportOrganization": {
                    report_id: {"titleOverride": "固定的结构归档报告", "pinned": True},
                },
            },
        })

    archived = secured_runtime.search_product_secured(
        q="固定的结构", kind="report", status="archived", current_user=owner,
    )
    active = secured_runtime.search_product_secured(
        q="固定的结构", kind="report", status="active", current_user=owner,
    )
    assert archived["count"] == 1
    assert archived["items"][0]["id"] == report_id
    assert archived["items"][0]["title"] == "固定的结构归档报告"
    assert archived["items"][0]["status"] == "archived"
    assert active["count"] == 0


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

    trashed = secured_runtime.update_project_secured(
        "empty", UpdateProjectRequest(lifecycle="TRASHED"), owner
    )
    assert trashed["status"] == "trashed"
    with engine.connect() as connection:
        trashed_config = connection.execute(
            select(project_configs.c.config_json).where(project_configs.c.project_id == "empty")
        ).scalar_one()
    assert trashed_config["trashedProject"] is True
    assert trashed_config["trashedPreviousStatus"] == "archived"
    assert trashed_config["archivedProject"] is True

    restored = secured_runtime.bulk_project_action_secured(
        BulkProjectActionRequest(projectIds=["empty", "empty"], action="restore"), owner
    )
    assert restored == {"action": "restore", "projectIds": ["empty"], "count": 1}
    with engine.connect() as connection:
        config = connection.execute(
            select(project_configs.c.config_json).where(project_configs.c.project_id == "empty")
        ).scalar_one()
    assert config["archivedProject"] is True
    assert "trashedProject" not in config
    assert "trashedAt" not in config

    restored_active = secured_runtime.bulk_project_action_secured(
        BulkProjectActionRequest(projectIds=["empty"], action="restore"), owner
    )
    assert restored_active["count"] == 1
    with engine.connect() as connection:
        config = connection.execute(
            select(project_configs.c.config_json).where(project_configs.c.project_id == "empty")
        ).scalar_one()
    assert config["archivedProject"] is False

    with pytest.raises(HTTPException) as exc_info:
        secured_runtime.update_project_secured("empty", UpdateProjectRequest(name="Denied"), viewer)
    assert exc_info.value.status_code == 403


def test_project_pin_is_persisted_as_non_scientific_organization_metadata(monkeypatch: pytest.MonkeyPatch):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())
    monkeypatch.setattr("mdi_api.phase2_runtime.list_phase2_projects", lambda: [])

    pinned = secured_runtime.update_project_secured("empty", UpdateProjectRequest(pinned=True), owner)
    assert pinned["pinned"] is True
    listed = secured_runtime.list_projects_secured(owner)
    assert listed[0]["id"] == "empty"
    assert listed[0]["pinned"] is True

    with pytest.raises(HTTPException) as exc_info:
        secured_runtime.update_project_secured("empty", UpdateProjectRequest(pinned=False), viewer)
    assert exc_info.value.status_code == 403

    unpinned = secured_runtime.update_project_secured("empty", UpdateProjectRequest(pinned=False), owner)
    assert unpinned["pinned"] is False
    with engine.connect() as connection:
        config = connection.execute(
            select(project_configs.c.config_json).where(project_configs.c.project_id == "empty")
        ).scalar_one()
    assert "pinnedProject" not in config


def test_bulk_project_pin_uses_the_same_non_scientific_metadata_authority(monkeypatch: pytest.MonkeyPatch):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, _viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    result = secured_runtime.bulk_project_action_secured(
        BulkProjectActionRequest(projectIds=["empty"], action="pin"),
        owner,
    )
    assert result == {"action": "pin", "projectIds": ["empty"], "count": 1}
    with engine.connect() as connection:
        config = connection.execute(
            select(project_configs.c.config_json).where(project_configs.c.project_id == "empty")
        ).scalar_one()
    assert config["pinnedProject"] is True


def test_project_tags_are_bounded_non_scientific_organization_metadata(monkeypatch: pytest.MonkeyPatch):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())
    monkeypatch.setattr("mdi_api.phase2_runtime.list_phase2_projects", lambda: [])

    updated = secured_runtime.update_project_secured(
        "empty",
        UpdateProjectRequest(tags=["  Structure ", "structure", "", "XRD"]),
        owner,
    )
    assert updated["tags"] == ["Structure", "XRD"]
    listed = secured_runtime.list_projects_secured(owner)
    assert listed[0]["tags"] == ["Structure", "XRD"]

    with pytest.raises(HTTPException) as exc_info:
        secured_runtime.update_project_secured(
            "empty", UpdateProjectRequest(tags=["XRD"]), viewer
        )
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


def test_dependency_impact_preview_is_server_derived_and_authorized(monkeypatch: pytest.MonkeyPatch):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    project_impact = secured_runtime.get_project_dependency_impact_secured("used", owner)
    assert project_impact["entity"] == "project"
    assert project_impact["entityId"] == "used"
    assert project_impact["dependencyCount"] >= 2
    assert any(item["kind"] == "datasets" and item["count"] == 2 for item in project_impact["dependencies"])
    assert next(
        item["href"]
        for item in project_impact["dependencies"]
        if item["kind"] == "datasets"
    ) == "/projects/used/data"
    assert project_impact["canDelete"] is False
    assert project_impact["impact"]["historicalProvenanceProtected"] is True
    assert project_impact["retentionPolicy"]["automaticPurge"] == "DISABLED"
    assert project_impact["retentionPolicy"]["manualPurgeRequiresZeroDependencies"] is True

    dataset_impact = secured_runtime.get_dataset_dependency_impact_secured("empty-dataset", owner)
    assert dataset_impact["entity"] == "dataset"
    assert dataset_impact["entityId"] == "empty-dataset"
    assert dataset_impact["dependencyCount"] == 0
    assert dataset_impact["canDelete"] is True
    assert dataset_impact["retentionPolicy"]["referencedProvenance"] == "PROTECTED_INDEFINITELY"

    with pytest.raises(HTTPException) as exc_info:
        secured_runtime.get_project_dependency_impact_secured("used", viewer)
    assert exc_info.value.status_code == 403


def test_project_export_manifest_is_bounded_authorized_and_non_executable(monkeypatch: pytest.MonkeyPatch):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, viewer = _management_engine()
    monkeypatch.setattr(secured_runtime, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    manifest = secured_runtime.get_project_export_manifest_secured("used", owner)
    assert manifest["schemaVersion"] == "mdi.project-reproducibility-manifest/1.0"
    assert manifest["exportKind"] == "authorized_project_provenance"
    assert manifest["executable"] is False
    assert manifest["project"]["id"] == "used"
    assert manifest["datasets"][0]["id"] == "dataset"
    assert manifest["bounds"]["truncated"]["datasets"] is False
    assert "provider prompts and responses" in manifest["excluded"]

    viewer_manifest = secured_runtime.get_project_export_manifest_secured("used", viewer)
    assert viewer_manifest["project"]["id"] == "used"

    stranger = CurrentUser(id="stranger", email="stranger@example.invalid", displayName="Stranger", roles=[])
    with pytest.raises(HTTPException) as exc_info:
        secured_runtime.get_project_export_manifest_secured("used", stranger)
    assert exc_info.value.status_code == 403


def test_legacy_analysis_request_scope_is_authorized_when_project_is_supplied(
    monkeypatch: pytest.MonkeyPatch,
):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, viewer = _management_engine()
    stranger = CurrentUser(
        id="stranger",
        email="stranger@example.invalid",
        displayName="Stranger",
        roles=[],
    )
    monkeypatch.setattr(
        secured_runtime, "create_engine_from_settings", lambda _settings: engine
    )
    monkeypatch.setattr(
        secured_runtime, "load_settings", lambda: SimpleNamespace()
    )

    owner_response = secured_runtime.submit_analysis_request_secured(
        {"projectId": "used", "mode": "auto"},
        owner,
    )
    assert owner_response["status"] == "accepted"
    viewer_response = secured_runtime.submit_analysis_request_secured(
        {"project_id": "used", "mode": "auto"},
        viewer,
    )
    assert viewer_response["status"] == "accepted"

    with pytest.raises(HTTPException) as denied:
        secured_runtime.submit_analysis_request_secured(
            {"projectId": "used", "mode": "auto"},
            stranger,
        )
    assert denied.value.status_code == 403

    # Older clients without a Project scope remain supported by the retired
    # non-executing compatibility contract.
    assert secured_runtime.submit_analysis_request_secured({"mode": "auto"}, stranger)["status"] == "accepted"


def test_artifact_download_denies_foreign_project_before_storage_read(
    monkeypatch: pytest.MonkeyPatch,
):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, owner, _viewer = _management_engine()
    stranger = CurrentUser(
        id="stranger",
        email="stranger@example.invalid",
        displayName="Stranger",
        roles=[],
    )
    monkeypatch.setattr(
        secured_runtime,
        "create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(
        secured_runtime,
        "load_settings",
        lambda: SimpleNamespace(),
    )
    monkeypatch.setattr(
        "mdi_api.phase2_runtime.get_phase2_artifact",
        lambda artifact_id: {
            "id": artifact_id,
            "jobId": "job-foreign",
            "projectId": "used",
            "contentType": "text/plain",
        },
    )
    monkeypatch.setattr(
        "mdi_api.phase2_runtime.get_phase2_job",
        lambda _job_id: {"id": "job-foreign", "projectId": "used"},
    )
    download_calls: list[str] = []

    def read_download(artifact_id: str) -> dict[str, object]:
        download_calls.append(artifact_id)
        return {"id": artifact_id, "content": "authorized payload"}

    monkeypatch.setattr("mdi_api.phase2_runtime.get_phase2_artifact_download", read_download)

    with pytest.raises(HTTPException) as denied:
        secured_runtime.get_phase2_artifact_download_secured("artifact-foreign", stranger)
    assert denied.value.status_code == 403
    assert download_calls == []

    allowed = secured_runtime.get_phase2_artifact_download_secured("artifact-foreign", owner)
    assert allowed == {"id": "artifact-foreign", "content": "authorized payload"}
    assert download_calls == ["artifact-foreign"]


def test_planner_artifact_browse_and_download_share_authorization_before_storage(
    monkeypatch: pytest.MonkeyPatch,
):
    import mdi_api.routers.secured_planner as secured_planner

    engine, owner, _viewer = _management_engine()
    stranger = CurrentUser(
        id="stranger",
        email="stranger@example.invalid",
        displayName="Stranger",
        roles=[],
    )
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(
        secured_planner,
        "create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(
        secured_planner,
        "load_settings",
        lambda: SimpleNamespace(),
    )
    monkeypatch.setattr(
        secured_planner,
        "get_planner_job",
        lambda _job_id: {"id": "job-foreign", "projectId": "used"},
    )
    reads: list[tuple[str, str, bool]] = []
    monkeypatch.setattr(
        secured_planner,
        "get_planner_job_artifact_content_route",
        lambda job_id, artifact_id, download=False: reads.append(
            (job_id, artifact_id, download)
        )
        or {"ok": True},
    )

    for download in (False, True):
        with pytest.raises(HTTPException) as denied:
            secured_planner.get_planner_job_artifact_content_secured(
                "job-foreign",
                "artifact-foreign",
                download=download,
                current_user=stranger,
            )
        assert denied.value.status_code == 403
    assert reads == []

    assert secured_planner.get_planner_job_artifact_content_secured(
        "job-foreign",
        "artifact-foreign",
        current_user=owner,
    ) == {"ok": True}
    assert secured_planner.get_planner_job_artifact_content_secured(
        "job-foreign",
        "artifact-foreign",
        download=True,
        current_user=owner,
    ) == {"ok": True}
    assert reads == [
        ("job-foreign", "artifact-foreign", False),
        ("job-foreign", "artifact-foreign", True),
    ]


def test_exact_dataset_reads_deny_cross_project_user_before_payload_projection(
    monkeypatch: pytest.MonkeyPatch,
):
    import mdi_api.routers.secured_runtime as secured_runtime

    engine, _owner, _viewer = _management_engine()
    stranger = CurrentUser(
        id="stranger",
        email="stranger@example.invalid",
        displayName="Stranger",
        roles=[],
    )
    reads: list[str] = []
    monkeypatch.setattr(
        secured_runtime,
        "create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(
        secured_runtime,
        "load_settings",
        lambda: SimpleNamespace(),
    )
    monkeypatch.setattr(
        "mdi_api.phase2_runtime.get_phase2_dataset",
        lambda dataset_id: reads.append(f"dataset:{dataset_id}") or {},
    )
    monkeypatch.setattr(
        "mdi_api.phase2_runtime.get_phase2_dataset_profile",
        lambda dataset_id: reads.append(f"profile:{dataset_id}") or {},
    )
    monkeypatch.setattr(
        "mdi_api.routers.datasets.get_dataset_object_store",
        lambda dataset_id: reads.append(f"object-store:{dataset_id}") or {},
    )

    exact_reads = [
        lambda: secured_runtime.get_dataset_secured("dataset", stranger),
        lambda: secured_runtime.get_dataset_profile_secured("dataset", stranger),
        lambda: secured_runtime.get_dataset_object_store_secured(
            "dataset",
            stranger,
        ),
    ]
    for invoke in exact_reads:
        with pytest.raises(HTTPException) as denied:
            invoke()
        assert denied.value.status_code == 403
        assert "dataset" not in str(denied.value.detail)
    assert reads == []


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
    trashed = secured_runtime.update_dataset_secured(
        "empty-dataset", UpdateDatasetRequest(lifecycle="TRASHED"), owner
    )
    assert trashed["status"] == "trashed"
    with engine.connect() as connection:
        row = connection.execute(select(datasets).where(datasets.c.id == "empty-dataset")).mappings().one()
    assert row["status"] == "archived"
    assert dict(row["metadata_json"] or {})["trashedPreviousStatus"] == "archived"

    restored = secured_runtime.bulk_dataset_action_secured(
        BulkDatasetActionRequest(datasetIds=["empty-dataset"], action="restore"), owner
    )
    assert restored["count"] == 1
    with engine.connect() as connection:
        row = connection.execute(select(datasets).where(datasets.c.id == "empty-dataset")).mappings().one()
    assert row["status"] == "archived"
    assert "trashedAt" not in dict(row["metadata_json"] or {})

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
