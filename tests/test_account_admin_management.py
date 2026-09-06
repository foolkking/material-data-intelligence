from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Response
from sqlalchemy import create_engine, func, insert, select
from sqlalchemy.pool import StaticPool
from starlette.requests import Request

from mdi_api.db import (
    account_invitations,
    audit_logs,
    auth_sessions,
    metadata,
    organizations,
    project_members,
    projects,
    users,
)
from mdi_api.routers import auth, platform_admin
from mdi_api.routers.auth import CurrentUser


def _engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    return engine


def _settings():
    return SimpleNamespace(
        auth_cookie_name="mdi_session",
        auth_required=True,
        auth_session_hours=24,
    )


def _request(token: str | None = None) -> Request:
    headers = []
    if token:
        headers.append((b"cookie", f"mdi_session={token}".encode("ascii")))
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/account",
            "headers": headers,
        }
    )


def _seed_user(engine, *, user_id: str = "user", password: str = "CurrentPassword-2026"):
    user = CurrentUser(
        id=user_id,
        email=f"{user_id}@example.invalid",
        displayName=user_id.title(),
        roles=["owner"],
    )
    with engine.begin() as connection:
        connection.execute(
            insert(users),
            {
                "id": user.id,
                "email": user.email,
                "display_name": user.displayName,
                "password_hash": auth._hash_password(password),
                "is_active": True,
            },
        )
    return user


def test_local_bootstrap_applies_only_explicit_valid_platform_role(monkeypatch):
    engine = _engine()
    monkeypatch.setattr(auth, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(auth, "load_settings", _settings)
    monkeypatch.setenv("MDI_LOCAL_USER_EMAIL", "local@example.invalid")
    monkeypatch.setenv("MDI_LOCAL_USER_PASSWORD", "LocalPassword-2026")
    monkeypatch.setenv("MDI_LOCAL_USER_PLATFORM_ROLE", "PLATFORM_ADMIN")

    admin = auth.login(
        auth.LoginRequest(
            email="local@example.invalid",
            password="LocalPassword-2026",
        ),
        Response(),
    )
    assert admin.platformRole == "PLATFORM_ADMIN"

    monkeypatch.setenv("MDI_LOCAL_USER_PLATFORM_ROLE", "not-a-role")
    ordinary = auth.login(
        auth.LoginRequest(
            email="local@example.invalid",
            password="LocalPassword-2026",
        ),
        Response(),
    )
    assert ordinary.platformRole == "USER"
    with engine.connect() as connection:
        assert connection.scalar(
            select(users.c.platform_role).where(users.c.id == "user_local")
        ) == "USER"


def test_platform_invitation_is_one_time_and_activation_creates_session(monkeypatch):
    engine = _engine()
    administrator = _seed_user(engine, user_id="admin")
    administrator = administrator.model_copy(update={"platformRole": "PLATFORM_ADMIN"})
    monkeypatch.setattr(platform_admin, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(platform_admin, "load_settings", _settings)
    monkeypatch.setattr(auth, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(auth, "load_settings", _settings)

    invitation = platform_admin.create_platform_invitation(
        platform_admin.PlatformInvitationRequest(
            email="new.researcher@example.invalid",
            displayName="New Researcher",
            expiresInDays=3,
        ),
        administrator,
    )
    assert invitation["email"] == "new.researcher@example.invalid"
    assert invitation["activationToken"]
    with engine.connect() as connection:
        stored = connection.execute(select(account_invitations)).mappings().one()
        assert stored["token_hash"] != invitation["activationToken"]
        assert stored["accepted_at"] is None

    response = Response()
    activated = auth.activate_account(
        auth.AccountActivationRequest(
            token=str(invitation["activationToken"]),
            password="NewResearcherPassword-2026",
        ),
        response,
    )
    assert activated.email == "new.researcher@example.invalid"
    assert "mdi_session=" in response.headers["set-cookie"]
    with engine.connect() as connection:
        user = connection.execute(
            select(users).where(users.c.email == activated.email)
        ).mappings().one()
        stored = connection.execute(select(account_invitations)).mappings().one()
        assert user["is_active"] is True
        assert stored["accepted_at"] is not None
        assert connection.scalar(
            select(func.count()).select_from(auth_sessions).where(
                auth_sessions.c.user_id == activated.id
            )
        ) == 1

    with pytest.raises(HTTPException) as replay:
        auth.activate_account(
            auth.AccountActivationRequest(
                token=str(invitation["activationToken"]),
                password="AnotherPassword-2026",
            ),
            Response(),
        )
    assert replay.value.detail["code"] == "ACCOUNT_INVITATION_INVALID"


def test_platform_invitation_rejects_existing_account_and_expired_token(monkeypatch):
    engine = _engine()
    administrator = _seed_user(engine, user_id="admin")
    administrator = administrator.model_copy(update={"platformRole": "PLATFORM_ADMIN"})
    monkeypatch.setattr(platform_admin, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(platform_admin, "load_settings", _settings)
    with pytest.raises(HTTPException) as existing:
        platform_admin.create_platform_invitation(
            platform_admin.PlatformInvitationRequest(
                email=administrator.email,
                displayName="Duplicate",
            ),
            administrator,
        )
    assert existing.value.detail["code"] == "ADMIN_INVITATION_ACCOUNT_EXISTS"

    raw_token = "expired-token-" + ("x" * 32)
    with engine.begin() as connection:
        connection.execute(
            insert(account_invitations).values(
                id="invite-expired",
                email="expired@example.invalid",
                display_name="Expired",
                token_hash=auth._token_hash(raw_token),
                expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
                invited_by_user_id=administrator.id,
            )
        )
    monkeypatch.setattr(auth, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(auth, "load_settings", _settings)
    with pytest.raises(HTTPException) as expired:
        auth.activate_account(
            auth.AccountActivationRequest(
                token=raw_token,
                password="ExpiredPassword-2026",
            ),
            Response(),
        )
    assert expired.value.detail["code"] == "ACCOUNT_INVITATION_INVALID"


def test_account_profile_session_password_and_deactivation_are_recoverable(
    monkeypatch,
):
    engine = _engine()
    user = _seed_user(engine)
    current_token = "current-token"
    other_token = "other-token"
    expires = datetime.now(timezone.utc) + timedelta(hours=2)
    with engine.begin() as connection:
        connection.execute(
            insert(auth_sessions),
            [
                {
                    "id": "session-current",
                    "user_id": user.id,
                    "token_hash": auth._token_hash(current_token),
                    "expires_at": expires,
                },
                {
                    "id": "session-other",
                    "user_id": user.id,
                    "token_hash": auth._token_hash(other_token),
                    "expires_at": expires,
                },
            ],
        )
    monkeypatch.setattr(auth, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(auth, "load_settings", _settings)

    updated = auth.update_profile(
        auth.ProfileUpdateRequest(displayName="  Researcher One  "),
        user,
    )
    assert updated.displayName == "Researcher One"

    listed = auth.list_auth_sessions(_request(current_token), updated)
    assert listed["count"] == 2
    assert next(item for item in listed["items"] if item["id"] == "session-current")[
        "isCurrent"
    ] is True

    revoked = auth.revoke_other_auth_sessions(_request(current_token), updated)
    assert revoked == {"ok": True, "revokedCount": 1}

    changed = auth.change_password(
        auth.PasswordChangeRequest(
            currentPassword="CurrentPassword-2026",
            newPassword="ReplacementPassword-2026",
        ),
        _request(current_token),
        updated,
    )
    assert changed == {"ok": True, "otherSessionsRevoked": 0}

    response = Response()
    assert auth.deactivate_account(
        auth.AccountDeactivationRequest(
            password="ReplacementPassword-2026",
            confirmEmail=user.email,
        ),
        response,
        updated,
    ) == {
        "ok": True,
        "provenanceRetained": True,
        "retentionPolicy": {
            "schemaVersion": "phase14r-retention/1.0",
            "automaticPurge": "DISABLED",
            "referencedProvenance": "PROTECTED_INDEFINITELY",
            "unreferencedTrash": "PROTECTED_ENTITY_RETENTION",
            "manualPurge": "NOT_SUPPORTED_FOR_ENTITY",
            "manualPurgeRequiresZeroDependencies": False,
        },
    }
    with engine.connect() as connection:
        row = connection.execute(select(users).where(users.c.id == user.id)).mappings().one()
        assert row["is_active"] is False
        assert row["display_name"] == "Researcher One"
        sessions = connection.execute(
            select(auth_sessions.c.revoked_at).where(auth_sessions.c.user_id == user.id)
        ).scalars().all()
        assert sessions and all(item is not None for item in sessions)
        actions = set(connection.execute(select(audit_logs.c.action)).scalars())
        assert {
            "account.profile.updated",
            "account.sessions.revoked_others",
            "account.password.changed",
            "account.deactivated",
        }.issubset(actions)
    assert "mdi_session=" in response.headers["set-cookie"]


def test_session_revocation_is_owner_scoped_and_current_session_uses_logout(
    monkeypatch,
):
    engine = _engine()
    user = _seed_user(engine, user_id="owner")
    other = _seed_user(engine, user_id="other")
    expires = datetime.now(timezone.utc) + timedelta(hours=2)
    with engine.begin() as connection:
        connection.execute(
            insert(auth_sessions),
            [
                {
                    "id": "session-current",
                    "user_id": user.id,
                    "token_hash": auth._token_hash("current"),
                    "expires_at": expires,
                },
                {
                    "id": "session-foreign",
                    "user_id": other.id,
                    "token_hash": auth._token_hash("foreign"),
                    "expires_at": expires,
                },
            ],
        )
    monkeypatch.setattr(auth, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(auth, "load_settings", _settings)

    with pytest.raises(HTTPException) as current:
        auth.revoke_auth_session("session-current", _request("current"), user)
    assert current.value.status_code == 409
    assert current.value.detail["code"] == "CURRENT_SESSION_REQUIRES_LOGOUT"

    with pytest.raises(HTTPException) as foreign:
        auth.revoke_auth_session("session-foreign", _request("current"), user)
    assert foreign.value.status_code == 404


def _seed_admin_data(engine):
    now = datetime.now(timezone.utc)
    with engine.begin() as connection:
        connection.execute(
            insert(users),
            [
                {
                    "id": "admin",
                    "email": "admin@example.invalid",
                    "display_name": "Admin",
                    "platform_role": "PLATFORM_ADMIN",
                    "is_active": True,
                },
                {
                    "id": "admin-two",
                    "email": "admin-two@example.invalid",
                    "display_name": "Second Admin",
                    "platform_role": "PLATFORM_ADMIN",
                    "is_active": True,
                },
                {
                    "id": "researcher",
                    "email": "researcher@example.invalid",
                    "display_name": "Researcher",
                    "platform_role": "USER",
                    "is_active": True,
                },
            ],
        )
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(
            insert(projects),
            {
                "id": "project",
                "organization_id": "org",
                "name": "Project",
                "description": "",
                "created_by": "admin",
            },
        )
        connection.execute(
            insert(project_members),
            {"project_id": "project", "user_id": "researcher", "role": "viewer"},
        )
        connection.execute(
            insert(auth_sessions),
            {
                "id": "researcher-session",
                "user_id": "researcher",
                "token_hash": auth._token_hash("researcher-token"),
                "expires_at": now + timedelta(hours=1),
            },
        )


def test_platform_admin_overview_user_management_and_sanitized_audit(monkeypatch):
    engine = _engine()
    _seed_admin_data(engine)
    administrator = CurrentUser(
        id="admin",
        email="admin@example.invalid",
        displayName="Admin",
        roles=[],
        platformRole="PLATFORM_ADMIN",
    )
    monkeypatch.setattr(
        platform_admin, "create_engine_from_settings", lambda _settings: engine
    )
    monkeypatch.setattr(platform_admin, "load_settings", _settings)
    monkeypatch.setattr(
        platform_admin,
        "build_operations_snapshot",
        lambda _settings: {
            "status": "ok",
            "capturedAt": "2026-09-01T00:00:00+00:00",
            "alertsSchemaVersion": "phase14r-operations-alerts/1.1",
            "alertSummary": {"total": 0},
            "alerts": [
                {
                    "code": "OPS_QUEUE_DEPTH_EXCEEDED",
                    "severity": "WARNING",
                    "component": "queues",
                    "observed": 101,
                    "threshold": 100,
                    "message": "Queue depth exceeded.",
                    "runbook": {
                        "id": "OPS-RUNBOOK-QUEUE-BACKLOG",
                        "reference": "docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md#operations-alert-response",
                        "operatorAction": "Inspect queue consumption.",
                        "recheckCommand": "python scripts/phase14r_operations_snapshot.py --same-stack --compact",
                        "secret": "do-not-project",
                    },
                    "secret": "do-not-project",
                }
            ],
            "database": {
                "status": "ok",
                "backend": "postgresql",
                "connections": {"active": 1},
                "secret": "do-not-project",
            },
            "queues": {
                "status": "ok",
                "backend": "redis",
                "workerCount": 6,
                "workerHealth": {
                    "status": "ok",
                    "healthyCount": 6,
                    "unhealthyStateCount": 0,
                    "staleHeartbeatCount": 0,
                },
            },
            "artifactStorage": {
                "status": "ok",
                "backend": "minio",
                "bucket": "private-bucket",
            },
            "resourceGovernance": {"status": "ok", "uploads": {"secret": True}},
        },
    )

    overview = platform_admin.get_platform_admin_overview(administrator)
    assert overview["counts"] == {
        "users": 3,
        "activeUsers": 3,
        "platformAdmins": 2,
        "projects": 1,
        "activeSessions": 1,
    }
    assert overview["operations"]["artifactStorage"] == {
        "status": "ok",
        "backend": "minio",
    }
    assert overview["operations"]["alerts"][0]["runbook"] == {
        "id": "OPS-RUNBOOK-QUEUE-BACKLOG",
        "reference": "docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md#operations-alert-response",
        "operatorAction": "Inspect queue consumption.",
        "recheckCommand": "python scripts/phase14r_operations_snapshot.py --same-stack --compact",
    }
    assert overview["operations"]["queues"]["workerHealth"]["healthyCount"] == 6
    assert "secret" not in overview["operations"]["database"]
    assert "secret" not in str(overview["operations"])

    listed = platform_admin.list_platform_users(
        q="research",
        status="ACTIVE",
        role="USER",
        limit=20,
        offset=0,
        current_user=administrator,
    )
    assert listed["total"] == 1
    assert listed["items"][0]["projectCount"] == 1
    assert listed["items"][0]["activeSessionCount"] == 1

    updated = platform_admin.update_platform_user(
        "researcher",
        platform_admin.PlatformUserUpdateRequest(isActive=False),
        administrator,
    )
    assert updated["isActive"] is False
    assert updated["activeSessionCount"] == 0

    audit = platform_admin.list_platform_audit(limit=10, current_user=administrator)
    assert audit["count"] == 1
    assert audit["items"][0]["action"] == "platform.user.updated"
    assert set(audit["items"][0]["metadata"]) <= platform_admin._SAFE_AUDIT_KEYS

    with engine.connect() as connection:
        assert connection.scalar(
            select(auth_sessions.c.revoked_at).where(
                auth_sessions.c.id == "researcher-session"
            )
        ) is not None


def test_platform_admin_mutations_fail_closed_for_self_and_last_admin(monkeypatch):
    engine = _engine()
    _seed_admin_data(engine)
    administrator = CurrentUser(
        id="admin",
        email="admin@example.invalid",
        displayName="Admin",
        roles=[],
        platformRole="PLATFORM_ADMIN",
    )
    monkeypatch.setattr(
        platform_admin, "create_engine_from_settings", lambda _settings: engine
    )
    monkeypatch.setattr(platform_admin, "load_settings", _settings)

    with pytest.raises(HTTPException) as self_role:
        platform_admin.update_platform_user(
            "admin",
            platform_admin.PlatformUserUpdateRequest(platformRole="USER"),
            administrator,
        )
    assert self_role.value.detail["code"] == "ADMIN_SELF_ROLE_CHANGE_FORBIDDEN"

    with engine.begin() as connection:
        connection.execute(
            users.update().where(users.c.id == "admin").values(is_active=False)
        )
    stale_admin_identity = CurrentUser(
        id="admin",
        email="admin@example.invalid",
        displayName="Admin",
        roles=[],
        platformRole="PLATFORM_ADMIN",
    )
    with pytest.raises(HTTPException) as last_admin:
        platform_admin.update_platform_user(
            "admin-two",
            platform_admin.PlatformUserUpdateRequest(platformRole="USER"),
            stale_admin_identity,
        )
    assert last_admin.value.detail["code"] == "LAST_ACTIVE_PLATFORM_ADMIN"


def test_platform_admin_project_membership_governance_is_bounded_and_owner_safe(monkeypatch):
    engine = _engine()
    _seed_admin_data(engine)
    administrator = CurrentUser(
        id="admin",
        email="admin@example.invalid",
        displayName="Admin",
        roles=[],
        platformRole="PLATFORM_ADMIN",
    )
    monkeypatch.setattr(platform_admin, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(platform_admin, "load_settings", _settings)

    projects_result = platform_admin.list_platform_projects(
        q="project", limit=20, offset=0, current_user=administrator
    )
    assert projects_result["total"] == 1
    assert projects_result["items"][0]["memberCount"] == 1

    members_result = platform_admin.list_platform_project_members("project", administrator)
    assert members_result["count"] == 1
    assert members_result["items"][0]["role"] == "viewer"

    updated = platform_admin.update_platform_project_member(
        "project",
        "researcher",
        platform_admin.PlatformProjectMemberUpdateRequest(role="researcher"),
        administrator,
    )
    assert updated["role"] == "researcher"

    with pytest.raises(HTTPException) as duplicate_owner:
        platform_admin.update_platform_project_member(
            "project",
            "researcher",
            platform_admin.PlatformProjectMemberUpdateRequest(role="owner"),
            administrator,
        )
    assert duplicate_owner.value.status_code == 409
    assert (
        duplicate_owner.value.detail["code"]
        == "PROJECT_OWNER_IDENTITY_IMMUTABLE"
    )

    removed = platform_admin.remove_platform_project_member("project", "researcher", administrator)
    assert removed["removed"] is True

    with pytest.raises(HTTPException) as owner_role:
        platform_admin.update_platform_project_member(
            "project",
            "admin",
            platform_admin.PlatformProjectMemberUpdateRequest(role="viewer"),
            administrator,
        )
    assert owner_role.value.detail["code"] == "PROJECT_OWNER_ROLE_REQUIRED"

    with pytest.raises(HTTPException) as owner_remove:
        platform_admin.remove_platform_project_member("project", "admin", administrator)
    assert owner_remove.value.detail["code"] == "PROJECT_OWNER_REMOVE_FORBIDDEN"
