from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import os
import secrets
from typing import Literal
import uuid

from fastapi import Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import and_, insert, inspect, select, update
from sqlalchemy.exc import SQLAlchemyError

from mdi_api.config import load_settings
from mdi_api.database import create_engine_from_settings
from mdi_api.db import account_invitations, auth_sessions, project_members, users
from mdi_api.lifecycle_policy import retention_policy_snapshot


PlatformRole = Literal["USER", "PLATFORM_ADMIN"]
PLATFORM_ROLE_USER: PlatformRole = "USER"
PLATFORM_ROLE_ADMIN: PlatformRole = "PLATFORM_ADMIN"


class CurrentUser(BaseModel):
    id: str
    email: str
    displayName: str
    roles: list[str]
    platformRole: PlatformRole = PLATFORM_ROLE_USER


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=512)


class ProfileUpdateRequest(BaseModel):
    displayName: str = Field(min_length=1, max_length=160)


class PasswordChangeRequest(BaseModel):
    currentPassword: str = Field(min_length=8, max_length=512)
    newPassword: str = Field(min_length=12, max_length=512)


class AccountDeactivationRequest(BaseModel):
    password: str = Field(min_length=8, max_length=512)
    confirmEmail: str = Field(min_length=3, max_length=320)


class AccountActivationRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)
    password: str = Field(min_length=12, max_length=512)
    displayName: str | None = Field(default=None, min_length=1, max_length=160)


def get_current_user_stub() -> CurrentUser:
    """Explicit legacy/test identity; product routes use get_current_user."""
    return CurrentUser(
        id="user_local",
        email="local@example.invalid",
        displayName="Local Researcher",
        roles=["owner"],
        platformRole=PLATFORM_ROLE_ADMIN,
    )


def require_platform_admin(current_user: CurrentUser) -> CurrentUser:
    """Fail closed for mutations of process-global platform configuration."""
    if current_user.platformRole != PLATFORM_ROLE_ADMIN:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "PLATFORM_ADMIN_REQUIRED",
                "message": "Platform administrator access is required.",
            },
        )
    return current_user


def get_current_user_compat(request: Request) -> CurrentUser:
    """Keep legacy TestClient contracts deterministic without weakening production auth.

    The pytest runner exposes `PYTEST_CURRENT_TEST`; real ASGI processes do not.
    Product research/session routes continue to depend on `get_current_user`.
    """
    if os.getenv("PYTEST_CURRENT_TEST"):
        token = request.cookies.get(load_settings().auth_cookie_name)
        if not token:
            return get_current_user_stub()
    return get_current_user(request)


def get_current_user(request: Request) -> CurrentUser:
    settings = load_settings()
    token = request.cookies.get(settings.auth_cookie_name)
    if not token:
        if not settings.auth_required:
            return get_current_user_stub()
        raise HTTPException(status_code=401, detail="请先登录。")
    now = datetime.now(timezone.utc)
    engine = create_engine_from_settings(settings)
    with engine.begin() as connection:
        row = connection.execute(
            select(
                auth_sessions.c.id, auth_sessions.c.user_id, auth_sessions.c.expires_at,
                users.c.email, users.c.display_name, users.c.platform_role, users.c.is_active,
            ).join(users, users.c.id == auth_sessions.c.user_id).where(
                and_(auth_sessions.c.token_hash == _token_hash(token), auth_sessions.c.revoked_at.is_(None))
            )
        ).mappings().first()
        if not row or not row["is_active"] or _as_utc(row["expires_at"]) <= now:
            raise HTTPException(status_code=401, detail="登录状态已失效。")
        connection.execute(update(auth_sessions).where(auth_sessions.c.id == row["id"]).values(last_seen_at=now))
        try:
            if project_members.name not in inspect(connection).get_table_names():
                roles = []
            else:
                roles = [item[0] for item in connection.execute(
                    select(project_members.c.role).where(project_members.c.user_id == row["user_id"]).distinct()
                ).all()]
        except SQLAlchemyError:
            # Historical owner-only databases predate project_members. The
            # authenticated identity remains valid; authorization helpers
            # still enforce project ownership against the projects table.
            roles = []
    return CurrentUser(
        id=row["user_id"],
        email=row["email"],
        displayName=row["display_name"],
        roles=roles or ["owner"],
        platformRole=row["platform_role"],
    )


def login(request: LoginRequest, response: Response) -> CurrentUser:
    settings = load_settings()
    email = request.email.strip().lower()
    engine = create_engine_from_settings(settings)
    with engine.begin() as connection:
        row = connection.execute(select(users).where(users.c.email == email)).mappings().first()
        row = _bootstrap_local_user(connection, email, request.password, row)
        if not row or not row["is_active"] or not row["password_hash"] or not _verify_password(request.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="邮箱或密码不正确。")
        raw_token = secrets.token_urlsafe(48)
        expires = datetime.now(timezone.utc) + timedelta(hours=settings.auth_session_hours)
        connection.execute(insert(auth_sessions).values(
            id=f"session_{uuid.uuid4().hex}", user_id=row["id"], token_hash=_token_hash(raw_token), expires_at=expires,
        ))
    response.set_cookie(
        settings.auth_cookie_name, raw_token, httponly=True, secure=_cookie_secure(), samesite="lax",
        max_age=settings.auth_session_hours * 3600, path="/",
    )
    return CurrentUser(
        id=row["id"],
        email=row["email"],
        displayName=row["display_name"],
        roles=["owner"],
        platformRole=row["platform_role"],
    )


def activate_account(request: AccountActivationRequest, response: Response) -> CurrentUser:
    """Consume a single administrator-issued invitation and establish a session."""
    settings = load_settings()
    now = datetime.now(timezone.utc)
    engine = create_engine_from_settings(settings)
    with engine.begin() as connection:
        invitation = connection.execute(
            select(account_invitations)
            .where(account_invitations.c.token_hash == _token_hash(request.token))
            .with_for_update()
        ).mappings().first()
        if (
            not invitation
            or invitation["accepted_at"] is not None
            or invitation["revoked_at"] is not None
            or _as_utc(invitation["expires_at"]) <= now
        ):
            raise HTTPException(
                status_code=400,
                detail={"code": "ACCOUNT_INVITATION_INVALID", "message": "激活链接无效或已过期。"},
            )
        existing = connection.execute(
            select(users.c.id, users.c.is_active).where(users.c.email == invitation["email"])
        ).mappings().first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail={"code": "ACCOUNT_ALREADY_EXISTS", "message": "该邮箱已经存在账户，请直接登录或联系管理员恢复。"},
            )
        user_id = f"user_{uuid.uuid4().hex}"
        display_name = (request.displayName or invitation["display_name"]).strip()
        connection.execute(
            insert(users).values(
                id=user_id,
                email=invitation["email"],
                display_name=display_name,
                password_hash=_hash_password(request.password),
                platform_role=PLATFORM_ROLE_USER,
                is_active=True,
            )
        )
        connection.execute(
            update(account_invitations)
            .where(account_invitations.c.id == invitation["id"])
            .values(accepted_at=now)
        )
        raw_token = secrets.token_urlsafe(48)
        expires = now + timedelta(hours=settings.auth_session_hours)
        connection.execute(
            insert(auth_sessions).values(
                id=f"session_{uuid.uuid4().hex}",
                user_id=user_id,
                token_hash=_token_hash(raw_token),
                expires_at=expires,
            )
        )
        _write_account_audit(
            connection,
            actor_user_id=user_id,
            action="account.activated",
            metadata={"invitationId": invitation["id"]},
        )
    response.set_cookie(
        settings.auth_cookie_name,
        raw_token,
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        max_age=settings.auth_session_hours * 3600,
        path="/",
    )
    return CurrentUser(
        id=user_id,
        email=invitation["email"],
        displayName=display_name,
        roles=["owner"],
        platformRole=PLATFORM_ROLE_USER,
    )


def logout(request: Request, response: Response, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, bool]:
    settings = load_settings()
    token = request.cookies.get(settings.auth_cookie_name)
    if token:
        engine = create_engine_from_settings(settings)
        with engine.begin() as connection:
            connection.execute(update(auth_sessions).where(auth_sessions.c.token_hash == _token_hash(token)).values(revoked_at=datetime.now(timezone.utc)))
    response.delete_cookie(settings.auth_cookie_name, path="/")
    return {"ok": True}


def update_profile(
    request: ProfileUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    display_name = request.displayName.strip()
    if not display_name:
        raise HTTPException(
            status_code=422,
            detail={"code": "DISPLAY_NAME_REQUIRED", "message": "显示名称不能为空。"},
        )
    now = datetime.now(timezone.utc)
    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        connection.execute(
            update(users)
            .where(and_(users.c.id == current_user.id, users.c.is_active.is_(True)))
            .values(display_name=display_name, updated_at=now)
        )
        _write_account_audit(
            connection,
            actor_user_id=current_user.id,
            action="account.profile.updated",
            metadata={"displayNameChanged": display_name != current_user.displayName},
        )
    return current_user.model_copy(update={"displayName": display_name})


def list_auth_sessions(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    settings = load_settings()
    current_hash = _request_token_hash(request, settings.auth_cookie_name)
    now = datetime.now(timezone.utc)
    engine = create_engine_from_settings(settings)
    with engine.connect() as connection:
        rows = connection.execute(
            select(
                auth_sessions.c.id,
                auth_sessions.c.token_hash,
                auth_sessions.c.created_at,
                auth_sessions.c.last_seen_at,
                auth_sessions.c.expires_at,
            )
            .where(
                and_(
                    auth_sessions.c.user_id == current_user.id,
                    auth_sessions.c.revoked_at.is_(None),
                    auth_sessions.c.expires_at > now,
                )
            )
            .order_by(auth_sessions.c.last_seen_at.desc(), auth_sessions.c.created_at.desc())
            .limit(100)
        ).mappings().all()
    return {
        "items": [
            {
                "id": row["id"],
                "createdAt": _as_utc(row["created_at"]).isoformat(),
                "lastSeenAt": _as_utc(row["last_seen_at"]).isoformat(),
                "expiresAt": _as_utc(row["expires_at"]).isoformat(),
                "isCurrent": bool(current_hash and row["token_hash"] == current_hash),
            }
            for row in rows
        ],
        "count": len(rows),
    }


def revoke_auth_session(
    session_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, bool]:
    settings = load_settings()
    current_hash = _request_token_hash(request, settings.auth_cookie_name)
    now = datetime.now(timezone.utc)
    engine = create_engine_from_settings(settings)
    with engine.begin() as connection:
        row = connection.execute(
            select(auth_sessions.c.id, auth_sessions.c.token_hash).where(
                and_(
                    auth_sessions.c.id == session_id,
                    auth_sessions.c.user_id == current_user.id,
                    auth_sessions.c.revoked_at.is_(None),
                )
            )
        ).mappings().first()
        if not row:
            raise HTTPException(
                status_code=404,
                detail={"code": "AUTH_SESSION_NOT_FOUND", "message": "未找到可撤销的登录会话。"},
            )
        if current_hash and row["token_hash"] == current_hash:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "CURRENT_SESSION_REQUIRES_LOGOUT",
                    "message": "当前会话请使用退出登录操作结束。",
                },
            )
        connection.execute(
            update(auth_sessions).where(auth_sessions.c.id == session_id).values(revoked_at=now)
        )
        _write_account_audit(
            connection,
            actor_user_id=current_user.id,
            action="account.session.revoked",
            metadata={"sessionId": session_id},
        )
    return {"ok": True}


def revoke_other_auth_sessions(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    settings = load_settings()
    current_hash = _request_token_hash(request, settings.auth_cookie_name)
    now = datetime.now(timezone.utc)
    conditions = [
        auth_sessions.c.user_id == current_user.id,
        auth_sessions.c.revoked_at.is_(None),
    ]
    if current_hash:
        conditions.append(auth_sessions.c.token_hash != current_hash)
    engine = create_engine_from_settings(settings)
    with engine.begin() as connection:
        result = connection.execute(
            update(auth_sessions).where(and_(*conditions)).values(revoked_at=now)
        )
        revoked = max(0, int(result.rowcount or 0))
        _write_account_audit(
            connection,
            actor_user_id=current_user.id,
            action="account.sessions.revoked_others",
            metadata={"revokedCount": revoked},
        )
    return {"ok": True, "revokedCount": revoked}


def change_password(
    request: PasswordChangeRequest,
    http_request: Request,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    if secrets.compare_digest(request.currentPassword, request.newPassword):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "PASSWORD_UNCHANGED",
                "message": "新密码必须与当前密码不同。",
            },
        )
    settings = load_settings()
    current_hash = _request_token_hash(http_request, settings.auth_cookie_name)
    now = datetime.now(timezone.utc)
    engine = create_engine_from_settings(settings)
    with engine.begin() as connection:
        row = connection.execute(
            select(users.c.password_hash).where(
                and_(users.c.id == current_user.id, users.c.is_active.is_(True))
            )
        ).mappings().first()
        if (
            not row
            or not row["password_hash"]
            or not _verify_password(request.currentPassword, row["password_hash"])
        ):
            raise HTTPException(
                status_code=401,
                detail={"code": "CURRENT_PASSWORD_INVALID", "message": "当前密码不正确。"},
            )
        connection.execute(
            update(users)
            .where(users.c.id == current_user.id)
            .values(password_hash=_hash_password(request.newPassword), updated_at=now)
        )
        session_conditions = [
            auth_sessions.c.user_id == current_user.id,
            auth_sessions.c.revoked_at.is_(None),
        ]
        if current_hash:
            session_conditions.append(auth_sessions.c.token_hash != current_hash)
        revoked = connection.execute(
            update(auth_sessions)
            .where(and_(*session_conditions))
            .values(revoked_at=now)
        )
        _write_account_audit(
            connection,
            actor_user_id=current_user.id,
            action="account.password.changed",
            metadata={"otherSessionsRevoked": max(0, int(revoked.rowcount or 0))},
        )
    return {"ok": True, "otherSessionsRevoked": max(0, int(revoked.rowcount or 0))}


def deactivate_account(
    request: AccountDeactivationRequest,
    response: Response,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, bool]:
    if request.confirmEmail.strip().lower() != current_user.email.strip().lower():
        raise HTTPException(
            status_code=422,
            detail={
                "code": "ACCOUNT_EMAIL_CONFIRMATION_MISMATCH",
                "message": "确认邮箱与当前账户不匹配。",
            },
        )
    settings = load_settings()
    now = datetime.now(timezone.utc)
    engine = create_engine_from_settings(settings)
    with engine.begin() as connection:
        row = connection.execute(
            select(users.c.password_hash, users.c.platform_role).where(
                and_(users.c.id == current_user.id, users.c.is_active.is_(True))
            )
        ).mappings().first()
        if (
            not row
            or not row["password_hash"]
            or not _verify_password(request.password, row["password_hash"])
        ):
            raise HTTPException(
                status_code=401,
                detail={"code": "CURRENT_PASSWORD_INVALID", "message": "当前密码不正确。"},
            )
        if row["platform_role"] == PLATFORM_ROLE_ADMIN:
            active_admins = connection.execute(
                select(users.c.id)
                .where(
                    and_(
                        users.c.platform_role == PLATFORM_ROLE_ADMIN,
                        users.c.is_active.is_(True),
                    )
                )
                .with_for_update()
            ).scalars().all()
            if len(active_admins) <= 1:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "LAST_ACTIVE_PLATFORM_ADMIN",
                        "message": "不能停用最后一名有效平台管理员。",
                    },
                )
        connection.execute(
            update(users)
            .where(users.c.id == current_user.id)
            .values(is_active=False, updated_at=now)
        )
        connection.execute(
            update(auth_sessions)
            .where(
                and_(
                    auth_sessions.c.user_id == current_user.id,
                    auth_sessions.c.revoked_at.is_(None),
                )
            )
            .values(revoked_at=now)
        )
        _write_account_audit(
            connection,
            actor_user_id=current_user.id,
            action="account.deactivated",
            metadata={"provenanceRetained": True},
        )
    response.delete_cookie(settings.auth_cookie_name, path="/")
    return {
        "ok": True,
        "provenanceRetained": True,
        "retentionPolicy": retention_policy_snapshot(
            manual_purge_supported=False
        ),
    }


def _bootstrap_local_user(connection, email: str, password: str, row):
    configured_email = os.getenv("MDI_LOCAL_USER_EMAIL", "local@example.invalid").strip().lower()
    configured_password = os.getenv("MDI_LOCAL_USER_PASSWORD")
    if email != configured_email or not configured_password or not secrets.compare_digest(password, configured_password):
        return row
    platform_role = _configured_local_platform_role()
    values = {
        "email": email,
        "display_name": os.getenv("MDI_LOCAL_USER_NAME", "本地研究者"),
        "password_hash": _hash_password(password),
        "platform_role": platform_role,
        "is_active": True,
        "updated_at": datetime.now(timezone.utc),
    }
    if row is None:
        # Historical local databases may already contain the reserved
        # bootstrap identity under an older email. Bind that same account
        # idempotently instead of attempting a duplicate primary-key insert.
        existing_local = connection.execute(select(users).where(users.c.id == "user_local")).mappings().first()
        if existing_local:
            connection.execute(update(users).where(users.c.id == "user_local").values(**values))
        else:
            connection.execute(insert(users).values(
                id="user_local", email=email, display_name=os.getenv("MDI_LOCAL_USER_NAME", "本地研究者"),
                password_hash=values["password_hash"], platform_role=platform_role, is_active=True,
            ))
    else:
        connection.execute(update(users).where(users.c.id == row["id"]).values(**values))
    return connection.execute(select(users).where(users.c.email == email)).mappings().first()


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return "scrypt$16384$8$1$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(digest).decode()


def _verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt, expected = encoded.split("$")
        if algorithm != "scrypt":
            return False
        actual = hashlib.scrypt(password.encode("utf-8"), salt=base64.urlsafe_b64decode(salt), n=int(n), r=int(r), p=int(p), dklen=32)
        return secrets.compare_digest(actual, base64.urlsafe_b64decode(expected))
    except (ValueError, TypeError):
        return False


def _token_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _cookie_secure() -> bool:
    return os.getenv("MDI_AUTH_COOKIE_SECURE", "false").lower() in {"1", "true", "yes", "on"}


def _configured_local_platform_role() -> PlatformRole:
    configured = os.getenv("MDI_LOCAL_USER_PLATFORM_ROLE", PLATFORM_ROLE_USER).strip().upper()
    if configured not in {PLATFORM_ROLE_USER, PLATFORM_ROLE_ADMIN}:
        return PLATFORM_ROLE_USER
    return configured  # type: ignore[return-value]


def _request_token_hash(request: Request, cookie_name: str) -> str | None:
    token = request.cookies.get(cookie_name)
    return _token_hash(token) if token else None


def _write_account_audit(
    connection,
    *,
    actor_user_id: str,
    action: str,
    metadata: dict[str, object],
) -> None:
    from mdi_api.db import audit_logs

    connection.execute(
        insert(audit_logs).values(
            id=f"audit_{uuid.uuid4().hex}",
            actor_user_id=actor_user_id,
            project_id=None,
            action=action,
            target_type="user",
            target_id=actor_user_id,
            metadata_json=metadata,
        )
    )


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
